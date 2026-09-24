# -*- coding: utf-8 -*-
"""audit/r4_lsh_neardup.py — rule R4: MinHash/LSH-recalled near-duplicate
(Jaccard >= 0.8) against the Big-Vul official test.
(2,093 items removed in the submitted run; plus 1,205 cross-split duplicates —
4,983 removed in total across R1-R4 + cross-split.)"""
import json
import sys
from collections import defaultdict

N_PERM = 128
BANDS, ROWS = 32, 4  # 32 bands x 4 rows -> J>=0.8 recall-dominant


def shingles(s, k=5):
    s = "".join((s or "").split())
    return {s[i:i + k] for i in range(max(0, len(s) - k + 1))}


def minhash_sig(sh, seed=1):
    sig = []
    for i in range(N_PERM):
        h = seed * 1_000_003 + i * 998_244_353
        sig.append(min((hash(x) ^ h) & 0xFFFFFFFF for x in sh) if sh else 0xFFFFFFFF)
    return sig


def lsh_index(test_codes):
    buckets = defaultdict(list)
    for idx, code in enumerate(test_codes):
        sig = minhash_sig(shingles(code))
        for b in range(BANDS):
            buckets[(b, tuple(sig[b * ROWS:(b + 1) * ROWS]))].append(idx)
    return buckets


def jaccard(a, b):
    sa, sb = shingles(a), shingles(b)
    return len(sa & sb) / len(sa | sb) if sa | sb else 0.0


def audit(train_records, bigvul_test, threshold=0.8):
    buckets = lsh_index([t.get("func_before") or t.get("function", "") for t in bigvul_test])
    codes = [t.get("func_before") or t.get("function", "") for t in bigvul_test]
    hits = []
    for r in train_records:
        src = r.get("func_before") or r.get("input", "")
        sig = minhash_sig(shingles(src))
        cands = set()
        for b in range(BANDS):
            cands.update(buckets.get((b, tuple(sig[b * ROWS:(b + 1) * ROWS])), ()))
        for c in cands:
            if jaccard(src, codes[c]) >= threshold:
                hits.append(r)
                break
    keep = [r for r in train_records if r not in hits]
    return keep, len(hits)


if __name__ == "__main__":
    train = json.load(open(sys.argv[1], encoding="utf-8"))
    test = json.load(open(sys.argv[2], encoding="utf-8"))
    keep, n = audit(train, test)
    print(f"R4: removed {n}; kept {len(keep)}")

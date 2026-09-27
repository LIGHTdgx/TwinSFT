# -*- coding: utf-8 -*-
"""audit/r3_trigram_jaccard.py — rule R3: character-trigram Jaccardi >= 0.8
against a test function of the SAME CVE (twin leakage).
(192 items removed in the submitted run.)"""
import json
import sys
from collections import Counter


def trigrams(s):
    s = "".join((s or "").split())
    return Counter(s[i:i + 3] for i in range(max(0, len(s) - 2)))


def jaccard(a, b):
    ca, cb = trigrams(a), trigrams(b)
    inter = sum((ca & cb).values())
    union = sum((ca | cb).values())
    return inter / union if union else 0.0


def audit(train_records, test_by_cve, threshold=0.8):
    hits = []
    for r in train_records:
        cve = str((r.get("meta") or {}).get("cve") or "").upper()
        for t in test_by_cve.get(cve, []):
            if jaccard(r.get("func_before") or r.get("input", ""), t) >= threshold:
                hits.append(r)
                break
    keep = [r for r in train_records if r not in hits]
    return keep, len(hits)


if __name__ == "__main__":
    train = json.load(open(sys.argv[1], encoding="utf-8"))
    tests = json.load(open(sys.argv[2], encoding="utf-8"))  # [{"cve":..., "func_before":...}]
    by_cve = {}
    for t in tests:
        by_cve.setdefault(str(t.get("cve") or t.get("CVE ID") or "").upper(), []).append(
            t.get("func_before") or t.get("function", ""))
    keep, n = audit(train, by_cve)
    print(f"R3: removed {n}; kept {len(keep)}")

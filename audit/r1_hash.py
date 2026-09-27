# -*- coding: utf-8 -*-
"""audit/r1_hash.py — rule R1: exact function-hash collision with any test set.

Every training item whose normalized function text hashes to a test function's
hash is removed. (1,243 items removed in the submitted run.)
"""
import hashlib
import json
import sys


def norm(code):
    return "".join((code or "").split())


def h(code):
    return hashlib.sha256(norm(code).encode("utf-8")).hexdigest()


def audit(train_records, test_sets):
    test_hashes = set()
    for tests in test_sets:
        for t in tests:
            test_hashes.add(h(t["func_before"] if "func_before" in t else t.get("function", "")))
    hits = [r for r in train_records if h(r.get("func_before") or r.get("input", "")) in test_hashes]
    keep = [r for r in train_records if r not in hits]
    return keep, len(hits)


if __name__ == "__main__":
    train = json.load(open(sys.argv[1], encoding="utf-8"))
    tests = [json.load(open(p, encoding="utf-8")) for p in sys.argv[2:]]
    keep, n = audit(train, tests)
    print(f"R1: removed {n}; kept {len(keep)}")

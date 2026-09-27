# -*- coding: utf-8 -*-
"""audit/r2_cve_id.py — rule R2: training item sharing a CVE id with any SVD-Bench test item.
(250 items removed in the submitted run.)"""
import json
import sys


def audit(train_records, svd_test):
    test_cves = {str(r.get("cve_id") or r.get("CVE ID") or "").upper() for r in svd_test} - {"", "NONE"}
    hits = [r for r in train_records if str((r.get("meta") or {}).get("cve") or r.get("cve_id") or "").upper() in test_cves]
    keep = [r for r in train_records if r not in hits]
    return keep, len(hits)


if __name__ == "__main__":
    train = json.load(open(sys.argv[1], encoding="utf-8"))
    svd_test = json.load(open(sys.argv[2], encoding="utf-8"))
    keep, n = audit(train, svd_test)
    print(f"R2: removed {n}; kept {len(keep)}")

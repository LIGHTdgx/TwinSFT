# -*- coding: utf-8 -*-
"""eval/tests/test_metrics.py — unit tests for the metric definitions on small fixtures."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics import (auc, confusion, implied_auc, macro_f1, prf,  # noqa: E402
                     trivial_f1)


def test_trivial_f1_formula():
    # balanced prevalence -> 2*0.5/1.5 = 2/3
    assert abs(trivial_f1(0.5) - 2 / 3) < 1e-9
    # 5.8% prevalence (Big-Vul) -> ~0.1096 (paper: .110)
    assert abs(trivial_f1(0.058) - 0.1096) < 5e-4


def test_prf_basic():
    pairs = [(1, 0.9), (1, 0.8), (0, 0.7), (0, 0.2)]
    m = prf(pairs, thr=0.75)
    assert m["confusion"] == (2, 0, 2, 0)
    assert m["precision"] == 1.0 and m["recall"] == 1.0 and m["f1"] == 1.0
    m2 = prf(pairs, thr=0.5)
    assert m2["confusion"] == (2, 1, 1, 0)
    assert abs(m2["precision"] - 2 / 3) < 1e-9


def test_auc_tie_aware():
    # perfect separation -> 1.0
    assert auc([0.9, 0.8], [0.2, 0.1]) == 1.0
    # fully tied -> 0.5
    assert abs(auc([0.5, 0.5], [0.5, 0.5]) - 0.5) < 1e-9
    # one tie group: pos {0.7,0.3}, neg {0.7,0.1} -> mid-rank AUC = 0.625
    # (pairs: tie .5, win 1, loss 0, win 1 -> 2.5/4)
    assert abs(auc([0.7, 0.3], [0.7, 0.1]) - 0.625) < 1e-9


def test_implied_auc():
    # all-positive: TPR=1, FPR=1 -> 0.5 ; perfect binary: TPR=1,FPR=0 -> 1.0
    assert abs(implied_auc(10, 10, 0, 0) - 0.5) < 1e-9
    assert abs(implied_auc(10, 0, 10, 0) - 1.0) < 1e-9


def test_macro_f1():
    a = [(1, 0.9), (0, 0.1)]
    b = [(1, 0.1), (0, 0.9)]  # inverted -> F1 0
    assert abs(macro_f1([a, b]) - 0.5) < 1e-9
    assert confusion(a, 0.5) == (1, 0, 1, 0)


if __name__ == "__main__":
    for fn in [test_trivial_f1_formula, test_prf_basic, test_auc_tie_aware,
               test_implied_auc, test_macro_f1]:
        fn()
        print("PASS", fn.__name__)

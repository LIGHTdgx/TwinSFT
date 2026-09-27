# -*- coding: utf-8 -*-
"""eval/demo.py — minimal verification entry: metrics + calibration on bundled scores."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from calibration import load_pairs  # noqa: E402
from metrics import auc, prf, trivial_f1  # noqa: E402

d = load_pairs(os.path.join(HERE, "..", "results", "score_distributions", "bigvul_full_scores.json"))
pos = [s for y, s in d if y == 1]
neg = [s for y, s in d if y == 0]
pi = len(pos) / len(d)
print(f"n={len(d)}  prevalence={pi:.3f}  trivial F1={trivial_f1(pi):.3f}")
print(f"V-score F1@0.5={prf(d, 0.5)['f1']:.3f}  AUC={auc(pos, neg):.3f}")
print("(paper, full test: F1 .213, AUC .809 — demo uses the first 2000 bundled rows)")

if __name__ == "__main__":
    pass

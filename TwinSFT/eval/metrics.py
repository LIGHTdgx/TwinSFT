# -*- coding: utf-8 -*-
"""eval/metrics.py — TwinSFT evaluation metrics (paper Sec. 3.2)

Implements: positive-class F1, macro F1, rank-based AUC (tie-aware),
all-positive trivial F1 = 2*pi/(1+pi) at prevalence pi, and the implied AUC of a
binary predictor = 0.5 + (TPR - FPR)/2. These are the exact definitions used to
produce results/table*.json.
"""
from collections import Counter


def confusion(pairs, thr=0.5):
    """pairs: iterable of (label 0/1, score float); predict positive iff score >= thr."""
    tp = fp = tn = fn = 0
    for y, s in pairs:
        if s >= thr:
            tp, fp = (tp + 1, fp) if y == 1 else (tp, fp + 1)
        else:
            fn, tn = (fn + 1, tn) if y == 1 else (fn, tn + 1)
    return tp, fp, tn, fn


def prf(pairs, thr=0.5):
    tp, fp, tn, fn = confusion(pairs, thr)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": p, "recall": r, "f1": f1, "confusion": (tp, fp, tn, fn)}


def macro_f1(per_language_pairs, thr=0.5):
    """Macro over languages of positive-class F1 (REEF protocol)."""
    f1s = [prf(pairs, thr)["f1"] for pairs in per_language_pairs]
    return sum(f1s) / len(f1s)


def auc(pos_scores, neg_scores):
    """Rank-based AUC with midrank tie handling (Mann-Whitney)."""
    pc, nc = Counter(pos_scores), Counter(neg_scores)
    vals = sorted(set(pos_scores) | set(neg_scores), reverse=True)
    P, N = len(pos_scores), len(neg_scores)
    tp = fp = 0
    area = 0.0
    for v in vals:  # empirical ROC step; integrate trapezoid at each tie group
        ctp, cfp = pc.get(v, 0), nc.get(v, 0)
        tpr_new, fpr_new = (tp + ctp) / P, (fp + cfp) / N
        area += (fpr_new - fp / N) * (tp / P + tpr_new) / 2  # trapezoid over tie group
        tp, fp = tp + ctp, fp + cfp
    return area


def trivial_f1(prevalence):
    """All-positive policy F1 at prevalence pi: 2*pi / (1 + pi)."""
    pi = prevalence
    return 2 * pi / (1 + pi)


def implied_auc(tp, fp, tn, fn):
    """AUC implied by a binary predictor: 0.5 + (TPR - FPR)/2."""
    tpr = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return 0.5 + (tpr - fpr) / 2

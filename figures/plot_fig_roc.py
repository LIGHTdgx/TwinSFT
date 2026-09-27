# -*- coding: utf-8 -*-
"""figures/plot_fig_roc.py — Extended Fig. (ROC curves), full recipe vs -noSplits
plus the zero-shot control's implied 2-segment curve, on the four low-prevalence
official tests. Reads the bundled per-sample scores in
results/score_distributions/ (first 2000 rows per set -> curves approximate the
paper figure; full scores reproduce it exactly).
Run from figures/: python plot_fig_roc.py"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SD = os.path.join(HERE, "..", "results", "score_distributions")

# zero-shot (same model) binary decision points (FPR, TPR), robust-parser CMs of
# the backbone on the official tests — implied AUC = 0.5 + (TPR-FPR)/2 (Table 1)
ZS = {"svd_java": (0.6585, 0.7813), "svd_javascript": (0.6240, 0.6677),
      "svd_python": (0.7373, 0.8012), "bigvul": (0.7126, 0.8183)}
SETS = [("svd_java", "SVD Java"), ("svd_javascript", "SVD JavaScript"),
        ("svd_python", "SVD Python"), ("bigvul", "Big-Vul")]


def load(name):
    d = json.load(open(os.path.join(SD, name + "_full_scores.json"), encoding="utf-8"))
    rows = [r for r in d["rows"] if "label" in r]
    return [r["p_vuln"] for r in rows if r["label"] == 1], [r["p_vuln"] for r in rows if r["label"] == 0]


def auc(pos, neg):
    from collections import Counter
    pc, nc = Counter(pos), Counter(neg)
    vals = sorted(set(pos) | set(neg), reverse=True)
    P, N = len(pos), len(neg)
    area = tp = fp = 0.0
    for v in vals:
        tpr_new = (tp + pc.get(v, 0)) / P
        fpr_new = (fp + nc.get(v, 0)) / N
        area += (fpr_new - fp / N) * ((tp / P) + tpr_new) / 2
        tp += pc.get(v, 0)
        fp += nc.get(v, 0)
    return area


def roc(pos, neg):
    from collections import Counter
    pc, nc = Counter(pos), Counter(neg)
    vals = sorted(set(pos) | set(neg), reverse=True)
    P, N = len(pos), len(neg)
    fpr, tpr, tp, fp = [0.0], [0.0], 0, 0
    for v in vals:
        tp += pc.get(v, 0)
        fp += nc.get(v, 0)
        fpr.append(fp / N)
        tpr.append(tp / P)
    return fpr, tpr


TICKS = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
fig, axes = plt.subplots(1, 4, figsize=(7.0, 1.8), dpi=300)
for ax, (name, title) in zip(axes, SETS):
    pos, neg = load(name)
    fpr, tpr = roc(pos, neg)
    ax.plot(fpr, tpr, color="#17375e", lw=1.0, zorder=4,
            label=f"TwinSFT (full) ({auc(pos, neg):.3f})")
    zf, zt = ZS[name]
    ax.plot([0, zf, 1], [0, zt, 1], color="0.45", lw=0.7, zorder=2,
            label=f"Zero-shot (implied, {0.5 + (zt - zf) / 2:.3f})")
    ax.plot([0, 1], [0, 1], color="0.82", ls=(0, (4, 3)), lw=0.5, zorder=1)
    ax.set_title(title, fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks(TICKS)
    ax.set_yticks(TICKS)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=4.3, loc="lower right", frameon=False, handlelength=1.1,
              borderaxespad=0.2, labelspacing=0.25)
for ax in (axes[0],):
    ax.set_ylabel("TPR", fontsize=6.5)
for ax in axes:
    ax.set_xlabel("FPR", fontsize=6.5)
fig.tight_layout(pad=0.5)
fig.savefig(os.path.join(HERE, "fig_roc_regenerated.pdf"), bbox_inches="tight")
print("saved fig_roc_regenerated.pdf (bundled-sample approximation; fig_roc.pdf = exact paper asset)")

# -*- coding: utf-8 -*-
"""results/score_distributions/plot.py — Fig. 2 of the paper.

Class-conditional score distributions on Big-Vul for the no-splits variant
(degenerate bimodal pattern, mean gap 0.15) vs the full framework (separated,
mean gap 0.37), using the per-sample p_vuln scores bundled here.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    d = json.load(open(os.path.join(HERE, name), encoding="utf-8"))
    pos = [r["p_vuln"] for r in d["rows"] if r.get("label") == 1]
    neg = [r["p_vuln"] for r in d["rows"] if r.get("label") == 0]
    return pos, neg


fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.55), dpi=300, sharey=True)
for ax, (fname, title) in zip(axes, [("bigvul_noSplits_scores.json", "TwinSFT-noSplits"),
                                     ("bigvul_full_scores.json", "TwinSFT (full)")]):
    pos, neg = load(fname)
    ax.hist(neg, bins=40, range=(0, 1), color="#c9c9c9", edgecolor="white", density=True)
    ax.hist(pos, bins=40, range=(0, 1), color="#4c7cae", edgecolor="white", alpha=0.85, density=True)
    ax.axvline(sum(neg) / len(neg), color="0.25", ls=":", lw=0.8)
    ax.axvline(sum(pos) / len(pos), color="#17375e", ls=":", lw=0.9)
    ax.set_yscale("log")
    ax.set_title(f"{title} (gap {sum(pos)/len(pos)-sum(neg)/len(neg):.2f})", fontsize=6.5)
    ax.set_xlim(0, 1)
axes[0].set_ylabel("density (log)", fontsize=6)
fig.text(0.55, 0.02, "vulnerability score  (gray: benign, blue: vulnerable, dotted: class means)",
         ha="center", fontsize=5.2)
fig.tight_layout(pad=0.5, rect=(0, 0.08, 1, 1))
fig.savefig(os.path.join(HERE, "fig_score.pdf"), bbox_inches="tight")
print("saved fig_score.pdf")

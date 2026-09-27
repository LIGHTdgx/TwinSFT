# -*- coding: utf-8 -*-
"""figures/plot_fig_auc.py — Extended Fig. (ablation F1 bars), regenerated from the
submitted Table 4 data (untuned readout). Run from figures/: python plot_fig_auc.py"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
T4 = json.load(open(os.path.join(HERE, "..", "results", "table4_ablation.json"), encoding="utf-8"))
UNT = T4["untuned_readout_v_score_theta0.5"]

SETS = ["Java", "JavaScript", "Python", "Big-Vul", "REEF"]
LABELS = ["SVD\nJava", "SVD\nJS", "SVD\nPy", "Big-Vul", "REEF"]
VARIANTS = [("full", "TwinSFT (full)", "#17375e"),
            ("-noSplits", "$-$noSplits", "#9e9e9e"),
            ("-noTwinRank", "$-$noTwinRank", "#7f9fc4"),
            ("-noLoc", "$-$noLoc", "#a9c4dd"),
            ("-3B", "TwinSFT-3B", "#c0504d")]

fig, ax = plt.subplots(figsize=(3.5, 2.1), dpi=300)
xs = list(range(len(SETS)))
w = 0.145
for i, (key, name, color) in enumerate(VARIANTS):
    vals = [UNT[key][s][0] for s in SETS]
    ax.bar([x + (i - 2) * w for x in xs], vals, width=w * 0.92, label=name,
           color=color, edgecolor="black", linewidth=0.3, zorder=3)
ax.set_xticks(xs)
ax.set_xticklabels(LABELS, fontsize=6)
ax.set_ylabel("Positive-class F1 ($\\theta{=}0.5$)", fontsize=6.5)
ax.set_ylim(0.0, 0.6)
ax.set_yticks([0, 0.2, 0.4, 0.6])
ax.tick_params(axis="y", labelsize=6)
ax.legend(fontsize=5.4, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.16),
          frameon=False, columnspacing=0.9, handlelength=1.2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(axis="y", color="0.9", linewidth=0.4, zorder=0)
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(HERE, "fig_auc_regenerated.pdf"), bbox_inches="tight")
print("saved fig_auc_regenerated.pdf (5 variants, submitted Table 4 untuned readout)")

# -*- coding: utf-8 -*-
"""figures/plot_fig_thr.py — Extended Fig. (threshold sweep on SVD, full recipe):
F1(theta) with the default theta=0.5 line and the per-language calibrated star.
Data: results/threshold_sweep.json (exact points computed from the full
per-sample scores). Run from figures/: python plot_fig_thr.py"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "..", "results", "threshold_sweep.json"), encoding="utf-8"))["data"]

fig, axes = plt.subplots(1, 3, figsize=(5.2, 1.7), dpi=300, sharey=True)
for ax, (L, v) in zip(axes, D.items()):
    ax.plot(v["theta_grid"], v["f1"], color="#17375e", lw=1.0)
    ax.axvline(0.5, color="0.5", ls=":", lw=0.7)
    ax.plot([v["calibrated_theta"]], [v["calibrated_f1"]], marker="*", color="#c0504d", ms=7)
    ax.set_title(f"{L}  (F1@0.5 {v['f1_at_0.5']:.3f} -> cal {v['calibrated_f1']:.3f})", fontsize=6)
    ax.set_xlim(0, 1)
    ax.tick_params(labelsize=6)
    ax.set_xlabel(r"threshold $\theta$", fontsize=6)
axes[0].set_ylabel("Positive-class F1", fontsize=6.5)
fig.tight_layout(pad=0.5)
fig.savefig(os.path.join(HERE, "fig_thr_regenerated.pdf"), bbox_inches="tight")
print("saved fig_thr_regenerated.pdf")

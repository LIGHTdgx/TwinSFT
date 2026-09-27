# Figures

| Figure | Asset | Reproducible from | Status |
|---|---|---|---|
| Fig. 1 — framework overview | `framework.png` | (schematic) | submitted version |
| Fig. 2 — class-conditional score distributions (Big-Vul, noSplits vs full) | `fig_score.pdf` | `../results/score_distributions/plot.py` + bundled per-sample scores | submitted version |
| Extended — ROC curves (4 low-prevalence tests, full vs noSplits + zero-shot implied) | `fig_roc.pdf` | `plot_fig_roc.py` -> `fig_roc_regenerated.pdf` (bundled rows = first 2000/set; the checked-in `fig_roc.pdf` is the exact paper asset) | extended (from the full technical version), data = submitted version |
| Extended — threshold sweep on SVD (F1(θ), default 0.5 vs calibrated θ*) | `fig_thr.pdf` | `plot_fig_thr.py` -> `fig_thr_regenerated.pdf` + `../results/threshold_sweep.json` (exact points) | extended, data = submitted version |
| Extended — ablation F1 bars (5 variants x 5 datasets, untuned readout) | `fig_auc.pdf` | `plot_fig_auc.py` -> `fig_auc_regenerated.pdf` + `../results/table4_ablation.json` (exact) | extended, data = submitted version |

All four PDFs are the **canonical submitted-version figures** (verified: fig_roc legends .754/.701/.664/.809 and noSplits .562/.516/.533; fig_auc's five-variant naming; fig_score labels). The scripts regenerate data-exact variants (`*_regenerated.pdf`) from the bundled JSONs. Exact sweep/star values: `results/threshold_sweep.json` (Java .317->.304 at theta*=.294, JavaScript .435->.421 at theta*=.223, Python .159->.191 at theta*=.438 — matching Table 4).

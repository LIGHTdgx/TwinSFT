# Data sources

The corpus is built from public sources; **none of the raw benchmark data is redistributed in this repository**. Obtain each source under its own license:

| Component | Size | Where to get it | Notes |
|---|---|---|---|
| SVD-Bench official train/test splits (Java/JS/Python) | 18.0k train verdicts | https://github.com/soarsmu/SVD-Bench (arXiv:2503.01449) | time-split: test = all post-June-2023 fixing commits |
| Big-Vul (TSE'24 split) train/valid/test | 12.0k train + 18.8k valid | Yin et al., IEEE TSE 2024 (arXiv per paper) | test 18,864 functions @ 5.8% prevalence |
| REEF function-level train | 10.1k | https://github.com/ASE-REEF/REEF-data + rebuild pipeline of arXiv:2506.07503 | our test rebuild covers 74% of the published test volume |
| External CVE-fix patch pairs | 3k pairs -> 6.0k verdicts + 4.0k TwinRank | public CVE/GitHub commit crawls | both versions of each function enter as ordinary verdict samples; pairs also feed TwinRank |
| General five-language pool | 8.0k | public function-level corpora (C/Go/Java/JS/Python) | real label prevalence |
| Localization supervision | 3.6k | derived from the same patch pairs | line ranges mapped from unified-diff hunks onto the function span |

Calibration sets (V-cal, per language): held-out slices of the training-side external pools (design: up to 133 positives + 267 negatives per language; actual sizes vary by pool), excluded from every training set and audited against every test set. See `eval/calibration.py`.

Curated artifacts in this repo (prompts, samples, JSONs) are released for research use; follow the upstream licenses for the datasets themselves.

# Training variants (Table 4)

All five variants are independent LoRA runs with identical hyperparameters (see `lora_sft.py`), differing only in the training corpus:

| Variant | Corpus |
|---|---|
| **full** | 61.7k = 48.1k official-split verdicts (SVD 18.0k + Big-Vul 12.0k + REEF 10.1k + 8.0k general pool) + 6.0k patch-pair verdicts + 4.0k TwinRank + 3.6k localization |
| **-noSplits** | full minus the benchmark official-split base; trained on the general-purpose function/patch corpora of the pre-benchmark recipe |
| **-noTwinRank** | full minus the 4k TwinRank family |
| **-noLoc** | full minus the 3.6k localization family |
| **-3B** | full corpus, backbone switched to Qwen2.5-Coder-3B-Instruct |

Evaluation of every variant uses the single untuned operating point (V-score, θ=0.5) plus the per-language calibrated readout (V-cal); see `eval/`.

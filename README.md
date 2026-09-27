# TwinSFT

**TwinSFT: Data-Centric Multi-Task Instruction Tuning for Function-Level Vulnerability Detection** (ICASSP 2027 submission)

TwinSFT is a data-centric instruction-tuning framework for a 7B code LLM (Qwen2.5-Coder-7B-Instruct). It keeps the standard supervised setup — training on the benchmarks' own published splits with conclusion-line verdicts — and adds two task families supervised automatically from patch pairs: **TwinRank** paired-version comparison and **patch-derived vulnerable-line localization**. Verdicts are read generatively (V-gen) or as a continuous decision-token score (V-score, θ=0.5), which enables post-hoc per-language threshold calibration (V-cal) and threshold-free AUC auditing. One training run surpasses the best published system of any kind on SVD-Bench Java, ranks above 16 of 17 baselines on Big-Vul, and exceeds every published open fine-tuned LLM on REEF.

All numbers in this repository correspond to the submitted version of the paper.

## Claim-to-artifact map

| Paper claim | Artifact |
|---|---|
| Instruction prompts (verdict / TwinRank / localization) | `prompts/` (templates + real, code-truncated examples) |
| Data framework (61.7k corpus composition) | `data/build_corpus.py`, `data/corpus_stats.json`, `data/samples/`, `data/sources.md` |
| Audit tooling (rules R1–R4, 4,983 items removed) | `audit/r1_hash.py` … `audit/r4_lsh_neardup.py`, `audit/report.json` |
| Evaluation harness (V-gen / V-score / V-cal; F1, macro-F1, AUC, trivial F1, implied AUC) | `eval/readouts.py`, `eval/calibration.py`, `eval/metrics.py`, `eval/tests/` |
| Results (Tables 1–4) | `results/table1_svd.json` … `results/table4_ablation.json` |
| Figures (paper + extended, with reproducible scripts) | `figures/` (see `figures/README.md`) |
| Score distributions (Fig. 2 + ROC inputs) | `results/score_distributions/` (+ `plot.py`); threshold sweep in `results/threshold_sweep.json` |
| Zero-shot & API controls (GLM-5.2, ~72k calls, ~13 h; local vLLM ~30 min) | `controls/zero_shot.py`, `controls/api_glm52.py`, `controls/cost_log_summary.md` |
| Training entry (LoRA r=64, α=128, dropout .05, bs 32, 2 epochs, lr 1e-4, 1×A800 ≈4 h) | `train/lora_sft.py`, `train/variants.md` |

## Results

**Table 1 — SVD-Bench official tests (positive-class F1 / AUC)** ([JSON](results/table1_svd.json))

| | Java | JavaScript | Python |
|---|---|---|---|
| Trivial (all-positive) | .140 | .298 | .162 |
| Zero-shot (same model) | .158 / .562 | .290 / .522 | .170 / .532 |
| GLM-5.2 API zero-shot | .191 / .610 | .258 / .487 | .157 / .519 |
| TwinSFT V-gen | .310 | .398 | .165 |
| TwinSFT V-score (θ=0.5) | **.317** / **.754** | **.435** / **.701** | .159 / **.664** |
| TwinSFT V-cal | .304 / .754 | .421 / .701 | **.191** / .664 |
| *PLMs:* GraphCodeBERT / CodeT5 / UniXcoder | .243 / **.269** / .232 | **.472** / .394 / .425 | .011 / .010 / **.013** |
| *LLMs (original data):* CodeGemma / CodeQwen1.5 / StarCoder-2 | **.120** / .080 / .072 | .413 / **.443** / .435 | **.026** / .011 / .001 |
| *LLMs (down-sampled 1:1):* CodeQwen1.5 / CodeGemma / CodeLlama | .241 / .237 / **.268** | **.465** / .393 / .337 | .199 / **.201** / .198 |

**Table 2 — Big-Vul official test (positive-class F1)** ([JSON](results/table2_bigvul.json))

| Detector | F1 | Detector | F1 |
|---|---|---|---|
| LineVul | **.272** | CodeBERT | .270 |
| UniXcoder | .256 | FT DeepSeek-Coder-6.7B | **.270** |
| FT CodeLlama-7B | .259 | FT Phi-2 | .241 |
| Trivial | .110 | Zero-shot (same model) | .122 |
| GLM-5.2 API | .126 | TwinSFT V-score | .213 |
| TwinSFT V-gen | .206 | TwinSFT V-cal (valid-split θ†=.910) | **.297** |

**Table 3 — REEF, macro F1 over seven languages** ([JSON](results/table3_reef.json))

| Detector | Macro F1 | Detector | Macro F1 |
|---|---|---|---|
| CodeT5+ | **.708** | CodeT5 | .694 |
| UniXcoder | .682 | Llama 3 (ZSP) | **.528** |
| Code Llama (ZSP) | .496 | DeepSeek-Coder (ZSP) | .380 |
| Code Llama (FSP) | **.568** | Llama 3 (FSP) | .491 |
| DeepSeek-Coder (FSP) | .486 | Trivial | .667 |
| Zero-shot (same model) | .630 | GLM-5.2 API | .591 |
| TwinSFT V-gen | .592 | TwinSFT V-score | .490 |
| TwinSFT V-cal | **.639** | | |

**Table 4 — Ablations under two readouts** ([JSON](results/table4_ablation.json), full 5×5×2×(F1,AUC))

*Untuned (V-score, θ=0.5), F1/AUC:*

| Variant | Java | JavaScript | Python | Big-Vul | REEF |
|---|---|---|---|---|---|
| full | .317/.754 | .435/.701 | .159/.664 | .213/.809 | .490/.684 |
| −Official splits | .186/.562 | .219/.516 | .139/.533 | .181/.600 | .340/.533 |
| −TwinRank | .276/.758 | .304/.696 | .142/.629 | .198/.781 | .433/.632 |
| −Loc | .322/.750 | .265/.742 | .186/.627 | .196/.792 | .517/.615 |
| 3B | .157/.568 | .340/.628 | .066/.515 | .163/.718 | .376/.615 |

*Calibrated (V-cal), F1 (AUC unchanged — threshold-free):*

| Variant | Java | JavaScript | Python | Big-Vul | REEF |
|---|---|---|---|---|---|
| full | .304 | .421 | .191 | **.297** | .639 |
| −Official splits | .142 | .281 | .161 | .188 | .598 |
| −TwinRank | .279 | .348 | .205 | .274 | .641 |
| −Loc | .221 | **.456** | .201 | .278 | **.648** |
| 3B | .141 | .326 | .164 | .240 | .593 |

## Reproduction

```bash
pip install -r requirements.txt
# 1) verify the evaluation harness on small fixtures
python -m pytest eval/tests/ -q
# 2) demo: metrics + calibration on bundled score samples (results/score_distributions/)
python eval/demo.py
# 3) regenerate the paper figures (Fig. 2 exact; ROC/threshold/ablation extended)
python results/score_distributions/plot.py && python figures/plot_fig_thr.py && python figures/plot_fig_auc.py && python figures/plot_fig_roc.py
# 4) full pipeline: see data/build_corpus.py -> train/lora_sft.py -> eval/ (data must be
#    obtained from the public benchmarks first; see data/sources.md)
```

Model serving for inference uses vLLM (`vllm serve` + LoRA adapter; ~40–66 functions/s on one A800).

## Calibration protocol

- **SVD / REEF (V-cal, per language):** thresholds are fit on held-out calibration sets drawn from the *training-side* external corpora — disjoint from every training set and every test set (hash- and CVE-audited). Threshold selection rule: maximize positive-class F1 on the calibration set. REEF's C#/C++ reuse C's threshold. Set sizes and label rates: see `eval/calibration.py` (header) and `data/sources.md`.
- **Big-Vul:** the threshold is fit on Big-Vul's *own official validation split* (18.8k functions, never the test), yielding θ = 0.910 for the full framework.
- Rationale: calibration must never touch test data; using the benchmark's own validation split where one exists, and audited external slices elsewhere, keeps the protocol both legal and reproducible.

## Baseline provenance

All published baseline numbers are taken verbatim from the three source papers' original reports — SVD-Bench (arXiv:2503.01449), TSE 2024 (Yin et al.), and the REEF study (arXiv:2506.07503) — at the top-3 per fine-tuned family as stated in the paper. **None of the baselines is re-implemented in this repository.** Disclosure: the only published system above TwinSFT on the Big-Vul test is **SVulD** (F1 .336), a graph-based detector that is neither a fine-tuned LLM nor a fine-tuned PLM.

## FAQ / Notes

- **Why is Python's V-score (.159) below the trivial floor (.162)?** The untuned threshold is misaligned with Python's prevalence; per-language calibration restores the margin (.191). This is exactly the readout contrast Table 4 is designed to show.
- **Why does the all-positive policy reach .667 on REEF?** REEF is balanced at 50:50, so any near-all-positive policy scores .59–.67 mechanically; that is why claims on REEF are anchored in AUC as well as F1.
- **Decision-token score.** V-score reads the top-k logits at the token position immediately after the model's own "结论:" (conclusion) marker and normalizes over the vulnerable/benign verdict tokens (Eq. 1 of the paper); see `eval/readouts.py`.
- **LoRA adapters** will be released on Hugging Face after the review period.

## License & citation

Code: MIT (see `LICENSE`). Curated artifacts (prompts, samples, result JSONs): released for research use; derived from the public benchmarks listed in `data/sources.md` — follow the upstream licenses for the datasets themselves.

If you find this useful, please cite the ICASSP 2027 paper "TwinSFT: Data-Centric Multi-Task Instruction Tuning for Function-Level Vulnerability Detection".

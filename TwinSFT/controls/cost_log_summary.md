# Cost log summary (paper Sec. 4.5)

| Route | Volume | Wall-clock | Hardware | Tokens |
|---|---|---|---|---|
| GLM-5.2 API (zero-shot, 4-way concurrency) | ~72k calls, every test in the paper | ~13 h | remote | ~17M in / ~0.7M out |
| TwinSFT served locally (vLLM + LoRA) | same ~70k-sample sweep | ~30 min | 1 x A800 | local |

- Local throughput: 40–66 functions/s on one A800 (`vllm serve` with the LoRA adapter).
- Net: ~30x faster at zero marginal cost, without sending source code to a third party.
- API script with the exact prompt: `api_glm52.py` (set `GLM_API_KEY` via environment).

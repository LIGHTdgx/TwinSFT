# -*- coding: utf-8 -*-
"""eval/calibration.py — V-cal protocol (paper Sec. 2.4 / 3.3)

Rule: per language, choose theta* maximizing positive-class F1 on the held-out
calibration set, then apply theta* to the test scores. Big-Vul instead uses the
benchmark's own official validation split (theta = 0.910 for the full framework).
REEF's C#/C++ reuse C's threshold (their calibration pools are not built).

Calibration-set provenance: held-out slices of the training-side external corpora
(design: up to 133 positives + 267 negatives per language), excluded from every
training set and hash-/CVE-audited against every test set — never test data.
"""
import json

from metrics import prf  # noqa: F401  (run from eval/ dir)


def fit_threshold(pairs):
    """theta* = argmax positive-class F1 over unique calibration scores."""
    best_v, best = -1.0, None
    for th in sorted({s for _, s in pairs}):
        v = prf(pairs, th)["f1"]
        if v > best_v + 1e-12:
            best_v, best = v, th
    return best


def calibrate_f1(calib_pairs, test_pairs, theta=None):
    th = theta if theta is not None else fit_threshold(calib_pairs)
    return th, prf(test_pairs, th)["f1"]


def macro_calibrate(per_language):
    """per_language: {lang: (calib_pairs, test_pairs)}; REEF C#/C++ reuse C's theta."""
    ths = {L: fit_threshold(c) for L, (c, _) in per_language.items()}
    th_c = ths.get("C", 0.5)
    f1s, ths_out = [], {}
    for L, (_, test) in per_language.items():
        th = ths.get(L, th_c)
        ths_out[L] = th
        f1s.append(prf(test, th)["f1"])
    return ths_out, sum(f1s) / len(f1s)


def load_pairs(path):
    """Load [{"label": 0/1, "p_vuln": float}, ...] (e.g. results/score_distributions/*)."""
    d = json.load(open(path, encoding="utf-8"))
    return [(r["label"], r["p_vuln"]) for r in d["rows"] if "label" in r]


if __name__ == "__main__":
    demo = load_pairs("../results/score_distributions/bigvul_full_scores.json")
    th, f1 = calibrate_f1(demo[:1000], demo[1000:2000])
    print(f"demo calibration on bundled Big-Vul scores: theta*={th:.3f}, "
          f"held-out F1={f1:.3f} (illustrates the rule; paper theta=.910 uses the full validation split)")

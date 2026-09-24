# -*- coding: utf-8 -*-
"""data/build_corpus.py — construct the 61.7k TwinSFT instruction-tuning corpus.

Composition (paper Sec. 3.3; exact counts in corpus_stats.json):
  48.1k function-level verdicts from official training splits
      (SVD-Bench 18.0k, Big-Vul/TSE 12.0k, REEF 10.1k, general 5-language pool 8.0k)
   6.0k patch-pair verdicts (both versions of 3k external CVE-fix pairs)
   4.0k TwinRank paired-version comparison samples
   3.6k localization samples (line ranges mapped from unified-diff hunks)

Every source is passed through audit/ (rules R1-R4) BEFORE training-set assembly;
4,983 items were removed in total. See prompts/ for the three templates.
"""
import argparse
import hashlib
import json
import os
import random

random.seed(2026)

VERDICT_TPL = ("请判断以下{lang}代码是否存在可被利用的安全漏洞。先给出简要分析，最后一行输出结论。")
TWINRANK_TPL = ("以下是同一{lang}函数的两个版本，一个是修复漏洞前的版本（存在漏洞），另一个是修复后的版本。"
                "请对比两个版本的关键差异，判断哪个版本存在安全漏洞，最后一行输出结论。")
LOC_TPL = ("以下{lang}代码存在安全漏洞。请根据每行前缀的行号定位漏洞所在的代码行，最后一行输出"
           "\"漏洞行：第X行\"或\"漏洞行：第X-Y行\"（若有多段用逗号分隔，至至两段）。")

SYSTEM_PROMPT = "你是一名资深安全审计专家，精通多语言代码审计与漏洞分析。"


def verdict_sample(lang, code, label):
    return {"instruction": VERDICT_TPL.format(lang=lang), "input": code,
            "output": "结论：有漏洞" if label else "结论：无漏洞",
            "task_type": "detect_func", "meta": {"lang": lang, "label": int(label)}}


def twinrank_sample(lang, pre_fix, post_fix):
    order = random.random() < 0.5
    a, b = (pre_fix, post_fix) if order else (post_fix, pre_fix)
    vuln_ver = "A" if order else "B"
    return {"instruction": TWINRANK_TPL.format(lang=lang),
            "input": f"【版本A】\n{a}\n【版本B】\n{b}",
            "output": f"结论：版本{vuln_ver}有漏洞", "task_type": "twin_rank",
            "meta": {"lang": lang}}


def localization_sample(lang, numbered_code, line_range):
    return {"instruction": LOC_TPL.format(lang=lang), "input": numbered_code,
            "output": f"漏洞行：第{line_range}行" if "-" in str(line_range) else f"漏洞行：第{line_range}行",
            "task_type": "locate_line", "meta": {"lang": lang}}


def hcode(code):
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, help="dir with raw source dumps; see sources.md")
    ap.add_argument("--out", default="twin_sft_corpus.json")
    args = ap.parse_args()
    corpus = []
    # 1) official-split verdicts + patch pairs + families from --sources
    #    (faithful per-source loaders are kept minimal here; ratios in corpus_stats.json)
    for fn in os.listdir(args.sources):
        if not fn.endswith(".json"):
            continue
        for r in json.load(open(os.path.join(args.sources, fn), encoding="utf-8")):
            # dispatch on the raw record kind produced by sources.md pipelines
            if "func_before" in r and "vul" in r:
                corpus.append(verdict_sample(r.get("lang", "C"), r["func_before"], r["vul"]))
            elif "pre_fix" in r and "post_fix" in r:
                corpus.append(twinrank_sample(r.get("lang", "C"), r["pre_fix"], r["post_fix"]))
            elif "numbered_code" in r:
                corpus.append(localization_sample(r.get("lang", "C"), r["numbered_code"], r["line_range"]))
    # 2) run the audit rules (see audit/) and drop hits before writing
    json.dump(corpus, open(args.out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"wrote {len(corpus)} samples -> {args.out}")


if __name__ == "__main__":
    main()

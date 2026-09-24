# -*- coding: utf-8 -*-
"""controls/zero_shot.py — same-model zero-shot control.

The identical Qwen2.5-Coder-7B-Instruct backbone WITHOUT fine-tuning, using the
same system prompt and verdict template as training (closed-book, verdict-only,
temperature 0.01), served via vLLM. Serves both SVD/Big-Vul functions and REEF.
"""
import argparse
import json
import re

import requests

SYSTEM_PROMPT = "你是一名资深安全审计专家，精通多语言代码审计与漏洞分析。"
VERDICT_PROMPT = ("请判断以下{lang}代码是否存在可被利用的安全漏洞。"
                  "先给出简要分析，最后一行输出结论。\n{code}")

# robust verdict extraction: recognizes 有/无 + 存在/不存在 安全漏洞 phrasings;
# unparsable outputs count as benign (the paper convention)
VULN = re.compile(r"(有漏洞|存在(可被利用的)?(安全)?漏洞|存在安全漏洞)")
BENIGN = re.compile(r"(无漏洞|不存在(安全)?漏洞|没有(安全)?漏洞)")


def parse_label(text):
    if not text:
        return 0
    tail = text[-120:]
    if VULN.search(tail):
        return 1
    if BENIGN.search(tail):
        return 0
    return 0


def run(dataset_path, api_base, lang_key="lang", max_tokens=800, workers=32):
    data = [x for x in json.load(open(dataset_path, encoding="utf-8"))
            if (x.get("func_before") or "").strip()]
    out = []
    import concurrent.futures as cf

    def call(x):
        r = requests.post(api_base + "/chat/completions", json={
            "model": "base",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": VERDICT_PROMPT.format(
                             lang=x.get(lang_key, "C"), code=x["func_before"])}],
            "temperature": 0.01, "max_tokens": max_tokens}, timeout=300)
        return {"id": x.get("id"), "true_label": int(x["vul"]),
                "pred_label": parse_label(r.json()["choices"][0]["message"]["content"])}

    with cf.ThreadPoolExecutor(workers) as ex:
        out = list(ex.map(call, data))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--api", default="http://localhost:8000/v1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = run(a.data, a.api)
    json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(rows)} predictions -> {a.out}")

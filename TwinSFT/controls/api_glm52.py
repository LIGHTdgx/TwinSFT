# -*- coding: utf-8 -*-
"""controls/api_glm52.py — GLM-5.2 frontier-API control (paper Sec. 4.5).

Protocol: zero-shot, closed-book, verdict-only — identical system prompt and
verdict template as the zero-shot control; temperature 0.01, max_tokens 800,
4-way concurrency, resumable via a response cache. ~72k calls in total
(~13 h wall-clock). Set your key via env GLM_API_KEY (never hardcode it).
"""
import argparse
import hashlib
import json
import os
import re
import time

import requests

SYSTEM_PROMPT = "你是一名资深安全审计专家，精通多语言代码审计与漏洞分析。"
VERDICT_PROMPT = ("请判断以下{lang}代码是否存在可被利用的安全漏洞。"
                  "先给出简要分析，最后一行输出结论。\n{code}")
ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

VULN = re.compile(r"(有漏洞|存在(可被利用的)?(安全)?漏洞)")
BENIGN = re.compile(r"(无漏洞|不存在(安全)?漏洞|没有(安全)?漏洞)")


def parse_label(text):
    if not text:
        return 0
    tail = text[-120:]
    return 1 if VULN.search(tail) else (0 if BENIGN.search(tail) else 0)


def key_of(lang, code):
    return hashlib.md5((SYSTEM_PROMPT + "|0.01|800|" +
                        VERDICT_PROMPT.format(lang=lang, code=code)).encode("utf-8")).hexdigest()


def call(lang, code, cache):
    k = key_of(lang, code)
    if k in cache:
        return cache[k]
    for _ in range(5):
        try:
            r = requests.post(ENDPOINT, timeout=300, headers={
                "Authorization": "Bearer " + os.environ["GLM_API_KEY"]}, json={
                "model": "glm-5.2",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                             {"role": "user", "content": VERDICT_PROMPT.format(lang=lang, code=code)}],
                "temperature": 0.01, "max_tokens": 800})
            out = r.json()["choices"][0]["message"]["content"]
            cache[k] = out
            return out
        except Exception:
            time.sleep(5)
    raise RuntimeError("API failed after retries")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--cache", default="glm_cache.json")
    a = ap.parse_args()
    cache = json.load(open(a.cache, encoding="utf-8")) if os.path.exists(a.cache) else {}
    data = [x for x in json.load(open(a.data, encoding="utf-8")) if (x.get("func_before") or "").strip()]
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(4) as ex:  # 4-way concurrency
        outs = list(ex.map(lambda x: call(x.get("lang", "C"), x["func_before"], cache), data))
    rows = [{"id": x.get("id"), "true_label": int(x["vul"]), "pred_label": parse_label(o)}
            for x, o in zip(data, outs)]
    json.dump(cache, open(a.cache, "w", encoding="utf-8"))
    print(f"{len(rows)} predictions (cache {len(cache)})")

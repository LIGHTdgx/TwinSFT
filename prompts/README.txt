TwinSFT instruction templates
=============================

All tasks use a unified chat format: a one-line task directive, the code block,
and a one-line answer beginning with "结论:" (conclusion). The system prompt is:

    你是一名资深安全审计专家，精通多语言代码审计与漏洞分析。
    (You are a senior security auditor, expert in multi-language code audit
     and vulnerability analysis.)

verdict.txt
-----------
请判断以下{lang}代码是否存在可被利用的安全漏洞。先给出简要分析，最后一行输出结论。
Answer line: `结论：有漏洞` / `结论：无漏洞`

twinrank.txt
------------
以下是同一{lang}函数的两个版本，一个是修复漏洞前的版本（存在漏洞），另一个是修复后的版本。
请对比两个版本的关键差异，判断哪个版本存在安全漏洞，最后一行输出结论。
Presented input: 【版本A】…code… 【版本B】…code… (randomized order, A/B balanced)
Answer line: `结论：版本A有漏洞` / `结论：版本B有漏洞`

localization.txt
----------------
以下{lang}代码存在安全漏洞。请根据每行前缀的行号定位漏洞所在的代码行，最后一行输出
"漏洞行：第X行"或"漏洞行：第X-Y行"（若有多段用逗号分隔，至多两段）。
Supervision: mapped automatically from the fix commit's unified-diff hunks onto
the function's line span (1-based).

Real (code-truncated) samples for each template: see examples/.
The decision tokens for V-score are the tokens beginning with 有/无 (verdict) and
版本A/版本B (TwinRank); see eval/readouts.py.

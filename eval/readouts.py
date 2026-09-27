# -*- coding: utf-8 -*-
"""eval/readouts.py — the three verdict readouts (paper Sec. 2.4)

V-gen : parse the generated conclusion line into a hard verdict.
V-score (Eq. 1): at the token position immediately after the model's own
    "结论:" marker, read top-k logits and normalize over the decision tokens:
        p_vuln = sum_{t in V+} exp(l_t) / sum_{t in V+ u V-} exp(l_t)
    V+ / V- = tokens beginning with the vulnerable / benign verdict words
    (有… / 无…; TwinRank: 版本A / 版本B). V-score uses theta = 0.5.
V-cal : per-language thresholds fit by calibration.py applied to p_vuln.
"""
import math
import re

VULN_PAT = re.compile(r"结论\s*[:：]\s*(有漏洞|版本[AB]有漏洞|存在)")
BENIGN_PAT = re.compile(r"结论\s*[:：]\s*(无漏洞|不存在|没有)")


def parse_verdict(text):
    """V-gen: +1 vulnerable / 0 benign / None unparsed (counted benign in metrics)."""
    if not text:
        return None
    tail = text.strip().splitlines()[-1] if text.strip() else ""
    if VULN_PAT.search(tail) or VULN_PAT.search(text[-60:]):
        return 1
    if BENIGN_PAT.search(tail) or BENIGN_PAT.search(text[-60:]):
        return 0
    return None


def decision_token_score(top_logprobs, pos_prefixes=("有",), neg_prefixes=("无",)):
    """Eq. (1). top_logprobs: dict token->logprob at the conclusion position."""
    num = sum(math.exp(lp) for t, lp in top_logprobs.items()
              if any(t.startswith(p) for p in pos_prefixes))
    den = num + sum(math.exp(lp) for t, lp in top_logprobs.items()
                    if any(t.startswith(p) for p in neg_prefixes))
    return num / den if den else 0.5


def v_score(top_logprobs):
    return decision_token_score(top_logprobs)


def v_cal(p_vuln, theta):
    return 1 if p_vuln >= theta else 0

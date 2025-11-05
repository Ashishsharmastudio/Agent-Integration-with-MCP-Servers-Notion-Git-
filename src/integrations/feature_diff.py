# src/integrations/feature_diff.py
import re
from typing import Set, Tuple

_BULLET = re.compile(r"""^\s*(?:[-*•]|\d+\.)\s+|^\s*\[(?: |x|X)\]\s+""")

def _clean_feature(line: str) -> str:
    line = re.sub(r"""^\s*(?:[-*•]|\d+\.)\s+""", "", line)
    line = re.sub(r"""^\s*\[(?: |x|X)\]\s+""", "", line)
    line = re.sub(r"[^\w\s:/\-\+\.#]", "", line)
    line = re.sub(r"\s+", " ", line).strip().lower()
    return line

def extract_features_from_text(text: str) -> Set[str]:
    lines = [l.rstrip() for l in (text or "").splitlines()]
    feats = []
    capture_bias = False
    for l in lines:
        if re.match(r"^\s*#{1,6}\s+", l):
            heading = re.sub(r"^\s*#{1,6}\s+", "", l).strip().lower()
            capture_bias = any(k in heading for k in ("feature", "capabilit", "scope", "task"))
            continue
        if _BULLET.search(l) or (capture_bias and l.strip().startswith(("-", "*", "•", "[", "1."))):
            feats.append(_clean_feature(l))
    return {f for f in feats if len(f) >= 3}

def compare_feature_sets(notion_text: str, code_text: str) -> Tuple[Set[str], Set[str], Set[str]]:
    f_notion = extract_features_from_text(notion_text)
    f_code = extract_features_from_text(code_text)
    overlap = f_notion & f_code
    only_notion = f_notion - f_code
    only_code = f_code - f_notion
    return only_notion, only_code, overlap

def summarize_feature_diff(query_llm, only_notion, only_code, overlap) -> str:
    prompt = (
        "You are a concise tech lead. Summarize the feature diff.\n\n"
        f"Overlap ({len(overlap)}): {sorted(list(overlap))}\n"
        f"Only in Notion ({len(only_notion)}): {sorted(list(only_notion))}\n"
        f"Only in Code ({len(only_code)}): {sorted(list(only_code))}\n\n"
        "Give a tight, actionable summary in 5–8 bullets. Close with the top 3 gaps to prioritize."
    )
    return query_llm(prompt)

#!/usr/bin/env python3
"""One-off: mine style phrases from 22 CS reply emails."""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent / "_style_extract_raw.json"
OUT = Path(__file__).resolve().parent / "_style_phrase_mine.json"

data = json.loads(RAW.read_text(encoding="utf-8"))


def clean_body(body: str) -> str:
    for marker in ("Dear ", "DEAR "):
        idx = body.find(marker)
        if idx >= 0:
            return body[idx:]
    return body


patterns = {
    "opening_thank": r"Thank you for contacting TOPENS\.[^\n]+",
    "opening_attention": r"Thank you for your attention\.[^\n]+",
    "opening_purchase": r"Thank you for purchasing TOPENS[^\n]+",
    "opening_glad": r"(?:We are glad|It'?s great) to hear from you[^\n]*",
    "pleasure": r"It will be a pleasure to assist you today[^\n]*",
    "pleasure_heidi": r"It'?s my pleasure to personally assist you today[^\n]*",
    "empathy_std": r"I apologize for any inconvenience this may have caused[^\n]+",
    "empathy_alt": r"I'?m sorry for any frustration you'?ve experienced[^\n]+",
    "warranty_12": r"All TOPENS products are backed by a 12-month warranty[^\n]*",
    "warranty_products": r"all of our products come with a 12-month warranty[^\n]*",
    "engineer_std": r"Checked with our engineer, please help us do some tests[^\n]+",
    "engineer_alt": r"please help us do some tests to find out the problem[^\n]+",
    "result_one_by_one": r"Please let me know the result one by one[^\n]*",
    "result_each": r"(?:Kindly |Please )?(?:let me know|tell me|reply) the result(?: of)? (?:each step|one by one|every step)[^\n]*",
    "looking_forward": r"Looking forward to (?:hearing from you|your reply)[^\n]*",
    "closing_valued": r"Thank you again for being a valued customer![^\n]+",
    "closing_once": r"Thank you once again for being a valued customer![^\n]+",
    "presales_hope": r"Hope this can help you[^\n]*",
    "multi_welcome": r"You are always welcome to contact us[^\n]*",
    "ack_prior": r"I know you'?ve already done this step[^\n]*",
}

found = defaultdict(list)
for d in data:
    b = clean_body(d["body"])
    for key, pat in patterns.items():
        for m in re.finditer(pat, b, re.I):
            txt = re.sub(r"\s+", " ", m.group(0).strip())
            found[key].append({"cs_id": d["cs_id"], "text": txt[:220]})

term_patterns = [
    r"\+BAT-\s*terminals?\s*\([^)]+\)",
    r"push button terminals?\s*\([^)]+\)",
    r"[Dd][Ii][Pp] switch\s*#\d+",
    r"instant(?:aneously)? short",
    r"immediately short",
    r"ULT, COM & DLT",
    r"DLMT&COM&ULMT",
    r"O/S/C and COM",
    r"FORCE potentiometer",
    r"SOFT STOP potentiometer",
    r"release (?:the )?clutch",
    r"erase all (?:the )?remote codes",
    r"referring to the attached video",
    r"backup fuse packed within the user manual pack",
]
term_hits = defaultdict(list)
for d in data:
    b = clean_body(d["body"])
    for pat in term_patterns:
        for m in re.finditer(pat, b, re.I):
            term_hits[pat].append({"cs_id": d["cs_id"], "text": m.group(0)})

report = {
    "pattern_counts": {k: len(v) for k, v in found.items()},
    "patterns": dict(found),
    "terminology": dict(term_hits),
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", OUT)
print(json.dumps(report["pattern_counts"], indent=2))

#!/usr/bin/env python3
"""Stability probe for cs_0002 generation."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case, ref_key_hits
from evals.runners.cs_22mail_batch_runner import run_case_with_images, load_scenarios
from generate_answer import _get_config
from library_router import load_unified_libraries

libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")
scenarios = load_scenarios(ROOT / "_scratch/eval/cs_email_query_map.json")
sc = scenarios["cs_0002"]
api_key = _get_config()[0]
ref_md = (
    ROOT / "samples/customer-service-emails/0002-a8132-et24-motor-no-power.md"
).read_text(encoding="utf-8")
ref_body = ref_md.split("## 客服回复", 1)[1]
if "```" in ref_body:
    ref_body = ref_body.split("```")[1]
ref_keys = ref_key_hits(ref_body)

for i in range(5):
    row = run_case_with_images(
        sc, libs, generate=True, api_key=api_key, domain_id="topens"
    )
    d = draft_case(row, sc)
    rk = ref_key_hits(row["generated_reply_en"] or "")
    print(
        f"run {i+1}: dim2={d['dim2']} dim4={d['dim4']} "
        f"steps={row['reply_audit']['step_count']} "
        f"keys={sorted(rk)} miss={sorted(ref_keys - rk)}"
    )

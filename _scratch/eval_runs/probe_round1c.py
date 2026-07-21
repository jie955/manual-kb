#!/usr/bin/env python3
"""Round 1c stability probe for targeted cases."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case, ref_key_hits, extract_reference_reply
from evals.runners.cs_22mail_batch_runner import run_case_with_images, load_scenarios
from generate_answer import _get_config
from library_router import load_unified_libraries

TARGETS = ["cs_0021", "cs_0018", "cs_0003", "cs_0011", "cs_0007"]
RUNS = 3

libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")
scenarios = load_scenarios(ROOT / "_scratch/eval/cs_email_query_map.json")
api_key = _get_config()[0]

for sid in TARGETS:
    sc = scenarios[sid]
    md = (ROOT / sc["file"]).read_text(encoding="utf-8")
    ref = extract_reference_reply(md)
    ref_keys = ref_key_hits(ref) if ref else set()
    print(f"\n=== {sid} ref_keys={sorted(ref_keys)} ===")
    for i in range(RUNS):
        row = run_case_with_images(
            sc, libs, generate=True, api_key=api_key, domain_id="topens"
        )
        d = draft_case(row, sc)
        rk = ref_key_hits(row["generated_reply_en"] or "")
        has_amazon = "amazon" in (row["generated_reply_en"] or "").lower()
        print(
            f"  run {i+1}: dim2={d['dim2']} dim4={d['dim4']} "
            f"steps={row['reply_audit']['step_count']} "
            f"miss={sorted(ref_keys - rk)} amazon={has_amazon}"
        )

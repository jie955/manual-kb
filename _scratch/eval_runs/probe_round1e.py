#!/usr/bin/env python3
"""Round 1e probe for cs_0004 + cs_0020."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case
from evals.runners.cs_22mail_batch_runner import run_case_with_images, load_scenarios
from generate_answer import _get_config
from library_router import load_unified_libraries

TARGETS = ["cs_0004", "cs_0020"]
RUNS = 3

libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")
scenarios = load_scenarios(ROOT / "_scratch/eval/cs_email_query_map.json")
api_key = _get_config()[0]

for sid in TARGETS:
    sc = scenarios[sid]
    print(f"\n=== {sid} ===")
    for i in range(RUNS):
        row = run_case_with_images(
            sc, libs, generate=True, api_key=api_key, domain_id="topens"
        )
        d = draft_case(row, sc)
        reply = row["generated_reply_en"] or ""
        has_link = "topens.com" in reply.lower()
        print(
            f"  run {i+1}: dim2={d['dim2']} dim4={d['dim4']} "
            f"steps={row['reply_audit']['step_count']} topens_link={has_link}"
        )

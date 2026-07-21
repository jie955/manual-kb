#!/usr/bin/env python3
"""Diagnose zh_leak: old token check vs new block check."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.cs_email_workflow import run_cs_email_workflow
from context_builder import build_context_for_hits
from engine.trace import detect_context_zh_leak
from library_router import load_unified_libraries

OLD_TOKENS = ("断配件", "Internal notes", "中文排查")


def old_ctx_rows_leak(ctx_rows: list[dict]) -> bool:
    for row in ctx_rows:
        block = json.dumps(row, ensure_ascii=False)
        if any(tok in block for tok in OLD_TOKENS):
            return True
    return False


def main() -> None:
    sid = sys.argv[1] if len(sys.argv) > 1 else "cs_0025"
    libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")
    sc = json.loads(
        (ROOT / "_scratch/eval/cs_email_query_map.json").read_text(encoding="utf-8")
    )
    scenario = next(s for s in sc["scenarios"] if s["id"] == sid)
    email = (scenario.get("verbatim_customer") or [scenario.get("primary_query")])[0]
    wf = run_cs_email_workflow(
        email, libs, search_query=scenario.get("primary_query"), generate=False
    )
    blocks = build_context_for_hits(wf.gen_hits, locale="en", response_mode="cs_email")
    print(f"=== {sid} ===")
    print("old_ctx_rows:", old_ctx_rows_leak(wf.gen_hits))
    print("new_blocks:", detect_context_zh_leak(blocks))
    for i, b in enumerate(blocks):
        cjk = sum(1 for ch in b if "\u4e00" <= ch <= "\u9fff")
        markers = [m for m in ("中文排查", "断配件", "Internal notes", "章节：", "故障标题：") if m in b]
        print(f"block {i+1}: cjk={cjk} markers={markers}")
        if cjk:
            for line in b.splitlines():
                if any("\u4e00" <= ch <= "\u9fff" for ch in line):
                    print("  ", line[:120])


if __name__ == "__main__":
    main()

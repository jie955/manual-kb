#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieval A/B：baseline vs enriched × vector vs hybrid [vs rerank]。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from retrieval_engine import DEFAULT_RERANKER

DEFAULT_MODEL = (
    r"D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts"
    r"\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3"
)
EVAL_DIR = Path(__file__).resolve().parent / "eval"


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual batch retrieval A/B")
    parser.add_argument("--chunks", type=Path, default=REPO_ROOT / "_scratch/vlm_batch/chunks_enriched.json")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reranker", default=DEFAULT_RERANKER)
    args = parser.parse_args()

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    chroma = EVAL_DIR / "chroma_enriched"
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(args.chunks),
            str(chroma),
            "--model",
            args.model,
        ]
    )

    reports = []
    for label, hybrid, rerank in [
        ("enriched_vector", None, None),
        ("enriched_hybrid_0.6", "0.6", None),
        ("enriched_hybrid_0.6_rerank", "0.6", args.reranker),
    ]:
        out = EVAL_DIR / f"topk_{label}.json"
        cmd = [
            sys.executable,
            "_scratch/vlm_batch/probe_topk_misses.py",
            str(chroma),
            "--model",
            args.model,
            "--out",
            str(out),
        ]
        if rerank:
            cmd.extend(["--reranker", rerank])
        # probe_topk always runs vector+hybrid; for rerank-only mode extend probe script
        run(cmd)
        if out.is_file():
            reports.extend(json.loads(out.read_text(encoding="utf-8")))

    summary = [
        {"mode": r["mode"], "top1_pass": r["top1_pass"], "total": len(r["probes"])}
        for r in reports
    ]
    summary_path = EVAL_DIR / "ab_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

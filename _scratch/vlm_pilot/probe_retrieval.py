#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_retrieval.py

VLM 试点 5 条检索探针（需先 embed 到 chroma）。

用法:
  python probe_retrieval.py _scratch/vlm_pilot/chroma --model _scratch/modelscope/BAAI/bge-m3
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from retrieval_engine import RetrievalConfig, search

PROBES = [
    ("立柱支架和拉式开门支架怎么装", "a3s-manual-p9-step1"),
    ("A16cm B14cm 最大开门角度", "a3s-manual-p9-step2"),
    ("PHOTO 端子接光电传感器", "a3s-manual-p18-terminal-table"),
    ("BAT 端子给系统供电", "a3s-manual-p18-terminal-table"),
    ("限位开关 DLMT ULMT 怎么接", "a3s-manual-p18-terminal-table"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="VLM pilot retrieval probes")
    parser.add_argument("chroma_dir", type=Path, help="Chroma 目录")
    parser.add_argument(
        "--model",
        default=str(REPO_ROOT / "_scratch" / "modelscope" / "BAAI" / "bge-m3"),
    )
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    config = RetrievalConfig(chroma_dir=args.chroma_dir, model=args.model, k=args.k)
    passed = 0
    for query, expected in PROBES:
        hits = search(config, query)
        top = hits[0].chunk_id if hits else None
        ok = top == expected
        passed += int(ok)
        mark = "OK" if ok else "MISS"
        print(f"[{mark}] {query}")
        print(f"      expected={expected} got={top}")
        if hits:
            print(f"      score={hits[0].score}")
    print(f"\n{passed}/{len(PROBES)} Top1 match", file=sys.stderr)


if __name__ == "__main__":
    main()

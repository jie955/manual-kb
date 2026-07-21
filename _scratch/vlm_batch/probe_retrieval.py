#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VLM batch 检索探针（需先 embed 到 chroma）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from retrieval_engine import RetrievalConfig, search

DEFAULT_MODEL = (
    r"D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts"
    r"\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3"
)

PROBES = [
    # pilot 页
    ("立柱支架和拉式开门支架怎么装", "a3s-manual-p9-step1"),
    ("A16cm B14cm 最大开门角度", "a3s-manual-p9-step2"),
    ("PHOTO 端子接光电传感器", "a3s-manual-p18-terminal-table"),
    ("BAT 端子给系统供电", "a3s-manual-p18-terminal-table"),
    # batch 其他页（期望 chunk_id 前缀或包含页码）
    ("安装前重要安全注意事项", "a3s-manual-p2"),
    ("装箱清单里有什么配件", "a3s-manual-p4"),
    ("门机规格参数额定电压", "a3s-manual-p6"),
    ("Push to Open 推开门安装 STEP", "a3s-manual-p13"),
    ("控制箱怎么安装 Mount Control Box", "a3s-manual-p17"),
    ("电源接线 Connection of Power Supply", "a3s-manual-p20"),
]


def chunk_matches(expected: str, got: str) -> bool:
    if got == expected:
        return True
    # 允许命中同页 child（如 p2-warning-1）
    if got.startswith(expected + "-") or got.startswith(expected.replace("-parent", "")):
        return True
    exp_base = expected.rsplit("-", 1)[0] if "-step" in expected else expected
    return got.startswith(exp_base)


def main() -> None:
    parser = argparse.ArgumentParser(description="VLM batch retrieval probes")
    parser.add_argument(
        "chroma_dir",
        type=Path,
        nargs="?",
        default=REPO_ROOT / "_scratch" / "vlm_batch" / "chroma",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("-k", type=int, default=3)
    parser.add_argument("--hybrid", type=float, default=None, help="hybrid_alpha，如 0.6")
    args = parser.parse_args()

    config = RetrievalConfig(
        chroma_dir=args.chroma_dir,
        model=args.model,
        k=args.k,
        recall_k=41,
        hybrid_alpha=args.hybrid,
    )
    passed = 0
    for query, expected in PROBES:
        hits = search(config, query)
        top = hits[0].chunk_id if hits else None
        ok = top and chunk_matches(expected, top)
        passed += int(ok)
        mark = "OK" if ok else "MISS"
        print(f"[{mark}] {query}")
        print(f"      expected~={expected} got={top}")
        if hits:
            print(f"      score={hits[0].score:.4f}")
    print(f"\n{passed}/{len(PROBES)} Top1 match", file=sys.stderr)


if __name__ == "__main__":
    main()

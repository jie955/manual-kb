#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_topk_misses.py — 4 条 miss + 全量探针的 Top-K 诊断（Vector / Hybrid）。

用法:
  python _scratch/vlm_batch/probe_topk_misses.py
  python _scratch/vlm_batch/probe_topk_misses.py --out _scratch/vlm_batch/eval/topk_baseline.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from retrieval_engine import RetrievalConfig, search

DEFAULT_MODEL = (
    r"D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts"
    r"\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3"
)

MISS_QUERIES = [
    ("PHOTO 端子接光电传感器", "a3s-manual-p18-terminal-table"),
    ("BAT 端子给系统供电", "a3s-manual-p18-terminal-table"),
    ("Push to Open 推开门安装 STEP", "a3s-manual-p13"),
    ("电源接线 Connection of Power Supply", "a3s-manual-p20"),
]

PROBES = [
    ("立柱支架和拉式开门支架怎么装", "a3s-manual-p9-step1"),
    ("A16cm B14cm 最大开门角度", "a3s-manual-p9-step2"),
    ("PHOTO 端子接光电传感器", "a3s-manual-p18-terminal-table"),
    ("BAT 端子给系统供电", "a3s-manual-p18-terminal-table"),
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
    if got.startswith(expected + "-") or got.startswith(expected.replace("-parent", "")):
        return True
    exp_base = expected.rsplit("-", 1)[0] if "-step" in expected else expected
    return got.startswith(exp_base)


def run_mode(
    label: str,
    chroma_dir: Path,
    model: str,
    *,
    hybrid_alpha: float | None,
    reranker: str | None,
    k: int,
) -> dict:
    config = RetrievalConfig(
        chroma_dir=chroma_dir,
        model=model,
        k=k,
        recall_k=41,
        hybrid_alpha=hybrid_alpha,
        reranker_model=reranker,
    )
    report: dict = {"mode": label, "misses": [], "probes": [], "top1_pass": 0}

    for query, expected in MISS_QUERIES:
        hits = search(config, query)
        exp_rank = next(
            (h.rank for h in hits if chunk_matches(expected, h.chunk_id)),
            None,
        )
        report["misses"].append(
            {
                "query": query,
                "expected": expected,
                "expected_rank": exp_rank,
                "top5": [
                    {"rank": h.rank, "chunk_id": h.chunk_id, "score": h.score}
                    for h in hits[:k]
                ],
            }
        )

    for query, expected in PROBES:
        hits = search(config, query)
        top = hits[0].chunk_id if hits else None
        ok = bool(top and chunk_matches(expected, top))
        report["top1_pass"] += int(ok)
        exp_rank = next(
            (h.rank for h in hits if chunk_matches(expected, h.chunk_id)),
            None,
        )
        report["probes"].append(
            {
                "query": query,
                "expected": expected,
                "top1": top,
                "ok": ok,
                "expected_rank": exp_rank,
                "top1_score": hits[0].score if hits else None,
                "top5": [
                    {"rank": h.rank, "chunk_id": h.chunk_id, "score": h.score}
                    for h in hits[:k]
                ],
            }
        )

    return report


def print_report(report: dict, k: int) -> None:
    print(f"\n=== {report['mode']} — Top1 {report['top1_pass']}/{len(PROBES)} ===")
    for item in report["misses"]:
        print(f"\nMISS-Q: {item['query']}")
        print(f"  expected: {item['expected']}  rank_in_top{k}: {item['expected_rank']}")
        for h in item["top5"]:
            mark = "*" if h["chunk_id"] == item["expected"] or chunk_matches(
                item["expected"], h["chunk_id"]
            ) else " "
            print(f"  {mark} #{h['rank']} {h['chunk_id']} {h['score']:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Top-K miss diagnosis")
    parser.add_argument(
        "chroma_dir",
        type=Path,
        nargs="?",
        default=REPO_ROOT / "_scratch" / "vlm_batch" / "chroma",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--reranker", default=None)
    args = parser.parse_args()
    k = args.k

    modes = [
        ("vector", None, None),
        ("hybrid_0.6", 0.6, None),
    ]
    if args.reranker:
        modes.append(("hybrid_0.6_rerank", 0.6, args.reranker))

    all_reports = []
    for label, alpha, reranker in modes:
        report = run_mode(
            label, args.chroma_dir, args.model, hybrid_alpha=alpha, reranker=reranker, k=k
        )
        print_report(report, k)
        all_reports.append(report)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(all_reports, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nWrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()

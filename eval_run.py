#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eval_run.py

批量评测检索：Top1 / Top3 准确率（按 group_id 判定）。

用法:
  python eval_run.py _scratch/run-006/chroma_db --name baseline
  python eval_run.py _scratch/run-006/chroma_db --prefix
  python eval_run.py _scratch/run-006/chroma_db --hybrid 0.6
  python eval_run.py _scratch/run-006/chroma_db --prefix --hybrid 0.6 --rerank
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from retrieval_engine import (
    BGE_QUERY_PREFIX,
    DEFAULT_LOCAL_MODEL,
    DEFAULT_RERANKER,
    RetrievalConfig,
    load_manifest,
    search,
)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_EVAL = SCRIPT_DIR / "eval_queries.json"


def load_eval(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["queries"]


def acceptable_groups(item: dict) -> set[str]:
    groups = {item["expected_group_id"]}
    groups.update(item.get("acceptable_group_ids") or [])
    return groups


def evaluate(config: RetrievalConfig, eval_items: list[dict]) -> dict:
    chunk_by_id, _ = load_manifest(config.chroma_dir)

    top1 = 0
    top3 = 0
    rows: list[dict] = []

    for item in eval_items:
        hits = search(config, item["query"])
        hit_groups = [h.group_id for h in hits]
        ok = acceptable_groups(item)
        t1 = bool(hit_groups and hit_groups[0] in ok)
        t3 = bool(set(hit_groups[:3]) & ok)
        top1 += int(t1)
        top3 += int(t3)

        top_hit = hits[0] if hits else None
        block = chunk_by_id.get(top_hit.chunk_id, {}) if top_hit else {}
        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "expected": item["expected_group_id"],
                "acceptable": sorted(ok),
                "top1_group": hit_groups[0] if hit_groups else None,
                "top1_question": block.get("question"),
                "top1_hit": t1,
                "top3_hit": t3,
                "top3_groups": hit_groups[:3],
                "category": item.get("category"),
            }
        )

    n = len(eval_items)
    return {
        "top1_acc": round(top1 / n, 4) if n else 0.0,
        "top3_acc": round(top3 / n, 4) if n else 0.0,
        "top1_hits": top1,
        "top3_hits": top3,
        "total": n,
        "details": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieval eval on eval_queries.json")
    parser.add_argument("chroma_dir", type=Path)
    parser.add_argument("--eval", type=Path, default=DEFAULT_EVAL)
    parser.add_argument("--model", default=DEFAULT_LOCAL_MODEL)
    parser.add_argument("--name", default="run", help="实验标签")
    parser.add_argument("--prefix", action="store_true", help="BGE 查询前缀")
    parser.add_argument("--hybrid", type=float, metavar="ALPHA", help="混合检索 α（向量权重）")
    parser.add_argument("--rerank", action="store_true", help="CrossEncoder rerank Top 召回")
    parser.add_argument("--reranker-model", default=DEFAULT_RERANKER)
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--json-out", type=Path, help="写入完整结果 JSON")
    args = parser.parse_args()

    eval_items = load_eval(args.eval)
    config = RetrievalConfig(
        chroma_dir=args.chroma_dir,
        model=args.model,
        k=args.k,
        query_prefix=BGE_QUERY_PREFIX if args.prefix else None,
        hybrid_alpha=args.hybrid,
        reranker_model=args.reranker_model if args.rerank else None,
    )

    result = evaluate(config, eval_items)
    summary = {
        "name": args.name,
        "model": args.model,
        "prefix": bool(args.prefix),
        "hybrid_alpha": args.hybrid,
        "rerank": bool(args.rerank),
        **{k: result[k] for k in ("top1_acc", "top3_acc", "top1_hits", "top3_hits", "total")},
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2), file=sys.stderr)
    print(json.dumps(result["details"], ensure_ascii=False, indent=2))

    if args.json_out:
        payload = {"summary": summary, "details": result["details"]}
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()

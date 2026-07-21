#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
query_local.py

实验流水线：本地 Chroma 检索演示（支持 BGE 前缀 / hybrid / rerank）。

用法:
  python query_local.py chroma_db/ "控制板灯不亮"
  python query_local.py chroma_db/ "控制板灯不亮" --prefix --hybrid 0.6 --rerank
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
    resolve_context,
    search,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Chroma query demo")
    parser.add_argument("chroma_dir", type=Path, help="embed_ingest_local 输出目录")
    parser.add_argument("query", help="检索问句（中文为主）")
    parser.add_argument("-k", type=int, default=5, help="返回条数")
    parser.add_argument("--model", default=DEFAULT_LOCAL_MODEL)
    parser.add_argument("--prefix", action="store_true", help="BGE 查询前缀")
    parser.add_argument("--hybrid", type=float, metavar="ALPHA", help="混合检索向量权重")
    parser.add_argument("--rerank", action="store_true", help="CrossEncoder 精排")
    parser.add_argument("--reranker-model", default=DEFAULT_RERANKER)
    args = parser.parse_args()

    chunk_by_id, _ = load_manifest(args.chroma_dir)
    config = RetrievalConfig(
        chroma_dir=args.chroma_dir,
        model=args.model,
        k=args.k,
        query_prefix=BGE_QUERY_PREFIX if args.prefix else None,
        hybrid_alpha=args.hybrid,
        reranker_model=args.reranker_model if args.rerank else None,
    )

    hits = search(config, args.query)
    out = {"query": args.query, "strategy": {
        "prefix": bool(args.prefix),
        "hybrid_alpha": args.hybrid,
        "rerank": bool(args.rerank),
    }, "hits": []}

    for hit in hits:
        meta = {"chunk_id": hit.chunk_id, **hit.metadata}
        ctx = resolve_context(meta, chunk_by_id)
        out["hits"].append(
            {
                "rank": hit.rank,
                "score": hit.score,
                "group_id": hit.group_id,
                **ctx,
            }
        )

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

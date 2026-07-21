#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embed_ingest_cloud.py

实验 E：OpenAI 兼容 /embeddings API 入库（AGICTO 等网关）。

环境变量:
  EMBED_API_KEY / OPENAI_API_KEY
  EMBED_BASE_URL   默认 https://api.openai.com/v1
  EMBED_MODEL      如 text-embedding-3-small

用法:
  python embed_ingest_cloud.py chunks.json chroma_db/openai-small --model text-embedding-3-small
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from chromadb.api.types import PyEmbeddings

from embed_ingest_local import COLLECTION_NAME, chroma_metadata, load_chunks

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "text-embedding-3-small"
BATCH_SIZE = 16


def embed_batch(texts: list[str], model: str, api_key: str, base_url: str) -> list[list[float]]:
    url = base_url.rstrip("/") + "/embeddings"
    payload = json.dumps({"model": model, "input": texts}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = sorted(data["data"], key=lambda x: x["index"])
    return [item["embedding"] for item in items]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cloud OpenAI-compatible embedding ingest")
    parser.add_argument("chunks_json", type=Path)
    parser.add_argument("chroma_dir", type=Path)
    parser.add_argument("--model", default=os.environ.get("EMBED_MODEL", DEFAULT_MODEL))
    parser.add_argument("--collection", default=COLLECTION_NAME)
    args = parser.parse_args()

    api_key = os.environ.get("EMBED_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("EMBED_BASE_URL", DEFAULT_BASE_URL)
    if not api_key:
        raise SystemExit("missing EMBED_API_KEY or OPENAI_API_KEY")

    all_chunks = load_chunks(args.chunks_json)
    retrievable = [c for c in all_chunks if c.get("is_retrievable", True)]
    texts = [c["embedding_text"] for c in retrievable]

    embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        print(f"embedding batch {i // BATCH_SIZE + 1}...", file=sys.stderr)
        embeddings.extend(embed_batch(batch, args.model, api_key, base_url))
        time.sleep(0.2)

    try:
        import chromadb
    except ImportError:
        raise SystemExit("pip install -r requirements-local.txt") from None

    args.chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(args.chroma_dir))
    try:
        client.delete_collection(args.collection)
    except Exception:
        pass
    collection = client.create_collection(
        name=args.collection,
        metadata={"hnsw:space": "cosine", "embedding_model": args.model},
    )
    collection.add(
        ids=[c["chunk_id"] for c in retrievable],
        embeddings=cast(PyEmbeddings, embeddings),
        documents=texts,
        metadatas=[chroma_metadata(c) for c in retrievable],
    )

    slim = []
    for c in all_chunks:
        slim.append(
            {
                k: c.get(k)
                for k in (
                    "chunk_id", "group_id", "parent_id", "is_child", "is_retrievable",
                    "section", "question", "embedding_text", "content_zh", "content_en",
                    "answer_zh_translated", "translation_status", "images", "has_image", "lang",
                )
            }
        )
    manifest_path = args.chroma_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps({"chunks": slim}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"ingested: {len(retrievable)} -> {args.chroma_dir} model={args.model}", file=sys.stderr)


if __name__ == "__main__":
    main()

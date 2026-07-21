#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embed_ingest_local.py

实验流水线第 3 步：将 chunk_builder 产出的 chunks.json 本地向量化并写入 ChromaDB。

- Embedding：BAAI/bge-m3（本地，中文检索为主）
- 向量库：Chroma PersistentClient（纯本地，无云依赖）
- 入库范围：仅 is_retrievable == true，字段 embedding_text

用法:
  pip install -r requirements-local.txt
  python embed_ingest_local.py chunks.json chroma_db/

父块全文不在向量库中，检索演示时用同目录 manifest.json 按 parent_id 回表。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from image_utils import images_metadata_str

if TYPE_CHECKING:
    from chromadb.api.types import Metadata

from en_representation import email_example_sources_csv

DEFAULT_MODEL = "BAAI/bge-m3"
COLLECTION_NAME = "qa_troubleshooting"


def load_chunks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]
    if isinstance(data, list):
        return data
    raise SystemExit("unsupported chunks.json format")


def chroma_metadata(chunk: dict) -> Metadata:
    """Chroma metadata 只支持标量；图片列表转逗号分隔文件名。"""
    parent_id = str(chunk.get("parent_id") or "")
    doc_type = str(chunk.get("doc_type") or "troubleshooting")
    raw_models = chunk.get("models")
    if isinstance(raw_models, list):
        models_csv = ",".join(str(m) for m in raw_models if m)
    elif raw_models:
        models_csv = str(raw_models)
    else:
        models_csv = ""
    email_examples = chunk.get("email_examples") or []
    if not isinstance(email_examples, list):
        email_examples = []
    return {
        "chunk_id": str(chunk["chunk_id"]),
        "group_id": str(chunk.get("group_id") or ""),
        "parent_id": parent_id,
        "is_child": bool(chunk.get("is_child")),
        "section": str(chunk.get("section") or ""),
        "question": str(chunk.get("question") or ""),
        "has_image": bool(chunk.get("has_image")),
        "lang": str(chunk.get("lang") or ""),
        "translation_status": str(chunk.get("translation_status") or ""),
        "images": images_metadata_str(chunk.get("images")),
        "doc_type": doc_type,
        "models": models_csv,
        "has_email_examples": bool(email_examples),
        "email_example_sources": email_example_sources_csv(email_examples),
    }


def build_manifest(all_chunks: list[dict]) -> dict:
    """供 query_local 回表：chunk_id -> 块；parent 块单独索引。"""
    by_id = {c["chunk_id"]: c for c in all_chunks}
    parents = {
        c["chunk_id"]: c
        for c in all_chunks
        if not c.get("is_retrievable", True)
    }
    return {
        "chunk_by_id": by_id,
        "parent_by_id": parents,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Local bge-m3 + Chroma ingest")
    parser.add_argument("chunks_json", type=Path, help="chunk_builder 输出的 chunks.json")
    parser.add_argument("chroma_dir", type=Path, help="Chroma 持久化目录")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"默认 {DEFAULT_MODEL}")
    parser.add_argument("--collection", default=COLLECTION_NAME)
    args = parser.parse_args()

    if not args.chunks_json.is_file():
        raise SystemExit(f"file not found: {args.chunks_json}")

    all_chunks = load_chunks(args.chunks_json)
    retrievable = [c for c in all_chunks if c.get("is_retrievable", True)]
    if not retrievable:
        raise SystemExit("no retrievable chunks")

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit(
            "missing deps: pip install -r requirements-local.txt"
        ) from None

    print(f"loading model: {args.model}", file=sys.stderr)
    model = SentenceTransformer(args.model)

    texts = [c["embedding_text"] for c in retrievable]
    ids = [c["chunk_id"] for c in retrievable]
    metadatas = [chroma_metadata(c) for c in retrievable]

    print(f"encoding {len(texts)} chunks...", file=sys.stderr)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

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
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    manifest_path = args.chroma_dir / "manifest.json"
    # manifest 不含 embedding，体积可控
    slim = []
    for c in all_chunks:
        slim.append(
            {
                k: c.get(k)
                for k in (
                    "chunk_id",
                    "group_id",
                    "parent_id",
                    "is_child",
                    "is_retrievable",
                    "section",
                    "question",
                    "embedding_text",
                    "content_zh",
                    "content_en",
                    "answer_zh_translated",
                    "translation_status",
                    "images",
                    "has_image",
                    "links",
                    "has_links",
                    "negotiation_offers",
                    "customer_reply_templates",
                    "structure_warnings",
                    "troubleshooting_ladder",
                    "email_examples",
                    "lang",
                    "doc_type",
                    "models",
                )
            }
        )
    manifest_path.write_text(
        json.dumps({"chunks": slim}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"ingested: {len(retrievable)} vectors -> {args.chroma_dir}", file=sys.stderr)
    print(f"collection: {args.collection}", file=sys.stderr)
    print(f"manifest: {manifest_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

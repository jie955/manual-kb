#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retrieval_engine.py

实验检索内核：向量 / BGE 查询前缀 / BM25 混合 / CrossEncoder rerank。
供 query_local.py、eval_run.py、experiment_suite.py 共用。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from image_utils import image_filenames, normalize_images
from link_utils import normalize_links

if TYPE_CHECKING:
    from collections.abc import Mapping

    from chromadb.api.types import Metadata

COLLECTION_NAME = "qa_troubleshooting"
BGE_QUERY_PREFIX = "为这个句子生成表示："
DEFAULT_LOCAL_MODEL = "_scratch/modelscope/Xorbits/bge-small-zh-v1.5"
DEFAULT_RERANKER = "_scratch/modelscope/BAAI/bge-reranker-v2-m3"

CandidateTuple = tuple[str, float, dict[str, Any]]

_embed_model_cache: dict[str, object] = {}


def _load_embed_model(model_path: str):
    if model_path in _embed_model_cache:
        return _embed_model_cache[model_path]
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_path)
    _embed_model_cache[model_path] = model
    return model


@dataclass
class RetrievalConfig:
    chroma_dir: Path
    model: str = DEFAULT_LOCAL_MODEL
    collection: str = COLLECTION_NAME
    k: int = 5
    recall_k: int = 20
    query_prefix: str | None = None
    hybrid_alpha: float | None = None
    reranker_model: str | None = None
    doc_type: str | None = None
    models: tuple[str, ...] | None = None


@dataclass
class SearchHit:
    chunk_id: str
    group_id: str
    score: float
    rank: int
    metadata: dict[str, Any] = field(default_factory=dict)


def load_manifest(chroma_dir: Path) -> tuple[dict[str, dict], list[dict]]:
    manifest_path = chroma_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chunks = manifest["chunks"]
    chunk_by_id = {c["chunk_id"]: c for c in chunks}
    retrievable = [c for c in chunks if c.get("is_retrievable", True)]
    return chunk_by_id, retrievable


def apply_query_prefix(query: str, prefix: str | None) -> str:
    if not prefix:
        return query
    if query.startswith(prefix):
        return query
    return f"{prefix}{query}"


def tokenize_mixed(text: str) -> list[str]:
    """中英文混合 FAQ 的简单分词：英文词 + 中文单字。"""
    tokens: list[str] = []
    for part in re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", text.lower()):
        if re.fullmatch(r"[\u4e00-\u9fff]+", part):
            tokens.extend(list(part))
        else:
            tokens.append(part)
    return tokens or [text.lower()]


def bm25_index(documents: list[str]):
    from rank_bm25 import BM25Okapi  # type: ignore[reportMissingImports]

    tokenized = [tokenize_mixed(doc) for doc in documents]
    return BM25Okapi(tokenized)


def chroma_meta_to_dict(meta: Mapping[str, Any] | Metadata) -> dict[str, Any]:
    return dict(meta)


def chunk_models(chunk: dict) -> set[str]:
    raw = chunk.get("models")
    if isinstance(raw, list):
        return {str(m).strip() for m in raw if m}
    if isinstance(raw, str) and raw.strip():
        return {m.strip() for m in raw.split(",") if m.strip()}
    return set()


def chunk_matches_filter(
    chunk: dict,
    *,
    doc_type: str | None,
    models: tuple[str, ...] | None,
) -> bool:
    if doc_type is not None:
        actual = str(chunk.get("doc_type") or "troubleshooting")
        if actual != doc_type:
            return False
    if models:
        cm = chunk_models(chunk)
        if cm and not any(m in cm for m in models):
            return False
    return True


def filter_retrievable(
    retrievable: list[dict],
    *,
    doc_type: str | None,
    models: tuple[str, ...] | None,
) -> list[dict]:
    if doc_type is None and not models:
        return retrievable
    return [
        c
        for c in retrievable
        if chunk_matches_filter(c, doc_type=doc_type, models=models)
    ]


def chroma_where_clause(doc_type: str | None) -> dict[str, str] | None:
    if not doc_type:
        return None
    return {"doc_type": doc_type}


def resolve_group_id(meta: dict, chunk_by_id: dict[str, dict]) -> str:
    gid = str(meta.get("group_id") or "")
    if gid:
        return gid
    cid = str(meta.get("chunk_id") or "")
    block = chunk_by_id.get(cid, {})
    return str(block.get("group_id") or "")


def _encode_query(model, query: str, prefix: str | None) -> list[float]:
    text = apply_query_prefix(query, prefix)
    return model.encode([text], normalize_embeddings=True)[0].tolist()


def _vector_candidates(
    config: RetrievalConfig,
    query: str,
    model,
    limit: int,
) -> list[CandidateTuple]:
    import chromadb

    q_emb = _encode_query(model, query, config.query_prefix)
    client = chromadb.PersistentClient(path=str(config.chroma_dir))
    collection = client.get_collection(config.collection)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=min(limit, collection.count()),
        include=["metadatas", "distances"],
        where=chroma_where_clause(config.doc_type),
    )
    out: list[CandidateTuple] = []
    metadatas = results.get("metadatas")
    distances = results.get("distances")
    if not metadatas or not distances:
        return out
    for meta, dist in zip(metadatas[0], distances[0]):
        meta_dict = chroma_meta_to_dict(meta)
        chunk_id = str(meta_dict.get("chunk_id") or "")
        sim = 1.0 - float(dist)
        out.append((chunk_id, sim, meta_dict))
    return out


def _hybrid_candidates(
    config: RetrievalConfig,
    query: str,
    model,
    retrievable: list[dict],
    chunk_by_id: dict[str, dict],
    limit: int,
) -> list[CandidateTuple]:
    alpha = config.hybrid_alpha if config.hybrid_alpha is not None else 0.6

    vec_hits = _vector_candidates(config, query, model, limit=len(retrievable))
    vec_by_id = {cid: sim for cid, sim, _ in vec_hits}

    bm25_docs = [
        f"{c.get('question', '')} {c.get('embedding_text', '')}" for c in retrievable
    ]
    bm25 = bm25_index(bm25_docs)
    bm25_scores = bm25.get_scores(tokenize_mixed(query))
    max_bm25 = max(bm25_scores) if len(bm25_scores) else 1.0
    if max_bm25 <= 0:
        max_bm25 = 1.0

    meta_by_id = {
        c["chunk_id"]: {
            "chunk_id": c["chunk_id"],
            "group_id": c.get("group_id", ""),
            "parent_id": c.get("parent_id") or "",
            "question": c.get("question", ""),
        }
        for c in retrievable
    }

    combined: list[CandidateTuple] = []
    for i, c in enumerate(retrievable):
        cid = c["chunk_id"]
        vec_sim = vec_by_id.get(cid, 0.0)
        bm25_norm = float(bm25_scores[i]) / max_bm25
        score = alpha * vec_sim + (1.0 - alpha) * bm25_norm
        combined.append((cid, score, meta_by_id[cid]))

    combined.sort(key=lambda x: x[1], reverse=True)
    return combined[:limit]


def _rerank(
    config: RetrievalConfig,
    query: str,
    candidates: list[tuple[str, float, dict]],
    chunk_by_id: dict[str, dict],
) -> list[CandidateTuple]:
    if not config.reranker_model or not candidates:
        return candidates

    from sentence_transformers import CrossEncoder

    reranker = CrossEncoder(config.reranker_model)
    pairs = []
    for cid, _, meta in candidates:
        block = chunk_by_id.get(cid, {})
        doc = block.get("embedding_text") or meta.get("question", "")
        pairs.append((query, str(doc)[:512]))
    scores = reranker.predict(pairs)
    reranked = [
        (cid, float(score), meta)
        for (cid, _, meta), score in zip(candidates, scores)
    ]
    reranked.sort(key=lambda x: x[1], reverse=True)
    return reranked


def search(config: RetrievalConfig, query: str) -> list[SearchHit]:
    chunk_by_id, retrievable = load_manifest(config.chroma_dir)
    retrievable = filter_retrievable(
        retrievable,
        doc_type=config.doc_type,
        models=config.models,
    )
    if not retrievable:
        return []

    model = _load_embed_model(config.model)

    recall_k = max(config.k, config.recall_k)
    if config.reranker_model:
        recall_k = max(recall_k, 10)

    if config.hybrid_alpha is not None:
        candidates = _hybrid_candidates(
            config, query, model, retrievable, chunk_by_id, recall_k
        )
    else:
        candidates = _vector_candidates(config, query, model, recall_k)
        allowed = {c["chunk_id"] for c in retrievable}
        candidates = [t for t in candidates if t[0] in allowed]

    if config.reranker_model:
        candidates = _rerank(config, query, candidates, chunk_by_id)

    hits: list[SearchHit] = []
    for rank, (chunk_id, score, meta) in enumerate(candidates[: config.k], start=1):
        group_id = resolve_group_id(meta, chunk_by_id)
        hits.append(
            SearchHit(
                chunk_id=chunk_id,
                group_id=group_id,
                score=round(score, 4),
                rank=rank,
                metadata=meta,
            )
        )
    return hits


def resolve_context(hit_meta: dict, chunk_by_id: dict) -> dict:
    """子块命中 → 回 parent；否则返回自身。"""
    parent_id = hit_meta.get("parent_id") or ""
    chunk_id = hit_meta["chunk_id"]
    if parent_id and parent_id in chunk_by_id:
        block = chunk_by_id[parent_id]
        role = "parent_via_child"
        matched_child = chunk_by_id.get(chunk_id)
    else:
        block = chunk_by_id.get(chunk_id, {})
        role = "direct"
        matched_child = None

    images = normalize_images(block.get("images"))
    links = normalize_links(block.get("links"))
    content_zh = block.get("content_zh")
    content_en = block.get("content_en")
    section = block.get("section")
    question = block.get("question")

    if matched_child and role == "parent_via_child":
        child_images = normalize_images(matched_child.get("images"))
        if child_images:
            images = child_images
        if not (content_en or "").strip():
            content_en = matched_child.get("content_en") or content_en
        if not (content_zh or "").strip():
            content_zh = matched_child.get("content_zh") or content_zh
        if not section:
            section = matched_child.get("section") or section
        if not question:
            question = matched_child.get("question") or question
        if not links:
            links = normalize_links(matched_child.get("links"))

    doc_type = block.get("doc_type") or hit_meta.get("doc_type")
    if not images and doc_type == "installation_manual":
        group_id = block.get("group_id") or hit_meta.get("group_id") or ""
        for c in chunk_by_id.values():
            if c.get("group_id") != group_id:
                continue
            cand = normalize_images(c.get("images"))
            if cand:
                images = cand
                break

    return {
        "resolve_role": role,
        "matched_chunk_id": chunk_id,
        "parent_id": parent_id or None,
        "section": section,
        "question": question,
        "content_zh": content_zh,
        "content_en": content_en,
        "images": images,
        "image_files": image_filenames(images),
        "links": links,
        "negotiation_offers": block.get("negotiation_offers") or [],
        "customer_reply_templates": block.get("customer_reply_templates") or [],
        "structure_warnings": block.get("structure_warnings") or [],
        "troubleshooting_ladder": block.get("troubleshooting_ladder") or [],
        "translation_status": block.get("translation_status"),
        "doc_type": doc_type,
        "matched_child_snippet": (
            (matched_child or {}).get("content_zh")
            or (matched_child or {}).get("embedding_text")
        ),
    }

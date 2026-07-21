#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三库统一入口：机型关键词路由 + fan-out 兜底（ADR-0002 §7）。

产品/索引/路由规则来自 domains/<id>/；本模块保留兼容符号与函数名。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from domains.loader import get_default_domain
from domains.models import DomainConfig, RoutingPolicy
from retrieval_engine import RetrievalConfig, SearchHit, resolve_context, search

REPO_ROOT = Path(__file__).resolve().parent


def _domain() -> DomainConfig:
    return get_default_domain()


def _library_specs() -> list[dict[str, str]]:
    return _domain().library_specs()


def _en_chroma_dirs() -> dict[str, str]:
    return _domain().en_chroma_dirs()


def _merged_chroma_dirs() -> dict[str, str]:
    return _domain().merged_chroma_dirs()


def _catalog_links() -> list[dict[str, str]]:
    return _domain().product_catalog_links()


# Compatibility symbols — tests and qa_server import these names.
# Values are generated from the active domain pack at import time.
LIBRARY_SPECS: list[dict[str, str]] = _library_specs()
EN_CHROMA_DIRS: dict[str, str] = _en_chroma_dirs()
MERGED_CHROMA_DIRS: dict[str, str] = _merged_chroma_dirs()
PRODUCT_CATALOG_LINKS: list[dict[str, str]] = _catalog_links()


def _compile_keyword_patterns(
    policy: RoutingPolicy | None = None,
) -> list[tuple[str, re.Pattern[str]]]:
    routing = policy or _domain().routing
    return [
        (kp.product_id, re.compile(kp.pattern, re.I))
        for kp in routing.keyword_patterns
    ]


_KEYWORD_PATTERNS: list[tuple[str, re.Pattern[str]]] = _compile_keyword_patterns()


def resolve_chroma_dir(library_id: str, *, index: str = "zh") -> Path:
    if index == "en":
        rel = EN_CHROMA_DIRS.get(library_id)
        if not rel:
            raise ValueError(f"no EN chroma for library: {library_id}")
        return REPO_ROOT / rel
    for spec in LIBRARY_SPECS:
        if spec["id"] == library_id:
            return REPO_ROOT / spec["chroma_dir"]
    raise ValueError(f"unknown library: {library_id}")


def resolve_merged_chroma_dir(library_id: str) -> Path:
    rel = MERGED_CHROMA_DIRS.get(library_id)
    if not rel:
        raise ValueError(f"no merged chroma for library: {library_id}")
    return REPO_ROOT / rel


def filter_library_specs(allowed_libraries: list[str] | None) -> list[dict[str, str]]:
    if not allowed_libraries:
        return list(LIBRARY_SPECS)
    allowed = {x.strip() for x in allowed_libraries if x.strip()}
    return [s for s in LIBRARY_SPECS if s["id"] in allowed]


@dataclass
class UnifiedLibrary:
    library_id: str
    label: str
    doc_title: str
    config: RetrievalConfig
    chunk_by_id: dict[str, dict[str, Any]]
    manual_config: RetrievalConfig | None = None


@dataclass
class RoutingResult:
    matched_library: str
    matched_library_label: str
    routing_method: str  # keyword | fan_out | forced
    library_scores: dict[str, float]
    keyword_hits: list[str]


def detect_library_hints(query: str) -> list[str]:
    hits: list[str] = []
    for lib_id, pattern in _KEYWORD_PATTERNS:
        if pattern.search(query):
            hits.append(lib_id)
    return hits


def load_unified_libraries(
    model: str,
    *,
    k: int = 3,
    index: str = "zh",
    merged: bool = False,
    allowed_libraries: list[str] | None = None,
) -> dict[str, UnifiedLibrary]:
    from retrieval_engine import RetrievalConfig, load_manifest

    out: dict[str, UnifiedLibrary] = {}
    for spec in filter_library_specs(allowed_libraries):
        lib_id = spec["id"]
        ts_chroma = resolve_chroma_dir(lib_id, index=index)
        if not ts_chroma.is_dir():
            raise FileNotFoundError(f"chroma dir not found: {ts_chroma}")

        manual_config: RetrievalConfig | None = None
        chunk_by_id: dict[str, dict[str, Any]] = {}

        if merged:
            merged_dir = resolve_merged_chroma_dir(lib_id)
            if not merged_dir.is_dir():
                raise FileNotFoundError(f"merged chroma dir not found: {merged_dir}")
            merged_chunk_by_id, _ = load_manifest(merged_dir)
            ts_chunk_by_id, _ = load_manifest(ts_chroma)
            chunk_by_id = {**merged_chunk_by_id, **ts_chunk_by_id}
            if index == "en":
                ts_search_dir = ts_chroma
                ts_doc_type = None
            else:
                ts_search_dir = merged_dir
                ts_doc_type = "troubleshooting"
            config = RetrievalConfig(
                chroma_dir=ts_search_dir,
                model=model,
                k=k,
                doc_type=ts_doc_type,
            )
            manual_config = RetrievalConfig(
                chroma_dir=merged_dir,
                model=model,
                k=1,
                doc_type="installation_manual",
            )
        else:
            ts_chunk_by_id, _ = load_manifest(ts_chroma)
            chunk_by_id = ts_chunk_by_id
            config = RetrievalConfig(chroma_dir=ts_chroma, model=model, k=k)

        out[lib_id] = UnifiedLibrary(
            library_id=lib_id,
            label=spec["label"],
            doc_title=spec["doc_title"],
            config=config,
            chunk_by_id=chunk_by_id,
            manual_config=manual_config,
        )
    return out


def _top1_score(lib: UnifiedLibrary, query: str) -> float:
    hits = search(lib.config, query)
    return hits[0].score if hits else 0.0


def _match_special_rules(
    query: str,
    libraries: dict[str, UnifiedLibrary],
    *,
    policy: RoutingPolicy | None = None,
) -> str | None:
    routing = policy or _domain().routing
    for rule in routing.special_rules:
        if rule.product_id not in libraries:
            continue
        if not re.search(rule.pattern, query, re.I):
            continue
        if any(re.search(ex, query, re.I) for ex in rule.exclude_patterns):
            continue
        if rule.require_patterns and not all(
            re.search(req, query, re.I) for req in rule.require_patterns
        ):
            continue
        return rule.product_id
    return None


def pick_library(
    query: str,
    libraries: dict[str, UnifiedLibrary],
    *,
    force_library: str | None = None,
) -> RoutingResult:
    if force_library:
        if force_library not in libraries:
            raise ValueError(f"unknown library: {force_library}")
        lib = libraries[force_library]
        return RoutingResult(
            matched_library=force_library,
            matched_library_label=lib.label,
            routing_method="forced",
            library_scores={force_library: _top1_score(lib, query)},
            keyword_hits=[],
        )

    hints = detect_library_hints(query)
    scores = {lid: _top1_score(lib, query) for lid, lib in libraries.items()}

    special = _match_special_rules(query, libraries)
    if special:
        return RoutingResult(
            matched_library=special,
            matched_library_label=libraries[special].label,
            routing_method="keyword",
            library_scores=scores,
            keyword_hits=[special],
        )

    if len(hints) == 1:
        lid = hints[0]
        return RoutingResult(
            matched_library=lid,
            matched_library_label=libraries[lid].label,
            routing_method="keyword",
            library_scores=scores,
            keyword_hits=hints,
        )

    if len(hints) > 1:
        best_hint = max(hints, key=lambda lid: scores[lid])
        return RoutingResult(
            matched_library=best_hint,
            matched_library_label=libraries[best_hint].label,
            routing_method="keyword",
            library_scores=scores,
            keyword_hits=hints,
        )

    best_id = max(scores, key=scores.get)
    return RoutingResult(
        matched_library=best_id,
        matched_library_label=libraries[best_id].label,
        routing_method="fan_out" if not hints else "keyword",
        library_scores=scores,
        keyword_hits=hints,
    )


def unified_search(
    query: str,
    libraries: dict[str, UnifiedLibrary],
    *,
    force_library: str | None = None,
    include_manual: bool = False,
) -> tuple[RoutingResult, list[SearchHit]]:
    routing = pick_library(query, libraries, force_library=force_library)
    lib = libraries[routing.matched_library]
    hits = search(lib.config, query)
    if include_manual and lib.manual_config:
        manual_hits = search(lib.manual_config, query)
        if manual_hits:
            base = len(hits)
            top_manual = manual_hits[0]
            if top_manual.score >= 0.35 and (
                not hits or top_manual.group_id != hits[0].group_id
            ):
                hits = list(hits) + [
                    SearchHit(
                        chunk_id=top_manual.chunk_id,
                        group_id=top_manual.group_id,
                        score=top_manual.score,
                        rank=base + 1,
                        metadata={
                            **top_manual.metadata,
                            "doc_type": "installation_manual",
                            "supplement": "manual",
                        },
                    )
                ]
    return routing, hits


def hits_to_context(
    hits: list[SearchHit],
    chunk_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for hit in hits:
        meta = {"chunk_id": hit.chunk_id, **hit.metadata}
        rows.append(
            {
                "rank": hit.rank,
                "score": hit.score,
                "group_id": hit.group_id,
                **resolve_context(meta, chunk_by_id),
            }
        )
    return rows

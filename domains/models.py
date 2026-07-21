#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Typed domain configuration objects (ADR · 企业 RAG 组件化)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProductSpec:
    id: str
    label: str
    doc_title: str
    aliases: tuple[str, ...] = ()
    display_order: int = 0


@dataclass(frozen=True)
class CatalogLink:
    family: str
    label: str
    url: str
    kind: str = "catalog"


@dataclass(frozen=True)
class IndexBinding:
    product_id: str
    chroma_zh: str
    chroma_en: str
    chroma_merged: str


@dataclass(frozen=True)
class KeywordPattern:
    product_id: str
    pattern: str


@dataclass(frozen=True)
class SpecialRouteRule:
    product_id: str
    pattern: str
    exclude_patterns: tuple[str, ...] = ()
    require_patterns: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class RoutingPolicy:
    keyword_patterns: tuple[KeywordPattern, ...]
    special_rules: tuple[SpecialRouteRule, ...]
    fallback: str = "fan_out"


@dataclass(frozen=True)
class ContextPolicy:
    cs_email_en_max_chars: int = 3200
    score_margin_top1_only: float = 0.012
    top1_excludes: dict[str, frozenset[str]] = field(default_factory=dict)
    forbid_content_zh_in_en: bool = True


@dataclass(frozen=True)
class ResponsePolicy:
    default_locale: str = "en"
    default_response_mode: str = "cs_email"
    context: ContextPolicy = field(default_factory=ContextPolicy)


@dataclass(frozen=True)
class DomainMeta:
    id: str
    display_name: str
    default_locale: str = "en"
    default_response_mode: str = "cs_email"
    brand: str = ""


@dataclass(frozen=True)
class StyleFamilySpec:
    family_id: str
    exemplar_relpath: str
    keywords: tuple[str, ...]
    email_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class StylePack:
    root: Path
    version: str
    default_family: str
    group_hints: dict[str, str]
    families: dict[str, StyleFamilySpec]
    principles_path: Path
    hold_out_gate: frozenset[str]
    scenario_map_path: Path
    presales_types: frozenset[str]
    warranty_scenario_substring: str
    scenario_overrides: dict[str, str]


@dataclass(frozen=True)
class PromptPack:
    root: Path
    version: str
    cs_email_system_en: str
    qa_system_en: str
    qa_system_zh: str


@dataclass
class DomainConfig:
    """Loaded domain pack — single source for product/index/routing/policy."""

    meta: DomainMeta
    products: tuple[ProductSpec, ...]
    catalog_links: tuple[CatalogLink, ...]
    indices: dict[str, IndexBinding]
    routing: RoutingPolicy
    response: ResponsePolicy
    style: StylePack
    prompts: PromptPack
    root: Path
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def library_specs(self) -> list[dict[str, str]]:
        ordered = sorted(self.products, key=lambda p: p.display_order)
        out: list[dict[str, str]] = []
        for p in ordered:
            binding = self.indices.get(p.id)
            if not binding:
                raise KeyError(f"missing index binding for product: {p.id}")
            out.append(
                {
                    "id": p.id,
                    "label": p.label,
                    "doc_title": p.doc_title,
                    "chroma_dir": binding.chroma_zh,
                }
            )
        return out

    def en_chroma_dirs(self) -> dict[str, str]:
        return {pid: b.chroma_en for pid, b in self.indices.items()}

    def merged_chroma_dirs(self) -> dict[str, str]:
        return {pid: b.chroma_merged for pid, b in self.indices.items()}

    def product_catalog_links(self) -> list[dict[str, str]]:
        return [
            {
                "family": c.family,
                "label": c.label,
                "url": c.url,
                "kind": c.kind,
            }
            for c in self.catalog_links
        ]

    def product_ids(self) -> list[str]:
        return [p.id for p in sorted(self.products, key=lambda x: x.display_order)]

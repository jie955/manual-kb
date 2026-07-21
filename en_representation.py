#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EN-primary retrieval representation (ADR-0001 · ADR-0003)."""

from __future__ import annotations

import re

MIN_EN_SUBSTANCE = 80


def build_embedding_text_en(
    question: str,
    content_en: str,
    *,
    symptom_keywords: str = "",
) -> str:
    """Symptom-level EN embed text: fault title + EN steps + optional keywords."""
    parts: list[str] = []
    q = (question or "").strip()
    en = (content_en or "").strip()
    kw = (symptom_keywords or "").strip()
    if q:
        parts.append(q)
    if en:
        parts.append(en)
    if kw:
        parts.append(kw)
    return "\n".join(parts)


def en_retrieval_ready(answer_en: str | None, *, min_len: int = MIN_EN_SUBSTANCE) -> bool:
    return len((answer_en or "").strip()) >= min_len


def classify_en_readiness(
    *,
    answer_en: str | None,
    answer_zh: str | None,
    has_templates: bool,
    is_gate_group: bool,
) -> str:
    """
    Returns: ready | enrich | blocking
    """
    en = (answer_en or "").strip()
    zh = (answer_zh or "").strip()
    if en_retrieval_ready(en):
        if zh and len(en) < len(zh) * 0.25 and len(zh) > 200:
            return "enrich"
        return "ready"
    if not en and (len(zh) > 80 or has_templates):
        return "blocking"
    if is_gate_group and len(en) < MIN_EN_SUBSTANCE:
        return "blocking"
    if en:
        return "enrich"
    return "blocking" if is_gate_group else "enrich"


def extract_en_symptom_keywords(question: str) -> str:
    """Pull English tokens from bilingual fault title for enrich overlay."""
    if not question:
        return ""
    # segments after · often carry EN symptom phrases
    parts = re.split(r"[·\|]", question)
    en_bits = [p.strip() for p in parts if re.search(r"[A-Za-z]{3,}", p)]
    return " · ".join(en_bits[:4])


def email_verbatim_from_example(example: dict) -> str:
    """Customer-side text only — never CS Reference reply."""
    return (example.get("verbatim") or example.get("customer_verbatim") or "").strip()


def append_email_verbatim_to_embedding(
    base: str,
    email_examples: list[dict] | None,
) -> str:
    """
    A-line · Grounding: append customer verbatim variants to embedding_text.
    ADR-0003: Reference reply must not enter embedding; customer email may.
    """
    if not email_examples:
        return (base or "").strip()
    lines: list[str] = []
    for ex in email_examples:
        verbatim = email_verbatim_from_example(ex)
        if not verbatim:
            continue
        tag = ex.get("scenario_id") or ex.get("source") or "email"
        lines.append(f"[Customer email · {tag}] {verbatim}")
    if not lines:
        return (base or "").strip()
    return f"{(base or '').rstrip()}\n\n[Customer reported variants]\n" + "\n".join(lines)


def email_example_sources_csv(email_examples: list[dict] | None) -> str:
    if not email_examples:
        return ""
    sources: list[str] = []
    for ex in email_examples:
        sid = ex.get("scenario_id") or ""
        if sid:
            sources.append(str(sid))
    return ",".join(sources)

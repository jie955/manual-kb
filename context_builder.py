#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM context assembly — locale / response_mode policy lives here, not in generate_answer.

CS email group-exclusion and length limits come from the active domain pack.
"""

from __future__ import annotations

import re

from display_content_utils import supplement_en_text
from domains.loader import get_default_domain
from domains.models import ContextPolicy
from image_utils import localize_images
from link_utils import display_link_label


def _context_policy() -> ContextPolicy:
    return get_default_domain().response.context


def filter_hits_for_cs_email(
    hits: list[dict],
    *,
    scores: list[float] | None = None,
    force_include_groups: frozenset[str] | None = None,
) -> list[dict]:
    """Reduce top3 context pollution for cs_email when Top1 is the authoritative group."""
    if not hits:
        return hits
    policy = _context_policy()
    top1_gid = str(hits[0].get("group_id") or "")
    exclude = policy.top1_excludes.get(top1_gid)
    keep = force_include_groups or frozenset()
    if exclude:
        filtered = [
            h
            for h in hits
            if str(h.get("group_id") or "") not in exclude
            or str(h.get("group_id") or "") in keep
        ]
        if filtered:
            base = filtered[:3]
            for h in hits:
                if h.get("doc_type") == "installation_manual" and h not in base:
                    base.append(h)
                    break
            return base[:4]
    margin = policy.score_margin_top1_only
    if scores and len(scores) >= 2 and scores[0] - scores[1] >= margin:
        filtered = hits[:1]
    else:
        filtered = hits[:3]
    for h in hits[len(filtered) :]:
        if h.get("doc_type") == "installation_manual":
            filtered.append(h)
            break
    return filtered[:4]


def _latin_ratio(text: str) -> float:
    if not text:
        return 0.0
    latin = sum(1 for ch in text if ord(ch) < 128)
    return latin / len(text)


def _strip_cjk(text: str) -> str:
    cleaned = re.sub(r"[\u4e00-\u9fff]+", " ", text or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ·-|")
    return cleaned


def _en_section_label(section: str) -> str:
    sec = (section or "").strip()
    if not sec:
        return ""
    en_tokens = [t for t in sec.split() if t and ord(t[0]) < 128]
    label = " ".join(en_tokens) if en_tokens else _strip_cjk(sec)
    return label


def _en_fault_title(question: str, section: str, content_en: str) -> str:
    """English-only fault label for EN cs_email context (ADR-0003 P-1)."""
    q = (question or "").strip()
    if q:
        parts = re.split(r"\s*[·•]\s*", q)
        en_parts = [
            _strip_cjk(p.strip())
            for p in parts
            if _latin_ratio(p) >= 0.55 and len(p.strip()) >= 8
        ]
        en_parts = [p for p in en_parts if len(p) >= 8]
        if en_parts:
            return " · ".join(en_parts)[:240]
        latin_tokens = re.findall(r"[A-Za-z0-9][\w\s/\-\.\'\",:;()]+", q)
        latin_joined = " ".join(t.strip() for t in latin_tokens if len(t.strip()) >= 3)
        if len(latin_joined) >= 12:
            return latin_joined[:240]
    sec_en = _en_section_label(section)
    if sec_en and _latin_ratio(sec_en) >= 0.8:
        return sec_en[:240]
    return "Fault reference (see English steps below)"


def _compress_en_for_cs_email(
    content_en: str,
    *,
    max_chars: int | None = None,
) -> str:
    """Keep cs_email context focused — long qa_011-style forks blow output tokens."""
    if max_chars is None:
        max_chars = _context_policy().cs_email_en_max_chars
    text = (content_en or "").strip()
    if len(text) <= max_chars:
        return text
    step_starts = [m.start() for m in re.finditer(r"(?m)^\s*\d+[\.\．、]\s", text)]
    if len(step_starts) >= 5:
        text = text[: step_starts[4]].rstrip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[... truncated for email context; use only steps shown above]"


def build_context_block(
    hit: dict,
    *,
    locale: str = "zh",
    response_mode: str = "qa",
) -> str:
    """Format one retrieval hit for LLM reference context."""
    content_zh = hit.get("content_zh") or ""
    content_en = hit.get("content_en") or ""
    en_mode = locale == "en"
    cs_email = response_mode == "cs_email"
    if en_mode:
        lines = [
            f"Section: {_en_section_label(hit.get('section') or '')}",
            f"Fault title: {_en_fault_title(hit.get('question') or '', hit.get('section') or '', content_en)}",
        ]
        if content_en.strip():
            body = content_en.strip()
            if cs_email:
                body = _compress_en_for_cs_email(body)
            lines.append(f"English troubleshooting steps:\n{body}")
        else:
            lines.append(
                "(No English troubleshooting steps in this reference.)"
            )
    else:
        lines = [
            f"章节：{hit.get('section') or ''}",
            f"故障标题：{hit.get('question') or ''}",
            f"中文排查步骤：\n{content_zh.strip() or '(无中文步骤)'}",
        ]
    images = hit.get("images") or []
    if images:
        if en_mode:
            images = localize_images(images, "en")
        label = "Images:" if en_mode else "配图说明："
        lines.append(label)
        for img in images:
            if isinstance(img, dict):
                fname = img.get("file") or ""
                if en_mode:
                    cap = (img.get("caption_en") or "").strip()
                else:
                    cap = img.get("caption") or ""
                if cap:
                    lines.append(f"  - {fname}: {cap}")
                elif fname:
                    lines.append(f"  - {fname}")
    links = hit.get("links") or []
    if links:
        link_label = (
            "Reference links (include in reply when relevant):"
            if en_mode
            else "参考链接（须在回答中列出，可点击）："
        )
        lines.append(link_label)
        for lk in links:
            if isinstance(lk, dict):
                label = display_link_label(lk, locale)
                url = lk.get("url") or ""
                kind = lk.get("link_type") or "other"
                if url:
                    lines.append(f"  - [{label}]({url}) ({kind})")
    templates = hit.get("customer_reply_templates") or []
    if templates:
        return "\n".join(lines)
    if not en_mode:
        en_sup = supplement_en_text(content_zh, content_en)
        if en_sup:
            lines.append(f"英文操作步骤（中文过短，须参考）：\n{en_sup[:2000]}")
        elif content_en and not content_zh:
            lines.append(f"英文原文（仅供参考）：\n{content_en[:1200]}")
    elif content_en.strip():
        en_sup = supplement_en_text(content_zh, content_en)
        if en_sup and en_sup.strip() != content_en.strip():
            lines.append(f"Additional English detail:\n{en_sup[:2000]}")
    return "\n".join(lines)


def build_context_for_hits(
    hits: list[dict],
    *,
    locale: str = "zh",
    response_mode: str = "qa",
    max_hits: int = 3,
    force_include_groups: frozenset[str] | None = None,
) -> list[str]:
    """Format Top-K hits as labeled reference blocks for the LLM user message."""
    if response_mode == "cs_email":
        hits = filter_hits_for_cs_email(
            hits, force_include_groups=force_include_groups
        )
        max_hits = min(max_hits, len(hits) or max_hits)
    parts: list[str] = []
    for i, hit in enumerate(hits[:max_hits], start=1):
        ref_label = f"Reference {i}" if locale == "en" else f"参考资料 {i}"
        block = build_context_block(hit, locale=locale, response_mode=response_mode)
        parts.append(f"--- {ref_label} ---\n{block}")
    return parts

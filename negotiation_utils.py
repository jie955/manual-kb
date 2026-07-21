#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""客服一次性协商话术识别：结构特征为主，非单纯关键词表。"""

from __future__ import annotations

import re

# 免责声明（常紧邻协商句）
DISCLAIMER_RE = re.compile(
    r"(?:"
    r"do not have .{0,120}? for sale in our store"
    r"|don't have .{0,120}? for sale"
    r"|not have .{0,120}? for sale in our store"
    r"|Regretfully,?\s+we do not have"
    r"|Sorry for the inconvenience"
    r"|we do not have this .{0,80}? for sale"
    r")",
    re.IGNORECASE | re.DOTALL,
)

# 协商提议：征询式 / 补偿式（结构特征）
NEGOTIATION_CLAUSE_RE = re.compile(
    r"(?:"
    r"(?:If you are willing|If you're willing).{0,200}?"
    r"(?:would like to send|we would like to send).{0,200}?"
    r"(?:cover the cost|to cover).{0,120}?"
    r"Is it acceptable\??"
    r"|"
    r"(?:we would like to send|would like to send) you .{0,160}?"
    r"(?:cover the cost|to cover).{0,120}?"
    r"Is it acceptable\??"
    r"|"
    r"(?:可以接受吗|愿意尝试的话).{0,120}?"
    r"(?:送|抵).{0,80}?"
    r"(?:可以接受|是否同意)"
    r")",
    re.IGNORECASE | re.DOTALL,
)

# 整句即为协商（短句、以征询结尾）
NEGOTIATION_SENTENCE_RE = re.compile(
    r"^(?:"
    r".*(?:would like to send|we would like to send).{0,200}?"
    r"(?:cover the cost|to cover).{0,80}?"
    r"Is it acceptable\??"
    r"|"
    r".*(?:可以接受吗|是否愿意接受)"
    r")$",
    re.IGNORECASE | re.DOTALL,
)


def extract_negotiation_clauses(text: str) -> list[str]:
    """从段落中提取协商话术子串（可多条）。"""
    if not (text or "").strip():
        return []
    found: list[str] = []
    for m in NEGOTIATION_CLAUSE_RE.finditer(text):
        clause = m.group(0).strip()
        if clause and clause not in found:
            found.append(clause)
    if found:
        return found
    # 按句切分再判整句
    for part in re.split(r"(?<=[.!?？])\s+", text):
        part = part.strip()
        if not part:
            continue
        if NEGOTIATION_SENTENCE_RE.match(part):
            found.append(part)
    return found


def strip_negotiation_from_text(text: str) -> tuple[str, list[str]]:
    """
    移除协商话术，返回 (清洗后正文, 被移除的协商片段列表)。
    要求：命中协商子句时，同段内通常已有免责声明（结构约束，降低误杀）。
    """
    if not (text or "").strip():
        return text, []

    offers = extract_negotiation_clauses(text)
    if not offers:
        return text, []

    # 结构约束：协商句附近应有「不卖/不便」类免责，避免 lone keyword 误杀
    if not DISCLAIMER_RE.search(text):
        # 整句协商且含征询问句时仍允许（如独立邮件段）
        if not any("acceptable" in o.lower() or "可以接受" in o for o in offers):
            return text, []

    cleaned = text
    for offer in offers:
        cleaned = cleaned.replace(offer, " ")
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r" +\n", "\n", cleaned)
    cleaned = re.sub(r"\n +", "\n", cleaned)
    return cleaned.strip(), offers


def negotiation_offers_from_text(text: str, lang: str) -> tuple[str, list[dict]]:
    """返回 (清洗后文本, negotiation_offers 列表)。"""
    cleaned, clauses = strip_negotiation_from_text(text)
    offers = [
        {"text": c, "lang": lang, "content_role": "negotiation_offer"}
        for c in clauses
        if c.strip()
    ]
    return cleaned, offers

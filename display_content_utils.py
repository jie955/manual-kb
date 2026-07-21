#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo / LLM 展示：content_zh 过薄时判定是否应补充 content_en。

全库扫描（2026-07-05）：单纯 zh/en<25% 会误触 30/34 组（AD5S EN 客服段普遍更长）。
现用组合规则：极短 / 极端比例 / 编号步骤不足。
"""

from __future__ import annotations

import re

# 非空但实质极短（与 chunk_builder.EMPTY_ZH_THRESHOLD 量级对齐）
MIN_ZH_SUBSTANCE = 80
# 极端 EN-heavy（qa_028 级标题句）
EXTREME_RATIO = 0.08
MIN_EN_FOR_EXTREME = 200
# 编号步骤不足且 EN 长文块
MIN_ZH_STEPS = 3
MIN_EN_FOR_STEP_RULE = 400
MAX_ZH_FOR_STEP_RULE = 250
# 多步骤但 zh 总字数仍偏短（batch1 qa_032 类）
MAX_ZH_COMPACT = 150
MIN_EN_COMPACT = 800
MAX_RATIO_COMPACT = 0.15

STEP_LINE_RE = re.compile(r"(?m)^\s*\d+[\s\.．、]")


def count_zh_numbered_steps(content_zh: str | None) -> int:
    return len(STEP_LINE_RE.findall((content_zh or "").strip()))


def is_thin_zh(content_zh: str | None, content_en: str | None) -> bool:
    """
    content_zh 非空但相对 content_en 过薄，主面板仅展示 zh 会严重残缺。

    规则（任一满足）：
    1. zh 空
    2. zh < 80 且 en > 3×zh
    3. en ≥ 200 且 zh/en < 8%（极端比例）
    4. zh 编号步骤 < 3 且 en ≥ 400 且 zh < 250
    5. 编号步骤 ≥ 3 但 zh < 150 且 en ≥ 800 且 zh/en < 15%（步骤行短、EN 长文块）
    """
    zh = (content_zh or "").strip()
    en = (content_en or "").strip()
    if not en:
        return False
    if not zh:
        return True
    zl, el = len(zh), len(en)
    if zl < MIN_ZH_SUBSTANCE and el > zl * 3:
        return True
    if el >= MIN_EN_FOR_EXTREME and zl / el < EXTREME_RATIO:
        return True
    steps = count_zh_numbered_steps(zh)
    if steps < MIN_ZH_STEPS and el >= MIN_EN_FOR_STEP_RULE and zl < MAX_ZH_FOR_STEP_RULE:
        return True
    if (
        steps >= MIN_ZH_STEPS
        and zl < MAX_ZH_COMPACT
        and el >= MIN_EN_COMPACT
        and zl / el < MAX_RATIO_COMPACT
    ):
        return True
    return False


def thin_zh_reason(content_zh: str | None, content_en: str | None) -> str | None:
    """调试/扫描：返回触发原因。"""
    zh = (content_zh or "").strip()
    en = (content_en or "").strip()
    if not en:
        return None
    if not zh:
        return "empty_zh"
    zl, el = len(zh), len(en)
    if zl < MIN_ZH_SUBSTANCE and el > zl * 3:
        return "short_zh_3x_en"
    if el >= MIN_EN_FOR_EXTREME and zl / el < EXTREME_RATIO:
        return "extreme_ratio"
    steps = count_zh_numbered_steps(zh)
    if steps < MIN_ZH_STEPS and el >= MIN_EN_FOR_STEP_RULE and zl < MAX_ZH_FOR_STEP_RULE:
        return f"few_steps({steps})_long_en"
    if (
        steps >= MIN_ZH_STEPS
        and zl < MAX_ZH_COMPACT
        and el >= MIN_EN_COMPACT
        and zl / el < MAX_RATIO_COMPACT
    ):
        return f"compact_steps({steps})_long_en"
    return None


def primary_display_text(content_zh: str | None, content_en: str | None) -> str:
    zh = (content_zh or "").strip()
    en = (content_en or "").strip()
    if zh:
        return content_zh or ""
    return en


def supplement_en_text(
    content_zh: str | None,
    content_en: str | None,
    *,
    customer_reply_templates: list | None = None,
) -> str | None:
    """EN 客服邮件模板不进 LLM 补充通道（V1.1 · TC148）。"""
    if customer_reply_templates:
        return None
    if is_thin_zh(content_zh, content_en):
        en = (content_en or "").strip()
        return en or None
    return None

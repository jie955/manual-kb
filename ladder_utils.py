#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""顺序排查梯（troubleshooting_ladder）检测与构建。"""

from __future__ import annotations

import re

# 行首编号：1 / 1. / 1、 / 1打开（数字后可直接接中文）
STEP_HEAD_RE = re.compile(
    r"(?m)^(\d+)(?:[\s\.．、]+|(?=[\u4e00-\u9fff]))"
)

LAST_RESORT_RE = re.compile(
    r"ERM12|external\s+receiver|外接收器|外置接收器",
    re.IGNORECASE,
)

TRY_FINAL_STEP_RE = re.compile(
    r"Try\s+Step\s+(\d+)\s+if\s+the\s+problem\s+persist",
    re.IGNORECASE,
)


def split_numbered_steps(text: str) -> dict[int, str]:
    """按行首编号切分为 {step_index: content}。"""
    text = (text or "").strip()
    if not text:
        return {}

    matches = list(STEP_HEAD_RE.finditer(text))
    if not matches:
        return {}

    steps: dict[int, str] = {}
    for i, match in enumerate(matches):
        step_index = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            steps[step_index] = content
    return steps


def _is_consecutive_ladder(steps: dict[int, str], *, min_steps: int = 2) -> bool:
    if len(steps) < min_steps:
        return False
    nums = sorted(steps)
    if nums[0] != 1:
        return False
    return nums == list(range(1, len(nums) + 1))


def _infer_last_resort(
    step_index: int,
    content_zh: str,
    content_en: str,
    prev_content_en: str,
) -> bool:
    combined = f"{content_zh}\n{content_en}"
    if LAST_RESORT_RE.search(combined):
        return True
    if prev_content_en:
        m = TRY_FINAL_STEP_RE.search(prev_content_en)
        if m and int(m.group(1)) == step_index:
            return True
    return False


def build_troubleshooting_ladder(
    answer_zh: str,
    answer_en: str,
    *,
    min_steps: int = 2,
) -> list[dict] | None:
    """
    从 answer_zh / answer_en 构建 troubleshooting_ladder[]。
    两侧至少一侧检出连续编号步骤（1..n）时返回 ladder，否则 None。
    """
    zh_steps = split_numbered_steps(answer_zh)
    en_steps = split_numbered_steps(answer_en)

    zh_ok = _is_consecutive_ladder(zh_steps, min_steps=min_steps)
    en_ok = _is_consecutive_ladder(en_steps, min_steps=min_steps)

    has_zh = len((answer_zh or "").strip()) > 20
    has_en = len((answer_en or "").strip()) > 20

    if has_zh and has_en:
        if not (zh_ok and en_ok) or len(zh_steps) != len(en_steps):
            return None
        indices = sorted(zh_steps)
    elif zh_ok:
        indices = sorted(zh_steps)
    elif en_ok:
        indices = sorted(en_steps)
    else:
        return None

    if indices[0] != 1 or indices != list(range(1, len(indices) + 1)):
        return None

    ladder: list[dict] = []
    prev_en = ""
    for step_index in indices:
        content_zh = zh_steps.get(step_index, "")
        content_en = en_steps.get(step_index, "")
        step: dict = {
            "step_index": step_index,
            "content_zh": content_zh,
            "content_en": content_en,
            "is_last_resort": _infer_last_resort(
                step_index, content_zh, content_en, prev_en
            ),
            "branches": [],
            "links": [],
            "images": [],
        }
        ladder.append(step)
        prev_en = content_en

    return ladder


def attach_troubleshooting_ladder(group: dict) -> None:
    """就地附加 troubleshooting_ladder（有则写入，无则不设键）。"""
    ladder = build_troubleshooting_ladder(
        group.get("answer_zh") or "",
        group.get("answer_en") or "",
    )
    if ladder:
        group["troubleshooting_ladder"] = ladder

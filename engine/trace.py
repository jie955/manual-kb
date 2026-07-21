#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RunTrace — per-answer audit record for API / eval (ADR §6)."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RunTrace:
    """Structured trace attached to /api/ask when requested."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    domain_id: str | None = None
    product_id: str | None = None
    route_reason: str | None = None
    routing_method: str | None = None
    index_paths: dict[str, str] = field(default_factory=dict)
    retrieved_hit_ids: list[str] = field(default_factory=list)
    retrieved_group_ids: list[str] = field(default_factory=list)
    prompt_pack_version: str | None = None
    style_pack_version: str | None = None
    style_family: str | None = None
    policy_version: str | None = None
    model_name: str | None = None
    validation_result: dict[str, Any] | None = None
    context_language_leak: bool | None = None
    latency_ms: float | None = None
    token_usage: dict[str, Any] | None = None
    cost: float | None = None
    started_at: float = field(default_factory=time.time)

    def finish(self) -> None:
        self.latency_ms = round((time.time() - self.started_at) * 1000, 1)

    def to_dict(self) -> dict[str, Any]:
        self.finish()
        data = asdict(self)
        data.pop("started_at", None)
        # Drop empty optional fields for a leaner API payload.
        return {k: v for k, v in data.items() if v is not None and v != [] and v != {}}


def detect_context_zh_leak(context_blocks: list[str] | list[dict]) -> bool:
    """True if EN cs_email context appears to contain Chinese troubleshooting prose."""
    markers = ("中文排查", "断配件", "Internal notes", "章节：", "故障标题：")
    for block in context_blocks:
        text = block if isinstance(block, str) else str(block)
        if any(m in text for m in markers):
            return True
        # CJK ideographs in context body are a strong leak signal for EN mode.
        if any("\u4e00" <= ch <= "\u9fff" for ch in text):
            # Allow short CJK in URLs/labels only — if density is high, flag.
            cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
            if cjk >= 8:
                return True
    return False

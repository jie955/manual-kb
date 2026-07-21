#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Policy · CS email style exemplars (Phase 3.2). Not Context Builder.

Compatibility facade — assets and logic live in domains/<id>/styles/ and
domains/prompt_style.py.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from domains.loader import get_default_domain
from domains.prompt_style import (
    StyleSelection,
    assert_hold_out_integrity,
    build_cs_email_system_prompt,
    load_principles_bullets,
    load_style_exemplar,
    resolve_style_family,
    select_style,
)

__all__ = [
    "HOLD_OUT_GATE",
    "STYLE_DIR",
    "ROUTER_PATH",
    "PRINCIPLES_PATH",
    "SCENARIO_MAP_PATH",
    "StyleSelection",
    "assert_hold_out_integrity",
    "build_cs_email_system_prompt",
    "load_principles_bullets",
    "load_style_exemplar",
    "resolve_style_family",
    "select_style",
]


def _style_root() -> Path:
    return get_default_domain().style.root


@lru_cache(maxsize=1)
def _hold_out_gate() -> frozenset[str]:
    return get_default_domain().style.hold_out_gate


STYLE_DIR = _style_root()
ROUTER_PATH = STYLE_DIR / "family_router.json"
PRINCIPLES_PATH = get_default_domain().style.principles_path
SCENARIO_MAP_PATH = get_default_domain().style.scenario_map_path
HOLD_OUT_GATE = _hold_out_gate()

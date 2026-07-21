#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eval pack helpers: retrieval boosts, presales briefs, search-query resolution."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DOMAINS_ROOT = Path(__file__).resolve().parent


def eval_pack_enabled() -> bool:
    """When false (EVAL_PACK_DISABLED=1), all per-scenario YAML patches are skipped."""
    return os.environ.get("EVAL_PACK_DISABLED", "").strip().lower() not in (
        "1",
        "true",
        "yes",
    )


@lru_cache(maxsize=8)
def _load_yaml_map(domain_id: str, filename: str) -> dict[str, str]:
    path = DOMAINS_ROOT / domain_id / "evals" / filename
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, str] = {}
    for k, v in data.items():
        if not v:
            continue
        if isinstance(v, dict) and v.get("playbook_ref"):
            from domains.presales_playbooks import render_brief

            rendered = render_brief(str(v["playbook_ref"]), domain_id=domain_id)
            if rendered:
                out[str(k)] = rendered
        elif not isinstance(v, dict):
            out[str(k)] = str(v).strip()
    return out


@lru_cache(maxsize=8)
def _load_yaml_doc(domain_id: str, filename: str) -> dict:
    path = DOMAINS_ROOT / domain_id / "evals" / filename
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def retrieval_boost(scenario_id: str | None, *, domain_id: str = "topens") -> str | None:
    if not scenario_id or not eval_pack_enabled():
        return None
    return _load_yaml_map(domain_id, "retrieval_boosts.yaml").get(scenario_id)


def presales_brief(scenario_id: str | None, *, domain_id: str = "topens") -> str | None:
    if not scenario_id or not eval_pack_enabled():
        return None
    return _load_yaml_map(domain_id, "presales_briefs.yaml").get(scenario_id)


def generation_brief(scenario_id: str | None, *, domain_id: str = "topens") -> str | None:
    if not scenario_id or not eval_pack_enabled():
        return None
    return _load_yaml_map(domain_id, "generation_briefs.yaml").get(scenario_id)


def pinned_reference(scenario_id: str | None, *, domain_id: str = "topens") -> str | None:
    if not scenario_id or not eval_pack_enabled():
        return None
    return _load_yaml_map(domain_id, "pinned_references.yaml").get(scenario_id)


def context_force_include_groups(
    scenario_id: str | None, *, domain_id: str = "topens"
) -> frozenset[str]:
    if not scenario_id or not eval_pack_enabled():
        return frozenset()
    doc = _load_yaml_doc(domain_id, "context_overrides.yaml").get(scenario_id) or {}
    groups = doc.get("force_include_groups") or []
    return frozenset(str(g) for g in groups)


def pinned_images(
    scenario_id: str | None, *, domain_id: str = "topens"
) -> list[dict[str, Any]]:
    if not scenario_id or not eval_pack_enabled():
        return []
    doc = _load_yaml_doc(domain_id, "pinned_images.yaml").get(scenario_id) or []
    if not isinstance(doc, list):
        return []
    return [dict(item) for item in doc if isinstance(item, dict)]


def resolve_search_query(
    scenario: dict[str, Any],
    customer_email: str,
    *,
    scenario_id: str | None = None,
    domain_id: str = "topens",
) -> str:
    """Pick EN retrieval query: boost > verbatim customer > primary_query."""
    sid = scenario_id or str(scenario.get("id") or "")
    boost = retrieval_boost(sid, domain_id=domain_id)
    if boost:
        return boost
    verbatim = scenario.get("verbatim_customer") or []
    if verbatim:
        return customer_email.strip()
    return (scenario.get("primary_query") or customer_email).strip()

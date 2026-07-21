#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style selection and CS email prompt assembly from domain StylePack / PromptPack."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from domains.loader import get_default_domain
from domains.models import DomainConfig, StylePack


@dataclass(frozen=True)
class StyleSelection:
    family_id: str
    exemplar_path: Path
    exemplar_text: str
    match_reason: str


def _domain(domain_id: str | None = None) -> DomainConfig:
    return get_default_domain(domain_id or "topens")


def _style(domain_id: str | None = None) -> StylePack:
    return _domain(domain_id).style


@lru_cache(maxsize=8)
def load_principles_bullets(domain_id: str = "topens") -> str:
    """Numbered SOP bullets from principles_en.md (layer 1)."""
    path = _style(domain_id).principles_path
    text = path.read_text(encoding="utf-8")
    bullets: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^\d+\.\s+\*\*(.+?)\*\*:\s*(.+)$", line.strip())
        if m:
            bullets.append(f"- {m.group(1)}: {m.group(2)}")
    return "\n".join(bullets)


def _top1_group_id(hits: list[dict] | None) -> str | None:
    if not hits:
        return None
    gid = hits[0].get("group_id")
    return str(gid) if gid else None


@lru_cache(maxsize=8)
def _presales_scenario_ids(domain_id: str = "topens") -> frozenset[str]:
    pack = _style(domain_id)
    if not pack.scenario_map_path.is_file():
        return frozenset()
    data = json.loads(pack.scenario_map_path.read_text(encoding="utf-8"))
    return frozenset(
        str(s["id"])
        for s in data.get("scenarios") or []
        if s.get("type") in pack.presales_types
    )


def resolve_style_family(
    customer_email: str,
    hits: list[dict] | None = None,
    *,
    scenario_id: str | None = None,
    domain_id: str | None = None,
) -> tuple[str, str]:
    """Pick scene family for skeleton exemplar. Returns (family_id, match_reason)."""
    pack = _style(domain_id)
    email_lower = (customer_email or "").lower()

    if scenario_id:
        sid = scenario_id.lower()
        overrides = pack.scenario_overrides
        if sid in {k.lower() for k in overrides}:
            for key, fam in overrides.items():
                if key.lower() == sid:
                    return fam, f"scenario_override:{sid}"
        if sid in {x.lower() for x in _presales_scenario_ids(domain_id or "topens")}:
            return "F7_presales", "scenario:presales"
        if pack.warranty_scenario_substring in sid:
            return "F8_warranty_rma", "scenario:warranty_composite"

    group_id = _top1_group_id(hits)
    if group_id and group_id in pack.group_hints:
        fam = pack.group_hints[group_id]
        return fam, f"group_hint:{group_id}"

    best_family: str | None = None
    best_score = 0
    for fam_id, spec in pack.families.items():
        score = 0
        for kw in spec.keywords:
            if kw.lower() in email_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_family = fam_id

    if best_family and best_score > 0:
        return best_family, f"keywords:{best_score}"

    return pack.default_family, "default"


def load_style_exemplar(
    family_id: str,
    *,
    domain_id: str | None = None,
) -> tuple[Path, str]:
    pack = _style(domain_id)
    spec = pack.families.get(family_id)
    if not spec:
        family_id = pack.default_family
        spec = pack.families[family_id]
    path = pack.root / spec.exemplar_relpath
    if not path.is_file():
        raise FileNotFoundError(f"Style exemplar missing: {path}")
    return path, path.read_text(encoding="utf-8")


def select_style(
    customer_email: str,
    hits: list[dict] | None = None,
    *,
    scenario_id: str | None = None,
    enabled: bool = True,
    domain_id: str | None = None,
) -> StyleSelection | None:
    if not enabled:
        return None

    family_id, reason = resolve_style_family(
        customer_email,
        hits,
        scenario_id=scenario_id,
        domain_id=domain_id,
    )
    path, text = load_style_exemplar(family_id, domain_id=domain_id)
    return StyleSelection(
        family_id=family_id,
        exemplar_path=path,
        exemplar_text=text.strip(),
        match_reason=reason,
    )


def build_cs_email_system_prompt(
    *,
    section: str,
    question: str,
    customer_email: str = "",
    hits: list[dict] | None = None,
    scenario_id: str | None = None,
    base_prompt: str | None = None,
    style_enabled: bool = True,
    domain_id: str | None = None,
) -> tuple[str, StyleSelection | None]:
    """
    Assemble CS email system prompt: base rules + principles + skeleton exemplar.
    Prompt Policy only — does not modify reference context blocks.
    """
    domain = _domain(domain_id)
    if base_prompt is None:
        base_prompt = domain.prompts.cs_email_system_en

    selection = select_style(
        customer_email,
        hits,
        scenario_id=scenario_id,
        enabled=style_enabled,
        domain_id=domain_id,
    )

    parts = [base_prompt.replace("{section}", section).replace("{question}", question)]

    principles = load_principles_bullets(domain_id or domain.meta.id)
    if principles:
        parts.append(
            "Support style principles (format and tone — facts must still come from references):\n"
            + principles
        )

    if selection:
        hold_note = ""
        if scenario_id and scenario_id in domain.style.hold_out_gate:
            hold_note = (
                "\n(Gate eval scenario — use structure/tone from exemplar only; "
                "all diagnostic facts from reference blocks below.)"
            )
        parts.append(
            f"Reply structure exemplar ({selection.family_id} · {selection.match_reason}). "
            "Follow layout and phrasing patterns; replace every [from references] placeholder "
            "with grounded content from the reference blocks. Do not copy terminal numbers or "
            "DIP settings from this exemplar. Curly-brace names in the exemplar "
            "({customer_name}, {agent}) are instructions—never print them literally in the reply."
            f"{hold_note}\n\n"
            + selection.exemplar_text
        )

    return "\n\n".join(parts), selection


def assert_hold_out_integrity(domain_id: str | None = None) -> None:
    """Runtime pool must not ship raw hold-out Reference files as exemplars."""
    pack = _style(domain_id)
    for cs_id in pack.hold_out_gate:
        for fam in pack.families.values():
            if cs_id in fam.email_sources and fam.exemplar_relpath.endswith(f"{cs_id}.md"):
                raise RuntimeError(f"Hold-out {cs_id} wired as runtime exemplar file")

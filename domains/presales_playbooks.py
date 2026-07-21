"""Render structured presales playbooks from domain pack YAML."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DOMAINS_ROOT = Path(__file__).resolve().parent


@lru_cache(maxsize=8)
def _load_playbooks(domain_id: str) -> dict[str, dict[str, Any]]:
    path = DOMAINS_ROOT / domain_id / "presales_playbooks.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    playbooks = data.get("playbooks") or {}
    return {str(k): v for k, v in playbooks.items() if isinstance(v, dict)}


def render_brief(playbook_id: str, *, domain_id: str = "topens") -> str | None:
    pb = _load_playbooks(domain_id).get(playbook_id)
    if not pb:
        return None

    lines: list[str] = []
    summary = pb.get("summary")
    if summary:
        lines.append(f"Presales facts ({summary}):")

    topo = pb.get("topology") or {}
    if topo.get("gate_count"):
        rel = topo.get("relationship", "independent")
        w = topo.get("typical_weight_lb")
        ft = topo.get("typical_length_ft")
        detail = f"Customer has {topo['gate_count']} separate gates"
        if w and ft:
            detail += f" (~{w} lbs, ~{ft} ft each)"
        if rel == "independent":
            detail += ", not one dual-leaf gate."
        lines.append(f"- {detail}")

    for ap in pb.get("anti_patterns") or []:
        product = ap.get("product", "")
        reason = ap.get("reason", "")
        if product and reason:
            lines.append(f"- {product} does NOT fit: {reason}")

    rec = pb.get("recommendation") or {}
    kits = rec.get("kits")
    model = rec.get("model", "")
    if kits and model:
        lines.append(
            f"- Recommend {kits} single-swing opener kits (e.g. {model}) "
            f"so each gate operates independently with its own remote."
        )
    rationale = rec.get("rationale")
    if rationale:
        lines.append(f"- {rationale}")
    power = rec.get("power")
    if power:
        lines.append(f"- {model} includes {power}.")

    links = pb.get("links") or {}
    if links:
        lines.append("Links to include in reply (plain text URLs):")
        if links.get("purchase"):
            lines.append(f"{model} purchase: {links['purchase']}")
        if links.get("manual"):
            lines.append(f"{model} manual: {links['manual']}")

    return "\n".join(lines).strip() if lines else None

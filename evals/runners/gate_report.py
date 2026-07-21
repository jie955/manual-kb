#!/usr/bin/env python3
"""Gate report helpers — markdown probe + scenario id lists."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOMAIN = "topens"


def get_gate_scenario_ids(domain_id: str = DEFAULT_DOMAIN) -> list[str]:
    path = ROOT / "domains" / domain_id / "evals" / "gates.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(data.get("gate_scenario_ids") or [])


def write_probe_markdown(payload: dict, out_path: Path) -> None:
    """Phase 0.3 internal probe · retrieval + optional generation."""
    eval_dir = out_path.parent.name
    if eval_dir == "eval" or "eval" in str(out_path).replace("\\", "/"):
        plan_link = "./cs_en_implementation_plan.md"
        json_link = "./cs_e2e_gate_results.json"
    else:
        plan_link = "../../_scratch/eval/cs_en_implementation_plan.md"
        json_link = "../../_scratch/eval/cs_e2e_gate_results.json"

    lines = [
        "# Phase 0.3 · E2E Gate Probe",
        "",
        f"**Date**: {payload.get('generated')} · **generate**={payload.get('generate')} · "
        f"**model**=`{payload.get('model')}`",
        "",
        f"**Plan**: [Implementation Plan §4.3]({plan_link}) · "
        f"**JSON**: [`cs_e2e_gate_results.json`]({json_link})",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    results = payload.get("results") or []
    scorable = [r for r in results if r.get("expected_groups")]
    hits = [r for r in scorable if r.get("top1_hit")]
    leaks = [r for r in results if r.get("context_zh_leak")]
    lines.append(f"| Gate cases | {len(results)} |")
    lines.append(f"| Top1 hit (scorable) | {len(hits)}/{len(scorable)} |")
    lines.append(f"| context_zh_leak | {len(leaks)} |")
    if payload.get("generate"):
        with_reply = sum(1 for r in results if r.get("reply_full"))
        lines.append(f"| Generated replies | {with_reply}/{len(results)} |")
    lines.extend(["", "## Cases", ""])

    for row in results:
        sid = row["scenario_id"]
        flag = (
            "OK"
            if row.get("top1_hit")
            else ("n/a" if not row.get("expected_groups") else "MISS")
        )
        lines.append(f"### `{sid}` · {row.get('label') or ''}")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Top1 | `{row.get('top1_group')}` [{flag}] |")
        lines.append(
            f"| Library | `{row.get('matched_library')}` ({row.get('routing_method')}) |"
        )
        lines.append(
            f"| Expected groups | `{', '.join(row.get('expected_groups') or []) or '—'}` |"
        )
        lines.append(f"| Top3 | `{', '.join(row.get('top3_groups') or [])}` |")
        lines.append(f"| ZH leak | {'❌' if row.get('context_zh_leak') else '✅'} |")
        if row.get("style"):
            st = row["style"]
            lines.append(f"| Style | `{st.get('family_id')}` ({st.get('match_reason')}) |")
        if row.get("reply_full"):
            lines.append(f"| Reply len | {row.get('reply_len')} |")
        lines.append("")
        if row.get("reply_full"):
            lines.append("#### System Reply")
            lines.append("")
            lines.append("```text")
            lines.append(row["reply_full"].strip())
            lines.append("```")
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")

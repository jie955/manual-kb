#!/usr/bin/env python3
"""Gate R · EN_READINESS scan across three qa_groups.json libraries."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from en_representation import classify_en_readiness  # noqa: E402

MAP_PATH = Path(__file__).resolve().parent / "cs_email_query_map.json"

LIBRARIES = [
    ("a3s", ROOT / "_scratch/run-006/qa_groups.json"),
    ("ad5s", ROOT / "_scratch/run-ad5s/qa_groups.json"),
    ("tc148", ROOT / "_scratch/run-tc148/qa_groups.json"),
]

# Gate Tier A + pilot + T1/T3/T4 expected groups (union)
GATE_SCENARIO_IDS = {
    "cs_0001",
    "cs_0008",
    "cs_0009",
    "cs_0010",
    "cs_0013",
    "cs_0015",
    "cs_0018",
    "cs_0019",
    "cs_0022",
    "cs_0023",
    "cs_0025",
    "cs_0026",
    "cs_0027",
}


def gate_group_ids() -> set[str]:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    groups: set[str] = set()
    for s in data["scenarios"]:
        if s["id"] not in GATE_SCENARIO_IDS:
            continue
        groups.update(s.get("expected_group_ids") or [])
        groups.update(s.get("alternate_group_ids") or [])
    return groups


def scan_library(lib_id: str, path: Path, gate_ids: set[str]) -> list[dict]:
    groups = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for g in groups:
        gid = g["group_id"]
        templates = g.get("customer_reply_templates") or []
        status = classify_en_readiness(
            answer_en=g.get("answer_en"),
            answer_zh=g.get("answer_zh"),
            has_templates=bool(templates),
            is_gate_group=gid in gate_ids,
        )
        rows.append(
            {
                "library": lib_id,
                "group_id": gid,
                "section": g.get("section"),
                "question": (g.get("question") or "")[:120],
                "en_len": len((g.get("answer_en") or "").strip()),
                "zh_len": len((g.get("answer_zh") or "").strip()),
                "has_templates": bool(templates),
                "status": status,
                "gate_group": gid in gate_ids,
            }
        )
    return rows


def render_md(rows: list[dict], gate_ids: set[str]) -> str:
    blocking = [r for r in rows if r["status"] == "blocking"]
    gate_blocking = [r for r in blocking if r["gate_group"]]
    counts = Counter(r["status"] for r in rows)
    lines = [
        "# EN_READINESS Scan · Gate R",
        "",
        f"**Date**: {date.today().isoformat()}",
        f"**Gate scenario groups** (union): {len(gate_ids)}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for st in ("ready", "enrich", "blocking"):
        lines.append(f"| {st} | {counts.get(st, 0)} |")
    lines.extend(
        [
            "",
            f"**Gate blocking** (must = 0 for Gate R switch): **{len(gate_blocking)}**",
            "",
            "## Gate blocking groups",
            "",
            "| Library | group_id | en_len | zh_len | templates | question (trunc) |",
            "| --- | --- | ---: | ---: | :---: | --- |",
        ]
    )
    for r in sorted(gate_blocking, key=lambda x: (x["library"], x["group_id"])):
        lines.append(
            f"| {r['library']} | {r['group_id']} | {r['en_len']} | {r['zh_len']} | "
            f"{'Y' if r['has_templates'] else ''} | {r['question']} |"
        )
    lines.extend(["", "## All blocking", ""])
    for r in sorted(blocking, key=lambda x: (x["library"], x["group_id"])):
        lines.append(
            f"- **{r['library']}** `{r['group_id']}` · en={r['en_len']} zh={r['zh_len']} "
            f"{'· template' if r['has_templates'] else ''}"
        )
    lines.extend(["", "## Per-library", ""])
    for lib_id, _ in LIBRARIES:
        sub = [r for r in rows if r["library"] == lib_id]
        c = Counter(r["status"] for r in sub)
        lines.append(f"- **{lib_id}**: ready={c.get('ready',0)} enrich={c.get('enrich',0)} blocking={c.get('blocking',0)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    gate_ids = gate_group_ids()
    all_rows: list[dict] = []
    for lib_id, path in LIBRARIES:
        if not path.is_file():
            print(f"WARN missing {path}", file=sys.stderr)
            continue
        all_rows.extend(scan_library(lib_id, path, gate_ids))

    out_md = Path(__file__).resolve().parent / "cs_en_readiness_scan.md"
    out_json = Path(__file__).resolve().parent / "cs_en_readiness_scan.json"
    out_md.write_text(render_md(all_rows, gate_ids), encoding="utf-8")
    out_json.write_text(
        json.dumps({"gate_group_ids": sorted(gate_ids), "rows": all_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    gate_blocking = sum(1 for r in all_rows if r["gate_group"] and r["status"] == "blocking")
    print(f"Wrote {out_md}")
    print(f"Gate blocking: {gate_blocking}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

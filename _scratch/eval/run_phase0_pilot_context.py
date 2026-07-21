#!/usr/bin/env python3
"""Phase 0.2 · Pilot context smoke — Oracle hits, locale=en, no API required."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from context_builder import build_context_for_hits  # noqa: E402

PILOTS = [
    {
        "id": "cs_0001",
        "label": "#1 AT12131S gate no response",
        "qa_groups": ROOT / "_scratch/run-006/qa_groups.json",
        "group_ids": ["qa_011"],
        "customer_email": (
            "the gate does nothing when i push the button or use the key pad remote.\n"
            "Product Model: TOPENS AT12131S"
        ),
    },
    {
        "id": "cs_0008",
        "label": "#8 PW502 TC148 push button not working",
        "qa_groups": ROOT / "_scratch/run-tc148/qa_groups.json",
        "group_ids": ["qa_002"],
        "customer_email": (
            "Push button not working, therefore we jumpered out #4&5 at the main "
            "control panel and still nothing happened. Other than that everything works.\n"
            "Product Model: PW502 · Accessories: TC148"
        ),
    },
]


def _load_groups(path: Path, group_ids: list[str]) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {g["group_id"]: g for g in data}
    hits: list[dict] = []
    for gid in group_ids:
        g = by_id[gid]
        imgs = g.get("images") or []
        hits.append(
            {
                "section": g.get("section") or "",
                "question": g.get("question") or "",
                "content_zh": g.get("answer_zh") or "",
                "content_en": g.get("answer_en") or "",
                "images": [{"file": f} if isinstance(f, str) else f for f in imgs],
            }
        )
    return hits


def main() -> int:
    out = ROOT / "_scratch/eval/phase0_pilot_context_smoke.md"
    lines = [
        "# Phase 0.2 · Pilot Context Smoke",
        "",
        f"**Date**: {date.today().isoformat()}",
        "**Mode**: Oracle hits · `locale=en` · post Phase 0.1 EN Context Policy",
        "",
    ]
    ok = True
    for pilot in PILOTS:
        hits = _load_groups(pilot["qa_groups"], pilot["group_ids"])
        ctx_parts = build_context_for_hits(hits, locale="en", response_mode="cs_email")
        full_ctx = "\n\n".join(ctx_parts)
        has_zh_leak = any(
            tok in full_ctx
            for tok in ("断配件", "Internal notes", "translate key points", "中文排查")
        )
        lines.extend(
            [
                f"## {pilot['label']} (`{pilot['id']}`)",
                "",
                f"**Groups**: {', '.join(pilot['group_ids'])}",
                "",
                "### Customer email (excerpt)",
                "",
                "```",
                pilot["customer_email"].strip(),
                "```",
                "",
                "### LLM context (`locale=en`)",
                "",
                "```",
                full_ctx,
                "```",
                "",
                f"**ZH leak check**: {'FAIL' if has_zh_leak else 'PASS'}",
                "",
            ]
        )
        if has_zh_leak:
            ok = False
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

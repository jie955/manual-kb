#!/usr/bin/env python3
"""Gate: TC148 customer_reply_templates 字段 + LLM context 隔离 + API 字段存在。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from context_builder import build_context_block

PROD = ROOT / "_scratch/run-tc148"
GROUPS = PROD / "qa_groups.json"
MANIFEST = PROD / "chroma_captioned/manifest.json"


def main() -> None:
    groups = {g["group_id"]: g for g in json.loads(GROUPS.read_text(encoding="utf-8"))}
    for gid in ("qa_001", "qa_002"):
        g = groups[gid]
        tpls = g.get("customer_reply_templates") or []
        assert len(tpls) == 1, f"{gid}: expected 1 template"
        assert tpls[0]["content_role"] == "customer_reply_template"
        assert len(tpls[0]["text"]) > 500
        assert not (g.get("answer_en") or "").strip(), f"{gid}: answer_en should be empty"
        assert "Please help us confirm" in tpls[0]["text"]

    chunks = json.loads(MANIFEST.read_text(encoding="utf-8"))["chunks"]
    by_gid = {c["group_id"]: c for c in chunks if not c.get("is_child")}
    for gid in ("qa_001", "qa_002"):
        c = by_gid[gid]
        assert c.get("customer_reply_templates"), f"{gid}: missing in manifest"
        assert not (c.get("content_en") or "").strip()

    hit = {
        "section": "",
        "question": "test",
        "content_zh": groups["qa_001"]["answer_zh"],
        "content_en": "",
        "customer_reply_templates": groups["qa_001"]["customer_reply_templates"],
        "links": groups["qa_001"].get("links") or [],
    }
    ctx = build_context_block(hit)
    assert "Please help us confirm" not in ctx
    assert "May I ask" not in ctx
    assert groups["qa_001"]["answer_zh"][:20] in ctx

    print("verify_tc148_customer_reply_template: PASS")


if __name__ == "__main__":
    main()

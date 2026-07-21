#!/usr/bin/env python3
"""TC148 content accuracy gate: links[] · COM image · short video · prose strip."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from link_utils import find_urls

TC148 = ROOT / "_scratch/run-tc148/qa_groups.json"
DRIVE = "drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS"
TOPENS = "how-to-connect-multiple-accessories-to-a-shared-terminal"


def main() -> int:
    groups = json.loads(TC148.read_text(encoding="utf-8"))
    ok = True

    qa001 = next(g for g in groups if g["group_id"] == "qa_001")
    qa002 = next(g for g in groups if g["group_id"] == "qa_002")

    # C1/C2/C4 — structure
    if not any(DRIVE in (lk.get("url") or "") for lk in qa002.get("links") or []):
        print("FAIL qa_002: missing Drive short video link")
        ok = False
    q2_topens = [lk for lk in qa002.get("links") or [] if TOPENS in (lk.get("url") or "")]
    if len(q2_topens) != 1:
        print(f"FAIL qa_002: expected 1 topens link, got {len(q2_topens)}")
        ok = False
    if len(qa002.get("links") or []) != 2:
        print(f"FAIL qa_002: expected 2 links total, got {len(qa002.get('links') or [])}")
        ok = False

    q1_links = qa001.get("links") or []
    if len(q1_links) != 1 or TOPENS not in (q1_links[0].get("url") or ""):
        print("FAIL qa_001: expected 1 topens link")
        ok = False
    if "image_001.png" not in (qa001.get("images") or []):
        print("FAIL qa_001: missing image_001 COM grounding")
        ok = False

    for gid, g in [("qa_001", qa001), ("qa_002", qa002)]:
        if find_urls(g.get("answer_en") or ""):
            print(f"FAIL {gid}: bare URL in answer_en")
            ok = False
        zh = g.get("answer_zh") or ""
        if "短接" not in zh and gid == "qa_002":
            print("FAIL qa_002: ZH missing 短接 step text")
            ok = False
        if "接地" not in zh and gid == "qa_001":
            print("FAIL qa_001: ZH missing 接地 step text")
            ok = False

    # Drive label
    drive_lk = next(lk for lk in qa002["links"] if DRIVE in lk["url"])
    if drive_lk.get("link_type") != "video":
        print("FAIL qa_002 Drive link_type should be video")
        ok = False
    if "short" not in (drive_lk.get("label") or "").lower() and "O/S/C" not in (
        drive_lk.get("label") or ""
    ):
        print(f"WARN qa_002 Drive label: {drive_lk.get('label')!r}")

    print(f"[C1-C4] qa_001 links={len(q1_links)} images={qa001.get('images')}")
    print(f"[C1-C4] qa_002 links={len(qa002.get('links') or [])} drive_label={drive_lk.get('label')!r}")

    # Optional retrieval spot-check
    try:
        from qa_server import _ask, _init_engine, _load_dotenv

        _load_dotenv()
        _init_engine(ROOT / "_scratch/run-tc148/chroma_captioned", "_scratch/modelscope/BAAI/bge-m3")
        for qid, q, exp in (
            ("T2", "TC148 没反应 遥控器正常", "qa_002"),
            ("T1", "墙壁开关自检后灯常亮", "qa_001"),
        ):
            top = (_ask(q, use_llm=False).get("hits") or [None])[0]
            gid = top.get("group_id") if top else None
            nlinks = len(top.get("links") or []) if top else 0
            nimgs = len(top.get("images") or []) if top else 0
            hit = gid == exp
            print(f"[retrieval {qid}] top1={gid} links={nlinks} images={nimgs} {'OK' if hit else 'note'}")
    except Exception as e:
        print(f"[retrieval] skip: {e}")

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

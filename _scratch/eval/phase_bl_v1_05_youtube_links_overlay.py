#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-05 post-close: qa_029/042/043 YouTube → links[] · prose strip · dedupe by video id."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from link_utils import apply_video_tier_links, find_urls, youtube_video_id

PROD = ROOT / "_scratch/run-ad5s"
STAMP = "20260705-bl-v1-05-youtube"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_029", "qa_042", "qa_043"})

EXPECTED_COUNTS = {"qa_029": 3, "qa_042": 4, "qa_043": 1}


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_groups(groups: list[dict]) -> None:
    for gid, exp_n in EXPECTED_COUNTS.items():
        g = next(x for x in groups if x["group_id"] == gid)
        en = g.get("answer_en") or ""
        if find_urls(en):
            raise SystemExit(f"{gid}: bare URL still in answer_en")
        links = g.get("links") or []
        if len(links) != exp_n:
            raise SystemExit(f"{gid}: expected {exp_n} links, got {len(links)}")
        ids = []
        for lk in links:
            vid = youtube_video_id(lk["url"])
            if vid and vid in ids:
                raise SystemExit(f"{gid}: duplicate video id {vid}")
            if vid:
                ids.append(vid)
            if lk.get("label") == "观看演示视频":
                raise SystemExit(f"{gid}: generic label on {lk['url']}")
        print(f"  OK {gid}: {len(links)} links, labels={[lk['label'][:40] for lk in links]}")


def merge_chunks() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_gid = {c["group_id"]: c for c in old_cap if c.get("is_retrievable", True)}
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = []
    for c in new_chunks:
        gid = c["group_id"]
        if gid in TOUCH_IDS:
            merged = deepcopy(c)
            old = old_by_gid.get(gid)
            if old and old.get("images"):
                merged["images"] = deepcopy(old["images"])
                merged["has_image"] = bool(old.get("has_image") or old["images"])
            out.append(merged)
        elif c["chunk_id"] in old_by_id:
            out.append(old_by_id[c["chunk_id"]])
        else:
            out.append(c)
    (PROD / "chunks_captioned.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    bak = PROD / f"qa_groups.json.bak-{STAMP}"
    if not bak.exists():
        shutil.copy2(PROD / "qa_groups.json", bak)

    groups = load_groups(PROD / "qa_groups.json")
    for g in groups:
        if g["group_id"] in TOUCH_IDS and apply_video_tier_links(g):
            print(f"  transformed {g['group_id']}")
    verify_groups(groups)
    (PROD / "qa_groups.json").write_text(
        json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    subprocess.run(
        [sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")],
        cwd=ROOT,
        check=True,
    )
    merge_chunks()
    subprocess.run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(PROD / "chroma_captioned"),
            "--model",
            str(MODEL),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "_scratch/eval/bl_v1_05_display_probe.py")],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "eval_run.py",
            str(PROD / "chroma_captioned"),
            "--eval",
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/bl_v1_05_youtube_eval.json"),
        ],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()

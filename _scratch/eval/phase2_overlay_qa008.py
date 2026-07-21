#!/usr/bin/env python3
"""阶段 2：外科 overlay qa_008（ladder）→ prod run-ad5s（qa_024 已 overlay）。"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "_scratch/run-ad5s"
PILOT = ROOT / "_scratch/run-ad5s-dry-ladder"
STAMP = "20260703-phase2"
GROUP = "qa_008"
CHUNK_ID = "qa_008_c001"


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def backup() -> None:
    for name in ("chroma_captioned",):
        src = PROD / name
        dst = PROD / f"{name}.bak-{STAMP}"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"backup {src} -> {dst}")
    for name in ("qa_groups.json", "chunks_captioned.json"):
        src = PROD / name
        dst = PROD / f"{name}.bak-{STAMP}"
        shutil.copy2(src, dst)
        print(f"backup {src} -> {dst}")


def merge_qa_groups() -> None:
    prod_groups = load_groups(PROD / "qa_groups.json")
    pilot = next(
        g for g in load_groups(PILOT / "qa_groups.json") if g["group_id"] == GROUP
    )
    if not pilot.get("troubleshooting_ladder"):
        raise SystemExit(f"{GROUP} pilot missing troubleshooting_ladder")
    merged = [pilot if g["group_id"] == GROUP else g for g in prod_groups]
    save_groups(PROD / "qa_groups.json", merged)
    print(f"merged {GROUP} into qa_groups.json (ladder {len(pilot['troubleshooting_ladder'])} steps)")


def merge_chunks_captioned() -> None:
    old = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    new_chunk = next(c for c in new if c["chunk_id"] == CHUNK_ID)
    old_chunk = next(c for c in old if c["chunk_id"] == CHUNK_ID)
    merged_chunk = dict(new_chunk)
    merged_chunk["images"] = old_chunk.get("images") or new_chunk.get("images")
    # 保留 caption 增强后的 embedding_text，避免 eval a08 退化
    if old_chunk.get("embedding_text"):
        merged_chunk["embedding_text"] = old_chunk["embedding_text"]
    out = [merged_chunk if c["chunk_id"] == CHUNK_ID else c for c in old]
    (PROD / "chunks_captioned.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ladder = merged_chunk.get("troubleshooting_ladder") or []
    last = ladder[-1] if ladder else {}
    print(
        f"merged {CHUNK_ID}: ladder={len(ladder)} steps, "
        f"is_last_resort={last.get('is_last_resort')}"
    )


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in (
        "backup",
        "merge-groups",
        "merge-chunks",
        "all",
    ):
        print("usage: phase2_overlay_qa008.py [backup|merge-groups|merge-chunks|all]")
        return 1
    step = sys.argv[1]
    if step in ("backup", "all"):
        backup()
    if step in ("merge-groups", "all"):
        merge_qa_groups()
    if step in ("merge-chunks", "all"):
        merge_chunks_captioned()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

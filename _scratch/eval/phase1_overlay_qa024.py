#!/usr/bin/env python3
"""阶段 1：外科 overlay qa_024 → prod run-ad5s。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "_scratch/run-ad5s"
PILOT = ROOT / "_scratch/run-ad5s-dry-ladder"
STAMP = "20260703-phase1"
GROUP = "qa_024"


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def merge_qa_groups() -> None:
    prod_groups = load_groups(PROD / "qa_groups.json")
    pilot_qa024 = next(
        g for g in load_groups(PILOT / "qa_groups.json") if g["group_id"] == GROUP
    )
    merged = [pilot_qa024 if g["group_id"] == GROUP else g for g in prod_groups]
    if not any(g["group_id"] == GROUP for g in merged):
        raise SystemExit(f"{GROUP} not found in prod qa_groups.json")
    save_groups(PROD / "qa_groups.json", merged)
    print(f"merged {GROUP} into {PROD / 'qa_groups.json'}")


def merge_chunks_captioned() -> None:
    old = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    new_by_id = {c["chunk_id"]: c for c in new if c["group_id"] == GROUP}
    parent_images = next(
        c["images"] for c in old if c["chunk_id"] == f"{GROUP}_parent"
    )
    out: list[dict] = []
    for c in old:
        if c["group_id"] != GROUP:
            out.append(c)
            continue
        merged = dict(new_by_id[c["chunk_id"]])
        if c["chunk_id"] == f"{GROUP}_parent":
            merged["images"] = parent_images
        out.append(merged)
    (PROD / "chunks_captioned.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"merged {GROUP} chunks into chunks_captioned.json ({len(new_by_id)} blocks)")


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


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("backup", "merge-groups", "merge-chunks", "all"):
        print("usage: phase1_overlay_qa024.py [backup|merge-groups|merge-chunks|all]")
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-08b Phase 1: AD5S §十/十一 qa_016–019 bounce title + answer lead disambiguation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PROD = ROOT / "_scratch/run-ad5s"
STAMP = "20260705-bl-v1-08b"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_016", "qa_017", "qa_018", "qa_019", "qa_040"})

PATCHES: dict[str, dict] = {
    "qa_016": {
        "question": "开到位后又弹回来·拉开门 Gate Open Bounce Back · Pull-to-Open · Open Position",
        "answer_zh_prefix": "症状：仅开到位后又弹回来（拉开门·§十开反弹·开门位；非关到位反弹·非§十一·非§十二限位·非§九中途）",
    },
    "qa_017": {
        "question": "开到位后反弹·推开门 Gate Open Bounce Back · Push-to-Open · Limit B",
        "answer_zh_prefix": "症状：开到位后反弹（推开门·§十开反弹·远端限位B；非关到位反弹·非拉开门·非§十二限位）",
    },
    "qa_018": {
        "question": "拉开门 关到位后又弹回来 Gate Close Bounce Back · Pull-to-Open · Limit B",
        "answer_zh_prefix": "症状：拉开门·关到位后又弹回来（§十一关反弹·pull-to-open·远端限位B；非推开门·非开到位反弹·非§十二）",
    },
    "qa_019": {
        "question": "推开门·关到位后又弹回来 Gate Close Bounce Back · Push-to-Open",
        "answer_zh_prefix": "症状：推开门·关到位后又弹回来（§十一关反弹·push-to-open·关门位；非拉开门·非开到位反弹）",
    },
    "qa_040": {
        "question": "开关门中途走停或反弹 Gate Stops or Bounces Mid-Travel",
        "answer_zh_prefix": "症状：开关门中途/一半走停或反弹（§九；非开到位反弹·非关到位反弹·非§十二限位）",
    },
}

OLD_PREFIXES = tuple(p["answer_zh_prefix"] for p in PATCHES.values()) + (
    "症状：开到位后又弹回来（拉开门·§十开反弹·开门位；非§十一关反弹·非§十二限位·非§九中途反弹）",
    "症状：开到位后反弹（推开门·§十开反弹·远端限位B；非拉开门·非§十一关反弹·非§十二限位）",
    "症状：关到位后又弹回来（拉开门·§十一关反弹·远端限位B；非§十开反弹·非§十二关门限位）",
    "症状：关到位反弹（推开门·§十一关反弹·关门位；非拉开门·非§十开反弹·非§十二限位）",
)


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_old_prefix(zh: str) -> str:
    changed = True
    while changed:
        changed = False
        for old in OLD_PREFIXES:
            if zh.startswith(old):
                zh = zh[len(old) :].lstrip("\n")
                changed = True
    return zh


def apply_patches(groups: list[dict]) -> list[dict]:
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in PATCHES:
            continue
        p = PATCHES[gid]
        g["question"] = p["question"]
        zh = strip_old_prefix((g.get("answer_zh") or "").strip())
        prefix = p["answer_zh_prefix"]
        if not zh.startswith(prefix):
            g["answer_zh"] = prefix + ("\n" + zh if zh else "")
        print(f"  patched {gid}: q={g['question'][:52]}…")
    return out


def backup() -> None:
    chroma_dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(PROD / "chroma_captioned", chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        bak = PROD / f"{name}.bak-{STAMP}"
        if not bak.exists():
            shutil.copy2(PROD / name, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def merge_chunks_captioned() -> None:
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
    (PROD / "chunks_captioned.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def pipeline() -> None:
    backup()
    groups = apply_patches(load_groups(PROD / "qa_groups.json"))
    save_groups(PROD / "qa_groups.json", groups)
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")])
    merge_chunks_captioned()
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(PROD / "chroma_captioned"),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(PROD / "chroma_captioned"),
            "--eval",
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/bl_v1_08b_ad5s_eval.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()

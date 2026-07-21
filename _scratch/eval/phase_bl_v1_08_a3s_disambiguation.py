#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-08 Phase 2: A3S §九反弹 + §不限位 qa_015–021 title + answer lead disambiguation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

GROUPS_DIR = ROOT / "_scratch/run-006"
CHROMA_DIR = ROOT / "_scratch/run-007/chroma_captioned"
STAMP = "20260705-bl-v1-08-p2"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({f"qa_{i:03d}" for i in range(15, 22)})

PATCHES: dict[str, dict] = {
    "qa_015": {
        "question": "门关到位又弹回来·拉开门 Gate Bounce Back · Pull-to-Open · Limit B",
        "answer_zh_prefix": "症状：门关到位又弹回来（拉开门·§九反弹·限位B；非推开门·非§十二限位不到位）",
    },
    "qa_016": {
        "question": "门关到位又弹回来·推开门 Gate Bounce Back · Push-to-Open",
        "answer_zh_prefix": "症状：门关到位又弹回来（推开门·§九反弹；非拉开门·非§十二限位不到位）",
    },
    "qa_017": {
        "question": "开门不限位/一直走（方向未明·泛化）Gate Open Limit · No Stop · Direction Unspecified",
        "answer_zh_body": (
            "请先确认安装方向（拉开门或推开门）。\n"
            "拉开门开位不限位 → 查限位A开位组；推开门开位不限位 → 查限位B开位组。\n"
            "若仅说「开门一直走/不限位」且无法区分方向，对照门Bracket安装方式再查对应子项。"
        ),
        "answer_zh_prefix": "症状：开门不限位或一直走且未说明拉/推（泛化入口；非关门限位B/A·非反弹）",
    },
    "qa_018": {
        "question": "开门不限位/位置不对·限位A（拉开门·开位）Gate Open Limit · Pull-to-Open · Limit A Open",
        "answer_zh_prefix": "症状：拉开门开门位置不对或开门不限位（限位A·开位；非关门限位B·非推开门开位）",
    },
    "qa_019": {
        "question": "开门停不下来/过位·限位B（推开门·开位）Gate Open Limit · Push-to-Open · Limit B Open",
        "answer_zh_prefix": "症状：推开门开门停不下来或开门过位（限位B·开位；非关门限位·非拉开门开位）",
    },
    "qa_020": {
        "question": "关门不限位/不到位·限位B（拉开门·关门位）Gate Close Limit · Pull-to-Open · Limit B Close",
        "answer_zh_prefix": "症状：拉开门关门不限位或关门不到位（限位B·关门位；非开门开位·非限位A）",
    },
    "qa_021": {
        "question": "关门不限位/不到位·限位A外移（推开门·关门位）Gate Close Limit · Push-to-Open · Limit A · Magnet",
        "answer_zh_prefix": "症状：推开门关不到位或关门不限位（限位A·关门位·可外移/磁环排查；非开门开位·非限位B）",
    },
}

OLD_PREFIXES = tuple(
    p["answer_zh_prefix"]
    for p in PATCHES.values()
    if "answer_zh_prefix" in p
)


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_old_prefix(zh: str) -> str:
    for old in OLD_PREFIXES:
        if zh.startswith(old):
            return zh[len(old) :].lstrip("\n")
    return zh


def apply_patches(groups: list[dict]) -> list[dict]:
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in PATCHES:
            continue
        p = PATCHES[gid]
        g["question"] = p["question"]
        if "answer_zh_body" in p:
            g["answer_zh"] = p["answer_zh_prefix"] + "\n" + p["answer_zh_body"]
        else:
            zh = strip_old_prefix((g.get("answer_zh") or "").strip())
            prefix = p["answer_zh_prefix"]
            if not zh.startswith(prefix):
                g["answer_zh"] = prefix + ("\n" + zh if zh else "")
        print(f"  patched {gid}: q={g['question'][:52]}…")
    return out


def backup() -> None:
    chroma_dst = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(CHROMA_DIR, chroma_dst)
    groups_path = GROUPS_DIR / "qa_groups.json"
    bak_groups = GROUPS_DIR / f"qa_groups.json.bak-{STAMP}"
    if not bak_groups.exists():
        shutil.copy2(groups_path, bak_groups)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks(use_backup: bool = True) -> list[dict]:
    base = CHROMA_DIR
    if use_backup:
        bak = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
        if (bak / "manifest.json").is_file():
            base = bak
    data = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    return data["chunks"]


def merge_captioned_chunks(new_chunks: list[dict], old_chunks: list[dict]) -> list[dict]:
    """Touched groups: new embedding + preserved image captions. Others: keep prod manifest."""
    out: list[dict] = []
    emitted: set[str] = set()
    for c in new_chunks:
        gid = c["group_id"]
        if gid in emitted:
            continue
        if gid not in TOUCH_IDS:
            for old in old_chunks:
                if old["group_id"] == gid:
                    out.append(deepcopy(old))
            emitted.add(gid)
            continue
        merged = deepcopy(c)
        old = next(
            (x for x in old_chunks if x["group_id"] == gid and x.get("is_retrievable", True)),
            None,
        )
        if old and old.get("images"):
            merged["images"] = deepcopy(old["images"])
            merged["has_image"] = bool(old.get("has_image") or old["images"])
        out.append(merged)
        emitted.add(gid)
    return out


def pipeline() -> None:
    backup()
    old_chunks = load_manifest_chunks()
    groups = apply_patches(load_groups(GROUPS_DIR / "qa_groups.json"))
    save_groups(GROUPS_DIR / "qa_groups.json", groups)
    chunks_out = GROUPS_DIR / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(GROUPS_DIR / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks)
    chunks_captioned = GROUPS_DIR / "chunks_captioned.json"
    chunks_captioned.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(chunks_captioned),
            str(CHROMA_DIR),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(CHROMA_DIR),
            "--eval",
            "eval_queries.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/bl_v1_08_a3s_eval.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()

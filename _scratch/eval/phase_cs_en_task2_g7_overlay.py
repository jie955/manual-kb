#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G7: AD5S #23 auto-close cycle erratic cluster (csq_147–151)."""

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
CHROMA_DIR = PROD / "chroma_captioned"
STAMP = "20260707-cs-en-task2-g7"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_015", "qa_016", "qa_018", "qa_019", "qa_020", "qa_025", "qa_040"})

PATCHES: dict[str, dict] = {
    "qa_040": {
        "question": (
            "开关门中途走停或反弹 · Auto Close Reverses When Starting to Close · "
            "Left Gate Closed Itself No Remote · Reopened Quarter Way Multiple Open Close · "
            "Auto Close Max Only 2 Seconds AD5S Dual Swing"
        ),
        "answer_zh_prefix": (
            "症状：AD5S双臂自动关门循环异常/无遥控自行开合/开四分之一又关/多次开合（§九；"
            "left gate stopped before open position then closed itself · reopened quarter way · "
            "opened and closed multiple times no remote · auto close set to max only stays open 2 seconds · "
            "disconnected battery gate finally closed · dual swing erratic cycle；"
            "非§十一关到位反弹·非§十开到位反弹·非遇阻知识qa_025·非只朝一个方向qa_015）"
        ),
    },
    "qa_016": {
        "answer_zh_prefix": (
            "症状：开到位过远/开门过位/反弹（拉开门·§十·gate bracket·moving rod；"
            "left gate stopped before open position · right gate opens all the way left gate not opening fully · "
            "opens too far gets binded · pull to open cattle gate；"
            "非关到位反弹§十一·非§九auto close循环·非无遥控多次开合）"
        ),
    },
    "qa_015": {
        "question": (
            "两个机臂只朝一个方向 · Dual Swing Left Right Gate Asymmetric · "
            "One Arm Not Opening Fully Other Opens All The Way AD5S"
        ),
        "answer_zh_prefix": (
            "症状：双臂不对称/一侧不开全/只朝一个方向（dual swing · left gate not opening fully · "
            "right gate opens all the way · two arms only work one direction AD5S；"
            "非auto close循环无遥控开合·非reopened quarter way·非§九中途反弹）"
        ),
    },
    "qa_020": {
        "answer_zh_prefix": (
            "症状：关门不到位或关门不限位/开门位置不对（限位B·dual swing left gate not opening fully；"
            "非auto close max 2 seconds·非无遥控多次开合·非§九中途反弹）"
        ),
    },
    "qa_018": {
        "answer_zh_prefix": (
            "症状：拉开门·关到位后又弹回来（§十一关反弹·pull-to-open·远端限位B；"
            "非开到位反弹·非auto close delay中途反转·非§九无遥控循环·非reopened quarter way multiple times）"
        ),
    },
    "qa_019": {
        "answer_zh_prefix": (
            "症状：推开门·关到位后又弹回来（§十一关反弹·push-to-open·关门位；"
            "非开到位反弹·非auto close delay中途反转·非§九无遥控循环）"
        ),
    },
    "qa_025": {
        "answer_zh_prefix": (
            "症状：遇阻反弹知识/双臂延时遇阻判断（§二十；"
            "非auto close delay开始关闭即反转·非auto close max only 2 seconds·"
            "非soft stop delay interaction·非无遥控多次开合）"
        ),
    },
}


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_known_prefix(zh: str, prefixes: tuple[str, ...]) -> str:
    for old in prefixes:
        if zh.startswith(old):
            return zh[len(old) :].lstrip("\n")
    return zh


def apply_patches(groups: list[dict]) -> list[dict]:
    prefixes = tuple(p["answer_zh_prefix"] for p in PATCHES.values() if "answer_zh_prefix" in p)
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in PATCHES:
            continue
        p = PATCHES[gid]
        if "question" in p:
            g["question"] = p["question"]
        if "answer_zh_prefix" in p:
            zh = strip_known_prefix((g.get("answer_zh") or "").strip(), prefixes)
            prefix = p["answer_zh_prefix"]
            if not zh.startswith(prefix):
                g["answer_zh"] = prefix + ("\n" + zh if zh else "")
        print(f"  patched {gid}")
    return out


def backup() -> None:
    chroma_dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists() and CHROMA_DIR.is_dir():
        shutil.copytree(CHROMA_DIR, chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        bak = PROD / f"{name}.bak-{STAMP}"
        if not bak.exists() and (PROD / name).is_file():
            shutil.copy2(PROD / name, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks() -> list[dict]:
    bak = PROD / f"chroma_captioned.bak-{STAMP}"
    base = bak if (bak / "manifest.json").is_file() else CHROMA_DIR
    return json.loads((base / "manifest.json").read_text(encoding="utf-8"))["chunks"]


def build_qa040_ad5s_embedding(question: str, segment: str) -> str:
    return (
        "AD5S dual swing gate reopened quarter way tried to close again multiple times no remote · "
        "left gate stopped before open position then closed itself · "
        "auto close set to max only stays open 2 seconds · "
        "opened and closed multiple times disconnected battery gate finally closed · "
        "gate reverses when starting to close after auto close delay\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa015_dual_embedding(question: str, segment: str) -> str:
    return (
        "right gate opens all the way left gate not opening fully AD5S dual swing · "
        "one arm not opening fully asymmetric dual swing left right gate\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def _merge_chunk_media(new_chunk: dict, old_by_id: dict[str, dict]) -> dict:
    merged = deepcopy(new_chunk)
    old = old_by_id.get(merged["chunk_id"])
    if not old:
        return merged
    if old.get("images"):
        merged["images"] = deepcopy(old["images"])
        merged["has_image"] = bool(old.get("has_image") or old["images"])
    if old.get("links") and not merged.get("links"):
        merged["links"] = deepcopy(old["links"])
        merged["has_links"] = bool(old.get("has_links") or old["links"])
    if old.get("content_en") and not merged.get("content_en"):
        merged["content_en"] = old["content_en"]
    return merged


def merge_captioned_chunks(new_chunks: list[dict], old_chunks: list[dict]) -> list[dict]:
    out: list[dict] = []
    emitted: set[str] = set()
    old_by_gid: dict[str, list[dict]] = {}
    for old in old_chunks:
        old_by_gid.setdefault(old["group_id"], []).append(old)

    for c in new_chunks:
        gid = c["group_id"]
        if gid in emitted:
            continue
        if gid not in TOUCH_IDS:
            out.extend(deepcopy(old_by_gid.get(gid, [])))
            emitted.add(gid)
            continue
        old_by_id = {x["chunk_id"]: x for x in old_by_gid.get(gid, [])}
        for nc in new_chunks:
            if nc["group_id"] != gid:
                continue
            merged = _merge_chunk_media(nc, old_by_id)
            cid = merged.get("chunk_id")
            q = merged.get("question") or ""
            seg = merged.get("content_zh") or ""
            if cid == "qa_040_c001":
                merged["embedding_text"] = build_qa040_ad5s_embedding(q, seg)
            elif cid == "qa_015_c001":
                merged["embedding_text"] = build_qa015_dual_embedding(q, seg)
            out.append(merged)
        emitted.add(gid)
    return out


def pipeline() -> None:
    backup()
    old_chunks = load_manifest_chunks()
    groups = apply_patches(load_groups(PROD / "qa_groups.json"))
    save_groups(PROD / "qa_groups.json", groups)
    chunks_out = PROD / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks)
    cap_path = PROD / "chunks_captioned.json"
    cap_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(cap_path),
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
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/cs_en_task2_ad5s_regression.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()

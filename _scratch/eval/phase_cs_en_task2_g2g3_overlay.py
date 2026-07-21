#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G2+G3: AD5S auto-close reversal + PW802 power cluster enrich + re-embed."""

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
STAMP = "20260707-cs-en-task2-g2g3"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_001", "qa_018", "qa_019", "qa_025", "qa_036", "qa_040"})

PATCHES: dict[str, dict] = {
    "qa_040": {
        "question": (
            "开关门中途走停或反弹 · Auto Close Reverses When Starting to Close · "
            "Second Try Closes · Delay Cycle Gate Stops or Bounces Mid-Travel"
        ),
        "answer_zh_prefix": (
            "症状：自动关门延迟后开始关闭即反转/中途反弹（§九；"
            "gate reverses when starting to close after auto close delay · "
            "additional delay cycle · closes on second try · "
            "soft stop and open close delay interaction；"
            "非§十一关到位反弹·非§十开到位反弹·非遇阻知识qa_025）"
        ),
    },
    "qa_018": {
        "answer_zh_prefix": (
            "症状：拉开门·关到位后又弹回来（§十一关反弹·pull-to-open·远端限位B；"
            "非开到位反弹·非auto close delay中途反转·非§九中途）"
        ),
    },
    "qa_019": {
        "answer_zh_prefix": (
            "症状：推开门·关到位后又弹回来（§十一关反弹·push-to-open·关门位；"
            "非开到位反弹·非auto close delay中途反转·非§九中途）"
        ),
    },
    "qa_025": {
        "answer_zh_prefix": (
            "症状：遇阻反弹知识/双臂延时遇阻判断（§二十；"
            "非auto close delay开始关闭即反转·非soft stop delay interaction）"
        ),
    },
    "qa_036": {
        "answer_zh_prefix": (
            "症状：运行慢/11#12#电压/调FORCE与SOFT STOP（"
            "非auto close reverses when starting to close·非delay cycle second try）"
        ),
    },
    "qa_001": {
        "question": (
            "控制板灯不亮（适配器）No Led On the Control Board · "
            "Power LED Flashes Red · Won't Work After Installation"
        ),
        "answer_zh_prefix": (
            "症状：完全不工作/控制板无反应/红灯闪（PW802·dual swing·安装后曾正常；"
            "red light flashing · won't work after installation · power LED flashes red · "
            "everything worked now won't work；非CODE LED微微亮·非单臂只朝一个方向）"
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
    if not chroma_dst.exists():
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


def build_qa040_symptom_embedding(question: str, segment: str) -> str:
    return (
        "gate reverses when starting to close after auto close delay · "
        "additional delay cycle tries again to close second try · "
        "dual swing AD8S auto close reverses then closes on second attempt · "
        "soft stop and open close delay interaction gate reverses half the time\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa001_embedding(question: str, answer_zh: str) -> str:
    return (
        "PW802 red light flashing gate won't work after installation · "
        "power LED flashes red dual swing gate opener not working · "
        "installed everything worked now won't work · red light flashlight\n"
        f"{question}\n{answer_zh}"
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
            if cid == "qa_040_c001":
                merged["embedding_text"] = build_qa040_symptom_embedding(
                    merged.get("question") or "",
                    merged.get("content_zh") or "",
                )
            elif gid == "qa_001" and merged.get("is_retrievable"):
                merged["embedding_text"] = build_qa001_embedding(
                    merged.get("question") or "",
                    merged.get("content_zh") or merged.get("embedding_text") or "",
                )
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

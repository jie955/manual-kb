#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G4: AD5S #19 open/limit + A3S #18/#21 power cluster enrich."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260707-cs-en-task2-g4"

AD5S_PROD = ROOT / "_scratch/run-ad5s"
AD5S_CHROMA = AD5S_PROD / "chroma_captioned"
AD5S_TOUCH = frozenset({"qa_005", "qa_016", "qa_019", "qa_020", "qa_025", "qa_037"})

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
A3S_TOUCH = frozenset({"qa_001", "qa_014"})

AD5S_PATCHES: dict[str, dict] = {
    "qa_016": {
        "question": (
            "开到位后又弹回来·拉开门 · Opens Too Far Gets Binded · "
            "Pull-to-Open Gate Bracket · Gate Open Bounce Back · Open Position"
        ),
        "answer_zh_prefix": (
            "症状：开到位过远/开门过位/反弹（拉开门·§十·gate bracket·moving rod；"
            "opens too far gets binded · first open hard stall force turned down · "
            "pull to open cattle gate；非关到位反弹§十一·非§九auto close）"
        ),
    },
    "qa_037": {
        "question": (
            "开门不限位/过位 · Opens Too Far · Pull-to-Open · Limit A Open · "
            "Gate Bracket Moving Rod Retracted"
        ),
        "answer_zh_prefix": (
            "症状：开门过远/开门不限位（限位A·拉开门·gate bracket；"
            "opens too far · open position too far · moving rod properly retracted · "
            "gets binded · AD5S dual solar pull to open；非关不到位·非遥控学码）"
        ),
    },
    "qa_020": {
        "answer_zh_prefix": (
            "症状：关门不到位或关门不限位（限位B·关门位；"
            "sometimes doesn't close · mind of its own · doesn't close fully；"
            "非开门过远·非开到位反弹）"
        ),
    },
    "qa_005": {
        "answer_zh_prefix": (
            "症状：遥控学不进去/学码灯不亮（remote not picking up · cannot program learn · "
            "clear remote codes reprogram M12；非开门过远·非限位）"
        ),
    },
    "qa_025": {
        "answer_zh_prefix": (
            "症状：遇阻反弹知识/双臂延时遇阻判断（§二十；"
            "非opens too far · 非gate bracket open position · 非remote not recognized）"
        ),
    },
    "qa_019": {
        "answer_zh_prefix": (
            "症状：推开门·关到位后又弹回来（§十一关反弹·push-to-open·关门位；"
            "非拉开门opens too far·非gate bracket开位）"
        ),
    },
}

A3S_PATCHES: dict[str, dict] = {
    "qa_001": {
        "question": (
            "控制板灯不亮（适配器）No Led On the Control Board · "
            "Batteries and AC Adapter Nothing Works · Board Has Power Arms Won't Move"
        ),
        "answer_zh_prefix": (
            "症状：完全不工作/无反应（batteries and AC adapter · not getting anything to work · "
            "nothing works · board has power won't send power to arm terminals · "
            "arms won't open or close · lights blink click；"
            "非CODE LED微微亮·非太阳能板单独故障）"
        ),
    },
    "qa_014": {
        "answer_zh_prefix": (
            "症状：只CODE LED微微亮/门机不工作但非完全无反应（"
            "非batteries AC adapter nothing works · 非board has power arms won't move）"
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


def apply_patches(groups: list[dict], patches: dict[str, dict], touch: frozenset[str]) -> list[dict]:
    prefixes = tuple(p["answer_zh_prefix"] for p in patches.values() if "answer_zh_prefix" in p)
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in touch:
            continue
        p = patches[gid]
        if "question" in p:
            g["question"] = p["question"]
        if "answer_zh_prefix" in p:
            zh = strip_known_prefix((g.get("answer_zh") or "").strip(), prefixes)
            prefix = p["answer_zh_prefix"]
            if not zh.startswith(prefix):
                g["answer_zh"] = prefix + ("\n" + zh if zh else "")
        print(f"  patched {gid}")
    return out


def backup(prod: Path, chroma: Path) -> None:
    chroma_dst = prod / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists() and chroma.is_dir():
        shutil.copytree(chroma, chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        src = prod / name
        bak = prod / f"{name}.bak-{STAMP}"
        if src.is_file() and not bak.exists():
            shutil.copy2(src, bak)


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks(prod: Path) -> list[dict]:
    bak = prod / f"chroma_captioned.bak-{STAMP}"
    chroma = prod / "chroma_captioned"
    base = bak if (bak / "manifest.json").is_file() else chroma
    return json.loads((base / "manifest.json").read_text(encoding="utf-8"))["chunks"]


def build_ad5s_open_embedding(question: str, segment: str) -> str:
    return (
        "AD5S dual solar gate opens too far gets binded sometimes doesn't close · "
        "opens too far open position gate bracket moving rod pull to open · "
        "first open hard turned down stall force · remote not picking up\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_a3s_power_embedding(question: str, answer_zh: str) -> str:
    return (
        "batteries and AC adapter installed not getting anything to work nothing works · "
        "A5 A8 gate opener batteries AC adapter · "
        "motherboard has power arms won't open or close click noise · "
        "board has power will not send power to arm terminals\n"
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


def merge_captioned_chunks(
    new_chunks: list[dict],
    old_chunks: list[dict],
    touch_ids: frozenset[str],
    *,
    custom_embedding: dict[str, str] | None = None,
) -> list[dict]:
    out: list[dict] = []
    emitted: set[str] = set()
    old_by_gid: dict[str, list[dict]] = {}
    for old in old_chunks:
        old_by_gid.setdefault(old["group_id"], []).append(old)
    custom_embedding = custom_embedding or {}

    for c in new_chunks:
        gid = c["group_id"]
        if gid in emitted:
            continue
        if gid not in touch_ids:
            out.extend(deepcopy(old_by_gid.get(gid, [])))
            emitted.add(gid)
            continue
        old_by_id = {x["chunk_id"]: x for x in old_by_gid.get(gid, [])}
        for nc in new_chunks:
            if nc["group_id"] != gid:
                continue
            merged = _merge_chunk_media(nc, old_by_id)
            cid = merged.get("chunk_id") or ""
            if cid in custom_embedding:
                merged["embedding_text"] = custom_embedding[cid]
            elif gid == "qa_001" and merged.get("is_retrievable") and "__qa_001__" in custom_embedding:
                merged["embedding_text"] = custom_embedding["__qa_001__"]
            out.append(merged)
        emitted.add(gid)
    return out


def pipeline_library(
    label: str,
    prod: Path,
    chroma: Path,
    patches: dict[str, dict],
    touch_ids: frozenset[str],
    eval_file: str,
    eval_out: Path,
) -> None:
    print(f"\n=== {label} ===")
    backup(prod, chroma)
    old_chunks = load_manifest_chunks(prod)
    groups = apply_patches(load_groups(prod / "qa_groups.json"), patches, touch_ids)
    save_groups(prod / "qa_groups.json", groups)
    chunks_out = prod / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(prod / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    custom_embedding = build_custom_embedding(label, new_chunks, groups)
    merged = merge_captioned_chunks(new_chunks, old_chunks, touch_ids, custom_embedding=custom_embedding)
    cap_path = prod / "chunks_captioned.json"
    cap_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(cap_path),
            str(chroma),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(chroma),
            "--eval",
            eval_file,
            "--model",
            str(MODEL),
            "--json-out",
            str(eval_out),
        ]
    )


def ad5s_custom_embeddings(new_chunks: list[dict], groups: list[dict]) -> dict[str, str]:
    custom: dict[str, str] = {}
    g016 = next(g for g in groups if g["group_id"] == "qa_016")
    g037 = next(g for g in groups if g["group_id"] == "qa_037")
    for c in new_chunks:
        cid = c.get("chunk_id") or ""
        if cid == "qa_037_c001":
            custom[cid] = build_ad5s_open_embedding(g037.get("question") or "", c.get("content_zh") or "")
        elif c["group_id"] == "qa_016" and cid.endswith("_c001"):
            custom[cid] = build_ad5s_open_embedding(g016.get("question") or "", c.get("content_zh") or "")
    return custom


def a3s_custom_embeddings(groups: list[dict]) -> dict[str, str]:
    g001 = next(g for g in groups if g["group_id"] == "qa_001")
    return {
        "__qa_001__": build_a3s_power_embedding(
            g001.get("question") or "",
            g001.get("answer_zh") or "",
        )
    }


def build_custom_embedding(
    label: str,
    new_chunks: list[dict],
    groups: list[dict],
) -> dict[str, str] | None:
    if label.startswith("AD5S"):
        return ad5s_custom_embeddings(new_chunks, groups)
    if label.startswith("A3S"):
        return a3s_custom_embeddings(groups)
    return None


def pipeline() -> None:
    print(f"backup stamp {STAMP}")
    pipeline_library(
        "AD5S G4",
        AD5S_PROD,
        AD5S_CHROMA,
        AD5S_PATCHES,
        AD5S_TOUCH,
        "eval_queries_ad5s.json",
        ROOT / "_scratch/eval/cs_en_task2_ad5s_regression.json",
    )
    pipeline_library(
        "A3S G3b",
        A3S_PROD,
        A3S_CHROMA,
        A3S_PATCHES,
        A3S_TOUCH,
        "eval_queries.json",
        ROOT / "_scratch/eval/cs_en_task2_zh_regression.json",
    )


if __name__ == "__main__":
    pipeline()

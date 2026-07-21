#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A3S §十 qa_017 dual-zone synthesis + qa_019 symptom boost (开位不限位 disambig)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from image_utils import normalize_images

GROUPS_DIR = ROOT / "_scratch/run-006"
CHROMA_DIR = ROOT / "_scratch/run-007/chroma_captioned"
STAMP = "20260706-a3s-qa017-dual-zone"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_017", "qa_019", "qa_021"})

QUESTION_017 = "开门不限位/一直走 Gate Open Limit · No Stop"
PREFIX_017 = "症状：开门不限位或一直走且未说明拉/推（泛化入口；非关门限位B/A·非反弹）"
INTRO_017 = "请先确认安装方向（若已知可略读另一区）。"
ZONE1_TITLE = "1) 拉开门安装 For pull-to-open installation"
ZONE2_TITLE = "2) 推开门安装 For push-to-open installation"

QUESTION_019 = (
    "开门不限位/停不下来·限位B（推开门·开位）"
    " Gate Open Limit · Push-to-Open · Limit B Open"
)
PREFIX_019 = (
    "症状：推开门开位不限位或开门停不下来或开门过位"
    "（限位B·开位；非关门限位·非拉开门开位·非方向未明泛化）"
)
OLD_PREFIX_019 = (
    "症状：推开门开门停不下来或开门过位或开位不限位"
    "（限位B·开位；非关门限位·非拉开门开位）"
)
OLD_PREFIX_019_ALT = (
    "症状：推开门开门停不下来或开门过位（限位B·开位；非关门限位·非拉开门开位）"
)


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_symptom_prefix(zh: str) -> str:
    zh = (zh or "").strip()
    while zh.startswith("症状："):
        nl = zh.find("\n")
        if nl < 0:
            return ""
        zh = zh[nl + 1 :].lstrip("\n")
    return zh.strip()


def build_qa017_answer(groups: list[dict]) -> tuple[str, list[str]]:
    g18 = next(g for g in groups if g["group_id"] == "qa_018")
    g19 = next(g for g in groups if g["group_id"] == "qa_019")
    steps_18 = strip_symptom_prefix(g18.get("answer_zh") or "")
    steps_19 = strip_symptom_prefix(g19.get("answer_zh") or "")
    body = (
        f"{PREFIX_017}\n{INTRO_017}\n\n"
        f"{ZONE1_TITLE}\n{steps_18}\n\n"
        f"{ZONE2_TITLE}\n{steps_19}"
    )
    images = list(g18.get("images") or []) + list(g19.get("images") or [])
    return body, images


def build_qa017_embedding() -> str:
    """Display title is clean; embedding keeps vague-only retrieval signals."""
    return (
        f"{QUESTION_017}\n"
        f"{PREFIX_017}\n"
        "请先确认安装方向。\n"
        "方向未明 · 泛化 · 开门一直走 · 不限位 · 两区均展示\n"
        "（非推开门 · 非拉开门 · 非已指明安装方向）"
    )


def build_qa019_embedding(question: str, answer_zh: str) -> str:
    return (
        "推开门开位不限位\n"
        "推开门开位不限位 推开门开门停不下来 推开门开门过位\n"
        f"{question}\n{answer_zh}"
    ).strip()


def build_qa021_embedding(question: str, answer_zh: str) -> str:
    return (
        "推开门关不到位 推开门关门不限位 推开门 关不到位 不限位\n"
        f"{question}\n{answer_zh}"
    ).strip()


def apply_patches(groups: list[dict]) -> list[dict]:
    out = deepcopy(groups)
    body_017, imgs_017 = build_qa017_answer(out)
    for g in out:
        gid = g["group_id"]
        if gid == "qa_017":
            g["question"] = QUESTION_017
            g["answer_zh"] = body_017
            g["images"] = imgs_017
            print(f"  patched {gid}: dual-zone len={len(body_017)} imgs={len(imgs_017)}")
        elif gid == "qa_019":
            g["question"] = QUESTION_019
            steps = strip_symptom_prefix(g.get("answer_zh") or "")
            g["answer_zh"] = PREFIX_019 + ("\n" + steps if steps else "")
            print(f"  patched {gid}: title+prefix 推开门开位不限位")
    return out


def backup() -> None:
    chroma_dst = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(CHROMA_DIR, chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        src = GROUPS_DIR / name
        dst = GROUPS_DIR / f"{name}.bak-{STAMP}"
        if src.is_file() and not dst.exists():
            shutil.copy2(src, dst)
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


def merge_image_captions(imgs: list, old_chunks: list[dict]) -> list[dict]:
    caption_by_file: dict[str, dict] = {}
    for c in old_chunks:
        for img in normalize_images(c.get("images")):
            if img.get("caption"):
                caption_by_file[img["file"]] = deepcopy(img)
    out: list[dict] = []
    for img in normalize_images(imgs):
        out.append(deepcopy(caption_by_file.get(img["file"], img)))
    return out


def merge_captioned_chunks(new_chunks: list[dict], old_chunks: list[dict]) -> list[dict]:
    out: list[dict] = []
    emitted: set[str] = set()
    embed_017 = build_qa017_embedding()
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
        merged = deepcopy(
            next(
                c
                for c in new_chunks
                if c["group_id"] == gid and c.get("is_retrievable", True)
            )
        )
        merged["is_retrievable"] = True
        merged["is_child"] = False
        if gid == "qa_017":
            merged["embedding_text"] = embed_017
            if merged.get("images"):
                merged["images"] = merge_image_captions(merged["images"], old_chunks)
                merged["has_image"] = bool(merged["images"])
        elif gid == "qa_019":
            merged["embedding_text"] = build_qa019_embedding(
                merged.get("question") or "", merged.get("content_zh") or ""
            )
        elif gid == "qa_021":
            merged["embedding_text"] = build_qa021_embedding(
                merged.get("question") or "", merged.get("content_zh") or ""
            )
        out.append(merged)
        emitted.add(gid)
    return out


def probe() -> None:
    from qa_server import _ask, _init_engine, _load_dotenv

    _load_dotenv()
    _init_engine(CHROMA_DIR, str(MODEL))
    probes = [
        ("q21-vague", "开门一直走 不限位", "qa_017"),
        ("q23b-push-open", "推开门开位不限位", "qa_019"),
        ("q25-close", "推开门 关不到位 不限位", "qa_021"),
        ("q23-existing", "推开门 开门停不下来", "qa_019"),
        ("q22-pull-open", "拉开门 开门位置不对 不限位", "qa_018"),
    ]
    print("\n=== §十 probe ===")
    for tag, q, exp in probes:
        top = (_ask(q, use_llm=False).get("hits") or [None])[0] or {}
        gid = top.get("group_id")
        score = top.get("score") or 0.0
        zh = top.get("content_zh") or ""
        ok = gid == exp
        extra = ""
        if exp == "qa_017":
            extra = f" zones={'拉开门' in zh and '推开门' in zh}"
        print(f"{tag} | {q} | top1={gid}({score:.3f}){extra} | {'PASS' if ok else 'FAIL'}")


def pipeline() -> None:
    backup()
    groups = apply_patches(load_groups(GROUPS_DIR / "qa_groups.json"))
    save_groups(GROUPS_DIR / "qa_groups.json", groups)
    old_chunks = load_manifest_chunks()
    chunks_out = GROUPS_DIR / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(GROUPS_DIR / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks)
    cap_path = GROUPS_DIR / "chunks_captioned.json"
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
            "eval_queries.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/a3s_qa017_dual_zone_eval.json"),
        ]
    )
    probe()


if __name__ == "__main__":
    pipeline()

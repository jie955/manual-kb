#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AD5S §十七 router synthesis (qa_041 三步全流程) + qa_042 images + retrieval disambig."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from chunk_builder import build_single_chunk
from docx import Document
from image_utils import normalize_images
from qa_doc_extractor import extract_images_from_paragraph, get_heading_level, iter_block_items

PROD = ROOT / "_scratch/run-ad5s"
CHROMA = PROD / "chroma_captioned"
STAMP = "20260706-ad5s-sec17-router"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
DOCX = ROOT / "samples/troubleshooting/AD5S-AD8S常见问题排查.docx"
IMAGE_DIR = PROD / "images"
SECTION_KEY = "十七、离合打不开"

TOUCH_IDS = frozenset({"qa_041", "qa_042"})

QUESTION_041 = "离合打不开 Clutch Won't Release"
PREFIX_041 = "症状：离合钥匙拧不开且未说明关门太紧/伸太过/内部卡住（泛化入口）"
INTRO_041 = "建议按顺序排查（若已知原因可略读其他步）。"
ZONE1_TITLE = "1) 脱门测·关门太紧 For gate closed too tight"
ZONE2_TITLE = "2) 伸太过·旋转拉杆 For over-extended arm"
ZONE3_TITLE = "3) 离合件分离/内部卡住 For clutch jam · lubrication"

QUESTION_042 = (
    "离合打不开·伸太过或内部卡住 Clutch Won't Release · Over-Extended or Internal Jam"
)
PREFIX_042 = (
    "症状：脱门仍打不开离合·伸太过或内部卡住"
    "（非关门太紧·非泛化未分场景）"
)

# docx §十七 inline: 限位B/伸太过 · 内部剖面 · 离合件B/C
QA_042_IMAGES = [
    "image_032.png",
    "image_031.png",
    "image_035.png",
]


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def next_image_index() -> int:
    nums = []
    for p in IMAGE_DIR.glob("image_*.*"):
        try:
            nums.append(int(p.stem.split("_")[1]))
        except (IndexError, ValueError):
            continue
    return max(nums) if nums else 0


def sec17_images_ready() -> bool:
    return all((IMAGE_DIR / name).is_file() for name in QA_042_IMAGES)


def extract_sec17_images() -> list[str]:
    """Extract §十七 inline images only when targets are missing."""
    if sec17_images_ready():
        print(f"  sec17 images already present: {QA_042_IMAGES}")
        return []
    doc = Document(str(DOCX))
    counter = [next_image_index()]
    in_sec = False
    found: list[str] = []
    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        lv = get_heading_level(block)
        if lv == 1:
            t = block.text.strip()
            if in_sec and SECTION_KEY.split("、")[0] not in t:
                break
            in_sec = SECTION_KEY in t
            continue
        if not in_sec:
            continue
        imgs = extract_images_from_paragraph(block, doc, str(IMAGE_DIR), counter)
        found.extend(imgs)
    print(f"  sec17 images extracted this run: {found}")
    return found


def split_steps_23(zh: str) -> tuple[str, str]:
    zh = (zh or "").strip()
    if not zh.startswith("2 "):
        return zh, ""
    idx3 = zh.find("\n3 ")
    if idx3 >= 0:
        return zh[2:idx3].strip(), zh[idx3 + 3 :].strip()
    return zh[2:].strip(), ""


def strip_child_prefix(zh: str) -> str:
    zh = (zh or "").strip()
    while zh.startswith("症状："):
        nl = zh.find("\n")
        if nl < 0:
            return ""
        zh = zh[nl + 1 :].lstrip()
    return zh


def build_qa041_answer(g41: dict, g42: dict) -> str:
    step1 = (g41.get("answer_zh") or "").strip()
    raw42 = strip_child_prefix(g42.get("answer_zh") or "")
    step2, step3 = split_steps_23(raw42 if raw42.startswith("2 ") else "2 " + raw42)
    parts = [PREFIX_041, INTRO_041, "", ZONE1_TITLE, step1]
    if step2:
        parts.extend(["", ZONE2_TITLE, step2])
    if step3:
        parts.extend(["", ZONE3_TITLE, step3])
    return "\n".join(parts)


def build_qa041_embedding() -> str:
    return (
        "离合打不开\n"
        f"{QUESTION_041}\n"
        f"{PREFIX_041}\n"
        "离合钥匙拧不开 · 泛化 · 三步均展示\n"
        "（非关门太紧 · 非伸太过 · 非已指明具体场景）"
    )


def build_qa042_embedding(question: str, answer_zh: str) -> str:
    return (
        "脱门也打不开离合 伸太过推不进去\n"
        "离合打不开 伸太过 内部卡住\n"
        f"{question}\n{answer_zh}"
    ).strip()


CANON_BAK = PROD / f"qa_groups.json.bak-{STAMP}"


def canonical_sec17_sources(groups: list[dict]) -> tuple[dict, dict]:
    """Always build router body from pre-overlay sources (idempotent re-runs)."""
    if CANON_BAK.is_file():
        src = load_groups(CANON_BAK)
        return (
            next(g for g in src if g["group_id"] == "qa_041"),
            next(g for g in src if g["group_id"] == "qa_042"),
        )
    g41 = next(g for g in groups if g["group_id"] == "qa_041")
    g42 = next(g for g in groups if g["group_id"] == "qa_042")
    step1 = (g41.get("answer_zh") or "").strip()
    if ZONE1_TITLE in step1:
        i1 = step1.index(ZONE1_TITLE) + len(ZONE1_TITLE)
        i2 = step1.find(ZONE2_TITLE, i1)
        step1 = step1[i1:i2].strip() if i2 > i1 else step1
    elif step1.startswith("1"):
        step1 = step1[1:].lstrip()
    g41 = {**g41, "answer_zh": step1}
    raw42 = strip_child_prefix(g42.get("answer_zh") or "")
    if not raw42.startswith("2 "):
        raw42 = "2 " + raw42.split("\n2 ", 1)[-1] if "\n2 " in raw42 else raw42
    g42 = {**g42, "answer_zh": raw42}
    return g41, g42


def apply_patches(groups: list[dict]) -> None:
    g41 = next(g for g in groups if g["group_id"] == "qa_041")
    g42 = next(g for g in groups if g["group_id"] == "qa_042")
    src41, src42 = canonical_sec17_sources(groups)
    body_041 = build_qa041_answer(src41, src42)
    g41["question"] = QUESTION_041
    g41["answer_zh"] = body_041
    g41["images"] = list(QA_042_IMAGES)
    g41["links"] = deepcopy(src42.get("links") or g42.get("links") or [])

    raw42 = strip_child_prefix(src42.get("answer_zh") or "")
    if not raw42.startswith("2 "):
        raw42 = "2 " + raw42
    step2, step3 = split_steps_23(raw42)
    g42["question"] = QUESTION_042
    g42["answer_zh"] = PREFIX_042 + "\n2 " + step2 + ("\n3 " + step3 if step3 else "")
    g42["images"] = list(QA_042_IMAGES)
    print(f"  qa_041 router: zh_len={len(body_041)} imgs={len(g41['images'])} links={len(g41['links'])}")
    print(f"  qa_042 child: zh_len={len(g42['answer_zh'])} imgs={len(g42['images'])}")


def backup() -> None:
    dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if not dst.exists():
        shutil.copytree(CHROMA, dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        src = PROD / name
        bak = PROD / f"{name}.bak-{STAMP}"
        if src.is_file() and not bak.exists():
            shutil.copy2(src, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks() -> list[dict]:
    bak = PROD / f"chroma_captioned.bak-{STAMP}"
    base = bak if (bak / "manifest.json").is_file() else CHROMA
    return json.loads((base / "manifest.json").read_text(encoding="utf-8"))["chunks"]


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


def build_router_chunk(group: dict, embedding_text: str, old_chunks: list[dict]) -> dict:
    """Force single retrievable chunk (router answers exceed SHORT_GROUP_THRESHOLD)."""
    chunk = build_single_chunk(group)
    chunk["embedding_text"] = embedding_text
    chunk["parent_id"] = None
    chunk["is_child"] = False
    chunk["is_retrievable"] = True
    if group.get("images"):
        chunk["images"] = merge_image_captions(group["images"], old_chunks)
        chunk["has_image"] = bool(chunk["images"])
    if group.get("links"):
        chunk["links"] = deepcopy(group["links"])
        chunk["has_links"] = True
    return chunk


def merge_captioned_chunks(
    new_chunks: list[dict], old_chunks: list[dict], groups: list[dict]
) -> list[dict]:
    out: list[dict] = []
    emitted: set[str] = set()
    embed_041 = build_qa041_embedding()
    group_by_id = {g["group_id"]: g for g in groups}
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
        if gid == "qa_041":
            merged = build_router_chunk(group_by_id["qa_041"], embed_041, old_chunks)
        else:
            merged = deepcopy(
                next(
                    x
                    for x in new_chunks
                    if x["group_id"] == gid and x.get("is_retrievable", True)
                )
            )
            merged["is_retrievable"] = True
            merged["is_child"] = False
            merged["parent_id"] = None
            merged["embedding_text"] = build_qa042_embedding(
                merged.get("question") or "", merged.get("content_zh") or ""
            )
            if merged.get("images"):
                merged["images"] = merge_image_captions(merged["images"], old_chunks)
                merged["has_image"] = bool(merged["images"])
            if merged.get("links"):
                merged["has_links"] = True
        out.append(merged)
        emitted.add(gid)
    return out


def probe() -> None:
    from qa_server import _ask, _init_engine, _load_dotenv

    _load_dotenv()
    _init_engine(CHROMA, str(MODEL))
    probes = [
        ("bare", "离合打不开", "qa_041"),
        ("tight", "离合钥匙拧不开 门关到位很紧", "qa_041"),
        ("extend", "脱门也打不开离合 伸太过推不进去", "qa_042"),
    ]
    print("\n=== §十七 probe ===")
    for tag, q, exp in probes:
        top = (_ask(q, use_llm=False).get("hits") or [None])[0] or {}
        gid = top.get("group_id")
        zh = top.get("content_zh") or ""
        imgs = len(top.get("images") or [])
        ok = gid == exp
        extra = ""
        if exp == "qa_041":
            extra = f" zones={'脱门测' in zh and '伸太过' in zh and '离合件' in zh} imgs={imgs}"
        print(f"{tag} | {q} | top1={gid}({top.get('score', 0):.3f}){extra} | {'PASS' if ok else 'FAIL'}")


def pipeline() -> None:
    backup()
    extract_sec17_images()
    groups = load_groups(PROD / "qa_groups.json")
    apply_patches(groups)
    save_groups(PROD / "qa_groups.json", groups)
    old_chunks = load_manifest_chunks()
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")])
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks, groups)
    (PROD / "chunks_captioned.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(CHROMA),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(CHROMA),
            "--eval",
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/ad5s_sec17_router_eval.json"),
        ]
    )
    probe()


if __name__ == "__main__":
    pipeline()

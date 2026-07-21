#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A3S §十三 fix: merge qa_036+qa_037 → single qa_037 matching docx H1 (no H2 split)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from docx import Document
from image_utils import normalize_images
from link_utils import infer_link_type, normalize_link
from qa_doc_extractor import classify_language, get_heading_level, iter_block_items

RUN = ROOT / "_scratch/run-006"
CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
STAMP = "20260706-a3s-sec13-merge"
DOCX = ROOT / "samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"

MERGE_GID = "qa_037"
REMOVE_GID = "qa_036"
TOUCH_IDS = frozenset({MERGE_GID, REMOVE_GID})

SECTION_QUESTION = "电机转机臂不伸缩 Motor Runs But Gate Doesn't Move"
LINK_PLACEHOLDER_ZH = frozenset({"博客文章链接：", "科普文章链接："})


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_orphan_section(doc: Document, section_key: str) -> tuple[str, list[dict]]:
    full_title: str | None = None
    in_section = False
    paras: list[dict] = []

    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        if not text:
            continue
        level = get_heading_level(block)
        if level == 1:
            if in_section and full_title:
                break
            in_section = section_key in text
            if in_section:
                full_title = text
            continue
        if not in_section:
            continue
        if level in (2, 3):
            continue
        paras.append({"text": text, "lang": classify_language(text)})

    if not full_title or not paras:
        raise SystemExit(f"orphan section not found or empty: {section_key} ({len(paras)} paras)")
    return full_title, paras


def build_merged_group(doc: Document, images: list[str]) -> dict:
    full_title, paras = collect_orphan_section(doc, "十三、电机转机臂不伸缩")
    if len(paras) != 16:
        raise SystemExit(f"expected 16 orphan paras for §十三, got {len(paras)}")

    g: dict = {
        "group_id": MERGE_GID,
        "section": full_title,
        "question": SECTION_QUESTION,
        "heading_level": 2,
        "answer_zh": "",
        "answer_en": "",
        "images": list(images),
        "links": [],
        "negotiation_offers": [],
        "structure_warnings": [],
    }
    zh_lines: list[str] = []
    en_lines: list[str] = []
    seen_urls: set[str] = set()

    for p in paras:
        text, lang = p["text"], p["lang"]
        if lang == "zh" and text.strip() in LINK_PLACEHOLDER_ZH:
            continue
        if lang == "zh":
            zh_lines.append(text)
        elif lang == "en":
            en_lines.append(text)
        for url in re.findall(r"https?://[^\s<>\"']+", text):
            url = url.rstrip(".,);]")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            g["links"].append(
                normalize_link(
                    {
                        "url": url,
                        "label": "观看演示视频" if infer_link_type(url) == "video" else "参考支持页",
                        "lang": lang,
                        "link_type": infer_link_type(url),
                    }
                )
            )

    g["answer_zh"] = "\n".join(zh_lines)
    g["answer_en"] = "\n".join(en_lines)
    print(
        f"  {MERGE_GID}: §十三 merged · paras=16 · zh={len(g['answer_zh'])} · "
        f"en={len(g['answer_en'])} · links={len(g['links'])} · imgs={len(g['images'])}"
    )
    return g


def merge_qa_groups() -> None:
    doc = Document(str(DOCX))
    groups = load_groups(RUN / "qa_groups.json")
    old_036 = next(g for g in groups if g["group_id"] == REMOVE_GID)
    images = list(old_036.get("images") or [])
    merged = build_merged_group(doc, images)
    out = [g for g in groups if g["group_id"] not in TOUCH_IDS]
    out.append(merged)
    out.sort(key=lambda g: g["group_id"])
    save_groups(RUN / "qa_groups.json", out)
    print(f"qa_groups: removed {REMOVE_GID} · merged into {MERGE_GID} · total={len(out)}")


def merge_image_captions(new_imgs: list, old_chunks: list[dict]) -> list[dict]:
    caption_by_file: dict[str, dict] = {}
    for c in old_chunks:
        for img in normalize_images(c.get("images")):
            if img.get("caption"):
                caption_by_file[img["file"]] = deepcopy(img)
    out: list[dict] = []
    for img in normalize_images(new_imgs):
        out.append(deepcopy(caption_by_file.get(img["file"], img)))
    return out


def merge_chunks_captioned(old_cap_path: Path) -> None:
    old_cap = json.loads(old_cap_path.read_text(encoding="utf-8"))
    new_chunks = json.loads((RUN / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    old_036 = next((c for c in old_cap if c["group_id"] == REMOVE_GID), None)
    out: list[dict] = []
    for c in new_chunks:
        if c["group_id"] == MERGE_GID:
            merged = deepcopy(c)
            imgs = merged.get("images") or (old_036.get("images") if old_036 else [])
            if imgs:
                merged["images"] = merge_image_captions(imgs, old_cap)
                merged["has_image"] = bool(merged["images"])
            out.append(merged)
        elif c["chunk_id"] in old_by_id and c["group_id"] not in TOUCH_IDS:
            out.append(deepcopy(old_by_id[c["chunk_id"]]))
        else:
            out.append(deepcopy(c))
    (RUN / "chunks_captioned.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"chunks_captioned: {len(out)} chunks (dropped {REMOVE_GID})")


def backup() -> None:
    chroma_dst = ROOT / f"_scratch/run-007/chroma_captioned.bak-{STAMP}"
    if chroma_dst.exists():
        shutil.rmtree(chroma_dst)
    shutil.copytree(CHROMA, chroma_dst)
    print(f"backup {CHROMA} -> {chroma_dst}")
    for name in ("qa_groups.json", "chunks_captioned.json"):
        shutil.copy2(RUN / name, RUN / f"{name}.bak-{STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def probe() -> None:
    from qa_server import _ask, _init_engine, _load_dotenv

    _load_dotenv()
    _init_engine(CHROMA, str(MODEL))
    probes = [
        ("sec13-title", "电机转机臂不伸缩", MERGE_GID),
        ("sec13-s1", "机臂伸太多缩不回去", MERGE_GID),
        ("sec13-s2", "电机转但机臂不动", MERGE_GID),
    ]
    print("\n=== §十三 probe ===")
    for tag, q, exp in probes:
        top = (_ask(q, use_llm=False).get("hits") or [None])[0] or {}
        gid = top.get("group_id")
        links = len(top.get("links") or [])
        imgs = len(top.get("images") or [])
        zh = top.get("content_zh") or ""
        ok = gid == exp and links >= 2 and "伸太过" in zh and "机臂不伸缩" in zh
        print(
            f"{tag} | {q} | top1={gid}({top.get('score'):.3f}) "
            f"links={links} imgs={imgs} zh_len={len(zh)} | {'PASS' if ok else 'FAIL'}"
        )


def pipeline() -> None:
    backup()
    merge_qa_groups()
    run([sys.executable, "chunk_builder.py", str(RUN / "qa_groups.json"), str(RUN / "chunks_out")])
    merge_chunks_captioned(RUN / "chunks_captioned.json")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(RUN / "chunks_captioned.json"),
            str(CHROMA),
            "--model",
            str(MODEL),
        ]
    )
    eval_out = ROOT / "_scratch/eval/a3s_sec13_merge_eval.json"
    run(
        [
            sys.executable,
            "eval_run.py",
            str(CHROMA),
            "--eval",
            "eval_queries.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(eval_out),
        ]
    )
    probe()


if __name__ == "__main__":
    pipeline()

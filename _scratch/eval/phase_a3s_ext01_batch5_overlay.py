#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-A3S-EXT-01 batch 5: DT→F prose (§十四机臂异响) → qa_039."""

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
from link_utils import infer_link_type, normalize_link
from qa_doc_extractor import classify_language, get_heading_level, iter_block_items

RUN = ROOT / "_scratch/run-006"
CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
STAMP = "20260705-bl-a3s-ext01-b5"
DOCX = ROOT / "samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"

BATCH5 = [
    (
        "十四、机臂声音异常",
        "qa_039",
        "机臂声音异常 Abnormal Noise From Arm",
    ),
]

NEW_GROUP_IDS = frozenset(gid for _, gid, _ in BATCH5)
DT_WARNINGS = [
    {
        "code": "dt_prose_only",
        "message": "观察后跳转(DT)·入库为 F prose；禁止 attach 线性 troubleshooting_ladder",
    }
]


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_orphan_section(doc: Document, section_key: str) -> tuple[str, list[dict]]:
    full_title: str | None = None
    in_section = False
    current_group: str | None = None
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
            current_group = None
            continue
        if not in_section:
            continue
        if level in (2, 3):
            current_group = text
            continue
        if current_group is None:
            paras.append({"text": text, "lang": classify_language(text)})

    if not full_title or not paras:
        raise SystemExit(f"orphan section not found or empty: {section_key} ({len(paras)} paras)")
    return full_title, paras


def _new_group(group_id: str, section: str, question: str) -> dict:
    return {
        "group_id": group_id,
        "section": section,
        "question": question,
        "heading_level": 2,
        "answer_zh": "",
        "answer_en": "",
        "images": [],
        "links": [],
        "negotiation_offers": [],
        "structure_warnings": list(DT_WARNINGS),
    }


def _append_para(g: dict, text: str, lang: str, zh_lines: list[str], en_lines: list[str]) -> None:
    if lang == "zh":
        zh_lines.append(text)
    elif lang == "en":
        en_lines.append(text)
    for url in re.findall(r"https?://[^\s<>\"']+", text):
        url = url.rstrip(".,);]")
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


def build_group(full_title: str, group_id: str, question: str, paras: list[dict]) -> dict:
    g = _new_group(group_id, full_title, question)
    zh_lines: list[str] = []
    en_lines: list[str] = []
    for p in paras:
        _append_para(g, p["text"], p["lang"], zh_lines, en_lines)
    g["answer_zh"] = "\n".join(zh_lines)
    g["answer_en"] = "\n".join(en_lines)
    return g


def build_batch5_groups(doc: Document) -> list[dict]:
    groups = []
    for key, gid, question in BATCH5:
        title, paras = collect_orphan_section(doc, key)
        g = build_group(title, gid, question, paras)
        groups.append(g)
        print(f"  {gid}: {key} · {len(paras)} paras · zh={len(g['answer_zh'])} en={len(g['answer_en'])}")
    return groups


def merge_groups(prod: list[dict], new_groups: list[dict]) -> list[dict]:
    out = [g for g in deepcopy(prod) if g["group_id"] not in NEW_GROUP_IDS]
    out.extend(new_groups)
    return out


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


def merge_qa_groups() -> list[dict]:
    doc = Document(str(DOCX))
    new_groups = build_batch5_groups(doc)
    merged = merge_groups(load_groups(RUN / "qa_groups.json"), new_groups)
    save_groups(RUN / "qa_groups.json", merged)
    print(f"merged +{len(new_groups)} groups -> {len(merged)} total")
    return new_groups


def merge_chunks_captioned() -> None:
    old_cap = json.loads((RUN / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((RUN / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = [
        old_by_id[c["chunk_id"]] if c["chunk_id"] in old_by_id and c["group_id"] not in NEW_GROUP_IDS else c
        for c in new_chunks
    ]
    (RUN / "chunks_captioned.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"chunks_captioned: {len(out)} chunks")


def pipeline() -> None:
    backup()
    merge_qa_groups()
    run([sys.executable, "chunk_builder.py", str(RUN / "qa_groups.json"), str(RUN / "chunks_out")])
    merge_chunks_captioned()
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
    run(
        [
            sys.executable,
            "eval_run.py",
            str(CHROMA),
            "--eval",
            "eval_queries.json",
            "--model",
            str(MODEL),
        ]
    )


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action == "backup":
        backup()
    elif action == "merge-groups":
        merge_qa_groups()
    elif action == "all":
        pipeline()
    else:
        raise SystemExit(f"unknown: {action}")

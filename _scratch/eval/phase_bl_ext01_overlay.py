#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-EXT-01 overlay: §十四引言→qa_022 · §十九 3组 · qa_024 UK diode."""

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

PROD = ROOT / "_scratch/run-ad5s"
STAMP = "20260705-bl-ext01"
DOCX = ROOT / "samples/troubleshooting/AD5S-AD8S常见问题排查.docx"
SEC14 = "十四、电机电流小导致走停"
SEC19 = "十九、保养与润滑"
UK_DIODE = "https://www.amazon.co.uk/dp/B079KCC8P9"
TOUCHED_GROUPS = frozenset({"qa_022", "qa_024", "qa_028", "qa_029", "qa_030"})


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def iter_paragraphs(doc: Document):
    current_section = None
    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        if not text:
            continue
        level = get_heading_level(block)
        if level == 1:
            current_section = text
            yield {"kind": "h1", "section": current_section, "text": text}
        elif level in (2, 3):
            yield {"kind": "h2", "section": current_section, "text": text, "level": level}
        else:
            yield {
                "kind": "para",
                "section": current_section,
                "text": text,
                "lang": classify_language(text),
            }


def collect_sec14_intro(doc: Document) -> str:
    in14 = False
    lines: list[str] = []
    for item in iter_paragraphs(doc):
        if item["kind"] == "h1":
            in14 = SEC14 in item["text"]
            continue
        if not in14:
            continue
        if item["kind"] == "h2":
            break
        if item["kind"] == "para" and item["lang"] == "zh":
            lines.append(item["text"])
    if not lines:
        raise SystemExit("§十四 intro zh paragraphs not found")
    return "\n".join(lines)


def _new_group(group_id: str, section: str, question: str) -> dict:
    return {
        "group_id": group_id,
        "section": section,
        "question": question,
        "heading_level": 2,
        "answer_zh": [],
        "answer_en": [],
        "images": [],
        "links": [],
        "negotiation_offers": [],
        "structure_warnings": [],
    }


def _append_para(g: dict, text: str, lang: str) -> None:
    if lang == "zh":
        g["answer_zh"].append(text)
    elif lang == "en":
        g["answer_en"].append(text)
    for url in re.findall(r"https?://[^\s<>\"']+", text):
        url = url.rstrip(".,);]")
        label = (
            "观看演示视频"
            if infer_link_type(url) == "video"
            else "参考支持页"
            if infer_link_type(url) == "support_page"
            else url
        )
        if not re.match(r"^https?://", text.strip()):
            label = text[:100].rstrip(":").strip() or label
        g["links"].append(
            normalize_link(
                {"url": url, "label": label, "lang": lang, "link_type": infer_link_type(url)}
            )
        )


def build_sec19_groups(doc: Document) -> list[dict]:
    in19 = False
    paras: list[dict] = []
    section_title: str | None = None
    for item in iter_paragraphs(doc):
        if item["kind"] == "h1":
            if in19 and section_title:
                break
            in19 = SEC19 in item["text"]
            if in19:
                section_title = item["text"]
            continue
        if not in19:
            continue
        if item["kind"] == "para":
            paras.append({"text": item["text"], "lang": item["lang"]})

    if not paras or not section_title:
        raise SystemExit("§十九 paragraphs not found")

    def find_idx(pred, start=0):
        for i in range(start, len(paras)):
            if pred(paras[i]["text"]):
                return i
        return len(paras)

    i_deep = find_idx(
        lambda t: t.startswith("如果运行不顺畅") or t.startswith("2. Deep Lubrication"),
        1,
    )
    i_guide = find_idx(
        lambda t: t.startswith("3. Guide") or "Essential Guide to Regular Maintenance" in t,
        i_deep,
    )
    # docx 在深度润滑段后重复粘贴 EN「1. Routine Maintenance」摘要块，勿收入 qa_029
    i_dup = find_idx(lambda t: t.startswith("1. Routine Maintenance"), i_deep + 2)
    i_deep_end = i_dup if i_dup < i_guide else i_guide

    splits = [
        (0, i_deep, "日常保养润滑 Routine Maintenance"),
        (i_deep, i_deep_end, "深度润滑（拆机臂）Deep Lubrication"),
        (i_guide, len(paras), "维护指南链接 Maintenance Guides"),
    ]

    groups = []
    for idx, (a, b, question) in enumerate(splits):
        g = _new_group(f"qa_{28 + idx:03d}", section_title, question)
        for p in paras[a:b]:
            _append_para(g, p["text"], p["lang"])
        g["answer_zh"] = "\n".join(g["answer_zh"])
        g["answer_en"] = "\n".join(g["answer_en"])
        groups.append(g)
    return groups


def patch_qa022(groups: list[dict], intro_zh: str) -> None:
    next(g for g in groups if g["group_id"] == "qa_022")["answer_zh"] = intro_zh


def patch_qa024_uk_diode(groups: list[dict]) -> None:
    g = next(x for x in groups if x["group_id"] == "qa_024")
    for step in g.get("troubleshooting_ladder") or []:
        for br in step.get("branches") or []:
            if br.get("applies_when", {}).get("region") != "UK":
                continue
            links = br.setdefault("links", [])
            if any(UK_DIODE in (x.get("url") or "") for x in links):
                return
            links.append(
                {
                    "url": UK_DIODE,
                    "label": "兼容二极管（第三方）",
                    "lang": "en",
                    "link_type": "purchase_link",
                }
            )
            print(f"qa_024 UK branch: {len(links)} links")
            return
    raise SystemExit("qa_024 UK branch not found")


def merge_groups(prod: list[dict], sec19: list[dict], intro_zh: str) -> list[dict]:
    out = [g for g in deepcopy(prod) if g["group_id"] not in {"qa_028", "qa_029", "qa_030"}]
    patch_qa022(out, intro_zh)
    patch_qa024_uk_diode(out)
    insert_at = next(i for i, g in enumerate(out) if str(g.get("section", "")).startswith("二十"))
    for j, g in enumerate(sec19):
        out.insert(insert_at + j, g)
    return out


def backup() -> None:
    for name in ("chroma_captioned",):
        src = PROD / name
        dst = PROD / f"{name}.bak-{STAMP}"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"backup {src} -> {dst}")
    for name in ("qa_groups.json", "chunks_captioned.json"):
        shutil.copy2(PROD / name, PROD / f"{name}.bak-{STAMP}")
        print(f"backup {PROD / name}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def merge_qa_groups() -> None:
    doc = Document(str(DOCX))
    intro = collect_sec14_intro(doc)
    sec19 = build_sec19_groups(doc)
    merged = merge_groups(load_groups(PROD / "qa_groups.json"), sec19, intro)
    save_groups(PROD / "qa_groups.json", merged)
    print(f"qa_022 intro {len(intro)} chars · sec19 +{len(sec19)} groups")


def merge_chunks_captioned() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = [
        old_by_id[c["chunk_id"]] if c["chunk_id"] in old_by_id and c["group_id"] not in TOUCHED_GROUPS else c
        for c in new_chunks
    ]
    (PROD / "chunks_captioned.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"chunks_captioned: {len(out)} chunks")


def pipeline() -> None:
    backup()
    merge_qa_groups()
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")])
    merge_chunks_captioned()
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(PROD / "chroma_captioned"),
            "--model",
            str(ROOT / "_scratch/modelscope/BAAI/bge-m3"),
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
            str(ROOT / "_scratch/modelscope/BAAI/bge-m3"),
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

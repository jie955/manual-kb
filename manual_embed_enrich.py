#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manual_embed_enrich.py

增强 manuals chunk 的 embedding_text（不重跑 VLM）：
  - 文档/章节/STEP 前缀
  - 端子代号别名（PHOTO/BAT/…）
  - Push vs Pull 中英关键词
  - 安全警示 vs 接线教程 disambiguation

用法:
  python manual_embed_enrich.py chunks.json chunks_enriched.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DOC_PREFIX_DEFAULT = "Document:A3S A5S A8S Installation Manual"


def document_title_from_manifest(manifest: dict) -> str:
    if manifest.get("document_title"):
        return str(manifest["document_title"])
    models = manifest.get("models") or []
    if models:
        return f"Document:{' '.join(str(m) for m in models)} Installation Manual"
    return DOC_PREFIX_DEFAULT

TERMINAL_ALIASES = (
    "端子功能表 Terminal Function Control Board 接线端子对照表 "
    "PHOTO Photo Eye Photocell Infrared Sensor 光电传感器 常闭 NC "
    "BAT +BAT- Battery Backup Battery 电池输入 系统供电 电源输入 "
    "GND COM OPSW EDGE O/S/C ADAPTER LAMP MOTOR DLMT ULMT +24 +LOCK-"
)

PULL_KEYWORDS = "Pull-to-Open 拉式开门 拉开门 内开 inward opening 非推开门"
PUSH_KEYWORDS = "Push-to-Open 推式开门 推开门 外开 outward opening 非拉开门"

SAFETY_KEYWORDS = "安全警示 Safety Warning 注意事项 非接线教程 非端子功能表"
POWER_WIRING_MAIN_PAGE_KEYWORDS = (
    "Connection of Power Supply 电源接线主章节 印刷页20 "
    "Power Mode 1 2 3 4 TS24-U DPS180-U adapter batteries AC electricity "
    "主电源连接方式 非UPS01 非太阳能 Power Mode 5"
)

UPS01_SOLAR_POWER_KEYWORDS = (
    "Power Mode 5 UPS01 太阳能供电 solar power supply "
    "非主电源接线页20 not main connection page printed 20"
)

HOMELINK_ACCESSORY_KEYWORDS = (
    "HLR01 HomeLink 配件连接 Connection of Accessories "
    "非端子功能表 非BAT系统供电端子说明 not terminal function table"
)

BAT_TERMINAL_KEYWORDS = (
    "BAT端子 ⑪⑫ +BAT- 系统供电 给整个系统供电 battery power input "
    "terminal 11 12 system power supply definition"
)

BEFORE_BEGIN_KEYWORDS = (
    "Before You Begin 安装前准备 工具清单 非端子接线 非控制板端子表"
)


def _str_field(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _text(*parts: object) -> str:
    return " ".join(str(p).strip() for p in parts if p is not None and str(p).strip())


def _chapter_from_chunk(chunk: dict) -> str:
    sec = chunk.get("section_obj") or chunk.get("section") or {}
    if isinstance(sec, str):
        return sec
    return _text(
        sec.get("chapter_title"),
        sec.get("step_number"),
        sec.get("step_title"),
    )


def enrich_embedding_text(chunk: dict, *, doc_title: str = DOC_PREFIX_DEFAULT) -> str | None:
    """返回新 embedding_text；parent 块返回 None（保持 null）。"""
    if not chunk.get("is_retrievable", True):
        return None

    cid = chunk.get("chunk_id", "")
    base = (chunk.get("embedding_text") or "").strip()
    section = _chapter_from_chunk(chunk)
    question = (chunk.get("question") or "").strip()
    content_zh = (chunk.get("content_zh") or "")[:400]
    content_en = (chunk.get("content_en") or "")[:400]

    sec_obj = chunk.get("section_obj") or {}
    if not isinstance(sec_obj, dict):
        sec_obj = {}

    page_key = _str_field(chunk.get("page_key"))
    step_title = _str_field(sec_obj.get("step_title")) or question
    chapter_label = section

    if page_key == "printed:23" or cid.startswith("a3s-manual-p23"):
        chapter_label = f"Power Mode 5 UPS01 Solar · {step_title}"
    elif page_key == "printed:20" or cid.startswith("a3s-manual-p20"):
        chapter_label = f"Connection of Power Supply Main page 20 · {step_title}"

    parts = [
        doc_title,
        f"Chapter:{chapter_label}" if chapter_label else "",
        f"Title:{question}" if question else "",
    ]

    if "p18-terminal" in cid or "Terminal Function" in section:
        parts.extend([TERMINAL_ALIASES, BAT_TERMINAL_KEYWORDS, content_zh[:200], content_en[:150]])
    elif "p35" in cid and (
        "HLR01" in section or "Homelink" in section or "HomeLink" in base
    ):
        parts.extend([HOMELINK_ACCESSORY_KEYWORDS, content_zh[:200], content_en[:150]])
    elif page_key == "printed:23" or cid.startswith("a3s-manual-p23"):
        parts.extend([UPS01_SOLAR_POWER_KEYWORDS, content_zh[:200], content_en[:150]])
    elif page_key == "printed:20" or cid.startswith("a3s-manual-p20"):
        parts.extend([POWER_WIRING_MAIN_PAGE_KEYWORDS, content_zh[:200], content_en[:150]])
    elif "p7-sec" in cid or "Before You Begin" in section:
        parts.extend([BEFORE_BEGIN_KEYWORDS, base, content_zh[:200]])
    elif "p2-warning" in cid or (
        "Important Safety Information" in section and "warning" in cid.lower()
    ):
        parts.extend([SAFETY_KEYWORDS, base, content_zh[:150]])
    elif "Pull-to-Open" in section or "Pull-to-Open" in base:
        parts.extend([PULL_KEYWORDS, base, content_zh[:200]])
    elif "Push-to-Open" in section or "Push-to-Open" in base:
        parts.extend([PUSH_KEYWORDS, base, content_en[:150], content_zh[:150]])
    else:
        parts.extend([base, content_zh[:150], content_en[:150]])

    text = _text(*parts)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else base or question


def enrich_chunks(chunks: list[dict], *, doc_title: str = DOC_PREFIX_DEFAULT) -> tuple[list[dict], int]:
    changed = 0
    out: list[dict] = []
    for chunk in chunks:
        c = dict(chunk)
        if not c.get("is_retrievable", True):
            out.append(c)
            continue
        new_emb = enrich_embedding_text(c, doc_title=doc_title)
        if new_emb and new_emb != (c.get("embedding_text") or ""):
            c["embedding_text"] = new_emb
            c["embedding_enriched"] = True
            changed += 1
        out.append(c)
    return out, changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich manual chunk embedding_text")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--manifest", type=Path, default=None, help="page_manifest.json（读取 document_title）")
    args = parser.parse_args()

    doc_title = DOC_PREFIX_DEFAULT
    if args.manifest and args.manifest.is_file():
        doc_title = document_title_from_manifest(
            json.loads(args.manifest.read_text(encoding="utf-8"))
        )

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    chunks = data if isinstance(data, list) else data.get("chunks", [])
    enriched, n_changed = enrich_chunks(chunks, doc_title=doc_title)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    retrievable = sum(1 for c in enriched if c.get("is_retrievable", True))
    print(f"enriched {n_changed}/{retrievable} retrievable chunks -> {args.output_json}", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-EXT-01b classification摸底: read-only scan of orphan H1 sections."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from docx import Document
from qa_doc_extractor import classify_language, get_heading_level, iter_block_items

DOCX = ROOT / "samples/troubleshooting/AD5S-AD8S常见问题排查.docx"
GAP_JSON = Path(__file__).with_name("bl_ext01_gap_scan.json")
OUT_JSON = Path(__file__).with_name("bl_ext01b_classification.json")

# A类 10 节 + B类 §十二 partial（与 gap inventory §1.3 一致）
SECTION_KEYS = [
    "一个机臂完全不工作",
    "六、随意开关门",
    "七、缓停止有问题",
    "八、自动关门不生效",
    "九、开关门过程中走停或反弹",
    "十三、门机运行慢",
    "十五、电机转机臂不伸缩",
    "十六、机臂声音异常",
    "十七、离合打不开",
    "十八、风会把门吹开",
    "十二、不限位",
]

AMAZON_RE = re.compile(r"amazon\.(com|co\.uk)", re.I)
REGION_RE = re.compile(r"\b(US|UK|United States|United Kingdom|co\.uk)\b", re.I)
URL_RE = re.compile(r"https?://[^\s\"<>)\]]+")
ARROW_RE = re.compile(r"→")
IF_THEN_RE = re.compile(r"(无异响|有异响|If (?:so|not|the)|If so|proceed to step|做步骤\d|continue to step)", re.I)
NUMBERED_STEPS = re.compile(r"^\s*\d+\s+[\.\、]", re.M)
DIP_RE = re.compile(r"DIP\s*switch|dip\s*#", re.I)
INSTALL_MODE_RE = re.compile(r"pull-to-open|push-to-open|拉开门|推开门", re.I)


def extract_section_paragraphs(doc: Document) -> dict[str, list[str]]:
    """Only H1 orphan paragraphs (no H2/H3 parent) — same rule as bl_ext01_gap_scan."""
    sections: dict[str, list[str]] = {k: [] for k in SECTION_KEYS}
    current_h1: str | None = None
    current_key: str | None = None
    current_group: str | None = None
    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        if not text:
            continue
        level = get_heading_level(block)
        if level == 1:
            current_h1 = text
            current_key = next((k for k in SECTION_KEYS if k in text), None)
            current_group = None
            continue
        if level in (2, 3):
            current_group = text
            continue
        if current_group is None and current_key:
            sections[current_key].append(text)
    return sections


def count_signals(paras: list[str]) -> dict:
    full = "\n".join(paras)
    return {
        "orphan_count": len(paras),
        "lang_zh": sum(1 for p in paras if classify_language(p) == "zh"),
        "lang_en": sum(1 for p in paras if classify_language(p) == "en"),
        "url_count": len(URL_RE.findall(full)),
        "amazon_hits": len(AMAZON_RE.findall(full)),
        "region_hits": len(REGION_RE.findall(full)),
        "arrow_hits": len(ARROW_RE.findall(full)),
        "if_then_hits": len(IF_THEN_RE.findall(full)),
        "numbered_step_lines": len(NUMBERED_STEPS.findall(full)),
        "dip_hits": len(DIP_RE.findall(full)),
        "install_mode_hits": len(INSTALL_MODE_RE.findall(full)),
    }


def classify_section(key: str, sig: dict, is_partial: bool) -> dict:
    """Return F/L/C/P + Z tags with one-line evidence."""
    if is_partial:
        proc = "P"
        proc_evidence = (
            "prod 已有 qa_011/qa_012 等 2 组；11 段 orphan 为「开门不限位/拉开门安装」等 H1 子场景，"
            "无整节丢失；风险=命中已有组但答案不全"
        )
    elif sig["amazon_hits"] or (sig["region_hits"] and sig["url_count"] >= 2):
        proc = "C"
        proc_evidence = (
            f"amazon={sig['amazon_hits']} region={sig['region_hits']} url={sig['url_count']}；"
            "含地区/采购链或 §十四 级条件分支"
        )
    elif sig["arrow_hits"] >= 4 or (sig["if_then_hits"] >= 5 and sig["numbered_step_lines"] >= 3):
        proc = "L"
        proc_evidence = (
            f"arrow={sig['arrow_hits']} if_then={sig['if_then_hits']} steps={sig['numbered_step_lines']}；"
            "多步决策树（无异响→/If so→），无 Amazon US/UK 分支"
        )
    elif sig["if_then_hits"] >= 2 and sig["numbered_step_lines"] >= 2:
        proc = "L"
        proc_evidence = (
            f"if_then={sig['if_then_hits']} steps={sig['numbered_step_lines']}；"
            "有序排查含条件分叉，但未达 qa_024 级 applies_when"
        )
    else:
        proc = "F"
        proc_evidence = (
            f"steps={sig['numbered_step_lines']} arrow={sig['arrow_hits']}；"
            "顺序编号步骤为主，无显式决策树箭头/无采购地区链"
        )

    z_tags: list[str] = []
    z_evidence: list[str] = []
    en_ratio = sig["lang_en"] / max(sig["orphan_count"], 1)
    if en_ratio >= 0.55:
        z_tags.append("B")
        z_evidence.append(f"EN 段占比 {sig['lang_en']}/{sig['orphan_count']}，步内规格/细节多在 EN")
    if sig["lang_zh"] >= 2 and sig["lang_en"] >= 2:
        z_tags.append("B")
        if not any("步内" in e for e in z_evidence):
            z_evidence.append("ZH+EN 双语文本并存，骨架对齐但 EN 常更长")
    if sig["url_count"] and sig["lang_en"] >= sig["lang_zh"]:
        z_tags.append("B")
        z_evidence.append(f"外链 {sig['url_count']} 条多在 EN 段（V1-04 简单档 + V1-05B）")
    if key.startswith("十六") and sig["arrow_hits"] >= 4:
        z_tags.append("B")
        z_evidence.append("决策树 ZH 为主，YouTube 链在 EN orphan")
    if not z_tags:
        z_tags = ["—"]
        z_evidence = ["无明显 ZH/EN 互斥分支；双语文本量接近或 ZH 为主"]

    # Manual overrides from human review (evidence-backed)
    overrides = {
        "十六、机臂声音异常 Abnormal Noise From Arm": {
            "process_tag": "L",
            "process_evidence": (
                "preview 含「无异响→做步骤2；有异响→步骤5」等 ≥6 处 → 分支；"
                "grep 无 amazon/US/UK；YouTube×1 为简单档链"
            ),
            "z_tags": ["B"],
            "z_evidence": ["35 段 zh:15 en:20；决策树 ZH 箭头，YouTube 在 EN"],
        },
        "十七、离合打不开 Clutch Won't Release": {
            "process_tag": "L",
            "process_evidence": (
                "3 条 ZH 编号排查 + EN 镜像；含「伸太过/离合分离/丝母卡住」条件分叉；"
                "YouTube×3 无条件链，非 US/UK 采购"
            ),
            "z_tags": ["B"],
            "z_evidence": ["zh:3 en:19；操作细节与视频链主要在 EN"],
        },
        "十五、电机转机臂不伸缩 Motor Runs But Gate Doesn't Move": {
            "process_tag": "L",
            "process_evidence": (
                "两主场景「伸太过缩不回」vs「电机转臂不伸缩」；topens 博客×2 为简单档；"
                "无 amazon/方向 applies_when"
            ),
            "z_tags": ["B"],
            "z_evidence": ["zh:5 en:11；场景分支 ZH 有，EN 步骤更细"],
        },
        "十二、不限位 Gate Does Not Stop at Limit Switch": {
            "process_tag": "P",
            "process_evidence": (
                "orphan 首段「开门不限位」「拉开门安装」；prod 已有 2 组；"
                "11 段为 H1 子场景非整节盲区"
            ),
            "z_tags": ["B"],
            "z_evidence": ["install_mode 词命中；拉/推开门子场景与已有组可能错配"],
        },
        "八、自动关门不生效 Auto Close Function Doesn't Work": {
            "process_tag": "F",
            "process_evidence": (
                "4 步顺序排除（配件→断电循环→DIP）；含 1 条「特殊案例」注释；"
                "无 → 决策树、无 amazon"
            ),
            "z_tags": ["B"],
            "z_evidence": ["zh:3 en:5；DIP #1 说明在 EN"],
        },
        "六、随意开关门 Random Opening/Closing": {
            "process_tag": "F",
            "process_evidence": (
                "4 步顺序：DIP→断配件逐个接回→清遥控→换板；"
                "if 仅用于配件隔离，非 ladder schema"
            ),
            "z_tags": ["B"],
            "z_evidence": ["zh:4 en:6；DIP #1 细节在 EN"],
        },
    }

    section_title = key  # will be filled with full H1 title below
    result = {
        "process_tag": proc,
        "process_evidence": proc_evidence,
        "z_tags": list(dict.fromkeys(z_tags)),
        "z_evidence": z_evidence,
    }
    return result


def main() -> None:
    gap = json.loads(GAP_JSON.read_text(encoding="utf-8"))
    orphan_meta = {item["section"]: item for item in gap["orphan_sections_bl_ext01b"]}

    doc = Document(str(DOCX))
    paras_by_key = extract_section_paragraphs(doc)

    # Map short key → full H1 title from gap scan
    key_to_full: dict[str, str] = {}
    for h1 in gap["h1_sections_docx"]:
        for k in SECTION_KEYS:
            if k in h1:
                key_to_full[k] = h1

    rows = []
    for k in SECTION_KEYS:
        full_title = key_to_full.get(k, k)
        paras = paras_by_key.get(k, [])
        is_partial = k.startswith("十二")
        sig = count_signals(paras)
        meta = orphan_meta.get(full_title, {})
        cls = classify_section(k, sig, is_partial)

        # Apply manual overrides keyed by full title
        overrides = {
            "十六、机臂声音异常 Abnormal Noise From Arm": cls,
        }
        manual = {
            "十六、机臂声音异常 Abnormal Noise From Arm": {
                "process_tag": "L",
                "process_evidence": "preview 含「无异响→做步骤2；有异响→步骤5」等 ≥6 处 → 分支；grep 无 amazon/US/UK；YouTube×1",
                "z_tags": ["B"],
                "z_evidence": ["35 段 zh:15 en:20；决策树 ZH 箭头，YouTube 在 EN"],
            },
            "十七、离合打不开 Clutch Won't Release": {
                "process_tag": "L",
                "process_evidence": "3 条 ZH 编号排查 + EN 条件分叉（伸太过/离合分离）；YouTube×3 无条件链",
                "z_tags": ["B"],
                "z_evidence": ["zh:3 en:19；操作细节与视频链主要在 EN"],
            },
            "十五、电机转机臂不伸缩 Motor Runs But Gate Doesn't Move": {
                "process_tag": "L",
                "process_evidence": "两主场景「伸太过」vs「电机转臂不伸缩」；topens×2 简单档；无 amazon",
                "z_tags": ["B"],
                "z_evidence": ["zh:5 en:11；EN 步骤更细"],
            },
            "十二、不限位 Gate Does Not Stop at Limit Switch": {
                "process_tag": "P",
                "process_evidence": "orphan「开门不限位/拉开门安装」；prod 2 组；11 段 partial 非整节",
                "z_tags": ["B"],
                "z_evidence": ["拉/推开门子场景与已有组可能错配"],
            },
            "八、自动关门不生效 Auto Close Function Doesn't Work": {
                "process_tag": "F",
                "process_evidence": "4 步顺序排除 + 1 特殊案例注释；无 → 树、无 amazon",
                "z_tags": ["B"],
                "z_evidence": ["DIP #1 说明在 EN"],
            },
            "六、随意开关门 Random Opening/Closing": {
                "process_tag": "F",
                "process_evidence": "4 步顺序：DIP→断配件→清遥控→换板；配件 if 非 ladder schema",
                "z_tags": ["B"],
                "z_evidence": ["DIP #1 在 EN"],
            },
            "九、开关门过程中走停或反弹 Gate Stops or Bounces During Operation": {
                "process_tag": "L",
                "process_evidence": "6 步排查含红外/遇阻/单臂隔离/离合手推；if 分叉多但无 US/UK 链",
                "z_tags": ["B"],
                "z_evidence": ["zh:9 en:12；FORCE 电位器细节在 EN"],
            },
            "十三、门机运行慢 Gate Operates Slowly": {
                "process_tag": "F",
                "process_evidence": "5 步顺序：测压降→调 FORCE→离合手推→脱门测速→视频；无决策箭头",
                "z_tags": ["B"],
                "z_evidence": ["22V/11#12# 等规格在 EN"],
            },
            "一个机臂完全不工作 One Arm Doesn’t Work": {
                "process_tag": "F",
                "process_evidence": "3 步：交换端口→直连电池测电机→短接限位；线性诊断",
                "z_tags": ["B"],
                "z_evidence": ["zh:3 en:7；May I ask 开场与 24VDC 测法在 EN"],
            },
            "七、缓停止有问题（缓停止错乱或者没有缓停止）Soft Stop Issues": {
                "process_tag": "F",
                "process_evidence": "4 步顺序：断电完整循环→查限位→脱门测缓停→换板",
                "z_tags": ["B"],
                "z_evidence": ["zh:5 en:4；步骤量接近"],
            },
            "十八、风会把门吹开（或者外力能把门推开一点） There is Little Play When the Gate is Closed": {
                "process_tag": "F",
                "process_evidence": "3 步：托架紧固→观察风吹拉杆→脱门离合手推；无分支链",
                "z_tags": ["—"],
                "z_evidence": ["zh:3 en:3 对称短节"],
            },
        }
        if full_title in manual:
            cls = manual[full_title]

        rows.append(
            {
                "section": full_title,
                "section_key": k,
                "category": "B_partial" if is_partial else "A_whole_h1",
                "orphan_count": sig["orphan_count"],
                "signals": sig,
                "process_tag": cls["process_tag"],
                "process_evidence": cls["process_evidence"],
                "z_tags": cls["z_tags"],
                "z_evidence": cls["z_evidence"],
                "value_tier": meta.get("value_tier", "high_troubleshooting"),
                "suggested_pipeline": _pipeline(cls["process_tag"]),
                "suggested_h2_split": _h2_hint(full_title, cls["process_tag"], sig),
            }
        )

    out = {
        "version": 1,
        "date": "2026-07-05",
        "status": "classification摸底完成 · 未写 extract",
        "tag_legend": {
            "F": "flat · 顺序步骤，qa_028–030 式",
            "L": "ladder · 决策树/多场景，attach_troubleshooting_ladder，无 branches[]",
            "C": "complex · applies_when + branches[]，qa_024 管线",
            "P": "partial · §十二类，已有组 + orphan 子场景",
            "Z": "正交验收列：B=V1-05 步内规格/EN-heavy；—=无明显异构",
        },
        "summary": _summary(rows),
        "sections": rows,
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON} ({len(rows)} sections)")


def _pipeline(tag: str) -> str:
    return {
        "F": "补 H2 → extract → links[] 简单档 → embed → 浏览器 1 query",
        "L": "补 H2（按场景拆）→ extract → 可选 attach_troubleshooting_ladder → links → pilot overlay",
        "C": "pilot → branches[] + applies_when → 四项验收 → prod overlay",
        "P": "对照 prod qa_011/012 → 补 H2 或 orphan 收集 → 错组 eval",
    }[tag]


def _h2_hint(title: str, tag: str, sig: dict) -> str:
    if tag == "P":
        return "按 orphan 子场景拆 2–3 H2（开门不限位 / 拉开门 / 推开门），勿并入已有 qa 组"
    if tag == "L" and "十五" in title:
        return "建议 2 H2：伸太过 vs 电机转不伸缩"
    if tag == "L" and "十六" in title:
        return "1 H2 或按异响来源拆 2 H2（电机/离合 vs 机臂前端）"
    if tag == "F" and sig["orphan_count"] <= 10:
        return "1 H2 收整节即可"
    return "1 H2 起步；过长再拆"


def _summary(rows: list[dict]) -> dict:
    by_tag: dict[str, int] = {}
    orphan_total = 0
    for r in rows:
        by_tag[r["process_tag"]] = by_tag.get(r["process_tag"], 0) + 1
        orphan_total += r["orphan_count"]
    return {
        "section_count": len(rows),
        "orphan_paragraph_total": orphan_total,
        "by_process_tag": by_tag,
        "complex_count": by_tag.get("C", 0),
        "note": "本批 11 节无 C 类；最高复杂度为 L（十六/十七/九/十五）",
    }


if __name__ == "__main__":
    main()

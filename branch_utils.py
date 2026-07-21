#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""互斥分支（branches[]）检测：qa_024 走停方向 + 采购链归位。

## region 锚点说明（2026-07-03 原文核对）

qa_024 **ZH 分支标题不含**「美国/英国/US/UK」等地域词；「注意链接国家」是客服提醒
（按客户国家选链接），**不表示**「上一行=US、下一行=UK」。

当前 region 赋值规则（实现假设，非字段级显式锚点）：

1. ``install_mode`` / ``stall_symptom``：仅来自 ZH 分支标题 + 括号镜像（有文本证据）。
2. ``region``：来自 **挂到该 branch 的采购链 URL 域名**（amazon.com→US，amazon.co.uk→UK），
   **不**硬编码「第一行 ZH→US」。
3. ZH 分支标题行与 EN 二极管接线段按 **文档出现顺序** 一一对齐（第 i 行标题 ↔ 第 i 个
   ``Connect anode of the diode`` 块 ↔ 该块后在 docx 中出现的下一条采购 URL）。
4. ZH 分支标题行数须与 EN ``Connect anode of the diode`` 接线块数 **相等**；不等则失败。
5. 若结构识别失败 → ``build_qa_024_ladder`` 返回 ``(None, reason)``；候选组写入
   ``structure_warnings[]`` 并 **stderr 告警**（不静默降级为「看似成功的平铺链」）。

**人工复核**：新型号/改版若调整段落或链接顺序，须重新核对本组映射后再入库。

**install/symptom 对齐**：与 region 相同，目前无第二独立锚点；仅靠 ZH 标题行序 ↔ EN 接线块序。
顺序错配时依赖上表第 4–5 条失败可见，勿硬对齐。
"""

from __future__ import annotations

import re
import sys
from typing import Any
from urllib.parse import urlparse

from ladder_utils import split_numbered_steps

INSTALL_ZH = {"拉开门": "pull_open", "推开门": "push_open"}
SYMPTOM_ZH = {"开门不正常": "open_abnormal", "关门不正常": "close_abnormal"}

BRANCH_TITLE_RE = re.compile(
    r"(拉开门|推开门)(开门不正常|关门不正常)加二极管电阻"
)
PAREN_MIRROR_RE = re.compile(r"（(拉开门|推开门)(开门不正常|关门不正常)）")

US_RESISTOR_RE = re.compile(r"amazon\.com/dp/B08HYZV3DW", re.I)
US_DIODE_RE = re.compile(r"amazon\.com/dp/B01HMSR2T4", re.I)
UK_LINK_RE = re.compile(r"amazon\.co\.uk/dp/(B07H33917Z|B079KCC8P9)", re.I)

# AD5S qa_024 实测：docx 中采购 URL 段落顺序（与 wiring 块后链接一致）
QA_024_EXPECTED_LINK_ORDER = (
    "us_resistor",
    "us_resistor",  # 重复段落
    "us_diode",
    "uk_b07h33917z",
    "uk_b079kcc8p9",
)

DISCLAIMER_RESISTOR_EN = (
    "Regretfully, we do not have this resistor for sale in our store. "
    "Sorry for the inconvenience."
)

# qa_024 docx 顺序：接线块 0 (+Motor/US) → 026+028；块 1 (Motor-/UK) → 027+029
QA_024_BRANCH_IMAGES = (
    ("image_026.png", "image_028.png"),
    ("image_027.png", "image_029.png"),
)

_INSTALL_STALL_KEYS = frozenset({"install_mode", "stall_symptom"})


def region_from_url(url: str) -> str | None:
    host = (urlparse(url).netloc or "").lower()
    if "amazon.co.uk" in host:
        return "UK"
    if "amazon.com" in host:
        return "US"
    return None


def branch_matches(branch: dict, ctx: dict) -> bool:
    """
    分支是否匹配用户上下文。支持 ``applies_when``（AND）与 ``applies_when_any``（OR 路径）。
    缺 key = 通配（与 schema §5.4 一致）。
    """
    ctx = ctx or {}
    any_list = branch.get("applies_when_any")
    if any_list:
        base_when = branch.get("applies_when") or {}
        for key, required in base_when.items():
            if key not in ctx:
                continue
            if ctx[key] != required:
                return False
        if not _INSTALL_STALL_KEYS.intersection(ctx.keys()):
            return True
        for path in any_list:
            if all(
                path.get(key) == ctx[key]
                for key in _INSTALL_STALL_KEYS
                if key in ctx
            ):
                return True
        return False

    when = branch.get("applies_when") or {}
    for key, required in when.items():
        if key not in ctx:
            continue
        if ctx[key] != required:
            return False
    return True


def filter_branches(branches: list[dict], ctx: dict) -> list[dict]:
    """给定上下文，返回应展示的 branch 列表（按文档顺序）。"""
    return [b for b in (branches or []) if branch_matches(b, ctx)]


def collect_ladder_branch_images(ladder: list[dict], ctx: dict) -> list[str]:
    """合并 ladder 各步可见 branch 的 images[]（去重保序）。"""
    seen: set[str] = set()
    out: list[str] = []
    for step in ladder or []:
        for br in filter_branches(step.get("branches") or [], ctx):
            for img in br.get("images") or []:
                file = img.get("file") if isinstance(img, dict) else str(img)
                if file and file not in seen:
                    seen.add(file)
                    out.append(file)
    return out


def _purchase_link(url: str, label: str, *, disclaimer: str = "") -> dict:
    entry: dict[str, Any] = {
        "url": url,
        "label": label,
        "lang": "en",
        "link_type": "purchase_link",
    }
    if disclaimer:
        entry["disclaimer"] = disclaimer
    return entry


def parse_zh_stall_branch_cases(answer_zh: str) -> list[dict[str, str]]:
    """从 ZH 分支标题解析 install_mode / stall_symptom（含括号镜像）。仅 ZH，不从 EN 推断。"""
    return [c for group in parse_zh_stall_branch_line_groups(answer_zh) for c in group]


def parse_zh_stall_branch_line_groups(answer_zh: str) -> list[list[dict[str, str]]]:
    """
    按 ZH 文档顺序，每个含分支标题的行为一组（主标题 + 括号镜像 = 最多 2 个 case）。
    用于与 EN 接线块按索引对齐，而非按臆测地域绑定。
    """
    groups: list[list[dict[str, str]]] = []

    def _cases_from_line(line: str) -> list[dict[str, str]]:
        m = BRANCH_TITLE_RE.search(line)
        if not m:
            return []
        out: list[dict[str, str]] = [
            {
                "install_mode": INSTALL_ZH[m.group(1)],
                "stall_symptom": SYMPTOM_ZH[m.group(2)],
                "content_zh": line,
            }
        ]
        pm = PAREN_MIRROR_RE.search(line)
        if pm:
            out.append(
                {
                    "install_mode": INSTALL_ZH[pm.group(1)],
                    "stall_symptom": SYMPTOM_ZH[pm.group(2)],
                    "content_zh": line,
                }
            )
        return out

    for line in (answer_zh or "").split("\n"):
        line = line.strip()
        if BRANCH_TITLE_RE.search(line):
            groups.append(_cases_from_line(line))

    return groups


def _en_main_ladder_text(answer_en: str) -> str:
    text = answer_en or ""
    cut = text.find("Connect anode of the diode to ")
    if cut > 0:
        text = text[:cut]
    return text.strip()


def _en_step3_resistor_intro(answer_en: str) -> str:
    steps = split_numbered_steps(_en_main_ladder_text(answer_en))
    return steps.get(3, "")


def _en_diode_wiring_blocks(answer_en: str) -> list[str]:
    text = answer_en or ""
    parts = re.split(r"(?=Connect anode of the diode to )", text)
    blocks = [p.strip() for p in parts if p.strip().startswith("Connect anode")]
    out: list[str] = []
    for block in blocks:
        end = block.find("\nAfter adding the resistor")
        if end > 0:
            block = block[:end].strip()
        out.append(block)
    return out


def is_stall_branch_candidate(group: dict) -> bool:
    """含 ZH 走停方向分支标题即视为候选（失败须告警，不可静默忽略）。"""
    return bool(parse_zh_stall_branch_line_groups(group.get("answer_zh") or ""))


def _ordered_purchase_urls(links: list[dict]) -> list[str]:
    """docx 提取顺序下的采购 URL 列表（去重电阻首条保留顺序）。"""
    urls: list[str] = []
    seen_resistor = False
    for raw in links or []:
        url = (raw.get("url") if isinstance(raw, dict) else str(raw)).strip()
        if not url:
            continue
        if US_RESISTOR_RE.search(url):
            if not seen_resistor:
                urls.append(url)
                seen_resistor = True
            continue
        urls.append(url)
    return urls


def _diode_urls_for_wiring_blocks(links: list[dict], wiring_count: int) -> list[str] | None:
    """
    电阻后的采购链顺序应对齐 wiring 块数。
    qa_024 实测： [US 二极管, UK#1, UK#2] 对应 2 个接线块（第二块为 UK 域链接）。
    """
    ordered = _ordered_purchase_urls(links)
    if US_RESISTOR_RE.search(ordered[0] if ordered else ""):
        diode_candidates = ordered[1:]
    else:
        diode_candidates = ordered

    if len(diode_candidates) < wiring_count:
        return None

    picked: list[str] = []
    for i in range(wiring_count):
        url = diode_candidates[i]
        if region_from_url(url) is None:
            return None
        picked.append(url)
    return picked


def build_qa_024_ladder(group: dict) -> tuple[list[dict] | None, str | None]:
    """
    构建 qa_024 型 ladder。成功 (ladder, None)；失败 (None, reason)。
    非候选组返回 (None, None)。
    """
    answer_zh = group.get("answer_zh") or ""
    answer_en = group.get("answer_en") or ""
    flat_links = group.get("links") or []
    gid = group.get("group_id") or "?"

    line_groups = parse_zh_stall_branch_line_groups(answer_zh)
    if not line_groups:
        return None, None

    if len(line_groups) != 2:
        return None, (
            f"{gid}: zh_branch_lines={len(line_groups)} (expected 2 for stall-branch template)"
        )

    branch_cases = parse_zh_stall_branch_cases(answer_zh)
    if len(branch_cases) != 4:
        return None, (
            f"{gid}: zh_branch_cases={len(branch_cases)} (expected 4 incl. parenthetical mirrors)"
        )

    zh_steps = split_numbered_steps(answer_zh)
    en_steps = split_numbered_steps(_en_main_ladder_text(answer_en))
    if not all(k in zh_steps for k in (1, 2, 3)) or not all(
        k in en_steps for k in (1, 2, 3, 4)
    ):
        return None, f"{gid}: main troubleshooting step numbering incomplete (zh/en)"

    wiring_blocks = _en_diode_wiring_blocks(answer_en)
    if len(wiring_blocks) != len(line_groups):
        return None, (
            f"{gid}: zh_branch_lines={len(line_groups)} "
            f"en_wiring_blocks={len(wiring_blocks)} (count mismatch — no index alignment)"
        )

    diode_urls = _diode_urls_for_wiring_blocks(flat_links, len(wiring_blocks))
    if not diode_urls:
        return None, (
            f"{gid}: purchase link count/order does not match "
            f"wiring_blocks={len(wiring_blocks)}"
        )

    ordered = _ordered_purchase_urls(flat_links)
    us_resistor = next((u for u in ordered if US_RESISTOR_RE.search(u)), None)
    if not us_resistor or region_from_url(us_resistor) != "US":
        return None, f"{gid}: US resistor link missing or not amazon.com"

    branches: list[dict] = []
    for idx, (cases, wiring, diode_url) in enumerate(
        zip(line_groups, wiring_blocks, diode_urls)
    ):
        region = region_from_url(diode_url)
        if not region:
            return None, f"{gid}: unrecognized purchase URL region: {diode_url}"
        if len(cases) != 2:
            return None, (
                f"{gid}: zh_branch_mirror_paths={len(cases)} "
                f"(expected 2 per line for stall-branch template)"
            )
        branch_link = _purchase_link(
            diode_url,
            "兼容二极管（第三方）" if region == "US" else "兼容采购链（第三方）",
        )
        img_pair = QA_024_BRANCH_IMAGES[idx] if idx < len(QA_024_BRANCH_IMAGES) else ()
        branches.append(
            {
                "applies_when": {"region": region},
                "applies_when_any": [
                    {
                        "install_mode": case["install_mode"],
                        "stall_symptom": case["stall_symptom"],
                    }
                    for case in cases
                ],
                "content_zh": cases[0]["content_zh"],
                "content_en": wiring,
                "images": list(img_pair),
                "links": [branch_link],
            }
        )

    if len(branches) != 2:
        return None, (
            f"{gid}: branches={len(branches)} (expected 2 content branches for qa_024)"
        )

    step3_zh = zh_steps[3]
    cut_zh = step3_zh.find("注意链接国家")
    step3_zh_intro = (
        step3_zh[:cut_zh].strip()
        if cut_zh > 0
        else step3_zh.split("拉开门")[0].strip() or step3_zh
    )

    ladder: list[dict] = [
        {
            "step_index": 1,
            "content_zh": zh_steps[1],
            "content_en": en_steps[1],
            "is_last_resort": False,
            "branches": [],
            "links": [],
            "images": [],
        },
        {
            "step_index": 2,
            "content_zh": zh_steps[2],
            "content_en": en_steps[2],
            "is_last_resort": False,
            "branches": [],
            "links": [],
            "images": [],
        },
        {
            "step_index": 3,
            "content_zh": step3_zh_intro,
            "content_en": _en_step3_resistor_intro(answer_en),
            "is_last_resort": False,
            "branches": branches,
            "links": [
                {
                    **_purchase_link(
                        us_resistor,
                        "Below is the link to the resistor that will work.",
                        disclaimer=DISCLAIMER_RESISTOR_EN,
                    ),
                    "applies_when": {"region": region_from_url(us_resistor)},
                }
            ],
            "images": [],
        },
        {
            "step_index": 4,
            "content_zh": "加了电阻之后，相当于增大了负载，需要加大遇阻力。",
            "content_en": en_steps[4],
            "is_last_resort": False,
            "branches": [],
            "links": [],
            "images": [],
        },
    ]

    return ladder, None


QA_023_RESISTOR_RE = re.compile(r"amazon\.com/dp/B08HYZV3DW", re.I)


def _split_qa_023_en_blocks(answer_en: str) -> list[str]:
    return [b.strip() for b in (answer_en or "").split("\n") if b.strip()]


def _qa_023_zh_lines(answer_zh: str) -> list[str]:
    return [ln.strip() for ln in (answer_zh or "").split("\n") if ln.strip()]


def build_qa_023_ladder(group: dict) -> tuple[list[dict] | None, str | None]:
    """
    qa_023：机臂并接排查 — 步骤 1 两条 parallel_test branch；步骤 2 电阻采购链。
    仅 group_id=qa_023 时构建；否则 (None, None)。
    """
    if group.get("group_id") != "qa_023":
        return None, None

    blocks = _split_qa_023_en_blocks(group.get("answer_en") or "")
    if len(blocks) < 4:
        return None, f"qa_023 expected >=4 EN blocks, got {len(blocks)}"

    video_en = blocks[-1]
    if "shoot a video" not in video_en.lower() and "dropbox" not in video_en.lower():
        return None, "qa_023 missing video fallback EN block"

    en_arm2_arm1 = blocks[0]
    en_arm1_arm2 = blocks[1]
    resistor_parts = [
        b
        for b in blocks[2:-1]
        if not b.lower().startswith("below is the link")
    ]
    if not resistor_parts:
        return None, "qa_023 missing resistor EN block"
    resistor_en = "\n".join(resistor_parts)

    zh_lines = _qa_023_zh_lines(group.get("answer_zh") or "")
    zh_intro = zh_lines[0] if zh_lines else ""
    zh_arm2_arm1 = next(
        (ln for ln in zh_lines if "机臂2" in ln and "机臂1" in ln),
        "机臂2的红黑线并到机臂1的电机接线端口",
    )
    zh_arm1_arm2 = next(
        (
            ln
            for ln in zh_lines
            if "机臂1" in ln and "机臂2" in ln and ln != zh_arm2_arm1
        ),
        "机臂1的红黑线并到机臂2的电机接线端口",
    )
    zh_resistor = next(
        (ln for ln in zh_lines if "加电阻" in ln or "并接后有问题" in ln),
        "并接后有问题的机臂可以正常工作，说明就是电机电流小问题，加电阻",
    )
    zh_video = next((ln for ln in zh_lines if "视频" in ln), "并接后也不行发视频看看")

    purchase_url = None
    for link in group.get("links") or []:
        url = str(link.get("url") or "")
        if QA_023_RESISTOR_RE.search(url):
            purchase_url = url
            break
    if not purchase_url:
        m = QA_023_RESISTOR_RE.search(group.get("answer_en") or "")
        if m:
            purchase_url = f"https://www.{m.group(0)}"

    step2_links: list[dict] = []
    if purchase_url:
        step2_links.append(
            _purchase_link(
                purchase_url,
                "Below is the link to the resistor that will work.",
                disclaimer=DISCLAIMER_RESISTOR_EN,
            )
        )

    branches = [
        {
            "applies_when": {"parallel_test": "arm2_on_arm1"},
            "content_zh": zh_arm2_arm1,
            "content_en": en_arm2_arm1,
            "images": ["image_024.png"],
            "links": [],
        },
        {
            "applies_when": {"parallel_test": "arm1_on_arm2"},
            "content_zh": zh_arm1_arm2,
            "content_en": en_arm1_arm2,
            "images": ["image_025.png"],
            "links": [],
        },
    ]

    ladder = [
        {
            "step_index": 1,
            "content_zh": zh_intro,
            "content_en": "",
            "is_last_resort": False,
            "branches": branches,
            "links": [],
            "images": [],
        },
        {
            "step_index": 2,
            "content_zh": zh_resistor,
            "content_en": resistor_en,
            "is_last_resort": False,
            "branches": [],
            "links": step2_links,
            "images": [],
        },
        {
            "step_index": 3,
            "content_zh": zh_video,
            "content_en": video_en,
            "is_last_resort": True,
            "branches": [],
            "links": [],
            "images": [],
        },
    ]
    return ladder, None


def attach_qa_023_structure(group: dict, *, log: Any = sys.stderr) -> bool:
    """写入 qa_023 troubleshooting_ladder；采购链归位到步骤 2 links[]。"""
    if group.get("group_id") != "qa_023":
        return False
    ladder, reason = build_qa_023_ladder(group)
    if ladder:
        group["troubleshooting_ladder"] = ladder
        group["links"] = []
        return True
    if reason:
        warning = {
            "code": "parallel_branch_align_failed",
            "message": reason,
        }
        group.setdefault("structure_warnings", []).append(warning)
        print(f"[branch_utils] WARNING: {reason}", file=log)
    return False


def attach_qa_024_structure(group: dict, *, log: Any = sys.stderr) -> bool:
    """
    写入 troubleshooting_ladder 并清空根级 links。
    候选组结构识别失败时：stderr 告警 + structure_warnings[]，返回 False。
    """
    ladder, reason = build_qa_024_ladder(group)
    if ladder:
        group["troubleshooting_ladder"] = ladder
        group["links"] = []
        return True

    if reason:
        warning = {
            "code": "stall_branch_align_failed",
            "message": reason,
        }
        group.setdefault("structure_warnings", []).append(warning)
        print(f"[branch_utils] WARNING: {reason}", file=log)
    return False

#!/usr/bin/env python3
"""Lightweight scope scan: EN customer-service email template vs spec-gap / polite inline copy.

Reuses negotiation_utils for negotiation_offer detection; adds email-genre signals
from BL-V1-05 / qa_023 patterns. Output: JSON + markdown for V1.1 content_role scoping.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys_path = ROOT
import sys

sys.path.insert(0, str(ROOT))
from negotiation_utils import extract_negotiation_clauses

LIBRARIES = {
    "AD5S": ROOT / "_scratch/run-ad5s/qa_groups.json",
    "A3S": ROOT / "_scratch/run-006/qa_groups.json",
    "TC148": ROOT / "_scratch/run-tc148/qa_groups.json",
}

# Email-template genre signals (weight, tier)
EMAIL_SIGNALS: list[tuple[str, re.Pattern[str], int, str]] = [
    (
        "opener_confirm",
        re.compile(r"^Please help us confirm\b", re.I | re.M),
        5,
        "definitive",
    ),
    (
        "following_tests_diagnosis",
        re.compile(r"If so, please do the following tests for further diagnosis", re.I),
        3,
        "definitive",
    ),
    (
        "if_problem_disappears",
        re.compile(r"If (?:the )?problem disappears", re.I),
        2,
        "branch",
    ),
    (
        "go_on_steps",
        re.compile(r"please go on the following steps", re.I),
        2,
        "branch",
    ),
    (
        "below_link_howto",
        re.compile(r"Below is the link of How to", re.I),
        2,
        "branch",
    ),
    (
        "may_i_ask",
        re.compile(r"May I ask\b", re.I),
        1,
        "polite",
    ),
    (
        "if_so_following_tests",
        re.compile(r"If so, please do the following tests\b", re.I),
        2,
        "polite",
    ),
    (
        "following_tests_generic",
        re.compile(r"please do the following tests\b", re.I),
        1,
        "polite",
    ),
    (
        "email_video_closing",
        re.compile(
            r"(?:send the video to my E-mail|dropbox, icloud or google drive)",
            re.I,
        ),
        1,
        "closing",
    ),
    (
        "thanks_cooperation",
        re.compile(r"Thanks for your understanding and cooperation", re.I),
        1,
        "closing",
    ),
    (
        "please_let_me_know",
        re.compile(r"Please let me know the result one by one", re.I),
        1,
        "closing",
    ),
    (
        "nested_letter_steps",
        re.compile(r"(?:^|\n)[a-c]\.\s", re.I | re.M),
        1,
        "structure",
    ),
    (
        "numbered_steps_en",
        re.compile(r"(?:^|\n)\d+\.\s", re.M),
        1,
        "structure",
    ),
]


def zh_has_aligned_steps(zh: str) -> bool:
    """ZH uses numbered troubleshooting skeleton (1/2/3 or a/b/c)."""
    if re.search(r"(?:^|\n)\d+\s", zh, re.M):
        return True
    if re.search(r"(?:^|\n)[a-z]\s", zh, re.M):
        return True
    if re.search(r"(?:^|\n)\d+\.", zh, re.M):
        return True
    return False


def zh_has_disappear_branch(zh: str) -> bool:
    return bool(
        re.search(
            r"问题消失|如果.*消失|如果问题|配件影响|一个配件接好",
            zh,
            re.I,
        )
    )


def en_has_unnumbered_section_titles(en: str) -> bool:
    """TC148-style titled sections without leading numbers."""
    for line in en.splitlines():
        line = line.strip()
        if not line or line.startswith("http"):
            continue
        if re.match(r"^\d+\.", line):
            continue
        if re.match(r"^[a-c]\.", line, re.I):
            continue
        if len(line) > 8 and line[0].isupper() and " " in line:
            if re.search(
                r"^(?:Isolate|Check|Disconnect|Please help|If |May I|Generally)",
                line,
                re.I,
            ):
                return True
    return False


def score_email_signals(en: str) -> tuple[int, list[str], dict[str, bool]]:
    score = 0
    hits: list[str] = []
    flags: dict[str, bool] = {}
    for name, pat, weight, _tier in EMAIL_SIGNALS:
        if pat.search(en):
            score += weight
            hits.append(name)
            flags[name] = True
    return score, hits, flags


def classify_group(lib: str, g: dict) -> dict:
    gid = g["group_id"]
    zh = (g.get("answer_zh") or "").strip()
    en = (g.get("answer_en") or "").strip()
    score, hits, flags = score_email_signals(en)

    neg_clauses = extract_negotiation_clauses(en)
    neg_offers = g.get("negotiation_offers") or []
    has_negotiation = bool(neg_clauses) or bool(neg_offers)

    definitive = bool(flags.get("opener_confirm"))
    branch_bundle = sum(
        1
        for k in (
            "following_tests_diagnosis",
            "if_problem_disappears",
            "go_on_steps",
            "below_link_howto",
        )
        if flags.get(k)
    )
    genre_mismatch = (
        definitive
        or (
            branch_bundle >= 2
            and not zh_has_disappear_branch(zh)
            and (len(en) > len(zh) * 1.5 or en_has_unnumbered_section_titles(en))
        )
    )
    zh_aligned = zh_has_aligned_steps(zh)

    if definitive or (branch_bundle >= 3 and genre_mismatch):
        bucket = "A_tc148_email_template"
        verdict = "EN 完整客服邮件稿 · ZH 内部速记 · 体裁异构"
    elif has_negotiation and score <= 3 and not definitive:
        bucket = "C_negotiation_only"
        verdict = "协商话术（BL-V1-06 · negotiation_offers 字段）· 非邮件模板体裁"
    elif score >= 2 and (flags.get("may_i_ask") or flags.get("if_problem_disappears")):
        if zh_aligned and not definitive:
            bucket = "B_polite_inline_copy"
            verdict = "EN 含客服口吻/分支句 · ZH 步骤骨架对齐 · 非整篇邮件稿"
        elif genre_mismatch:
            bucket = "A_tc148_email_template"
            verdict = "EN 客服邮件特征 + ZH 无对等分支 · 体裁异构"
        else:
            bucket = "B_polite_inline_copy"
            verdict = "EN 礼貌/分支用语 · 结构仍属排查步骤"
    elif flags.get("email_video_closing") or flags.get("thanks_cooperation"):
        bucket = "D_media_request_closing"
        verdict = "末尾索视频/邮件附件话术 · 步骤主体仍为排查手册"
    elif score >= 1:
        bucket = "E_weak_signal"
        verdict = "零星礼貌用语 · 不构成邮件稿体裁"
    else:
        bucket = "Z_none"
        verdict = "无客服邮件体裁特征"

    return {
        "library": lib,
        "group_id": gid,
        "question": g.get("question", ""),
        "bucket": bucket,
        "verdict": verdict,
        "email_score": score,
        "signals": hits,
        "negotiation_clauses": len(neg_clauses) + len(neg_offers),
        "zh_len": len(zh),
        "en_len": len(en),
        "zh_aligned_steps": zh_aligned,
        "zh_disappear_branch": zh_has_disappear_branch(zh),
        "en_unnumbered_titles": en_has_unnumbered_section_titles(en),
        "en_opener_80": en[:80].replace("\n", " "),
    }


def main() -> None:
    all_rows: list[dict] = []
    for lib, path in LIBRARIES.items():
        groups = json.loads(path.read_text(encoding="utf-8"))
        for g in groups:
            all_rows.append(classify_group(lib, g))

    interesting = [r for r in all_rows if r["bucket"] != "Z_none"]
    by_bucket: dict[str, list[dict]] = {}
    for r in interesting:
        by_bucket.setdefault(r["bucket"], []).append(r)

    out_json = ROOT / "_scratch/eval/en_email_template_scope_scan.json"
    out_json.write_text(
        json.dumps({"rows": all_rows, "interesting": interesting}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    bucket_desc = {
        "A_tc148_email_template": "TC148 型 · EN 整篇客服邮件稿 vs ZH 速记（content_role 候选）",
        "B_polite_inline_copy": "AD5S 型 · EN 礼貌/分支句嵌入 · 步骤骨架仍对齐",
        "C_negotiation_only": "协商话术 · negotiation_offer（已实现）",
        "D_media_request_closing": "仅末尾索视频/附件 · 非整篇邮件稿",
        "E_weak_signal": "弱信号 · 不构成体裁差异",
    }

    lines = [
        "# EN 客服邮件体裁 · 范围摸底",
        "",
        f"**日期**：2026-07-05 · **脚本**：[`scan_en_email_template_scope.py`](./scan_en_email_template_scope.py)",
        "",
        "专门筛 **EN 是否为完整客服邮件模板**（非 V1-05 规格缺口扫描）。",
        "复用 `negotiation_utils` 协商检测 + BL-V1-05 TC148 型信号（`Please help us confirm` / `If problem disappears` 等）。",
        "",
        "## 库级汇总",
        "",
        "| 库 | 总组数 | 有信号 | A 邮件稿 | B 礼貌嵌入 | C 协商 | D 索视频 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for lib in LIBRARIES:
        lib_rows = [r for r in all_rows if r["library"] == lib]
        n = len(lib_rows)
        sig = len([r for r in lib_rows if r["bucket"] != "Z_none"])
        a = len([r for r in lib_rows if r["bucket"] == "A_tc148_email_template"])
        b = len([r for r in lib_rows if r["bucket"] == "B_polite_inline_copy"])
        c = len([r for r in lib_rows if r["bucket"] == "C_negotiation_only"])
        d = len([r for r in lib_rows if r["bucket"] == "D_media_request_closing"])
        lines.append(f"| **{lib}** | {n} | {sig} | {a} | {b} | {c} | {d} |")

    lines.extend(
        [
            "",
            "## 结论（设计范围）",
            "",
        ]
    )
    a_all = [r for r in all_rows if r["bucket"] == "A_tc148_email_template"]
    if len(a_all) == 2 and all(r["library"] == "TC148" for r in a_all):
        lines.append(
            "- **A 型（整篇客服邮件稿 vs ZH 速记）全库仅 TC148 2 组** — 与 2026-07-03 `Please help us confirm` 结论一致；AD5S/A3S **无**同体裁组。"
        )
    else:
        lines.append(f"- **A 型共 {len(a_all)} 组**：{', '.join(r['library']+':'+r['group_id'] for r in a_all)}")

    b_ad5s = [r for r in all_rows if r["bucket"] == "B_polite_inline_copy" and r["library"] == "AD5S"]
    b_a3s = [r for r in all_rows if r["bucket"] == "B_polite_inline_copy" and r["library"] == "A3S"]
    lines.append(
        f"- **B 型（礼貌/分支句嵌入、步骤仍对齐）**：AD5S {len(b_ad5s)} 组 · A3S {len(b_a3s)} 组 — "
        "属 EN 排查文案风格差异，**不应**走「客服邮件模板可选展开」通道（与 BL-V1-05 子模式 B 一致）。"
    )
    c_all = [r for r in all_rows if r["bucket"] == "C_negotiation_only"]
    lines.append(
        f"- **C 型（协商）**：{len(c_all)} 组 — 已有 `negotiation_offer` / BL-V1-06（qa_023 等协商句在 `negotiation_offers[]`，不在 `answer_en`）。"
    )
    d_all = [r for r in all_rows if r["bucket"] == "D_media_request_closing"]
    lines.append(
        f"- **D 型（末尾索视频）**：{len(d_all)} 组 — 步骤主体仍是排查手册；可选折叠，但 **非** TC148 式整篇邮件稿。"
    )
    lines.extend(
        [
            "",
            "**V1.1  implication**：若只为 A 型服务，`content_role` 机制范围 **≤2 组（TC148）**；"
            "通用 schema + demo UI 可能 overkill，**字段标注或 TC148 专用展示** 即可。",
            "",
            "## 分桶说明",
            "",
        ]
    )
    for k, desc in bucket_desc.items():
        n = len(by_bucket.get(k, []))
        lines.append(f"- **{k}** ({n}) — {desc}")

    for bucket in (
        "A_tc148_email_template",
        "B_polite_inline_copy",
        "C_negotiation_only",
        "D_media_request_closing",
    ):
        rows = by_bucket.get(bucket, [])
        if not rows:
            continue
        lines.extend(["", f"## {bucket}", ""])
        lines.append("| 库 | group | 分数 | 信号 | 判定 |")
        lines.append("| --- | --- | ---: | --- | --- |")
        for r in rows:
            sig = ", ".join(r["signals"][:6])
            if len(r["signals"]) > 6:
                sig += "…"
            lines.append(
                f"| {r['library']} | {r['group_id']} | {r['email_score']} | {sig} | {r['verdict']} |"
            )

    out_md = ROOT / "_scratch/eval/en_email_template_scope_scan.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")
    print(f"Interesting: {len(interesting)} / {len(all_rows)}")
    for k in sorted(by_bucket):
        print(f"  {k}: {len(by_bucket[k])}")


if __name__ == "__main__":
    main()

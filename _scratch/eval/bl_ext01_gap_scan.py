#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-EXT-01 gap inventory: read-only scan of AD5S docx vs qa_groups.json."""

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
QA_GROUPS = ROOT / "_scratch/run-ad5s/qa_groups.json"
URL_RE = re.compile(r"https?://[^\s\"<>)\]]+")


def load_groups() -> list[dict]:
    return json.loads(QA_GROUPS.read_text(encoding="utf-8"))


def iter_docx_paragraphs(doc: Document):
    current_section = None
    current_question = None
    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        level = get_heading_level(block)
        if level == 1:
            current_section = text
            current_question = None
            yield {"kind": "h1", "section": current_section, "text": text, "level": 1}
        elif level in (2, 3):
            current_question = text
            yield {
                "kind": "h2" if level == 2 else "h3",
                "section": current_section,
                "question": current_question,
                "text": text,
                "level": level,
            }
        elif text:
            yield {
                "kind": "para",
                "section": current_section,
                "question": current_question,
                "text": text,
                "lang": classify_language(text),
            }


def scan_section19(doc: Document) -> dict:
    """Analyze §十九 paragraph-by-paragraph language classification."""
    in19 = False
    rows = []
    for item in iter_docx_paragraphs(doc):
        if item["kind"] == "h1":
            in19 = "十九" in item["text"] or "保养" in item["text"]
            if in19:
                rows.append({"type": "section_start", **item})
            elif rows:
                break
            continue
        if not in19:
            continue
        if item["kind"] in ("h2", "h3"):
            rows.append({"type": "heading", **item})
        else:
            rows.append({"type": "para", **item})
    return {"row_count": len(rows), "rows": rows}


def scan_formula(doc: Document) -> list[dict]:
    patterns = [
        ("50ohm", re.compile(r"50\s*[Ω欧]|50\s*ohm", re.I)),
        ("25ohm", re.compile(r"25\s*[Ω欧]|25\s*ohm", re.I)),
        ("1152", re.compile(r"1152")),
        ("power_formula", re.compile(r"1152\s*[÷/]\s*[Rr]|功率.*1152|power.*1152", re.I)),
    ]
    hits = []
    ctx = {"section": None, "question": None}
    for item in iter_docx_paragraphs(doc):
        if item["kind"] == "h1":
            ctx["section"] = item["text"]
            ctx["question"] = None
        elif item["kind"] in ("h2", "h3"):
            ctx["question"] = item["text"]
        elif item["kind"] == "para":
            text = item["text"]
            for name, pat in patterns:
                if pat.search(text):
                    hits.append(
                        {
                            "pattern": name,
                            "section": ctx["section"],
                            "question": ctx["question"],
                            "lang": item["lang"],
                            "text": text[:200],
                        }
                    )
    return hits


def scan_urls(doc: Document) -> list[dict]:
    hits = []
    ctx = {"section": None, "question": None}
    for item in iter_docx_paragraphs(doc):
        if item["kind"] == "h1":
            ctx["section"] = item["text"]
            ctx["question"] = None
        elif item["kind"] in ("h2", "h3"):
            ctx["question"] = item["text"]
        elif item["kind"] == "para":
            for url in URL_RE.findall(item["text"]):
                hits.append(
                    {
                        "url": url.rstrip(".,;)"),
                        "section": ctx["section"],
                        "question": ctx["question"],
                        "lang": item["lang"],
                        "context": item["text"][:120],
                    }
                )
    return hits


def urls_in_qa_groups(groups: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for g in groups:
        gid = g["group_id"]
        for link in g.get("links") or []:
            u = link.get("url")
            if u:
                out.setdefault(u, []).append(f"{gid}:links[]")
        text = (g.get("answer_zh") or "") + "\n" + (g.get("answer_en") or "")
        for u in URL_RE.findall(text):
            out.setdefault(u.rstrip(".,;)"), []).append(f"{gid}:prose")
        ladder = g.get("troubleshooting_ladder") or []
        for step in ladder:
            for link in step.get("links") or []:
                u = link.get("url")
                if u:
                    out.setdefault(u, []).append(f"{gid}:ladder")
            for br in step.get("branches") or []:
                for link in br.get("links") or []:
                    u = link.get("url")
                    if u:
                        out.setdefault(u, []).append(f"{gid}:branch")
    return out


def all_h1_sections(doc: Document) -> list[str]:
    secs = []
    for item in iter_docx_paragraphs(doc):
        if item["kind"] == "h1":
            secs.append(item["text"])
    return secs


def main():
    doc = Document(str(DOCX))
    groups = load_groups()
    group_sections = sorted({g.get("section") for g in groups})

    print("=" * 60)
    print("BL-EXT-01 GAP SCAN")
    print("=" * 60)

    h1s = all_h1_sections(doc)
    print(f"\n## H1 sections in docx ({len(h1s)})")
    for i, s in enumerate(h1s, 1):
        in_qg = any(s == gs or (gs and s[:6] in (gs or "")) for gs in group_sections)
        marker = "OK" if in_qg else "MISS"
        print(f"  {i:2}. [{marker}] {s[:80]}")

    print(f"\n## qa_groups sections ({len(group_sections)})")
    for s in group_sections:
        print(f"  - {s[:80]}")

    # §十九
    s19 = scan_section19(doc)
    print(f"\n## §十九 scan ({s19['row_count']} items)")
    lang_counts = {"zh": 0, "en": 0, "empty": 0}
    alternation_risk = []
    prev_lang = None
    for r in s19["rows"]:
        if r.get("type") != "para":
            print(f"  [{r.get('type','?')}] {r.get('text','')[:70]}")
            continue
        lang = r.get("lang", "?")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        if prev_lang and prev_lang != lang and prev_lang != "empty" and lang != "empty":
            alternation_risk.append((prev_lang, lang, r.get("text", "")[:60]))
        prev_lang = lang
    print(f"  Para lang counts: {lang_counts}")
    print(f"  Adjacent lang flips: {len(alternation_risk)}")
    for i, (a, b, t) in enumerate(alternation_risk[:8]):
        print(f"    flip {i+1}: {a}->{b} | {t}")
    if len(alternation_risk) > 8:
        print(f"    ... +{len(alternation_risk)-8} more")

    # Formula
    formula_hits = scan_formula(doc)
    print(f"\n## 50Ω/1152 formula hits in docx ({len(formula_hits)})")
    for h in formula_hits:
        print(f"  [{h['pattern']}] lang={h['lang']} | Q={h['question']}")
        print(f"    {h['text']}")

    qg_text = json.dumps(groups, ensure_ascii=False)
    for pat in ["50", "1152", "25Ω", "25欧"]:
        print(f"  qa_groups contains '{pat}': {pat in qg_text}")

    # URLs
    doc_urls = scan_urls(doc)
    qg_urls = urls_in_qa_groups(groups)
    doc_unique = {}
    for h in doc_urls:
        doc_unique.setdefault(h["url"], h)

    print(f"\n## URL inventory")
    print(f"  docx unique URLs: {len(doc_unique)}")
    print(f"  qa_groups unique URLs: {len(qg_urls)}")

    missing = []
    covered = []
    for url, meta in sorted(doc_unique.items()):
        if url in qg_urls:
            covered.append((url, meta, qg_urls[url]))
        else:
            missing.append((url, meta))

    print(f"\n  COVERED ({len(covered)}):")
    for url, meta, refs in covered:
        print(f"    {url}")
        print(f"      docx: §{(meta['section'] or '')[:40]} | {meta['question']}")
        print(f"      qg:   {', '.join(refs)}")

    print(f"\n  MISSING ({len(missing)}):")
    for url, meta in missing:
        domain = re.sub(r"https?://([^/]+).*", r"\1", url)
        print(f"    {url}")
        print(f"      domain={domain} lang={meta['lang']} | Q={meta['question']}")
        print(f"      ctx: {meta['context'][:100]}")

    # Write JSON for doc
    out = {
        "h1_sections_docx": h1s,
        "h1_sections_in_qa_groups": group_sections,
        "section19": {
            "lang_counts": lang_counts,
            "alternation_flips": len(alternation_risk),
            "sample_flips": [{"from": a, "to": b, "text": t} for a, b, t in alternation_risk[:20]],
            "rows_preview": [
                {k: v for k, v in r.items() if k != "section"}
                for r in s19["rows"][:30]
            ],
        },
        "formula_hits": formula_hits,
        "urls": {
            "docx_count": len(doc_unique),
            "qg_count": len(qg_urls),
            "covered": [
                {"url": u, "docx_section": m["section"], "docx_question": m["question"], "qg_refs": refs}
                for u, m, refs in covered
            ],
            "missing": [
                {"url": u, "section": m["section"], "question": m["question"], "lang": m["lang"], "context": m["context"]}
                for u, m in missing
            ],
        },
    }
    out_path = Path(__file__).parent / "bl_ext01_gap_scan.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")

    # --- orphan paragraph audit ---
    orphan = []
    current_section = None
    current_group = None
    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        t = block.text.strip()
        if not t:
            continue
        lv = get_heading_level(block)
        if lv == 1:
            current_section = t
            current_group = None
            continue
        if lv in (2, 3):
            current_group = t
            continue
        if current_group is None:
            orphan.append(
                {
                    "section": current_section,
                    "lang": classify_language(t),
                    "text": t[:120],
                    "has_url": bool(URL_RE.search(t)),
                    "has_formula": bool(re.search(r"1152|50\s*欧", t)),
                }
            )

    from collections import Counter

    sec_counts = Counter((o["section"] or "?")[:40] for o in orphan)
    print(f"\n## Orphan paragraphs (H1 body, no H2/H3): {len(orphan)}")
    for sec, cnt in sec_counts.most_common():
        print(f"  {cnt:3} | {sec}")

    formula_orphans = [o for o in orphan if o["has_formula"]]
    print(f"\n  Formula orphans: {len(formula_orphans)}")
    for o in formula_orphans:
        print(f"    [{o['lang']}] {o['text']}")

    # full URL recount in qa_groups including ladder
    urls2 = urls_in_qa_groups(groups)
    print(f"\n## qa_groups URL recount (incl ladder): {len(urls2)}")
    for u in sorted(urls2):
        print(f"  {u} <- {', '.join(urls2[u])}")

    # --- per-section orphan summaries (BL-EXT-01b) ---
    EXCLUDE_SECTIONS = ("十四", "十九")  # 十四/十九 本轮单独处理
    TECH_KW = re.compile(
        r"故障|排查|检查|测量|万用表|保险丝|限位|离合|电阻|二极管|电机|机臂|遥控|"
        r"troubleshoot|check|measure|multimeter|fuse|limit|clutch|resistor|diode|motor|remote",
        re.I,
    )
    BOILER_KW = re.compile(r"copyright|版权|免责声明|目录|table of contents", re.I)

    by_sec: dict[str, list] = {}
    for o in orphan:
        sec = o["section"] or "?"
        if any(x in sec for x in EXCLUDE_SECTIONS):
            continue
        by_sec.setdefault(sec, []).append(o)

    section_summaries = []
    print(f"\n## BL-EXT-01b orphan section summaries (excl §十四/§十九): {len(by_sec)} sections")
    for sec in sorted(by_sec.keys(), key=lambda s: -len(by_sec[s])):
        rows = by_sec[sec]
        zh_n = sum(1 for r in rows if r["lang"] == "zh")
        en_n = sum(1 for r in rows if r["lang"] == "en")
        url_n = sum(1 for r in rows if r["has_url"])
        tech_n = sum(1 for r in rows if TECH_KW.search(r["text"]))
        boiler = any(BOILER_KW.search(r["text"]) for r in rows)
        # first lines as preview (dedupe consecutive similar)
        previews = []
        for r in rows[:8]:
            previews.append(f"[{r['lang']}] {r['text']}")
        if len(rows) > 8:
            previews.append(f"... +{len(rows) - 8} more paragraphs")

        if boiler and tech_n == 0:
            value = "low_boilerplate"
        elif tech_n >= 5 or (tech_n >= 2 and zh_n >= 2):
            value = "high_troubleshooting"
        elif tech_n >= 1 or url_n >= 1:
            value = "medium_mixed"
        else:
            value = "low_unclear"

        summary = {
            "section": sec,
            "orphan_count": len(rows),
            "lang_zh": zh_n,
            "lang_en": en_n,
            "url_paragraphs": url_n,
            "tech_keyword_hits": tech_n,
            "value_tier": value,
            "previews": previews,
        }
        section_summaries.append(summary)
        print(f"\n### {sec[:70]}")
        print(f"  orphans={len(rows)} zh={zh_n} en={en_n} urls={url_n} tech_hits={tech_n} tier={value}")
        for p in previews[:5]:
            print(f"    {p}")

    out["orphan_sections_bl_ext01b"] = section_summaries
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

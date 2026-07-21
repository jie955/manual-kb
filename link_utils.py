#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外链工具：从 prose 抽链、推断类型/标签、与 images[] 同级的 links[] 规范化。"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qs, urlparse

URL_RE = re.compile(r"https?://[^\s<>\"']+")
URL_ONLY_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)

VIDEO_HOSTS = ("drive.google.com", "youtube.com", "youtu.be", "vimeo.com")


def find_urls(text: str) -> list[str]:
    return [u.rstrip(".,);]") for u in URL_RE.findall(text or "")]


def is_url_only(text: str) -> bool:
    return bool(URL_ONLY_RE.match((text or "").strip()))


def strip_urls_from_text(text: str) -> str:
    cleaned = URL_RE.sub("", text or "")
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def infer_link_type(url: str) -> str:
    host = (urlparse(url).netloc or "").lower()
    if any(v in host for v in VIDEO_HOSTS):
        return "video"
    if "topens.com" in host:
        return "support_page"
    if "amazon.com" in host or "amazon.co.uk" in host:
        return "purchase_link"
    return "other"


def pick_link_label(candidates: list[str], url: str, link_type: str) -> str:
    """用紧邻 URL 前的英文句作 label；无则按 link_type 给默认文案。"""
    for line in reversed(candidates):
        line = line.strip()
        if not line:
            continue
        if link_type == "video":
            if "instantaneously short" in line.lower():
                return line.rstrip(":").strip()
            if "short" in line.lower() or "O/S/C" in line or "terminal" in line.lower():
                return line.rstrip(":").strip()
        if link_type == "support_page":
            m = re.search(
                r"link of (.+?)(?:\s+for your reference)?\.?$",
                line,
                re.IGNORECASE,
            )
            if m:
                return m.group(1).strip()
            if "link" in line.lower() and len(line) < 120:
                return line.rstrip(":").strip()
    if link_type == "video":
        return "观看演示视频"
    if link_type == "support_page":
        return "参考支持页"
    return url


def display_link_label(link: dict | Any, locale: str = "zh") -> str:
    """Locale-appropriate link label for LLM context / UI."""
    lk = normalize_link(link)
    url = lk["url"]
    label = (lk.get("label") or "").strip()
    link_type = lk.get("link_type") or infer_link_type(url)
    if locale != "en":
        return label or url
    if label and not any("\u4e00" <= ch <= "\u9fff" for ch in label):
        return label
    if link_type == "video":
        return "Demo video"
    if link_type == "support_page":
        return "Support article"
    if link_type == "purchase_link":
        return "Product link"
    return url


def normalize_link(entry: Any) -> dict:
    if isinstance(entry, dict):
        url = str(entry.get("url") or "").strip()
        return {
            "url": url,
            "label": (entry.get("label") or "").strip() or url,
            "lang": str(entry.get("lang") or "en"),
            "link_type": str(entry.get("link_type") or infer_link_type(url)),
        }
    url = str(entry).strip()
    return {
        "url": url,
        "label": url,
        "lang": "en",
        "link_type": infer_link_type(url),
    }


def normalize_links(links: Any) -> list[dict]:
    if not links:
        return []
    if isinstance(links, list):
        return [normalize_link(x) for x in links if normalize_link(x).get("url")]
    return []


# BL-V1-04 简单档：根级 links[]，无 troubleshooting_ladder / branches
SIMPLE_LINK_GROUP_IDS = frozenset({"qa_003", "qa_010", "qa_030"})

# BL-V1-05 post-close：YouTube 视频链 · 根级 links[] · prose 剥离
VIDEO_LINK_GROUP_IDS = frozenset({"qa_029", "qa_042", "qa_043"})


def youtube_video_id(url: str) -> str | None:
    """Extract YouTube video id; host/path normalize only (no title fuzzy match)."""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""
    if "youtu.be" in host:
        vid = path.lstrip("/").split("/")[0].split("?")[0]
        return vid or None
    if "youtube.com" in host:
        if "/shorts/" in path:
            part = path.split("/shorts/", 1)[1]
            return part.split("/")[0].split("?")[0] or None
        qs = parse_qs(parsed.query)
        if qs.get("v"):
            return qs["v"][0]
    return None


def label_before_url(text: str, url: str) -> str:
    """Label = non-empty line immediately before URL (or same-line prefix)."""
    idx = text.find(url)
    if idx < 0:
        return ""
    before = text[:idx].rstrip()
    if not before:
        return ""
    line = before.split("\n")[-1].strip()
    if line.endswith(":"):
        line = line[:-1].strip()
    return line


def apply_video_tier_links(group: dict) -> bool:
    """YouTube links[] from answer_en: dedupe by video id, label from preceding EN line."""
    gid = group.get("group_id")
    if gid not in VIDEO_LINK_GROUP_IDS:
        return False
    if group.get("troubleshooting_ladder"):
        return False

    en = group.get("answer_en") or ""
    urls = find_urls(en)
    if not urls:
        return False

    seen: set[str] = set()
    new_links: list[dict] = []
    candidates = [ln.strip() for ln in en.split("\n") if ln.strip()]

    for url in urls:
        vid = youtube_video_id(url)
        dedupe_key = vid if vid else url
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        link_type = infer_link_type(url)
        label = label_before_url(en, url)
        if not label:
            label = pick_link_label(candidates, url, link_type)
        new_links.append(
            {
                "url": url,
                "label": label,
                "lang": "en",
                "link_type": link_type,
            }
        )

    cleaned = strip_urls_from_text(en)
    old_links = group.get("links") or []
    changed = new_links != old_links or cleaned != en
    group["links"] = new_links
    group["answer_en"] = cleaned
    return changed


def apply_simple_tier_links(group: dict) -> bool:
    """将 answer_en 中的外链提升到根级 links[] 并从 prose 剥离。返回是否有变更。"""
    gid = group.get("group_id")
    if gid not in SIMPLE_LINK_GROUP_IDS:
        return False
    if group.get("troubleshooting_ladder"):
        return False

    en = group.get("answer_en") or ""
    urls = find_urls(en)
    if not urls and gid != "qa_030":
        return False

    candidates = [ln.strip() for ln in en.split("\n") if ln.strip()]
    existing = {normalize_link(x)["url"] for x in (group.get("links") or [])}
    changed = False

    for url in urls:
        if url not in existing:
            link_type = infer_link_type(url)
            idx = en.find(url)
            label = ""
            if idx > 0:
                prev = en[:idx].rstrip().split("\n")[-1].strip().rstrip(":")
                if prev and len(prev) < 200:
                    label = prev
            if not label:
                label = pick_link_label(candidates, url, link_type)
            group.setdefault("links", []).append(
                {
                    "url": url,
                    "label": label,
                    "lang": "en",
                    "link_type": link_type,
                }
            )
            existing.add(url)
        changed = True

    cleaned = strip_urls_from_text(en)
    if cleaned != en:
        group["answer_en"] = cleaned
        changed = True
    return changed

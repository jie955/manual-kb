#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""images 字段工具：兼容字符串列表与 caption 后的 dict 列表。"""

from __future__ import annotations

from typing import Any


def _strip_caption(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def migrate_legacy_caption(img: dict) -> dict:
    """仅有 caption 时写入 caption_zh，保持 caption 不变（向后兼容）。"""
    out = dict(img)
    caption = _strip_caption(out.get("caption"))
    caption_zh = _strip_caption(out.get("caption_zh"))
    if caption and not caption_zh:
        out["caption_zh"] = caption
    elif caption_zh and not caption:
        out["caption"] = caption_zh
    return out


def normalize_image_entry(entry: Any) -> dict:
    if isinstance(entry, str):
        return migrate_legacy_caption(
            {"file": entry, "caption": None, "caption_status": "not_captioned"}
        )
    if isinstance(entry, dict):
        out = {
            "file": str(entry.get("file") or ""),
            "caption": entry.get("caption"),
            "caption_zh": entry.get("caption_zh"),
            "caption_en": entry.get("caption_en"),
            "caption_status": str(entry.get("caption_status") or "unknown"),
        }
        return migrate_legacy_caption(out)
    return migrate_legacy_caption(
        {"file": str(entry), "caption": None, "caption_status": "unknown"}
    )


def normalize_images(images: Any) -> list[dict]:
    if not images:
        return []
    if isinstance(images, str):
        return [normalize_image_entry(x) for x in images.split(",") if x.strip()]
    if isinstance(images, list):
        return [normalize_image_entry(x) for x in images]
    return []


def display_caption(img: dict, locale: str = "zh") -> str | None:
    """按 locale 返回展示用 caption。"""
    img = migrate_legacy_caption(img)
    if locale == "en":
        return (
            _strip_caption(img.get("caption_en"))
            or _strip_caption(img.get("caption_zh"))
            or _strip_caption(img.get("caption"))
        )
    return _strip_caption(img.get("caption_zh")) or _strip_caption(img.get("caption"))


def public_image_file(file_ref: str) -> str:
    """Map absolute/manual paths to a basename served under /images/."""
    ref = (file_ref or "").strip().replace("\\", "/")
    if not ref:
        return ""
    if ref.startswith("/images/"):
        return ref.removeprefix("/images/")
    name = ref.rsplit("/", 1)[-1]
    return name or ref


def localize_images(images: Any, locale: str = "zh") -> list[dict]:
    """Normalize images and set caption to the locale-appropriate display value."""
    out: list[dict] = []
    for img in normalize_images(images):
        row = dict(img)
        row["caption"] = display_caption(row, locale)
        row["file"] = public_image_file(row.get("file") or "")
        out.append(row)
    return out


def image_filenames(images: Any) -> list[str]:
    return [img["file"] for img in normalize_images(images) if img["file"]]


def images_metadata_str(images: Any) -> str:
    return ",".join(image_filenames(images))


def caption_text_for_embedding(images: Any) -> str:
    """将有效 caption 拼成可追加到 embedding_text 的短文本（中文优先）。"""
    parts = []
    for img in normalize_images(images):
        cap = display_caption(migrate_legacy_caption(img), "zh")
        if cap:
            parts.append(cap)
    if not parts:
        return ""
    return "[图示] " + "；".join(parts)

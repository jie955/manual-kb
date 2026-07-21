#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from image_utils import (
    caption_text_for_embedding,
    display_caption,
    localize_images,
    migrate_legacy_caption,
    normalize_image_entry,
)


def test_migrate_legacy_caption():
    img = {"file": "image_007.png", "caption": "中文说明", "caption_status": "generated"}
    out = migrate_legacy_caption(img)
    assert out["caption_zh"] == "中文说明"
    assert out["caption"] == "中文说明"


def test_display_caption_en_prefers_caption_en():
    img = {
        "file": "image_007.png",
        "caption_zh": "中文",
        "caption_en": "English caption",
        "caption": "中文",
    }
    assert display_caption(img, "en") == "English caption"
    assert display_caption(img, "zh") == "中文"


def test_display_caption_en_fallback_to_zh():
    img = {"file": "image_001.png", "caption_zh": "仅中文", "caption": "仅中文"}
    assert display_caption(img, "en") == "仅中文"


def test_localize_images_sets_display_caption():
    images = [
        {
            "file": "image_007.png",
            "caption_zh": "中文",
            "caption_en": "English",
            "caption": "中文",
        }
    ]
    en = localize_images(images, "en")
    assert en[0]["caption"] == "English"
    assert en[0]["caption_en"] == "English"
    zh = localize_images(images, "zh")
    assert zh[0]["caption"] == "中文"


def test_normalize_image_entry_string():
    out = normalize_image_entry("image_001.png")
    assert out["file"] == "image_001.png"
    assert out["caption_status"] == "not_captioned"


def test_caption_text_for_embedding_uses_zh():
    images = [{"file": "x.png", "caption_zh": "图示A", "caption_en": "Figure A"}]
    assert caption_text_for_embedding(images) == "[图示] 图示A"

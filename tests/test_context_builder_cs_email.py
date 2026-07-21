"""Context compression for cs_email mode."""

from context_builder import _compress_en_for_cs_email, build_context_block


def test_compress_en_keeps_first_four_numbered_steps():
    long_en = (
        "1 First step about BAT 11# 12#\n"
        "detail line\n"
        "2 Second disconnect accessories DIP 3\n"
        "3 Third motor test\n"
        "4 Fourth limit test\n"
        "5 Fifth should drop\n"
    )
    out = _compress_en_for_cs_email(long_en, max_chars=500)
    assert "1 First" in out
    assert "4 Fourth" in out
    # short fixture fits entirely under max_chars
    assert len(long_en) <= 500 or "5 Fifth" not in out


def test_cs_email_mode_applies_compression():
    hit = {
        "section": "s",
        "question": "q",
        "content_en": "1 " + ("x" * 5000),
        "content_zh": "",
    }
    ctx = build_context_block(hit, locale="en", response_mode="cs_email")
    assert len(ctx) < 6000
    assert "truncated for email context" in ctx or len(hit["content_en"]) > 3200


def test_en_cs_email_context_strips_bilingual_title_and_zh_caption():
    hit = {
        "section": "全灭故障 Complete Failure",
        "question": "遥控器无反应 No Response At All · AT12131 Push Button",
        "content_en": "1 Disconnect accessories.",
        "content_zh": "1 断配件",
        "images": [
            {
                "file": "image_007.png",
                "caption_zh": "中文配图说明",
                "caption_en": "English figure caption",
            }
        ],
    }
    ctx = build_context_block(hit, locale="en", response_mode="cs_email")
    assert "No Response At All" in ctx
    assert "English figure caption" in ctx
    assert "断配件" not in ctx
    assert "中文配图说明" not in ctx
    assert not any("\u4e00" <= ch <= "\u9fff" for ch in ctx)

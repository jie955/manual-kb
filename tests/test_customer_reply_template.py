from context_builder import build_context_block


def test_build_context_block_skips_en_when_customer_reply_template():
    hit = {
        "section": "s",
        "question": "q",
        "content_zh": "1 断配件\n2 测线规",
        "content_en": "Please help us confirm if the gate opener runs randomly.",
        "customer_reply_templates": [
            {
                "text": "Please help us confirm if the gate opener runs randomly.",
                "lang": "en",
                "content_role": "customer_reply_template",
            }
        ],
    }
    ctx = build_context_block(hit)
    assert "Please help us confirm" not in ctx
    assert "1 断配件" in ctx


def test_build_context_block_still_supplements_thin_zh_without_template():
    hit = {
        "section": "s",
        "question": "q",
        "content_zh": "短",
        "content_en": "Step one detailed English troubleshooting prose " * 20,
    }
    ctx = build_context_block(hit)
    assert "英文操作步骤" in ctx


def test_build_context_block_en_excludes_content_zh():
    hit = {
        "section": "Power",
        "question": "No response",
        "content_zh": "1 断配件\n2 测 DIP #3",
        "content_en": "1 Disconnect accessories.\n2 Set DIP switch #3 OFF.",
    }
    ctx = build_context_block(hit, locale="en")
    assert "English troubleshooting steps:" in ctx
    assert "Disconnect accessories" in ctx
    assert "断配件" not in ctx
    assert "Internal notes" not in ctx
    assert "Chinese" not in ctx


def test_build_context_block_en_empty_en_no_zh_fallback():
    hit = {
        "section": "Power",
        "question": "No response",
        "content_zh": "1 断配件\n2 测线规",
        "content_en": "",
    }
    ctx = build_context_block(hit, locale="en")
    assert "No English troubleshooting steps" in ctx
    assert "断配件" not in ctx

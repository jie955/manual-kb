"""Draft 22-mail scoring — §7.2 ref_keys / no-gold-ref guardrails."""

from _scratch.eval.draft_22mail_scoring import draft_dim2, draft_dim4


def test_no_gold_ref_top1_hit_steps_pending_human():
    row = {
        "generated_reply_en": "Dear Customer,\n\n1. step one\n2. step two\n3. step three\n4. step four\n",
        "top1_hit": True,
        "reply_audit": {"step_count": 4},
    }
    scen = {"type": "fault", "tier": "test"}
    d2, note = draft_dim2(row, scen, ref="")
    assert d2 == "待人工"
    assert "无金标准" in note
    assert draft_dim4("对", d2, "无需图") == "待人工"


def test_no_ref_keys_pattern_pending_not_fail():
    row = {
        "generated_reply_en": "Dear Customer,\n\n1. a\n2. b\n3. c\n",
        "top1_hit": True,
        "reply_audit": {"step_count": 3},
    }
    scen = {"type": "fault"}
    ref = "Dear Customer,\n\nPlease check wiring.\n\nBest regards,\nHeidi"
    d2, note = draft_dim2(row, scen, ref=ref)
    assert d2 == "待人工"
    assert "无 ref_keys 模式" in note
    assert draft_dim4("对", d2, "无需图") == "待人工"


def test_low_ref_keys_overlap_still_minor_edit():
    row = {
        "generated_reply_en": "Measure 11# and 12# terminals.",
        "top1_hit": True,
        "reply_audit": {"step_count": 4},
    }
    ref = (
        "1. Measure 11# and 12#\n"
        "2. DIP switch #5 OFF\n"
        "3. Short 4# and 5#\n"
        "4. Shipping address and zip code\n"
    )
    d2, note = draft_dim2(row, {"type": "fault"}, ref=ref)
    assert d2 == "小改可发"
    assert "ref_keys=" in note
    assert draft_dim4("对", d2, "无需图") == "不通过"

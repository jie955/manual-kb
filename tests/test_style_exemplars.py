"""Phase 3.2 · style exemplar routing and prompt assembly."""

from __future__ import annotations

from style_exemplars import (
    HOLD_OUT_GATE,
    build_cs_email_system_prompt,
    load_principles_bullets,
    load_style_exemplar,
    resolve_style_family,
    select_style,
)


def test_hold_out_gate_ids():
    assert HOLD_OUT_GATE == frozenset(
        {"cs_0001", "cs_0008", "cs_0013", "cs_0022"}
    )


def test_resolve_tc148_keywords():
    fam, reason = resolve_style_family(
        "PW502 TC148 push button not working instant short 4# 5#"
    )
    assert fam == "F2_tc148_wired"
    assert reason.startswith("keywords:")


def test_resolve_group_hint_qa_011():
    fam, reason = resolve_style_family(
        "gate does nothing",
        [{"group_id": "qa_011", "section": "s", "question": "q"}],
    )
    assert fam == "F1_no_response"
    assert reason == "group_hint:qa_011"


def test_resolve_group_hint_qa_022():
    fam, reason = resolve_style_family(
        "stops before fully open",
        [{"group_id": "qa_022", "section": "s", "question": "q"}],
    )
    assert fam == "F4_limit_travel"
    assert reason == "group_hint:qa_022"


def test_resolve_presales_scenario_id():
    fam, reason = resolve_style_family(
        "Minnesota solar gate question",
        scenario_id="cs_0024",
    )
    assert fam == "F7_presales"
    assert reason == "scenario:presales"


def test_resolve_presales_joyce_mail_cs_0006():
    fam, reason = resolve_style_family(
        "What is the difference between models A8131 and AT12131?",
        [{"group_id": "qa_011", "section": "s", "question": "q"}],
        scenario_id="cs_0006",
    )
    assert fam == "F7_presales"
    assert reason == "scenario:presales"


def test_resolve_presales_joyce_mail_cs_0011():
    fam, reason = resolve_style_family(
        "what is the difference between A8132 PW802 AD8 AT1202",
        [{"group_id": "qa_042", "section": "s", "question": "q"}],
        scenario_id="cs_0011",
    )
    assert fam == "F7_presales"
    assert reason == "scenario:presales"


def test_resolve_default_when_no_signal():
    fam, reason = resolve_style_family("hello")
    assert fam == "F1_no_response"
    assert reason == "default"


def test_load_exemplar_contains_placeholder():
    _path, text = load_style_exemplar("F1_no_response")
    assert "[from references" in text
    assert "Dear {customer_name}" in text
    assert "one by one" in text.lower()


def test_select_style_for_gate_hold_out_still_returns_skeleton():
    sel = select_style(
        "AT12131S gate does nothing when I push the button",
        [{"group_id": "qa_011"}],
        scenario_id="cs_0001",
    )
    assert sel is not None
    assert sel.family_id == "F1_no_response"
    assert "[from references" in sel.exemplar_text


def test_build_cs_email_system_prompt_includes_layers():
    base = "BASE {section} · {question}"
    system, sel = build_cs_email_system_prompt(
        section="Power",
        question="No response",
        customer_email="TC148 wired button fails",
        hits=[{"group_id": "qa_010"}],
        base_prompt=base,
    )
    assert "BASE Power · No response" in system
    assert "Support style principles" in system
    assert "Greeting:" in system
    assert sel is not None
    assert sel.family_id == "F1_no_response"
    assert sel.match_reason == "group_hint:qa_010"
    assert "Reply structure exemplar" in system
    assert "Dear {customer_name}" in system


def test_build_cs_email_hold_out_note():
    system, _sel = build_cs_email_system_prompt(
        section="Power",
        question="No response",
        customer_email="gate does nothing",
        hits=[{"group_id": "qa_011"}],
        scenario_id="cs_0001",
        base_prompt="BASE {section} · {question}",
    )
    assert "Gate eval scenario" in system


def test_style_disabled():
    system, sel = build_cs_email_system_prompt(
        section="s",
        question="q",
        customer_email="tc148 button",
        base_prompt="BASE {section} · {question}",
        style_enabled=False,
    )
    assert sel is None
    assert "Reply structure exemplar" not in system


def test_principles_bullets_non_empty():
    bullets = load_principles_bullets()
    assert "Greeting:" in bullets
    assert "Numbered steps:" in bullets
    assert len(bullets.splitlines()) >= 10

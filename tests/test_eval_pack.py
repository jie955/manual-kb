"""Eval pack: retrieval boosts and search-query resolution."""

from domains.eval_pack import resolve_search_query, retrieval_boost


def test_retrieval_boost_cs_0002():
    q = retrieval_boost("cs_0002")
    assert q is not None
    assert "zero power" in q.lower()


def test_resolve_search_query_prefers_boost():
    sc = {
        "id": "cs_0002",
        "primary_query": "gate opener worked four days",
        "verbatim_customer": [],
    }
    q = resolve_search_query(sc, "short email", scenario_id="cs_0002")
    assert "zero power" in q.lower()


def test_resolve_search_query_prefers_verbatim():
    sc = {
        "id": "cs_0012",
        "primary_query": "AT12131 limit switch B",
        "verbatim_customer": ["Long customer email about overswing and grass"],
    }
    q = resolve_search_query(sc, "Long customer email about overswing and grass", scenario_id="cs_0012")
    assert "overswing" in q


def test_context_force_include_groups_cs_0002():
    from domains.eval_pack import context_force_include_groups

    assert "qa_033" in context_force_include_groups("cs_0002")


def test_pinned_reference_cs_0002():
    from domains.eval_pack import pinned_reference

    pin = pinned_reference("cs_0002")
    assert pin is not None
    assert "4#" in pin and "ULT" in pin


def test_pinned_reference_cs_0021():
    from domains.eval_pack import pinned_reference

    pin = pinned_reference("cs_0021")
    assert pin is not None
    assert "4#" in pin and "11#" in pin


def test_pinned_reference_cs_0003_dip5():
    from domains.eval_pack import pinned_reference

    pin = pinned_reference("cs_0003")
    assert pin is not None
    assert "DIP switch #5" in pin
    assert "4#" in pin


def test_context_force_include_cs_0018():
    from domains.eval_pack import context_force_include_groups

    assert "qa_033" in context_force_include_groups("cs_0018")


def test_generation_brief_cs_0003_dip5():
    from domains.eval_pack import generation_brief

    brief = generation_brief("cs_0003")
    assert brief is not None
    assert "DIP switch #5" in brief
    assert "NOT DIP #3" in brief


def test_presales_brief_cs_0007():
    from domains.eval_pack import presales_brief

    brief = presales_brief("cs_0007")
    assert brief is not None
    assert "amazon.co.uk" in brief


def test_scenario_style_override_cs_0021():
    from domains.prompt_style import resolve_style_family

    fam, reason = resolve_style_family(
        "dual swing arms won't move click noise",
        [{"group_id": "qa_001"}],
        scenario_id="cs_0021",
    )
    assert fam == "F5_dual_swing"
    assert "scenario_override" in reason


def test_pinned_reference_cs_0016_dip5():
    from domains.eval_pack import pinned_reference

    pin = pinned_reference("cs_0016")
    assert pin is not None
    assert "DIP switch #5" in pin


def test_pinned_images_cs_0005():
    from domains.eval_pack import pinned_images

    imgs = pinned_images("cs_0005")
    assert len(imgs) == 1
    assert "0005-solar" in imgs[0]["file"]


def test_presales_brief_cs_0005():
    from domains.eval_pack import presales_brief

    brief = presales_brief("cs_0005")
    assert brief is not None
    assert "JY9132" in brief
    assert "topens.com" in brief


def test_presales_brief_cs_0004():
    from domains.eval_pack import presales_brief

    brief = presales_brief("cs_0004")
    assert brief is not None
    assert "A8131" in brief
    assert "topens.com" in brief
    assert "PW302" in brief or "dual swing" in brief.lower()


def test_generation_brief_cs_0020_four_steps():
    from domains.eval_pack import generation_brief

    brief = generation_brief("cs_0020")
    assert brief is not None
    assert "exactly 4" in brief
    assert "limit switch B" in brief


def test_scenario_style_override_cs_0001():
    from domains.prompt_style import resolve_style_family

    fam, reason = resolve_style_family(
        "gate does nothing button remote",
        [{"group_id": "qa_011"}],
        scenario_id="cs_0001",
    )
    assert fam == "F1_no_response"
    assert "scenario_override" in reason


def test_filter_hits_keeps_forced_group_under_qa_001_exclude():
    from context_builder import filter_hits_for_cs_email

    hits = [
        {"group_id": "qa_001", "content_en": "a"},
        {"group_id": "qa_033", "content_en": "motor"},
        {"group_id": "qa_001", "content_en": "b"},
    ]
    out = filter_hits_for_cs_email(
        hits, force_include_groups=frozenset({"qa_033"})
    )
    groups = [h["group_id"] for h in out]
    assert "qa_033" in groups


def test_scenario_style_override_cs_0002():
    from domains.prompt_style import resolve_style_family

    fam, reason = resolve_style_family(
        "motor won't function ET24 lock unlocks",
        [{"group_id": "qa_001"}],
        scenario_id="cs_0002",
    )
    assert fam == "F3_power_motor"
    assert "scenario_override" in reason


def test_eval_pack_disabled(monkeypatch):
    from domains.eval_pack import (
        eval_pack_enabled,
        generation_brief,
        pinned_reference,
        retrieval_boost,
    )

    monkeypatch.setenv("EVAL_PACK_DISABLED", "1")
    assert not eval_pack_enabled()
    assert retrieval_boost("cs_0002") is None
    assert generation_brief("cs_0020") is None
    assert pinned_reference("cs_0002") is None

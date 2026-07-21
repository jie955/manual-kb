"""Domain pack loader + compatibility symbol tests."""

from __future__ import annotations

import pytest

from domains.loader import DomainConfigError, load_domain
from library_router import (
    EN_CHROMA_DIRS,
    LIBRARY_SPECS,
    MERGED_CHROMA_DIRS,
    PRODUCT_CATALOG_LINKS,
    detect_library_hints,
)


def test_load_topens_domain():
    domain = load_domain("topens")
    assert domain.meta.id == "topens"
    assert domain.meta.display_name == "TOPENS"
    assert [p.id for p in domain.products] == ["a3s", "ad5s", "tc148"]
    assert set(domain.indices) == {"a3s", "ad5s", "tc148"}
    assert domain.routing.keyword_patterns
    assert domain.routing.special_rules
    assert "qa_022" in domain.response.context.top1_excludes
    assert domain.style.default_family == "F1_no_response"
    assert "F1_no_response" in domain.style.families
    assert domain.style.hold_out_gate == frozenset(
        {"cs_0001", "cs_0008", "cs_0013", "cs_0022"}
    )
    assert "TOPENS Customer Service" in domain.prompts.cs_email_system_en
    assert "**Greeting**" in domain.style.principles_path.read_text(encoding="utf-8")


def test_style_pack_exemplars_on_disk():
    domain = load_domain("topens")
    rel = domain.style.families["F1_no_response"].exemplar_relpath
    path = domain.style.root / rel
    assert path.is_file()
    assert "[from references" in path.read_text(encoding="utf-8")


def test_compat_symbols_match_domain():
    domain = load_domain("topens")
    assert LIBRARY_SPECS == domain.library_specs()
    assert EN_CHROMA_DIRS == domain.en_chroma_dirs()
    assert MERGED_CHROMA_DIRS == domain.merged_chroma_dirs()
    assert PRODUCT_CATALOG_LINKS == domain.product_catalog_links()


def test_keyword_hints_basic():
    assert detect_library_hints("My TC148 retractive switch") == ["tc148"]
    assert "ad5s" in detect_library_hints("AD5S dual swing left panel")
    assert "a3s" in detect_library_hints("A8132 arm replacement")


def test_missing_domain_raises():
    with pytest.raises(DomainConfigError):
        load_domain("does-not-exist")


def test_run_trace_shape():
    from engine.trace import RunTrace

    t = RunTrace(domain_id="topens", product_id="a3s")
    d = t.to_dict()
    assert d["trace_id"]
    assert d["domain_id"] == "topens"
    assert d["product_id"] == "a3s"
    assert "latency_ms" in d

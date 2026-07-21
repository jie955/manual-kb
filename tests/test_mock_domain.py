"""Second mock domain — proves engine needs no code changes for new domain packs."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from domains.loader import DomainConfigError, clear_domain_cache, load_domain
from domains.prompt_style import build_cs_email_system_prompt, resolve_style_family
from engine.trace import RunTrace, detect_context_zh_leak

REPO = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO / "engine"


def setup_function() -> None:
    clear_domain_cache()


def test_load_mock_domain_pack():
    domain = load_domain("mock")
    assert domain.meta.id == "mock"
    assert domain.meta.display_name == "ACME Mock"
    assert [p.id for p in domain.products] == ["alpha"]
    assert domain.indices["alpha"].chroma_en.endswith("chroma_captioned_en")
    assert domain.style.default_family == "M1_default"
    assert "ACME Customer Service" in domain.prompts.cs_email_system_en
    assert domain.routing.keyword_patterns[0].product_id == "alpha"


def test_mock_style_routing():
    fam, reason = resolve_style_family("alpha mock gate issue", domain_id="mock")
    assert fam == "M1_default"
    assert reason.startswith("keywords:")


def test_mock_cs_email_prompt_render():
    system, sel = build_cs_email_system_prompt(
        section="Power",
        question="No response",
        customer_email="alpha unit not working",
        hits=[{"group_id": "qa_x"}],
        domain_id="mock",
    )
    assert "ACME Customer Service agent" in system
    assert sel is not None
    assert sel.family_id == "M1_default"
    assert "Dear {customer_name}" in system


def test_engine_trace_domain_agnostic():
    trace = RunTrace(domain_id="mock", product_id="alpha")
    trace.route_reason = "keyword"
    trace.prompt_pack_version = "1"
    trace.style_pack_version = "1"
    d = trace.to_dict()
    assert d["domain_id"] == "mock"
    assert d["product_id"] == "alpha"
    assert detect_context_zh_leak(["English only context block"]) is False


def test_engine_modules_do_not_import_topens():
    """engine/ must stay domain-agnostic — no topens imports or string literals."""
    for py in ENGINE_DIR.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "topens" not in alias.name.lower(), f"{py.name} imports {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                assert "topens" not in mod.lower(), f"{py.name} imports from {mod}"
        assert "topens" not in text.lower(), f"{py.name} contains topens literal"


def test_mock_invalid_routing_product_rejected(tmp_path):
    """Loader schema: routing must reference known product ids."""
    import shutil

    src = REPO / "domains" / "mock"
    dst = tmp_path / "badmock"
    shutil.copytree(src, dst)
    (dst / "domain.yaml").write_text(
        (dst / "domain.yaml").read_text(encoding="utf-8").replace("id: mock", "id: badmock"),
        encoding="utf-8",
    )
    routing = dst / "routing.yaml"
    routing.write_text(
        "fallback: fan_out\nkeyword_patterns:\n"
        "  - product_id: unknown\n    pattern: 'test'\n",
        encoding="utf-8",
    )
    with pytest.raises(DomainConfigError, match="unknown product"):
        load_domain("badmock", domains_root=tmp_path)

"""CS Email Agent Workflow tests."""

from agents.cs_email_workflow import CsEmailWorkflowResult, dedupe_display_hits


def test_dedupe_keeps_manual_supplement():
    hits = [
        {"group_id": "qa_001", "doc_type": "troubleshooting", "rank": 1},
        {"group_id": "qa_001", "doc_type": "troubleshooting", "rank": 2},
        {
            "group_id": "qa_001",
            "doc_type": "installation_manual",
            "rank": 3,
            "supplement": "manual",
        },
    ]
    out = dedupe_display_hits(hits)
    assert len(out) == 2
    assert out[0]["rank"] == 1
    assert out[1]["doc_type"] == "installation_manual"


def test_routing_meta_shape():
    result = CsEmailWorkflowResult(
        customer_email="test",
        search_query="test",
        hits=[],
        gen_hits=[],
        matched_library="a3s",
        matched_library_label="A3S",
        routing_method="keyword",
        library_scores={"a3s": 0.9},
        keyword_hits=["a3s"],
    )
    meta = result.routing_meta()
    assert meta["unified"] is True
    assert meta["matched_library"] == "a3s"
    assert meta["routing_method"] == "keyword"

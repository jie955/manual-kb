from retrieval_engine import (
    chunk_matches_filter,
    chroma_where_clause,
    filter_retrievable,
)


def test_chroma_where_doc_type():
    assert chroma_where_clause("installation_manual") == {
        "doc_type": "installation_manual"
    }
    assert chroma_where_clause(None) is None


def test_chunk_matches_filter_doc_type():
    manual = {"doc_type": "installation_manual", "models": ["A3S"]}
    ts = {"doc_type": "troubleshooting", "models": []}
    assert chunk_matches_filter(manual, doc_type="installation_manual", models=None)
    assert not chunk_matches_filter(ts, doc_type="installation_manual", models=None)


def test_chunk_matches_filter_models():
    chunk = {"doc_type": "installation_manual", "models": ["AD5S", "AD8S"]}
    assert chunk_matches_filter(chunk, doc_type=None, models=("AD5S",))
    assert not chunk_matches_filter(chunk, doc_type=None, models=("A3S",))


def test_filter_retrievable_empty_models_means_no_model_gate():
    rows = [
        {"chunk_id": "a", "doc_type": "troubleshooting"},
        {"chunk_id": "b", "doc_type": "installation_manual", "models": ["TC148"]},
    ]
    out = filter_retrievable(rows, doc_type="troubleshooting", models=("A3S",))
    assert [r["chunk_id"] for r in out] == ["a"]

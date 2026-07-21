from pathlib import Path

import pytest

from library_router import (
    MERGED_CHROMA_DIRS,
    PRODUCT_CATALOG_LINKS,
    filter_library_specs,
    load_unified_libraries,
    unified_search,
)

REPO = Path(__file__).resolve().parents[1]
MODEL = "_scratch/modelscope/BAAI/bge-m3"


def test_filter_library_specs_all():
    ids = [s["id"] for s in filter_library_specs(None)]
    assert ids == ["a3s", "ad5s", "tc148"]


def test_filter_library_specs_two_series():
    ids = [s["id"] for s in filter_library_specs(["a3s", "ad5s"])]
    assert ids == ["a3s", "ad5s"]
    assert "tc148" not in ids


def test_product_catalog_links_shape():
    assert len(PRODUCT_CATALOG_LINKS) >= 2
    for row in PRODUCT_CATALOG_LINKS:
        assert row.get("label") and row.get("url")


@pytest.mark.skipif(
    not (REPO / MERGED_CHROMA_DIRS["a3s"]).is_dir(),
    reason="merged chroma not built",
)
def test_load_unified_merged_en_manual_config():
    libs = load_unified_libraries(
        MODEL,
        k=2,
        index="en",
        merged=True,
        allowed_libraries=["a3s"],
    )
    lib = libs["a3s"]
    assert lib.manual_config is not None
    assert lib.manual_config.doc_type == "installation_manual"


@pytest.mark.skipif(
    not (REPO / MERGED_CHROMA_DIRS["a3s"]).is_dir(),
    reason="merged chroma not built",
)
def test_unified_search_manual_supplement():
    libs = load_unified_libraries(
        MODEL,
        k=2,
        index="en",
        merged=True,
        allowed_libraries=["a3s"],
    )
    _, hits = unified_search(
        "DIP switch photocell wiring installation control board",
        libs,
        include_manual=True,
    )
    dtypes = {h.metadata.get("doc_type") for h in hits}
    assert "installation_manual" in dtypes

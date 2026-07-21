#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-PDF-04 page_identity 回归：印刷好页 id 不变 + 前置页修复。"""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from page_identity import (
    assert_printed_page_canonical_p2,
    assert_printed_page_identity_unchanged,
    canonical_parent_id,
    chunk_ids_for_page,
    normalize_page_chunks,
    page_key,
)

REPO = Path(__file__).resolve().parents[1]
MANUAL = REPO / "_scratch" / "vlm_a3s_full" / "manual_chunks.json"


def _load_manual() -> list[dict]:
    if not MANUAL.is_file():
        return []
    return json.loads(MANUAL.read_text(encoding="utf-8"))


def _page_chunks(manual: list[dict], printed: int) -> list[dict]:
    return [
        deepcopy(c)
        for c in manual
        if c.get("page_range") == [printed, printed]
        and (
            c.get("chunk_id", "").startswith(f"a3s-manual-p{printed}")
            or c.get("parent_id") == f"a3s-manual-p{printed}"
        )
    ]


class TestPageIdentity(unittest.TestCase):
    def test_pure_no_network_docstring(self):
        """normalize_page_chunks 不 import 网络模块（纯后处理契约）。"""
        import inspect

        src = inspect.getsource(normalize_page_chunks)
        self.assertNotIn("urllib", src)
        self.assertNotIn("_parse_page_via_api", src)

    @unittest.skipUnless(MANUAL.is_file(), "manual_chunks.json missing")
    def test_printed_p9_p18_p20_unchanged(self):
        manual = _load_manual()
        for printed in (9, 18, 20):
            entry = {"printed_page": printed, "pdf_index": printed + 2}
            before = _page_chunks(manual, printed)
            self.assertTrue(before, f"no fixtures for p{printed}")
            after = normalize_page_chunks(before, entry)
            assert_printed_page_identity_unchanged(
                before, after, label=f"p{printed}"
            )

    @unittest.skipUnless(MANUAL.is_file(), "manual_chunks.json missing")
    def test_printed_p2_canonical_not_front_matter(self):
        """反例样本：无 duplicate，但须确认仍为 a3s-manual-p2 / printed:2。"""
        manual = _load_manual()
        entry = {"printed_page": 2, "pdf_index": 4}
        before = _page_chunks(manual, 2)
        self.assertTrue(before, "no fixtures for p2")
        after = normalize_page_chunks(before, entry)
        assert_printed_page_identity_unchanged(before, after, label="p2")
        assert_printed_page_canonical_p2(after, printed=2)

    def test_front_matter_contact_reparents_to_idx1(self):
        entry = {"printed_page": None, "pdf_index": 1}
        before = [
            {
                "chunk_id": "a3s-manual-p1",
                "parent_id": None,
                "is_retrievable": False,
                "content_zh": "",
                "content_en": "",
            },
            {
                "chunk_id": "a3s-manual-idx1-1",
                "parent_id": "a3s-manual-p1",
                "is_retrievable": True,
                "content_en": "support@topens.com",
            },
        ]
        after = normalize_page_chunks(before, entry)
        self.assertEqual(canonical_parent_id(entry), "a3s-manual-idx1")
        self.assertEqual(chunk_ids_for_page(after), ["a3s-manual-idx1", "a3s-manual-idx1-1"])
        self.assertEqual(after[1]["parent_id"], "a3s-manual-idx1")
        self.assertEqual(after[0]["page_key"], "idx:1")

    def test_duplicate_report(self):
        chunks = [
            {"chunk_id": "a3s-manual-p1"},
            {"chunk_id": "a3s-manual-p1"},
            {"chunk_id": "a3s-manual-p3"},
            {"chunk_id": "a3s-manual-p3"},
            {"chunk_id": "a3s-manual-p9"},
        ]
        from page_identity import duplicate_chunk_id_report

        n, ids = duplicate_chunk_id_report(chunks)
        self.assertEqual(n, 2)
        self.assertEqual(ids, ["a3s-manual-p1", "a3s-manual-p3"])

    def test_images_file_not_mutated(self):
        entry = {"printed_page": 9, "pdf_index": 11}
        before = [
            {
                "chunk_id": "a3s-manual-p9-step1",
                "parent_id": "a3s-manual-p9",
                "is_retrievable": True,
                "images": [
                    {
                        "image_id": "p9-img1",
                        "file": "images/p9-step1-explosion.png",
                    }
                ],
            }
        ]
        after = normalize_page_chunks(before, entry)[0]
        self.assertEqual(after["images"][0]["file"], "images/p9-step1-explosion.png")
        self.assertEqual(after["images"][0]["image_id"], "p9-img1")


if __name__ == "__main__":
    unittest.main()

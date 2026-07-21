#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from link_utils import (
    display_link_label,
    find_urls,
    infer_link_type,
    is_url_only,
    pick_link_label,
    strip_urls_from_text,
)


class TestLinkUtils(unittest.TestCase):
    def test_url_only(self):
        self.assertTrue(is_url_only("https://drive.google.com/file/d/abc/view"))
        self.assertFalse(is_url_only("see https://x.com for help"))

    def test_strip_urls(self):
        t = "Below is the link.\nhttps://topens.com/blogs/foo\nNext step."
        self.assertEqual(find_urls(t), ["https://topens.com/blogs/foo"])
        self.assertNotIn("https://", strip_urls_from_text(t))

    def test_link_type(self):
        self.assertEqual(
            infer_link_type(
                "https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view"
            ),
            "video",
        )
        self.assertEqual(
            infer_link_type(
                "https://topens.com/blogs/blog-posts/how-to-connect-multiple-accessories"
            ),
            "support_page",
        )

    def test_pick_label_video(self):
        label = pick_link_label(
            ['How to instantaneously short the "O/S/C COM" terminals:'],
            "https://drive.google.com/file/d/x/view",
            "video",
        )
        self.assertIn("O/S/C", label)

    def test_pick_label_support(self):
        label = pick_link_label(
            [
                "Below is the link of How to Connect Multiple Accessories to a Shared Terminal on a TOPENS Gate Opener Control Board for your reference."
            ],
            "https://topens.com/blogs/blog-posts/how-to-connect-multiple-accessories",
            "support_page",
        )
        self.assertIn("Connect Multiple Accessories", label)

    def test_display_link_label_en_replaces_zh_default(self):
        lk = {
            "url": "https://topens.com/blogs/foo",
            "label": "参考支持页",
            "link_type": "support_page",
        }
        self.assertEqual(display_link_label(lk, "en"), "Support article")


if __name__ == "__main__":
    unittest.main()

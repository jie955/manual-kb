#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import unittest
from pathlib import Path

from branch_utils import (
    attach_qa_023_structure,
    attach_qa_024_structure,
    branch_matches,
    build_qa_023_ladder,
    build_qa_024_ladder,
    collect_ladder_branch_images,
    filter_branches,
    parse_zh_stall_branch_cases,
    region_from_url,
)


def _qa_024_group() -> dict:
    for path in (
        Path("_scratch/run-ad5s-dry-v106/qa_groups.json"),
        Path("_scratch/run-ad5s-dry-ladder/qa_groups.json"),
    ):
        if path.exists():
            return next(
                x
                for x in json.loads(path.read_text(encoding="utf-8"))
                if x["group_id"] == "qa_024"
            )
    raise unittest.SkipTest("qa_024 dry-run json not present")


class TestBranchUtils(unittest.TestCase):
    def test_parse_zh_four_cases(self):
        zh = (
            "拉开门开门不正常加二极管电阻 （推开门关门不正常）\n"
            "拉开门关门不正常加二极管电阻（推开门开门不正常）"
        )
        cases = parse_zh_stall_branch_cases(zh)
        self.assertEqual(len(cases), 4)
        keys = {(c["install_mode"], c["stall_symptom"]) for c in cases}
        self.assertEqual(
            keys,
            {
                ("pull_open", "open_abnormal"),
                ("push_open", "close_abnormal"),
                ("pull_open", "close_abnormal"),
                ("push_open", "open_abnormal"),
            },
        )

    def test_qa_024_ladder_two_content_branches(self):
        g = _qa_024_group()
        ladder, reason = build_qa_024_ladder(g)
        self.assertIsNone(reason)
        self.assertIsNotNone(ladder)
        assert ladder is not None
        self.assertEqual(len(ladder), 4)
        step3 = ladder[2]
        self.assertEqual(step3["step_index"], 3)
        self.assertEqual(len(step3["links"]), 1)
        self.assertEqual(step3["links"][0]["applies_when"], {"region": "US"})
        self.assertEqual(len(step3["branches"]), 2)

        regions = {b["applies_when"]["region"] for b in step3["branches"]}
        self.assertEqual(regions, {"US", "UK"})

        us_br = next(b for b in step3["branches"] if b["applies_when"]["region"] == "US")
        self.assertEqual(len(us_br["applies_when_any"]), 2)
        self.assertEqual(
            {(p["install_mode"], p["stall_symptom"]) for p in us_br["applies_when_any"]},
            {("pull_open", "open_abnormal"), ("push_open", "close_abnormal")},
        )
        self.assertIn("image_026.png", us_br["images"])
        self.assertIn("image_028.png", us_br["images"])
        self.assertNotIn("image_027.png", us_br["images"])

        uk_br = next(b for b in step3["branches"] if b["applies_when"]["region"] == "UK")
        self.assertIn("image_027.png", uk_br["images"])
        self.assertIn("+Motor", us_br["content_en"])
        self.assertIn("Motor-", uk_br["content_en"])

        for b in step3["branches"]:
            url = b["links"][0]["url"]
            self.assertEqual(b["applies_when"]["region"], region_from_url(url))

        link_count = len(step3["links"]) + sum(
            len(b.get("links") or []) for b in step3["branches"]
        )
        self.assertEqual(link_count, 3)

    def test_branch_matches_empty_ctx_shows_two_branches(self):
        g = _qa_024_group()
        ladder, _ = build_qa_024_ladder(g)
        assert ladder is not None
        step3_branches = ladder[2]["branches"]
        self.assertEqual(len(filter_branches(step3_branches, {})), 2)

    def test_branch_matches_us_region_one_branch(self):
        g = _qa_024_group()
        ladder, _ = build_qa_024_ladder(g)
        assert ladder is not None
        step3_branches = ladder[2]["branches"]
        matched = filter_branches(step3_branches, {"region": "US"})
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["applies_when"]["region"], "US")

    def test_branch_matches_screenshot_scenario(self):
        g = _qa_024_group()
        ladder, _ = build_qa_024_ladder(g)
        assert ladder is not None
        ctx = {
            "install_mode": "push_open",
            "stall_symptom": "close_abnormal",
            "region": "US",
        }
        matched = filter_branches(ladder[2]["branches"], ctx)
        self.assertEqual(len(matched), 1)
        br = matched[0]
        self.assertTrue(branch_matches(br, ctx))
        self.assertIn("+Motor", br["content_en"])
        self.assertIn("推开门关门不正常", br["content_zh"])

    def test_us_branch_images_exclude_027(self):
        g = _qa_024_group()
        ladder, _ = build_qa_024_ladder(g)
        assert ladder is not None
        imgs = collect_ladder_branch_images(ladder, {"region": "US"})
        self.assertIn("image_026.png", imgs)
        self.assertNotIn("image_027.png", imgs)

    def test_close_abnormal_partial_ctx_two_different_branches(self):
        g = _qa_024_group()
        ladder, _ = build_qa_024_ladder(g)
        assert ladder is not None
        matched = filter_branches(ladder[2]["branches"], {"stall_symptom": "close_abnormal"})
        self.assertEqual(len(matched), 2)
        contents = {b["content_en"][:40] for b in matched}
        self.assertEqual(len(contents), 2)

    def test_zh_en_wiring_count_mismatch_returns_reason(self):
        g = _qa_024_group()
        broken = dict(g)
        broken["answer_en"] = g["answer_en"].replace(
            "Connect anode of the diode to “Motor-”",
            "REMOVED_SECOND_WIRING",
        )
        ladder, reason = build_qa_024_ladder(broken)
        self.assertIsNone(ladder)
        self.assertIsNotNone(reason)
        assert reason is not None
        self.assertIn("en_wiring_blocks=1", reason)
        self.assertIn("count mismatch", reason)

    def test_attach_failure_emits_structure_warning(self):
        g = _qa_024_group()
        broken = dict(g)
        broken["answer_en"] = g["answer_en"].replace(
            "Connect anode of the diode to “Motor-”",
            "REMOVED_SECOND_WIRING",
        )
        broken.pop("structure_warnings", None)
        import io

        buf = io.StringIO()
        ok = attach_qa_024_structure(broken, log=buf)
        self.assertFalse(ok)
        self.assertEqual(len(broken.get("structure_warnings") or []), 1)
        self.assertEqual(
            broken["structure_warnings"][0]["code"], "stall_branch_align_failed"
        )
        self.assertIn("WARNING", buf.getvalue())


def _qa_023_fixture() -> dict:
    return {
        "group_id": "qa_023",
        "answer_zh": (
            "测试有问题的机臂，好的机臂的红黑线并联到有问题的机臂红黑线接线端口，并把好的机臂的离合打开；"
            "如果俩机臂都怀疑电机电流小问题，分别并接；\n"
            "机臂2的红黑线并到机臂1的电机接线端口\n"
            "机臂1的红黑线并到机臂2的电机接线端口\n"
            "并接后有问题的机臂可以正常工作，说明就是电机电流小问题，加电阻\n"
            "注意链接国家\n"
            "并接后也不行发视频看看"
        ),
        "answer_en": (
            "Referring to the diagram below, connect the BLACK & RED wires of the arm 2 "
            "to the BLACK & RED wires of the arm 1 in parallel. Then connect the BLACK & RED "
            'wires of the arm 1 to "MOTOR" terminals on the control board as normal. '
            "Disengage the clutch of arm 2, and press the remote to see whether the gate 1 "
            "opens and closes properly.\n"
            "Referring to the diagram below, connect the BLACK & RED wires of the arm 2 back "
            'to "MOTOR" terminals on the control board as normal. Then connect the BLACK & RED '
            "wires of the arm 1 to the BLACK & RED wires of the arm 2 in parallel. "
            "Disengage the clutch of arm 1, and press the remote to see whether the gate 2 "
            "opens and closes properly.\n"
            "If the problem disappear in the above step, adding some load to the gate motor "
            "by connecting a resistor to the BLACK & RED wires of the arm in parallel to solve "
            "the problem. Regretfully, we do not have this resistor for sale in our store. "
            "Sorry for the inconvenience. Instead, you can purchase the resistors via the "
            "following link.\n"
            "Below is the link to the resistor that will work.\n"
            "If the gate 1 and gate 2 cannot work normally in step 2 and step 3, it is much "
            "suggested to shoot a video showing the problem and some pictures of the control "
            "board, so that we can figure out the problem."
        ),
        "links": [
            {
                "url": "https://www.amazon.com/dp/B08HYZV3DW",
                "label": "resistor",
                "lang": "en",
                "link_type": "purchase_link",
            }
        ],
        "images": ["image_024.png", "image_025.png"],
    }


class TestQa023Ladder(unittest.TestCase):
    def test_build_two_parallel_branches(self):
        ladder, reason = build_qa_023_ladder(_qa_023_fixture())
        self.assertIsNone(reason)
        assert ladder is not None
        self.assertEqual(len(ladder), 3)
        branches = ladder[0]["branches"]
        self.assertEqual(len(branches), 2)
        self.assertEqual(len(filter_branches(branches, {})), 2)
        self.assertEqual(
            filter_branches(branches, {"parallel_test": "arm2_on_arm1"})[0]["images"],
            ["image_024.png"],
        )

    def test_attach_clears_root_links(self):
        g = _qa_023_fixture()
        self.assertTrue(attach_qa_023_structure(g))
        self.assertEqual(g["links"], [])
        self.assertEqual(len(g["troubleshooting_ladder"][1]["links"]), 1)


if __name__ == "__main__":
    unittest.main()

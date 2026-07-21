#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import unittest
from pathlib import Path

from ladder_utils import build_troubleshooting_ladder, split_numbered_steps

QA_008_ZH = (
    "1打开控制箱调整天线位置和方向\n"
    "2 通过穿线孔尝试把天线拉出来点试试\n"
    "3 更换遥控器电池试试\n"
    "4 加外接收器"
)

QA_008_EN = (
    "1 Please note that the M12 remote has an open-area range of approximately 65 feet. "
    "If the gate opener does not respond within this distance, open the motor cover and "
    "locate the black antenna on top of the control board. Adjust its position and direction—"
    "vertical, horizontal, or tilted—to improve signal reception, then test the remote again. "
    "If the range remains insufficient, proceed to Step 2.\n"
    "2 Pull the Antenna Out from the Control Box: Pull the antenna through the cable gland "
    "at the bottom of the control box and extend it fully straight for optimal signal reception. "
    "Test the gate operation with the remote control to check if the control range has increased. "
    "If the range is still insufficient, proceed to Step 3.\n"
    "3 Replace Remote Control Battery: The remote control battery may be exhausted. "
    "Replace the battery with a new one and attempt to operate the gate again. "
    "2 PCS 3V lithium cell CR2025 batteries are required for one remote. "
    "Try Step 4 if the problem persists.\n"
    "4 Add an ERM12 External Receiver: Connect the ERM12 external receiver to the control board "
    "of the gate opener. Program the M12 remote control with the ERM12 external receiver."
)


class TestLadderUtils(unittest.TestCase):
    def test_split_numbered_steps_zh(self):
        steps = split_numbered_steps(QA_008_ZH)
        self.assertEqual(sorted(steps.keys()), [1, 2, 3, 4])
        self.assertIn("加外接收器", steps[4])

    def test_build_qa_008_ladder(self):
        ladder = build_troubleshooting_ladder(QA_008_ZH, QA_008_EN)
        self.assertIsNotNone(ladder)
        assert ladder is not None
        self.assertEqual(len(ladder), 4)
        self.assertEqual([s["step_index"] for s in ladder], [1, 2, 3, 4])
        self.assertFalse(ladder[0]["is_last_resort"])
        self.assertFalse(ladder[1]["is_last_resort"])
        self.assertFalse(ladder[2]["is_last_resort"])
        self.assertTrue(ladder[3]["is_last_resort"])
        self.assertEqual(ladder[3]["branches"], [])
        self.assertIn("ERM12", ladder[3]["content_en"])
        self.assertIn("加外接收器", ladder[3]["content_zh"])

    def test_no_ladder_for_unnumbered(self):
        self.assertIsNone(
            build_troubleshooting_ladder("检查电压和保险丝", "Check voltage and fuse.")
        )

    def test_qa_008_from_dry_run_json(self):
        path = Path("_scratch/run-ad5s-dry-v106/qa_groups.json")
        if not path.exists():
            self.skipTest("dry-run json not present")
        groups = json.loads(path.read_text(encoding="utf-8"))
        g = next(x for x in groups if x["group_id"] == "qa_008")
        ladder = build_troubleshooting_ladder(g["answer_zh"], g["answer_en"])
        self.assertIsNotNone(ladder)
        assert ladder is not None
        self.assertEqual(len(ladder), 4)
        self.assertTrue(ladder[-1]["is_last_resort"])


if __name__ == "__main__":
    unittest.main()

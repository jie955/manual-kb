#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from display_content_utils import is_thin_zh, thin_zh_reason

QA_001_ZH = (
    "1 检查接线，测控制板BAT端口的电压\n"
    "2 如果电压正常，检查控制板power灯是否正常闪烁，如果没亮，检查更换保险丝\n"
    "3 如果电压低于22VDC，断开电池和控制板之间的接线，测量电池电压是否正常，如果低，测TS24-U适配器的输出，如果输出正常，多充一会儿试试；\n"
    "4 如果电池电压还是不行，检查电池，更换电池试试"
)


class TestDisplayContentUtils(unittest.TestCase):
    def test_qa_031_like(self):
        zh = "1 检查\n2 断开配件"
        self.assertTrue(is_thin_zh(zh, "x" * 1235))

    def test_qa_001_prod_not_thin(self):
        self.assertFalse(is_thin_zh(QA_001_ZH, "x" * 1074))

    def test_qa_032_compact_steps(self):
        zh = (
            "1 断电重置，走个完整的开关门循环\n"
            "2 检查限位功能，观察是否限位停\n"
            "3 检查缓停止功能在机臂不带门的时候是否正常\n"
            "4 还不行换控制板"
        )
        self.assertTrue(is_thin_zh(zh, "x" * 1013))

    def test_qa_022_prod_not_thin(self):
        zh = (
            "电机电流小导致的走停一般是电机开始启动一下然后就猛地停住，一般是开门有问题，或者关门有问题，"
            "这种一般机臂不带门，手握住拉耳，按遥控器机臂可以正常伸缩；\n"
            "门突然启动时扯着机臂动导致电流小造成的，这种情况换控制板还不好用，只能并电阻，"
            "门的状态包括机臂电流是可能会波动的，如果只是偶尔这样，说明电流不是特别小，"
            "这个时候阻值大一点没关系，可以先试试50欧的电阻，电阻发热没那么严重，相对来说会更好一些。不行再25欧。\n"
            "负载电阻没有规定电压，只有功率要求，20欧-100欧都可以，功率要大于1152除以电阻值。\n"
            "电阻阻值变小发热会更厉害，电阻最好不要贴在盒子上安装。"
        )
        self.assertFalse(is_thin_zh(zh, "x" * 482))

    def test_qa_033_few_steps(self):
        zh = (
            "1 断开有线配件，按遥控器让门停半路\n"
            "2 如果断开配件后，自动关门还是没起作用\n"
            "特殊案例：推拉开门逻辑反了"
        )
        self.assertTrue(is_thin_zh(zh, "x" * 1070))


if __name__ == "__main__":
    unittest.main()

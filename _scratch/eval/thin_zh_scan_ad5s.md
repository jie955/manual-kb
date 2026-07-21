# BL-V1-07 · AD5S thin-ZH 全库扫描

**组数** 34 · **thin** 20 · **边界未触发** 0

## 判定规则（v2 · 2026-07-05）

1. zh 空 → thin
2. zh < 80 且 en > 3×zh
3. en ≥ 200 且 zh/en < 8%
4. 编号步骤 < 3 且 en ≥ 400 且 zh < 250
5. 编号步骤 ≥ 3 且 zh < 150 且 en ≥ 800 且 zh/en < 15%

> v1 的 zh/en<25% 误触 **30/34**；v2 全库 **见 thin_reason 列**

## thin 组

| group  |  zh |   en |  ratio | steps | reason                   | question                                            |
| ------ | --: | ---: | -----: | ----: | ------------------------ | --------------------------------------------------- |
| qa_030 |   0 |  373 |    0.0 |     0 | empty_zh                 | 维护指南链接 Maintenance Guides                     |
| qa_028 |   7 |  241 |  0.029 |     0 | short_zh_3x_en           | 日常保养润滑 Routine Maintenance                    |
| qa_008 |  54 | 1336 | 0.0404 |     3 | short_zh_3x_en           | 遥控距离不够 Short Remote Range                     |
| qa_031 |  59 | 1235 | 0.0478 |     4 | short_zh_3x_en           | 随意开关门 Random Opening/Closing                   |
| qa_005 |  36 |  663 | 0.0543 |     0 | short_zh_3x_en           | 学不上遥控器 （学习灯不亮）Cannot Program Remote    |
| qa_018 |  90 | 1504 | 0.0598 |     4 | extreme_ratio            | 拉开门安装 For Pull-to-Open Installation            |
| qa_017 |  90 | 1499 |   0.06 |     4 | extreme_ratio            | 推开门安装 For Push-to-Open Installation            |
| qa_019 | 119 | 1809 | 0.0658 |     5 | extreme_ratio            | 推开门安装 For Push-to-Open Installation            |
| qa_016 | 119 | 1761 | 0.0676 |     5 | extreme_ratio            | 拉开门安装 For Pull-to-Open Installation            |
| qa_029 |  36 |  532 | 0.0677 |     0 | short_zh_3x_en           | 深度润滑（拆机臂）Deep Lubrication                  |
| qa_006 |  82 | 1167 | 0.0703 |     0 | extreme_ratio            | 学不上遥控器 （学习灯亮）Cannot Program Remote      |
| qa_021 | 125 | 1422 | 0.0879 |     0 | few_steps(0)_long_en     | 推开门安装 For push-to-open installation            |
| qa_023 | 158 | 1650 | 0.0958 |     0 | few_steps(0)_long_en     | 并接机臂红黑线排查                                  |
| qa_034 | 119 | 1220 | 0.0975 |     2 | few_steps(2)_long_en     | 风会把门吹开 There is Little Play When the Gat      |
| qa_020 | 185 | 1536 | 0.1204 |     0 | few_steps(0)_long_en     | 推开门安装 For push-to-open installation            |
| qa_032 | 123 | 1013 | 0.1214 |     4 | compact_steps(4)_long_en | 缓停止有问题 Soft Stop Issues                       |
| qa_015 | 121 |  930 | 0.1301 |     2 | few_steps(2)_long_en     | 两个机臂只朝一个方向 Two Arms Only Work One Direct  |
| qa_007 |  67 |  445 | 0.1506 |     0 | short_zh_3x_en           | 其中一个遥控器无法工作 One (or Some) of Remotes Doe |
| qa_033 | 201 | 1070 | 0.1879 |     2 | few_steps(2)_long_en     | 自动关门不生效 Auto Close Function Doesn't Work     |
| qa_013 |  74 |  315 | 0.2349 |     0 | short_zh_3x_en           | 不工作（只CODE LED微微亮）                          |

## 非 thin（按 ratio 升序 · 边界观察）

| group  |   zh |   en |  ratio | thin? |
| ------ | ---: | ---: | -----: | :---: |
| qa_009 |  213 | 1627 | 0.1309 |      |
| qa_001 |  157 | 1074 | 0.1462 |      |
| qa_003 |  232 | 1514 | 0.1532 |      |
| qa_002 |  202 | 1235 | 0.1636 |      |
| qa_011 |  137 |  825 | 0.1661 |      |
| qa_004 |  700 | 4064 | 0.1722 |      |
| qa_012 |  348 | 1887 | 0.1844 |      |
| qa_010 |  620 | 3345 | 0.1854 |      |
| qa_024 |  685 | 3566 | 0.1921 |      |
| qa_026 |  257 | 1337 | 0.1922 |      |
| qa_014 |  476 | 1232 | 0.3864 |      |
| qa_027 | 1089 | 2753 | 0.3956 |      |
| qa_022 |  278 |  482 | 0.5768 |      |
| qa_025 |  385 |  561 | 0.6863 |      |

## 重点边界

- **qa_022**: zh=278 en=482 ratio=0.5768 thin=False · preview: `电机电流小导致的走停一般是电机开始启动一下然后就猛地停住，一般是开门有问题，或者关门有问题，这种一般机臂不带门，手握住拉…`
- **qa_001**: zh=157 en=1074 ratio=0.1462 thin=False · preview: `1 检查接线，测控制板BAT端口的电压 2 如果电压正常，检查控制板power灯是否正常闪烁，如果没亮，检查更换保险丝 …`
- **qa_008**: zh=54 en=1336 ratio=0.0404 thin=True · preview: `1打开控制箱调整天线位置和方向 2 通过穿线孔尝试把天线拉出来点试试 3 更换遥控器电池试试 4 加外接收器…`
- **qa_025**: zh=385 en=561 ratio=0.6863 thin=False · preview: `AD5S/AD8S控制板直接接触遇阻（指不连接红外，控制板本身的遇阻功能）不分开关门，第一次遇阻反弹3秒，第二次遇阻停止…`
- **qa_028**: zh=7 en=241 ratio=0.029 thin=True · preview: `日常保养润滑：…`

# eval_queries 覆盖表（2026-07-05 更新）

> 运行：`python eval_run.py _scratch/run-007/chroma_captioned --eval eval_queries.json`（A3S）  
> AD5S：`python eval_run.py _scratch/run-ad5s/chroma_captioned --eval eval_queries_ad5s.json`  
> Demo 人工验收：[`demo_checklist.md`](./demo_checklist.md)

## A3S · `eval_queries.json`（BL-V1-02 · 28/28 组）

| id | query | group_id | category | 口语变体 |
| --- | --- | --- | --- | :---: |
| q01 | 控制板灯不亮 | qa_001 | ambiguous_title | ✅ |
| q02 | 适配器供电 control board power 灯不亮 | qa_001 | title_paraphrase | |
| q03 | 纯太阳能控制板指示灯不亮 | qa_002 | title_paraphrase | |
| q04 | 太阳能充不进电池 | qa_003 | colloquial | ✅ |
| q05 | 接上太阳能板门机就不转了 | qa_004 | long_group_child | ✅ |
| q06 | 电池耗电特别快 | qa_005 | colloquial | ✅ |
| q07 | 遥控器学不上 学习灯不亮 | qa_006 | confusable_pair | ✅ |
| q08 | 学遥控器时学习灯一直亮 | qa_007 | confusable_pair | ✅ |
| q09 | 其中一个遥控器坏了 | qa_008 | title_paraphrase | |
| q10 | 遥控距离太短 | qa_009 | colloquial | ✅ |
| q11 | 按好几次遥控器才有反应 | qa_010 | colloquial | ✅ |
| q12 | 遥控器按了没反应 | qa_011 | long_group_child | ✅ |
| q13 | 控制板一直咔哒响 | qa_012 | colloquial | ✅ |
| q14 | 一按遥控器保险丝就烧 | qa_013 | long_group_child | ✅ |
| q15 | CODE LED 微微亮不工作 | qa_014 | title_paraphrase | |
| q16 | 手动反推门机排查 | qa_022 | title_paraphrase | |
| q17 | 电机电流偏小是什么原因 | qa_025 | translated_group | ✅ |
| q18 | no response when pressing remote | qa_011 | english_query | |
| q19 | 门关到位又弹回来 拉开门 | qa_015 | colloquial | ✅ |
| q20 | 推开门安装 关门反弹怎么调 | qa_016 | colloquial | ✅ |
| q21 | 开门一直走 不限位 | qa_017 | colloquial | ✅ |
| q22 | 拉开门 开门位置不对 不限位 | qa_018 | long_group_child | |
| q23 | 推开门 开门停不下来 | qa_019 | colloquial | ✅ |
| q24 | 拉开门 关门不限位 限位B怎么调 | qa_020 | long_group_child | |
| q25 | 推开门 关不到位 不限位 | qa_021 | colloquial | ✅ |
| q26 | 拉开门开门走停 加二极管电阻 | qa_023 | title_paraphrase | |
| q27 | 推开门开门不正常 二极管怎么接 | qa_024 | confusable_pair | ✅ acceptable qa_023 |
| q28 | 万用表测机臂电流多少正常 | qa_026 | colloquial | ✅ |
| q29 | 测工作电流详细步骤 11号12号 | qa_027 | translated_group | |
| q30 | 空载电流测多少算正常 | qa_028 | colloquial | ✅ |

| 指标 | 值 |
| --- | ---: |
| 组覆盖 | **28/28 (100%)** · 设计 |
| 口语变体占比 | **18/30 (60%)** |
| eval 验证 | **29/30 Top1 · 30/30 Top3**（BL-V1-08 Phase2 · q27 acceptable BL-V1-03） |

**`translated_group` 压测**：qa_017（空 ZH）、qa_025/q27/q29（EN 为主）— 扩 query 后须跑 Top1 留档。

---

## TC148 · `eval_queries_tc148.json`

| id | query | group_id | category | 口语变体 |
| --- | --- | --- | --- | :---: |
| t01 | 接上墙壁开关后门自己乱开 | qa_001 | colloquial | ✅ |
| t02 | TC148 一接上门机就乱动 | qa_001 | colloquial | ✅ |
| t03 | 墙壁按键干扰 门机随机动作 | qa_001 | title_paraphrase | |
| t04 | 按 TC148 没反应 遥控能用 | qa_002 | colloquial | ✅ |
| t05 | TC148 防水按钮按了门不动 | qa_002 | colloquial | ✅ |
| t06 | push button 端口短接测试 O/S/C COM | qa_002 | long_group_child | |

**原文外链（提取在 `content_en`，demo 未展示 · BL-V1-04）**：qa_001/qa_002 各 1× [topens 共端子博文](https://topens.com/blogs/blog-posts/how-to-connect-multiple-accessories-to-a-shared-terminal-on-a-topens-gate-opener-control-board)；qa_002 另 1× [Drive 短接视频](https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing)。t06 命中 qa_002 时应优先视频链，非 qa_001 `image_001` COM 图。

| 指标 | 值 |
| --- | ---: |
| 组覆盖 | **2/2 (100%)** |
| 口语变体占比 | **4/6 (67%)** |

---

## AD5S · `eval_queries_ad5s.json`（BL-V1-03 · v3 · 2026-07-05）

| id | query | group_id | category | 口语 |
| --- | --- | --- | --- | :---: |
| a01–a15 | （首版 · 不变） | qa_001–qa_014/022/010 | 见 JSON | ✅ 为主 |
| a16 | 门刚动一下就走停 推一下门能走过去 | qa_022 | colloquial | ✅ |
| b01–b14 | （Batch1–7 · 不变） | qa_031–043 | colloquial 为主 | ✅ |
| r12a/r12b/b07/l12 | §十二 | qa_020/021/037 | — | ✅ |
| **c01–c13** | 13 组补齐 · 见 [`bl_v1_03_execution_record.md`](./bl_v1_03_execution_record.md) | qa_007…qa_030 | colloquial 为主 | ✅ |

| 指标 | 值 |
| --- | ---: |
| prod 组数 | **43** |
| eval 条数 | **47** |
| **主期望组覆盖** | **41/43（95.3%）** |
| **含 acceptable 触及** | **43/43（100%）** |
| 仅 acceptable 无 primary | **qa_024 · qa_029** |
| Top1（2026-07-05） | **45/47（95.7%）** · BL-V1-05 后（与 08b/04 持平） |
| Top3 | **47/47（100%）** |

> **BL-V1-05 Tier A spec**（**12/12**）：**✅** · [`bl_v1_05_execution_record.md`](./bl_v1_05_execution_record.md)  
> **BL-V1-04 外链/branch**（c08/c13/a04/a09）：**✅** · [`bl_v1_04_execution_record.md`](./bl_v1_04_execution_record.md)  
> **§十/十一 bounce**（c04–c07）：**BL-V1-08b ✅** · Top1 4/4 · b10 无回归  
> **§十二 legacy**：l12 · **BL-V1-08 ✅**

~~13 组无 eval~~ → **BL-V1-03 已关闭** · 留档 [`bl_v1_03_execution_record.md`](./bl_v1_03_execution_record.md)

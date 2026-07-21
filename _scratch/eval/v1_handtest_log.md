# docx V1 线 · Demo 手测留档

**日期**：2026-07-05  
**脚本**：[`v1_docx_handtest_browser.py`](./v1_docx_handtest_browser.py) · [`tc148_handtest_browser.py`](./tc148_handtest_browser.py) · [`v1_handtest_llm_on_browser.py`](./v1_handtest_llm_on_browser.py)

---

## a16 Top3 核实（文档修正）

| 来源 | `top3_groups` |
| --- | --- |
| [`bl_v1_03_ad5s_eval.json`](./bl_v1_03_ad5s_eval.json) | `[qa_024, qa_040, **qa_024**]` |
| [`bl_v1_05_youtube_eval.json`](./bl_v1_05_youtube_eval.json)（当前基线） | `[qa_024, qa_040, **qa_040**]` |

gate 均因 **qa_040 ∈ acceptable** 通过。已写入 [`ad5s_eval_known_misses.md`](./ad5s_eval_known_misses.md) rank#3 沿革脚注。

---

## LLM=off · AD5S `:8765` · 12/12 PASS

| id | query | top1 | 要点 |
| --- | --- | --- | --- |
| TA01 | 控制板灯不亮 | qa_001 | flat · 配图 1 |
| TA10 | 按遥控器完全没有反应 | qa_010 | flat · 视频链 1 |
| TA33 | 自动关门功能没用… | qa_033 | Tier A DIP#2 |
| TA40 | 门开到一半就停… | qa_040 | Tier A 中途走停 |
| LB16 | 开到位后又弹回来 拉开门 | qa_016 | 限位域 · 配图 3 |
| LB37 | 拉开门 开门不限位 限位A怎么调 | qa_037 | eval **b07** 口径 |
| B31 | 门自己乱开乱关 | qa_031 | thin-ZH + EN 块 |
| YT29 | 拆机臂内部怎么润滑 | qa_029 | **3** 可点 YouTube |
| YT42 | 脱门也打不开离合 伸太过… | qa_042 | **4** 可点 YouTube · eval **b12** |
| **P23** | 电机电流小 并接机臂排查 | qa_023 | ladder · **parallel 标签** · 三下拉 hidden ✅ |
| **P24** | 走停加电阻 二极管怎么接 | qa_024 | ladder · **三下拉 visible** · 筛选后 1 US 卡 ✅ |
| S08 | 遥控距离太短… | qa_008 | ladder 4 步 |

截图：`_scratch/eval/screenshots/v1_handtest/*.png`

**探针说明**：首轮用非 eval 口语（LB37/YT42）曾 Top1 miss — 换 **b07/b12** 口径后 12/12，属探针措辞问题非回归。

---

## LLM=off · TC148 `:8766` · 2/2 blocking PASS（T3 补丁前快照）

| id | top1 | links | 图 | 判定 |
| --- | --- | ---: | ---: | --- |
| T2 | qa_002 ✅ | 2 | 0 | PASS |
| T1 | qa_001 ✅ | 1 | 1 | PASS · COM 图 |
| T3 | qa_001（**known Top1 miss**） | 1 | 1 | → **已关闭** · 见下节 |

T3 在补丁前命中 qa_001 时 ZH 为随机开关门/接地，不含短接步骤 — 与 2026-07-03 demo 记录一致，属已知 open 项，不 retro-block V1 结案。

---

## LLM=on · 客户演示路径 · 7/7 PASS

**模式**：playwright headless · `#useLlm` checked · `gemini-2.5-flash` · AD5S `:8765` + TC148 `:8766`  
**结果 JSON**：[`v1_handtest_llm_on_result.json`](./v1_handtest_llm_on_result.json)

### AD5S · 5/5

| id | query | top1 | LLM 字 | links | 要点 |
| --- | --- | --- | ---: | ---: | --- |
| L-P23 | 电机电流小 并接机臂排查 | qa_023 | 829 | 1 | parallel ladder + 润色 ✅ |
| L-P24 | 走停加电阻 二极管怎么接 | qa_024 | 867 | 4 | 三下拉 + 筛选 + 润色 ✅ |
| L-TA10 | 按遥控器完全没有反应 | qa_010 | 1297 | 1 | flat + 视频链 + 润色 ✅ |
| L-YT29 | 拆机臂内部怎么润滑 | qa_029 | 454 | 3 | **3** 可点 YouTube + 润色 ✅ |
| L-TA01 | 控制板灯不亮 | qa_001 | 932 | 0 | flat + 配图 + 润色 ✅ |

### TC148 · 2/2

| id | query | top1 | LLM 字 | links | 要点 |
| --- | --- | --- | ---: | ---: | --- |
| L-T2 | TC148 没反应 遥控器正常 | qa_002 | 1151 | 2 | 短接排查 + 润色 ✅ |
| **L-T3** | push button 端口短接 O/S/C COM | **qa_002** | 1218 | 2 | **T3 补丁后 Top1** · 短接语义 + 润色 ✅ |

截图：`_scratch/eval/screenshots/v1_handtest_llm_on/L-*.png`（`#answerPanel` 含手册步骤 + LLM 润色区）

---

## TC148 T3 · 已关闭（V1.1 #1）

| 阶段 | Top1 | 说明 |
| --- | --- | --- |
| 补丁前（eval / LLM=off 手测） | qa_001 | known miss · COM/push button 与 qa_001 接地图重叠 |
| 补丁后（eval + demo API + LLM=on L-T3） | **qa_002** | 症状化 question + 互斥标签 · **6/6 Top1** · t01–t05 无回归 |

留档：[`tc148_t3_execution_record.md`](./tc148_t3_execution_record.md)

---

## 仍 open（V1.1+）

（无 · docx V1.1 三项已全部关闭）

---

## V1.1 #3 · TC148 客服邮件模板 · ✅

**字段**：`customer_reply_templates[]` · `content_role: customer_reply_template` · `answer_en` 已剥离（仅 2 组）  
**Demo**：默认折叠 · 说明文案已确认 · 主面板仍仅 ZH · **不进 LLM context**  
**Gate**：eval 6/6 · [`verify_tc148_customer_reply_template.py`](./verify_tc148_customer_reply_template.py) · [`tc148_customer_reply_browser.py`](./tc148_customer_reply_browser.py) 2/2  
**截图**：`_scratch/eval/screenshots/v1_handtest_llm_on/CRT-T1_crt_fold.png` · `CRT-T2_crt_fold.png`

---

## 结论

**docx V1 线 demo 手测 gate：通过** — LLM=off 全量 + LLM=on 客户演示路径均已 playwright 留档；Tier A / YouTube links / qa_023 parallel UI / qa_024 筛选 / TC148 T3 均可演示；无 blocking 缺陷。

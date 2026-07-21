# docx V1 线 · 结案记录

**日期**：2026-07-05  
**状态**：**✅ 结案**

---

## 闭环摘要

| 阶段 | 内容 | 留档 |
| --- | --- | --- |
| 摸底 | AD5S 148+11 段内容查不到 | [`bl_ext01_gap_inventory.md`](./bl_ext01_gap_inventory.md) |
| 内容找回 | BL-EXT-01 / **01b** Batch1–7 + orphan 11 节 | [`bl_ext01b_batch7_execution_record.md`](./bl_ext01b_batch7_execution_record.md) |
| 检索质量 | V1-02 A3S · V1-08 限位域 · V1-08b 反弹 · **V1-03** AD5S eval 47 条 | [`bl_v1_03_execution_record.md`](./bl_v1_03_execution_record.md) |
| 外链/分支 | **V1-04** links[] + qa_023 parallel | [`bl_v1_04_execution_record.md`](./bl_v1_04_execution_record.md) |
| 双语缺口 | **V1-05** Tier A 12/12 + Tier B audit | [`bl_v1_05_execution_record.md`](./bl_v1_05_execution_record.md) |
| 展示 | **V1-07** thin-ZH EN 补充块 | [`bl_v1_07_gate_verification.md`](./bl_v1_07_gate_verification.md) |
| 收尾 | YouTube links · parallel_test UI · TC148 verify · a16/c12 留档 | [`bl_v1_05_post_close_execution_record.md`](./bl_v1_05_post_close_execution_record.md) |
| 手测 | AD5S 12/12 · TC148 2/2 blocking | [`v1_handtest_log.md`](./v1_handtest_log.md) |

---

## 当前基线（AD5S prod）

| 指标 | 值 |
| --- | ---: |
| eval Top1 | **45/47** |
| eval Top3 | **47/47** |
| 已知 Top1 miss | a16 · c12（confusable · 非 bug） |
| display probe | 14/14 |

详见 [`ad5s_eval_known_misses.md`](./ad5s_eval_known_misses.md) · a16 Top3 沿革：`bl_v1_03` → `[…, qa_024]` · 当前 → `[…, qa_040]`。

---

## Gate #5 · demo 分库

- 三库分库 demo **通过**（2026-07-03 初验 + 2026-07-05 手测复验）
- **merge** 仍 blocked by **BL-RET-01a**（V2 / merge 里程碑前）

---

## V1.1 / 后续 · non-blocking

| 项 | 说明 |
| --- | --- |
| **A3S 内容缺口** | 手测对照 **A3S docx** · **12/18 H1 未入库**（含 §五随意开关门 · §十六风 · §十七保养等）· [`a3s_content_gaps_backlog.md`](./a3s_content_gaps_backlog.md) · scan [`a3s_gap_scan.md`](./a3s_gap_scan.md) |
| ~~demo LLM=on 路径截图~~ | **✅ 2026-07-05** · 7/7 · [`v1_handtest_log.md`](./v1_handtest_log.md) §LLM=on · [`v1_handtest_llm_on_browser.py`](./v1_handtest_llm_on_browser.py) |
| ~~**TC148 T3** 检索排序~~ | **✅ 2026-07-05** · [`tc148_t3_execution_record.md`](./tc148_t3_execution_record.md) |
| ~~**V1.1** TC148 EN 邮件稿~~ | **✅ 2026-07-05** · `customer_reply_templates[]` · demo 折叠区 · LLM 隔离 · [`phase_tc148_customer_reply_template.py`](./phase_tc148_customer_reply_template.py) |

---

## 结论

**docx V1 线结案。** 内容 substantially 入库、质量线到位、高风险改动区手测通过；miss 与 open 项均有 traceable 留档，不 retro-block。

**V2 启动**：[`v1_lessons_for_v2.md`](./v1_lessons_for_v2.md)

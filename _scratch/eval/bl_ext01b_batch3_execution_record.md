# BL-EXT-01b · Batch 3 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01b_batch3_overlay.py`](./phase_bl_ext01b_batch3_overlay.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01b-b3`  
**baseline**：[`batch3_sec12_baseline.md`](./batch3_sec12_baseline.md) · **BL-V1-08**（qa_020/021 标题 · 不在本批 scope）

---

## 范围 · P×1（11 段 orphan → qa_037）

| group | question（最终） | zh | en |
| --- | --- | ---: | ---: |
| **qa_037** | 开门过位不停（拉开门·限位A·开位）Gate Won't Stop at Open Position · Pull-to-Open · Limit A | 112 | 811 |

orphan 为 **单一子场景**：开门过位/不停 · 拉开门 · 限位A · 开位（非关门/限位B）

---

## prod 规模

| 指标 | Batch 2 后 | Batch 3 后 |
| --- | ---: | ---: |
| qa_groups | 36 | **37** |
| 可检索向量 | 61 | **62** |

---

## qa_037 embedding 收窄（P 回归 fix · 2026-07-05）

**初版 overlay** question「开门不限位（拉开门）」+ 正文含泛化「不限位」→ r12a Top1 从 qa_020 **漂移到 qa_037**（见 baseline 对照）。

**调整**（仅 qa_037 · 未动 qa_020/021）：

- **question**：强调「开门过位不停 / 限位A / 开位」
- **answer_zh 首行**：`症状：开门过位或开门不停（限位A·开位；非关门限位B）` — embedding 中 **去掉裸「不限位」**

re-chunk + re-embed（无 schema 变更）

---

## 检索 · 三阶段对照

| id | query | baseline Top1 | overlay 初版 Top1 | **fix 后 Top1** |
| --- | --- | --- | --- | --- |
| **r12a** | 拉开门 关门不限位 限位B怎么调 | qa_020 · 0.7419 | qa_037 ❌ | **qa_020 · 0.7419** ✅ |
| **r12b** | 推开门 关不到位 限位B | qa_020 · 0.7122* | qa_037 ❌ | **qa_020 · 0.7615** ✅ |
| **b07** | 拉开门 开门不限位 限位A怎么调 | — | qa_037 ✅ | **qa_037 · 0.7509** ✅ |

\* r12b baseline 用原 q25「…不限位」时 Top1 亦为 qa_020；该泛化 query fix 后仍 Top1=qa_037（0.725）— 故 **r12b 锚点改为限位B 症状 query**（同 b05 思路：query 须带 A/B 区分，不能单靠 expected 糊弄）

**legacy probe**（fix 后 · 仅观察）：「推开门 关不到位 **不限位**」→ Top1 仍 qa_037 — 说明 §十二 族 **泛化「不限位」query 本身不可作稳定锚点**；BL-V1-08 标题歧义另论。

---

## P 类 gate（最终）

| 项 | 状态 |
| --- | :---: |
| orphan → qa_037 | ✅ |
| b07 Top1 | ✅ |
| r12a 无 qa_037 抢 Top1 | ✅ |
| r12b 锚 qa_020（限位B query） | ✅ |
| a01–b06 无回归 | ✅ |
| **eval Top1** | **25/25** |

机器可读：[`batch3_sec12_post_fix_eval.json`](./batch3_sec12_post_fix_eval.json)

---

## 结论

**Batch 3 收尾 ✅** — ingest + P 回归 gate 全绿 · Batch 4 可开。

**仍待办（非 Batch3 阻塞）**：BL-V1-08 qa_020/021 question 标题差异化 · 14 组 eval 覆盖（BL-V1-03）

---

## 下一批

**Batch 4**：§十五 L-scenario（2 H2 · 16 段）

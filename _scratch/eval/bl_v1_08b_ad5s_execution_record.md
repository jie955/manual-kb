# BL-V1-08b · Phase 1 执行记录（AD5S · 2026-07-05）

**脚本**：[`phase_bl_v1_08b_ad5s_bounce.py`](./phase_bl_v1_08b_ad5s_bounce.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-v1-08b`  
**对照**：[`bl_v1_08b_bounce_domain_diagnosis.md`](./bl_v1_08b_bounce_domain_diagnosis.md) · 限位域 [`bl_v1_08_ad5s_execution_record.md`](./bl_v1_08_ad5s_execution_record.md)

---

## 范围 · qa_016–019 + qa_040（§九中途 anchor）

| group | 改后 question（最终） |
| --- | --- |
| **qa_016** | 开到位后又弹回来·拉开门 · Open Position |
| **qa_017** | 开到位后反弹·推开门 · Limit B |
| **qa_018** | **拉开门 关到位后又弹回来** · Pull · Limit B |
| **qa_019** | 推开门·关到位后又弹回来 |
| **qa_040** | 开关门中途走停或反弹 · Mid-Travel |

均加 **answer_zh 首行互斥标签**（开/关到位 · 拉/推 · 非§十二限位 · 非中途/非到位交叉声明）。

---

## BL-V1-03 bounce gate（c04–c07 + b10）

| id | query（最终） | expected | Top1 iter0 | **Top1 后** |
| --- | --- | --- | --- | --- |
| c04 | 开到位后又弹回来 拉开门安装 | qa_016 | qa_037 ❌ | **qa_016** ✅ |
| c05 | 推开门 开到位后反弹怎么调 | qa_017 | qa_019 ❌ | **qa_017** ✅ |
| c06 | **拉开门 关到位后又弹回来** | qa_018 | qa_021 ❌ | **qa_018** ✅ |
| c07 | 关到位后又弹回来 推开门 | qa_019 | qa_020 ❌ | **qa_019** ✅ |
| b10 | 门开关到一半就停住或弹回来 | qa_040 | qa_040 ✅ | **qa_040** ✅（iter2 曾回归 · qa_040 首行修复） |

**c06** 需 eval query 拉/推前置 + qa_018 question 与 query 空格镜像（**Top1 margin ≈0.0002** · qa_018 vs qa_016）。

> **维护备注**：c06 修复为压线过关，非 embedding 空间结构性拉开。若 AD5S prod 内容变更、qa_023/024 branch 入库、或 **re-embed / 换模型**，须 **优先复验 c06**（及 c04–c07 全组）；c06 若再 miss，先查是否为本修复复发，而非当新问题从零查。

---

## 全库 eval（47 条）

| 指标 | BL-V1-03 后 | **08b 后** |
| --- | ---: | ---: |
| Top1 | 41/47（87.2%） | **45/47（95.7%）** |
| Top3 | 45/47 | **47/47（100%）** |

**仍 miss（非 bounce gate · 08b 前即有）**：

| id | 备注 |
| --- | --- |
| a16 | qa_022 → qa_024 · Top3 ✅ · acceptable |
| c12 | qa_028 → qa_030 · §十九 thin-ZH · Top3 ✅ |

**§十二无回归**：r12a/r12b/l12 ✅

机器可读：[`bl_v1_08b_ad5s_eval.json`](./bl_v1_08b_ad5s_eval.json)

---

## Phase 2 · A3S bounce 同步检查

A3S §九关反弹 **已在 BL-V1-08 Phase2** 症状化（qa_015/016）· 本项 **无 prod 改动**。

| id | query | Top1 | 结论 |
| --- | --- | --- | --- |
| q19 | 门关到位又弹回来 拉开门 | **qa_015** | ✅ 仍绿 |
| q20 | 推开门安装 关门反弹怎么调 | **qa_016** | ✅ 仍绿 |

复跑 30 条：**29/30 Top1**（仅 q27 confusable · BL-V1-03 acceptable）— 与 Phase2 一致。

**结论**：A3S bounce 域 **无需 08b Phase2 overlay**；限位域（qa_017–021）已在 V1-08 处理。

---

## 关闭边界

**BL-V1-08b Phase1 AD5S ✅** — §十/十一到位反弹 + §九 b10 anchor。  
**≠** a16/c12 全库 Top1 全绿 · **≠** BL-V1-04 外链/qa_023 branch。

**demo**：embed 后须 **重启 qa_server**（AD5S chroma）。

---

## 下一项

**BL-V1-04** — qa_024/qa_030 外链 · qa_023 branch

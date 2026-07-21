# BL-V1-08 · Phase 1 执行记录（AD5S · 2026-07-05）

**脚本**：[`phase_bl_v1_08_ad5s_disambiguation.py`](./phase_bl_v1_08_ad5s_disambiguation.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-v1-08`  
**对照诊断**：[`bl_v1_08_limit_domain_diagnosis.md`](./bl_v1_08_limit_domain_diagnosis.md)  
**Phase 2**：A3S qa_015/017–021 — **未启动** · AD5S 关闭 **≠** 限位域全库已解

---

## 范围 · qa_020 / qa_021 / qa_037

| group | 改前 question | 改后 question |
| --- | --- | --- |
| **qa_020** | 推开门安装 | **关门限位不到位·限位B（推/拉开门）** Gate Close Limit · Limit Switch B · Push/Pull |
| **qa_021** | 推开门安装 | **关门限位不到位·限位A外移·磁环排查** Gate Close Limit · Limit A · Magnet/Short Test |
| **qa_037** | 开门过位不停（拉开门·限位A·开位） | **开门不限位/过位（拉开门·限位A·开位）** Gate Open Limit · Pull-to-Open · Limit A Open |

三组均加 **answer_zh 首行症状标签**（开/关 · 限位 A/B · 互斥声明），re-chunk + re-embed bge-m3。

---

## 迭代与回归修复

| 轮次 | 变更 | legacy l12 | b07 |
| --- | --- | --- | --- |
| **1** | 020/021 症状化标题 + 首行 | Top1 **qa_020** ✅（acceptable 含 021）· **非 qa_037** | Top1 **qa_020** ❌（expected qa_037） |
| **2** | qa_037 question 加「开门不限位」· 020/021 首行强化「非开门开位/非限位A」 | 同左 | Top1 **qa_037** ✅ |

---

## 检索 gate（fix 后 · 33 queries）

| id | query | expected | Top1 | 备注 |
| --- | --- | --- | --- | --- |
| **r12a** | 拉开门 关门不限位 限位B怎么调 | qa_020 | **qa_020** | 保持 Batch3 |
| **r12b** | 推开门 关不到位 限位B | qa_020 | **qa_020** | 保持 Batch3 |
| **b07** | 拉开门 开门不限位 限位A怎么调 | qa_037 | **qa_037** | Phase 1 必修 |
| **l12** | 推开门 关不到位 不限位 | qa_021 | **qa_020** | acceptable 含 020/021 · **Top1 非 qa_037** ✅ |

**全库**：**33/33 Top1 · 33/33 Top3**（较 Batch7 后 +1 query l12）

机器可读：[`bl_v1_08_ad5s_eval.json`](./bl_v1_08_ad5s_eval.json)

---

## 结论

**Phase 1 AD5S ✅** — 三方限位域标题/embedding 解耦 · legacy「不限位」关门 query 不再漂到 qa_037 · b07 无回归。

**显式未关**：

- **Phase 2 A3S**（qa_015/017–021）— 同模式、独立 gate
- **l12 Top1=qa_021** — 当前 qa_020 acceptable 通过；非阻塞
- **q27** A3S confusable — BL-V1-03

**demo**：embed 后须 **重启 qa_server**（manifest 刷新）。

---

## 下一项

**BL-V1-08 Phase 2** — A3S 限位域对照诊断 + qa_015–021 / qa_017 空 ZH 处理 · 或穿插 **BL-V1-03** eval 覆盖（按排期 V1 顺序）。

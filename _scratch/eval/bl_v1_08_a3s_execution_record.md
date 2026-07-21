# BL-V1-08 · Phase 2 执行记录（A3S · 2026-07-05）

**脚本**：[`phase_bl_v1_08_a3s_disambiguation.py`](./phase_bl_v1_08_a3s_disambiguation.py)  
**备份**：`_scratch/run-006/qa_groups.json.bak-20260705-bl-v1-08-p2` · `_scratch/run-007/chroma_captioned.bak-20260705-bl-v1-08-p2`  
**对照**：Phase 1 [`bl_v1_08_ad5s_execution_record.md`](./bl_v1_08_ad5s_execution_record.md) · [`bl_v1_08_limit_domain_diagnosis.md`](./bl_v1_08_limit_domain_diagnosis.md)

---

## 范围 · qa_015–021（§九反弹 + §不限位）

| group | 改前 question | 改后 question（最终） |
| --- | --- | --- |
| **qa_015** | 拉开门安装 | **门关到位又弹回来·拉开门** Gate Bounce Back · Pull-to-Open · Limit B |
| **qa_016** | 推开门安装 | **门关到位又弹回来·推开门** Gate Bounce Back · Push-to-Open |
| **qa_017** | 开门不限位（空 ZH） | **开门不限位/一直走（方向未明·泛化）** + 最小 ZH 骨架 |
| **qa_018** | 拉开门安装 | **开门不限位/位置不对·限位A（拉开门·开位）** |
| **qa_019** | 推开门安装 | **开门停不下来/过位·限位B（推开门·开位）** |
| **qa_020** | 拉开门安装 | **关门不限位/不到位·限位B（拉开门·关门位）** |
| **qa_021** | 推开门安装 | **关门不限位/不到位·限位A外移（推开门·关门位）** |

三组 §十二 关门域 + §九 反弹域 + qa_017 泛化入口均加 **answer_zh 首行互斥标签**（同 AD5S Phase 1 方法论）。

**qa_017 空 ZH**：补最小骨架（拉/推分流指引），保留 q21「开门一直走 不限位」expected 入口。

---

## 流水线要点

1. patch `run-006/qa_groups.json` → `chunk_builder` → 仅 **TOUCH 组** 用新 embedding
2. **非 TOUCH 组** 整组保留 pre-patch manifest（含 `answer_zh_translated` / caption）— 避免 q30 类翻译字段丢失回归
3. TOUCH 组 image caption 从 pre-patch manifest 合并
4. re-embed → `run-007/chroma_captioned`

---

## 检索 · BL-V1-02 限位域 gate

| id | query | BL-V1-02 Top1 | **Phase 2 Top1** |
| --- | --- | --- | --- |
| **q19** | 门关到位又弹回来 拉开门 | qa_020 ❌ | **qa_015** ✅ |
| **q22** | 拉开门 开门位置不对 不限位 | qa_017 ❌ | **qa_018** ✅ |
| **q23** | 推开门 开门停不下来 | qa_020 ❌ | **qa_019** ✅ |
| **q24** | 拉开门 关门不限位 限位B怎么调 | qa_017 ❌ | **qa_020** ✅ |
| **q25** | 推开门 关不到位 不限位 | qa_017 ❌ | **qa_021** ✅ |

**限位域 5/5 Top1**（BL-V1-02 中 5 条 miss 全部修复）

---

## 全库 eval（30 条 · v2）

| 指标 | BL-V1-02 前 | **Phase 2 后** |
| --- | ---: | ---: |
| Top1 | 24/30（80%） | **29/30（96.7%）** |
| Top3 | 27/30（90%） | **30/30（100%）** |

**仍 miss（显式非本项）**：

| id | expected | Top1 | 备注 |
| --- | --- | --- | --- |
| **q27** | qa_024 | qa_023 | Top3 ✅ · confusable_pair → **BL-V1-03** acceptable |

**无回归**：q30（qa_028）等非 TOUCH 组经 manifest 保留策略保持绿。

机器可读：[`bl_v1_08_a3s_eval.json`](./bl_v1_08_a3s_eval.json) · 前态 [`bl_v1_08_a3s_pre_eval.json`](./bl_v1_08_a3s_pre_eval.json)

---

## 结论

**BL-V1-08 Phase 2 A3S ✅** — 与 AD5S Phase 1 同构方法论验证有效；**限位/反弹域 A3S 已知缺陷已关闭**（q27 按排期留给 BL-V1-03）。

**BL-V1-08 全项**：Phase 1 AD5S ✅ + Phase 2 A3S ✅ · **限位域双库 gate 完成**（q27 为 confusable 非限位域）。

**demo**：embed 后须 **重启 qa_server**（A3S：`run-007/chroma_captioned` + `run-006/images`）。

---

## 下一项

**BL-V1-03** — AD5S 13 组 eval 覆盖扩展 · q27 acceptable 可选

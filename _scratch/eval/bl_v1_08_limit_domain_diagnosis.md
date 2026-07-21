# BL-V1-08 · 限位/反弹/安装方向语义域检索混淆（A3S + AD5S 对照）

**状态**：Phase 1 ✅ AD5S · Phase 2 ✅ A3S · **限位域双库 gate 完成**（q27 confusable → BL-V1-03）  
**触发**：Batch3 AD5S baseline + legacy probe · BL-V1-02 A3S 30 条全量验证 · 2026-07-05

---

## 模式结论（诊断 · 2026-07-05）

**同一类文档结构问题，非单库偶发。**

门禁排查 docx 在「拉/推 · 开/关 · 限位 A/B · 反弹/不限位」维度上 **重复复用 install_mode 标题**（「拉开门安装 / 推开门安装 / 开门不限位」），embedding 空间天然撞车。  
**任何**类似结构的 troubleshooting 文档（含未来 TC148 若出现安装方向类 H2）应 **预判** 同类检索区分度不足。

| 库 | 撞车组 | 典型 miss / 风险 query |
| --- | --- | --- |
| **AD5S** | qa_020/021 同标题 · + qa_037 开位 | legacy「…不限位」→ qa_037；020/021 互抢 |
| **A3S** | qa_016–021 多组「拉/推开门安装」· qa_017「开门不限位」空 ZH | q19–q25 全落限位域 · **5/5 Top1 miss**（BL-V1-02） |

**修复不必同批、不必同文案** — 两组 prod 分组/段落结构不同；但 **诊断与验收须对照**，AD5S Phase 1 关闭后须显式跑 A3S Phase 2 checklist。

---

## 标题撞车对照

### AD5S（Phase 1 范围）

| group | section | 现 `question` | 子场景 |
| --- | --- | --- | --- |
| qa_020 | §十二 | **推开门安装**（与 021 相同） | 关门不到位 · 限位 B · 拉/推混排 |
| qa_021 | §十二 | **推开门安装** | 关不到位 · 限位 A 外移 · 磁环/短接 |
| qa_037 | §十二 orphan | 开门过位不停（拉开门·限位A·开位）✅ 已收窄 | 开门过位 · 限位 A 开位 |

### A3S（Phase 2 · 同步检查）

| group | section | 现 `question` | 备注 |
| --- | --- | --- | --- |
| qa_015 | §九 关到位反弹 | 拉开门安装 | q19 expected |
| qa_016 | §九 | 推开门安装 | |
| qa_017 | 不限位 | **开门不限位** | answer **空** · q22/q24/q25 常抢 Top1 |
| qa_018 | 不限位 | 拉开门安装 | q22 expected |
| qa_019 | 不限位 | 推开门安装 | q23 expected |
| qa_020 | 不限位 | 拉开门安装 | q24 expected |
| qa_021 | 不限位 | 推开门安装 | q25 expected |

A3S §九反弹 与 §「不限位」**分节**但 query 侧关键词（拉开门/推开门/不限位）高度共享 → 与 AD5S §十–§十二 同构。

---

## 探针快照（bge-m3 · 2026-07-05）

### A3S · run-007 · post BL-V1-08 Phase 2

| query id | query | expected | Top1 | 备注 |
| --- | --- | --- | --- | --- |
| q19 | 门关到位又弹回来 拉开门 | qa_015 | **qa_015** | ✅ |
| q22 | 拉开门 开门位置不对 不限位 | qa_018 | **qa_018** | ✅ |
| q23 | 推开门 开门停不下来 | qa_019 | **qa_019** | ✅ |
| q24 | 拉开门 关门不限位 限位B怎么调 | qa_020 | **qa_020** | ✅ |
| q25 | 推开门 关不到位 不限位 | qa_021 | **qa_021** | ✅ |
| **全库** | 30 条 v2 | — | **29/30 Top1** | q27 → BL-V1-03 · [`bl_v1_08_a3s_eval.json`](./bl_v1_08_a3s_eval.json) |

### AD5S · run-ad5s · post BL-V1-08 Phase 1

| probe | expected | Top1 | 备注 |
| --- | --- | --- | --- |
| legacy l12「推开门 关不到位 不限位」 | qa_021（acceptable 020/021） | **qa_020** | **非 qa_037** ✅ |
| r12a / r12b（限位B） | qa_020 | qa_020 | 保持 |
| b07 | qa_037 | **qa_037** | 迭代 2 修复 |
| **全库 eval** | — | **33/33 Top1** | +l12 gate · [`bl_v1_08_ad5s_eval.json`](./bl_v1_08_ad5s_eval.json) |

---

## Phase 计划

### Phase 1 · AD5S（✅ 2026-07-05）

1. qa_020/021 **question 症状化** + answer_zh **首行标签**（同 qa_037 Batch3 思路） ✅
2. qa_037 与 020/021 **关门域** 进一步解耦 ✅
3. re-chunk + re-embed §十二 相关组 ✅
4. eval：r12a/r12b/b07 + **legacy l12** · **33/33 Top1** — [`bl_v1_08_ad5s_execution_record.md`](./bl_v1_08_ad5s_execution_record.md)

### Phase 2 · A3S（✅ 2026-07-05）

1. 对照上表改 qa_015–021 / qa_017 标题 + 首行标签 ✅
2. qa_017 空 ZH 最小骨架 ✅
3. 重跑 `eval_queries.json` q19–q25 · **5/5 Top1** · 全库 **29/30** — [`bl_v1_08_a3s_execution_record.md`](./bl_v1_08_a3s_execution_record.md)

### 显式非范围（本项）

- q27 qa_023/024 confusable · Top3 已过 → BL-V1-03 acceptable 可选
- TC148 当前无此类组 · **仅作模式预警**

---

## 关联

- [`bl_v1_08_qa020_021_title_disambiguation.md`](./bl_v1_08_qa020_021_title_disambiguation.md) — AD5S 细节与 Batch3 边界
- [`bl_v1_02_a3s_verification.md`](./bl_v1_02_a3s_verification.md)
- [`batch3_sec12_baseline.md`](./batch3_sec12_baseline.md)

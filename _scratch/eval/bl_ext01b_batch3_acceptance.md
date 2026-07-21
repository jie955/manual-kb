# BL-EXT-01b · Batch 3 验收清单（§十二 partial · P×1）

**范围锁定**：Batch3 **仅** 11 段 orphan → qa_037；**不改** qa_020/021 · 标题歧义 → **BL-V1-08** [`bl_v1_08_qa020_021_title_disambiguation.md`](./bl_v1_08_qa020_021_title_disambiguation.md)  
**分类**：[`bl_ext01b_classification.md`](./bl_ext01b_classification.md) · Tag **P**  
**上一批**：[`bl_ext01b_batch2_execution_record.md`](./bl_ext01b_batch2_execution_record.md)

---

## P 类 vs F 类：风险不同

| 类 | 主要风险 | Batch1/2 已验 |
| --- | --- | --- |
| **F** | 内容单薄 · thin-ZH · 检索命中但客户看不懂 | thin 规则 + EN 块 + b01–b06 |
| **P** | **内容归属错位** · 命中旧组但子场景不全，或新组抢旧组 Top1 | **本批重点** |

§十二 不是整节 orphan：prod **已有 2 组**，11 段是 H1 下 **未挂 H2 的子场景**（开门不限位 / 拉开门安装 / 限位 A 外移等）。  
处理时最易出错：

1. **职责边界划错** — orphan 该进新 H2 却并进 qa_020/qa_021，或拆组后段落挂错 install_mode（拉/推）
2. **Top1 漂移** — 新增组/embed 后，原先应命中 **qa_020/qa_021** 的 query 被新组抢走（P 类比 F 类「a01–b04 无回归」更易发生，因同节、同关键词域）

**拆分原则**（classification）：按 orphan 子场景拆 **2–3 H2**（开门不限位 / 拉开门 / 推开门），**勿并入**已有 qa_020/qa_021 正文。

---

## prod 既存组（§十二 · 回归锚点）

| group | question（prod） | 说明 |
| --- | --- | --- |
| **qa_020** | 推开门安装 For push-to-open installation | 含拉/推双场景混排 · 限位 B · 配图 image_019–020 |
| **qa_021** | 推开门安装 For push-to-open installation | 限位 A · 磁环/控制板短接 · 配图 image_021–023 |

> 两组合并 question 标题相同 — 回归须靠 **query 语义**（拉/推 · 开/关 · 限位 A/B）区分，不能只看 group title。

---

## 验收项（Batch 3 完成后 · 全部须过）

### A. 新组正向（同 F 批）

- [ ] overlay 后 orphan **11 段**全部进入预期新 group（qa_037+，具体 ID 脚本定）
- [ ] `eval_queries_ad5s.json` 新增 **b07/b08**（或按实际拆组数 b07–b09）· 各新组 **Top1**
- [ ] 职责边界人工 spot-check：新组 answer 不含 qa_020/021 已覆盖的整段 duplicate；旧组未吞 orphan 独有子场景

### B. §十二 既存组回归（P 类必做 · 与 b07 同等重要）

**覆盖盲区**：qa_020/qa_021 在 Batch3 前 **无 eval**（全库 q24/q25 未迁入 AD5S 子集）— 见 [`batch3_sec12_baseline.md`](./batch3_sec12_baseline.md) · AD5S 组覆盖 **20/36→22/36**。

**r12a/r12b 已写入** `eval_queries_ad5s.json` · **overlay 前 baseline 已快照**（2026-07-05）：

| reg id | query | expected | baseline Top1 | score |
| --- | --- | --- | --- | ---: |
| **r12a** | 拉开门 关门不限位 限位B怎么调 | qa_020 | **qa_020** ✅ | 0.7419 |
| **r12b** | 推开门 关不到位 不限位 | qa_021 | **qa_020** ⚠️ Top2=qa_021 | 0.7122 |

**overlay 后对照**（与 baseline 比，非与「理想期望」比）：

- r12a：Top1 仍为 qa_020；score/Top3 记录入 batch3 执行记录
- r12b：Top1 **不得**变为新组；维持 qa_020 或 **改善**为 qa_021 均可；若 Top1→新组 → 失败
- 全库 a01–b06 + r12a：Top1 **不低于** baseline 23/24

~~开工前须从全库设计迁入~~ ✅ 已完成

### C. 交叉混淆（P 类 spot-check）

- [ ] b07 类 query（新组 · 如「开门不限位」）→ **新 group Top1**，**非** qa_020/021
- [ ] r12a/r12b → **仍** qa_020/021（与上条同时成立）
- [ ] a13（qa_014 单臂方向）· b05（qa_035 完全不工作）· batch1/2 全套 → **无回归**（同每批）

### D. 运维（同 BL-V1-07）

- [ ] embed 后 **kill 旧 qa_server → 重启 → `/api/health` + 抽样新/旧组 content 非空**
- [ ] （下批固化）写入 [`demo_checklist.md`](./demo_checklist.md) 或 overlay 脚本说明

---

## 开工前检查

- [x] r12a/r12b 已写入 `eval_queries_ad5s.json` · baseline → [`batch3_sec12_baseline.md`](./batch3_sec12_baseline.md)
- [ ] 脚本计划：单独 `phase_bl_ext01b_batch3_overlay.py` · stamp `bl-ext01b-b3` · **不与 F 批混跑**

---

## 参考

- gap inventory §十二 partial：[`bl_ext01_gap_inventory.md`](./bl_ext01_gap_inventory.md) §1.3 B 类
- 全库 eval 设计 q24/q25：[`eval_queries.json`](../eval_queries.json) · [`coverage_table.md`](./coverage_table.md)

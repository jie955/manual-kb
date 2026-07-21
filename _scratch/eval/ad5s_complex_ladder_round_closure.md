# AD5S 复杂档 schema → prod 本轮收尾全貌

**日期**：2026-07-05 · **状态**：**正式关闭 ✅**  
**下一批入口**：**BL-EXT-01**（[`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §14 · [`docs/排期.md`](../../docs/排期.md) D 区）  
**事实源**：[`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) + [`docs/排期.md`](../../docs/排期.md)（不依赖聊天记录）

---

## 1. 当前 prod 态（2026-07-05）

| 维度 | 状态 |
| --- | --- |
| **库** | `_scratch/run-ad5s/chroma_captioned`（**52 vectors**） |
| **ladder 组** | **2**：`qa_024`（branch + 筛选）、`qa_008`（4 步 + ERM12 末环） |
| **flat 组** | **25**（overlay 前旧 extract，**interim 暂态**） |
| **检索** | eval **15/15**（阶段 1+2 各跑一轮） |
| **浏览器** | D2b/A8-prod（ladder 新组）+ M1–M3-prod（混合态旧组重签） |
| **demo** | `http://127.0.0.1:8765/` · `python qa_server.py --chroma-dir _scratch/run-ad5s/chroma_captioned --images-dir _scratch/run-ad5s/images --port 8765` |

---

## 2. 本轮完整链路（设计 → prod）

```mermaid
flowchart LR
  A[截图发现问题] --> B[全文 pandoc 核查]
  B --> C[condition 维度扫描]
  C --> D[schema 定稿<br/>ladder+branches+applies_when_any]
  D --> E[qa_008 / qa_024 extract]
  E --> F[单测 branch_utils]
  F --> G[pilot dry-ladder :8766]
  G --> H[截图暴露筛选/配图 bug]
  H --> I[镜像语义修复 4→2 branch]
  I --> J[四项验收脚本]
  J --> K[prod 收窄到 2 组 overlay]
  K --> L[混合态 M1–M3 浏览器]
  L --> M[文档定性收尾 §14]
```

| 阶段 | 产出 | 路径 |
| --- | --- | --- |
| Schema | `troubleshooting_ladder`、`branches[]`、`applies_when_any` | [`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) §3–§5 |
| 代码 | branch 筛选、⇄ 标签、配图过滤、`hasLadder` 回退 | `branch_utils.py` · `demo/index.html` |
| 测试 | 9/9 单元测试 + 四项自动化 | `tests/test_branch_utils.py` · [`verify_qa_024_acceptance.py`](./verify_qa_024_acceptance.py) |
| 切换 | 外科 overlay 两阶段 | [`phase1_overlay_qa024.py`](./phase1_overlay_qa024.py) · [`phase2_overlay_qa008.py`](./phase2_overlay_qa008.py) |
| 混合回归 | Playwright headless 3/3 | [`mixed_prod_browser_regression.py`](./mixed_prod_browser_regression.py) |
| 闭环记录 | pilot + prod 签字 | [`qa_024_branch_closure.md`](./qa_024_branch_closure.md) · [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §12–15 |

---

## 3. 关键产出 vs 刻意没做

### 3.1 已完成

- **qa_024**：4 branch → **2 branch**（`applies_when_any` OR 镜像路径）；branch 级配图；prod D2b ✅
- **qa_008**：ladder 4 步 + `is_last_resort` 末环；prod A8 ✅
- **25 组 flat**：行为与 overlay 前 prod 一致（`hasLadder` 回退）；M1–M3 浏览器重签 ✅

### 3.2 刻意没做（及原因）

| 未做项 | 原因 |
| --- | --- |
| **全库 27 组 re-extract** | 会静默 `attach_troubleshooting_ladder` **~11 组** + 全组 BL-V1-06 协商剥离；**大部分无浏览器验收** |
| **qa_023 复杂档 prod overlay** | 未走 qa_024 同级 pipeline（pilot → 四项 → 浏览器 → overlay） |
| **BL-EXT-01** | extract 缺口独立 backlog；下一批首项 |
| **BL-V1-05 / D2 §十四修复** | 仅定性记录；D2 维持 ⚠️re-review |
| **三库 merge（BL-RET-01a）** | Gate #5 已结论：分库 demo 通过即可 |

详见 [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §4 方案 B · §8。

---

## 4. 验收记录时效性

> **原则**：不同 prod 态的浏览器记录**不可混用**为签字依据。

| 记录批次 | 适用场景 | **不适用**于 |
| --- | --- | --- |
| **Gate #5 D1/D3/D4** | overlay **前**旧 prod flat 组 | 混合 prod 签字 |
| **D2b / A8-prod** | overlay **后** ladder 新组（qa_024 / qa_008） | — |
| **M1–M3-prod** | overlay **后**混合 prod 旧组 flat | — |
| **D2 ⚠️re-review** | qa_022 双向异构定性 | **勿**当 ✅ 数值/公式已验 |

记录位置：[`demo_qa_log.md`](./demo_qa_log.md) · 混合态定义 [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) **§15**

---

## 5. 下一批优先级（§14 · 按此开，不必重排）

| 序 | ID | 内容 | 入口 |
| ---: | --- | --- | --- |
| 1 | **BL-EXT-01** | extract 覆盖缺口：§十九保养无组、50Ω/1152 公式、URL 21→8 | [`ad5s_full_doc_review.md`](./ad5s_full_doc_review.md) **§五–§六** · [`docs/排期.md`](../../docs/排期.md) D 区 |
| 2 | **BL-V1-04 简单档** | qa_003 / qa_010 链接白名单（TC148 简单档已验） | [`docs/排期.md`](../../docs/排期.md) **§ BL-V1-04** |
| 3 | **qa_023 复杂档** | 同 qa_024 管线：pilot → 四项 → 外科 overlay；V1-06 协商过滤已有基础 | [`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) §复杂档 · [`ad5s_full_doc_review.md`](./ad5s_full_doc_review.md) §一 |

**切换原则不变**：潜在 auto-ladder 组**不批量切**；每组独立 pilot + 浏览器验收后再 overlay（[`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §4 · §14）。

**BL-EXT-01 开批条件**（有实质进展再续）：pandoc 与 `qa_groups` 缺口表钉死 · §十九保养组方案 · 50Ω/1152 入库路径 · 21→8 链接差集与归属组明确。

---

## 6. 仍开着、本轮未动的 backlog

| ID | 简述 | 备注 |
| --- | --- | --- |
| **BL-V1-05** | TC148 结构性 ZH/EN 非互译；AD5S 双向异构（§十四） | 目前只有定性，无修复；D2 ⚠️re-review |
| **qa_022 双向异构** | 未处理 | [`demo_qa_log.md`](./demo_qa_log.md) D2 已标 re-review，勿当 ✅ |
| **BL-V1-04 AD5S 简单档** | qa_003/010 链接白名单 | 排在 BL-EXT-01 之后 |
| **BL-RET-01a** | 多库 merge 前 `doc_type` + `search()` 过滤 | P0 blocker；PDF 线 + docx 线都需要 |
| **BL-PDF-02** | PDF 线配图 `image_id` / file basename 统一 | 与 re-embed 独立一轮 |
| **~11 auto-ladder 组** | 全量 re-extract 会触发 | **禁止批量切 prod** |

其他已在排期 D 区登记：BL-RET-01b、BL-V1-03 eval 补全、52 页 PDF 扩量等 → [`docs/排期.md`](../../docs/排期.md)。

---

## 7. 关键文档锚点核对（2026-07-05）

| 引用 | 锚点 | 核实 |
| --- | --- | --- |
| 切换计划 · 技术约束 | [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) **§3** | ✅ embed 无增量 · 25 flat interim |
| 切换计划 · 下一批 | 同上 **§14** | ✅ BL-EXT-01 → V1-04 简单档 → qa_023 |
| 切换计划 · 混合回归 | 同上 **§15** | ✅ M1–M3 · 3/3 PASS · Gate #5 不适用 |
| 浏览器记录 | [`demo_qa_log.md`](./demo_qa_log.md) D2b-prod / A8-prod / M1–M3-prod | ✅ 行 25–30 |
| qa_024 闭环 | [`qa_024_branch_closure.md`](./qa_024_branch_closure.md) §4.2–4.3 | ✅ pilot + prod |
| extract 缺口 | [`ad5s_full_doc_review.md`](./ad5s_full_doc_review.md) **§五**（保养）· **§六**（BL-EXT-01） | ✅ |
| schema 复杂档 | [`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) §4–§5 · §9 | ✅ |
| 排期 backlog | [`docs/排期.md`](../../docs/排期.md) 总表 L56 · D 区 L205 · BL-V1-04 L316–341 | ✅ |

---

## 8. 关闭声明

本轮 **AD5S 复杂档 schema → pilot → 2 组 prod overlay → 混合态回归 → 文档定性** 已全部落地。

**prod 停在**：2 ladder + 25 flat interim。  
**下一批**：BL-EXT-01；有实质进展再开。  
**勿再追**：本轮无待办项。

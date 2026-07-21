# Architecture Decision Records（ADR）

本目录存放 manual-kb 的架构决策记录。编号与状态以本文件为单一事实源。

## 索引

| 编号 | 标题 | 状态 | 日期 |
| --- | --- | --- | --- |
| [0001](./0001-phase2-retrieval-representation.md) | Phase 2：Retrieval Representation & Retrieval Pipeline | Accepted（决策冻结 · enrich 机制仍有效） | 2026-07-07 |
| [0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md) | English CS：跨语言检索与本地化生成 | **Superseded by 0003**（客户路径 · 见文首墓碑） | 2026-07-07 |
| [0003](./0003-english-cs-english-authoritative-pipeline.md) | English CS：英文权威检索与生成 | **Proposed**（Phase 1b · EN-index 默认 · Caption 回灌 DONE） | 2026-07-07（刷新 2026-07-08） |
| [0004](./0004-semantic-judge-layer-for-cs-eval-and-routing.md) | Semantic Judge 层：CS 评测与路由语义判断 | **Proposed**（Phase 2a eval · 2b runtime 可选 · 不在 Round 1e 内实施） | 2026-07-10 |
| [组件化重构](./企业%20RAG%20邮件助手组件化重构方案.md) | 企业 RAG 邮件助手组件化（领域包 / Workflow / EvalPack） | **Phase 1 架构 Accepted** · 质量门禁 **未关闭**（holdout 1/5 · 须人工 xlsx）· 2026-07-10 |

## 约定

- **编号**：四位递增 `NNNN-short-title.md`，不跳号、不重用已退役编号。
- **状态**：`Proposed` → `Accepted` → `Deprecated` / `Superseded by NNNN`。
- **只放决策正文**：排期与流水线状态见 [`docs/排期.md`](../排期.md)；实验数据见 `_scratch/` 各 run 目录。
- **English CS POC**：[**Implementation Plan v1.3**](../../_scratch/eval/cs_en_implementation_plan.md) · [**ADR-0003**](./0003-english-cs-english-authoritative-pipeline.md) · [**ADR-0004**](./0004-semantic-judge-layer-for-cs-eval-and-routing.md)（Semantic Judge · Proposed）· [**甲方验收标准**](../../_scratch/eval/cs_client_requirement_standard.md)（叶天洲 §一 · 殷主管 §二 MVP）· [`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md)（勾选/留档）· [ADR-0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md)（Superseded · 客户路径）
- **ADR-0001 收口（2026-07-07）**：决策 1–7 冻结；`vlm_batch` E0/E1/E2 有数据（6/10→10/10）。全量 `vlm_a3s_full` 7/10、`representation/` 模块、MRR/nDCG 见 ADR 正文「验收与实施状态」与 [`docs/排期.md`](../排期.md)（BL-RET-01a/b）。
## 相关文档

- [排期 · ingest 与 v2 状态](../排期.md)（含 **BL-RET-01a/b**、§6b 单库排序、§8 p1/p3、§9 eval 覆盖）
- [VLM 小批量实验](../../_scratch/vlm_batch/README.md)
- [VLM A3S 全量](../../_scratch/vlm_a3s_full/README.md)

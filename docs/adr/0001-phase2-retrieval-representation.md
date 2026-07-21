# ADR-0001 · Phase 2：Retrieval Representation & Retrieval Pipeline

**状态**：Accepted（决策冻结 · 小批量门禁通过 · 2026-07-07）  
**日期**：2026-07-02（决策）· 2026-07-07（验收收口）  
**前置**：VLM 小批量 13 页（54 块 / 41 可检索）；baseline 探针 **6/10 Top1** → enriched **10/10**（[`ab_summary.json`](../../_scratch/vlm_batch/eval/ab_summary.json)）  
**关联**：[`docs/排期.md`](../排期.md) · [`_scratch/vlm_batch/README.md`](../../_scratch/vlm_batch/README.md) · [ADR-0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md)（Superseded · 客户路径）· [**ADR-0003**](./0003-english-cs-english-authoritative-pipeline.md)（**English CS 客户路径 · 语言权威与 Gate**）· **全量探针** [`vlm_a3s_full`](../../_scratch/vlm_a3s_full/README.md)

> **English CS 分工（2026-07-07）**：客户路径的 **Primary authoritative source、Gate R/K/G/S、E2E DoD** 见 [**ADR-0003**](./0003-english-cs-english-authoritative-pipeline.md)。**本 ADR 决策 2（Semantic Expansion / offline enrich）** 仍为 EN representation 补写的**机制层**；工程师中文路径与通用 Retrieval Pipeline **仍以本 ADR 为准**。

---

## 验收与实施状态（2026-07-07）

**本 ADR 冻结的是架构决策与实验结论**；工程落地分阶段，排期与 backlog 见 [`docs/排期.md`](../排期.md)（**BL-RET-01a/b**、**BL-PDF-04**）。

| 范围 | 状态 | 说明 |
| --- | --- | --- |
| **决策 1–7**（原则） | ✅ Accepted | `vlm_batch` A/B 证实瓶颈在 Representation，非 embedding 模型 |
| **小批量门禁**（`vlm_batch` 10 条探针） | ✅ 10/10 | `manual_embed_enrich.py` + 重 embed；vector / hybrid 0.6 均满 |
| **全量单库**（`vlm_a3s_full` 195 块） | ⚠️ 7/10 | 扩库排序竞争；待 **BL-PDF-04** 语料钉死后 **BL-RET-01b** |
| **Representation Builder**（`representation/`） | ⏳ 未建 | 过渡实现：`manual_embed_enrich.py`（见决策 5 修订） |
| **Query Understanding + metadata 前置** | ⏳ 未做 | 单库 7/10 miss 不能靠 `doc_type` 过滤解决；**BL-RET-01a** 仅跨库 merge 前 |
| **Benchmark 矩阵 E0–E3** | ⚠️ 部分 | E0/E1/E2 有数据；MRR/nDCG 与 E3 单独留档未做（enriched 下非 batch 瓶颈） |

**与 English CS（[ADR-0003](./0003-english-cs-english-authoritative-pipeline.md)）**：客户路径的 symptom 级 **EN** 关键词 enrich **复用本 ADR 决策 2**（离线 `embedding_text` / representation enrich，不另建轮子）。**语言权威、索引主字段、生成 context、Gate 与 DoD** 不在此重复 — 见 ADR-0003。历史 cross-ref [ADR-0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md) 之跨语中文索引路径 **已 Superseded**。

---

## 背景

完整阅读 VLM 小批量 review 后的收敛结论：

> **这版 review 已不仅是普通复盘，可作为下一阶段 ADR 的基础。整体判断赞同 90% 以上，以下是对 review 的进一步收敛与补充。**

当前代码基线（2026-07-07）：

- Document Understanding：`pdf_vlm_parser.py` → `manual_chunk_adapter.py` ✅（batch 13 页 + full 46 页均已跑通）
- Knowledge Representation：各 ingest 线仍维护 `embedding_text`；manual 线已有 **`manual_embed_enrich.py` 过渡 enrich** ⚠️
- Retrieval Engineering：`retrieval_engine.py` 已有 vector / hybrid / rerank；**batch 探针 10/10**；**无 Query Understanding、无前置 metadata constraint**（跨库见 BL-RET-01a）⏳

---

## 核心结论：三层 Pipeline 与瓶颈定位

```
PDF
 ↓
① Document Understanding（VLM）
 ↓
② Knowledge Representation（Chunk / Representation）
 ↓
③ Retrieval Engineering
```

| 层 | 状态 | 说明 |
| --- | --- | --- |
| Document Understanding | ✅ 基本完成 | batch 13/13；full 46 页 VLM + 195 向量 |
| Knowledge Representation | ⚠️ POC 已证、工程未统一 | enrich 有效（6/10→10/10）；尚无 `representation/` 模块 |
| Retrieval Engineering | ⚠️ 分场景 | batch **10/10**；full **7/10**；端子/电源/安装步语义竞争仍在全量库 |

**决策前提（冻结）**：除非发现新的解析错误，不再优先投入 OCR / VLM / chunk split。下一阶段重心转向 Representation 与 Retrieval Pipeline。

---

## 决策 1：问题不在 Embedding，而在 Representation

常见误判：「embedding 模型不够好」。

实际链路：

```
Chunk → [Representation Text] → Embedding → Vector Search
              ↑
         真正需要优化的层
```

**命名收敛**：不再使用 `embedding_text` 作为概念名（字段名可渐进迁移），改称为：

- **Semantic Representation**，或
- **Retrieval Representation**

含义：如何向向量模型（及 BM25 / Reranker）描述这一块知识——不是简单字符串拼接。

---

## 决策 2：Alias → Knowledge Expansion（语义扩展）

Alias 只解决同义词；Retrieval 还需要补 **用户表达**。

示例：

| 手册代号 | 扩展（非 alias 列表） |
| --- | --- |
| PHOTO | PHOTO terminal · Photocell · Photo Eye · Infrared Safety Sensor · Obstacle Detection · Control Board Terminal |
| BAT | BAT terminal · Battery · Backup Battery · Battery Input · Emergency Power |

用户问「断电备用电池接哪里？」——query 中无 `BAT`，但 `Backup Battery → BAT` 应能命中。

这是 **Semantic Expansion**，不是 flat alias table。

---

## 决策 3：Metadata Filter 前置，非后处理

不推荐：

```
Vector → Top20 → Metadata Filter   # Top1 可能已在过滤前丢失
```

推荐：

```
Query → Intent / Entity 识别 → Metadata Constraint → Vector / Hybrid Search
```

示例：「PHOTO 端子」→ intent=`Terminal Lookup` → constraint `chapter=Terminal` → search。

现有 `retrieval_engine.py` 支持 hybrid/rerank，但 metadata 约束尚未进入 query 链路。

---

## 决策 4：补齐 Retrieval Pipeline

当前实际路径：

```
Query → Embedding → Search
```

目标企业级路径：

```
Query
 ↓
Query Understanding（intent / entity / constraint / target）
 ↓
Query Expansion
 ↓
Metadata Constraint
 ↓
Hybrid Retrieval（vector + BM25，已有基础设施）
 ↓
Rerank（已有 bge-reranker-v2-m3）
 ↓
LLM（可选，产品口径仍以 Top1 原文步骤为准）
```

**最大缺口**：Query Understanding。

示例 query「PHOTO 端子接光电传感器」可解构为：

| 维度 | 值 |
| --- | --- |
| Intent | Terminal Lookup |
| Entity | PHOTO |
| Constraint | Control Board |
| Target | Terminal Function |

---

## 决策 5：不做长期分叉 enrich 脚本，做 Representation Builder

**目标**：反对按 ingest 源各写长期并行的 enrich 脚本（`manual_embed_enrich.py` → 未来 `docx_repr` / `faq_repr` 永久分叉）。

**修订（2026-07-07）**：`manual_embed_enrich.py` 作为 **POC 过渡实现** 已验证决策 1–2，允许保留至 `representation/` 模块落地；新 enrich 逻辑须向统一 `build_representation()` 收敛，**ADR-0002** symptom enrich 与之共用机制。

**建议**统一抽象：

```
representation/
    manual_repr.py
    faq_repr.py      # 对应 troubleshooting docx 线
    docx_repr.py     # 通用 fallback
```

统一接口：

```python
build_representation(chunk) -> {
    semantic_text: str,
    keywords: list[str],
    entities: list[str],
    expansions: list[str],   # 原 alias 升级
    metadata: dict,
}
```

Embedding、BM25、Reranker **共用同一 representation 输出**。

---

## 决策 6：Representation 不完全依赖 VLM 输出

引入独立 **Post-Processor（Semantic Enricher）**：

```
VLM Output
      │
      ▼
Semantic Enricher
      ├── Chapter Context
      ├── Terminology Expansion
      ├── Entity Extraction
      ├── Canonical Keywords
      ├── Cross-reference Injection
      ▼
Representation
```

收益：更换 VLM（Gemini / GPT-4o / Qwen-VL）或 Embedding（BGE / NV-Embed / E5）时，知识表示层保持稳定。

---

## 决策 7：Benchmark 驱动，非「感觉变好了」

实验矩阵（扩展现有 `eval_run.py` / `experiment_suite.py`）：

| Experiment | Representation | Retrieval | Rerank | Top1 | Top3 | MRR | nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 | baseline（VLM `embedding_text`） | vector | × | **6/10** | — | — | — |
| E1 | enriched（`manual_embed_enrich`） | vector | × | **10/10** | — | — | — |
| E2 | enriched | hybrid 0.6 | × | **10/10** | — | — | — |
| E3 | enriched | hybrid 0.6 | ✓ | — | — | — | — |

数据来源：[`_scratch/vlm_batch/eval/ab_summary.json`](../../_scratch/vlm_batch/eval/ab_summary.json) · 探针脚本 [`probe_topk_misses.py`](../../_scratch/vlm_batch/probe_topk_misses.py)。E3 未单独留档：enriched 下 vector/hybrid 均已满，rerank 非小批量门禁瓶颈。

**工作流**（仍有效）：任何 Representation 改动 → 跑 Benchmark → 数据决策 → 更新排期 / 本 ADR 实施表。

探针集：

- A3S troubleshooting：`eval_queries.json`（18 query，**18/18**）
- A3S manual v2 · **batch**：`_scratch/vlm_batch/` 10 条口语 query（**10/10** enriched）
- A3S manual v2 · **full**：`_scratch/vlm_a3s_full/` 同 10 条（**7/10** hybrid 0.6，2026-07-03 诊断）

---

## Phase 2 四模块拆分

| # | 模块 | 职责 | 实施状态（2026-07-07） |
| --- | --- | --- | --- |
| 1 | **Representation Builder** | 统一 `build_representation(chunk)`，替代各线分散的 `embedding_text` 拼接 | ⏳ 未建；过渡：`manual_embed_enrich.py` |
| 2 | **Terminology Knowledge Base** | 术语 / 缩写 / 语义扩展（PHOTO、BAT、DLMT 等） | ⚠️ 硬编码于 enrich 脚本；待抽成 KB |
| 3 | **Retrieval Pipeline** | Query Understanding → Metadata Constraint → Hybrid → Rerank | ⚠️ hybrid/rerank 已有；QU/metadata 前置 ⏳ |
| 4 | **Evaluation Benchmark** | 固定探针集 + Top1/Top3/MRR/nDCG，全改动必过门禁 | ⚠️ Top1 已用于 batch/full；MRR/nDCG ⏳ |

---

## 与当前代码的映射

| 现状 | Phase 2 演进 |
| --- | --- |
| `pdf_vlm_parser.py` prompt 内嵌 embedding_text 规则 | VLM 只产出结构化 chunk；representation 由 enricher 负责 |
| `chunk_builder.build_embedding_text()` | 迁入 `representation/faq_repr.py` |
| `caption_images.py --enrich-embedding` | 改为 enricher 的一个 enrich 步骤 |
| `embed_ingest_local.py` 读 `embedding_text` | 读 `representation.semantic_text`（兼容期双字段） |
| `retrieval_engine.py` hybrid/rerank | 增加 query understanding + metadata pre-filter |
| `eval_run.py` Top1/Top3 | 扩展 MRR/nDCG + manual 探针集 |

---

## 暂不做的（Explicit Non-Goals）

- 为 batch 10/10 再换 embedding 模型（representation 增益已证；模型对比非当前 P0）
- LLM 生成式回答（产品口径仍为 Top1 原文步骤；生成侧见 ADR-0002）
- 为 English CS POC 新建独立 Language Adapter enrich 层（symptom 扩展走本 ADR 离线 enrich）

---

## 开放问题（部分已收敛）

| # | 问题 | 状态（2026-07-07） |
| --- | --- | --- |
| 1 | Terminology KB 人工维护 vs 半自动从 `structured.rows` 抽取？ | **暂缓**：POC 人工维护于 `manual_embed_enrich.py`；full 达标后再抽 KB |
| 2 | Query Understanding 用规则 / 小模型 / LLM？ | **暂缓**：单库 full 7/10 优先 enrich + 排序（BL-RET-01b），非 QU |
| 3 | `doc_type` + `page_range` + `chapter` 哪些 metadata 进 Chroma filter？ | **部分收敛**：单库 miss 同 doc_type，filter 无效；**BL-RET-01a** 服务跨库 merge |
| 4 | troubleshooting 与 manual 合并检索的 cross-reference 优先级？ | **未启动**：blocked by BL-RET-01a · V2 merge |

---

## 结论

**决策层（Accepted）**：瓶颈在 Representation；Semantic Expansion + 离线 enrich 可验证地提升 Top1；Retrieval Pipeline 目标形态（QU → metadata → hybrid → rerank）仍成立。

**工程层（进行中）**：

> 小批量门禁已过；全量单库与 `representation/` 统一模块、跨库 metadata（BL-RET-01a）为下一刀。

不是「继续优化 VLM」，而是在 Document Understanding 过线的前提下，建立可验证、可复用的表示层与检索链路——支撑全量多型号、多 ingest 源的统一演进。

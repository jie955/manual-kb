# English Customer Support POC · Implementation Plan v1.3

**性质**：POC **工程交付计划**（Implementation）— 展开 [ADR-0003](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md)，**不替代**架构 ADR 与 [甲方验收标准](./cs_client_requirement_standard.md)  
**日期**：2026-07-07（v1.3：评审纳入 · 部署前置 · 甲方协作可选）  
**上一版**：v1.2 — Phase 0 拆为 0.0–0.3 · Context Builder 架构边界  
**关联**：[执行清单 · 勾选/留档](./cs_en_poc_execution.md) · [DoD 缺口](./cs_en_adr_dod_gap.md) · [发版门禁包](./cs_client_feedback_pack.md)

> **ADR 级最高约束**  
> *Internal reasoning language is an implementation detail; customer-facing language is a product contract.*  
> 内部可用中文索引/工程师模式；**客户可见**路径须英文进 → 英文出，且不得暴露中文检索/中间表示。

---

## 文档治理（固定分工 · 禁止互拷）

```text
ADR-0003
        │
        ▼
Implementation Plan（本文件）
        │
        ▼
Execution Checklist
```

| 文档 | 职责 | Source of Truth |
| --- | --- | :---: |
| [**ADR-0003**](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md) | 架构决策、原则、Gate **定义** | **Architecture SoR** |
| **Implementation Plan**（本文件） | 实施计划、阶段、DoD、风险、Owner | **Execution SoR** |
| [**cs_en_poc_execution.md**](./cs_en_poc_execution.md) | 每日执行、勾选、产物链接、状态跟踪 | **否**（Tracking Artifact） |
| [**cs_client_requirement_standard.md**](./cs_client_requirement_standard.md) | 甲方验收标准 | **Business SoR** |

**维护规则**：修改一处只改对应 SoR；Tracking 文档 **链接** 计划与 ADR，**不复制** Phase 正文或验收条款。

**物理实现**：索引形态（三库分库 / 双字段单库 / 未来 Milvus 等）由 **ADR-0003** 决定；本计划只交付 **English Retrieval Index** 能力，不绑定具体目录名或向量库产品。

**生成路径架构边界**（Phase 0 起固定）：

```text
generate_answer.py          context_builder.py（或 context/）
Retriever → Context → LLM → Reply     ↑ 唯一 Context Policy 入口
                                      locale · response_mode · audience · engineer_mode
```

- **Context Policy**（哪些字段进 LLM reference block）→ **仅** Context Builder  
- **Prompt Policy**（选哪条 system prompt）→ Generator / `prompts` 模块  
- **禁止**在 `generate_answer()` 内按 locale / mode 拼装 `content_zh` / `content_en`  
- **UI 展示**（`display_content_utils`）与 **LLM context** 分离 — Phase 0 只动后者

---

# 0. Objective（为什么做）

## Goal

验证系统能够完成 **真实英文客服闭环**：

```text
English Customer Email
        │
        ▼
English Retrieval Index
        │
        ▼
Grounded Reasoning
        │
        ▼
Professional English Reply
```

本阶段 **不是** 构建多语言知识库或 Workflow 产品。

> 验证英文客服场景能否完成 **End-to-End Grounded Reply**，且甲方 **感知不到** 中文中间层。

## Success Criteria（感知层 · Business）

甲方应看到：

```text
English Email → English Reply
```

**不应**看到：

```text
English → Chinese Retrieval → Chinese Answer →（再译成英文）
```

| # | 标准 |
| ---: | --- |
| SC-1 | 客服默认路径 UI + 回信 **无可感知中文** |
| SC-2 | **Customer cannot perceive Chinese reasoning** |
| SC-3 | 内部 Gate G/S 达标；**可选**（部署后）殷主管盲测 **≥ 10** 封认可 Grounding **与** Style |

工程门禁见 **§12 Acceptance（Gate R → K → G → S）**。  
**甲方现场协作**（殷主管 / 叶天洲）见 **§1.1 部署与甲方协作** — **非** POC 工程 DoD 硬前置，须 **平台/服务器部署就绪** 后方可安排。

---

# 1. Scope（做什么 / 不做什么）

## In Scope

| 项 | 说明 |
| --- | --- |
| English Customer Email | 27 场景 + 176 query（[`cs_email_query_map.json`](./cs_email_query_map.json)） |
| **殷主管 MVP 范围** | 两系列 A3S/A5S/A8S + AD5S/AD8S · 排查 + 说明书 + 产品链接 — 见 [验收标准 §二](./cs_client_requirement_standard.md#二殷主管一线需求第一阶段-mvp--业务真源) · [进度表](./client_mvp_two_series_progress.md) |
| **English Retrieval Index** | EN-primary 表达 + 客户路径检索切换（实现见 ADR-0003） |
| English Grounded Reply | `locale=en` · `response_mode=cs_email` |
| Style exemplars | Reference + `reply-principles-and-tips.md`（**不进** embedding） |
| Human / Gate 评测 | Gate G（Grounding）+ Gate S（Style）分列 |
| E2E Demo | `--unified-cs` · 隐藏中文 chunk / 型号库下拉 |
| 内部 Gate 填包 | 门禁包 G/S 分列 · `run_cs_e2e_gate` 留档 |
| **可选** · 甲方协作 | 部署后：术语真源 · Pilot 映射 · 殷主管/叶天洲现场评审（见 §1.1） |

## 1.1 · 部署与甲方协作

**干系人**：叶天洲 = 最终决策方；**殷主管 = 一线业务方 · 第一验收人 · 首选配合测试**。工程 **第一优先级** 满足 [验收标准 §二 MVP](./cs_client_requirement_standard.md#二殷主管一线需求第一阶段-mvp--业务真源)，再进入叶天洲汇报链。

**原则**：POC 工程 DoD 以 **内部 Gate R/K/G/S + 门禁包（探针诊断）+ 真邮四维 §2.3（发链判据）** 为准；发测试链接前须内部自验，**不**将「请殷主管帮我们测一轮再调」作为发版模型。

| 层级 | 内容 | 何时 |
| --- | --- | --- |
| **工程必做** | 本地/CI 跑通 E2E · 填门禁包（探针）· **22 封真邮 Round 0/1 四维**（[`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md)）· Demo UI 四项 | Phase 0.3–5 |
| **部署 · 发链接** | `qa_server --unified-cs` 部署至 **平台/服务器** · 稳定 URL · API/索引/图片可访问 | Phase **5.0** — **殷主管 §二 可测标准硬前置** |
| **殷主管试跑** | 针对性试跑 · 反馈 · 术语确认 · **真邮四维 §2.3 已由工程侧 Round 1 自验** | **部署后** · 第二验收关口 |
| **叶天洲演示** | 部门选型 / 汇报 | **殷主管书面认可后**（验收标准 F-3） |

```text
内部 Gate + **真邮 ≥16/19** → 部署稳定 URL → 殷主管试跑反馈 → [认可后] 叶天洲演示
```

**对外叙事（薄 EN 拒答）**：英文资料未就绪时，系统会礼貌索要信息或说明无法给出步骤 — 这是 **Gate R 白名单设计**，不是 demo 失败。演示脚本须预先说明。

**禁止**：未部署、未填门禁包，即对外承诺「随时可约甲方试跑」。

## Out of Scope（Product Phase · 本 POC 不做）

| 项 | 说明 |
| --- | --- |
| 多语言 Runtime 大一统 | 保留 `locale` 参数化即可 |
| Language Adapter（在线） | 离线 EN enrich only（[ADR-0001](../../docs/adr/0001-phase2-retrieval-representation.md) 决策 2） |
| Cross-lingual Runtime 作为 **客户终态** | 中文索引仅工程师/Debug |
| Workflow Learning / 在线 Feedback Loop | 竞品参照，非交付物 |
| Rule Engine / Coze 产品形态 | — |
| **一键发送**（邮件客户端集成） | 殷主管 §二 MVP-1-1 加分项；本期 **复制粘贴级**回信 |
| 独立「邮件库」/`english_corpus/` 顶层目录 | 邮件步骤 **并入现有 qa 组** |
| 向量库 / 分库 **物理选型** | ADR 决策；本计划不绑定 chroma 路径或厂商 |

---

# 2. Existing Baseline（Already Implemented · 勿写进 Todo）

**原则**：Baseline 只在此登记一次；Implementation 正文 **只写 Delta**。

| Item | Status | 留档 / 说明 |
| --- | :---: | --- |
| `locale` + `response_mode=cs_email` | **DONE** | `generate_answer.py` |
| `CS_EMAIL_SYSTEM_PROMPT_EN` | **DONE** | 同左 |
| `library_router` + 三库路由 | **DONE** | 客户路径按机型选库 |
| `customer_reply_templates` **隔离** | **DONE** | 不与 troubleshooting chunk 混 embed |
| 27 场景 + **176 query** | **DONE** | [`cs_email_query_map.json`](./cs_email_query_map.json) — **eval 唯一真源** |
| 三库 **中文** Retrieval Index + hybrid/rerank | **DONE** | Post **G8c** legacy：Gate **14/14** · all **~78%** |
| Oracle smoke（3 case） | **DONE** | [`cs_en_oracle_gen_smoke.md`](./cs_en_oracle_gen_smoke.md) |
| Demo `--unified-cs` **代码** | **PARTIAL** | UI 四项未勾选；LLM context 已 EN-only（Phase 0.1） |
| **`context_builder.py`** | **DONE** | Phase 0.0 抽离 · 0.1 EN Context Policy |
| **`run_cs_e2e_gate.py`** | **DONE** | Gate case E2E probe · 默认 retrieval-only · `--generate` 需 API |

---

# 3. Delta Scope（本轮新增 · 本计划唯一排期范围）

| # | Delta | 对应 Phase |
| ---: | --- | --- |
| D0 | **Extract Context Builder** → 独立模块（Zero Behavior Change） | Phase **0.0** |
| D1 | **EN Context Policy**：`locale=en` 不注入 `content_zh`；Prompt 对齐 | Phase **0.1** |
| D1b | Pilot E2E + 内部初评（`cs_0001` · `cs_0008`） | Phase **0.2** / **0.3** |
| D2 | EN_READINESS 扫描 + Gate case blocking 处理 | Phase 0 并行 → 1a |
| D3 | **English Retrieval Index**（Pilot 子集 → 全量） | Phase 1a / 1b |
| D4 | 客户路径切换至 EN-primary 索引 | Phase 1b |
| D5 | EN-index 检索 baseline（Gate K） | Phase 2 |
| D6 | Style exemplars + Gate G/S E2E 填包 | Phase 3 / 4 |
| D7 | Demo UI 验收 + **部署** + 可选甲方书面确认 | Phase **5.0**–**5.4** |

**不在 Delta**：locale、query map、中文索引 baseline、template 隔离机制 — 已 DONE，仅作回归对照。

---

# 4. Phase 0 · Stop the Bleeding（1–2 天）

**Objective**：**Refactor → Policy → Pilot → Review** 四步分离；客户路径 Context Policy 不再注入中文 semantic。

> 去掉 `content_zh` 是 **Context Policy**，不是 Generator 业务逻辑。不得在 `generate_answer()` 内写 locale 分支拼 context。

## Phase 0 总表

| Phase | Task | DoD |
| --- | --- | --- |
| **0.0** | **Extract `build_context_block()`** → `context_builder.py` | **Zero Behavior Change**；`tests/test_customer_reply_template.py` 等全过 |
| **0.1** | **EN Context Policy**（`locale=en` 不注入 `content_zh`） | Prompt 中无中文知识；**无 zh 自动回退**；薄 EN → 拒答/索要信息（Gate R），不读 zh |
| **0.2** | **Pilot**（`cs_0001` AT12131S · `cs_0008` TC148） | E2E Grounded English Reply 可生成；[`cs_email_pilot_cards.md`](./cs_email_pilot_cards.md)（含 **Context-only / EN Index** 双列） |
| **0.3** | **Internal Review** | 内部 G/S 初评 + 填门禁包探针；**可选**部署后殷主管 review |

**推荐顺序**：

```text
0.0 Refactor（模块抽离）
  → 0.1 Policy（EN context + prompt 对齐）
  → 0.2 Pilot（cs_0001 + cs_0008 E2E）
  → 0.3 Internal Review（+ 可选 skeleton exemplar 探针）
```

**与 0.1 并行（不阻塞 policy switch）**：

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| EN_READINESS 扫描 | Eng | 三库 `qa_groups.json` · Gate 14 | [`cs_en_readiness_scan.md`](./cs_en_readiness_scan.md) |
| `run_cs_e2e_gate` | Eng | 门禁必跑 case | JSON + 门禁包 G/S 列（默认 retrieval-only；`--generate` 需 API） |

---

## 4.0 · Extract Context Builder（Refactor · 无行为变更）

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 0.0.1 新建 `context_builder.py` | Eng | 现有 `build_context_block` in `generate_answer.py` | 函数迁出；import 更新 |
| 0.0.2 API 预留 | Eng | ADR-0003 §Context Builder | 签名含 `locale`；可选 `response_mode`（0.0 **不改变行为**） |
| 0.0.3 回归 | Eng | 现有 tests + TC148 verify + gate context probe | **Zero Behavior Change** |

**0.0.3 回归扩展**（评审 v1.3）：

- `python _scratch/eval/run_cs_e2e_gate.py`（**无** `--generate`）— Gate 9 case context · 断言 **无 zh leak**
- 176 query **检索-only sanity**（不必调 LLM）— Top1 与 legacy 一致或 miss 书面留档
- 防「某条路径绕过 Context Builder」

**DoD**：`generate_answer()` 只调用 `build_context_block(...)` / `build_context_for_hits(...)`，**不知道** zh/en 字段如何选择。

**Import 受影响**（迁模块时一次性改）：`generate_answer.py` · `tests/test_customer_reply_template.py` · `_scratch/eval/verify_tc148_customer_reply_template.py` · `_scratch/eval/scan_thin_zh_ad5s.py`

---

## 4.1 · EN Context Policy（Policy Change）

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 0.1.1 剔除 zh injection | Eng | `context_builder.py` · `locale=en` | 移除 Internal notes / `content_zh` 分支 |
| 0.1.2 禁止 zh 回退 | Eng | ADR-0003 薄 EN 策略 | `content_en` 空时不从 zh supplement；生成侧拒答/索要信息 |
| 0.1.3 Prompt 对齐 | Eng | `CS_EMAIL_SYSTEM_PROMPT_EN` · `QA_SYSTEM_PROMPT_EN` | 删除「translate Chinese internal notes」等与 policy 矛盾条款 |
| 0.1.4 增补 grounding 约束 | Eng | ADR-0003 §4.1 | 不得采信 Reference 中未出现的端子号/电压 |

**DoD**：

- `locale=en` 的 LLM user context **不含** `content_zh` 文本  
- System prompt **不**要求模型翻译已不存在的 Chinese notes  
- **`不等待`** 全库 EN 索引即可切换（与 ADR「Phase 0 不阻塞于 Gate R 全库」一致）

**薄 EN 策略（实现说明）**：当前为 **软约束** — `context_builder` 在无 EN 步骤时注入占位句，拒答/索要信息由 prompt + LLM 执行；Phase 1a 前可对 thin-EN case 列清单，必要时加生成侧 pre-check（全 hit 无 EN steps → 固定索要模板）。对外演示须用 §1.1 叙事。

**不在 0.1**：改检索索引、改 Demo UI 皮肤、工程师模式 UI 仍可见 zh（`display_content_utils` 不动）。

---

## 4.2 · Pilot E2E

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 0.2.1 Pilot 卡片 | Eng（映射可后补殷主管） | `cs_0001` AT12131S · `cs_0008` TC148 · Reference | [`cs_email_pilot_cards.md`](./cs_email_pilot_cards.md) |
| 0.2.2 跑通链路 | Eng | Customer Email → Retriever → **Context Builder** → Prompt → Reply | 2 case 生成稿 + 日志 |

```text
Customer Email → Retriever → Context Builder → Prompt → Reply
```

**Exit**：2 封 Pilot 有可对比 Reference 的英文生成稿；暴露 EN corpus 缺口（供 Gate R / Phase 1a）。  
**Pilot 双列**（评审 v1.3）：卡片须分 **Context-only (0.1)** 与 **EN Index (1a)** 记录 G/S，用于量化 EN 索引增量。

---

## 4.3 · Internal Review

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 0.3.1 逐步对照 Reference | Eng（**可选**部署后殷主管） | Pilot 生成稿 | Grounding / Style 初评 |
| 0.3.2 填门禁探针 | Eng | Gate 必跑子集 · `run_cs_e2e_gate --generate` | [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) G/S 列 |
| 0.3.3 Style 探针（可选） | Eng | 每 Pilot 1 个 skeleton exemplar | 验证 Gate S 方向；正式 exemplar 池见 Phase 3.2 |

**Exit Phase 0**：Policy 已切换 · Pilot 差距可见 · 首轮 G/S 探针留档 · Pilot 卡片双列框架就绪 · [`cs_en_adr_dod_gap.md`](./cs_en_adr_dod_gap.md) 同步刷新。

---

# 5. Phase 1a · Pilot · English Retrieval Index（3–5 天）

**Objective**：在 **Gate 14 + TC148 + #1 DIP + Pilot 映射组** 上交付 **EN-primary 子集索引**。

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 1a.1 整理 EN 资料 | Eng + 殷主管 | CS emails · 原则 doc · `answer_en` | EN_READINESS patch 清单 |
| 1a.2 English Representation | Eng | [ADR-0001](../../docs/adr/0001-phase2-retrieval-representation.md) 决策 2 | `embedding_text_en`（或 ADR 等价字段） |
| 1a.3 Build **English Retrieval Index**（Pilot 子集） | Eng | Pilot qa 组 · ADR-0003 选项 | 可检索 EN 索引 + manifest（`Embedding Count == Chunk Count`） |
| 1a.4 路由接线（Pilot） | Eng | `library_router` · locale=en | 客户路径可打 Pilot EN 索引 |

**Representation（摘要）**：

```text
question（英 fault title）+ content_en + EN symptom keywords
```

**禁止**：`answer_zh` 作 EN 客服默认主字段；Reference 全文进 embedding；新建顶层 `english_corpus/`。

**Exit · Gate R（子集）**：Pilot / Gate case **blocking = 0**（或个案书面接受）。

---

# 6. Phase 1b · Batch · English Retrieval Index（视 blocking，often +1 周）

**Objective**：全量 **English Retrieval Index** + 客户路径默认 EN-primary。

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 1b.1 全量 `answer_en` 补写 | Eng + 殷主管 | EN_READINESS · TC148 templates | patched `qa_groups.json` |
| 1b.2 邮件步骤并入 qa 组 | Eng | Reference 诊断步骤 | `email_examples[]` / `answer_en` |
| 1b.3 Task2 overlay → EN 字段 | Eng | G8c overlay | EN 字段 + 全库 re-embed |
| 1b.4 客户路径 EN-primary 切换 | Eng | Phase 1a manifest | router 默认 EN 索引 |

**Deliverable**：[`cs_en_retrieval_baseline.md`](./cs_en_retrieval_baseline.md) 新增 **EN-index** 章节；legacy 标 `adr-0002-legacy`。

**Exit · Gate R（全量）**：Gate case EN blocking = 0（或书面接受）。

---

# 7. Phase 2 · Retrieval Validation → Gate K

**Objective**：英文 query 在 **English Retrieval Index** 上命中正确知识组。

**心态底线**（评审 v1.3）：叶天洲反馈未强调「检索不准」；Gate K miss 若集中在 edge case、**G/S 已达标**，**不因此否定 POC**。Stretch target（90%）未达 **不单独 Fail**；与 §12 Critical（编造、机型错、中文泄露）分层。

**Eval 真源**：[`cs_email_query_map.json`](./cs_email_query_map.json) — **扩展 merge**，不新建 `eval_cases.json`。

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 2.1 Pilot 子集 eval | Eng | Phase 1a 索引 · Tier A 14 | 子集 baseline |
| 2.2 全量 eval | Eng | Phase 1b 索引 · 176 query | EN-index baseline 报告 |

### Target vs Gate（检索 Top1）

| 切片 | **Target**（ aspiration · 不单独 Fail POC） | **Gate**（ POC 通过线） |
| --- | --- | --- |
| Gate Tier A（14） | Top1 **90%**（stretch） | Top1 **≥ legacy（14/14）** 或个案书面接受 + miss 解释 |
| corpus_direct 全量 | Top1 **90%** | Top1 **≥ legacy（~78%）** 或书面接受 |
| logic | 留档 + miss 聚类 | 不设硬 Fail %；EN 跑完后定 stretch |
| out | — | 评路由/拒答，不单卡 Top1 |

> **88% 不 Fail POC**，若 Gate（≥ legacy）满足且 miss 有书面解释。

**Deliverable**：`cs_en_retrieval_baseline.md` EN 章节（或 `cs_en_retrieval_baseline_en.md`）。

---

# 8. Phase 3 · Generation → Gate G（Grounding）

**Objective**：英文回信 **步骤忠实、不 hallucination**。

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 3.1 locale + response_mode | — | — | **DONE**（Baseline） |
| 3.2 Style exemplars + 原则 doc | Eng（Reference 可后补殷主管） | Reference · `reply-principles-and-tips.md` · [**Style Corpus Plan**](./cs_en_style_corpus_plan.md) | 按场景族 1–2 封 exemplar 配置；**0.3 可挂 skeleton 探针** |
| 3.3 Template 边界 | Eng | ADR-0002 template 隔离 | troubleshooting **不进** LLM context；展示/轻量改写 only |
| 3.4 Grounded only | Eng | EN context blocks | 无端子/DIP/电压编造；无 evidence → 索要/拒答 |

**Acceptance（Gate G）**：门禁包必跑 case Grounding 可接受 · 无 critical；对照 Reference 步骤级 ≥ 4/5；`locale=en` 无 runtime `content_zh`。

---

# 9. Phase 4 · Human Evaluation → Gate S + Gate G 复核

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| 4.1 **22 封真邮四维复测** | Eng | Round 1 xlsx + json | MVP **≥16/19** ④通过（发链判据） |
| 4.1b 探针内部评（可选交叉） | Eng | Gate case | 诊断附录 · 不可替代 4.1 |
| 4.1c **可选** · 殷主管试跑 | 殷主管 | 部署后 | 反馈 · 第二验收 |
| 4.2 填门禁包（探针） | Eng | Gate G/S 分列 | [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) |
| 4.3 可选量化表 | Eng | 27 场景 | `cs_human_eval_scores.md` / xlsx |

| Metric | 门禁 | **Target** | **Gate** |
| --- | --- | --- | --- |
| Knowledge | K | 见 Phase 2 Target | ≥ legacy |
| Grounding | **G** | 步骤对照 Reference 5/5 | 可接受；无 critical |
| English | S | median **4.5** | median **≥ 3** |
| Support Style | **S** | 贴近 TOPENS Reference | median **≥ 3**；无「完全不像客服信」 |

**禁止**：Grounding 5/5 + Style 2/5 仍报「E2E 通过」而不拆因。

---

# 10. Phase 5 · Deploy & Demo → POC Success SC-1～3

| Task | Owner | Input | Output |
| --- | --- | --- | --- |
| **5.0** | **部署至平台/服务器** | Eng | 稳定 URL · 索引/API/图片可访问 · 部署留档 |
| 5.1 Demo 脚本与 UI 四项 | Eng | `--unified-cs` · cs-email 模式 | 勾选留档（Tracking） |
| 5.2 内部 Gate 包完备 | Eng | Gate R/K/G/S | 门禁包填完 · 无未书面接受的 critical |
| 5.3 **可选** · 殷主管发版确认 | 殷主管 | Gate 包 · **已部署环境** | 书面确认 |
| 5.4 **可选** · 叶天洲演示 | 商务 | 部署环境 · SC-1～3 | 感知验收 |

**工程 Exit（不含可选协作）**：5.0 + 5.1 + 5.2 完成即 POC 工程 DoD。5.3/5.4 依赖部署且由商务排期，**不阻塞** Phase 1a–4 继续推进。

**展示**：`English Email → [auto Product line] → English Reply`（工程师折叠：Reference · 中文步骤 · 检索详情）

**Demo 不展示**（客服默认路径）：中文 chunk 全文 · 中文 Answer 首屏 · 型号库下拉 · 技术 pill

**禁止**：仅报 legacy 中文索引 14/14 即对外演示 E2E 成绩（须 EN 路径 + 门禁包 G/S）。

**本地联调**：

```powershell
python qa_server.py --unified-cs --demo-presentation cs-email --images-dir _scratch/run-006/images --port 8765
```

**部署**：生产/演示 URL 与启动参数写入 Tracking（[`cs_en_poc_execution.md`](./cs_en_poc_execution.md) §部署）。

---

# 11. Risks & Rollback

| Risk | 描述 | Mitigation | Rollback |
| --- | --- | --- | --- |
| **R1 · EN Corpus 不足** | `answer_en` 空/弱，Grounding 无 evidence | EN_READINESS · offline 补写 · **Reference Exemplars** 补 Style（不进 embed） | 个案书面接受 + 优先补 Pilot 组 |
| **R2 · Retrieval 下降** | EN-index Top1 低于 legacy | Phase 1a Pilot 先验 · enrich 增量 · hybrid/rerank 复验 | **回退中文索引**（工程师/Debug）；客户路径保持 EN context 无 zh |
| **R3 · Reply AI 味 / 不像客服** | Style 2/5 但 Grounding 尚可 | Exemplars + 原则 doc · **Human Review**（殷主管 Gate S） | 调 prompt/exemplar；不掩盖 Grounding 问题 |
| **R4 · Template 污染 Retrieval** | 礼貌模板误命中 troubleshooting | **Template Isolation**（Baseline DONE）· TC148 专项 gate | 保持 template 不进 embed / 不进 troubleshooting context |
| **R5 · 中文 context 泄漏** | 甲方感知 Chinese reasoning | Phase **0.1** Context Policy · UI 隐藏中文 chunk | Hotfix `context_builder`；Demo 暂停 |
| **R7 · generate_answer if 膨胀** | locale/mode/template 分支堆在 Generator | Phase **0.0** 模块抽离；policy 只进 Context Builder | Refactor PR 独立回滚 |
| **R6 · 机型/qa 映射错误** | 如 cs_0001 → 错误 DIP 组 | Pilot 卡片 + 映射真源（可选殷主管） | 修正 `cs_email_query_map` expected；不盲目跨库 |
| **R8 · 文档/Tracking 漂移** | Baseline 标 DONE 但 gap/计划仍写旧状态 | 每 Phase exit 刷新 [`cs_en_adr_dod_gap.md`](./cs_en_adr_dod_gap.md) | 以代码 + gate 脚本输出为准 |
| **R9 · 软拒答 vs hallucination** | 薄 EN 仅靠 prompt，模型仍可能编造 | thin-EN 清单 · 可选 pre-check · §1.1 对外叙事 | 固定索要模板；Gate R 补 corpus |

---

# 12. Acceptance（Gate R / K / G / S）

```text
Gate R → K → G → S → [5.0 部署] → [可选 殷主管] → [可选 叶天洲]
```

| 门禁 | Gate（POC 通过线） | Target（ aspiration） |
| --- | --- | --- |
| **R** | Gate case EN blocking = 0（或个案书面接受） | 全库 `en_retrieval_ready` 覆盖率最大化 |
| **K** | Tier A Top1 **≥ legacy 14/14** | direct Top1 **90%** |
| **G** | Grounding 可接受；无 critical | 步骤对照 Reference **5/5** |
| **S** | Reply Quality median **≥ 3** | median **4.5** · 可选殷主管盲测认可 |

## Definition of Done · 业务验收

| 验收项 | DoD |
| --- | --- |
| **Knowledge** | EN-index 稳定命中；Gate K 满足 |
| **Grounding** | 可追溯 EN 证据；无编造（Gate G） |
| **English Reply** | 自然专业；无中文中间结果暴露（SC-1/2） |
| **Support Style** | TOPENS 客服风格（Gate S） |
| **Customer Experience** | English → English 闭环（SC-3） |
| **协作** | Gate 清单、Pilot 映射、术语留档；**可选**部署后殷主管书面确认 |

**Critical（一票否决）**：编造步骤/端子/电压；机型张冠李戴；客户路径可见中文 reasoning。

---

---

# 13. Execution Checklist（Tracking · 非 SoR）

## v1.3 变更摘要（评审纳入）

| 主题 | 变更 |
| --- | --- |
| 部署前置 | 新增 Phase **5.0** · 平台/服务器部署为对外演示硬前置 |
| 甲方协作 | 殷主管 / 叶天洲 review **可选** · 不阻塞 Phase 1a–4 · 见 §1.1 |
| 0.0.3 回归 | + `run_cs_e2e_gate` context leak · 176 query 检索-only sanity |
| Pilot | 统一为 `cs_0001` + `cs_0008` · 卡片 **Context-only / EN Index** 双列 |
| Gate K | 明确 stretch 未达不 Fail · edge miss + G/S 达标可推进 |
| Style | 0.3 可挂 skeleton exemplar 探针 |
| 薄 EN | 软约束说明 + §1.1 对外叙事 |
| 风险 | + R8 文档漂移 · R9 软拒答 |
| 脚本 | `run_cs_e2e_gate.py` 标 **DONE**（非待建） |

**日常勾选、产物路径、legacy 留档、回归命令** → 见 [**cs_en_poc_execution.md**](./cs_en_poc_execution.md)。

本计划 **不复制** checklist 条目；Tracking 文档 **只链接** 本文件 Phase 编号（0～5）与 §12 Gate。

## 推荐执行顺序

```text
Phase 0.0 → 0.1 → 0.2 → 0.3（并行：EN_READINESS · run_cs_e2e_gate）
         → Phase 1a（Pilot EN Index）→ Phase 2（EN 子集 K）→ Phase 3/4（G/S）
         → Phase 1b（Batch）→ Phase 2（全量 K）→ Phase 5.0–5.2（部署 + Demo）
         → [可选 5.3–5.4 甲方协作 · 须已部署]
```

**禁止**：跳过 0.0 直接在 `generate_answer.py` 写 locale if/else。  
**禁止**：仅报 legacy 中文索引 14/14 即对外演示 E2E。  
**禁止**：先全库 EN embed 再定 Pilot 格式。  
**禁止**：未部署即对外承诺「随时可约甲方试跑」。

## 留档索引

| 文件 | SoR |
| --- | --- |
| 本文件 | Execution Plan |
| [`cs_en_poc_execution.md`](./cs_en_poc_execution.md) | Tracking |
| [`cs_en_adr_dod_gap.md`](./cs_en_adr_dod_gap.md) | 缺口快照 |
| [`cs_client_requirement_standard.md`](./cs_client_requirement_standard.md) | Business |
| [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) | Gate G/S 填表 |
| [`cs_en_retrieval_baseline.md`](./cs_en_retrieval_baseline.md) | Gate K 数据 |

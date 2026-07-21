# ADR-0003 · English CS：英文权威检索与生成（修订 ADR-0002）

> **产品一句话（对外）**：英文客服 = 英文资料检索 + 英文步骤 Grounding + 真人客服风格。

**状态**：Proposed（**Phase 1b 进行中** · **Caption EN 回灌 DONE** · **EN-index 已为 cs-email 默认**；**Accept 前须** Pilot 留档 + 首轮 Gate G/S 填包 + **真邮四维 E–H** — 见 §Accept 条件）  
**日期**：2026-07-07（**进度刷新** 2026-07-08 · Caption / Demo / EN-runtime）  
**取代范围**：[ADR-0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md) 之 **§工程路径 · §POC 验收（English Customer Mode）** — **非**废止 ADR-0002 全文（工程师模式 / §7 三库路由 / template 隔离等仍有效）  
**触发**：[甲方验收标准](../../_scratch/eval/cs_client_requirement_standard.md)（叶天洲 §一 · **殷主管 §二 MVP 优先**）· [DoD 缺口](../../_scratch/eval/cs_en_adr_dod_gap.md)  
**关联**：[ADR-0001](./0001-phase2-retrieval-representation.md) · [ADR-0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md) · [**Implementation Plan v1.3**](../../_scratch/eval/cs_en_implementation_plan.md) · [`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md)

---

## 背景

### 叶天洲反馈（摘要 · 决策方）

甲方老板 19:48 确认：全英文场景下**英文内容才是准确的**；中文仅为新员工理解的辅助且**用词不准**。当前 Demo「全部喂给 AI、中文干扰、再翻译得乱七八糟、完全偏掉」；未学习殷主管提供的真实回信风格；竞品切片与沟通节奏更好。

### 殷主管一线需求（摘要 · 第一阶段 MVP · **工程第一优先级**）

殷主管为**实际业务方**与**首选配合测试**人选（叶天洲为最终决策方）。第一阶段：两系列（A3S/A5S/A8S、AD5S/AD8S）· 排查 + 说明书 + 产品链接 · **80% 以上准确率**的**图文结合**英文回信 · 部署后发**测试链接**供其针对性试跑。中文仅员工理解；英文步骤须可复制进对客邮件。「一键发送」为加分项，非本期必交。

完整原文与结构化标准见 [**甲方验收标准**](../../_scratch/eval/cs_client_requirement_standard.md)（§一 叶天洲 · **§二 殷主管 MVP**）。**范围与交付形态以 §二 为准**；原则底线以 §一、§三 为准。

### ADR-0002 路径的失效模式

ADR-0002 冻结路径：

```text
English Query → 中文索引 chroma（question + answer_zh · bge-m3 跨语）→ Top-K
             → Generator(locale=en, response_mode=cs_email) → English Reply
```

ADR-0002 **禁止**在线 `EN → CN → EN` 双译，但工程上仍存在等价的**三段式失真**：

| 阶段           | 实际行为                                                                                            | 客户感知                                   |
| -------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| **检索** | 向量空间由`question + answer_zh` 构建（`chunk_builder.py`）                                     | 英文 query 打在「不准的中文 symptom 空间」 |
| **载荷** | 命中块同时携带`content_zh` / `content_en`                                                       | —                                         |
| **生成** | ~~`build_context_block(locale=en)` 注入 `content_zh`~~ → **`context_builder.py` EN-only**（Phase 0.1） | 「中文干扰 AI 再写成英文」—— **LLM context 已修复**；Style / EN 索引仍待 Phase 1+ |

**判定**：Task 1 检索 Gate 14/14 ✅ **不能**证明该路径满足甲方 P0；E2E 生成未验收；叶天洲批评**成立**。

**Supersedes（取代范围）**：ADR-0002 之 **English Customer Mode** 工程路径与 POC DoD（§决策 1–2、§工程分层默认路径、§POC 验收）。**不**废止 ADR-0002 全文 — 工程师模式、§7 三库分库/路由、template 隔离、验证资产目录等 **继续引用 ADR-0002**，与本 ADR 并存。

### ADR-0002 仍保留的部分（不推翻）

| 决策                                                                                | 状态                                  |
| ----------------------------------------------------------------------------------- | ------------------------------------- |
| 三库**分库** chroma（a3s / ad5s / tc148）                                     | ✅ 保留                               |
| 客服**统一入口** + `library_router` 自动路由                                | ✅ 保留                               |
| `customer_reply_templates` **不进** embedding / troubleshooting LLM context | ✅ 保留                               |
| `locale` + `response_mode` 参数化生成（不复制 pipeline）                        | ✅ 保留                               |
| 发版前**内部 Gate 自验**（不把甲方当回归台）                                  | ✅ 保留                               |
| 中文工程师路径 / 中文 eval 基线                                                     | ✅ 保留（**不对客户默认暴露**） |
| Workflow / Coze 产品形态                                                            | ❌ 仍不做                             |

---

## 问题陈述（冻结表述）

English CS **客户路径**的 Retrieval Representation 与 Generation Context：

- **Primary authoritative source（主权威来源）** = 经审核的英文：`content_en`、`answer_en` 补写、离线 EN enrich、Reference 诊断步骤（见 §实施第二步）。  
- **English Retrieval Path MUST NOT depend on Chinese semantic representation**（英文检索/生成路径 **不得依赖**中文 symptom 空间或运行时中文 context）。

中文手册内容可作为**团队内部阅读理解、工程师模式展示、离线补 EN 的参照**，但：

1. **不得**作为 English Customer Mode 的**默认**检索向量主字段；  
2. **不得**在 `locale=en` 时作为 LLM 的**默认可采信** grounding context。

**中文独有信息（公式、工程备注等仅存在于 ZH）的处理**（避免 ADR 与数据现实冲突）：

```text
禁止：runtime 直接读 content_zh 生成英文回信
允许：offline 将中文要点经殷主管确认后写入 answer_en / EN enrich，并记录 linkage
未补全前：标 en_retrieval_ready=false 或 Gate case 书面接受
```

手册 docx 内 ZH/EN **非互译**（V1-05）——不能用「跨语检索中文 + 生成时译回英文」替代英文真源。

### 根因定性（冻结 · 不必再为 ADR-0002 辩护）

叶天洲 19:48 的两条核心诉求**准确**，对应 V1 线 **方向性错误**，不是「bge-m3 多语言不够强」可绕过的调参问题：

| 诉求                                                         | 根因                                                                                                                                                            |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 「英文内容才是准确的，中文是给新员工简单理解用的，用词不准」 | **把权威性更低的中文当成了 embedding 主锚点**（`question + answer_zh`），**把权威性更高的英文当成了附属字段**（`answer_en` 不参与相似度）       |
| 「DEMO 会学习邮件风格来回复，结果一点也没有」                | 甲方期望是**学习 TOPENS 客服真实回复风格**（诊断表达、分支逻辑、配图/链接引用），而非「检索到相关内容拼出答案」；此前 **未针对该期望设计** pipeline |

**结论**：本 ADR「**英文作为主权威来源**、邮件作为风格/步骤语料」方向 **正确，直接执行，不再论证**。

---

## 决策

### 1. 目标客户路径（取代 ADR-0002 §工程路径）

```text
English Customer Email
        ↓
[library_router · 机型/关键词/fan-out]     ← 保留 ADR-0002 §7
        ↓
English Query → English Retrieval Representation → chroma_en（或 EN-primary embedding）
        ↓
Top-K hits（content_en 为主 · 端子/DIP/电压 grounded）
        ↓
Generator(locale=en, response_mode=cs_email, style_exemplars=…)
        ↓
Grounded English Reply
```

**对客户的产品表述**（与文首一致）：

> 英文客服 = 英文资料检索 + 英文步骤 Grounding + 真人客服风格；**不**使用未经审核的中文辅助说明参与 AI 决策。

### 2. 英文权威的三层边界

| 层 | 英文路径规则 | 中文角色 |
| --- | --- | --- |
| **Indexing** | `embedding_text` 以 **EN representation** 为主（见 §3） | **不进入** EN 客服默认索引；中文 chroma 供 `locale=zh` / 工程师 / Debug / Audit |
| **Retrieval** | 英文 query 只打 **EN-primary** 索引 | **禁止** English Customer Path **依赖**中文索引 Top-K 作为默认 |
| **Generation** | `locale=en` 时 context = `content_en` + links/images + **已审核** EN enrich | `content_zh` **禁止** runtime 进入 LLM context；工程师模式可单独展示 |
| **Display（配图）** | `locale=en` 时 `images[].caption` = **`caption_en`**（crosswalk 回灌 · 见 §4.3） | 中文 caption **不得**在 CS 客户视图默认展示；工程师视图保留 `caption_zh` |

### 3. Retrieval Representation（承接 ADR-0001 决策 2）

英文客服索引的 `embedding_text` 构建优先级：

```text
1. question_en（若有）或 question + 标准英文 fault title
2. + content_en（手册英文步骤 · 主文本）
3. + 离线 EN symptom enrich（客户 verbatim / 端子号 / 机型 · ADR-0001 机制）
4. 禁止：answer_zh 作为 EN 客服路径的默认 embedding 主字段
```

**薄 EN 块**（`content_en` 过短或为空）：

- **不得**回退为「检索中文 + 生成时读中文」
- 须走：**offline EN enrich 写回** / 标记 `en_retrieval_ready=false` / E2E 拒答或索要信息
- 与殷主管对齐术语真源（DIP #3 vs #5 等）后补 EN representation

**实现选项**（POC 阶段择一，不并行维护三套）：

| 选项                                | 说明                                                                                                    | 推荐                                 |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| **A · 双字段单库**           | 同一 chroma 集合；`embedding_text_en` 与 `embedding_text_zh` 分字段；英文路径只 embed/query EN 字段 | POC**首选**（重建 embed 即可） |
| **B · 双 chroma 目录**       | `chroma_captioned`（ZH · 工程师）+ `chroma_captioned_en`（EN · 客服）                             | 隔离清晰；存储翻倍                   |
| **C · 仅 overlay EN chunks** | 在现有库上叠加 EN-only child chunks（Task2 延伸）                                                       | 过渡可用；长期归并 A/B               |

### 4. Generation：剔除中文 context + 风格注入

#### 4.0 Context Builder · 架构边界（Phase 0.0 起）

**原则**：`locale` / `response_mode` / `audience` / `engineer_mode` 等维度 **只影响 Context Builder**；`generate_answer()` 永远只做：

```text
Retriever → Context → LLM → Reply
```

| 层 | 职责 | 模块 |
| --- | --- | --- |
| **Context Policy** | 哪些字段进 LLM reference block | `context_builder.py`（自 Phase 0.0 从 `generate_answer.py` 抽离） |
| **Prompt Policy** | 选哪条 system prompt、是否仍提 Chinese notes | `generate_answer.py` / prompts |
| **Display Policy** | Demo 主面板展示 zh/en | `display_content_utils`（**Phase 0 不改**） |

**禁止**：在 `generate_answer()` 内按 locale 拼装 `content_zh` / `content_en`。

#### 4.1 Context Policy（P0 · Phase 0.1）

**顺序**：先 **0.0 模块抽离（Zero Behavior Change）**，再 **0.1 Policy 切换** — 见 §分阶段实施 · Phase 0。

- 在 Context Builder 内，`locale=en`：**移除** `content_zh` / Internal notes 分支
- 薄 EN（`content_en` 空）：**不得**回退为读 zh；须拒答/索要信息，或 offline enrich 后重试（Gate R）
- `supplement_en_text` 仅允许 **EN 素材**补全（不向 LLM 注入 zh 正文）
- **Prompt 对齐**（与 Context Policy 同 PR 或紧随 0.1）：`CS_EMAIL_SYSTEM_PROMPT_EN` / `QA_SYSTEM_PROMPT_EN` **删除**「translate Chinese internal notes」等与 policy 矛盾条款
- `CS_EMAIL_SYSTEM_PROMPT_EN` 增加：**不得**采信未出现在 Reference 材料中的端子号/电压

#### 4.2 Style（P1 · 同一发版波次）

叶天洲「学习邮件风格」——**必须进入 pipeline**，非纯 prompt 空话：

| 机制                      | 说明                                                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Style exemplars** | 从 27 场景 Reference 按场景族选 1–2 封（**非**通篇复制）；注入 `cs_email` system 或 dedicated style 段 |
| **原则 doc**        | `reply-principles-and-tips.md` 压缩为生成约束（五项要素、逐步要结果）                                         |
| **禁止**            | 将完整 Reference 邮件写入`embedding_text`（避免检索偏向长文）                                                 |

#### 4.3 Image Caption · 双语回灌（2026-07-08 · **DONE**）

**根因**：docx 故障排查管线（`caption_images.py` → `image_00x.png` · 仅中文 `caption`）与说明书 VLM 管线（`manual_chunks.json` → `p41-*.png` · `caption_zh`/`caption_en`）**文件名不同、从未 merge**，导致 EN 客服 Demo 仍展示中文 figcaption（违反 P-1）。

**决策**：英文 caption **写入客服索引真源**（非 Demo 硬编码映射）；展示层按 `locale` 选字段。

| 层 | 实现 | 路径 |
| --- | --- | --- |
| **Schema** | `caption_zh` / `caption_en` + legacy `caption` 兼容 | [`image_utils.py`](../../image_utils.py) · `display_caption()` · `localize_images()` |
| **Crosswalk** | docx `images[].file` basename → EN（含分库 `overrides`） | [`samples/troubleshooting/image_caption_crosswalk.json`](../../samples/troubleshooting/image_caption_crosswalk.json) |
| **Sync** | 回灌 `chunks_captioned.json` + chroma zh/en `manifest.json`（**不**默认 re-embed） | [`scripts/sync_image_caption_en.py`](../../scripts/sync_image_caption_en.py) · `--mvp` / `--all` |
| **API** | `qa_server._ask()` · `locale=en` 时对 `hits[].images` 做 `localize_images` | [`qa_server.py`](../../qa_server.py) |
| **Demo** | CS 模式英文 figcaption + `Click to enlarge`；无 EN 时隐藏 figcaption | [`demo/index.html`](../../demo/index.html) · build `20260708h` |

**Phase 1 回灌范围**（2026-07-08）：

- **MVP**：22 封真邮涉及的 11 basename（含 `image_007` · DLMT/COM/ULMT 短接图）
- **全库**：三库 docx 全部 `image_*`（~40 basename · crosswalk 40 条 · `missing_en = 0`）

**验收**：CS Demo 命中 `qa_011` / `image_007` 时 figcaption 为英文（与 Reference 步骤 5 语义一致）；`locale=zh` / 工程师视图仍为中文。

**不在本波 scope**：caption 进 EN `embedding_text` 重 embed（展示层 fix 已满足 P-1 配图）；`caption_images.py` 一次 VLM 双语输出（optional follow-up）。

### 5. 评测：Gate G / Gate S 分列，检索为附录

| 指标 | 门禁 | 角色 |
| --- | --- | --- |
| **E2E Grounding**（步骤/端子/DIP/机型 vs Reference） | **Gate G** | **P0 · 发版硬门槛** |
| **Reply Quality / Style**（体裁 vs Joyce/Lori/Heidi） | **Gate S** | **P1 · 发版硬门槛（median ≥ 3）** |
| Retrieval@1（EN query · EN index） | Gate K | 附录；**不得**单独向甲方汇报达标 |
| Oracle（注入 expected_group） | — | 内部探针 only |

**Gate G 与 Gate S 分列记录**（[`cs_client_feedback_pack.md`](../../_scratch/eval/cs_client_feedback_pack.md)）：禁止仅用「E2E 通过」掩盖 Style 2/5 + Grounding 5/5；定位须能回答「不准」vs「不像客服信」。

### 6. 协作关口（非代码 · 工程留档 + 可选甲方协作）

**工程必做**（不依赖甲方排期）：

- 切片策略、DIP/端子真源、机型路由规则：**内部留档**于 Pilot 卡片 / 门禁包 / query map
- 内部 Gate R/K/G/S + [`cs_client_feedback_pack.md`](../../_scratch/eval/cs_client_feedback_pack.md) 填完

**可选 · 部署后**（见 [Implementation Plan v1.3 §1.1](../../_scratch/eval/cs_en_implementation_plan.md#11--部署与甲方协作可选--非工程硬门禁)）：

- 部署至 **平台/服务器**（稳定 URL）后，方可安排殷主管书面确认 → 叶天洲演示（见甲方标准 F-3）
- **不**将「约殷主管 / 约叶天洲」作为 POC 工程 Phase 硬阻塞项

---

## 实施三步 · 判据与验收

**方法论**：每一步须有 **可检验判据**，不得凭感觉宣称「做完了」。对外发版须通过 **§四道门禁**（Gate R → K → G → S）；**仅 Gate K 达标不能对叶天洲演示**。

### 第一步 · 中英文字段权威性对调

**操作**：三库 `embedding_text` 以 **`answer_en` / EN representation 为主**；`answer_zh` **降级**为工程师阅读理解，**不进入** EN 客服索引与 LLM context。

**前置 · 非「改字段即完」**：须先完成 **EN_READINESS 扫描**（三库逐 `group_id`）：

| 扫描项                 | 说明                                                                                                                                                                   |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `answer_en` 空或极短 | 例：TC148`qa_001`/`qa_002` 的 `answer_en: ""`，英文在 `customer_reply_templates`（须迁移为可检索 troubleshooting EN，**仍不进 embedding 的长模板正文**） |
| 关键规格仅存在于 ZH    | 例：AD5S`qa_022` 的 50Ω / 1152÷R 公式仅在 `answer_zh`；A3S `qa_022`（#13 走停）EN 相对完整 — **同名 group 跨库异构**                                    |
| 端子 / DIP / 电压阈值  | 与殷主管 / Joyce Reference 真源对照（如#1 **DIP #3** vs `ad5s` `qa_010` step #5）                                                                            |

**产出**：[`cs_en_readiness_scan.md`](../../_scratch/eval/cs_en_readiness_scan.md)（待建）— 列 `blocking` / `enrich` / `en_retrieval_ready`。

**切换判据（Gate R · Readiness）**：

| 条件                        | 标准                                                                        |
| --------------------------- | --------------------------------------------------------------------------- |
| Gate case**blocking** | **= 0** 方可对 Gate 场景切换 EN embedding                             |
| 非 Gate 组                  | 可标`en_retrieval_ready=false`；E2E 拒答或索要机型/信息                   |
| TC148                       | template 英文步骤已写入可 grounding 的`answer_en` 或经审核的 EN enrich 段 |

**Phase 0 · Context Policy（不等待全库 EN 索引）**：按 **0.0 → 0.1** 切换；**0.1 完成**即 `locale=en` 不再向 LLM 注入 `content_zh`（与 Gate R 全库 blocking 清零 **解耦**）。

### 第二步 · 邮件语料并入现有 qa 组（不建独立「邮件库」）

**原则**：27 场景（叶天洲侧常称 22+ 批邮件）中 **能对应到三库已有 qa 组** 的，将邮件里的 **英文诊断步骤** 与 **客户提问方式** 提炼后：

- 写入该组 **`email_examples[]`**（新字段 · 元数据）；和/或
- **补充 / 校正** `answer_en`（步骤级，非通篇粘贴 Reference）

**「能对应」判据**（型号名 **不重要**，步骤内容 **才重要**）：

| 用                                                     | 不用                 |
| ------------------------------------------------------ | -------------------- |
| 诊断步骤序列（测电压 → 短接端子 → FORCE/限位…）     | 仅 SKU / 型号字符串  |
| 故障现象 verbatim（stops before open / no response…） | 保修段落、情绪性表述 |
| 与`expected_library` + 殷主管确认的板型/DIP 真源     | 自动按邮件型号挂组   |

**映射注意 · #1 AT12131S（cs_0001）**：

- 主路径：`a3s` · **`qa_011`**（board-family · Joyce **DIP #3**）
- 备路径：`ad5s` · `qa_010`（**alternate** · step2 写 #5 与 #1 真源有已知矛盾 — **须殷主管裁定**，不能仅因「都是 push button 无反应」挂 qa_010）

**产出（每封邮件一条）**：

```text
cs_id · group_id · library · step_alignment_notes · en_fields_updated[]
```

**验收判据**：

- 映射后 EN-index 上该场景 Tier A verbatim **Top1 不降级**（或书面接受并记录原因）
- E2E：系统回信与 Reference **步骤级 Grounding ≥ 4**（门禁包）

**Pilot**：**先**结构化提炼已到手邮件（如 AT12131S、UPS01）→ 格式经确认 → **再**批量处理剩余邮件；不必等 23/27 封齐才定格式。

**结构化卡片模板（Pilot 产出）**：

| 字段                             | 内容                                   |
| -------------------------------- | -------------------------------------- |
| Customer verbatim                | 客户原话（英文）                       |
| CS Reference steps               | 客服回信编号步骤                       |
| Mapped`group_id` + `library` | 及**步骤对齐理由**               |
| `answer_en` gap                | 需补写 / 已 patch 字段                 |
| 是否进入 query map               | `cs_email_query_map.json` merge 标记 |

### 第三步 · 英文 eval · 基准与 E2E

**Query 真源**：以 **客户邮件原话** 为 Tier A（比自编 query 更真实，且已有 Reference 可作 ground truth）：

- 已有：[`cs_email_query_map.json`](../../_scratch/eval/cs_email_query_map.json) · **176 query / 27 场景** · [`customer-query-candidates.md`](../../samples/customer-service-emails/customer-query-candidates.md)
- 增量：新邮件经 Pilot 格式提炼后 **merge** JSON（[`extract_cs_email_queries.py`](../../_scratch/eval/extract_cs_email_queries.py)），**避免两套 eval 漂移**

**不是**从零编写英文 query；**是**：

1. 核对 / 增补 Tier A verbatim（邮件原话）
2. 在 **EN-index** 上重跑 Task 1（旧结果标 `adr-0002-legacy`）
3. 跑 **E2E**（完整 pipeline → 对照 Reference）— 叶天洲真正关心的指标

---

## 四道门禁（Gate R · K · G · S）

| 门禁 | 名称 | 检验什么 | 通过线（摘要） |
| --- | --- | --- | --- |
| **Gate R** | Readiness | `answer_en` / enrich 是否够切换 EN 索引 | Gate case **blocking = 0**（或个案书面接受） |
| **Gate K** | Knowledge | EN-index 检索 Top1 | Gate Tier A ≥ ADR-0002 legacy（14/14 或书面接受个案）；**2026-07-08 G11 后 13/14**（`csq_078` 薄边） |
| **Gate G** | Grounding | 客户邮件 → 系统回信 **步骤/规格** vs Reference | 可接受；**无 critical**；门禁包 Grounding 列 |
| **Gate S** | Style | 回信 **体裁/语气** vs 真实 CS | Reply Quality **median ≥ 3**；无「完全不像客服信」 |

```text
Gate R ──→ Gate K ──→ Gate G ──→ Gate S ──→ [部署] ──→ [可选 殷主管] ──→ [可选 叶天洲]
         ↑              ↑           ↑
    仅 K 通过 ≠ 演示   P0 硬门槛    P1 硬门槛（与 G 分列填包）
```

**过关规则**：

- **发版最低线**：Gate R + K + **G** 必过；**S** 必过（median ≥ 3）或书面接受个别 case 体裁差距  
- **禁止**：Grounding 5/5 + Style 2/5 仍对外宣称「E2E 已通过」而不拆因  
- **禁止**：向甲方单独汇报 Gate K 100% 而 Gate G/S 未跑或未填 [`cs_client_feedback_pack.md`](../../_scratch/eval/cs_client_feedback_pack.md)

> 注：旧称「Gate E」= **Gate G + Gate S** 联合留档；新文档统一用 G/S。

---

## POC Success · 感知标准（叶天洲会买单的表述）

工程 Gate 之外，增加 **客户可感知** 成功标准（纳入 DoD）：

| # | 标准 |
| ---: | --- |
| P-1 | **客服默认路径**：UI 与回信正文 **无可感知中文**（含配图 figcaption · §4.3；工程师/Debug 模式除外） |
| P-2 | **Customer cannot perceive Chinese reasoning** — 甲方无需听解释「我们内部用中文索引」 |
| P-3 | 内部 Gate G/S 达标；**可选**（部署后）殷主管盲测 **≥ 10** 封 Gate case 认可 Grounding **与** Style |

叶天洲原话本质是「看到了中文干扰、不像真人客服信」— **P-1～P-3** 与 **Gate G/S** 分别覆盖。

---

## 分阶段实施（推荐顺序 · 对齐四道门禁）

```text
Phase 0 · 止血（1–2 天）                         → Gate G/S 探针
  0.0 Extract Context Builder → context_builder.py（Zero Behavior Change）
  0.1 EN Context Policy：locale=en 不注入 content_zh；Prompt 对齐
  0.2 Pilot：cs_0001 + cs_0008 E2E
  0.3 Internal Review → 填门禁包 G/S 探针列
  （并行）EN_READINESS 扫描 · run_cs_e2e_gate

Phase 1a · EN Representation · Pilot（3–5 天）   → Gate R + Gate K（子集）
  范围：Gate 14 组 + TC148 + #1 DIP + Pilot 邮件映射组
  补 blocking answer_en / TC148 template → 可检索 EN 步骤
  embedding_text_en + 子集重 embed + EN baseline（子集）
  library_router 英文路径改打 EN 索引（Pilot 库）→ **2026-07-08 全三库 cs-email 默认 EN-index**

Phase 1b · EN Representation · Batch（视 blocking 另估，often +1 周） → Gate R + K（全量）
  三库全量 EN embed + Task2 overlay 迁移至 EN 字段
  邮件步骤 enrich 批量并入 qa 组
  全量 EN retrieval baseline（legacy 对照）
  **2026-07-08 AM**：`chroma_captioned_en` 三库已建（a3s 121 · ad5s 100 · tc148 2）；G11 G9/G10 overlay → EN-index · Gate K **13/14**
  **2026-07-08 PM**：`qa_server --demo-presentation cs-email` **默认 EN-index**；**Caption EN 回灌**（§4.3 · crosswalk 40 条 · sync --all）
  **Wave 1 进行中**：22 封真邮 Round 0 批量 E2E（[`cs_22mail_batch_runner.py`](../../_scratch/eval/cs_22mail_batch_runner.py)）· 四维 E–H 人工待填

Phase 2 · Style（与 1b 重叠）                   → Gate S
  cs_email + style exemplars + 原则 doc
  email_examples / Reference 步骤对齐

Phase 3 · 部署与发版演示                         → Gate G + S + POC Success P-1～P-3
  5.0 部署至平台/服务器 · UI 四项验收 + 门禁包无 critical
  [可选] 殷主管书面确认 · 叶天洲演示
```

**工期说明**：**禁止**将「三库全量 EN + 27 场景」绑死在「3–5 天」；以 **1a Pilot 出口** 为第一批里程碑，1b 工期依 [`cs_en_readiness_scan.md`](../../_scratch/eval/cs_en_readiness_scan.md) blocking 数量另估。

**禁止**：仅改 Demo 皮肤或只报 Task1 Top1 即对叶天洲演示。

---

## Accept 条件（Proposed → Accepted）

本 ADR **可立即按 Proposed 实施**；转为 **Accepted** 须：

1. Phase **0.0 + 0.1 + 0.2 + 0.3** 完成（Context Builder 抽离 · EN policy · Pilot · 首轮 G/S 探针）  
2. Pilot 卡片（≥2 封）格式经确认  
3. EN_READINESS 扫描首版留档  

**不在 Accept 前 Freeze** 全库工期与个别 case 的 Style 阈值豁免。

---

## Definition of Done（取代 ADR-0002 §POC 验收 · English Customer Mode）

**全部满足方可再次邀请甲方演示**（须 **Gate R + K + G + S** · **§POC Success** · **已部署**；殷主管/叶天洲现场为 **可选**，见 §6）：

| # | 项 | 标准 |
| ---: | --- | --- |
| 1 | **Gate R** | EN_READINESS：Gate case blocking = 0；或个案书面接受 |
| 2 | **Gate K** | EN-index Gate Tier A Top1 ≥ ADR-0002 legacy（14/14 或书面接受个案） |
| 3 | **Gate G** | 门禁包 Grounding 可接受；**无 critical**；`locale=en` 无 runtime `content_zh` in LLM context |
| 4 | **Gate S** | Reply Quality **median ≥ 3**；对照 Reference 无「完全不像客服信」 |
| 5 | **POC Success P-1～P-3** | 客服路径无可感知中文（**含配图 caption** · §4.3）；内部 G/S 达标；**可选**殷主管盲测 ≥10 封 |
| 6 | **E2E 留档** | `cs_client_feedback_pack.md`（**G/S 分列**）+ `run_cs_e2e_gate` 或等价 JSON |
| 7 | **统一入口** | 客服不选手册库（ADR-0002 §7 仍有效） |
| 8 | **回归** | 中文工程师路径 eval 不低于冻结基线；TC148 template gate PASS |
| 9 | **部署** | 平台/服务器可访问 Demo（Implementation Plan Phase 5.0） |
| 10 | **协作（可选）** | 部署后：殷主管对 Gate 清单、术语真源、Pilot 映射书面确认 |

**Critical（一票否决）**：编造端子/电压/DIP；机型张冠李戴；英文回复明显由不准中文「译出」。

---

## 明确不做（延续 + 增补）

**延续 ADR-0002**：

- 在线 Query Translation 作为默认路径
- `customer_reply_templates` 入向量库
- 三库 chroma **物理合并**为单索引
- 客服手动选库作为默认 UX
- Workflow 闭环平台

**本 ADR 增补禁止**：

- English Customer Path **依赖** `answer_zh` 作为默认 `embedding_text` 主字段  
- `locale=en` 将 `content_zh` 作为 **runtime** LLM grounding context（含「translate key points only」）  
- 以 Oracle / Gate K Top1 alone 代替 **Gate G**  
- 以「E2E 通过」代替 **Gate S** 分列评估  
- 未部署、未过内部 Gate G/S，即向叶天洲演示  
- 仅报 Gate K Top1 而 Gate G/S 未填包即对外演示  

---

## 备选方案与否决理由

| 方案                                         | 裁决                                                                                    |
| -------------------------------------------- | --------------------------------------------------------------------------------------- |
| **bge-m3 跨语即可、不必改索引**        | **否决** — 叶天洲 P0-3 是数据层根因；跨语不能使不准的中文变权威                  |
| **维持 ADR-0002 + 仅藏中文 UI**        | **否决** — 不解决叶天洲 P0-3；E2E 仍污染                                         |
| **维持中文索引 + 禁止 context 中文**   | **过渡仅 Phase 0** — 检索仍在中文空间，P0-4 切片问题仍在；**不能**作为终态 |
| **英文索引 + 中文工程师双轨**          | **采纳** — 本 ADR 主方案                                                         |
| **27 场景 Reference 全文入 embedding** | **否决** — 压制步骤块（同 ADR-0002 template 教训）                               |
| **重建 multilingual 大一统 runtime**   | **否决** — `locale` 参数化保留；双 representation 字段即可                     |

---

## 后果

### 正面

- 与叶天洲 19:48 原文及 [`cs_client_requirement_standard.md`](../../_scratch/eval/cs_client_requirement_standard.md) **语义对齐**
- 失败模式可对外解释：「系统以**英文为主权威来源**做检索与生成」  
- E2E 与检索指标分离，避免「Top1 100%」误导
- 配图双语 crosswalk 打通 docx 与 manual VLM 两条管线，**P-1 中文 figcaption 泄漏**已关闭（2026-07-08）

### 负面 / 成本

- 三库需 **EN representation 重建 embed**（或双 chroma）；Task2 overlay 需迁移到 EN 字段
- 薄 EN / 异构组须与殷主管逐条补真源 — **人力对齐成本**
- 中文 eval 基线须回归守护，避免 EN 改动破坏工程师路径  
- ADR-0002 **English Customer 章节**由本 ADR 接替；ADR-0002 其余条款仍作工程师路径索引

### 迁移

| 资产                                    | 动作                                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `chroma_captioned`（ZH）              | 保留；`locale=zh` / engineer；**BL-RET-01a** 已重 embed（`doc_type` / `models`） |
| EN embed 字段 /`chroma_captioned_en`  | **Phase 1b 三库已建**（2026-07-08）；**cs-email Demo 默认 EN-index**（`library_router` · `qa_server`） |
| Task2 G1–G8c overlay                   | legacy **ZH-index** · Gate **14/14** · all **78%**（2026-07-07） |
| Task2 **G9+G10** overlay               | **EN-index**（G11 · 2026-07-08）· `cs_0026`→`qa_001` · `cs_0013`→`qa_022` · E2E 可评分 **7/7** |
| **`image_caption_crosswalk.json`**     | docx `image_*` → `caption_en` · **40 basename** · [`sync_image_caption_en.py`](../../scripts/sync_image_caption_en.py) 回灌 chunks + manifest（2026-07-08） |
| `chroma_merged`（ts+manual）          | a3s/ad5s/tc148 merge 完成（**Demo 未接** · 见 [`client_mvp_two_series_progress.md`](../../_scratch/eval/client_mvp_two_series_progress.md)） |
| `cs_en_retrieval_baseline`            | **ZH-index** 2026-07-08：Gate **14/14** · all **68.8%**（109 scorable）；标 `adr-0002-legacy` 对照保留 |
| `cs_en_retrieval_baseline_en`         | **EN-index** G11 后：Gate **13/14** · all **54.1%** — **ADR-0003 主口径 · runtime 已切换** |
| `cs_22mail_eval_round0.json`          | 22 封真邮 Round 0 批量回信留档（2026-07-08）· MVP 19 封待四维 E–H |
| `cs_en_readiness_scan.md`             | Gate R · 三库 EN 完整性（**Gate blocking 2 · tc148**） |
| `cs_email_pilot_cards.md`             | Pilot 邮件结构化卡片（AT12131S · UPS01 · 待建） |
| `build_context_block` / **`context_builder.py`** | Phase **0.0–0.1 DONE**（模块抽离 + EN policy） |
| **`image_utils.py`**                  | `caption_zh` / `caption_en` · `localize_images()` · Phase **Caption 回灌 DONE** |

---

## 参考

- **甲方验收标准**：[`_scratch/eval/cs_client_requirement_standard.md`](../../_scratch/eval/cs_client_requirement_standard.md)
- **缺口对照**：[`_scratch/eval/cs_en_adr_dod_gap.md`](../../_scratch/eval/cs_en_adr_dod_gap.md)
- **Query / eval 真源**：[`cs_email_query_map.json`](../../_scratch/eval/cs_email_query_map.json) · [`customer-query-candidates.md`](../../samples/customer-service-emails/customer-query-candidates.md)
- **被取代决策**：[ADR-0002](./0002-english-cs-cross-lingual-retrieval-localized-generation.md)
- **Representation 机制**：[ADR-0001](./0001-phase2-retrieval-representation.md) 决策 2
- **工程交付计划**：[Implementation Plan v1.3](../../_scratch/eval/cs_en_implementation_plan.md) · [`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md)
- **配图 EN crosswalk**：[image_caption_crosswalk.json](../../samples/troubleshooting/image_caption_crosswalk.json) · [`sync_image_caption_en.py`](../../scripts/sync_image_caption_en.py)
- **真邮 Round 0**：[cs_22mail_eval_round0.json](../../_scratch/eval/cs_22mail_eval_round0.json) · [22封真邮_四维评分表.xlsx](../../_scratch/eval/22封真邮_四维评分表.xlsx)

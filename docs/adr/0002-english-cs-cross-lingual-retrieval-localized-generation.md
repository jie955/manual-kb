# ADR-0002 · English CS：跨语言检索与本地化生成

**状态**：Superseded by [ADR-0003](./0003-english-cs-english-authoritative-pipeline.md)（**English CS 客户默认路径**）· 中文工程师路径 / 三库分库 / template 隔离仍有效  
**日期**：2026-07-07  
**前置**：客服邮件语料 27 场景归档（**正文纯英文**）· [`cs_email_query_map.json`](../../_scratch/eval/cs_email_query_map.json) · **当前 POC 运行态仍为中文**（索引 / 展示 / 生成 / eval 门禁）· 三库 docx 中文 Top1 已通过  
**关联**：[ADR-0001](./0001-phase2-retrieval-representation.md) · [**ADR-0003**](./0003-english-cs-english-authoritative-pipeline.md)（**English Customer Mode 现行草案**）· [`docs/排期.md`](../排期.md) · [**甲方验收标准**](../../_scratch/eval/cs_client_requirement_standard.md)（叶天洲 19:48 · **冲突时以甲方标准为准**) · [`samples/customer-service-emails/customer-query-candidates.md`](../../samples/customer-service-emails/customer-query-candidates.md) · [`reply-principles-and-tips.md`](../../samples/customer-service-emails/reply-principles-and-tips.md) · **执行清单** [`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md)

---

> **墓碑 · 阅读指引（2026-07-07）**
>
> 本 ADR 之 **English Customer Mode**（客户默认路径：跨语中文索引 → 英文生成）已由 [**ADR-0003**](./0003-english-cs-english-authoritative-pipeline.md) **Supersedes**。对叶天洲/殷主管的 POC **勿再按本文工程路径编码或验收**。
>
> | 范围 | 指引 |
> | --- | --- |
> | **客户 Demo / 发版 / Gate DoD** | → [**ADR-0003**](./0003-english-cs-english-authoritative-pipeline.md)（Gate R·K·G·S） |
> | **本文仍有效（可引用）** | §7 三库分库与统一入口 · template 隔离 · `locale`/`response_mode` · 验证资产目录 · 发版前内部 Gate 原则 · 工程师中文路径 |
> | **本文勿再执行** | `question+answer_zh` 作 English CS 主 embedding · 跨语中文索引为终态 · `content_zh` 进 `locale=en` LLM context · 以 Task1 Top1 代替 E2E |
>
> 下文保留 **历史决策快照**（git 保真）；与 ADR-0003 冲突时以 **0003 + 甲方验收标准** 为准。

---

## 背景

manual-kb **当前已交付的 POC 运行态是中文路径**：

- 检索索引：`question + answer_zh`（`chunk_builder.py`）
- Demo 主面板：以 `content_zh` 为主（thin 时补 `content_en`）
- LLM：`generate_answer.py` 固定 **简体中文** system prompt
- 门禁：`eval_queries.json` 等 **中文 query** Top1/Top3

与此相对，[`samples/customer-service-emails/`](../../samples/customer-service-emails/) 归档的 **客户原文与客服回信均为纯英文**（场景 MD 内「客户原文」「客服回复」段不落中文翻译；元数据 / 问题摘要可为中文）。  
**勿将「语料是英文」等同于「POC 已是英文端到端」**——后者是本 ADR 要增量交付的目标，不是现状。

甲方与真实客户场景要求 **英文来信 → 英文客服回信**，且 **端到端准确**（找对人、说对步骤、不瞎编）。架构讨论已收敛；本 ADR **冻结边界与 DoD**，后续只允许数据驱动微调（如修正 `expected_group_ids`、条件触发 representation enrich），**不再扩展新 pipeline 形态**。

### 甲方需求优先级（冻结 · 2026-07）

**若核心偏差，POC 白做。** 讨论与验收须按以下顺序，不得颠倒：

| 优先级 | 要求 | 说明 |
| ---: | --- | --- |
| **P0** | **英文进 → 英文出 + 准确** | 硬门槛。客户这封邮件在讲什么故障，系统须落到**对的排查路径**（E2E：检索 + 生成合一评判）。界面英文化但答错题 = 未交付。 |
| **P1** | **像真实客服信的格式与语气** | **仅在 P0 成立基础上的加分项**（开场、保修一句、逐步要结果、索地址等）。答错题时写得再像 Joyce 也不算及格。 |
| **—** | 中文索引 / 工程师展开 | 对内手段；**不得**作为甲方默认首屏或验收替代。 |

排查手册 docx 内 **ZH/EN 非互译**（内部速记 vs 对客邮件体裁，见 V1-05 / V1.1）。**本 POC**：在 **不替换中文基线** 的前提下叠加英文检索与英文生成，而非重构 multilingual runtime。

### 验证资产（非「仅 22 封邮件」）

甲方提供的材料构成**发版前自验**的主数据集，覆盖大部分真实客户交流形态，**不依赖**甲方反复试跑才能收敛：

| 资产 | 路径 / 规模 | 用途 |
| --- | --- | --- |
| **客服场景语料** | `samples/customer-service-emails/` · **27 场景**（真实 22 + 甲方测试 5） | 客户原话、真实 CS 回信（Reference）、多轮 / 售前售后 / 已排查信息 |
| **Query 候选** | `cs_email_query_map.json` · **176 条**（Tier A verbatim + 衍生 + fork probe） | 检索与 E2E Gate 集 |
| **客服回复原则** | `reply-principles-and-tips.md` | 准确之后的体裁与 SOP（五项要素、分层、勿通篇复制） |
| **排查手册三库** | A3S / AD5S / TC148 `chroma_captioned` | Grounded 步骤真源 |
| **Side-by-side / Oracle** | `cs_side_by_side_demo.md` · Task 0 smoke | 分离「生成上限」与「E2E 瓶颈」 |

**对外表述**：我们有足量真实客户交流素材与 gold 回信，**发版前在内部跑通 Gate**；不是「只有 22 封信、剩下的靠甲方测出来」。

### 甲方商务对话中的参照（非本次发版交付模型）

甲方曾描述另一供应商做法（大意）：做出来 → 甲方测 → 反馈不对 → 对方调「阈值规则」（召回或别的，甲方技术不懂）→ 准确率越来越高。

**定位**：

- 这是**商务口吻下的协作期望参照**，不是 manual-kb 要交付的 **Workflow 产品形态**。
- **本次发版不得依赖**「先交给甲方试 → 再根据反馈多轮发布调参」作为收敛路径——工程上不可持续，且核心若偏了，甲方测再多轮也救不回来。
- **正确做法**：用上述验证资产在**交付前**完成 Gate 自验（Task 1 E2E + Task 4 双维 + 关键 case 对照 Reference）；达标后一次性演示。发版后若有个案问题，走常规定制/fix，**不**把「甲方当回归测试台」写进 DoD。

[`cs_client_feedback_pack.md`](../../_scratch/eval/cs_client_feedback_pack.md) 定位为 **发版门禁记录表**（内部填），不是「等甲方填反馈列再算完成」。

---

## 工程分层（讨论标注 · 防 KPI 混谈）

| 层 | 职责 | 与甲方验收的关系 |
| --- | --- | --- |
| **Knowledge** | 检索命中正确 qa 组 · Top1/Top3 | **P0 准确性的主因**（E2E miss 多源于此） |
| **Generation** | `locale` + `response_mode` → 英文 CS 信 | P0 步骤忠实度 + P1 体裁 |
| **Presentation** | Demo 英进英出 · 不默认暴露中文 chunk | 必要条件，**不替代**准确性 |
| ~~Workflow 产品~~ | ~~反馈闭环平台~~ | **不在 POC DoD**；甲方口中的「调规则」= 我方内部改检索/prompt/路由的总称 |

```text
甲方验收路径（默认）:
  English Customer Email → Grounded English Reply（准）

工程路径（对内）:
  English Query → 中文索引 chroma → Top-K → Generator(en, cs_email)

发版前（对内 · 必做）:
  Gate 集 E2E 自验 → 对照 Reference / 原则 doc → 未达标不交付
```

**产品原则**：中间过程可以是中文索引，**但不能作为甲方默认首屏**。对内解释：「内部知识映射为中文索引，输出与客户语言一致。」

---

## 语料语言 vs 当前 POC 基线

| 维度 | 客服邮件语料 | 当前 POC 运行态 | ADR-0002 增量目标 |
| --- | --- | --- | --- |
| **客户 query** | 纯英文（verbatim） | 中文 eval query | 英文 query eval + 可选 `locale=en` 生成 |
| **客服 outbound** | 纯英文（27 场景语料 + Reference 回信） | 中文 LLM / 无 cs_email mode | `response_mode=cs_email` + `locale=en` |
| **排查知识库索引** | —（语料不进库） | `answer_zh` 向量化 | **不改**；必要时 offline EN symptom enrich |
| **手册正文展示** | — | 中文为主 | 生成层读 EN 素材；展示层中文基线 **保持** |
| **eval 门禁** | `cs_email_query_map`（EN） | `eval_queries*.json`（ZH） | 英文 Gate 集 **另跑、另留档**；中文回归 **不降级** |

```text
英文邮件语料（samples/customer-service-emails/）  →  eval query / 回信风格参考
中文排查库（三库 chroma + answer_zh）            →  检索 grounded 真源（POC 主库）
ADR-0002 增量                                   →  英问 + 英答，跨语命中中文索引库
```


## 决策

### 1. 能力定义（产品表述）

在 **中文 POC 基线之上叠加** 英文客服能力（非替换中文路径）。能力由两项组成，共用同一套 **中文索引** 知识库、**分开评测、分开优化**：

1. **跨语言检索（Knowledge）**：English Query → 正确 QA Group。
2. **本地化生成（Presentation + Generation）**：Grounded **English Reply**（对齐纯英文语料 outbound 体裁）。

**对客户的产品表述**（推荐）：

> 英文客服能力 = 跨语言检索（English Query → 正确 QA Group）+ 本地化生成（Grounded English Reply）；共用同一知识库，分项评测与优化。

不绑定单一输出体裁（邮件 / Chat / WhatsApp 均可在 `response_mode` 扩展），不绑定单一语言（`locale` 维度预留）。

### 2. 禁止路径

**不得**采用「英文问 → 译成中文检索/生成 → 再译回英文」作为 POC 主路径。该路径 AI 味重，与真实 CS 邮件体裁不符，且无法单独验证检索与生成各自效果。

### 3. 生成层参数化（不派生多 pipeline）

在现有 `generate_answer.py` 上增加两个维度，**不**为每种语言/场景新建独立 runtime 函数：

| 参数 | 取值 | 含义 |
| --- | --- | --- |
| `locale` | `zh` \| `en` | 输出语言 |
| `response_mode` | `qa` \| `cs_email` | 输出体裁（排查助手 vs 客服邮件） |

`locale=zh` 且未指定 mode 时，行为与现网一致。

### 4. 检索层冻结

- POC **不**引入 Query Translation、Language Adapter、独立 EN chroma。
- 英文 query **直接**打现有三库（bge-m3 + 与中文 eval 对齐的 retrieval 配置）。
- 若跨语言 Top1 不足，**先测再改**；仅在不达标时按 [ADR-0001](./0001-phase2-retrieval-representation.md) 对 `embedding_text` 做 **symptom 级 EN 关键词 enrich**（离线），而非重构知识库或在线翻译。

### 5. Template 与 Knowledge Layer 隔离

`customer_reply_templates[]`（及 `negotiation_offers[]`）：

- **永不**进入 `embedding_text` / 向量索引；
- **永不**与 internal steps 混进同一 LLM context（TC148 V1.1 gate 已落地）；
- 仅用于 **展示层** 或 **cs_email 模式的轻量改写/参考**，不作为检索主文本。

### 6. Presentation Layer（Demo · P0 · UI/UX 纳入发版改造）

**对客户默认演示路径**：

```text
Customer Email (English) · paste full text
        ↓
[auto product routing — 客服不可见]
        ↓
Knowledge Match（英文摘要 + Product line）
        ↓
Grounded English Reply
```

**UI/UX 要求**（详见 [`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md) §「P0 · Demo UI/UX」）：

- 多行输入（整封邮件）；**无型号库下拉**（工程师模式可 force override）
- 主屏仅英文回信；中文步骤 / 检索详情 / Reference 折叠
- Side-by-side 示例 chip；技术 pill 对客服隐藏
- 启动：`python qa_server.py --unified-cs --demo-presentation cs-email`

- **禁止**客服首屏：中文 chunk 全文、型号库下拉、技术栈 pill。
- **保留**工程师展开（force library · 中文步骤 · Reference gold）。
- 汇报顺序：**英文回信 → Grounding（准确）→ 体裁 → 检索附录**。

---

## 边界（Frozen · 维护者必读）

```text
User Query (any language)
        ↓
   Retriever          ← locale / response_mode 不影响此层
        ↓
   Top-K hits
        ↓
   Generator(locale, response_mode)   ← 仅此层受参数影响
        ↓
   Localized Reply
```

- **`locale` / `response_mode` 只影响生成与展示**，不改变 chunk、embed、manifest、hybrid 权重。
- **三库分库检索**：query 须按 `expected_library` 路由至对应 `chroma_captioned`（见下表），禁止单库混评。

| `expected_library` | Chroma 目录 |
| --- | --- |
| `a3s` | `_scratch/run-007/chroma_captioned` |
| `ad5s` | `_scratch/run-ad5s/chroma_captioned` |
| `tc148` | `_scratch/run-tc148/chroma_captioned` |

- **`corpus_mapping`**（direct / logic / out）仅用于 **eval 分层**，不是 runtime 分支类型。

### 7. 三库分库 vs 统一入口（冻结）

**结论：知识层不合并 chroma；产品层必须统一入口、自动路由。**

| 层 | 是否合并三库 | 说明 |
| --- | :---: | --- |
| **Knowledge（索引）** | **否** | 三份独立 `chroma_captioned` **保持分库**。A3S/AD5S/TC148 品类与组规模异构（TC148 仅 2 组）；混为单一索引会拉高跨品类误命中（如 #8 英文 query 在 A3S 上 Top1 变遥控器组）。中文 eval 门禁亦按库建立，合并会破坏可回归性。 |
| **Presentation（客服界面）** | **是（统一体验）** | **禁止**以「客服手动选型号库再提问」作为交付形态 — 对一线不友好，且 #8 已证明选错库 = P0 必败。 |
| **Runtime（检索调用）** | **逻辑合并** | 发版须实现 **单一粘贴入口**；库选择在 **服务端自动完成**，客服无感。 |

**发版要求的自动路由（POC P0 · 择一或组合，交付前实现）**：

1. **机型/关键词路由（优先）**：从客户来信解析 `Product Model`、配件名（TC148、A3S、AD5S…）或 query map 中的 `expected_library` 规则 → 命中单库检索。  
2. **三库 fan-out（兜底）**：并行检索三库，取 **全局 Top1**（须带 `library` 元数据与最低分阈值；低分可拒答/索要机型）。  
3. **工程师模式**：保留选手册库仅作 **内部调试**，不对客服默认暴露。

```text
客服视角（交付）:
  粘贴英文邮件 → Send → English Reply
  （可选一行：Matched product line · A3S / AD5S / TC148）

工程视角（保持）:
  query → router → 单库或 fan-out chroma → Top-K → generate_answer
```

**当前 Demo 状态**：`--unified-cs` 单端口 + `library_router.py` 自动路由；CS 模式隐藏选库、textarea 输入、Product line 展示。路由准确率须 Task 1 Gate 留档（#13 等近分场景需关键词/enrich）。

**#8 / #13 教训**：

| Case | 手动选库风险 |
| --- | --- |
| #8 TC148 | 在 A3S 库测 → 必错（已发生） |
| #13 A3S | 库对但 Top1 仍可能偏 — 属检索准度，非选库 |

---

## 已有能力（本轮不修改）

| 能力 | 状态 | 代码/留档 |
| --- | --- | --- |
| `embedding_text` = `question + answer_zh` | ✅ | `chunk_builder.py` |
| `customer_reply_templates` 不进 embedding / LLM internal context | ✅ | `generate_answer.py` · `verify_tc148_customer_reply_template.py` |
| thin-ZH 展示补 EN（非邮件模板） | ✅ | BL-V1-07 · `display_content_utils.py` |
| 三库 bge-m3 + 中文 eval 门禁 | ✅ | `eval_queries*.json` · `docs/排期.md` |
| Hybrid / rerank 基础设施 | ✅ | `retrieval_engine.py` |
| CS 邮件语料 + EN query map | ✅ | `cs_email_query_map.json` |
| 客服回复原则 | ✅ | `reply-principles-and-tips.md` |

**Regression Checklist（POC 验收前）**

- [ ] 未将 template / negotiation 写入 `embedding_text`
- [ ] TC148 template gate 仍 PASS
- [ ] 中文 eval Top1 不低于冻结前基线
- [ ] EN eval 显式使用 bge-m3，未误用 `retrieval_engine` 默认 `bge-small-zh-v1.5`

---

## POC 新增工作（优先级 · 2026-07-07 修订）

完整步骤与 Exit 见 [`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md)。

| 优先级 | Task | 产出 |
| ---: | --- | --- |
| **P0** | **Demo UI/UX** | `demo/index.html` + `--unified-cs` | 见执行清单「P0 · Demo UI/UX」 |
| **P0** | **统一入口 + 自动路由** | `library_router.py` · `qa_server --unified-cs` | 客服不选手册库 |
| **P0** | **E2E 准确 · Gate 自验** | Task 1 E2E + Task 4；门禁包内部填满 |
| **P0** | Demo 英进英出 | 默认 CS 路径不暴露中文 chunk |
| **P0** | **Task 0 · Oracle 生成** | `cs_en_oracle_gen_smoke.md` · 分离生成上限 vs 检索瓶颈 |
| **P1** | Task 3 · `locale` + `response_mode` | `generate_answer.py` · 英文 cs_email prompt |
| **P1** | Task 1 · EN Retrieval / E2E Eval | `cs_en_retrieval_baseline.json` + `.md` |
| **P1** | Task 4 · 双维评分 | Grounding（准确）+ Reply Quality（体裁加分） |
| **P2** | Task 2 · enrich（条件） | 仅 Gate 不达标 |
| **—** | 发版后个案 fix | 非常规；**不**写入发版 DoD |

**推荐执行顺序**：

```text
Task 3 → Task 0（Oracle）→ Task 1（E2E Top1）→ Task 4 + 填门禁包 → [Task 2] → P0 Demo → 交付
```

**Task 0 目的**：Oracle 差 → 优先生成/context；Oracle 好、E2E 差 → 优先 retrieval/routing/enrich。**Oracle 好不能代替发版 Gate。**

Eval 集：**按 case 聚合、允许多 query**；Gate 集 = direct 10 场景 × Tier A verbatim（不全量 176 条）。

---

## Definition of Done（POC 验收 · 发版门禁）

**全部满足即 POC 可交付甲方演示**（**不**要求甲方多轮试跑后才算完成）：

| 项 | 标准 |
| --- | --- |
| **P0 · 准确** | Gate 集 E2E：Grounding 可接受；无 critical；Task 1 Top1 留档 |
| **P0 · 统一入口** | 客服路径 **不要求选手册库**；自动路由或 fan-out 已实现 |
| **P0 · 英进英出** | Demo 默认 `locale=en` + `cs_email`；中文 chunk 非首屏 |
| **Task 0** | Oracle smoke 完成；用于定位瓶颈，**非**发版充分条件 |
| **Task 1** | Gate 集 Top1 / Top3 / MRR 留档；未达标须 Task 2 或书面接受「检索受限」 |
| **Task 3** | `locale=en` + `response_mode=cs_email` 可演示 |
| **Task 4** | Gate 集双维评分：**Grounding 优先**；Reply Quality median ≥3（体裁加分） |
| **门禁包** | [`cs_client_feedback_pack.md`](../../_scratch/eval/cs_client_feedback_pack.md) 由**我方**填完 Round 1 + 已知差距；**不**依赖甲方填表 |
| **回归** | Regression Checklist 无回退 |

**Task1 Gate 集**：direct 场景 `#8–10, #13, #15, #18–19, T1, T3, T4` 的 Tier A 客户原话。

**Task2 触发（任一）**：Gate Top1 **< 60%**；或与同组中文 probe 差 **≥ 15pp**；或 T1/T3/T4 Tier A **全部 miss**。

**Task2 通过**：Gate Top1 提升 **≥ 10pp** 或 **≥ 70%**；否则接受检索受限，生成层仍交付。

**Task4**：Retrieval@1 与 Reply Quality **分开记**；Reply Quality median **≥ 3** 且无 critical（编造步骤 / 错误保修承诺）。

**POC 不承诺**：out 场景 docx Top1、logic 场景 SKU 完全一致、法德西等多语言、在线 Language Adapter、**以甲方反复试跑为收敛手段的发版模型**、Workflow 自动闭环平台。

---

## 明确不做（POC 范围外 · 冻结期间禁止立项）

- 独立 `generate_cs_reply_en()` / 按语言复制 pipeline
- 在线 Query Translation 作为默认路径
- `customer_reply_templates` 入向量库
- 为 POC 新建 Language Adapter 组件（symptom 扩展走 ADR-0001 离线 enrich）
- 合并三库为 **单一 chroma 目录**（索引层；TC148 仅 2 组会被 A3S/AD5S 淹没，跨品类误命中上升）
- 以 **客服手动选库** 作为发版默认交互（仅允许工程师调试模式）

---

## 备选方案与否决理由

| 方案 | 否决理由 |
| --- | --- |
| EN → CN → EN 双译 | 质量不可控；无法分拆检索/生成指标；不符合 CS 体裁 |
| 仅改 prompt 为英文、索引仍纯中文且不测跨语言 | 无法证明「英文问」能力，POC 不可验收 |
| Template 进 embedding | 检索偏向长邮件文，压制内部步骤块（V1.1 已防） |
| 两套 eval JSON（中英完全分离） | 易漂移；采用 case 聚合 + 可选 zh/en 对照 probe |
| POC 阶段上 Language Adapter | 与「先跑数据」冲突；PHOTO/端子等统一走 representation enrich |
| 三库 **chroma 物理合并** | 破坏分库 eval；TC148 组数过少；#8 类跨品类误命中风险 |
| 客服 **手动选库** 交付 | 不友好；选错库 = P0 失败；应用自动路由 / fan-out |

---

## 后果

### 正面

- 执行边界清晰：改 prompt / 跑 eval / 条件 enrich，不触发架构重写。
- 指标可交付：向甲方主报 **E2E 准确（Grounding）**；Retrieval@1 与 Reply Quality 作附录，体裁单列。
- 与 V1 docx 双语异构、TC148 template 隔离 **一致**，无 retroactive 债。

### 负面 / 风险

- 跨语言 Top1 可能低于中文 eval，需 Task2 或接受「检索受限 + 生成补救」。
- `logic` / `out` 场景需人工评「拒答/索要五项要素」，不能单看 Top1。
- 多库 **自动路由** 规则须用 Gate 集验证；fan-out 须记录 `library` + score 便于审计。

### 后续（POC 之后 · 非冻结期）

- 若 EN Gate 稳定：将 Tier A 并入 `eval_queries*.json` 的 case 结构（带 `lang`）。
- 若多语种扩量：再评估 Language Adapter 或独立 representation 线，**另开 ADR**。
- ADR-0001 的 Semantic Expansion 与 Task2 **共用 enrich 机制**，不重复造轮子。
- 发版后持续「甲方测一轮改一轮」：**非**本 POC 交付模型；个案 fix 另议。

---

## 参考

- **POC 执行清单**：[`cs_en_poc_execution.md`](../../_scratch/eval/cs_en_poc_execution.md)
- **甲方反馈 case 包**：[`cs_client_feedback_pack.md`](../../_scratch/eval/cs_client_feedback_pack.md)
- 英文 query 候选：[`customer-query-candidates.md`](../../samples/customer-service-emails/customer-query-candidates.md)
- Query map 真源：[`cs_email_query_map.json`](../../_scratch/eval/cs_email_query_map.json)
- V1 双语教训：[`v1_lessons_for_v2.md`](../../_scratch/eval/v1_lessons_for_v2.md) §1.4 · §2.1

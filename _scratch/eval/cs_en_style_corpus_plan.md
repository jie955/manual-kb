# 22 封真实回信 · 风格训练语料计划（草案）

**性质**：POC **专题交付计划**（Style Corpus）— 展开 [Implementation Plan §8 Phase 3.2](./cs_en_implementation_plan.md#8-phase-3--generation--gate-ggrounding) 与 [ADR-0003 §4.2 Style](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md#42-stylep1--同一发版波次)  
**日期**：2026-07-07（草案 v0.1）  
**状态**：S1 蒸馏完成（Style Card + 10 skeleton）· 待殷主管审 · 运行时接入 ⬜  
**产物目录**：[`samples/customer-service-emails/style/`](../../samples/customer-service-emails/style/) · 校对 [`extraction_review.md`](../../samples/customer-service-emails/style/extraction_review.md)
**关联**：[甲方验收 P1-1](./cs_client_requirement_standard.md) · [27 场景语料](../../samples/customer-service-emails/README.md) · [回复原则](../../samples/customer-service-emails/reply-principles-and-tips.md) · [门禁包 Gate S](./cs_client_feedback_pack.md) · [Pilot Cards](./cs_email_pilot_cards.md)

> **一句话**  
> 22 封 Joyce/Lori/Heidi 真实回信 = **离线风格蒸馏语料** + **按场景族 few-shot 库** + **Gate S 对照 gold**；**不是** embedding 训练集，**不是** 22 封全文塞进 prompt。

---

## 文档治理

| 文档 | 职责 | 本文件关系 |
| --- | --- | --- |
| [ADR-0003](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md) | Style 机制定义（exemplars · 原则 doc · 禁止进 embed） | **不替代** ADR |
| [Implementation Plan v1.3](./cs_en_implementation_plan.md) | Phase 3.2 任务与 Gate S 门禁 | **展开** Phase 3.2 |
| [cs_en_poc_execution.md](./cs_en_poc_execution.md) | 勾选与产物链接 | Tracking **链接** 本文件 |
| [reply-principles-and-tips.md](../../samples/customer-service-emails/reply-principles-and-tips.md) | 体裁 SOP 真源（中文） | 层 1 输入 |

**维护规则**：Style Card / exemplar 配置变更 → 更新本文件 §6–§8 与产物路径；Gate 阈值不改 ADR，只链门禁包。

---

## 1. 目标与边界

### 1.1 为什么要做

叶天洲 P1-1：「连真实回复邮件都提供了，DEMO 应学习邮件风格来回复。」当前 `CS_EMAIL_SYSTEM_PROMPT_EN` 仅有规则 bullet，**无** TOPENS 真人写法示范，Gate S 无法系统性改善。

### 1.2 语料范围

| 纳入 | 排除 | 理由 |
| --- | --- | --- |
| **22 封**真实归档（`0001`–`0022`）之 **客服回复** 英文原件 | `0023`–`0027` 甲方测试题 | 测试题无 Reference 回信，仅作 **纯 eval** |
| Reference 中的 **体裁、句式、术语、结构** | Reference 中的 **逐步诊断事实** 作为 few-shot 事实源 | 事实须来自 retrieval `content_en` / `answer_en` |
| 离线蒸馏产物（Style Card · skeleton exemplar） | 22 封 **全文** 同时进 prompt | token · 抄错 DIP/端子 · eval 泄漏 |

### 1.3 成功判据（Gate S）

| 指标 | Gate | Target |
| --- | --- | --- |
| Reply Quality / Style（对照 Reference 体裁） | median **≥ 3** | **4.5** |
| 无「完全不像客服信」 | 门禁包 **0** 条 critical | — |
| Hold-out Gate case | #8 #13 #22 #1 + T1–T5 **不得** 出现在运行时 few-shot 池 | — |

**禁止**：Grounding 5/5 + Style 2/5 仍报「E2E 通过」（见 Implementation Plan §9）。

---

## 2. 三线分离（同一批邮件 · 三种用法）

```text
22 封 Reference 回信
        │
        ├─► A · Grounding 线 ──► answer_en / email_examples[] / query map（进 EN 索引 · 不进 style prompt）
        │
        ├─► B · Style 线 ──────► Style Card + 场景族 exemplar（进 prompt · 不进 embedding）
        │
        └─► C · Eval 线 ───────► Gate G/S 对照 gold（hold-out · 不进运行时 few-shot）
```

| 线 | 产物 | 消费者 | 进 LLM prompt？ | 进 embedding？ |
| --- | --- | --- | :---: | :---: |
| **A · Grounding** | 步骤对齐笔记 · `answer_en` patch | Retriever → Context Builder | ❌ | ✅ |
| **B · Style** | Style Card · skeleton exemplar 配置 | `style_exemplars` / system 段 | ✅ | ❌ |
| **C · Eval** | 门禁包 · 殷主管盲测 | 人工 / 半自动评分 | ❌ | ❌ |

**原则**：Style 教 **怎么写**；Retrieval context 教 **写什么**。ADR-0003 明确 **禁止** 将完整 Reference 写入 `embedding_text`。

---

## 3. 三层 Style 架构

```text
层 1  reply-principles-and-tips.md（压缩为 EN bullets）
        ↓
层 2  Style Card（离线从 22 封蒸馏 · 殷主管审）
        ↓
层 3  场景族 dynamic few-shot（运行时 1 封/族 · skeleton 优先）
        ↓
Generator(locale=en, response_mode=cs_email, style_exemplars=…)
```

### 层 1 · 原则 doc（已有）

- 来源：[`reply-principles-and-tips.md`](../../samples/customer-service-emails/reply-principles-and-tips.md)
- 注入方式：压缩为 **10–15 条英文** prompt bullets（问候 · 12 个月质保 · 逐步要结果 · 索订单/地址 · 勿通篇复制 · 已排查要回应）
- **POC 不注入**：客户分层、赔偿策略、公司利益平衡（人工策略，非生成 SOP）

### 层 2 · Style Card（本计划主交付 · 待建）

离线一次性从 22 封提炼，版本化 YAML/JSON，供 prompt 组装与殷主管审阅。

**建议 schema（草案）**：

```yaml
# samples/customer-service-emails/style/style_card.v0.yaml（路径待定 · Pilot 后冻结）

meta:
  version: "0.1"
  source_count: 22
  reviewers: []  # 殷主管签字留档

openings:
  - pattern: "Dear {name}, Thank you for contacting TOPENS. This is {agent} from TOPENS Customer Service Team."
    sources: [cs_0001]
  - pattern: "It will be a pleasure to assist you today."
    sources: [cs_0001, cs_0008]

empathy:
  - "I apologize for any inconvenience this may have caused, but do not worry, we will do our best to help you."

engineering_handoff:
  - "Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help."

step_intro:
  - "If the voltage is normal, please check whether the power led on the control board is ON."
  - "If it fails, please immediately short the push button terminals (4# and 5#)..."

result_request:
  - "Please let me know the result one by one."
  - "Please share me the order # ... for further assistance."

closings:
  - "Thank you again for being a valued customer! Your complete satisfaction is what we strive for."
  - "Best regards, {agent}\nTOPENS Customer Service Team"

terminology:
  terminals: ["+BAT- terminals (11# and 12#)", "push button terminals (4# and 5#)"]
  dip: ["turning the dip switch #{n} off", "even though you didn't install the photocell"]
  actions: ["instant short", "continuous jumper", "erase all remotes codes and reprogram"]

structure_templates:
  troubleshooting_4step:
    description: "编号条件分支 · 每步 if/then · 末步索结果"
    skeleton_sources: [cs_0001, cs_0008]
  presales_recommendation:
    description: "逐条解答 · 附购买链接 · 注意事项"
    skeleton_sources: [cs_0004, cs_0005]
  warranty_rma:
    description: "共情 · 质保链接 · 索地址/订单/照片"
    skeleton_sources: [cs_0017]
```

### 层 3 · 场景族 dynamic few-shot

- **选取**：每族 **1–2 封** Reference → 转为 **skeleton exemplar**（保留开头/过渡/编号结构；步骤事实替换为 `[from references]`）
- **路由**：按 retrieval Top1 `group_id` / symptom 族 / `response_mode=cs_email` 路由表选择 exemplar
- **上限**：单次生成 **≤ 1 完整 skeleton + Style Card 摘要**（控制 token）

**Skeleton 示例（#1 抽象）**：

```text
Dear {customer},

Thank you for contacting TOPENS. … [empathy]

Checked with our engineer, please help us do some tests…

1. [Step grounded in references — wire check · BAT voltage · fuse/LED]
2. [Disconnect accessories · DIP off · reprogram · short 4#/5#]
3. [Motor direct 24V test]
4. [Limit short ULT/COM/DLT test]

Please let me know the result one by one.
… [order # / address if missing]

Best regards,
{agent}
TOPENS Customer Service Team
```

---

## 4. 场景族 taxonomy 与 22 封映射

基于 [`customer-service-emails/README.md` · 主题聚类](../../samples/customer-service-emails/README.md#主题聚类便于-eval) 扩展，用于 exemplar 路由与 hold-out 规划。

| 场景族 ID | 说明 | 22 封成员 | Exemplar 候选（层 3） | Hold-out（Gate eval） |
| --- | --- | --- | --- | --- |
| **F1 · no_response** | 按钮/遥控无反应 · 11#/12# · DIP · 4#/5# | #1 #10 #18 | **#1** Joyce（DIP #3 真源） | #1 ✅ Gate |
| **F2 · tc148_wired** | TC148 · 4#/5# · instant short · 屏蔽 | #8 #9 #10 | **#8** PW502/TC148 | #8 ✅ Gate |
| **F3 · power_motor** | 电机零电压 · 板有电臂不动 · 红灯闪 | #2 #16 #21 | #2 或 #21 | — |
| **F4 · limit_travel** | 走停 · 开不全 · over close · 开过头 | #12 #13 #14 #19 | **#13** A3S 走停 | #13 ✅ Gate |
| **F5 · dual_swing** | 双臂 · slave · 离合 · 一侧异常 | #3 #15 #16 #20 #22 | #15 或 #20 | #22 ✅ Gate |
| **F6 · auto_close_rebound** | auto close · 反转 · 全开回关 | #15 #20 #22 | #22（已结案 · 体裁完整） | #22 ✅ Gate |
| **F7 · presales** | 选型对比 · 推荐 · 链接 | #4 #5 #6 #7 #11 | **#5** 太阳能/对比 | — |
| **F8 · warranty_rma** | 保修 · 换件 · 再故障 | #17 | **#17** | — |
| **F9 · remote_learn** | 学码 · 遥控识别 | #19 | #19 | — |
| **F10 · multi_turn** | 多轮线程（体裁：承接上文） | #2 #9 #22 | #9（进阶排查语气） | — |

### 22 封明细表

| cs_id | # | 文件 | 类型 | 场景族 | Style 蒸馏 | Exemplar 池 | Gate hold-out |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| cs_0001 | 1 | [`0001`](../../samples/customer-service-emails/0001-at12131s-gate-no-response.md) | 故障 | F1 | ✅ | — | **G+S** |
| cs_0002 | 2 | [`0002`](../../samples/customer-service-emails/0002-a8132-et24-motor-no-power.md) | 故障 | F3 | ✅ | 候选 | — |
| cs_0003 | 3 | [`0003`](../../samples/customer-service-emails/0003-ad8-leds-respond-gate-wont-open.md) | 故障 | F5 | ✅ | — | — |
| cs_0004 | 4 | [`0004`](../../samples/customer-service-emails/0004-pw302-two-separate-gates-recommendation.md) | 售前 | F7 | ✅ | 候选 | — |
| cs_0005 | 5 | [`0005`](../../samples/customer-service-emails/0005-at12132s-dual-swing-solar-jy9132-recommendation.md) | 售前 | F7 | ✅ | **首选** | — |
| cs_0006 | 6 | [`0006`](../../samples/customer-service-emails/0006-a8131-vs-at12131-comparison.md) | 售前 | F7 | ✅ | — | — |
| cs_0007 | 7 | [`0007`](../../samples/customer-service-emails/0007-dual-swing-model-comparison-uk-remotes.md) | 售前 | F7 | ✅ | — | — |
| cs_0008 | 8 | [`0008`](../../samples/customer-service-emails/0008-pw502-tc148-push-button-not-working.md) | 故障 | F2 | ✅ | — | **G+S** |
| cs_0009 | 9 | [`0009`](../../samples/customer-service-emails/0009-at6131-tc148-erratic-wired-button.md) | 故障 | F2/F10 | ✅ | 候选 | — |
| cs_0010 | 10 | [`0010`](../../samples/customer-service-emails/0010-a8131-tc148-no-response.md) | 故障 | F1/F2 | ✅ | — | — |
| cs_0011 | 11 | [`0011`](../../samples/customer-service-emails/0011-a8132-ad8-at1202-pw802-comparison.md) | 售前 | F7 | ✅ | — | — |
| cs_0012 | 12 | [`0012`](../../samples/customer-service-emails/0012-at12131-limit-overswing-stops-halfway.md) | 故障 | F4 | ✅ | 候选 | — |
| cs_0013 | 13 | [`0013`](../../samples/customer-service-emails/0013-a3s-stops-before-fully-open.md) | 故障 | F4 | ✅ | **首选** | **G+S** |
| cs_0014 | 14 | [`0014`](../../samples/customer-service-emails/0014-at602-limit-overclose-magnetic-ring.md) | 故障 | F4 | ✅ | — | — |
| cs_0015 | 15 | [`0015`](../../samples/customer-service-emails/0015-ad8s-auto-close-reverses-second-try.md) | 故障 | F5/F6 | ✅ | 候选 | — |
| cs_0016 | 16 | [`0016`](../../samples/customer-service-emails/0016-pw802-red-light-flashing-wont-work.md) | 故障 | F3/F5 | ✅ | — | — |
| cs_0017 | 17 | [`0017`](../../samples/customer-service-emails/0017-a5131-arm-failed-again-warranty.md) | 故障 | F8 | ✅ | **首选** | — |
| cs_0018 | 18 | [`0018`](../../samples/customer-service-emails/0018-a5-a8-nothing-works-battery-ac.md) | 故障 | F1 | ✅ | 候选 | — |
| cs_0019 | 19 | [`0019`](../../samples/customer-service-emails/0019-ad5s-opens-too-far-remote-not-recognized.md) | 故障 | F4/F9 | ✅ | — | — |
| cs_0020 | 20 | [`0020`](../../samples/customer-service-emails/0020-at1202-wont-stay-closed-slave-arm.md) | 故障 | F5/F6 | ✅ | 候选 | — |
| cs_0021 | 21 | [`0021`](../../samples/customer-service-emails/0021-a8132-board-power-arms-wont-move.md) | 故障 | F3 | ✅ | — | — |
| cs_0022 | 22 | [`0022`](../../samples/customer-service-emails/0022-a5132-opens-then-recloses-resolved.md) | 故障 | F5/F6/F10 | ✅ | — | **G+S** |

**Exemplar 池规模（目标）**：10–12 封 skeleton（每族 1 首选 + 少量备选），**与 Gate hold-out 零交叠**。

**甲方测试题（纯 eval · 无 Reference）**：

| 测# | cs_id | 场景族 | 用途 |
| --- | --- | --- | --- |
| T1 | cs_0023 | F6 | Style + Grounding 生成 eval |
| T2 | cs_0024 | F7 | 售前完整性 |
| T3 | cs_0025 | F2+F8 | 复合排查+保修 |
| T4 | cs_0026 | F1/F4 | 已排查 · 勿通篇复制 |
| T5 | cs_0027 | F1 | 无机型通性 |

---

## 5. 离线蒸馏工作流

### Phase S0 · 单封 Pilot（1–2 天）

| Step | 输入 | 产出 | Owner |
| ---: | --- | --- | --- |
| S0.1 | [`0001`](../../samples/customer-service-emails/0001-at12131s-gate-no-response.md) Reference | Style Card **v0 单封样例** + skeleton #1 | Eng |
| S0.2 | 殷主管 30min 审 | 术语/DIP/句式裁定 · schema 冻结 | 殷主管 |
| S0.3 | 对照 [`cs_email_pilot_cards.md`](./cs_email_pilot_cards.md) | Grounding 与 Style **分列**初评 | Eng |

### Phase S1 · 全量 22 封蒸馏（2–3 天）

| Step | 动作 |
| ---: | --- |
| S1.1 | 逐封标注：opening / empathy / handoff / step_pattern / closing / terminology / 多轮承接 |
| S1.2 | 合并去重 → `style_card.v0.yaml` |
| S1.3 | 按 §4 生成每族 skeleton exemplar 文件 |
| S1.4 | 标注与 Grounding 线冲突项（如 DIP #3 vs #5）→ **Style 用 Joyce 真源 · Grounding 用裁定后 answer_en** |

### Phase S2 · 运行时接入（Phase 3.2 工程）

| Step | 模块 | 说明 |
| ---: | --- | --- |
| S2.1 | `prompts/` 或 `generate_answer.py` | 层 1 EN bullets + Style Card 摘要段 |
| S2.2 | `style_exemplars.py`（或配置 JSON） | 场景族 → skeleton 路径；hold-out 过滤 |
| S2.3 | 路由 | retrieval meta / symptom keyword → 族 ID |
| S2.4 | 门禁 | #8 #13 #22 #1 E2E 填 [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) Gate S |

```text
English Customer Email
        ↓
Retriever → Context Builder（EN-only · Gate G 真源）
        ↓
Style Router → pick family → load skeleton exemplar（Gate hold-out 过滤）
        ↓
LLM（system = rules + principles + style card snippet + 1 skeleton）
        ↓
English Reply → Gate S vs Reference（hold-out）或 vs principles（T1–T5）
```

---

## 6. 产物清单（Deliverables）

| 产物 | 路径（建议） | Phase | 状态 |
| --- | --- | --- | --- |
| **本计划** | `_scratch/eval/cs_en_style_corpus_plan.md` | ✅ 草案 |
| Style Card v0 | `samples/customer-service-emails/style/style_card.v0.yaml` | S1 | ✅ |
| Skeleton exemplars | `samples/customer-service-emails/style/exemplars/{family_id}.md` | S1 | ✅ F1–F10 |
| 族路由表 | `samples/customer-service-emails/style/family_router.yaml` | S2 | ✅ |
| 原则 doc EN 压缩 | `samples/customer-service-emails/style/principles_en.md` | S2 | ✅ |
| 蒸馏校对留档 | `samples/customer-service-emails/style/extraction_review.md` | S1 | ✅ |
| 运行时配置 | `_scratch/eval/cs_style_exemplars_config.json` | S2 | ✅ |
| **`style_exemplars.py`** | 仓库根 · Prompt Policy | S2 | ✅ |
| 殷主管 Style 审阅留档 | `_scratch/eval/cs_style_card_review.md` | S1 | ⬜ |
| Gate S 填包 | [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) | S2 | ⬜ |

**`samples/customer-service-emails/style/` 目录约定**（Pilot 通过后创建 README）：

- 只放 Style 蒸馏产物（Card · skeleton · router）
- **不放** eval 分数或门禁包（留在 `_scratch/eval/`）

---

## 7. 风险与缓解

| ID | 风险 | 缓解 |
| --- | --- | --- |
| **ST1** | 22 封全文 few-shot → 抄错 DIP/端子 | Skeleton + 事实仅来自 reference blocks |
| **ST2** | Hold-out 泄漏 → Gate S 虚高 | 配置层强制过滤 cs_0001/0008/0013/0022；CI 可选检查 |
| **ST3** | Style 好但 Grounding 差 | Gate G/S **分列**；先 EN context 无 zh（Phase 0.1） |
| **ST4** | 通篇复制手册感 | 原则 doc + T4 专项；exemplar 教 **密度** 不教 **长度** |
| **ST5** | 多 agent 口吻（Joyce/Lori/Heidi）混杂 | Style Card 统一术语；落款用占位 `{agent}` |
| **ST6** | 售前/保修策略进 prompt | 层 1 只取 **体裁 SOP**，业务策略留人工 |

---

## 8. 验收与评审关口

### 8.1 工程验收（Gate S）

- Side-by-side **#8 #13 #22** + Pilot **#1**：Style ≥ 3/5，且无「完全不像客服信」
- T1–T5：对照 `reply-principles` 检查项（售前 8 问、已排查、无机型等）
- 殷主管盲测 ≥ 10 封（Implementation Plan §9）

### 8.2 殷主管审阅清单（Style Card）

- [ ] 开场/共情/工程师转述是否与团队习惯一致
- [ ] 术语表：端子号 · DIP · instant short · FORCE/SOFT STOP 等
- [ ] DIP/板型 conflict 裁定（#1 **#3** vs `ad5s qa_010` **#5**）
- [ ] Hold-out 列表确认（Gate case 不得进 exemplar 池）
- [ ] 售前/保修 skeleton 是否过度承诺（赔偿/退货策略）

### 8.3 与 Phase 依赖

| 前置 | 说明 |
| --- | --- |
| Phase 0.1 | `locale=en` 无 runtime `content_zh` |
| Phase 1+ | EN-index 就绪（Style 可与 Grounding 并行蒸馏，但 E2E 评 S 依赖 G） |
| Phase 3.2 | 本计划 **运行时接入** 归属 |

---

## 9. 开放问题（草案待决）

| # | 问题 | 建议 |
| ---: | --- | --- |
| Q1 | Style Card 放 `samples/.../style/` 还是 `_scratch/eval/`？ | **samples/.../style/**（甲方语料衍生 · 可复用）；eval 分数仍放 `_scratch/eval/` |
| Q2 | 路由信号：Top1 group vs keyword vs 显式 `scenario_family`？ | POC：**keyword + group 映射表**；不做 ML 分类器 |
| Q3 | 是否 fine-tune？ | **否**（22 封过少）；few-shot + Card 足够 POC |
| Q4 | Lori/Heidi 封数少，是否加权 Joyce？ | 蒸馏 **全量**；exemplar **按族** 选最佳封，不限 agent |
| Q5 | 多轮 #9 #22 是否单独 few-shot 段？ | F10 族增加「承接上文」pattern；运行时若检测到 thread 标记则加 snippet |

---

## 10. 下一步

1. **殷主管**：过一遍 §4 hold-out + §8.2 审阅清单（30min）
2. **Eng**：S0 Pilot — 从 #1 产出 Style Card 单封样例 + skeleton
3. **Eng**：S1 全量 22 封蒸馏 → `style_card.v0.yaml`
4. **Eng**：Phase 3.2 接入 `style_exemplars` + 填门禁包 Gate S
5. **Tracking**：在 [`cs_en_poc_execution.md`](./cs_en_poc_execution.md) 勾选 S0–S2

---

## 交叉引用

| 文件 | 角色 |
| --- | --- |
| **本文件** | 22 封风格训练语料 **计划 SoR**（草案） |
| [Implementation Plan §8–§9](./cs_en_implementation_plan.md) | Phase 3.2 / Gate S 工程归属 |
| [ADR-0003 §4.2](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md) | 架构：exemplars · 不进 embed |
| [cs_client_requirement_standard.md](./cs_client_requirement_standard.md) | 甲方 P1-1 来源 |
| [customer-service-emails/README.md](../../samples/customer-service-emails/README.md) | 27 场景索引 |

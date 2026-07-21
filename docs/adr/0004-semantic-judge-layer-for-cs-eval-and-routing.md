# ADR-0004 · 语义判断层（Semantic Judge）— CS 评测与路由

**状态**：Proposed（**不在 Round 1e 危机节奏内实施** · 须质量 Phase 1 人工 xlsx + holdout 基线稳定后再开 Phase 2a）  
**日期**：2026-07-10  
**触发**：Holdout T1–T5 ④草稿 **1/5** vs Joyce 22 Round 1e **19/19** 曲线背离；[`fix_classification_holdout_and_round1e_2026-07-10.md`](../../_scratch/eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md) §「同一缺口 × 三次机械替代」诊断  
**关联**：[组件化重构方案](./企业%20RAG%20邮件助手组件化重构方案.md) · [ADR-0003](./0003-english-cs-english-authoritative-pipeline.md) · [`draft_22mail_scoring.py`](../../_scratch/eval/draft_22mail_scoring.py) · [`domains/prompt_style.py`](../../domains/prompt_style.py)

---

## 背景

Phase 1 组件化已落地：`agents/cs_email_workflow`、EvalPack、StylePack、正式 eval runners。质量门禁**未关闭** — holdout 暴露出一类系统性缺口，而非三处独立 bug。

当前流水线在三个位置用**机械规则**模拟本应由**语义判断**完成的工作：

| 位置 | 现有机制 | 典型失效 |
| --- | --- | --- |
| ① 检索命中 | `top1_group in acceptable_groups`（case map 白名单） | `cs_0015` / `cs_0023` 同族 auto-close，top1 均为 `qa_040`，① 一判对一判错 |
| ② Style 路由 | `group_hints` → 关键词计数（`resolve_style_family`） | `cs_0026` top1=`qa_001` → `F2_tc148_wired`，客户已在「已换板/直供/短接限位」阶段 |
| ③ 生成质量 ②/④ | `ref_key_hits` 正则 + `dim4` 要求 ②=直接可发 | `cs_0025`/`cs_0027` test tier 无金标准回信 → 永不上「直接可发」 |

Round 1e 讨论常在「修评测框架 vs 修生成逻辑」间打转，因为**评测侧与 runtime 侧都在用规则假装会做语义判断**。  
「通用修复 vs 过拟合补丁」清单仍有价值，但按判定机制看，许多「通用修复」（domain 标签统一 acceptable、playbook 迁移）只是把机械规则从 **per-case** 扩到 **per-domain** — **本质仍是规则，不是判断**。

---

## 问题陈述（冻结表述）

English CS 流水线缺少一层**领域无关的语义等价 / 质量判断能力**，导致：

1. **检索评估**无法回答「Top1 内容是否语义上能答这封客户来信」，只能查 group_id 是否在白名单。  
2. **Style 路由**无法回答「客户当前处于排查流程的哪个阶段」，只能查 top1 group_hint 或关键词命中数。  
3. **生成质量评估**在无 Reference 回信时无法判断草稿是否可用，只能依赖 Joyce 真邮词表或一票否决。

**本 ADR 不否定** Phase 1 过渡手段（acceptable 组统一、test-tier 评分分支、prompt/style 微调），但要求显式标注为 **`[mechanical-stopgap]`**，不得被误认为终局方案。

---

## 决策

### 1. 引入 `engine/` 层 Semantic Judge（领域无关接口）

新增模块（命名暂定）：

```text
engine/
  semantic_judge.py      # 接口 + 默认 stub（规则回退）
  semantic_judge_llm.py  # 可选 LLM 实现（Phase 2a 后）
```

**不得** import `domains/topens` 常量；领域 rubric（测试要求清单、排查阶段枚举）由 `DomainConfig` / EvalPack 注入。

### 2. 三个判断点（统一抽象，分阶段接入）

| 判断 API（概念） | 输入 | 输出 | 优先接入 |
| --- | --- | --- | --- |
| `judge_retrieval_relevance` | 客户来信 + Top1 块（question/answer_en） | `{relevant: bool, confidence, rationale}` | **Eval 2a** |
| `judge_troubleshooting_stage` | 客户来信 | `{stage, rationale}`（可选 `style_family_hint`） | Runtime **2b** |
| `judge_reply_quality` | 客户来信 + 草稿 + rubric? | `{tier: 直接可发\|小改可发\|需重写, gaps[]}` | **Eval 2a** |

**Phase 2a（Eval-only）**：先改 `_scratch/eval/draft_22mail_scoring.py` 与 runners 的草稿逻辑，**不改变** runtime 发信路径。  
**Phase 2b（Runtime）**：`select_style` / workflow 可选调用 stage judge — 须 A/B 与 patch_off 对照，不得单独作为质量门禁达标依据。

### 3. 过渡手段：test-tier 评分分支（Phase 1 可并行，仍属 stopgap）

在 semantic judge 落地前，允许对 `tier=test` 且无 `## 客服回复` 的 case（T3/T5 等）：

| 允许 | 禁止 |
| --- | --- |
| ② 草稿输出 **建议** + ④=**待人工** | 框架改完自动 ④=通过 |
| 用 **测试要求清单** + 同族真邮作人工对照辅助 | 用测试要求作 **自动通过条件** |
| holdout 全量进 xlsx **人工签 H 列** | 以「框架已修」跳过 H 列 |

实现位置：`_scratch/eval/draft_22mail_scoring.py`（或正式 `evals/scoring/` 若后续迁入）。  
标签：**`[mechanical-stopgap]`** — 解决「无 ref 即永不上直接可发」的框架 bug，**不**替代 semantic judge。

### 4. 过渡手段：acceptable 组 taxonomy（Phase 1 P1）

允许按 `domains` 标签（如 `auto_close` + `dual_arm`）统一 acceptable 组模板，**前提**：

- 须做 **语义核实**（见 fix_classification §7.1），不得「命中率高就加 group_id」  
- PR / 清单标注 **`[mechanical-stopgap]`**  
- 长期由 `judge_retrieval_relevance` 弱化对静态白名单的依赖

### 5. Judge 自身的防过拟合约束（与实现同步，不可后补）

若 judge 使用 LLM：

1. **固定 judge prompt 版本** — 写入 trace / 报告 meta，禁止 silent 改动  
2. **Judge holdout** — 定期抽样人工核对 judge vs 人工四维；judge 准确率纳入质量报告  
3. **禁止反馈环** — judge 分数 **不得** 用于调生成 prompt、EvalPack brief、或采样策略（避免「machine 说过了就当过了」）  
4. **④ 发链依据** — 长期保留人工 xlsx H 列签字；judge 输出仅为 **初筛 / 草稿建议**  
5. **Eval 身份隔离** — judge **不得**读 `scenario_id` 做 per-case override（与 EvalPack 靶向注入同规）

---

## 非目标（Phase 2 内不做）

- 用 semantic judge **自动关闭**质量 Phase 1 或替代殷主管/人工 xlsx  
- 在 Round 1e 危机窗口内 **同时** 上大 judge + 摘 EvalPack + 改 acceptable（顺序见下）  
- 把 judge 训练成 Joyce 22 专用分类器（holdout / test tier 须持续有效）  
- 引入外部 agent 平台或多轮 judge 辩论

---

## 架构位置

```text
agents/cs_email_workflow.py
  ├─ library_router / retrieval          (现有)
  ├─ domains/prompt_style.select_style   (2b: 可选 stage judge 输入)
  ├─ generate_answer                     (现有)
  └─ engine/semantic_judge.*             (2b: 可选 post-gen 审计)

evals/runners/cs_22mail_batch_runner.py
  └─ draft_22mail_scoring / 正式 scoring
       ├─ [stopgap] acceptable_groups / test-tier 分支
       └─ [2a] judge_retrieval_relevance + judge_reply_quality
```

导入方向：`engine/semantic_judge` **不得** import 具体 domain；`domains/*/evals/` 可提供 rubric YAML。

---

## 建议实施顺序

| 阶段 | 动作 | 类型 |
| ---: | --- | --- |
| **Now** | 人工 xlsx（Joyce 抽 5–8 + holdout 全 5） | P0 人工 |
| **Now** | `--no-eval-pack` patch_off 对照 | P0 验证 |
| **Now** | test-tier 评分 → ④待人工（非自动通过） | P1 **`[mechanical-stopgap]`** |
| **Now** | auto_close acceptable 统一（语义核实后） | P1 **`[mechanical-stopgap]`** |
| **Now** | cs_0026 prompt / incomplete 审计拆分 | P1 生成/审计 |
| **2a** | `engine/semantic_judge.py` 接口 + eval 侧接入 + judge holdout 集 | 本 ADR 核心 |
| **2b** | runtime style stage judge（A/B） | 可选，须 2a 稳定 |
| **2c** | acceptable 白名单退化为 judge 失败时的 fallback | 收敛 |

**阻塞关系**：2a **不得**在质量 Phase 1 人工 xlsx 完成前作为「门禁达标」依据；可先并行开发接口与 shadow 模式（只写报告、不改 dim4）。

---

## 验收标准（Accept 条件）

### Phase 2a（Eval judge）

- [ ] holdout T1–T5：judge ① 建议与人工 xlsx E 列一致率 ≥ 人工标定的基线（先定目标，如 4/5）  
- [ ] test tier：judge ② 建议与人工 F 列对比，**无**「无 ref 即永不上直接可发」框架 bug  
- [ ] judge holdout 集（≥5 封，含 Joyce + holdout 混合）：人工 vs judge 一致率留档  
- [ ] 报告含 `judge_version` / `judge_rationale`；④ 仍默认待人工或人工确认  
- [ ] 单元测试：mock judge + stub 回退；`engine/` 无 topens 硬编码

### Phase 2b（Runtime judge，可选 Accept）

- [ ] patch_off 对照：style 误落率不高于 Phase 1 基线 + 指定 holdout case 改善  
- [ ] trace 含 `stage_judge` / `style_reason` 可审计  
- [ ] 无 EvalPack scenario_id 泄漏进 judge 输入

---

## 后果

### 正面

- 统一解释 holdout 失败与「通用 vs 过拟合」讨论打转的根因  
- Eval 与 runtime 共用同一语义抽象，换 domain 只换 rubric  
- 逐步缩小 acceptable / ref_keys / group_hints 维护面

### 负面 / 风险

- LLM judge 增加 eval 成本与延迟 — 2a 可仅 holdout + 抽样跑 judge  
- Judge 本身可被过拟合 — 靠 §决策 5 约束缓解  
- 团队可能误以为「上了 judge 就可跳过人工」— 本 ADR 明确禁止

---

## 参考实现锚点（Phase 1 现状）

```python
# ① 机械 membership — evals/runners/cs_22mail_batch_runner.py
top1_hit = (top1_group in ok) if ok else None

# ② 机械路由 — domains/prompt_style.py
if group_id and group_id in pack.group_hints:
    return fam, f"group_hint:{group_id}"

# ③ 机械 ②/④ — _scratch/eval/draft_22mail_scoring.py
# "Reference / reply grounding hints for ② draft (not semantic QA)."
if d2 != "直接可发":
    return "不通过"
```

---

## 相关文档

- [fix_classification_holdout_and_round1e_2026-07-10.md](../../_scratch/eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md) — 案例级分类 + §7 核实护栏  
- [组件化重构方案 · Phase 2 待办](./企业%20RAG%20邮件助手组件化重构方案.md#phase-2-待办建议顺序)  
- [`cs_client_requirement_standard.md`](../../_scratch/eval/cs_client_requirement_standard.md) — 甲方 test tier 与真邮分离

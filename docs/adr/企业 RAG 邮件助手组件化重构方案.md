
# 企业 RAG 邮件助手组件化重构方案

时间：2026年7月10日  
状态：**Phase 1 架构已落地** · **质量门禁未关闭**（Joyce 22 ④草稿 19/19 须警惕过拟合；holdout + 人工 xlsx 为 Phase 2 前置）  
关联：ADR-0003 English CS pipeline · [`domains/topens/README.md`](../../domains/topens/README.md) · [`evals/README.md`](../../evals/README.md)

## 目标

把当前 TOPENS 企业 RAG + 英文邮件助手 POC 重构为可复制的组件化产品架构：

- **同一套核心代码支持不同客户/行业/产品线**，换客户主要替换领域包、知识索引和评测包。
- **核心引擎领域无关**：检索、rerank、上下文构造、LLM 调用、后处理、审计接口不绑定 TOPENS。
- **领域配置可版本化**：产品注册表、索引路径、路由规则、术语规则、风格样例、prompt policy、catalog link 全部从代码常量迁出。
- **产品外壳可换品牌**：API 和 demo UI 不再硬编码 TOPENS/A3S/AD5S/TC148。
- **保留当前 POC 行为质量**：现有 CS email 流程、Gate R/K/G/S、22-mail eval、中文泄漏检测必须继续通过。

## 范围

**纳入范围**

- 重分层当前模块：
  - 产品外壳：`qa_server.py`、`demo/index.html`
  - 领域配置：`library_router.py`、`style_exemplars.py`、`pilot_en_context.py`、`context_builder.py` 中 TOPENS 常量与策略
  - 核心引擎：`retrieval_engine.py`，`engine/trace.py`，后续 `engine/routing.py` 等
  - 评测治理：正式 `evals/runners/` + `domains/topens/evals/`
- 建立 `domains/topens/` 领域包，承载当前 TOPENS 配置。
- 建立配置加载、schema 校验、默认值和失败提示。
- 将评测脚本从 scratch 资产升级为正式质量门禁（scratch 保留兼容 shim）。
- 保持当前 API 行为兼容，除新增可选参数外不破坏现有 demo。

**暂不纳入范围**

- 不接真实邮箱发送、CRM、ERP、工单系统。
- 不做多租户权限系统和企业 SSO。
- 不改当前向量库内容生产流程的大逻辑，只把索引绑定配置化。
- 不引入复杂多 agent 框架；先做确定性 CS Email Agent Workflow。
- 物理搬迁 `qa_server.py` → `apps/api/`（后续 Phase）。

## Phase 1 实施状态（2026-07-10）

| Plan 节 | 状态 | 交付物 / 说明 |
| --- | --- | --- |
| §1 目标分层 | **部分** | 已建 `domains/`、`agents/`、`engine/`、`evals/`；`retrieval_engine.py` 仍在根目录 |
| §2 领域包 v1 | **完成** | `domains/topens/` YAML + `prompts/` + `styles/` + `evals/gates.yaml`；`domains/loader.py` 校验 |
| §3 路由与检索 | **完成** | `library_router.py` 配置驱动；兼容 `LIBRARY_SPECS` 等符号；`engine/routing.py` 未物理拆分 |
| §4 Prompt / Style | **完成** | `PromptPack` / `StylePack`；`domains/prompt_style.py`；`style_exemplars.py` 为兼容 facade |
| §5 Context policy | **完成** | group exclusion、压缩长度从 `policies.yaml` 读取 |
| §6 Agent Workflow | **完成** | `agents/cs_email_workflow.py`；`qa_server` unified CS + eval runners 共用 |
| §7 API / Demo | **部分** | `--domain` / `trace` / `/api/config` 扩展；demo 品牌与产品列表已接 config；chips / side-by-side 仍本地硬编码 |
| §8 评测治理 | **完成** | 正式 runner + `_scratch/eval_runs/`；**EvalPack** 靶向 YAML（Round 1b–1e）；scratch shim 见下表 |

**单元测试**：119 passed（含 `test_eval_pack`、`test_cs_email_workflow`、`test_mock_domain`）。

### Joyce 22-mail 草稿评分（Round 1e · 2026-07-10）

| 轮次 | MVP19 ④通过 | 说明 |
| --- | --- | --- |
| post-refactor | 8/19 | 组件化后首跑 · [`scoring_draft_compare_2026-07-10.md`](../../_scratch/eval_runs/scoring_draft_compare_2026-07-10.md) |
| Round 1b | 9/19 | retrieval_boost / presales_brief 初版 |
| Round 1b re-run | 7/19 | cs_0002 Reference 0 指令修复前 |
| Round 1c | 13/19 | 故障三件套 cs_0021/0018/0003 + presales 强制链接 |
| Round 1d | 17/19 | cs_0016 + fan_out acceptable_groups + pinned_images |
| **Round 1e** | **19/19** | cs_0004 presales brief + cs_0020 四步 mandatory · [`round1e_compare_2026-07-10.md`](../../_scratch/eval_runs/round1e_compare_2026-07-10.md) |

> **过拟合警示**：上表 7→13→17→19 曲线是在 **同一组 19 封邮件** 上经 Round 1b–1e 多轮 **per-`cs_id` EvalPack 补丁** 达成，不能单独证明泛化。`mandatory N 步`、`presales_brief` 等规则若写死到具体措辞/场景，在新邮件上可能失效甚至帮倒忙。

### Holdout 验证（T1–T5 · 2026-07-10）

未参与 Round 1b–1e 补丁的 5 封（`cs_0023`–`cs_0027`，见 `gates.yaml` gate scenarios）：

| 集合 | ④草稿通过 | 说明 |
| --- | --- | --- |
| Joyce 22 MVP19 · Round 1e | 19/19 | 同集 5 轮靶向 |
| **Holdout T1–T5** | **1/5** | MVP-like **1/4** · 仅 cs_0024 通过 |

权威 batch：[`holdout_t1_t5_2026-07-10.json`](../../_scratch/eval_runs/holdout_t1_t5_2026-07-10.json)  
对比报告：[`holdout_t1_t5_compare_2026-07-10.md`](../../_scratch/eval_runs/holdout_t1_t5_compare_2026-07-10.md)  
草稿四维：[`scoring_draft_holdout_t1_t5_2026-07-10.md`](../../_scratch/eval/scoring_draft_holdout_t1_t5_2026-07-10.md)

```bash
python _scratch/eval_runs/run_holdout_t1_t5.py
```

**Phase 1 质量结论（当前）**：架构拆分与 EvalPack 机制 ✅；**④真邮质量目标未达成** — 须先完成 holdout 扩充 + **人工 xlsx 四维**（②直接可发、③图片配对），再更新本 ADR 质量行与 Phase 2 优先级。

修复分类清单（通用 vs 过拟合）：[`fix_classification_holdout_and_round1e_2026-07-10.md`](../../_scratch/eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md)

```bash
python evals/runners/cs_22mail_batch_runner.py --round round1e --generate --index en \
  --out _scratch/eval_runs/cs_22mail_round1e_2026-07-10.json
python _scratch/eval/draft_22mail_scoring.py --json _scratch/eval_runs/cs_22mail_round1e_2026-07-10.json
```

### 当前目录（实际）

```text
agents/
  cs_email_workflow.py     # CS email 确定性编排（route→retrieve→style→generate→audit→trace）
domains/
  loader.py models.py prompt_style.py eval_pack.py
  topens/
    domain.yaml products.yaml indices.yaml routing.yaml policies.yaml terminology.yaml
    prompts/               # cs_email + QA system prompts
    styles/                # family_router, principles, exemplars/
    evals/                 # gates.yaml + EvalPack YAML（见 evals/README.md）
engine/
  trace.py                 # RunTrace + context zh-leak 检测
evals/
  runners/
    run_cs_e2e_gate.py
    cs_22mail_batch_runner.py
    gate_report.py         # write_probe_markdown, gate scenario ids
library_router.py          # 兼容入口，内部读 DomainConfig
context_builder.py pilot_en_context.py style_exemplars.py generate_answer.py
qa_server.py demo/index.html
retrieval_engine.py        # 核心检索实现（待包装为 engine/retrieval.py）
```

### Scratch 兼容（评测）

| 用途 | 权威路径 | Scratch 兼容入口 |
| --- | --- | --- |
| Gate 9-case E2E | `evals/runners/run_cs_e2e_gate.py` | `_scratch/eval/run_cs_e2e_gate.py`（转发 + 可选 legacy 输出） |
| Joyce 22-mail | `evals/runners/cs_22mail_batch_runner.py` | `_scratch/eval/cs_22mail_batch_runner.py`（转发） |

```bash
# 正式 runner（报告 → _scratch/eval_runs/）
python evals/runners/run_cs_e2e_gate.py --index en

# 同时更新 Phase 0 基准 JSON + phase0_gate_probe.md
python evals/runners/run_cs_e2e_gate.py --index en --scratch-legacy-output
# 等价：python _scratch/eval/run_cs_e2e_gate.py --index en
```

Case map 正文仍在 `_scratch/eval/cs_email_query_map.json`（含 `expected_group_ids` / `alternate_group_ids` 用于 fan_out ①判定）；`domains/topens/evals/gates.yaml` 持指针与 gate 元数据。

### EvalPack 靶向机制（Round 1b–1e）

加载器：`domains/eval_pack.py` · 配置：`domains/topens/evals/*.yaml`

| 机制 | 文件 | 用途 |
| --- | --- | --- |
| `retrieval_boost()` | `retrieval_boosts.yaml` | 场景级 EN 检索 query 覆盖 |
| `presales_brief()` | `presales_briefs.yaml` | 售前权威事实 + 购买链接（生成时强制输出 URL） |
| `generation_brief()` | `generation_briefs.yaml` | 故障场景 Joyce 锚点 / mandatory 步数 |
| `pinned_reference()` | `pinned_references.yaml` | 注入 **Reference 0** 权威阶梯（优先于 Reference 1） |
| `context_force_include_groups()` | `context_overrides.yaml` | top1_excludes 下仍保留指定 group（如 qa_033） |
| `pinned_images()` | `pinned_images.yaml` | batch `images_used` 注入（如 cs_0005 太阳能截图） |

`generate_answer.py`：有 pinned reference 时跟 **Reference 0** 步序；有 presales brief 时强制包含全部购买链接。`cs_22mail_batch_runner.py` 合并 `pinned_images`。

## Plan

### 1. 建立目标分层

采用六层结构（Phase 1 以边界 + 导入方向为先，不全量搬文件）：

```text
apps/                     # Phase 2：qa_server 迁入 apps/api/
  api/
  demo/
agents/
  cs_email_workflow.py    # ✅ Phase 1
engine/
  trace.py                # ✅ Phase 1
  retrieval.py            # ⏳ 包装 retrieval_engine
  routing.py              # ⏳ 从 library_router 抽出算法层
  generation.py           # ⏳ LLM transport + prompt 渲染
  context.py              # ⏳ 通用 context 接口
  validation.py           # ⏳ audit/normalize 接口
domains/
  topens/                 # ✅ Phase 1
evals/
  runners/                # ✅ Phase 1
  reports/                # ⏳ 可选；当前用 _scratch/eval_runs/
```

导入方向：`agents` → `engine` + `domains`；`engine` **不得** import 具体 `domains/topens` 常量（当前 `engine/trace.py` 已满足）。

### 2. 领域包 v1

为当前 TOPENS 建立 `domains/topens/`：

| 资产 | 文件 | Phase 1 |
| --- | --- | --- |
| 领域元数据 | `domain.yaml` | ✅ |
| 产品注册 + catalog | `products.yaml` | ✅ |
| 索引绑定 | `indices.yaml` | ✅ |
| 路由规则 | `routing.yaml` | ✅ |
| 术语（stub） | `terminology.yaml` | ✅ stub |
| CS 上下文策略 | `policies.yaml` | ✅ |
| Prompt | `prompts/*.md` + `prompts.yaml` | ✅ |
| Style | `styles/` + `styles.yaml` | ✅ |
| Eval 元数据 | `evals/gates.yaml` + EvalPack YAML | ✅（case map 仍指向 scratch，含 acceptable_groups） |

配置加载器（`domains/loader.py`）输出：

```text
DomainConfig
  ├─ meta, products, catalog_links, indices, routing, response
  ├─ StylePack   # family_router, principles, holdout, exemplar 路径校验
  └─ PromptPack  # cs_email / QA zh|en system prompts
```

启动校验（已实现）：缺产品 id、缺索引路径、routing 引用未知产品、style exemplar 文件不存在、holdout 与 `gates.yaml` 不一致 → `DomainConfigError`。

尚未单独建模：`EvalPack` 对象（gate 配置仅在 YAML + `eval_pack.py` 函数加载）。

**Phase 1b 已完成**：EvalPack YAML + `eval_pack.py` loader；case map 补充 fan_out 场景的 `expected_group_ids`。

### 3. 路由与检索拆分

- **已完成**：`library_router.py` 从 `DomainConfig` 生成 `LIBRARY_SPECS` / `EN_CHROMA_DIRS` / `MERGED_CHROMA_DIRS` / `PRODUCT_CATALOG_LINKS`；`pick_library` / `unified_search` 读 `routing.yaml`。
- **待办**：`engine.routing` 通用模块；`Retriever.search(index_binding, …)` 包装层。

### 4. Prompt、风格与生成拆分

- **已完成**：prompt 迁入 `domains/topens/prompts/`；style 迁入 `domains/topens/styles/`；选择与组装在 `domains/prompt_style.py`；`generate_answer.py` 保留 LLM transport + normalize/audit；`style_exemplars.py` 为兼容 re-export。
- **待办**：`engine/generation.py` prompt renderer；validation pipeline 完全可配置化。

### 5. Context policy 配置化

- **已完成**：`policies.yaml` → `ResponsePolicy.context`（group exclusion、压缩长度、margin）。
- **待办**：图片/链接 per-mode 策略、EN fallback 规则写入配置。

### 6. Agent Workflow v1

**已实现** `agents/cs_email_workflow.py`：

```text
Input Email
→ route product line          (library_router.unified_search)
→ retrieve + enrich context   (hits_to_context, pilot_en_context)
→ build context + leak check  (context_builder, detect_context_zh_leak)
→ select style family         (domains.prompt_style.select_style)
→ generate draft              (generate_answer)
→ normalize + audit reply     (generate_answer 内 normalize + audit_cs_email_reply)
→ return answer + RunTrace
```

`RunTrace` 字段（`engine/trace.py`）：domain/product、route、index path、hit/group ids、prompt/style pack version、model、validation、zh leak、latency；token/cost 暂留空。

- `qa_server`：`unified-cs` + `cs_email` 走 workflow；`/api/ask` 支持 `include_trace`。
- `evals/runners/*`：`run_case` 委托同一 workflow。

### 7. API 与 Demo 产品外壳去领域化

**已完成**

- CLI：`--domain topens`、`--response-mode`、`--locale`、`--allowed-products`（`--allowed-libraries` 别名）。
- `/api/config`：`domain_display_name`、`brand`、`products`、`catalog_links`、`available_modes`。
- `demo/index.html`：标题、客服署名、产品下拉、catalog 从 `/api/config` 渲染。

**待办**

- Demo chips、`DEMO_SIDE_BY_SIDE`、工程师视图文案去硬编码。
- UI theme tokens / labels 全量 config 驱动。
- `qa_server` 迁入 `apps/api/`。

### 8. 评测治理正式化

**已完成**

- `evals/runners/run_cs_e2e_gate.py`、`cs_22mail_batch_runner.py`
- `domains/topens/evals/gates.yaml`（gate ids、22-mail ids、style holdout、case map 指针）
- 报告默认 `_scratch/eval_runs/`；`--scratch-legacy-output` 写 Phase 0 基准至 `_scratch/eval/`
- Gate 语义不变：R / K / G / S

## 验证标准

### 功能验收

| 项 | Phase 1 |
| --- | --- |
| TOPENS CS email demo 端到端 | ✅ 路径未改行为 |
| catalog / manual / 图片引用 | ✅ 配置与 workflow 一致 |
| `/api/ask` 向后兼容 + 新参数 | ✅ |
| `/api/config` 驱动 demo 产品列表 | ✅ 部分（chips 除外） |

### 架构验收

| 项 | Phase 1 |
| --- | --- |
| `engine/` 不绑定 TOPENS 常量 | ✅ `trace.py` 无 domain 硬编码 |
| 新产品线只改领域包 | ✅ products/indices/routing YAML |
| prompt/style/routing 不散落引擎 | ✅ 已迁入 `domains/topens/` |
| 第二 mock domain 零改 engine | ✅ `domains/mock/` + `tests/test_mock_domain.py` |

### 质量门禁

| 项 | Phase 1 |
| --- | --- |
| 单元测试 | ✅ **119 passed** |
| context zh 泄漏 | ✅ Gate 9/9 · 22-mail 22/22 PASS（[`cs_e2e_gate_compare_2026-07-10.md`](../../_scratch/eval_runs/cs_e2e_gate_compare_2026-07-10.md)） |
| Gate G 机械指标 | ✅ Top1/Library/zh_leak 对齐基线（同上） |
| Joyce 22-mail 机械指标 | ✅ Top1 · zh_leak 对齐 Round0（[`cs_22mail_compare_2026-07-10.md`](../../_scratch/eval_runs/cs_22mail_compare_2026-07-10.md)） |
| Joyce 22-mail ④草稿（MVP19） | ⚠️ **19/19** Round 1e · **同集过拟合风险** · [`round1e_compare_2026-07-10.md`](../../_scratch/eval_runs/round1e_compare_2026-07-10.md) · **须人工 xlsx 确认** |
| Holdout T1–T5 ④草稿 | ⚠️ **1/5**（MVP-like 1/4）· [`holdout_t1_t5_compare_2026-07-10.md`](../../_scratch/eval_runs/holdout_t1_t5_compare_2026-07-10.md) · **阻塞质量门禁关闭** |
| 人工 xlsx 四维 E–H | ⏳ **未做** — Joyce 22 抽样 + holdout 全量；②③优先 |
| 22-mail report 含 trace | ✅ runner 输出 `trace` + `context_zh_leak` |
| 配置校验用例 | ✅ loader + eval_pack 测试 + 启动 fail-fast |

### 回归标准

- 第一阶段不改变生成主路径行为，除 trace/config 字段新增外，不改变外部响应语义。✅
- Prompt 迁文件后关键约束仍在：`test_style_exemplars` + `test_build_cs_email_system_prompt_*`。✅
- 英文客服邮件：不输出中文、不编造承诺、不把 style 当事实、不暴露 gate 细节。✅（逻辑未改，靠 gate 续验）

## Phase 2 待办（建议顺序）

1. **[ADR-0004](./0004-semantic-judge-layer-for-cs-eval-and-routing.md)** · `engine/semantic_judge.py` — eval 侧 2a（检索/生成质量 judge + judge holdout）；runtime style stage 2b 可选。Phase 1 过渡手段（acceptable taxonomy、test-tier ④待人工）标 `[mechanical-stopgap]`，见 ADR 正文。
2. `engine/routing.py` + `engine/retrieval.py` 包装层；`library_router` 变薄。
3. `engine/generation.py` / `validation.py`；`generate_answer.py` 只保留 transport。
4. Demo 全量 config 驱动；`apps/api/` 外壳。
5. ~~`domains/topens/evals/` 迁入 case map 正文；`EvalPack` loader。~~ EvalPack loader ✅；case map 正文仍留 scratch（acceptable_groups 已补）
6. ~~第二个 mock domain 包 + 启动校验回归测试。~~ ✅ `domains/mock/`（2026-07-10）

## 默认假设

- 默认领域为 `topens`。
- 默认产品线仍为 A3S、AD5S、TC148。
- 默认模式为 `cs_email`，默认语言为英文。
- Phase 1 **架构**以「行为不变的拆分 + EvalPack 机制」为目标 — ✅ 已落地。
- **质量**不在同集反复打补丁后宣布达成；EvalPack per-case YAML 是 eval 稳定化手段，可泛化规则应迁入 `domains/topens/presales_playbooks.yaml` 等领域配置（例：`two_independent_gates` → 2× A8131）。
- 评测 gate 语义不变；正式 runner 在 `evals/runners/`，scratch 仅兼容。
- 暂不引入外部 agent 平台；本地 workflow、trace、tool boundary 已打通。

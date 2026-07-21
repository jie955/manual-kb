# English CS POC · 执行清单

> **Tracking Artifact** — 日常勾选与产物链接；**非** Execution SoR。Phase / DoD / 风险 / Owner → [Implementation Plan v1.3](./cs_en_implementation_plan.md)；Gate 定义 → [ADR-0003](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md)；甲方标准 → [验收标准](./cs_client_requirement_standard.md)。

**架构决策**：[ADR-0003](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md)（**Proposed** · 取代 ADR-0002 客户路径）· [ADR-0002](../../docs/adr/0002-english-cs-cross-lingual-retrieval-localized-generation.md)（Superseded）  
**工程交付计划**：[Implementation Plan v1.3](./cs_en_implementation_plan.md)  
**甲方验收标准**：[验收标准](./cs_client_requirement_standard.md)（**Business SoR** · 叶天洲 §一 + **殷主管 §二 MVP 优先**）  
**Query 真源**：[`cs_email_query_map.json`](./cs_email_query_map.json) · [`customer-query-candidates.md`](../../samples/customer-service-emails/customer-query-candidates.md)  
**状态**：Phase **1b 出口已接** · EN-index Gate K **13/14** · E2E（EN-index）**cs_0013/cs_0026 OK** · **Wave 1 核心检索项已完成** · 2026-07-08  
**DoD 对照**：[`cs_en_adr_dod_gap.md`](./cs_en_adr_dod_gap.md) · **客户 MVP 范围**：[`client_mvp_two_series_progress.md`](./client_mvp_two_series_progress.md)

### Wave 1–4 总览（发链前必过）

| Wave | 目标 | 工期 | 状态 |
| --- | --- | ---: | :---: |
| **Wave 1** | 真邮四维 80% 线 · EN Gate K 14/14 · 探针诊断 | 3–5 天 | ☐ |
| **Wave 2** | 演示收窄两系列 · UI 四项 | 1–2 天 | ☐ |
| **Wave 3** | 说明书 + 产品链接入 Demo | 3–5 天 | ☐ |
| **Wave 4** | 部署稳定 URL → 发殷主管试跑包 | 1–2 天 | ☐ |

**出口（发链条件）**：验收标准 §二 MVP-0-1～0-6 + §2.3 **19 封真邮四维 ≥16/19** + Phase 5.0 部署留档。

**验收口径（冻结）**：Gate 探针集（~10 封）分数 **仅作诊断** — 定位检索/生成/图片/机型；**发链判据** 为 [`22封真邮_四维评分表.xlsx`](./22封真邮_四维评分表.xlsx) 算出的通过率（见 [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md)）。探针经 overlay 精修，**不可**替代真邮 80% 对外汇报。

**禁止**：Wave 1 未过真邮 80% 线即部署发链 · 以「请殷主管帮我们测」替代内部 Gate · **只用探针分数替代真邮通过率作对外汇报依据**

---

## 核心（若偏差则白做）

| 优先级 | 要求 |
| ---: | --- |
| **P0** | **英文进 → 英文出 + 准确**（E2E：找对故障路径、步骤忠实、不瞎编） |
| **P1** | **像真实客服信**（格式、语气）— **仅 P0 成立后的加分** |
| **发版** | **交付前**用验证资产自验达标；**不依赖**甲方多轮试跑才收敛 |

甲方商务对话里「另一家：做出来 → 我测 → 反馈 → 调阈值 → 更准」= **协作参照**，不是本次 POC 的交付模型，也不是 Workflow 产品立项。

---

## 验证资产（发版前自验 · 非「仅 22 封邮件」）

| 资产 | 规模 | 用途 |
| --- | --- | --- |
| [`samples/customer-service-emails/`](../../samples/customer-service-emails/) | **27 场景**（真实 22 + 甲方测试 5） | 客户原话 + Reference 回信 + 多轮/售前/已排查 |
| [`cs_email_query_map.json`](./cs_email_query_map.json) | **176 query** | Gate / 检索 eval |
| [`reply-principles-and-tips.md`](../../samples/customer-service-emails/reply-principles-and-tips.md) | 原则 doc | P1 体裁与 SOP |
| [**cs_en_style_corpus_plan.md**](./cs_en_style_corpus_plan.md) | 22 封风格训练语料 | Style Card · skeleton · [`style_exemplars.py`](../../style_exemplars.py) Phase 3.2 ✅ |
| [`cs_side_by_side_demo.md`](./cs_side_by_side_demo.md) | 3 case + Oracle | 上限探针 + 演示样例 |
| [**cs_22mail_eval_readme.md**](./cs_22mail_eval_readme.md) + [**22封真邮_四维评分表.xlsx**](./22封真邮_四维评分表.xlsx) | Joyce **22 封** · MVP 子集 **19 封** | **发链 80% 判据**（探针仅诊断） |
| 三库 `chroma_captioned` / `chroma_captioned_en` | A3S / AD5S / TC148 | Grounded 真源 |

**覆盖面**：故障排查、售前、多轮、限位 fork、保修复合、out-of-corpus 拒答等 — 已覆盖大部分与客户交流的内容形态。**发版门禁在此跑通**，不能把甲方当成回归测试台。

---

## Existing Capabilities（Already Implemented · 本轮不改）

| 能力 | 状态 | 本轮 |
| --- | --- | --- |
| `embedding_text` = `question + answer_zh` | ✅ | 否 |
| `customer_reply_templates` 隔离 | ✅ | 否 |
| 三库 bge-m3 chroma + 中文 eval 门禁 | ✅ | 回归对照 |
| Hybrid / rerank | ✅ | 配置冻结，仅验证 |
| CS 英文语料 + query map | ✅ | **发版 Gate 消费** |
| `reply-principles-and-tips.md` | ✅ | P1 参照 |
| 中文 `generate_answer` | ✅ | 保留；`locale` / `response_mode` |

---

## New Work（按优先级）

| 优先级 | Task | 产出 | Exit |
| ---: | --- | --- | --- |
| **P0** | **Task 1 · E2E 检索 Gate** | `cs_en_retrieval_baseline.json` + `.md` | Gate 集 Top1/Top3/MRR；miss 有解释与改法 |
| **P0** | **Task 4 · 双维评分** | `cs_human_eval_scores.md` 或门禁包内 | **Grounding 优先**；无 critical |
| **P0** | **发版门禁包（内部）** | [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) | 我方填完 Gate case；**不**等甲方 |
| **P0** | **统一入口 + 自动路由** | `qa_server` / demo | 客服不选库；机型路由或 fan-out |
| **P0** | Demo 英进英出 | 同上 | EN Email → EN Reply |
| **P0** | Task 0 · Oracle | `cs_en_oracle_gen_smoke.md` | 定位瓶颈；**非**发版充分条件 |
| **P1** | Task 3 · locale + mode | `generate_answer.py` | `cs_email` 可调用 |
| **P1** | Side-by-side 演示 | `cs_side_by_side_demo.md` | #8 #13 #22 |
| **P2** | Task 2 · enrich | overlay + 重 embed | Gate 不达标时 · **Post G8c：Gate 14/14 · all 78%** |

### 执行顺序（推荐）

```text
Phase 0 ✅ → Wave 1（准确率）→ Wave 2（范围）→ Wave 3（三类内容）→ Wave 4（部署发链）→ 殷主管试跑
```

历史顺序（Task 3→0→1→4）已收敛进 **Wave 1–4** 勾选表（见下）。日常以 Wave 表勾选为准。

**禁止**：以「先交付 Demo → 甲方测 → 再改一版」作为收敛计划。

**ADR-0003 四道门禁**：Gate R → K → **G**（Grounding）→ **S**（Style）— **仅 Gate K 通过不可演示**。Phase 0 顺序见 [Implementation Plan §4](./cs_en_implementation_plan.md#4-phase-0--stop-the-bleeding12-天)。

---

## Phase 0 · Tracking（→ Plan §4 · 0.0–0.3）

| Phase | Task | 状态 |
| --- | --- | :---: |
| **0.0** | Extract `build_context_block` → `context_builder.py`（Zero Behavior Change） | ☑ |
| **0.1** | EN Context Policy：`locale=en` 不注入 `content_zh`；Prompt 对齐 | ☑ |
| **0.2** | Pilot E2E：`cs_0001` · `cs_0008` · `cs_0013` | ☑ [`phase0_pilot_replies/`](./phase0_pilot_replies/) |
| **0.3** | Internal Review → G/S 探针 | ☑ [`phase0_reference_style_review.md`](./phase0_reference_style_review.md) · 殷主管待 |
| 并行 | EN_READINESS → [`cs_en_readiness_scan.md`](./cs_en_readiness_scan.md) | ☑ Gate blocking **2** (tc148) |
| 并行 | `run_cs_e2e_gate.py` | ☑ [`phase0_e2e_gate_probe.md`](./phase0_e2e_gate_probe.md) |
| **1a** | Pilot English Retrieval Index | ☑ [`phase_1a_pilot_en_index.json`](./phase_1a_pilot_en_index.json) |
| **1b** | Full EN index（三库 `chroma_captioned_en`） | ☑ [`phase_1b_full_en_index.json`](./phase_1b_full_en_index.json) · a3s **121** · ad5s **100** · tc148 **2** |
| **1b** | EN-index baseline（Gate K 主口径） | ☑ Gate **13/14** · all **54.1%** · [`cs_en_retrieval_baseline_en.json`](./cs_en_retrieval_baseline_en.json) |
| **BL-RET-01a** | 三库 ts + 四 manual 重 embed（`doc_type`） | ☑ [`bl_ret_01a_batch_report.json`](./bl_ret_01a_batch_report.json) |
| **merge** | ts + manual → `unified/*/chroma_merged` | ☑ [`merge_model_chroma_report.json`](./merge_model_chroma_report.json) · **Demo 未接** |
| **G9+G10** | `cs_0026` / `cs_0013` 检索修复（ZH-index overlay） | ☑ |
| **G11** | G9/G10 → **EN-index** overlay | ☑ [`phase_cs_en_task2_g11_en_overlay.py`](./phase_cs_en_task2_g11_en_overlay.py) · Gate **13/14** |
| **1b 出口** | `qa_server` / `run_cs_e2e_gate` 英文路径 → EN-index | ☑ `library_router.load_unified_libraries(index=en)` |
| **3.2** | Style exemplars → `style_exemplars.py` + pytest | ☑ hold-out · 族路由 · `run_cs_e2e_gate` `style` 字段 |

---

## Wave 1 · 准确率（攻克殷主管 §二「先攻克准确率」· 3–5 天）

> **出口**：EN-index Gate K **14/14** · **MVP 真邮子集 19 封四维 ≥16/19 通过**（§2.3 严格线）· 门禁包（探针）填完 · **无未书面接受的 critical**  
> **主 KPI**：**22 封真邮四维通过率**（发链判据）；Gate G/S 探针 = **诊断**；Gate K = **中间指标**

### 1.0 真邮基线 · Round 0（G11 切 EN 路径之后 · 修库之前）

| # | 任务 | 产物 / 命令 | 状态 |
| ---: | --- | --- | :---: |
| 1.0.1 | 完成 **§1.1.5**（EN-primary 客户路径）后，[`cs_22mail_batch_runner.py`](./cs_22mail_batch_runner.py) 对 Joyce **22 封**跑 E2E（`--index en --generate`） | [`cs_22mail_eval_round0.json`](./cs_22mail_eval_round0.json) | ☐ |
| 1.0.2 | 在 [`22封真邮_四维评分表.xlsx`](./22封真邮_四维评分表.xlsx) **「基线评分」** sheet 四维打分 | 见 [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md) | ☐ |
| 1.0.3 | 记录 **Round 0 通过率**（MVP 子集 19 封 · ④严格线） | 写入 xlsx 底部汇总 + readme 变更记录 | ☐ |
| 1.0.4 | 按 `fail_tag` 统计：检索 / 生成 / 图片 / 机型 — 定 Wave 1.2 优先级 | 若 ③ 拖后腿 → 加图片专项（§1.2.11） | ☐ |
| 1.0.5 | **路径留档**：Round 0 与 Round 1 **必须同一路径**（EN + `cs_email`）；若 legacy 快照标 `path=zh-index-legacy` | 禁止与 EN Round 1 直接比 | ☐ |

**四维（严格线）**：①对 · ②**直接可发** · ③非{图不对,该配没配} → ④通过。「小改可发」**不算**通过。

### 1.1 EN 检索 Gate K（12/14 → 14/14）· G11

| # | 任务 | 产物 / 命令 | 状态 |
| ---: | --- | --- | :---: |
| 1.1.1 | 从 [`cs_en_retrieval_baseline_en.json`](./cs_en_retrieval_baseline_en.json) 列出 **2 条 EN miss**（`csq_071` #12 · `csq_078` #13）并写 miss 原因 | 备注写入 baseline `.md` 或 Task2 优先级表 | ☐ |
| 1.1.2 | **G11** · G9/G10 + #12/#13 limit overlay 迁移 EN 索引 | [`phase_cs_en_task2_g11_en_overlay.py`](./phase_cs_en_task2_g11_en_overlay.py) · EN re-embed 留档 | ☐ |
| 1.1.3 | 对迁移后仍 miss 的 EN 条补 overlay / enrich | overlay json · Task2 优先级表 | ☐ |
| 1.1.4 | 重跑 EN baseline：`python _scratch/eval/run_cs_en_retrieval_baseline.py --index en` | [`cs_en_retrieval_baseline_en.json`](./cs_en_retrieval_baseline_en.json) · Gate **14/14** | ☐ |
| 1.1.5 | **`library_router` / `qa_server` 英文客服路径改打 EN-primary**（`chroma_captioned_en`） | `run_cs_e2e_gate.py --index en` · 无 zh leak | ☐ |
| 1.1.6 | ZH-index 回归：Gate 14/14 **不得回退** | 对比 [`cs_en_retrieval_baseline.json`](./cs_en_retrieval_baseline.json) | ☐ |

**运维**：embed 同一路径 **禁止并行 job**；G10 生产库与 `phase_cs_en_a_line_batch_overlay.py` **勿同时跑**。

### 1.2 Critical case · 知识修库 + 生成（E2E 非 Oracle）

| # | Case | 当前 G | 任务清单 | 状态 |
| ---: | --- | ---: | --- | :---: |
| 1.2.1 | **#13** `cs_0013` · a3s | 4 | Joyce 四步 `qa_022` overlay 已做；**F4 exemplar** 签名人改 Joyce；`filter_hits_for_cs_email` 剔除 qa_034 电机直测步；E2E `--generate` 对照 Reference | ☐ |
| 1.2.2 | **#22** `cs_0022` · ad5s | **2** | §九双臂场景 `answer_en` 补写；真邮 **A 线** overlay 进 chroma；E2E 覆盖安全反转 3s / limit A·B / 单臂 isolate（见 [`cs_side_by_side_demo.md`](./cs_side_by_side_demo.md) Case C） | ☐ |
| 1.2.3 | **#8** `cs_0008` · tc148 | 3 | 端子 **4#/5#** 勿写成 11#/12#；补「先断延长线换短线」；承认已 jumper（内部 Gate · **MVP 演示可隐藏 TC148**） | ☐ |
| 1.2.4 | **#1** `cs_0001` · a3s | — | 路由 `qa_011` · 生成步骤 **DIP #3**；`ad5s` `qa_010` #5 矛盾 **书面登记**待殷主管裁定 | ☐ |
| 1.2.5 | **T1** `cs_0023` · ad5s | 3 | 检索 `qa_040` 已 OK；生成 FORCE/SOFT STOP/DIP3 步序提到 **≥4**；体裁补 Name 表单句（若 Reference 需要） | ☐ |
| 1.2.6 | **T4** `cs_0026` · a3s | 3 | Top1 已修（G9）；生成走 **qa_001** 排查梯非限位组；G/S 提到 **≥4** | ☐ |
| 1.2.7 | **#15** `cs_0015` · ad5s | — | E2E 跑通 + 填门禁包（§九双臂相关） | ☐ |
| 1.2.8 | **#18** `cs_0018` · a3s | — | E2E 跑通 + 填门禁包（探针） | ☐ |
| 1.2.9 | **#4** `cs_0004` · a3s | — | 门禁包 **未跑** — 补跑 E2E + G/S（探针诊断） | ☐ |
| 1.2.10 | **#3** `cs_0003` · a3s | — | 门禁包 **未跑** — 补跑 E2E + G/S（探针诊断） | ☐ |
| 1.2.11 | **图片专项**（若 Round 0 ③ 失败率偏高） | — | 修 `images[]` 检索/展示 · Demo 回信内嵌图 · 勿留到 Wave 4 | ☐ |

**个案脚本参考**：[`phase_cs_en_qa022_joyce_overlay.py`](./phase_cs_en_qa022_joyce_overlay.py) · [`cs_en_task2_repair_priority.md`](./cs_en_task2_repair_priority.md) · G11 [`phase_cs_en_task2_g11_en_overlay.py`](./phase_cs_en_task2_g11_en_overlay.py)

### 1.3 探针诊断 · 真邮复测 · 80% 线

| # | 任务 | 产物 / 命令 | 状态 |
| ---: | --- | --- | :---: |
| 1.3.1 | Gate 探针 E2E：`python _scratch/eval/run_cs_e2e_gate.py --generate`（需 `QA_API_KEY`） | [`cs_e2e_gate_results.json`](./cs_e2e_gate_results.json) · **诊断用** | ☐ |
| 1.3.2 | 填完 [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md)：System Reply · retrieval_group · **G** · **S** | 探针无空行 · **不可替代**真邮 80% | ☐ |
| 1.3.3 | Reference 对照：#1 · #8 · #13 逐步级核对（[`phase0_reference_style_review.md`](./phase0_reference_style_review.md)） | 探针诊断附录 | ☐ |
| 1.3.4 | **Critical 清零**或书面「已知限制」：端子 · DIP · 机型 · 编造步骤 | 探针 + 真邮均适用 | ☐ |
| 1.3.5 | **Round 1 复测**：22 封真邮重跑 E2E → [`22封真邮_四维评分表.xlsx`](./22封真邮_四维评分表.xlsx) **「复测评分(Wave1后)」** | 与 Round 0 同路径 | ☐ |
| 1.3.6 | MVP 子集 **19 封 ≥16 封** ④通过（严格线） | 满足验收标准 §2.3 | ☐ |
| 1.3.7 | Round 0 → Round 1 **通过率提升**留档一行（内部汇报用） | xlsx + readme | ☐ |
| 1.3.8 | 可选：Joyce **抽审 5 封** 或第二人交叉评分 disputed case | 备注写入 xlsx | ☐ |
| 1.3.9 | 探针 Gate **S** median **≥3**（体裁；不掩盖真邮未达标） | 门禁包汇总 | ☐ |
| 1.3.10 | 导出 Round 1 汇总 → [`cs_22mail_eval_round1.json`](./cs_22mail_eval_round1.json)（待建） | git-friendly 留档 | ☐ |

**MVP 80% 分子集（19 封 · 不含 TC148 #8–#10）**：全表见 [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md#mvp-80-子集--19-封清单)。

**通过线**：**≥16/19** ④通过（≥84%）· **不是** Gate 探针 8/10 或 G≥4 子集。

### Wave 1 · Exit Checklist

- [ ] EN-index Gate K **14/14**（G11 · [`cs_en_retrieval_baseline_en.json`](./cs_en_retrieval_baseline_en.json)）
- [ ] 客户路径检索走 **EN-primary**
- [ ] Round 0 + Round 1 真邮评分完成（xlsx + json 留档）
- [ ] MVP 真邮子集 **≥16/19** ④通过（严格线）
- [ ] [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) 探针填完（诊断）
- [ ] **无未书面接受的 critical**
- [ ] #22 真邮四维 ④通过（当前最大短板）

---

## Wave 2 · 演示范围收窄（殷主管 §二 两系列 · 1–2 天）

> **出口**：客服 Demo 仅暴露 **a3s + ad5s** · UI 四项验收勾选 · 示例 chip 对齐 MVP 子集

| # | 任务 | 产物 / 验证 | 状态 |
| ---: | --- | --- | :---: |
| 2.1 | `qa_server` / `library_router` 增加 **`--allowed-libraries a3s,ad5s`**（或 env）演示模式 | TC148 **不加载** · 误路由消除 | ☐ |
| 2.2 | 启动命令文档化（Tracking §部署） | 见下「MVP 演示启动」 | ☐ |
| 2.3 | UI 验收 ①：客服路径**看不到**「型号库」下拉 | 人工勾选 | ☐ |
| 2.4 | UI 验收 ②：**#13 chip**（或 T4）无需选库 → `Product line: A3S · auto` | 替代原 #8/TC148 chip 验收 | ☐ |
| 2.5 | UI 验收 ③：结果区展示 **`Product line: … · auto`** | 人工勾选 | ☐ |
| 2.6 | UI 验收 ④：Engineer 可展开中文步骤与 force library | 人工勾选 | ☐ |
| 2.7 | Demo **example chips** 换成真邮代表：**#13 · #22 · #15 · #1**（Joyce 22 封 · 非 Gate 探针） | `demo/index.html` | ☐ |
| 2.8 | 主面板 **仅 English Reply**；中文 chunk / Internal notes **不可见**（cs-email 模式） | 截图留档 | ☐ |
| 2.9 | 回信区展示 **配图**（`images[]`）与 **参考链接**（`links[]` 可点击项） | 至少 #13 · qa_011 有图可验 | ☐ |
| 2.10 | 更新 [`client_mvp_two_series_progress.md`](./client_mvp_two_series_progress.md)「隐藏 TC148」行 → ✅ | 进度表 | ☐ |

**MVP 演示启动（Wave 2 后推荐）**：

```powershell
python qa_server.py --unified-cs --demo-presentation cs-email --allowed-libraries a3s,ad5s --images-dir _scratch/run-006/images --port 8765
```

> `--allowed-libraries` 待 Wave 2.1 实现；实现前用文档标注「工程师模式勿演示 TC148 case」。

### Wave 2 · Exit Checklist

- [ ] 演示范围 **仅两系列**（TC148 对客服不可达）
- [ ] UI 四项 **全部勾选**
- [ ] 示例 chips 与 MVP 子集一致
- [ ] 图文回信在 Demo 可见（英文 + 图）

---

## Wave 3 · 三类内容同一入口（排查 + 说明书 + 产品链 · 3–5 天）

> **出口**：[`client_mvp_two_series_progress.md`](./client_mvp_two_series_progress.md) 三类内容 Demo 可达 · 排查 Top1 **不因 manual 接入而污染**  
> **B 轴并行计划（不表示 Wave 1/C 轴进展）**：[`pdf_manual_parallel_track.md`](./pdf_manual_parallel_track.md)

### 3.1 说明书接入 unified-cs

| # | 任务 | 产物 / 路径 | 状态 |
| ---: | --- | --- | :---: |
| 3.1.1 | 确认 **BL-RET-01a** merge 产物可用（[`merge_model_chroma_report.json`](./merge_model_chroma_report.json)） | ts + manual `chroma_merged` | ☐ |
| 3.1.2 | `LIBRARY_SPECS` / router 注册 **manual 库**（A3S · `chroma_enriched` **195** 向量） | 代码 + 配置留档 | ☐ |
| 3.1.3 | A3S 说明书源：[`vlm_a3s_full/README.md`](../vlm_a3s_full/README.md) · PDF `samples/manuals/A3S,A5(S),A8(S)说明书.pdf` | VLM **46/46** ✅ | ☐ |
| 3.1.4 | Demo 可 **检索并展示** manual 命中（工程师模式先验 · 客服路径按需 fan-out 或低分阈值） | 手测 1 条安装/端子类 query | ☐ |
| 3.1.5 | AD5S 补 **3 页 VLM fail**（[`vlm_ad5s_full`](../vlm_ad5s_full) **45/48**） | failed 页清单 + 重跑 | ☐ |
| 3.1.6 | AD5S manual 注册（**213** 向量） | 同 3.1.2 | ☐ |
| 3.1.7 | **跨 doc_type 检索**：manual 命中 **不挤占** troubleshooting Top1（BL-RET-01a 过滤 / rerank） | Gate 子集复跑 Top1 无回退 | ☐ |
| 3.1.8 | 更新进度表「说明书 · Demo 可搜/可看」→ ✅ | `client_mvp_two_series_progress.md` | ☐ |

### 3.2 产品链接（一期：B 全 + A 静态）

| # | 任务 | 说明 | 状态 |
| ---: | --- | --- | :---: |
| 3.2.1 | **B 类** · 排查内 `links[]`：A3S 多组 URL 仍散落在 `answer_en` prose → **结构化进 `links[]`** | 对照 [`a3s_18h1_handtest_issues.md`](./a3s_18h1_handtest_issues.md) | ☐ |
| 3.2.2 | **B 类** · AD5S `links[]` 覆盖优于 A3S — 抽查 **43 组**缺链组清单 | [`bl_v1_04_execution_record.md`](./bl_v1_04_execution_record.md) | ☐ |
| 3.2.3 | **COMPLIANCE-011** · qa_011 Drive 链：与殷主管确认 Demo **能否展示**；定 strip / 折叠 / 不可点方案 | [`a3s_18h1_handtest_log.md`](./a3s_18h1_handtest_log.md) §二 | ☐ |
| 3.2.4 | **A 类** · catalog 参数册：`samples/catalog/*.pdf` — 一期 **不 ingest**；Demo 加 **静态 topens 产品页链**（A3S 族 / AD5S 族各 1） | UI 脚注或侧栏 | ☐ |
| 3.2.5 | Demo「参考链接」UI：有 `links[]` 的组 **全部可点**；无链组不裸奔 prose URL | 手测 #13 · qa_011 · ad5s qa_003 | ☐ |
| 3.2.6 | 更新进度表「产品链接」→ B ✅ · A 静态 ✅ | `client_mvp_two_series_progress.md` | ☐ |

### 3.3 真邮 A 线（检索切片 · 与准确率联动）

| # | 任务 | 说明 | 状态 |
| ---: | --- | --- | :---: |
| 3.3.1 | 22 封真邮 **未 overlay chroma** — 优先 #15/#19/#22 场景 EN symptom 进 `embedding_text_en` | [`cs_en_a_line_step0_labels.md`](./cs_en_a_line_step0_labels.md) | ☐ |
| 3.3.2 | 批量 overlay 脚本跑通 **单库串行** embed（禁并行竞态） | `phase_cs_en_a_line_*` 留档 | ☐ |
| 3.3.3 | EN-index 复跑 baseline · MVP 子集 Top1 **不回退** | baseline json | ☐ |

### Wave 3 · Exit Checklist

- [ ] A3S + AD5S **说明书**在 Demo 可检索/可看
- [ ] 排查 Top1 Gate **14/14 保持**（manual 接入后）
- [ ] 产品链 **B 类**主要组可点击；**A 类**静态链已挂
- [ ] COMPLIANCE-011 **有书面方案**（哪怕「维持不可点」）
- [ ] `client_mvp_two_series_progress.md` 三类内容 **≥⚠️→✅**

---

## Wave 4 · 部署 · 发殷主管测试链接（1–2 天）

> **出口**：稳定公网 URL · 试跑包 · 内部 Gate 包完备 · **可交付殷主管试跑**（[`cs_en_adr_dod_gap.md`](./cs_en_adr_dod_gap.md)）

| # | 任务 | 产物 | 状态 |
| ---: | --- | --- | :---: |
| 4.1 | **Wave 1 Exit** 全部勾选 | — | ☐ |
| 4.2 | **Wave 2 Exit** 全部勾选 | — | ☐ |
| 4.3 | **Wave 3 Exit** 全部勾选（或书面登记说明书/链接为「试跑后迭代」） | — | ☐ |
| 4.4 | 部署 **Phase 5.0**：`qa_server --unified-cs` 至平台/服务器 | 稳定 **HTTPS URL** | ☐ |
| 4.5 | 部署物打包：三库 EN chroma · merged manual（若已接）· **双系列图片目录** · env/API key | 部署清单 md | ☐ |
| 4.6 | 生产启动参数与本地一致：`cs-email` · `allowed-libraries a3s,ad5s` · images-dir | 写入本节「部署留档」 | ☐ |
| 4.7 | 冒烟：公网 URL 跑 **#13 · #22 · T1** 三条 E2E | 截图或 json | ☐ |
| 4.8 | 编制 **殷主管试跑包**：① URL ② **5–10 条建议试跑邮件（从 Joyce 22 封真邮挑 · 覆盖 a3s/ad5s 典型场景）** ③ 已知限制 ④ 反馈表（cs_id · 四维 · 备注） | [`yin_supervisor_pilot_pack.md`](./yin_supervisor_pilot_pack.md)（待建） | ☐ |
| 4.9 | 商务发链给殷主管 · **不**同步约叶天洲（须殷主管认可后 F-3） | 邮件/微信留档 | ☐ |
| 4.10 | 建立 **试跑反馈 → 个案 fix → 小版本** 迭代节奏（不推翻 Wave 1 Gate） | issue 列表或门禁包附录 | ☐ |

### 部署留档（Wave 4 填）

| 项 | 值 |
| --- | --- |
| **公网 URL** | _（部署后填写）_ |
| **启动命令** | _（部署后填写）_ |
| **部署日期** | _ |
| **索引版本** | EN `chroma_captioned_en` · merge _（若有）_ |
| **范围** | `a3s` + `ad5s` only |

### Wave 4 · Exit Checklist

- [ ] 公网 URL 可访问 · 三条冒烟通过
- [ ] 殷主管试跑包已发出
- [ ] [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) 与 Wave 1 一致（无回退）
- [ ] 验收标准 §六「**满足殷主管第一阶段（可发测试链接）**」→ **可勾选**

---

## 本期明确不做（Wave 1–4 边界）

- **一键发送**（MVP-1-1 加分 · Out of Scope）
- **全型号 / TC148 进殷主管演示**
- **catalog PDF ingest**（一期静态链即可）
- **未过真邮 80% 线（19 封 ≥16/19 严格线）就发链接**
- **只用 Gate 探针 G/S 或 Gate K 分数替代真邮通过率作对外汇报依据**

---

## 三库：不合并索引，但必须统一客服入口

| 问题 | 决策 |
| --- | --- |
| 三库 chroma **要不要合成一个**？ | **不要**。分库保留（品类异构、TC148 仅 2 组、中文 eval 分库已验证）。 |
| 客服 **要不要手动选库**？ | **不要**。对一线不友好；#8 在 A3S 上测 = 必错。 |
| 发版怎么做？ | **单一粘贴入口** + 服务端 **自动路由**（机型/关键词）或 **三库 fan-out 取全局 Top1**；工程师模式可保留选手册库。 |

**当前 Demo**：型号库下拉 + `:8765/8766/8767` 三分端口 = **工程联调工具**，**≠** 发版 UX。发版前须实现路由并隐藏客服侧选库。

**实现候选**（见 ADR-0002 §7）：

1. 解析来信中的 `Product Model` / TC148 / A3S / AD5S → 单库检索  
2. 解析失败 → 三库并行检索，取最高分（带 `library` 标签与低分拒答）  
3. Gate 集须覆盖路由正确性（#8→tc148、#13→a3s 等）

---

## Gate 集（Task 1 / Task 4 / 发版门禁）

**direct 10 场景 · Tier A verbatim**：

| 场景 | 库 | 备注 |
| --- | --- | --- |
| #8 #9 #10 | tc148 | |
| #13 | a3s | 期望走停/力矩，非限位 Top1 |
| #15 #19 | ad5s | |
| #18 | a3s | |
| T1 T3 T4 | ad5s / tc148 / a3s | 甲方测试 |

Chroma 路由见 ADR-0002。Eval **显式** `--model _scratch/modelscope/BAAI/bge-m3`。

**已知风险（须发版前处理或书面接受）**：

| Case | 风险 |
| --- | --- |
| #8 | Demo 须 TC148 库/路由；A3S 上测 = 必错 |
| #13 | 英文 query 易 Top1 限位组；期望 `qa_034`/`qa_022` 路径 |
| #22 | out-of-corpus；评体裁与拒答，不卡 Top1 |
| **#1** | board-family → `qa_011`；**DIP #3** gate（`ad5s` `qa_010` 写 #5 为库内疑点） |

### 准确率 Gate · DIP #3 vs #5（#1 驱动）

| 真源 | 关红外 photocell |
| --- | --- |
| Joyce #1 + 控制板丝印 | **DIP #3** OFF |
| `a3s` `qa_011` step 2 | **#3** ✅ |
| `ad5s` `qa_010` step 2 | **#5** ❌（与 `qa_040` #3 矛盾） |

发版前：英文 CS 生成对「遥控器无反应 / 断配件」类步骤须写 **#3**（board-family 同代板）；修库另开 overlay，不阻塞 #1 eval。

---

## Task 0 · Oracle（内部上限探针）

```text
English Email → 注入 expected_group → generate_answer(en, cs_email) → 对比 Reference
```

| Oracle | E2E Top1 | 下一刀 |
| --- | --- | --- |
| 差 | — | Prompt / context |
| 好 | 差 | Retrieval / routing / enrich |
| 好 | 好 | 可进 Gate 抽样 |

---

## P0 · Demo UI/UX（发版改造范围）

**目标**：客服路径「粘贴邮件 → Send → 英文回信」，无技术概念外露。

| 项 | 客服默认 | 工程师模式 |
| --- | --- | --- |
| 输入 | **多行 textarea**（整封邮件） | 同左 |
| 型号库下拉 | **隐藏** | 显示（unified 下为 force override） |
| 技术 pill（bge-m3 等） | **隐藏** | 可恢复 |
| 主面板 | **English Reply** | 中文排查步骤 |
| 知识匹配 | 一行英文摘要 + **Product line** | + group_id / 检索详情 |
| 示例 | Side-by-side #8 #13 #22 chips | — |
| Reference | 折叠 gold 回信（内部对照） | 同左 |

**启动（推荐）**：

```powershell
python qa_server.py --unified-cs --demo-presentation cs-email --images-dir _scratch/run-006/images --port 8765
```

浏览器：`http://127.0.0.1:8765/` — 单端口，三库自动路由（`library_router.py`）。

**发版前 UI 验收**（→ **Wave 2** §2.3–2.6 · 代码已实现 · 见 [DoD 对照](./cs_en_adr_dod_gap.md)）：

- [ ] 客服路径看不到「型号库」下拉
- [ ] **#13 chip**（MVP）无需选手册库即可命中 A3S 路径（原 #8/TC148 改为工程师/internal only）
- [ ] 结果区展示 `Product line: … · auto`
- [ ] Engineer 可展开中文步骤与 force library

**代码**：`demo/index.html` · `qa_server.py --unified-cs` · `library_router.py`

---

**甲方默认路径**：

```text
Customer Email (English) → Grounded English Reply（准）
```

- Knowledge Match：一行摘要即可；**不以 score 当主 KPI**。
- 工程师展开：中文步骤 / group_id / 检索详情 / **选手册库（仅调试）**。
- **发版**：客服路径不得出现型号库下拉；匹配产品线由系统自动展示。

---

## 发版门禁包（原「甲方反馈包」）

[`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) = **交付前内部验收表**：

- 我方对 Gate case 跑 E2E，填 System Reply + Grounding + Quality。
- 对照 Reference（有则必对）。
- 差距在发版前消化，或写入「已知限制」一节随交付说明。

**不**要求：甲方填 Feedback 列、Round 2 迭代演示、≥3 case 甲方试跑后才算 DoD。

---

## Task 1 / Task 2 Exit（摘要）

见 ADR-0002 legacy 线与 ADR-0003 EN-index 线。**双轨勿混报**：

| 索引 | 产物 | Gate Tier A（14） | All scorable | 备注 |
| --- | --- | ---: | ---: | --- |
| **ZH-index**（legacy · overlay 在 `chroma_captioned`） | [`cs_en_retrieval_baseline.json`](./cs_en_retrieval_baseline.json) | **14/14** | **68.8%** | Post G9/G10 + BL-RET-01a 重 embed（2026-07-08） |
| **EN-index**（ADR-0003 主口径 · **runtime 已切换**） | [`cs_en_retrieval_baseline_en.json`](./cs_en_retrieval_baseline_en.json) | **13/14** | **54.1%** | G11 · `csq_078` 薄边（Top3 含 `qa_022`） |

Task2 触发（legacy）：Gate Top1 **< 60%** 或与中文 probe 差 **≥ 15pp** 或 Tier A 全 miss。  
**Legacy 已触发并完成（2026-07-07）**：Gate **35.7% → 100%（14/14）**；all **78.0%**（Post G8c）。  
**Post G9/G10（2026-07-08）**：E2E 可评分 **7/7**（`cs_0026`/`cs_0013` OK）；ZH-index Gate **14/14** 保持；all 回落至 **68.8%**（非 Gate overlay 部分受 BL-RET-01a 重 embed 影响）。  
**遗留**：EN-index Gate **12/14**（`csq_071` #12 · `csq_078` #13）；A3S zh `q23b`；非 Gate 50 条（EN-index）。

**运维约束**：**禁止**多 job 并行 embed 同一路径 `chroma_dir`（2026-07-08 竞态教训）；`phase_cs_en_a_line_batch_overlay.py` 与 G10 生产库 **冲突** — 殷主管 review 前勿重跑。

**Task4**：**Grounding（准确）与 Reply Quality（体裁）分开记**；对外主报 Grounding。

---

## Regression Checklist（发版前）

- [x] Template 未进 `embedding_text`
- [x] `verify_tc148_customer_reply_template.py` PASS（2026-07-07）
- [ ] 中文 eval Top1 不低于冻结基线（**Post G8c**：A3S **43/47** · AD5S **43/48**；`q23` ✅ · `q23b` ❌）
- [x] EN Gate 使用 bge-m3 + 正确 chroma
- [x] ZH-index baseline 重跑（2026-07-08 · Gate **14/14**）
- [x] EN-index baseline（2026-07-08 · Gate **13/14** · G11）
- [x] `library_router` / `qa_server` 英文路径改打 **EN-index**
- [x] G9/G10 overlay 迁移至 EN 索引（G11 · 剩 `csq_078` 1 条薄边）
- [ ] Demo 默认英进英出（须 `--demo-presentation cs-email` 启动）
- [ ] **客服路径不要求选手册库**（→ **Wave 2** UI 验收）
- [ ] MVP 真邮子集 **≥16/19** ④通过（→ **Wave 1** §1.3.6 · [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md)）
- [ ] `--allowed-libraries a3s,ad5s` 演示模式（→ **Wave 2** §2.1）
- [ ] 说明书挂 unified-cs（→ **Wave 3** §3.1）
- [ ] 公网测试链接部署（→ **Wave 4** §4.4）
- [x] Phase 0.0：`context_builder.py` 抽离（tests PASS）
- [x] Phase 0.1：`locale=en` LLM context 无 `content_zh`
- [x] Phase 0.3：E2E 探针（[`phase0_e2e_gate_probe.md`](./phase0_e2e_gate_probe.md) · [`phase0_gate_probe.md`](./phase0_gate_probe.md)）
- [x] EN_READINESS + Phase 1a Pilot EN index（[`phase_1a_pilot_en_index.json`](./phase_1a_pilot_en_index.json)）
- [x] 门禁包 G/S 初评（[`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) · 9/9 生成）
- [ ] 殷主管正式 G/S Review

---

## 部署与甲方协作（→ Plan §1.1 · Wave 4 · Phase 5.0）

| 项 | 状态 | 说明 |
| --- | :---: | --- |
| 本地联调 | ☑ | `--unified-cs --demo-presentation cs-email` |
| Wave 1–3 出口 | ☐ | 见上节 Exit Checklist |
| **平台/服务器部署** | ☐ | **Wave 4** §4.4 · 稳定 URL · 索引/API/图片 |
| 殷主管试跑包 | ☐ | **Wave 4** §4.8 · 链接 + 建议 case + 已知限制 |
| 内部 Gate 包填完 | ☑ | G/S 初评 2026-07-08 · Wave 1 须复验无回退 |
| 殷主管试跑反馈闭环 | ☐ | 部署后 · 第一验收关口 |
| 叶天洲演示 | ☐ | **殷主管认可后**（验收标准 F-3） |

**禁止**：未部署、未填门禁包，即对外承诺「随时可约甲方试跑」。

## 留档路径

| 文件 | 内容 |
| --- | --- |
| `cs_en_oracle_gen_smoke.md` | Task 0 |
| `cs_en_retrieval_baseline.json` / `.md` | Task 1 · **ZH-index** · Gate **14/14** · all **68.8%**（2026-07-08） |
| `cs_en_retrieval_baseline_en.json` / `.md` | Task 1 · **EN-index** · Gate **12/14** · all **54.1%**（2026-07-08） |
| [`cs_en_task2_repair_priority.md`](./cs_en_task2_repair_priority.md) | Task 2 · R0→G10 波次与下一刀 |
| [`bl_ret_01a_batch_report.json`](./bl_ret_01a_batch_report.json) | 三库 ts + 四 manual 重 embed |
| [`merge_model_chroma_report.json`](./merge_model_chroma_report.json) | ts + manual merge（Demo 未接） |
| [`phase_1b_full_en_index.json`](./phase_1b_full_en_index.json) | Phase 1b 全量 EN 索引 |
| [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md) | **22 封真邮四维** · 80% 发链判据 |
| [`22封真邮_四维评分表.xlsx`](./22封真邮_四维评分表.xlsx) | Round 0/1 评分 |
| `cs_client_feedback_pack.md` | **Gate 探针诊断**（非 80% 判据）· G/S 初评 2026-07-08 |
| `cs_human_eval_scores.md` | Task 4（可选独立）· **未建** |
| `cs_side_by_side_demo.md` | 演示 + Reference 对照 · Oracle ✅ / E2E 见 probe |
| [`cs_email_pilot_cards.md`](./cs_email_pilot_cards.md) | Phase 0.2 Pilot 卡片 |
| [`phase0_e2e_gate_probe.md`](./phase0_e2e_gate_probe.md) | Phase 0.3 摘要 · overlay · 命令 |
| [`phase0_gate_probe.md`](./phase0_gate_probe.md) | Phase 0.3 全文回信 |
| [`phase0_reference_style_review.md`](./phase0_reference_style_review.md) | Reference vs System · #1/#8/#13 |
| [`cs_en_readiness_scan.md`](./cs_en_readiness_scan.md) | Gate R 扫描 |
| [`phase_1a_pilot_en_index.json`](./phase_1a_pilot_en_index.json) | Phase 1a Pilot EN 索引 |
| [`cs_en_implementation_plan.md`](./cs_en_implementation_plan.md) | **工程交付计划 v1.3** |
| [`cs_client_requirement_standard.md`](./cs_client_requirement_standard.md) | **甲方验收标准**（叶天洲 §一 + 殷主管 §二 MVP） |
| [`cs_en_adr_dod_gap.md`](./cs_en_adr_dod_gap.md) | ADR DoD 对照 · 发版缺口 |
| [`client_mvp_two_series_progress.md`](./client_mvp_two_series_progress.md) | **客户 MVP** · 两系列 × 三类内容 |
| [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md) | **22 封真邮四维** · 80% 线说明 |
| [`22封真邮_四维评分表.xlsx`](./22封真邮_四维评分表.xlsx) | Round 0/1 评分模板 |
| `yin_supervisor_pilot_pack.md` | **Wave 4** · 殷主管试跑包（待建） |

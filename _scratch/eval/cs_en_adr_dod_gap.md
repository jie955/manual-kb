# ADR-0002 DoD 对照 · 发版缺口（2026-07-07）

**真源**：[甲方验收标准](./cs_client_requirement_standard.md) · [ADR-0003](../../docs/adr/0003-english-cs-english-authoritative-pipeline.md) · [Implementation Plan v1.3](./cs_en_implementation_plan.md) · [ADR-0002](../../docs/adr/0002-english-cs-cross-lingual-retrieval-localized-generation.md)（Superseded）· [执行清单](./cs_en_poc_execution.md)  
**背景**：叶天洲 19:48 见验收标准 §一；**殷主管第一阶段 MVP** 见 §二；本表对照**当前仓库状态**与 ADR 发版门禁。

**图例**：✅ 已达标 · ⚠️ 部分完成 · ❌ 未达标 / 阻塞演示

---

## 总览

| 维度 | 状态 | 一句话 |
| --- | :---: | --- |
| **检索 Gate（Task 1）** | ✅ | Gate Tier A **14/14 Top1**（Post G8c）· all scorable **78.0%** |
| **修库（Task 2）** | ✅ | R0→G8c 完成；中文回归 A3S **43/47**（`q23b` 仍 miss）· AD5S **43/48** |
| **生成参数（Task 3）** | ✅ | `locale` + `response_mode=cs_email` 已实现 |
| **Oracle（Task 0）** | ✅ | 3/3 smoke；median Quality 3.67 |
| **E2E 生成验收（Task 4）** | ❌ | **仅 Oracle**；门禁包未填；无 E2E side-by-side 留档 |
| **Demo UI/UX** | ⚠️ | 代码已具备 unified-cs；**未做发版前 UI 四项勾选验收** |
| **发版门禁包** | ❌ | 表格全空 |
| **Regression Checklist** | ⚠️ | TC148 gate PASS；其余未逐项留档 |

**结论**：**检索层已就绪，E2E 生成 + 门禁包 + 甲方演示路径未闭环**——与叶天洲「生成不准、不像真客服信」反馈一致。

---

## ADR DoD 逐项

| # | ADR DoD 项 | 标准 | 状态 | 证据 / 缺口 |
| ---: | --- | --- | :---: | --- |
| 1 | **P0 · 准确** | Gate E2E Grounding 可接受；无 critical | ❌ | Task 1 检索 Top1 ✅；**E2E 生成未跑**。[`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) 全空。Oracle B 仍有端子号瑕疵（11#/12# vs 4#/5#） |
| 2 | **P0 · 统一入口** | 客服不选手册库；自动路由 | ⚠️ | [`library_router.py`](../../library_router.py) + `qa_server --unified-cs` ✅；Demo `showLibBar = !cs \|\| engineer` 已隐藏选库。**缺**：四项 UI 验收未勾选（执行清单 §162–167） |
| 3 | **P0 · 英进英出** | 默认 `locale=en` + `cs_email`；中文 chunk 非首屏 | ⚠️ | LLM context：**DONE**（`context_builder.py`）。Demo UI 四项仍待勾 |
| 4 | **Task 0** | Oracle smoke 完成 | ✅ | [`cs_en_oracle_gen_smoke.md`](./cs_en_oracle_gen_smoke.md) |
| 5 | **Task 1** | Gate Top1/Top3/MRR 留档 | ✅ | [`cs_en_retrieval_baseline.md`](./cs_en_retrieval_baseline.md) · gate_direct_logic_tier_a **100%** |
| 6 | **Task 3** | `locale=en` + `cs_email` 可演示 | ✅ | [`generate_answer.py`](../../generate_answer.py) · `CS_EMAIL_SYSTEM_PROMPT_EN` |
| 7 | **Task 4** | 双维评分；Grounding 优先；Quality median ≥3 | ❌ | Oracle 初评有（side-by-side）；**无 E2E 评分**；无 [`cs_human_eval_scores.md`](./cs_human_eval_scores.md) |
| 8 | **门禁包** | 我方填完；不依赖甲方 | ❌ | [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) T1–T5、#8/#13/#22、#1 均未填 |
| 9 | **回归** | Regression Checklist 无回退 | ⚠️ | 见下节 |

---

## Regression Checklist

| 项 | 状态 | 备注 |
| --- | :---: | --- |
| Template 未进 `embedding_text` | ✅ | ADR 已声明；无代码改动需求 |
| `verify_tc148_customer_reply_template.py` PASS | ✅ | 2026-07-07 本地跑通 |
| 中文 eval Top1 不低于冻结基线 | ⚠️ | Task2 留档 A3S 45/47 · AD5S 43/48；**未与冻结基线数字逐项对比留档** |
| EN Gate 使用 bge-m3 + 正确 chroma | ✅ | baseline 脚本显式 bge-m3 |
| Demo 默认英进英出 | ⚠️ | 须 `--demo-presentation cs-email` 启动；**非默认 qa_server 参数** |
| 客服路径不要求选手册库 | ⚠️ | 代码已实现；**未勾选 UI 验收** |
| 门禁包 Gate case 已填 | ❌ | 全空 |

---

## New Work 任务表（执行清单 §49–61）

| Task | 产出 | Exit | 状态 |
| ---: | --- | --- | :---: |
| Task 1 · E2E 检索 Gate | baseline json/md | Gate Top1 留档 | ✅ |
| Task 4 · 双维评分 | human_eval 或门禁包内 | Grounding 优先 | ❌ |
| 发版门禁包 | cs_client_feedback_pack | 我方填完 | ❌ |
| 统一入口 + 路由 | library_router + qa_server | 客服不选库 | ⚠️ 代码 ✅ / 验收 ❌ |
| Demo 英进英出 | demo + server | EN → EN | ⚠️ |
| Task 0 · Oracle | oracle smoke md | 探针完成 | ✅ |
| Task 3 · locale + mode | generate_answer | cs_email 可调用 | ✅ |
| Side-by-side 演示 | #8 #13 #22 | 演示样例 | ⚠️ Oracle 有；**E2E 未填** |
| Task 2 · enrich | overlay | Gate 不达标时 | ✅ Post G8c（Gate 14/14 · all 78%） |

---

## 叶天洲反馈 ↔ 缺口映射

| 叶天洲说的 | 当前状态 | 下一步 |
| --- | --- | --- |
| 生成准确率不高 | 检索 Gate ✅；**E2E 生成未验收** | 跑 E2E Gate case → 填门禁包 Grounding |
| 没学邮件风格 | `cs_email` prompt ✅；**未 E2E 对照 Reference** | Task 4 Quality 评分；优先 #13 #8 |
| 中文资料干扰 AI | **Phase 0.1 DONE** — `context_builder` · `locale=en` 不注入 `content_zh` | 0.3 跑 `run_cs_e2e_gate` 填包；Style exemplar 探针 |
| 切片不准 | Task2 后 Gate 100% | 对甲方演示用 **E2E** 而非 Oracle；展示 routing + group |
| 没跟殷主管沟通 | 流程可选 | **部署后**商务安排；技术侧用门禁包作对齐清单（Plan §1.1） |
| 竞品沟通多、迭代快 | ADR 禁止依赖甲方试跑收敛 | 内部先填门禁包再演示；个案 fix 发版后 |

---

## 阻塞甲方演示的 P0 动作（推荐顺序）

```text
1. 启动 Demo：python qa_server.py --unified-cs --demo-presentation cs-email --images-dir _scratch/run-006/images --port 8765
2. UI 验收四项（执行清单 §162–167）→ 勾选留档
3. 对 Gate 必跑 case 跑 E2E（非 Oracle）：
   · #8 cs_0008 · #13 cs_0013 · #22 cs_0022
   · T1 T3 T4（甲方测试题）
   · 扩展 #1 DIP #3
4. 填入 cs_client_feedback_pack：System Reply + retrieval_group + Grounding + Quality
5. 清零 critical（端子号、DIP、机型路由）或写入「已知限制」
6. 演示叙事：只展示 E2E 达标 case；Reference 折叠对照；不展示中文 chunk
```

### E2E Gate 脚本

- [`run_cs_e2e_gate.py`](./run_cs_e2e_gate.py)：`library_router.unified_search` + 可选 `generate_answer(en, cs_email)` · 输出 [`cs_e2e_gate_results.json`](./cs_e2e_gate_results.json)  
  - 检索 + context leak：`python _scratch/eval/run_cs_e2e_gate.py`  
  - 含生成：`python _scratch/eval/run_cs_e2e_gate.py --generate`（需 `QA_API_KEY`）  
- Oracle 对照：[`run_cs_side_by_side_gen.py`](./run_cs_side_by_side_gen.py)

---

## 发版判定

| 判定 | 条件 |
| --- | --- |
| **可内部预演** | Demo unified-cs 启动 + #8 chip E2E 手动跑通 1 条 |
| **可交付殷主管试跑** | 验收标准 §二 MVP-0 + §2.3 **真邮 19 封 ≥16/19** + 已部署稳定 URL |
| **可交付甲方演示** | 门禁包 Gate case 填完 + 无未书面接受的 critical + UI 四项 ✅ + **已部署至平台/服务器** |
| **当前** | **不可发测试链接** — 差真邮四维 80% · G11/EN 路径 · 部署未做 |

---

## 架构路径判定（摘要）

ADR 路径 `English Query → 中文索引 chroma → Generator(en, cs_email) → English Reply` 在**甲方语义下未满足验收** — 详见 [甲方验收标准](./cs_client_requirement_standard.md) §五、§5.5。检索 Gate 达标 ≠ E2E 达标 ≠ 殷主管 MVP 达标。

---

## 留档

| 文件 | 角色 |
| --- | --- |
| [`cs_client_requirement_standard.md`](./cs_client_requirement_standard.md) | **甲方验收标准真源**（叶天洲 §一 + 殷主管 §二 MVP + 差距分析） |
| 本文件 | ADR DoD 对照 / 发版缺口 |
| [`cs_en_poc_execution.md`](./cs_en_poc_execution.md) | 执行清单（已同步勾选状态） |
| [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) | 待填门禁包 |

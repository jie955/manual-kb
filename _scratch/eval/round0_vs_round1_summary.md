# Round 0 vs Round 1 · 机械对比留档

**日期**：2026-07-08（初版）· 2026-07-10（补批次血缘）  
**脚本**：[`compare_round0_round1.py`](./compare_round0_round1.py) · [`draft_22mail_scoring.py`](./draft_22mail_scoring.py)

---

## 批次血缘（防混读 · 2026-07-10）

Joyce 22 目前有 **四批独立生成 JSON**（文件名易混）。下表记录的是 **生成阶段**（测的是什么能力），不是仅记 draft ④ 数字。  
**不可**把不同批次的 ④ 横向直接比；回看本文 **不必**再跑 MD5 校验。

### 生成阶段一览（自洽说明）

| 批次 ID | JSON | 生成时间 | Runner / 入口 | 检索与生成路径 | EvalPack（靶向 YAML） | 本批在测什么 | 人工 xlsx 对照建议 |
| --- | --- | --- | --- | --- | :---: | --- | --- |
| **Round 0** | [`cs_22mail_eval_round0.json`](./cs_22mail_eval_round0.json) | 07-08 16:14 | 旧 [`cs_22mail_batch_runner.py`](./cs_22mail_batch_runner.py) · `--round round0` | EN `chroma_captioned_en` · `unified_search` · `generate_answer(cs_email)` | **无** | **Wave1 修前基线**（normalize/售前路由/预检等通用改动**之前**） | sheet **基线评分(修复前)** |
| **Round 1** | [`cs_22mail_eval_round1.json`](./cs_22mail_eval_round1.json) | 07-08 22:01 | 同上 · `--round round1` | 同上 | **无** | **通用工程改动之后、EvalPack 补丁之前**的复测 — 更接近「系统原生 + 格式/路由通用修复」，**不含** per-case brief/pinned/boost | sheet **复测评分(Wave1后)** · **当前人工评分主线** |
| **Round 1e** | [`../eval_runs/cs_22mail_round1e_2026-07-10.json`](../eval_runs/cs_22mail_round1e_2026-07-10.json) | 07-10 17:15 | 新 [`evals/runners/cs_22mail_batch_runner.py`](../evals/runners/cs_22mail_batch_runner.py) · `--round round1e` · `run_cs_email_workflow` | 同上 + workflow 编排 | **全开**（`retrieval_boosts` / `generation_briefs` / `pinned_references` / `presales_briefs` / `context_overrides` / `pinned_images` 等 · 见 [`fix_classification…`](../eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md) §二） | **同集多轮靶向补丁后的上限探测** — 非原生能力；**不得**单独对外冒充系统水平 | 仅诊断/演进对照 · **非**当前 xlsx 主线 |
| **patch_off** | [`../eval_runs/cs_22mail_patch_off_2026-07-10.json`](../eval_runs/cs_22mail_patch_off_2026-07-10.json) | 07-10 18:11 | 新 runner · `--round patch_off` · **`--no-eval-pack`** | 同上（新栈） | **显式关闭** | 新 runner 栈上的 **无补丁对照**（与 Round 1e 同代码、关 YAML） | 与 round1e 差分 · 见 [`patch_off_compare_2026-07-10.md`](../eval_runs/patch_off_compare_2026-07-10.md) |

**命名陷阱**：`cs_22mail_eval_round1.json`（07-08）≠ `cs_22mail_round1e_2026-07-10.json`（07-10）— 后者才是 Round **1e**。

### 同脚本④草稿（`draft_22mail_scoring.py` · 仅排序参考）

| 批次 | MVP19 草稿④ | 备注 |
| --- | ---: | --- |
| Round 1（07-08 · 无补丁） | **8/19** | [`scoring_draft_round1.md`](./scoring_draft_round1.md) |
| patch_off（07-10 · 无补丁 · 新栈） | **7/19** | [`scoring_draft_cs_22mail_patch_off_2026-07-10.md`](./scoring_draft_cs_22mail_patch_off_2026-07-10.md) |
| Round 1e（07-10 · 补丁全开） | **19/19** | [`scoring_draft_cs_22mail_round1e_2026-07-10.md`](./scoring_draft_cs_22mail_round1e_2026-07-10.md) |

**校验（一次性留档）**：Round 1 / Round 1e / patch_off 三批 **22/22 封 `generated_reply_en` MD5 两两不同** → 排除「同批数据、两套结果」。

### 机械④不可信（证据链 · 同尺不同内容）

- **同一把尺**：均为 `draft_22mail_scoring.py`（`ref_keys` 字符串重叠 + DIP 硬规则 + ②=直接可发 → ④ 等）— **没有**第二套 EvalPack 内置④判定器。  
- **EvalPack 作用**：改 **生成内容**（brief / pinned / boost），使同一尺子上 `ref_keys` 更易打满 — 故 7–8/19 → 19/19。  
- **混淆变量已排除**：不是「评分工具不一致」，而是「内容是否被补丁喂饱术语表」。  
- **禁止**将草稿「还差 N 封」当发链结论；④ **必须人工**签字（见 [`fix_classification…`](../eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md) §三、§七）。

### Round 1（07-08）②草稿解读 · 人工顺序（冻结）

针对 [`scoring_draft_round1.md`](./scoring_draft_round1.md)（**不是** round1e）：

| 优先级 | mail | 动作 |
| ---: | --- | --- |
| **P0** | #12 #14 #19 #21 #22 | `ref_keys` 50–75%：**语义是否覆盖**，非术语字面 |
| **P0** | #16 | DIP 硬规则（`qa_011`+DIP#5→小改）是否误降级 |
| **P1** | #1 #20 #22 | ① 待定 — 定案前④合计会变（**#14 已在 P0 定①错**） |
| **P2** | ref_keys=100% 等 | 仍须过一遍，不因 100% 跳过 |

- **勿** `--apply-sheet`，直至边界 case + ① 定案后再写 xlsx H 列。  
- **Round 1e ②草稿**：按需再出；**不预设**对外主线转向补丁批 — 先评完无补丁 Round 1，再决定是否用 Round 1e 对外（防补丁数字冒充原生能力）。

---

## 路径说明

| 轮次 | JSON | 生成时间 | xlsx sheet |
| --- | --- | --- | --- |
| Round 0 | [`cs_22mail_eval_round0.json`](./cs_22mail_eval_round0.json) | 2026-07-08T16:14:40 | **基线评分(修复前)** |
| Round 1 | [`cs_22mail_eval_round1.json`](./cs_22mail_eval_round1.json) | 2026-07-08T22:01:12 | **复测评分(Wave1后)** |

> Round 0→1 之间 **无 intentional Wave 1 修复批次**；差异主要来自 style 路由与 batch_runner 预检字段。正式 Wave 1 出口仍以 **人工 E–H + ≥16/19** 为准。

---

## 预检指标（Round 0 → Round 1）

| 指标 | Round 0 | Round 1 |
| --- | ---: | ---: |
| truncated | 0/22 | 0/22 |
| proceed_ref | 0/22* | 0/22 |
| check_step_ref | 0/22* | 0/22 |
| glued_steps | 0/22* | 0/22 |
| incomplete | 0/22* | 0/22 |
| **top1 变化** | — | **0 封** |

\* Round 0 JSON 无 `reply_audit` 字段；预检列仅 Round 1 可比。

---

## Style family 变化（5 封）

| cs_id | Round 0 | Round 1 |
| --- | --- | --- |
| cs_0004 | F5_dual_swing | **F7_presales** |
| cs_0005 | F5_dual_swing | **F7_presales** |
| cs_0006 | F1_no_response | **F7_presales** |
| cs_0007 | F2_tc148_wired | **F7_presales** |
| cs_0011 | F1_no_response | **F7_presales** |

售前类（#4–#7、#11）人工打 **②** 时勿按排查 Reference 逐步对齐。

---

## 草稿通过率（须人工确认）

见 [`scoring_draft_round0.md`](./scoring_draft_round0.md) · [`scoring_draft_round1.md`](./scoring_draft_round1.md)  
**不可**替代 xlsx 正式 E–H。

---

## 人工下一步（07-10 更新 · 以无补丁 Round 1 为主线）

1. **对照 JSON**：[`cs_22mail_eval_round1.json`](./cs_22mail_eval_round1.json) + [`scoring_draft_round1.md`](./scoring_draft_round1.md)  
2. **xlsx sheet**：「复测评分(Wave1后)」— 按上文 P0→P1→P2 人工填 E–H；**勿** `--apply-sheet`  
3. 仅统计 B=「是」→ **≥16/19** 方为 Wave 1 发链线  
4. **评完后再决定**：是否另用 Round 1e（补丁批）对外 — 见批次血缘表「不得冒充原生能力」  
5. 基线 sheet 仍可用 Round 0 + [`scoring_draft_round0.md`](./scoring_draft_round0.md) 作前后对比  
6. **E–H 填表留档**：P0 [`p0_semantic_review…`](./p0_semantic_review_round1_2026-07-10.md) · P1 [`p1_and_safety_audit…`](./p1_and_safety_audit_round1_2026-07-10.md) · P2 [`p2_semantic_review…`](./p2_semantic_review_round1_2026-07-10.md) — **P0+P1+P2 收敛后一次性写入，勿 `--apply-sheet`**

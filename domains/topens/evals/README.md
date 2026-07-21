# TOPENS eval assets

Gate ids, holdout lists, and **EvalPack** targeted-fix YAML live here.  
Large case maps remain under `_scratch/eval/`; runners resolve paths via `gates.yaml`.

## Layout

| File | Loader | Purpose |
| --- | --- | --- |
| `gates.yaml` | `domains/loader.py` | Gate 9 ids, Joyce 22 ids, style holdout, case map pointer |
| `retrieval_boosts.yaml` | `eval_pack.retrieval_boost()` | Scenario EN retrieval query override |
| `presales_briefs.yaml` | `eval_pack.presales_brief()` | Presales facts + purchase URLs |
| `generation_briefs.yaml` | `eval_pack.generation_brief()` | Fault Joyce anchors / mandatory step count |
| `pinned_references.yaml` | `eval_pack.pinned_reference()` | **Reference 0** authoritative ladder |
| `context_overrides.yaml` | `eval_pack.context_force_include_groups()` | Force-include groups under top1_excludes |
| `pinned_images.yaml` | `eval_pack.pinned_images()` | Eval-only images merged into batch `images_used` |

## Runtime wiring

- `agents/cs_email_workflow.py` → `context_force_include_groups` on context build
- `generate_answer.py` → Reference 0 injection, presales/generation briefs, Reference 0 step order
- `evals/runners/cs_22mail_batch_runner.py` → `pinned_images`, `resolve_search_query`
- `domains/prompt_style.py` → `family_router.json` `scenario_overrides` (style family per cs_id)

## Case map (`_scratch/eval/cs_email_query_map.json`)

Per-scenario fields used by batch runner / draft scoring:

- `expected_group_ids` / `alternate_group_ids` — ① top1_hit（fan_out 场景须显式声明）
- `verbatim_customer` — retrieval query 优先于 `primary_query`
- `type: presales` — presales brief + 强制链接输出路径

## 维护约定

- 新增 fail_tag 靶向 fix：先加 YAML + `test_eval_pack.py`，再跑 `_scratch/eval_runs/probe_*.py`，最后 `--round roundNx` 全批
- 不往本目录放散装一次性 probe 脚本（放 `_scratch/eval_runs/`）
- Case map 正文迁移 Phase 2 前仍维护 scratch 路径；改 `expected_group_ids` 时同步更新 draft 对照

## 权威结果（2026-07-10）

Round 1e · Joyce 22 MVP19 ④草稿 **19/19** — **同集多轮靶向，过拟合风险**；须人工 xlsx 确认。  
Holdout T1–T5（`cs_0023`–`cs_0027`，无 EvalPack 补丁）④草稿 **1/5** — see [`holdout_t1_t5_compare_2026-07-10.md`](../../../_scratch/eval_runs/holdout_t1_t5_compare_2026-07-10.md).

> **T1–T5 已「见过光」** — 可用于 xlsx/复盘，**不可**作为桶 A/B 修完后的 blind holdout；下一批须换新邮件（见 [`fix_classification…§10.3`](../../../_scratch/eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md)）。

可泛化 presales 业务规则放 `../presales_playbooks.yaml`；eval 场景用 `playbook_ref` 引用（例 `cs_0004` → `two_independent_gates`）。

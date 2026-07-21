# Holdout T1–T5 vs Joyce 22 Round 1e

**日期**：2026-07-10  
**目的**：在未参与 Round 1b–1e EvalPack 靶向补丁的邮件上验证泛化，判断 19/19 是否过拟合。

## 集合定义

| 集合 | scenario ids | EvalPack 补丁 |
| --- | --- | --- |
| Joyce 22 MVP19（Round 1e） | cs_0001–cs_0022 子集 19 封 | ✅ 多轮 per-case YAML |
| **Holdout T1–T5** | cs_0023–cs_0027 | ❌ 无 |

Holdout 场景已在 `gates.yaml` `gate_scenario_ids` 中，但不在 `joyce_22_ids`，且 `presales_briefs` / `generation_briefs` / `pinned_references` 等均无对应条目。

## ④草稿对比

| 集合 | ④通过 | 备注 |
| --- | --- | --- |
| Joyce 22 MVP19 · Round 1e | **19/19** | 5 轮在同一组邮件上靶向修复 |
| **Holdout T1–T5** | **1/5** | MVP-like **1/4**（排除 tc148 cs_0025） |

**结论（草稿 · 须人工确认）**：Holdout ④通过率远低于 Joyce 22，支持「同一评测集反复打补丁 → 曲线过拟合」的假设。19/19 **不能**作为 Phase 1 质量目标达成的依据。

## Holdout 逐封

| id | test | ① | ② | ④ | 主要问题 |
| --- | --- | --- | --- | --- | --- |
| cs_0023 | T1 | 错 | 小改可发 | 不通过 | top1=qa_040 不在 acceptable；AD5S auto-close 路由 |
| cs_0024 | T2 | 对 | 直接可发 | **通过** | presales 泛化尚可（无 brief 补丁） |
| cs_0025 | T3 | 对 | 小改可发 | 不通过 | tc148 保修；生成缺 ref_keys |
| cs_0026 | T4 | 对 | 需重写 | 不通过 | **audit incomplete**（2 步收束 · 非 max_tokens） |
| cs_0027 | T5 | 对 | 小改可发 | 不通过 | **评分无金标准** · 生成可能已够 |

## 与 Round 1e 曲线对照

```
post-refactor  8/19
Round 1b       9/19
Round 1c      13/19
Round 1d      17/19
Round 1e      19/19   ← 同集 5 轮靶向
Holdout       1/5    ← 未见过的 5 封
```

## 产物

- Batch JSON：[`holdout_t1_t5_2026-07-10.json`](./holdout_t1_t5_2026-07-10.json)
- 四维草稿：[`scoring_draft_holdout_t1_t5_2026-07-10.md`](../eval/scoring_draft_holdout_t1_t5_2026-07-10.md)
- Runner：[`run_holdout_t1_t5.py`](./run_holdout_t1_t5.py)

## 下一步（阻塞 Phase 2 / ADR 质量结论）

1. **人工 xlsx 四维**（Joyce 22 抽样 + holdout 全 5 封），重点 ②直接可发、③图片配对
2. 按 **[通用修复 vs 过拟合补丁清单](./fix_classification_holdout_and_round1e_2026-07-10.md)** 修问题 — 禁止为 holdout 逐封加 EvalPack
3. 扩充 holdout 集或冻结 EvalPack 后再跑一轮

```bash
python _scratch/eval_runs/run_holdout_t1_t5.py
```

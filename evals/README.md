# Formal evaluation runners

Stable CS email gate scripts live here. Scratch overlays and one-off probes
remain under `_scratch/eval/`. Reports go to `_scratch/eval_runs/` — never
overwrite baseline fixtures without a new dated filename.

## Runners

| Script | Purpose |
| --- | --- |
| `run_cs_e2e_gate.py` | Gate 9-case E2E（R/K/G/S 机械指标） |
| `cs_22mail_batch_runner.py` | Joyce 22-mail batch（`--generate` 调 LLM） |
| `gate_report.py` | Probe markdown helpers |

```bash
# Gate 9-case
python evals/runners/run_cs_e2e_gate.py --index en --generate

# Joyce 22-mail（权威 Round 1e）
python evals/runners/cs_22mail_batch_runner.py --round round1e --generate --index en \
  --out _scratch/eval_runs/cs_22mail_round1e_2026-07-10.json

# 四维草稿评分（非官方分数）
python _scratch/eval/draft_22mail_scoring.py \
  --json _scratch/eval_runs/cs_22mail_round1e_2026-07-10.json
```

## Scratch compatibility

- `_scratch/eval/run_cs_e2e_gate.py` → forwards here (+ optional legacy JSON/MD)
- `_scratch/eval/cs_22mail_batch_runner.py` → forwards to `cs_22mail_batch_runner.py`

## Domain eval assets

Gate ids, holdout lists, and **EvalPack** YAML: `domains/topens/evals/`  
Loader: `domains/eval_pack.py`  
Case map: `_scratch/eval/cs_email_query_map.json` (pointer in `gates.yaml`)

## Round 1e 留档（2026-07-10）

| 产物 | 路径 |
| --- | --- |
| Batch JSON | `_scratch/eval_runs/cs_22mail_round1e_2026-07-10.json` |
| ④草稿评分 | `_scratch/eval/scoring_draft_cs_22mail_round1e_2026-07-10.md` |
| 演进对比 | `_scratch/eval_runs/round1e_compare_2026-07-10.md` |

MVP19 ④草稿：**19/19**（**同集 Round 1b–1e 靶向补丁 · 过拟合风险** · 须人工确认后写入 xlsx E–H）。

## Holdout T1–T5（2026-07-10）

未参与 Round 1b–1e 补丁的 gate 场景 `cs_0023`–`cs_0027`：

| 产物 | 路径 |
| --- | --- |
| Batch JSON | `_scratch/eval_runs/holdout_t1_t5_2026-07-10.json` |
| ④草稿评分 | `_scratch/eval/scoring_draft_holdout_t1_t5_2026-07-10.md` |
| vs Round 1e | `_scratch/eval_runs/holdout_t1_t5_compare_2026-07-10.md` |

④草稿：**1/5**（MVP-like 1/4）— **阻塞宣布 Phase 1 质量达成**；人工 xlsx ②③为 Phase 2 前置。

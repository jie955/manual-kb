# _scratch/eval — overlay probes & historical reports

**Gate / E2E 正式 runner（权威实现）**

| 用途 | 正式路径 | 旧 scratch 入口（兼容） |
| --- | --- | --- |
| Gate 9-case E2E | `evals/runners/run_cs_e2e_gate.py` | `_scratch/eval/run_cs_e2e_gate.py` → 转发 + 写 legacy JSON/MD |
| Joyce 22-mail batch | `evals/runners/cs_22mail_batch_runner.py` | `_scratch/eval/cs_22mail_batch_runner.py` → 转发 |

**推荐命令**

```bash
# 正式（报告 → _scratch/eval_runs/，不覆盖基准）
python evals/runners/run_cs_e2e_gate.py --index en

# 需同时更新 scratch 留档 JSON + phase0_gate_probe.md
python evals/runners/run_cs_e2e_gate.py --index en --scratch-legacy-output

# 旧文档里的路径仍可用（等价于上一行）
python _scratch/eval/run_cs_e2e_gate.py --index en
```

**留在此目录的内容**

- `cs_email_query_map.json` — case map（指针也在 `domains/topens/evals/gates.yaml`）
- `cs_e2e_gate_results.json` / `phase0_gate_probe.md` — Phase 0 基准快照（仅 `--scratch-legacy-output` 或兼容 launcher 写入）
- overlay 脚本、诊断脚本、历史 JSON — 不搬迁，保真

**勿再** 在 `_scratch/eval/` 新增 runner 正文；改 `evals/runners/` + `agents/cs_email_workflow.py`。

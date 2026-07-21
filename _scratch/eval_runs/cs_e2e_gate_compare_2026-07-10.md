# Gate G/S · Post-Refactor Compare

**Baseline**: `cs_e2e_gate_results.json` (2026-07-08)
**Current**: `cs_e2e_gate_2026-07-10.json` (2026-07-10)

## Mechanical metrics (Gate G / K)

| Metric | Baseline | Current |
| --- | --- | --- |
| Top1 hit (scorable) | 5/6 | 5/6 |
| Library hit | 9/9 | 9/9 |
| context_zh_leak | 0/9 | 0/9 |
| Generated replies | 9/9 | 9/9 |
| Truncated | 0 | 1 |

## Per-case

| Case | Top1 | Lib | ZH leak | Style | Reply len | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| cs_0001 | `qa_011`→`qa_011` [None→None] | `a3s` | ✅ | `F1_no_response` | 3081→3939 | — |
| cs_0008 | `qa_001`→`qa_001` [True→True] | `tc148` | ✅ | `F2_tc148_wired` | 2179→1849 | — |
| cs_0013 | `qa_022`→`qa_022` [True→True] | `a3s` | ✅ | `F4_limit_travel` | 2391→2517 | — |
| cs_0022 | `qa_040`→`qa_040` [None→None] | `ad5s` | ✅ | `F1_no_response` | 2294→2336 | — |
| cs_0023 | `qa_040`→`qa_040` [False→False] | `ad5s` | ✅ | `F6_auto_close_rebound` | 2263→2183 | — |
| cs_0024 | `qa_040`→`qa_040` [None→None] | `ad5s` | ✅ | `F7_presales` | 2379→3510 | — |
| cs_0025 | `qa_001`→`qa_001` [True→True] | `tc148` | ✅ | `F8_warranty_rma` | 2188→1924 | — |
| cs_0026 | `qa_001`→`qa_001` [True→True] | `a3s` | ✅ | `F2_tc148_wired` | 2023→2187 | — |
| cs_0027 | `qa_010`→`qa_010` [True→True] | `a3s` | ✅ | `F1_no_response` | 3260→3229 | — |

## Verdict

- **Gate G (mechanical)**: ✅ no regression
- **Gate S**: manual G/S 1–5 unchanged in this script; compare `reply_full` in JSON / probe MD

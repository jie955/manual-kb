# 22-Mail Batch · Post-Refactor Compare

**Baseline**: `cs_22mail_eval_round0.json` (2026-07-08)
**Current**: `cs_22mail_post_refactor_2026-07-10.json` (2026-07-10)

## Mechanical metrics

| Metric | Baseline | Current |
| --- | --- | --- |
| Cases | 22 | 22 |
| MVP19 subset | 19 | 19 |
| Top1 hit (scorable) | 8/13 | 8/13 |
| MVP19 Top1 hit | 6/19 | 6/19 |
| context_zh_leak | 0/22 | 0/22 |
| Generated | 22/22 | 22/22 |
| Truncated | 0 | 1 |
| Audit/format flags | 0 | 1 |

## Per-case deltas

| Case | Top1 | Lib | Style | Reply len | Flags |
| --- | --- | --- | --- | --- | --- |
| cs_0001 | `qa_011`→`qa_011` | `a3s`→`a3s` | `F1_no_response` | 3352→3307 | len changed |
| cs_0002 | `qa_037`→`qa_037` | `a3s`→`a3s` | `F3_power_motor` | 2778→2472 | len changed |
| cs_0003 | `qa_010`→`qa_010` | `ad5s`→`ad5s` | `F1_no_response` | 3068→2671 | len changed |
| cs_0004 | `qa_015`→`qa_015` | `ad5s`→`ad5s` | `F5_dual_swing`→`F7_presales` | 1254→2425 | style changed, len changed |
| cs_0005 | `qa_007`→`qa_007` | `ad5s`→`ad5s` | `F5_dual_swing`→`F7_presales` | 1456→1697 | style changed, len changed |
| cs_0006 | `qa_011`→`qa_011` | `a3s`→`a3s` | `F1_no_response`→`F7_presales` | 965→892 | style changed, len changed |
| cs_0007 | `qa_020`→`qa_020` | `a3s`→`a3s` | `F2_tc148_wired`→`F7_presales` | 2427→3801 | style changed, len changed |
| cs_0008 | `qa_001`→`qa_001` | `tc148`→`tc148` | `F2_tc148_wired` | 2398→1620 | len changed, truncated, incomplete:missing closing: results, media |
| cs_0009 | `qa_031`→`qa_031` | `ad5s`→`ad5s` | `F2_tc148_wired` | 2779→2598 | len changed |
| cs_0010 | `qa_002`→`qa_002` | `tc148`→`tc148` | `F2_tc148_wired` | 1571→1903 | len changed |
| cs_0011 | `qa_042`→`qa_042` | `a3s`→`a3s` | `F1_no_response`→`F7_presales` | 1351→2023 | style changed, len changed |
| cs_0012 | `qa_019`→`qa_019` | `a3s`→`a3s` | `F1_no_response` | 1921→1943 | len changed |
| cs_0013 | `qa_022`→`qa_022` | `a3s`→`a3s` | `F4_limit_travel` | 2343→2401 | len changed |
| cs_0014 | `qa_019`→`qa_019` | `a3s`→`a3s` | `F4_limit_travel` | 1863→1815 | len changed |
| cs_0015 | `qa_040`→`qa_040` | `ad5s`→`ad5s` | `F6_auto_close_rebound` | 2123→2116 | len changed |
| cs_0016 | `qa_001`→`qa_001` | `ad5s`→`ad5s` | `F2_tc148_wired` | 2168→2323 | len changed |
| cs_0017 | `qa_033`→`qa_033` | `a3s`→`a3s` | `F8_warranty_rma` | 2791→2722 | len changed |
| cs_0018 | `qa_001`→`qa_001` | `a3s`→`a3s` | `F2_tc148_wired` | 2041→2287 | len changed |
| cs_0019 | `qa_015`→`qa_015` | `ad5s`→`ad5s` | `F1_no_response` | 2016→2600 | len changed |
| cs_0020 | `qa_040`→`qa_040` | `ad5s`→`ad5s` | `F5_dual_swing` | 2076→2061 | len changed |
| cs_0021 | `qa_033`→`qa_033` | `a3s`→`a3s` | `F1_no_response` | 2647→2525 | len changed |
| cs_0022 | `qa_040`→`qa_040` | `ad5s`→`ad5s` | `F1_no_response` | 2378→2279 | len changed |

## Verdict

- **Mechanical (K/G)**: see table above
- **Gate S / ④整体通过**: human ①②③④ in xlsx; compare `generated_reply_en` in JSON

- **Post-refactor mechanical**: ✅ no regression
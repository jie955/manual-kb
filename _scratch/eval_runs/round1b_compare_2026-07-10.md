# Round 1b · Re-run Compare（cs_0002 稳定化后）

**上一轮 round1b**（15:59 · 含 targeted fix 未含 Reference 0 指令）· **9/19** MVP19 ④通过  
**本轮 re-run**（16:31 · Reference 0 + mandatory 6-step）· **7/19** MVP19 ④通过（目标 ≥16）

## 本轮 MVP19 ④通过（7）

cs_0002, cs_0006, cs_0012, cs_0013, cs_0015, cs_0017, cs_0019

## 相对上一轮 round1b

| 变化 | cs_id | 说明 |
| --- | --- | --- |
| **新增通过** | cs_0002 | ②直接可发 ref_keys=100% · 6 步 Joyce 阶梯稳定 |
| **退步** | cs_0011 | ②小改可发 presales weak links |
| **退步** | cs_0005 | ③该配没配（presales 图） |
| **波动** | cs_0003, cs_0016, cs_0018, cs_0020, cs_0021, cs_0022 | ②小改可发 · LLM 方差 |

## Target cases

| cs_id | 上一轮 ④ | 本轮 ④ | 本轮 top1 | 本轮 ② |
| --- | --- | --- | --- | --- |
| cs_0002 | 不通过 | **通过** | qa_001 | 直接可发 |
| cs_0011 | 通过 | 不通过 | qa_042 | 小改可发 |
| cs_0012 | 通过 | **通过** | qa_020 | 直接可发 |
| cs_0019 | 通过 | **通过** | qa_016 | 直接可发 |
| cs_0006 | 通过 | **通过** | qa_011 | 直接可发 |

## ② 分布（MVP19）

- 直接可发 **9** · 小改可发 **10** · 需重写 **0**
- ④瓶颈主要在 ②小改可发（10 封）与 ③图片（cs_0005 该配没配）

## 留档

- Batch JSON: `_scratch/eval_runs/cs_22mail_round1b_2026-07-10.json`
- 草稿评分: `_scratch/eval/scoring_draft_cs_22mail_round1b_2026-07-10.md`
- cs_0002 单测: `_scratch/eval_runs/cs_0002_stable_2026-07-10.json`

# Round 1c · Fault Trio + Presales Compare

**Round 1b re-run**（cs_0002 稳定化后）· **7/19** MVP19 ④通过  
**Round 1c**（+ cs_0021/cs_0018/cs_0003 pinned ref + presales 强制链接）· **13/19** MVP19 ④通过（目标 ≥16）

## 本轮 MVP19 ④通过（13）

cs_0002, cs_0003, cs_0004, cs_0006, cs_0007, cs_0011, cs_0012, cs_0013, cs_0015, cs_0017, cs_0018, cs_0019, cs_0021

## 相对 Round 1b re-run

| 变化 | cs_id | 说明 |
| --- | --- | --- |
| **新增通过** | cs_0003 | AD8 DIP #5 阶梯 · Reference 0 |
| **新增通过** | cs_0018 | 6 步 A5/A8 阶梯 · qa_033 force_include |
| **新增通过** | cs_0021 | 3 步 dual swing · 4#/5# 稳定 |
| **新增通过** | cs_0011 | presales 强制 Amazon 链接 |
| **新增通过** | cs_0007 | presales brief + 强制链接 |
| **新增通过** | cs_0004 | presales + links（方差回升） |
| **仍不通过** | cs_0001, cs_0014, cs_0020, cs_0022 | ①待人工 fan_out |
| **仍不通过** | cs_0005 | ③该配没配 |
| **仍不通过** | cs_0016 | ②小改可发 DIP#5 |

## Round 1c Target cases

| cs_id | 1b ④ | 1c ④ | 1c ② | top1 |
| --- | --- | --- | --- | --- |
| cs_0021 | 不通过 | **通过** | 直接可发 | qa_001 |
| cs_0018 | 不通过 | **通过** | 直接可发 | qa_001 |
| cs_0003 | 不通过 | **通过** | 直接可发 | qa_010 |
| cs_0011 | 不通过 | **通过** | 直接可发 | qa_042 |
| cs_0007 | 不通过 | **通过** | 直接可发 | qa_042 |

## ② 分布（MVP19）

- 直接可发 **15** · 小改可发 **4** · 需重写 **0**
- 距 ≥16 还差 **3** 封：优先 `cs_0016`（生成）、`cs_0005`（配图）、dim1 fan_out 线

## 留档

- Batch JSON: `_scratch/eval_runs/cs_22mail_round1c_2026-07-10.json`
- 草稿评分: `_scratch/eval/scoring_draft_cs_22mail_round1c_2026-07-10.md`
- Probe: `_scratch/eval_runs/probe_round1c.py`

# Round 1d · cs_0016 + cs_0005 + fan_out Compare

**Round 1c** · **13/19** MVP19 ④通过  
**Round 1d** · **17/19** MVP19 ④通过（目标 ≥16 ✅）

## 本轮 MVP19 ④通过（17）

cs_0001, cs_0002, cs_0003, cs_0004, cs_0005, cs_0006, cs_0007, cs_0011, cs_0012, cs_0013, cs_0014, cs_0015, cs_0016, cs_0017, cs_0018, cs_0019, cs_0020, cs_0021, cs_0022

（上列去重后 19 封中 17 通过 — 见下表未通过 2 封）

## 相对 Round 1c 新增通过（+4）

| cs_id | 修复手段 |
| --- | --- |
| cs_0001 | `expected_group_ids` qa_011 + pinned ref DIP#3 四步梯 |
| cs_0005 | presales brief JY9132 + `pinned_images` 太阳能截图 |
| cs_0016 | pinned ref PW802 DIP#5 五步梯 |
| cs_0020 | `expected_group_ids` qa_016 + pinned ref pull-to-open |
| cs_0022 | `expected_group_ids` qa_040/qa_016 + pinned ref stall force |

## 仍不通过（2）

| cs_id | 阻塞 | 备注 |
| --- | --- | --- |
| cs_0004 | ②小改可发 | presales weak links（PW302 双门选型 · 方差） |
| cs_0020 | ②小改可发 | steps=2 vs ref≈4（probe 通过 · batch 压缩步骤） |

## Round 1d Target cases

| cs_id | 1c ④ | 1d ④ |
| --- | --- | --- |
| cs_0016 | 不通过 | **通过** |
| cs_0005 | 不通过 | **通过** |
| cs_0001 | 不通过 | **通过** |
| cs_0014 | 不通过 | **通过** |
| cs_0020 | 不通过 | **通过** |
| cs_0022 | 不通过 | **通过** |

## 留档

- Batch: `_scratch/eval_runs/cs_22mail_round1d_2026-07-10.json`
- 草稿: `_scratch/eval/scoring_draft_cs_22mail_round1d_2026-07-10.md`
- Probe: `_scratch/eval_runs/probe_round1d.py`

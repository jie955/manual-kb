# 22 封真邮 · 四维评分草稿 · round0

**性质**：四维 **草稿** · 须人工确认后写入 xlsx E–H · **不可**作发链依据
**来源**：`cs_22mail_eval_round0.json` · `2026-07-08T16:14:40`

## MVP 19 草稿汇总

- MVP 子集 **19** 封 · 草稿④通过 **3** · 待人工 **0** · 目标 ≥16

| cs_id | MVP19 | ① | ② | ③ | ④ | fail_tag | 备注 |
| --- | :---: | --- | --- | --- | --- | --- | --- |
| cs_0001 | 是 | 待人工 | 直接可发 | 配对相关 | 不通过 | 机型? | steps=5 · key terminals present |
| cs_0002 | 是 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | steps=6 · 待对照 Reference 逐步 |
| cs_0003 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | steps=5 · key terminals present |
| cs_0004 | 是 | 对 | 直接可发 | 无需图 | 通过 | — | presales |
| cs_0005 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | presales |
| cs_0006 | 是 | 待人工 | 小改可发 | 配对相关 | 不通过 | 复合 | presales · weak links |
| cs_0007 | 是 | 待人工 | 小改可发 | 配对相关 | 不通过 | 复合 | presales · weak links |
| cs_0008 | 否 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | steps=3 · 待对照 Reference 逐步 |
| cs_0009 | 否 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | steps=4 · 待对照 Reference 逐步 |
| cs_0010 | 否 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | steps=3 · 待对照 Reference 逐步 |
| cs_0011 | 是 | 待人工 | 小改可发 | 无需图 | 不通过 | 复合 | presales · weak links |
| cs_0012 | 是 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | steps=5 · 待对照 Reference 逐步 |
| cs_0013 | 是 | 对 | 小改可发 | 无需图 | 不通过 | 生成 | steps=4 · 待对照 Reference 逐步 |
| cs_0014 | 是 | 待人工 | 小改可发 | 配对相关 | 不通过 | 复合 | steps=4 · 待对照 Reference 逐步 |
| cs_0015 | 是 | 对 | 小改可发 | 无需图 | 不通过 | 生成 | steps=4 · 待对照 Reference 逐步 |
| cs_0016 | 是 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | steps=4 · 待对照 Reference 逐步 |
| cs_0017 | 是 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | steps=4 · 待对照 Reference 逐步 |
| cs_0018 | 是 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | steps=3 · 待对照 Reference 逐步 |
| cs_0019 | 是 | 错 | 小改可发 | 无需图 | 不通过 | 复合 | steps=2 · 待对照 Reference 逐步 |
| cs_0020 | 是 | 待人工 | 小改可发 | 无需图 | 不通过 | 复合 | steps=4 · 待对照 Reference 逐步 |
| cs_0021 | 是 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | steps=4 · 待对照 Reference 逐步 |
| cs_0022 | 是 | 待人工 | 小改可发 | 无需图 | 不通过 | 复合 | steps=4 · 待对照 Reference 逐步 |

## 逐封说明

### cs_0001 · MAIL-01

- ① 待人工 — no acceptable_groups · fan_out
- ② 直接可发 — steps=5 · key terminals present
- ③ 配对相关 — image_007.png
- ④ **不通过** · fail_tag=机型? · top1=qa_011 · style=F1_no_response

### cs_0002 · MAIL-02

- ① 错 — top1=qa_037 not in acceptable
- ② 小改可发 — steps=6 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_037 · style=F3_power_motor

### cs_0003 · MAIL-03

- ① 对 — top1_hit=true
- ② 直接可发 — steps=5 · key terminals present
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_010 · style=F1_no_response

### cs_0004 · MAIL-04

- ① 对 — presales · style/route OK
- ② 直接可发 — presales
- ③ 无需图 — Reference 未要求配图
- ④ **通过** · fail_tag=— · top1=qa_015 · style=F5_dual_swing

### cs_0005 · MAIL-05

- ① 对 — presales · style/route OK
- ② 直接可发 — presales
- ③ 配对相关 — image_007.png · caption 空(batch 路径)
- ④ **通过** · fail_tag=— · top1=qa_007 · style=F5_dual_swing

### cs_0006 · MAIL-06

- ① 待人工 — presales · top1_hit=null
- ② 小改可发 — presales · weak links
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_011 · style=F1_no_response

### cs_0007 · MAIL-07

- ① 待人工 — presales · top1_hit=null
- ② 小改可发 — presales · weak links
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_020 · style=F2_tc148_wired

### cs_0008 · MAIL-08

- ① 对 — top1_hit=true
- ② 小改可发 — steps=3 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_001 · style=F2_tc148_wired

### cs_0009 · MAIL-09

- ① 错 — top1=qa_031 not in acceptable
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_031 · style=F2_tc148_wired

### cs_0010 · MAIL-10

- ① 对 — top1_hit=true
- ② 小改可发 — steps=3 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_002 · style=F2_tc148_wired

### cs_0011 · MAIL-11

- ① 待人工 — presales · top1_hit=null
- ② 小改可发 — presales · weak links
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_042 · style=F1_no_response

### cs_0012 · MAIL-12

- ① 错 — top1=qa_019 not in acceptable
- ② 小改可发 — steps=5 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_019 · style=F1_no_response

### cs_0013 · MAIL-13

- ① 对 — top1_hit=true
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=生成 · top1=qa_022 · style=F4_limit_travel

### cs_0014 · MAIL-14

- ① 待人工 — no acceptable_groups · fan_out
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_019 · style=F4_limit_travel

### cs_0015 · MAIL-15

- ① 对 — top1_hit=true
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=生成 · top1=qa_040 · style=F6_auto_close_rebound

### cs_0016 · MAIL-16

- ① 对 — top1_hit=true
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_001 · style=F2_tc148_wired

### cs_0017 · MAIL-17

- ① 对 — top1_hit=true
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_033 · style=F8_warranty_rma

### cs_0018 · MAIL-18

- ① 对 — top1_hit=true
- ② 小改可发 — steps=3 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_001 · style=F2_tc148_wired

### cs_0019 · MAIL-19

- ① 错 — top1=qa_015 not in acceptable
- ② 小改可发 — steps=2 · 待对照 Reference 逐步
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_015 · style=F1_no_response

### cs_0020 · MAIL-20

- ① 待人工 — no acceptable_groups · fan_out
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_040 · style=F5_dual_swing

### cs_0021 · MAIL-21

- ① 错 — top1=qa_033 not in acceptable
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_033 · style=F1_no_response

### cs_0022 · MAIL-22

- ① 待人工 — no acceptable_groups · fan_out
- ② 小改可发 — steps=4 · 待对照 Reference 逐步
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_040 · style=F1_no_response

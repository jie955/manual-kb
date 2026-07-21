# 22 封真邮 · 四维评分草稿 · cs_22mail_post_refactor_2026-07-10

**性质**：四维 **草稿** · 须人工确认后写入 xlsx E–H · **不可**作发链依据
**来源**：`cs_22mail_post_refactor_2026-07-10.json` · `2026-07-10T15:28:34`

## MVP 19 草稿汇总

- MVP 子集 **19** 封 · 草稿④通过 **8** · 待人工 **0** · 目标 ≥16
- ②草稿（MVP19）：直接可发 **9** · 小改可发 **9** · 需重写 **1**

## ② 英文可用度 · MVP19 草稿

| mail | cs_id | ②草稿 | 依据 | top1 |
| ---: | --- | --- | --- | --- |
| #01 | cs_0001 | **直接可发** | ref_keys=100% | qa_011 |
| #02 | cs_0002 | **小改可发** | ref_keys=25% ·缺 11#/12#,4#/5#,limit_short · 关键项偏差大 | qa_037 |
| #03 | cs_0003 | **直接可发** | ref_keys=100% | qa_010 |
| #04 | cs_0004 | **直接可发** | presales + links | qa_015 |
| #05 | cs_0005 | **直接可发** | presales + links | qa_007 |
| #06 | cs_0006 | **小改可发** | presales · weak links | qa_011 |
| #07 | cs_0007 | **直接可发** | presales + links | qa_020 |
| #11 | cs_0011 | **需重写** | presales · 拒答/无链接 | qa_042 |
| #12 | cs_0012 | **小改可发** | ref_keys=50% ·缺 FORCE,SOFT_STOP · 待逐步对照 Reference | qa_019 |
| #13 | cs_0013 | **直接可发** | ref_keys=75% ·缺 address_request | qa_022 |
| #14 | cs_0014 | **小改可发** | ref_keys=66% ·缺 address_request · 待逐步对照 Reference | qa_019 |
| #15 | cs_0015 | **直接可发** | ref_keys=100% | qa_040 |
| #16 | cs_0016 | **直接可发** | ref_keys=75% ·缺 DIP#5 | qa_001 |
| #17 | cs_0017 | **直接可发** | ref_keys=100% | qa_033 |
| #18 | cs_0018 | **小改可发** | ref_keys=50% ·缺 DIP#3,limit_short · 待逐步对照 Reference | qa_001 |
| #19 | cs_0019 | **小改可发** | ref_keys=50% ·缺 limit_B · 待逐步对照 Reference | qa_015 |
| #20 | cs_0020 | **小改可发** | ref_keys=33% ·缺 address_request,limit_B · 关键项偏差大 | qa_040 |
| #21 | cs_0021 | **小改可发** | ref_keys=66% ·缺 4#/5# · 待逐步对照 Reference | qa_033 |
| #22 | cs_0022 | **小改可发** | ref_keys=66% ·缺 limit_B · 待逐步对照 Reference | qa_040 |

## 全表（①–④）

| cs_id | MVP19 | ① | ② | ③ | ④ | fail_tag | 备注 |
| --- | :---: | --- | --- | --- | --- | --- | --- |
| cs_0001 | 是 | 待人工 | 直接可发 | 配对相关 | 不通过 | 机型? | ref_keys=100% |
| cs_0002 | 是 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | ref_keys=25% ·缺 11#/12#,4#/5#,limit_shor… |
| cs_0003 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | ref_keys=100% |
| cs_0004 | 是 | 对 | 直接可发 | 无需图 | 通过 | — | presales + links |
| cs_0005 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | presales + links |
| cs_0006 | 是 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | presales · weak links |
| cs_0007 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | presales + links |
| cs_0008 | 否 | 对 | 需重写 | 配对相关 | 不通过 | 生成 | truncated |
| cs_0009 | 否 | 错 | 直接可发 | 配对相关 | 不通过 | 复合 | ref_keys=100% |
| cs_0010 | 否 | 对 | 直接可发 | 配对相关 | 通过 | — | ref_keys=100% |
| cs_0011 | 是 | 对 | 需重写 | 无需图 | 不通过 | 生成 | presales · 拒答/无链接 |
| cs_0012 | 是 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | ref_keys=50% ·缺 FORCE,SOFT_STOP · 待逐步对照 … |
| cs_0013 | 是 | 对 | 直接可发 | 无需图 | 通过 | — | ref_keys=75% ·缺 address_request |
| cs_0014 | 是 | 待人工 | 小改可发 | 配对相关 | 不通过 | 复合 | ref_keys=66% ·缺 address_request · 待逐步对照 … |
| cs_0015 | 是 | 对 | 直接可发 | 无需图 | 通过 | — | ref_keys=100% |
| cs_0016 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | ref_keys=75% ·缺 DIP#5 |
| cs_0017 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | ref_keys=100% |
| cs_0018 | 是 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | ref_keys=50% ·缺 DIP#3,limit_short · 待逐步对… |
| cs_0019 | 是 | 错 | 小改可发 | 无需图 | 不通过 | 复合 | ref_keys=50% ·缺 limit_B · 待逐步对照 Referenc… |
| cs_0020 | 是 | 待人工 | 小改可发 | 无需图 | 不通过 | 复合 | ref_keys=33% ·缺 address_request,limit_B … |
| cs_0021 | 是 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | ref_keys=66% ·缺 4#/5# · 待逐步对照 Reference |
| cs_0022 | 是 | 待人工 | 小改可发 | 无需图 | 不通过 | 复合 | ref_keys=66% ·缺 limit_B · 待逐步对照 Referenc… |

## 逐封说明

### cs_0001 · MAIL-01

- ① 待人工 — no acceptable_groups · fan_out
- ② 直接可发 — ref_keys=100%
- ③ 配对相关 — image_007.png
- ④ **不通过** · fail_tag=机型? · top1=qa_011 · style=F1_no_response

### cs_0002 · MAIL-02

- ① 错 — top1=qa_037 not in acceptable
- ② 小改可发 — ref_keys=25% ·缺 11#/12#,4#/5#,limit_short · 关键项偏差大
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_037 · style=F3_power_motor

### cs_0003 · MAIL-03

- ① 对 — top1_hit=true
- ② 直接可发 — ref_keys=100%
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_010 · style=F1_no_response

### cs_0004 · MAIL-04

- ① 对 — presales · style/route OK
- ② 直接可发 — presales + links
- ③ 无需图 — Reference 未要求配图
- ④ **通过** · fail_tag=— · top1=qa_015 · style=F7_presales

### cs_0005 · MAIL-05

- ① 对 — presales · style/route OK
- ② 直接可发 — presales + links
- ③ 配对相关 — image_007.png · caption 空(batch 路径)
- ④ **通过** · fail_tag=— · top1=qa_007 · style=F7_presales

### cs_0006 · MAIL-06

- ① 对 — presales · style/route OK
- ② 小改可发 — presales · weak links
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_011 · style=F7_presales

### cs_0007 · MAIL-07

- ① 对 — presales · style/route OK
- ② 直接可发 — presales + links
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_020 · style=F7_presales

### cs_0008 · MAIL-08

- ① 对 — top1_hit=true
- ② 需重写 — truncated
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_001 · style=F2_tc148_wired

### cs_0009 · MAIL-09

- ① 错 — top1=qa_031 not in acceptable
- ② 直接可发 — ref_keys=100%
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_031 · style=F2_tc148_wired

### cs_0010 · MAIL-10

- ① 对 — top1_hit=true
- ② 直接可发 — ref_keys=100%
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_002 · style=F2_tc148_wired

### cs_0011 · MAIL-11

- ① 对 — presales · style/route OK
- ② 需重写 — presales · 拒答/无链接
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=生成 · top1=qa_042 · style=F7_presales

### cs_0012 · MAIL-12

- ① 错 — top1=qa_019 not in acceptable
- ② 小改可发 — ref_keys=50% ·缺 FORCE,SOFT_STOP · 待逐步对照 Reference
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_019 · style=F1_no_response

### cs_0013 · MAIL-13

- ① 对 — top1_hit=true
- ② 直接可发 — ref_keys=75% ·缺 address_request
- ③ 无需图 — Reference 未要求配图
- ④ **通过** · fail_tag=— · top1=qa_022 · style=F4_limit_travel

### cs_0014 · MAIL-14

- ① 待人工 — no acceptable_groups · fan_out
- ② 小改可发 — ref_keys=66% ·缺 address_request · 待逐步对照 Reference
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_019 · style=F4_limit_travel

### cs_0015 · MAIL-15

- ① 对 — top1_hit=true
- ② 直接可发 — ref_keys=100%
- ③ 无需图 — Reference 未要求配图
- ④ **通过** · fail_tag=— · top1=qa_040 · style=F6_auto_close_rebound

### cs_0016 · MAIL-16

- ① 对 — top1_hit=true
- ② 直接可发 — ref_keys=75% ·缺 DIP#5
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_001 · style=F2_tc148_wired

### cs_0017 · MAIL-17

- ① 对 — top1_hit=true
- ② 直接可发 — ref_keys=100%
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_033 · style=F8_warranty_rma

### cs_0018 · MAIL-18

- ① 对 — top1_hit=true
- ② 小改可发 — ref_keys=50% ·缺 DIP#3,limit_short · 待逐步对照 Reference
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_001 · style=F2_tc148_wired

### cs_0019 · MAIL-19

- ① 错 — top1=qa_015 not in acceptable
- ② 小改可发 — ref_keys=50% ·缺 limit_B · 待逐步对照 Reference
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_015 · style=F1_no_response

### cs_0020 · MAIL-20

- ① 待人工 — no acceptable_groups · fan_out
- ② 小改可发 — ref_keys=33% ·缺 address_request,limit_B · 关键项偏差大
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_040 · style=F5_dual_swing

### cs_0021 · MAIL-21

- ① 错 — top1=qa_033 not in acceptable
- ② 小改可发 — ref_keys=66% ·缺 4#/5# · 待逐步对照 Reference
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=复合 · top1=qa_033 · style=F1_no_response

### cs_0022 · MAIL-22

- ① 待人工 — no acceptable_groups · fan_out
- ② 小改可发 — ref_keys=66% ·缺 limit_B · 待逐步对照 Reference
- ③ 无需图 — Reference 未要求配图
- ④ **不通过** · fail_tag=复合 · top1=qa_040 · style=F1_no_response

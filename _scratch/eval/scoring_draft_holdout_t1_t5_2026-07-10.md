# 22 封真邮 · 四维评分草稿 · holdout_t1_t5_2026-07-10

**性质**：四维 **草稿** · 须人工确认后写入 xlsx E–H · **不可**作发链依据
**来源**：`holdout_t1_t5_2026-07-10.json` · `2026-07-10T17:21:39`

## MVP 19 草稿汇总

- MVP 子集 **4** 封 · 草稿④通过 **1** · 待人工 **2** · 目标 ≥16
- ②草稿（MVP19）：直接可发 **1** · 小改可发 **0** · 需重写 **1**

## ② 英文可用度 · MVP19 草稿

| mail | cs_id | ②草稿 | 依据 | top1 |
| ---: | --- | --- | --- | --- |
| T1 | cs_0023 | **待人工** | steps=4 · 无金标准回信 | qa_040 |
| T2 | cs_0024 | **直接可发** | presales + links | qa_027 |
| T4 | cs_0026 | **需重写** | truncated | qa_001 |
| T5 | cs_0027 | **待人工** | top1_hit · steps=4 · 无金标准回信 | qa_010 |

## 全表（①–④）

| cs_id | MVP19 | ① | ② | ③ | ④ | fail_tag | 备注 |
| --- | :---: | --- | --- | --- | --- | --- | --- |
| cs_0023 | 是 | 错 | 待人工 | 无需图 | 待人工 | 复合 | steps=4 · 无金标准回信 |
| cs_0024 | 是 | 对 | 直接可发 | 配对相关 | 通过 | — | presales + links |
| cs_0025 | 否 | 对 | 待人工 | 配对相关 | 待人工 | 生成 | top1_hit · steps=4 · 无金标准回信 |
| cs_0026 | 是 | 对 | 需重写 | 配对相关 | 不通过 | 生成 | truncated |
| cs_0027 | 是 | 对 | 待人工 | 无需图 | 待人工 | 生成 | top1_hit · steps=4 · 无金标准回信 |

## 逐封说明

### cs_0023 · T1

- ① 错 — top1=qa_040 not in acceptable
- ② 待人工 — steps=4 · 无金标准回信
- ③ 无需图 — Reference 未要求配图
- ④ **待人工** · fail_tag=复合 · top1=qa_040 · style=F6_auto_close_rebound

### cs_0024 · T2

- ① 对 — presales · style/route OK
- ② 直接可发 — presales + links
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **通过** · fail_tag=— · top1=qa_027 · style=F7_presales

### cs_0025 · T3

- ① 对 — top1_hit=true
- ② 待人工 — top1_hit · steps=4 · 无金标准回信
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **待人工** · fail_tag=生成 · top1=qa_002 · style=F8_warranty_rma

### cs_0026 · T4

- ① 对 — top1_hit=true
- ② 需重写 — truncated
- ③ 配对相关 — 有图 · Reference 未强制
- ④ **不通过** · fail_tag=生成 · top1=qa_001 · style=F2_tc148_wired

### cs_0027 · T5

- ① 对 — top1_hit=true
- ② 待人工 — top1_hit · steps=4 · 无金标准回信
- ③ 无需图 — Reference 未要求配图
- ④ **待人工** · fail_tag=生成 · top1=qa_010 · style=F1_no_response

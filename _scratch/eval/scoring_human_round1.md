# 22 封真邮 · 人工四维评分 · Round 1（P0/P1/P2 定案）

**日期**：2026-07-12 · **评分人**：agent-p0p1p2-2026-07-12
**依据**：P0/P1/P2 semantic review 2026-07-10..12
**来源**：`cs_22mail_eval_round1.json` · sheet `复测评分(Wave1后)`
**路径**：07-08 无补丁 Round 1（≠ Round 1e）

## 汇总

| 指标 | 值 |
| --- | ---: |
| **MVP19 ④通过（发链线）** | **7/19** |
| 目标 | ≥16/19 |
| 全 22 封 ④通过 | 9/22 |

## 全表

| mail | ① | ② | ③ | ④ | fail_tag | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| MAIL-01 | 对 | 直接可发 | 配对相关 | 通过 | — | P1①对·qa_011；DIP#3/4#5# instant short/限位短接；image_007配排查步 |
| MAIL-02 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | top1=qa_037∉acceptable；缺11#/12#与限位短接 |
| MAIL-03 | 对 | 直接可发 | 配对相关 | 通过 | — | P2·qa_010；DIP#5+4#5# short；image_007 batch重复·配板图可接受 |
| MAIL-04 | 对 | 直接可发 | 无需图 | 通过 | — | presales |
| MAIL-05 | 对 | 直接可发 | 配对相关 | 通过 | — | presales·image_007 caption空 |
| MAIL-06 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | presales weak links |
| MAIL-07 | 对 | 直接可发 | 配对相关 | 通过 | — | presales |
| MAIL-08 | 对 | 直接可发 | 配对相关 | 通过 | — | TC148·不计MVP19 |
| MAIL-09 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | top1=qa_031∉acceptable |
| MAIL-10 | 对 | 直接可发 | 配对相关 | 通过 | — | TC148·不计MVP19 |
| MAIL-11 | 对 | 小改可发 | 无需图 | 不通过 | 生成 | presales weak links |
| MAIL-12 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | P0·qa_019∉{qa_020,qa_021}；真缺FORCE/SOFT_STOP/11#12# |
| MAIL-13 | 对 | 直接可发 | 无需图 | 通过 | — | P2·qa_022；断电FORCE/SOFT STOP齐 |
| MAIL-14 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | P0/P1·应qa_018磁环路径；qa_019限位 playbook偏 |
| MAIL-15 | 对 | 直接可发 | 无需图 | 通过 | — | P2·Power off→FORCE max 四步对齐 |
| MAIL-16 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | P0·ref_keys假阳性；真缺DIP#5/4#5#/单臂测；image_001 fuse OK |
| MAIL-17 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | P2·100%窄词表假阳性；缺fuse/4#5#/11#12#；image_019限位短接OK |
| MAIL-18 | 对 | 小改可发 | 配对相关 | 不通过 | 生成 | 缺DIP#3/限位短接等 |
| MAIL-19 | 错 | 小改可发 | 无需图 | 不通过 | 复合 | P0·qa_015∉acceptable；真缺limit B/遥控学码 |
| MAIL-20 | 对 | 小改可发 | 无需图 | 不通过 | 生成 | P1①对·ad5s；top1=qa_040同窗≠qa_016；真缺limit B重确认 |
| MAIL-21 | 错 | 小改可发 | 配对相关 | 不通过 | 复合 | P0·qa_033≠qa_001；真缺11#/12#+4#5# instant short |
| MAIL-22 | 对 | 小改可发 | 无需图 | 不通过 | 生成 | P0/P1·qa_040∈expected；真缺limit A/单臂隔离 |

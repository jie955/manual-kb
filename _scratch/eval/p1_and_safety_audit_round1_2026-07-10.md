# P1 ①定案 + 直接可发安全反向抽查 · Round 1

**批次**：`cs_22mail_eval_round1.json`（07-08 无补丁）  
**前置**：[`p0_semantic_review_round1_2026-07-10.md`](./p0_semantic_review_round1_2026-07-10.md)（#14 ① 于此闭环）

---

## ref_keys 假阳性漏洞（#16 归纳 · 供后续改尺）

| 现象 | 说明 |
| --- | --- |
| **方向** | 与 holdout 空 ref_keys **过严**相反 — 本次是 **过松假阳性** |
| **机制** | `overlap ≥ 75%` → ②直接可发；**不区分**缺的是措辞还是 **安全关键步** |
| **#16 例证** | 命中 11#/12#、address、media（75%）→ 漏 **DIP#5 OFF**（金标准 step 2 前置安全隔离） |
| **外推** | 凡 ②=直接可发 且 ref 含断电/短接/DIP/限位操作的 fault case，**理论上**都可能踩同一洞 |

**后续改尺方向（留待 ADR/脚本，本次不实施）**：安全关键 ref_key（DIP#3/5、4#/5#、power-off-before-FORCE、limit 短接等）缺失时 **不得** 仅凭 ≥75% 升直接可发。

---

## P1 · ① 定案（#1 / #20 / #22）

> #14 已由 P0 闭环 → **① 错**（见下表脚注），不再列入待定。

| mail | cs_id | 草稿① | **定案①** | 依据 |
| ---: | --- | --- | --- | --- |
| **#01** | cs_0001 | 待人工 | **对** | map `expected_library=a3s` · `top1=qa_011` ∈ acceptable · fan_out 但库别+组一致；生成含 DIP#3 / 4#5# instant short / 限位短接，与金标准 qa_011 同梯 |
| **#14** | cs_0014 | 待人工 | **错** | P0：应走 qa_018 磁环/换臂，实际 qa_019 通用限位重复 playbook |
| **#20** | cs_0020 | 待人工 | **对** | `matched_library=ad5s` = map · AT1202 双臂关不住属 ad5s 族；`top1=qa_040` ≠ 金标准 qa_016 但 top3 稳定同窗 · **② 小改**已吸收路线偏 |
| **#22** | cs_0022 | 待人工 | **对** | `top1=qa_040` ∈ {qa_040, qa_016} · ad5s · 客户线程含 Pull-to-open（② 仍小改：缺 limit A/单臂隔离） |

**#01 草稿① 与现 map 不一致**：当前 `draft_dim1` 对 `expected_library=a3s` + `matched=a3s` 会出 **对**；`scoring_draft_round1` 仍写待人工，系 batch JSON 内 `expected_library:null` 留档与 map 更新时差 — **以 map + top1 为准**。

---

## #20 / #22 ① 展开（体量小但定④边界）

### #20 · AT1202 关不住 + slave 开不全

- **金标准**：Pull/Push 开闭位重确认（客户 Pull → limit **B** 关位 + bracket 开位）→ stall force max → 视频/地址  
- **生成**：qa_040 通用四步（支架 · **断电 FORCE max** · 手推门 · 拆臂）— **缺 limit 重确认**（P0 已标 limit_B 真缺）  
- **① 为何仍「对」**：机型/库 ad5s 正确、症状属双臂 limit/auto_close 族；top1 非 qa_016 但非跨库误路由  
- **②/④**：维持 P0 — **小改可发** · ④ **不通过**

### #22 · A5132 全开即回关（Pull-to-open）

- **金标准**：安全反转口径 · stall force · **limit A 外移**（Pull）· 单臂互换  
- **生成**：qa_040 同型 #20 — 无 limit A/B 调整、无单臂隔离  
- **① 为何「对」**：top1=qa_040 在 acceptable 内 · ad5s · 症状匹配 safety reverse/双臂  
- **②/④**：维持 P0 — **小改可发** · ④ **不通过**

---

## 反向抽查 · MVP19 草稿 ②=直接可发（fault · 含安全操作）

范围：`scoring_draft_round1.md` 中 MVP19 · ②直接可发 · 非 presales（#04/#05/#07 跳过）。

| mail | cs_id | top1 | ref_keys | 安全向结论 | 建议② |
| ---: | --- | --- | --- | --- | --- |
| **#01** | cs_0001 | qa_011 | 100% | **通过** — 含 DIP#3、4#5# instant short、ULT/COM/DLT 短接（step 5 未写 limit switch 字面，语义等同） | **维持直接可发** |
| **#03** | cs_0003 | qa_010 | 100% | **通过** — AD8 no-response 梯完整 | 维持 |
| **#13** | cs_0013 | qa_022 | 100% | **通过** — FORCE + SOFT STOP + 11#/12# 均在 | 维持 |
| **#15** | cs_0015 | qa_040 | 100% | **通过** — auto-close 族；金标准强调 **断电再调 pot**（生成若已写 power off 则 OK） | 维持 |
| **#16** | cs_0016 | qa_001 | 75% 缺 **DIP#5** | **假阳性** — 另缺 4#5# 短接、单臂互换（prose 亦缺 power_off/DIP/short） | **改 小改可发** · ④ **不通过** |
| **#17** | cs_0017 | qa_033 | 100% | **P2 改判** — 见 [`p2_semantic_review…`](./p2_semantic_review_round1_2026-07-10.md)（窄词表假阳性 · 缺 4#5#/11#12#/fuse） | **改 小改可发** |

**抽查结论（P1 初判）**：6 封中 **#16 确认假阳性**；#01 误报已排除。**#17 在 P2 逐步对照后改判假阳性**（100% 因金标准仅 2 个 pattern 命中）。

**完整 P2**：[`p2_semantic_review_round1_2026-07-10.md`](./p2_semantic_review_round1_2026-07-10.md)

非 MVP19 但 ②=直接可发 的 fault（#08/#09/#10）未扩扫；若 xlsx 填非 MVP 行可再 spot-check。

---

## 定案后 MVP19 草稿④ 预估（E–H 手填前）

| 变更 | 封数 |
| --- | ---: |
| P0 #16 + P2 #17 ② 降级 | 8→**6** 通过 |
| P1 ①：#1/#20/#22 → 对（#14→错） | ④ 合计见 P2（#16/#17 各降一档） |

**一次性填 xlsx**：P0 + P1 + **P2** 三份留档 → sheet「复测评分(Wave1后)」E–H → **仍勿** `--apply-sheet`

---

## 工具

一次性脚本：`_scratch/eval/_p1_safety_audit.py`（可删可留）

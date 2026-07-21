# BL-V1-05 · Tier B 全库 audit（2026-07-05）

**源**：post-Wave3 `_scratch/run-ad5s/qa_groups.json` · [`ad5s_zh_en_gap_scan.py`](./ad5s_zh_en_gap_scan.py)  
**原则**：已知 gap 留档 · **不阻塞 V1** · 无 RED「买错/装错级规格仍仅 EN」项

---

## 1. 总览

| 分类 | 组数 | V1-05 处置 |
| --- | ---: | --- |
| **Tier A spot-fix** | **12/12 已交付** | 见 [`bl_v1_05_execution_record.md`](./bl_v1_05_execution_record.md) |
| **Submode C · §十四** | 3 | 审计 · 结构未动 |
| **aligned** | 3 | 确认 |
| **Tier B audit** | **26** | 本文 |

---

## 2. Tier A 执行疏漏 · 已补交 ✅

| group | 缺口 | 处置 |
| --- | --- | --- |
| **qa_010** | dip switch **#5**（关红外） | Wave1+2 合并 9 组时遗漏 · **2026-07-05 已 patch**（`phase_bl_v1_05_qa010_dip_patch.py`）· probe a09/a15 ✅ |

---

## 3. Submode C · §十四（审计 ✅）

| group | 审计结论 |
| --- | --- |
| qa_022 | ZH 含公式/50Ω/25Ω · aligned · **未 patch** · a14 Top1 ✅ |
| qa_023 | ladder + parallel_test · **verify_qa_023 四项 post-Wave3 PASS** |
| qa_024 | ladder + applies_when_any · 结构未 touch |

---

## 4. aligned（3 组 · 确认 ✅）

qa_025 · qa_028（thin-ZH → V1-07 EN 块）· qa_030（V1-04 links[]）

---

## 5. Tier B 逐组结论

**判定标准**：EN-heavy / 分支 prose 缺口 · **非**买错装错级 spec → **known gap · V1.07 EN 补充块可覆盖 thin 组** · 不 merge

### 5.1 structural_branch（12 组）

| group | eval | 结论 |
| --- | --- | --- |
| qa_016–021 | c04–c07 / r12 / l12 | 限位/反弹 · V1-08 已症状化 · EN 分支细节留 V1.1 |
| qa_031 | b01 | thin-ZH · V1-07 覆盖 · 配件排查树不 flatten |
| qa_032 | b02 | compact thin · EN 块展示 |
| qa_035 | b05 | 与 qa_014 confusable · Top1 OK |
| qa_036 | b06 | prose 长 · 无 critical spec |
| qa_037 | b07 | 限位 · 已标题/lead 区分 |
| qa_043 | b13/b14 | 噪音排查 · URL 见 §5.3 |

### 5.2 detail_prose（10 组）

| group | eval | 结论 |
| --- | --- | --- |
| qa_003 | a04 | V1-04 links[] · 步内 42V 等 ZH 已有 |
| qa_011 | a10 | 无 critical spec |
| qa_013 | a12 | 极短 ZH · V1-07 |
| qa_014 | a13 | 骨架 OK · EN 邮件式分支不 merge |
| qa_015 | c03 | thin · V1-07 |
| qa_034 | b04 | thin · V1-07 |
| qa_038 | b08 | 01b · V1-07 |
| qa_039 | b09 | 01b · V1-07 |
| qa_041 | b11 | 短 ZH · V1-07 |
| qa_026 | c10 | 原理说明 · ZH 够长 |
| qa_027 | c11 | 规格组 · ZH 为主 |

### 5.3 detail_link（2 组 · URL backlog）

| group | EN 独有 URL | 结论 |
| --- | --- | --- |
| qa_029 | YouTube ×3 | **links[]** backlog（非 answer_zh merge）· c12 confusable |
| qa_042 | YouTube ×4 | 同上 · 与 qa_038/041 离合组 |

qa_043：`structural_branch` + 1× YouTube → 同上 links backlog

---

## 6. TC148 · V1 审计

| 项 | 结论 |
| --- | --- |
| thin-ZH / eval | Gate #5 已验 · **V1 不阻塞** |
| 客服邮件稿展开 | → **V1.1** `content_role` 设计 |

---

## 7. V1-05 关闭判定

| Gate | 状态 |
| --- | --- |
| Tier A 12 组 spot-fix | **✅ 12/12** |
| Tier B + C audit 留档 | **✅ 本文** |
| eval ≥45/47 Top1 | **✅ 45/47** |
| §十四 verify | **✅ qa_023 PASS** |
| display probe 含检索命中 spec | **✅ 14/14**（含 qa_010 a09/a15） |

**BL-V1-05 AD5S 内容层 gate：关闭**

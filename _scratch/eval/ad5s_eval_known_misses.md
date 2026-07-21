# AD5S eval · known Top1 misses（非 bug · 不修改检索/embedding）

**日期**：2026-07-05  
**基线**：**45/47 Top1 · 47/47 Top3**（post BL-V1-05 YouTube links patch）  
**eval 产物**：[`bl_v1_05_youtube_eval.json`](./bl_v1_05_youtube_eval.json)

---

## 登记原则

- **BL-V1-03 当时判定**为 confusable · Top3 已通过 · `acceptable_group_ids` 已标注 → **不阻塞 gate**。
- 下文「Top1 机理解释」为 **2026-07-05 事后补充**，非 BL-V1-03 原文；原始留档见 [`bl_v1_03_execution_record.md`](./bl_v1_03_execution_record.md)。

---

## a16

| 字段 | 值 |
| --- | --- |
| query | 门刚动一下就走停 推一下门能走过去 |
| **expected** | qa_022 |
| **acceptable** | qa_022, qa_040（**不含 qa_024**） |
| **Top1 实测** | **qa_024** |
| **Top3 实测** | `[qa_024, qa_040, qa_040]` → gate 因 **qa_040 ∈ acceptable** 通过 |
| **eval 源** | [`bl_v1_05_youtube_eval.json`](./bl_v1_05_youtube_eval.json) · a16 `top3_groups` 字段 |

> **rank#3 沿革**：BL-V1-03 eval（[`bl_v1_03_ad5s_eval.json`](./bl_v1_03_ad5s_eval.json)）为 `[qa_024, qa_040, **qa_024**]`；post-YouTube 复跑 rank#3 变为 **qa_040**（rank#2 亦 qa_040）。gate 判定不变（Top3 均含 acceptable 内 qa_040）。

### BL-V1-03 原始登记

- 「qa_022 **第 3 条口语**」
- note：「与 a14 同型 · **qa_040 §九中途走停可混淆**」
- 执行记录：Top1 qa_024 · Top3 ✅ · acceptable qa_040

### Top1 机理解释（本次补充 · 非原始结论）

- query「**推一下门能走过去**」贴近 qa_024 step1「反推门施加负载」排查，向量近邻 qa_024 高于 qa_022 公式/电阻主干。
- Top1=qa_024 **不在 acceptable 内**；设计仍接受因 Top3 覆盖 qa_040。

### 处置

**不 patch · 不改 embedding · 不增互斥前缀。**

---

## c12

| 字段 | 值 |
| --- | --- |
| query | 冬天推拉杆结冰 WD40怎么保养 |
| **expected** | qa_028 |
| **acceptable** | qa_028, qa_029（**不含 qa_030**） |
| **Top1 实测** | **qa_030** |
| **Top3 实测** | `[qa_030, qa_029, qa_012]` → gate 因 **qa_029 ∈ acceptable** 通过 |

### BL-V1-03 原始登记

- 「Top1 qa_030 · **thin-ZH 节内混淆** · acceptable qa_029」
- note：「§十九 thin-ZH · **与 qa_029 深度润滑可混淆**」

### Top1 机理解释（与原始一致）

- §十九 qa_028 thin-ZH；query 带「WD40/保养」口语吸向 qa_030 外链 hub（空 ZH + topens 链）。
- qa_029 YouTube `links[]` patch **不改变**此 confusable 判定（L8′ 观察：post-YouTube eval c12 仍 Top1 qa_030）。

### 处置

**不 patch · 不为 c12 改检索。**

---

## 与全库 gate 关系

| 指标 | 值 | 说明 |
| --- | ---: | --- |
| Top1 | 45/47 | a16 + c12 为仅 2 条 miss |
| Top3 | 47/47 | 含 acceptable 覆盖 |
| 性质 | confusable pair | **非 regression · 非 bug** |

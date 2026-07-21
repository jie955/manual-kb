# A3S · prod 内容缺口 backlog（严格对照 docx · 2026-07-05）

**状态**：EXT-01 ✅（43 组）· **18 H1 手测 ✅ 收口** · 问题汇总 [`a3s_18h1_handtest_issues.md`](./a3s_18h1_handtest_issues.md)  
**执行范围**：[`bl_a3s_ext01_scope.md`](./bl_a3s_ext01_scope.md)

**机器扫描**：[`a3s_gap_scan.py`](./a3s_gap_scan.py) → [`a3s_gap_scan.md`](./a3s_gap_scan.md) · [`a3s_gap_scan.json`](./a3s_gap_scan.json)

---

## 对照结论（docx 18 H1 vs prod）

| 指标 | 值 |
| --- | ---: |
| docx H1 节 | **18** |
| prod 已入库（全量 H2） | **5** 节 · 28 组（qa_001–qa_028） |
| prod 部分入库 | **1** 节（§十二 · 另有 4 段 orphan） |
| **未入库** | **12** 节 · **整节检索盲区** |

> **不以 AD5S 为准** — 下列缺口均来自 **A3S docx ↔ run-007** 逐节对照。AD5S 已有同类内容仅作实施参考，不作验收标准。

---

## 手测衍生 backlog（2026-07-05 · 补库后）

| 线 | 说明 | 留档 |
| --- | --- | --- |
| **BL-A3S-EXT-02?** | orphan overlay 配图 · qa_029–043 · ≥12 张 | [`a3s_ext01_image_gap_scan.md`](./a3s_ext01_image_gap_scan.md) |
| **BL-V1-04 A3S** | baseline `links[]` · **qa_003**（qa_011 → **COMPLIANCE-011** 单列） | [`a3s_18h1_handtest_issues.md`](./a3s_18h1_handtest_issues.md) |
| **EN 折叠参考 UI** | 均衡组 EN 规格 demo 不可见 · 非全库双栏 | [`bl_v1_07_thin_zh_display.md`](./bl_v1_07_thin_zh_display.md) §后续 |

---

## 手测首条复现

| 字段 | 值 |
| --- | --- |
| 问句 | `风会把门吹开` |
| docx | **§十六** 风会把门吹开（H1 下 **6 段 orphan · 0 个 H2**） |
| prod | **无组** |
| 误命中 | qa_023（§十二）· score **0.605** |

---

## docx 目录 · 三节状态一览

与 Word 导航窗格一致（18 节）：

| # | docx H1 | prod | 说明 |
| ---: | --- | ---: | --- |
| 一 | 电源问题 | ✅ 5 组 | qa_001–005 |
| 二 | 遥控器问题 | ✅ 5 组 | qa_006–010 |
| 三 | 完全不工作 | ✅ 4 组 | qa_011–014 |
| **四** | **只朝一个方向** | ❌ | 17 orphan 段 |
| **五** | **随意开关门** | ❌ | 10 orphan 段 |
| **六** | **缓停止有问题** | ❌ | 9 orphan 段 |
| **七** | **自动关门不生效** | ❌ | 9 orphan 段 |
| **八** | **开关门过程中走停或反弹** | ❌ | 19 orphan 段 |
| 九 | 关到位后反弹 | ✅ 2 组 | qa_015–016 |
| 十 | 不限位 | ✅ 5 组 | qa_017–021 |
| **十一** | **门机运行慢** | ❌ | 12 orphan 段 |
| 十二 | 电机电流小导致走停 | ⚠️ 7 组 | qa_022–028 · **+4 orphan** |
| **十三** | **电机转机臂不伸缩** | ❌ | 16 orphan 段 |
| **十四** | **机臂声音异常** | ❌ | 35 orphan 段 |
| **十五** | **离合打不开** | ❌ | 22 orphan 段 |
| **十六** | **风会把门吹开** | ❌ | 6 orphan 段 · **手测命中** |
| **十七** | **保养与润滑** | ❌ | 29 orphan 段 |
| **十八** | **其他产品知识讲解** | ❌ | 38 orphan 段 |

**❌ 未入库 12 节** = 手测时在 A3S 库问这些主题 → **必错或弱命中**，与检索质量无关。

---

## 根因

与 AD5S BL-EXT-01 同型：源 docx **H1 下无 H2** 的整节正文，`qa_doc_extractor` 在 `current_group is None` 时 **skip**，未进入 `qa_groups.json` / chroma。

A3S V1 只完成了 **有 H2 的 28 组** + eval 28/28；**未跑 A3S 侧 EXT 补库**。

---

## 与 eval 边界

- `eval_queries.json` 覆盖 **已入库 28 组** — **不包含**上表 12 节。
- 三库 demo 手测若用 A3S 库覆盖全 docx 目录 → 需以 **本文 + gap scan** 为对照表，失败项默认 **已知缺口**，非 regression。

---

## 建议执行（待拍板）

1. 复用 AD5S BL-EXT-01b 分类流程，对 **A3S docx** 12 节 orphan 分批 overlay  
2. re-embed `run-007` · 扩 `eval_queries.json`  
3. demo：低分警告（score &lt; 0.65）或 A3S chip 仅列已入库主题  

**扫描复跑**：`python _scratch/eval/a3s_gap_scan.py`

---

## 交叉链接

- 扫描明细：[`a3s_gap_scan.md`](./a3s_gap_scan.md)  
- AD5S 同型摸底（对照用）：[`bl_ext01_gap_inventory.md`](./bl_ext01_gap_inventory.md)  
- V1 结案：[`v1_docx_closure.md`](./v1_docx_closure.md)

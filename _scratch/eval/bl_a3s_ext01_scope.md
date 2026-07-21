# BL-A3S-EXT-01 · A3S orphan 补库（执行范围）

**状态**：**✅ B1–B7 已全部落地**（43 组 · missing H1 = 0）  
**手测基准**：[`samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx`](../../samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx)（**18 H1**）  
**缺口摸底**：[`a3s_gap_scan.md`](./a3s_gap_scan.md) · **12 H1 未入库 + §十二 partial**  
**prod 路径**：`_scratch/run-006/qa_groups.json` → re-embed → `_scratch/run-007/chroma_captioned` · images `_scratch/run-006/images`

**验收原则**：**BL-A3S-EXT-01 全部批次落地 + eval 扩分母 + 重启 :8765 之后**，再按 **docx 全 18 节目录** 做理解 A 手测。此前 A3S 手测仅覆盖已入库 6 域（28 组）。

---

## 与 AD5S BL-EXT-01b 关系

| | AD5S | A3S |
| --- | --- | --- |
| 线 | **✅ 已完成** · 43 组 | **本线** · 28→目标 ~40+ 组 |
| 方法 | orphan overlay → chunk_builder → embed → eval | **同型** · 节名/正文以 **A3S docx** 为准 |
| 参照 | 仅作 F/L/DT 分类参考 | **禁止** copy AD5S manifest 到 A3S |

---

## 当前 prod vs docx

| 状态 | H1 数 | 节 |
| --- | ---: | --- |
| ✅ 已入库 | 6 | 一 · 二 · 三完全不工作 · 九 · 十不限位 · 十二（7 组） |
| ⚠️ partial | 1 | §十二 +4 orphan 段 → **B7** |
| ❌ 未入库 | 12 | 四 · 五 · 六 · 七 · 八 · 十一运行慢 · 十三–十八（见 gap scan） |

**新 group_id**：自 **qa_029** 起（当前止于 qa_028）。

---

## 批次计划（定稿）

| 批 | A3S docx 节（匹配 key） | 新 group_id | Tag（预期） | eval 探针（补后） |
| --- | --- | --- | --- | --- |
| **B1** | 五随意开关门 · 六缓停 · 七自动关 · 风会把门吹开 | qa_029–032 | F | 风/随意开关门/自动关 |
| **B2** | 四只朝一方向 · 门机运行慢 | qa_033–034 | F | 口语 stress |
| **B3** | 八走停或反弹 | qa_035 | F（核实） | 中途走停 |
| **B4** | 十三转臂不伸缩 · 十五离合 | qa_036–038 | L-scenario | 2–3 组 |
| **B5** | 十四机臂异响 | qa_039 | DT→F prose | 异响 decision |
| **B6** | 十七保养 · 十八产品知识 | qa_040–042 | F + links | WD40/规格 |
| **B7** | §十二 partial（4 orphan） | qa_043? | P | 勿回归 qa_022–028 |

> 编号 qa_036–043 为规划占位；实施时以 merge 脚本 `NEW_GROUP_IDS` 为准。

---

## 每批 gate（与 AD5S 同）

1. **backup** `qa_groups` + `chroma_captioned.bak-{STAMP}`  
2. overlay merge → `chunk_builder` → `chunks_captioned` 合并  
3. `embed_ingest_local.py` → run-007  
4. **eval**：原 28 组 **无回归** + 本批新 query Top1  
5. **demo**：重启 `:8765` · 浏览器 spot-check  
6. 留档 `bl_a3s_ext01_batchN_execution_record.md`

---

## 脚本（待/run）

| 用途 | 路径 |
| --- | --- |
| gap scan | [`a3s_gap_scan.py`](./a3s_gap_scan.py) |
| 分类摸底 | [`a3s_ext01_classify_scan.py`](./a3s_ext01_classify_scan.py) |
| B7 overlay | [`phase_a3s_ext01_batch7_overlay.py`](./phase_a3s_ext01_batch7_overlay.py) |
| B3–7 留档 | [`bl_a3s_ext01_batch3_7_execution_record.md`](./bl_a3s_ext01_batch3_7_execution_record.md) |

**B1 执行**（甲方/负责人拍板后）：

```powershell
python _scratch/eval/phase_a3s_ext01_batch1_overlay.py all
# 重启 A3S qa_server :8765
```

---

## 全目录手测（补库后 · 进行中）

- 留档：[`a3s_18h1_handtest_log.md`](./a3s_18h1_handtest_log.md)  
- 覆盖 docx **18/18 H1** · 每节 ≥1 口语探针  
- eval 已扩至 **45** 条 · gap scan **missing H1 = 0**

---

## 交叉链接

- 缺口 backlog：[`a3s_content_gaps_backlog.md`](./a3s_content_gaps_backlog.md)  
- **18 H1 手测**：[`a3s_18h1_handtest_log.md`](./a3s_18h1_handtest_log.md)
- AD5S 参照：[`bl_ext01b_batch7_execution_record.md`](./bl_ext01b_batch7_execution_record.md)  
- 方法论：[`v1_lessons_for_v2.md`](./v1_lessons_for_v2.md) §1.3 baseline

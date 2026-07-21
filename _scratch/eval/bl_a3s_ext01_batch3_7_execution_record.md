# BL-A3S-EXT-01 · Batch3–7 执行留档

**日期**：2026-07-05  
**范围**：B3→B7 全部落地 · **34 → 43 组** · docx **18/18 H1 有组**

| 批 | 脚本 | 新 group_id | 合并后组数 | eval |
| --- | --- | --- | ---: | --- |
| B3 | [`phase_a3s_ext01_batch3_overlay.py`](./phase_a3s_ext01_batch3_overlay.py) | qa_035 | 35 | 30/30 |
| B4 | [`phase_a3s_ext01_batch4_overlay.py`](./phase_a3s_ext01_batch4_overlay.py) | qa_036–038 | 38 | 30/30 |
| B5 | [`phase_a3s_ext01_batch5_overlay.py`](./phase_a3s_ext01_batch5_overlay.py) | qa_039 | 39 | 30/30 |
| B6 | [`phase_a3s_ext01_batch6_overlay.py`](./phase_a3s_ext01_batch6_overlay.py) | qa_040–042 | 42 | 30/30 |
| B7 | [`phase_a3s_ext01_batch7_overlay.py`](./phase_a3s_ext01_batch7_overlay.py) | qa_043 | **43** | 30/30 |

**备份**：`chroma_captioned.bak-20260705-bl-a3s-ext01-b{3..7}` · `run-006/*.bak-*`

## 各批范围

### B3 · §八走停或反弹
- **qa_035** · 19 paras · zh=237

### B4 · §十三转臂 + §十五离合
- **qa_036** · 伸太过缩不回去 · 10 paras（同 AD5S §十五切分）
- **qa_037** · 电机转但机臂不伸缩 · 6 paras
- **qa_038** · 离合打不开 · 22 paras（合并 1 组）

### B5 · §十四机臂异响
- **qa_039** · 35 paras · `dt_prose_only` warning

### B6 · §十七保养 + §十八产品知识
- **qa_040** · 日常保养润滑 · paras 0–11
- **qa_041** · 深度润滑与保养参考 · paras 12–28
- **qa_042** · 其他产品知识 · 38 paras

### B7 · §十二 partial（P）
- **qa_043** · 4 orphan 段 · 插入 qa_028 之后
- question 收窄 + `answer_zh` 首行互斥标签（勿与 qa_022–028 混检）

## Chroma

- **可检索向量**：manifest **~52**（43 组 · 含长组子块）
- **retrievable root groups**（gap scan）：**35**

## 检索 spot-check（embed 后 · 未重启 :8765）

| query | expect | top1 | score | 备注 |
| --- | --- | --- | ---: | --- |
| 开关门过程中走停反弹 | qa_035 | **qa_035** | 0.771 | ✅ |
| 门开关到一半就停 | qa_035 | qa_019 | 0.696 | ⚠️ 口语易撞 §十限位 |
| 电机转但机臂不动 | qa_037 | **qa_037** | 0.749 | ✅ |
| 离合钥匙拧不开 | qa_038 | **qa_038** | 0.796 | ✅ |
| 机臂开关门有异响 | qa_039 | **qa_039** | 0.774 | ✅ |
| 日常保养喷WD40润滑 | qa_040 | **qa_040** | 0.649 | ✅ |
| AB值是什么意思 | qa_042 | **qa_042** | 0.427 | ✅ |
| 并电阻解决电流小走停 | qa_043 | **qa_043** | 0.693 | ✅ |
| 风会把门吹开（回归） | qa_032 | **qa_032** | 0.744 | ✅ |

## 缺口

[`a3s_gap_scan.md`](./a3s_gap_scan.md) 复跑：**missing H1 = 0** · §十二仍标记 partial（docx orphan 计数与 overlay 组并存属预期）

## 后续

1. **重启 A3S `:8765`** 后浏览器手测（否则 content_zh 可能空）
2. 扩 [`eval_queries.json`](../../eval_queries.json) 至 ~45 条（含 B1–B7 新组）
3. docx **18 H1 全目录理解 A 手测**

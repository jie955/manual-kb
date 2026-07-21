# BL-A3S-EXT-01 · Batch2 执行留档

**日期**：2026-07-05  
**脚本**：[`phase_a3s_ext01_batch2_overlay.py`](./phase_a3s_ext01_batch2_overlay.py)  
**备份**：`chroma_captioned.bak-20260705-bl-a3s-ext01-b2`

## 范围

| group_id | docx 节 | paras | zh 字 |
| --- | --- | ---: | ---: |
| qa_033 | 四、只朝一个方向 | 17 | 442 |
| qa_034 | 门机运行慢 | 12 | 216 |

**合并后**：32 → **34** 组 · chroma **43** vectors

## Eval 回归

`eval_queries.json` · **30/30 Top1 · 30/30 Top3**

## B2 探针（`:8765` post restart）

| query | expect | top1 | score | content_zh |
| --- | --- | --- | ---: | ---: |
| 机臂只朝一个方向转 | qa_033 | **qa_033** | 0.688 | 442 |
| 门开关特别慢 | qa_034 | **qa_034** | 0.745 | 216 |
| 风会把门吹开（回归） | qa_032 | **qa_032** | 0.744 | 119 |

## 缺口

未入库 H1：**8 → 6**（§四 · §十一 已补）

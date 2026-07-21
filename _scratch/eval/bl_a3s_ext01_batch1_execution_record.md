# BL-A3S-EXT-01 · Batch1 执行留档

**日期**：2026-07-05  
**脚本**：[`phase_a3s_ext01_batch1_overlay.py`](./phase_a3s_ext01_batch1_overlay.py)  
**备份**：`run-007/chroma_captioned.bak-20260705-bl-a3s-ext01-b1` · `run-006/qa_groups.json.bak-*`

## 范围

| group_id | docx 节 | paras | question |
| --- | --- | ---: | --- |
| qa_029 | 五、随意开关门 | 10 | 随意开关门 Random Opening/Closing |
| qa_030 | 六、缓停止有问题 | 9 | 缓停止有问题 Soft Stop Issues |
| qa_031 | 七、自动关门不生效 | 9 | 自动关门不生效 Auto Close Function Doesn't Work |
| qa_032 | 风会把门吹开 | 6 | 风会把门吹开 There is Little Play When the Gate is Closed |

**合并后**：28 → **32** 组 · chroma **39** retrievable vectors

## Eval 回归

`eval_queries.json` v2 · **30/30 Top1 · 30/30 Top3**（原 28 组无回归）

## B1 探针（`:8765` · post embed）

| query | expect | top1 | score |
| --- | --- | --- | ---: |
| 风会把门吹开 | qa_032 | **qa_032** | 0.744 |
| 风大能把门吹开一点怎么办 | qa_032 | **qa_032** | 0.772 |
| 门自己乱开乱关 | qa_029 | **qa_029** | 0.750 |
| 自动关门功能没用 | qa_031 | **qa_031** | 0.787 |

**手测复测项「风会把门吹开」：✅ 通过**（此前误命中 qa_023 @ 0.605）

## 缺口变化

B1 后 docx **18 H1** 中 **未入库由 12 → 8**（五/六/七/风 已 overlay 入库）。见 [`a3s_gap_scan.md`](./a3s_gap_scan.md) 复跑（missing=8）。

## 后续

- **B2–B7** 见 [`bl_a3s_ext01_scope.md`](./bl_a3s_ext01_scope.md)  
- 全 18 节目录手测 **待 EXT-01 全部完成**  
- demo 重启 `:8765` 后 UI 复测（若仍见 qa_023 → 旧进程）

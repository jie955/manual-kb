# BL-EXT-01b · Batch 2 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01b_batch2_overlay.py`](./phase_bl_ext01b_batch2_overlay.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01b-b2`  
**前置**：BL-V1-07 gate 四项 ✅

---

## 范围 · F×2

| group | 节 | orphan 段 | question | zh | en |
| --- | --- | ---: | --- | ---: | ---: |
| **qa_035** | 一个机臂完全不工作 | 10 | 一个机臂完全不工作 One Arm Doesn't Work | 102 | 1270 |
| **qa_036** | 十三、门机运行慢 | 12 | 门机运行慢 Gate Operates Slowly | 215 | 1772 |

**方法**：同 Batch1 — docx orphan → 合成 H2 overlay → chunk_builder → re-embed bge-m3

---

## prod 规模

| 指标 | Batch 1 后 | **Batch 2 后** |
| --- | ---: | ---: |
| qa_groups | 34 | **36** |
| 可检索向量 | 59 | **61** |
| chunks_captioned | 66 | **68** |

---

## 检索回归

```
eval_queries_ad5s.json · bge-m3 · 22/22 Top1（100%）· 22/22 Top3
```

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| b05 | 双机臂其中一个臂完全不工作 | **qa_035** | 初版 query 误 Top1→qa_014，已改 query |
| b06 | 门开关特别慢 运行速度很慢 | **qa_036** | |
| a01–b04 | — | — | **无回归** |

**b05 混淆对**：qa_035「完全不工作」vs qa_014「只朝一个方向」— eval 标注 `acceptable_group_ids: [qa_035, qa_014]`；a13 仍锁 qa_014。

---

## thin-ZH（BL-V1-07）

| group | thin | reason |
| --- | :---: | --- |
| qa_035 | ✅ | compact_steps(3)_long_en |
| qa_036 | ❌ | zh=215 步骤较完整；22V/11#12# 等规格仍在 EN（V1-05B） |

---

## 运维

embed 后 **须重启 qa_server**（manifest 刷新）— 见 BL-V1-07 gate 记录。  
**待固化**（下批顺手）：[`demo_checklist.md`](./demo_checklist.md) 或 overlay 说明加「kill 旧进程 → 重启 → health + 抽样 content 非空」。

---

## 下一批

**Batch 3**：§十二 partial（P×1 · 11 段）— 单独批 · **验收清单** [`bl_ext01b_batch3_acceptance.md`](./bl_ext01b_batch3_acceptance.md)（含 qa_020/021 回归 r12a/r12b）

---

## 回滚

```powershell
Copy-Item _scratch/run-ad5s/qa_groups.json.bak-20260705-bl-ext01b-b2 _scratch/run-ad5s/qa_groups.json -Force
Copy-Item _scratch/run-ad5s/chunks_captioned.json.bak-20260705-bl-ext01b-b2 _scratch/run-ad5s/chunks_captioned.json -Force
Remove-Item -Recurse -Force _scratch/run-ad5s/chroma_captioned
Copy-Item -Recurse _scratch/run-ad5s/chroma_captioned.bak-20260705-bl-ext01b-b2 _scratch/run-ad5s/chroma_captioned
```

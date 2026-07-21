# BL-EXT-01b · Batch 5 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01b_batch5_overlay.py`](./phase_bl_ext01b_batch5_overlay.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01b-b5`  
**分类**：§九 **F**（原 L 已核实降级 · [`bl_ext01b_sec09_sec16_verification.md`](./bl_ext01b_sec09_sec16_verification.md)）

---

## 范围 · F×1（21 段 orphan → qa_040）

| group | question | paras | zh | en |
| --- | --- | ---: | ---: | ---: |
| **qa_040** | 开关门过程中走停或反弹 Gate Stops or Bounces During Operation | 21 | 279 | 3206 |

**结构**：主干 1–6（红外 → FORCE/SOFT STOP → 单臂隔离 → 离合手推 → 脱门测臂 → 视频）+ 附录 follow-up（测电压/180° · 不带门伸出反弹 → 离合测电机/24V 直连）。整节 **1 H2** 收整。

---

## prod 规模

| 指标 | Batch 4 后 | **Batch 5 后** |
| --- | ---: | ---: |
| qa_groups | 39 | **40** |
| 可检索向量 | 64 | **65** |
| chunks_captioned | 71 | **72** |

---

## 检索回归

```
eval_queries_ad5s.json · bge-m3 · 28/28 Top1（100%）· 28/28 Top3
```

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| **b10** | 门开关到一半就停住或弹回来 | **qa_040** | acceptable 含 qa_022（§十四电流走停） |
| a01–b09 · r12a/r12b | — | — | **无回归** |

**交叉观察**（非 gate 失败）：a14 Top3 含 qa_040；b08 Top3 含 qa_040 — 同域「走停」语义邻近，Top1 仍正确。

---

## thin-ZH（BL-V1-07 · spot-check）

| group | thin | reason |
| --- | :---: | --- |
| qa_040 | ✅ | zh=279 步骤骨架在 · FORCE/22V 等规格主要在 EN（Z 列 B） |

---

## 结论

**Batch 5 收尾 ✅** — §九 F 类 overlay · eval 28/28 · 无回归。

**下一批**：**Batch 6 · §十七** 离合打不开（L-scenario · 22 段 · 2 H2）。**Batch 7 · §十六 DT** 须设计闭环后再 extract。

---

## 回滚

```powershell
Copy-Item _scratch/run-ad5s/qa_groups.json.bak-20260705-bl-ext01b-b5 _scratch/run-ad5s/qa_groups.json -Force
Copy-Item _scratch/run-ad5s/chunks_captioned.json.bak-20260705-bl-ext01b-b5 _scratch/run-ad5s/chunks_captioned.json -Force
Remove-Item -Recurse -Force _scratch/run-ad5s/chroma_captioned
Copy-Item -Recurse _scratch/run-ad5s/chroma_captioned.bak-20260705-bl-ext01b-b5 _scratch/run-ad5s/chroma_captioned
```

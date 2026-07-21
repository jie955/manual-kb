# BL-EXT-01b · Batch 4 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01b_batch4_overlay.py`](./phase_bl_ext01b_batch4_overlay.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01b-b4`  
**前置**：Batch 3 ✅ · BL-V1-08 backlog 已扩写（qa_020/021/037 三方 + legacy「不限位」）

---

## 范围 · L×1（§十五 · 16 段 orphan → 2 H2）

| group | question | paras | zh | en | links |
| --- | --- | ---: | ---: | ---: | ---: |
| **qa_038** | 伸太过缩不回去 Arm Extended Too Far Won't Retract | 10 | 177 | 1056 | 2 |
| **qa_039** | 电机转但机臂不伸缩 Motor Runs But Arm Won't Move | 6 | 210 | 924 | 0 |

**拆分**：classification **L-scenario** —「伸太过」vs「电机转不伸缩」各一 H2；qa_038 含 toopens×2 外链。

---

## prod 规模

| 指标 | Batch 3 后 | **Batch 4 后** |
| --- | ---: | ---: |
| qa_groups | 37 | **39** |
| 可检索向量 | 62 | **64** |
| chunks_captioned | 68 | **71** |

---

## 检索回归

```
eval_queries_ad5s.json · bge-m3 · 27/27 Top1（100%）· 27/27 Top3
```

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| **b08** | 机臂伸太过缩不回去 离合打开了 | **qa_038** | Top3 含 qa_039（同节） |
| **b09** | 电机转但拉杆不动 机臂不伸缩 | **qa_039** | Top3 含 qa_014；acceptable qa_035 |
| a01–b07 · r12a/r12b | — | — | **无回归** |

---

## thin-ZH（BL-V1-07 · spot-check）

| group | thin | reason |
| --- | :---: | --- |
| qa_038 | ✅ | zh=177 · EN 步骤更细（Z 列 B） |
| qa_039 | ✅ | zh=210 · 离合/丝杆排查 EN 更长 |

---

## 结论

**Batch 4 收尾 ✅** — §十五 L-scenario 2 H2 入库 · eval 27/27 · 无 P 类交叉漂移（与同节 qa_038/039 互 Top3 可接受）。

**下一批**：**Batch 5 · §九** 走停或反弹（**F** · 21 段）— 原 L 已核实降为 F · 流程同 Batch1/2。Batch 6=§十七 L；**Batch 7=§十六 DT**（须 schema/展示设计闭环 · **非** F/L overlay 可直接开工）— 见 [`bl_ext01b_classification.md`](./bl_ext01b_classification.md) §建议批次

---

## 回滚

```powershell
Copy-Item _scratch/run-ad5s/qa_groups.json.bak-20260705-bl-ext01b-b4 _scratch/run-ad5s/qa_groups.json -Force
Copy-Item _scratch/run-ad5s/chunks_captioned.json.bak-20260705-bl-ext01b-b4 _scratch/run-ad5s/chunks_captioned.json -Force
Remove-Item -Recurse -Force _scratch/run-ad5s/chroma_captioned
Copy-Item -Recurse _scratch/run-ad5s/chroma_captioned.bak-20260705-bl-ext01b-b4 _scratch/run-ad5s/chroma_captioned
```

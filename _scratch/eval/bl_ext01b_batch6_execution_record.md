# BL-EXT-01b · Batch 6 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01b_batch6_overlay.py`](./phase_bl_ext01b_batch6_overlay.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01b-b6`  
**分类**：§十七 **L-scenario** · 2 H2（非 DT · §十六 Batch7 设计闭环后再动）

---

## 范围 · L×1（22 段 orphan → 2 H2）

| group | question | paras | zh | en | links |
| --- | --- | ---: | ---: | ---: | ---: |
| **qa_041** | 离合打不开·关门太紧 Clutch Won't Release · Gate Closed Too Tight | 2 | 94 | 362 | 0 |
| **qa_042** | 离合打不开·伸太过或内部卡住 Clutch Won't Release · Over-Extended or Internal Jam | 20 | 197 | 2235 | 6 |

**拆分依据**（ZH 编号 1 vs 2–3）：

| 场景 | 内容 |
| --- | --- |
| **qa_041** | 脱门测离合 · 关门到位太紧难拧 → 调开关门位置 |
| **qa_042** | 脱门仍打不开 → 伸太过（限位 B / 视频×3）→ 非伸太过则拆壳查离合件/丝母/润滑 |

qa_042 含 YouTube×4（简单档 links[] · BL-V1-04 随节入库）。

---

## prod 规模

| 指标 | Batch 5 后 | **Batch 6 后** |
| --- | ---: | ---: |
| qa_groups | 40 | **42** |
| 可检索向量 | 65 | **67** |
| chunks_captioned | 72 | **74** |

---

## 检索回归

```
eval_queries_ad5s.json · bge-m3 · 30/30 Top1（100%）· 30/30 Top3
```

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| **b11** | 离合钥匙拧不开 门关到位很紧 | **qa_041** | |
| **b12** | 脱门也打不开离合 伸太过推不进去 | **qa_042** | acceptable 含 qa_038 |
| a01–b10 · r12a/r12b | — | — | **无回归** |

**交叉观察**（非 gate 失败）：b08 Top3 含 qa_042、qa_041 — §十五伸太过 vs §十七离合域邻近；Top1 仍 qa_038。

---

## thin-ZH（BL-V1-07 · spot-check）

| group | thin | reason |
| --- | :---: | --- |
| qa_041 | ✅ | zh=94 · 步骤 1 骨架在 |
| qa_042 | ✅ | zh=197 · 拆机/润滑细节主要在 EN（Z 列 B） |

---

## 结论

**Batch 6 收尾 ✅** — §十七 L-scenario 2 H2 入库 · eval 30/30 · 无回归。

**BL-EXT-01b orphan 节**：11 节中 **10 节已 overlay**（剩 **§十六 DT · Batch7** — **须单独设计讨论**，不套用 F/L overlay）。

---

## 回滚

```powershell
Copy-Item _scratch/run-ad5s/qa_groups.json.bak-20260705-bl-ext01b-b6 _scratch/run-ad5s/qa_groups.json -Force
Copy-Item _scratch/run-ad5s/chunks_captioned.json.bak-20260705-bl-ext01b-b6 _scratch/run-ad5s/chunks_captioned.json -Force
Remove-Item -Recurse -Force _scratch/run-ad5s/chroma_captioned
Copy-Item -Recurse _scratch/run-ad5s/chroma_captioned.bak-20260705-bl-ext01b-b6 _scratch/run-ad5s/chroma_captioned
```

# BL-EXT-01b · Batch 7 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01b_batch7_overlay.py`](./phase_bl_ext01b_batch7_overlay.py)  
**验收清单**：[`bl_ext01b_batch7_acceptance.md`](./bl_ext01b_batch7_acceptance.md)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01b-b7`  
**设计**：DT → **F+prose** · 拒绝 schema A · C/`decision_hints` 留 ingest 后可选

---

## 范围 · DT→F×1（35 段 orphan → qa_043）

| group | question | paras | zh | en | links |
| --- | --- | ---: | ---: | ---: | ---: |
| **qa_043** | 机臂声音异常 Abnormal Noise From Arm | 35 | 332 | 1946 | 1 |

**结构**：观察后跳转 prose 保留（1→2/5 等）· **无** `troubleshooting_ladder`  
**`structure_warnings`**：`dt_prose_only` — 观察后跳转(DT)·禁止 attach 线性 ladder

---

## prod 规模 · **BL-EXT-01b orphan 11/11 节全部入库**

| 指标 | Batch 6 后 | **Batch 7 后** |
| --- | ---: | ---: |
| qa_groups | 42 | **43** |
| 可检索向量 | 67 | **70** |
| chunks_captioned | 74 | **78** |

---

## 检索回归

```
eval_queries_ad5s.json · bge-m3 · 32/32 Top1（100%）· 32/32 Top3
```

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| **b13** | 按遥控机臂有异响 离合打开还有声音 | **qa_043** | C1/C2 探针 |
| **b14** | 机臂声音异常 推拉杆不顺 润滑丝杆挡圈 | **qa_043** | 初版「…卡顿润滑…」→ qa_029 · 已加「声音异常」区分 · acceptable qa_029 |
| a01–b12 · r12a/r12b | — | — | **无回归** |

---

## DT spot-check（验收 §C · 两条独立）

**探针**：「按遥控机臂有异响 离合打开还有声音」

| # | 路径 | 结果 |
| ---: | --- | --- |
| **C1** | **无 LLM** (`use_llm: false` · demo 不勾选) | ✅ Top1=qa_043 · prose 含「有异响→…步骤5」· `structure_warnings` 可见 · **误读风险**：客户仍可能把全文当顺序必读 — **可接受、非零**（见验收清单备注） |
| **C2** | **有 LLM** (`use_llm: true`) | ✅ 未出现「依次完成步骤2–4」类表述 · 生成内容直达步骤5等价排查（拆外壳/离合凸轮/齿轮箱）· 未强制步骤2–4 |

---

## thin-ZH（BL-V1-07 · spot-check）

| group | thin | reason |
| --- | :---: | --- |
| qa_043 | ✅ | zh=332 决策箭头在 · 拆机/润滑细节主要在 EN（Z 列 B） |

---

## 结论

**Batch 7 收尾 ✅** · **BL-EXT-01b 11 节 orphan overlay 全部完成**  
**仍待办（非 Batch7 阻塞）**：`decision_hints[]` 手填（可选）· BL-V1-03 未覆盖 prod 组 eval · BL-V1-08 §十二 legacy

---

## 回滚

```powershell
Copy-Item _scratch/run-ad5s/qa_groups.json.bak-20260705-bl-ext01b-b7 _scratch/run-ad5s/qa_groups.json -Force
Copy-Item _scratch/run-ad5s/chunks_captioned.json.bak-20260705-bl-ext01b-b7 _scratch/run-ad5s/chunks_captioned.json -Force
Remove-Item -Recurse -Force _scratch/run-ad5s/chroma_captioned
Copy-Item -Recurse _scratch/run-ad5s/chroma_captioned.bak-20260705-bl-ext01b-b7 _scratch/run-ad5s/chroma_captioned
```

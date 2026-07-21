# Task 2 · 英文检索修库优先级（baseline 驱动）

**状态**：**Post G11** · ZH-index Gate **14/14** · EN-index Gate **13/14** · 2026-07-08  
**输入**：[`cs_en_retrieval_baseline.json`](./cs_en_retrieval_baseline.json)（ZH-index）· [`cs_en_retrieval_baseline_en.json`](./cs_en_retrieval_baseline_en.json)（EN-index）  
**Task 2 通过线（ADR-0002 legacy · ZH-index）**：Gate Tier A Top1 **≥ 45%** → **已达成**（**100%** · 14/14）  
**ADR-0003 主口径（EN-index）**：Gate **13/14** · E2E `cs_0013`/`cs_0026` ✅ · 薄边 **`csq_078`**（verbatim → `qa_030` · scenario E2E → `qa_022`）

---

## 1. Baseline 快照

### ZH-index（legacy · overlay 在 `chroma_captioned`）

| 切片 | Task 1 | Post G7c | Post G8c | **Post G10 + BL-RET-01a** |
| --- | ---: | ---: | ---: | ---: |
| 全部可评分（109） | 31.2% | 74.3% | **78.0%** | **68.8%** |
| **Gate Tier A**（14） | 35.7% | 100% | **100%** | **100%** |
| logic（45） | 20.0% | 80.0% | **86.7%** | **66.7%** |
| direct（64） | — | — | **71.9%** | **70.3%** |
| 路由 acc（109 labeled） | 65.2% | 89.6% | **89.6%** | **89.0%** |
| Top3（109） | 51.4% | 84.4% | **86.2%** | **83.5%** |

> Post G10 后 all 从 78% 回落至 68.8%：BL-RET-01a 重 embed 重置部分非 Gate overlay；**Gate 14/14 保持**（G9/G10 已 re-apply 至 a3s 生产库）。

### EN-index（ADR-0003 主口径 · 首跑 2026-07-08）

| 切片 | EN-index |
| --- | ---: |
| 全部可评分（109） | **54.1%** |
| **Gate Tier A**（14） | **85.7%（12/14）** |
| logic（45） | **51.1%** |
| direct（64） | **56.3%** |
| 路由 acc（109 labeled） | **89.0%** |
| Top3（109） | **58.7%** |

**EN Gate miss（2）**：`csq_071`（#12 · `qa_019` vs `qa_020`/`qa_021`）· `csq_078`（#13 · `qa_030` vs `qa_022`）— G10 修复 **仅在 ZH-index**，EN 索引待迁移。

**E2E 9-case 检索（Post G10 restore）**：可评分 **7/7** · `cs_0026`→`qa_001` · `cs_0013`→`qa_022` · 见 [`cs_e2e_gate_results.json`](./cs_e2e_gate_results.json)

**中文回归（Post G10）**

| 库 | 现况 | 备注 |
| --- | ---: | --- |
| A3S | **43/47** | `q23` ✅ · `q23b` ❌（`qa_018` 拉/推 1 字混淆） |
| AD5S | **43/48** | `b10/a16` 仍 miss（未在本波触及） |

---

## 2. 已执行波次（R0 → G8c）

| 波次 | 脚本 / 产物 | 主攻 | 结果摘要 |
| --- | --- | --- | --- |
| **Task 1** | `run_cs_en_retrieval_baseline.py` | 基线 | Gate **35.7%** · all **31.2%** |
| **R0** | `library_router.py` | 路由 keyword | logic 路由 ~45% → ~72% |
| **G1** | `phase_cs_en_task2_overlay.py` | A3S #13 `qa_022` 走停 | merge 全 chunk 修复；`csq_078` ✅ |
| **G2+G3** | `phase_cs_en_task2_g2g3_overlay.py` | AD5S #15 auto-close · #16 PW802 | #15 簇 **6/6**；Gate +#15/#16 |
| **G4** | `phase_cs_en_task2_g4_overlay.py` + router | #18/#19/#21 | #18/#19/#21 Tier A ✅ |
| **G5** | `phase_cs_en_task2_g5_overlay.py` + router | #17 A5131 `qa_033` | Gate **14/14**（暂）；#17 **7/7** |
| **G6** | `phase_cs_en_task2_g6_overlay.py` + router | #12 限位 · #13 · #27 · #2 | logic **+8.8pp**；#27 **5/6**；Gate 暂 **13/14** |
| **G6b** | `phase_cs_en_task2_g6b_overlay.py` | #12 oracle + 开/关中文拆分 | `csq_071` ✅；A3S zh **45/47** |
| **G7** | `phase_cs_en_task2_g7_overlay.py` + router | AD5S #23 `qa_040` | `csq_148–150` **3/3** ✅ |
| **G7b** | `phase_cs_en_task2_g7b_overlay.py` + router | #1/#2/#27 衍生 | `csq_002/006/009/010/174/176` ✅ |
| **G7c** | `phase_cs_en_task2_g7c_overlay.py` | #15 `qa_036`/`qa_040` 拆分 | Gate **14/14**；#15 **6/6** |
| **G8** | `phase_cs_en_task2_g8_overlay.py` + router | q23/#12/#13 尾 | #12 `073/076/077` ✅；Gate 暂 **13/14**（`078` 回归） |
| **G8b** | `phase_cs_en_task2_g8b_overlay.py` | `csq_078` + q23b | Gate 恢复；`q23b` 部分修复 |
| **G8c** | `phase_cs_en_task2_g8c_overlay.py` | q23 + 开/关 FORCE 拆分 | Gate **14/14**；#12/#13 衍生 **6/6**；`q23` ✅ |
| **G9** | `phase_cs_en_task2_g9_overlay.py` | T4 `cs_0026` board-replaced cluster | `qa_001`/`qa_033` vs `qa_010` · Top1 **`qa_001`** |
| **G10** | `phase_cs_en_task2_g10_overlay.py` | T4 derived + #13 margin | `cs_0013`→`qa_022`（0.709 vs `qa_020` 0.619）· E2E **7/7** |
| **BL-RET-01a** | `bl_ret_01a_batch_reembed.py` | 三库 ts + 四 manual · `doc_type` | 7 target 重 embed · stamped JSON 备份 |
| **merge** | `merge_model_chroma.py` | ts + manual → `chroma_merged` | a3s **316** · ad5s **313** · tc148 **21** retrievable |

**Chroma 备份戳**：`bak-20260707-cs-en-task2-{g1,…,g8c}` · `20260708-cs-en-task2-g9/g10` · `20260708-bl-ret-01a` · `20260708-merge`

**运维**：2026-07-08 并行 embed 竞态 — `phase_cs_en_a_line_batch_overlay.py` **勿**与 G10 生产库同跑；恢复自 `.a3s-ts-stamped-20260708-bl-ret-01a.json`。

---

## 3. Gate Tier A · 14 可评分 case

| # | 邮件 | Verbatim query | Top1 | 波次 |
| ---: | --- | --- | --- | --- |
| 1 | AT12131S 无反应 | `csq_001` | `qa_011` ✅ | R0 |
| 8 | TC148 jumper | `csq_044` | `qa_002` ✅ | — |
| 9 | TC148 自循环 | `csq_050–052` | `qa_001/002` ✅ | — |
| 10 | TC148 无反应 | `csq_059` | `qa_002` ✅ | — |
| 12 | AT12131 限位 | `csq_071` | `qa_020` ✅ | G6b oracle |
| 13 | A3S 走停 | `csq_078` | `qa_022` ✅ | G1+G8c |
| 15 | AD8S auto-close | `csq_090` | `qa_040` ✅ | G7c |
| 16 | PW802 红灯 | `csq_096` | `qa_001` ✅ | G2+G3 |
| 17 | A5131 保修 | `csq_102` | `qa_033` ✅ | G5 |
| 18 | A5/A8 电池 | `csq_109` | `qa_001` ✅ | G4 |
| 19 | AD5S 开过头 | `csq_116` | `qa_016` ✅ | G4 |
| 21 | A8132 有电无机臂 | `csq_130` | `qa_001` ✅ | G4 |

**Gate Tier A：14/14 ✅**（G8c 后无 miss）

---

## 4. 场景簇 Top1（Post G8c）

| 场景 | 可评分 query | Top1 | 备注 |
| --- | ---: | ---: | --- |
| **#12 AT12131 限位** | 7 | **7/7** | `073/076/077` ✅（G8c） |
| **#13 A3S 走停** | 6 | **6/6** | `081/082` ✅；`078` Gate ✅ |
| **#15 AD8S auto-close** | 6 | **6/6** | G7c ✅ |
| #16 PW802 | 6 | **5/6** | |
| #17 A5131 | 7 | **7/7** | |
| #23 AD5S 循环关 | 5 | **5/5** | G7 ✅ |
| #27 遥控多次 | 6 | **6/6** | G7b ✅ |

---

## 5. 剩余 Miss 解剖（24 条 · Post G8c）

详见 [`cs_en_retrieval_baseline.md`](./cs_en_retrieval_baseline.md) Top1 misses 列表。

| 类型 | 约条数 | 主改层 |
| --- | ---: | --- |
| **库对、组错** | ~18 | chunk 症状前缀 / 自定义 embedding |
| **路由错库** | ~6 | `library_router.py`（`csq_101` ad5s · `csq_174/176` 等） |

**高优非 Gate**

| 条目 | 要点 | 下一波 |
| --- | --- | --- |
| A3S zh **`q23b`** | `qa_018` vs `qa_019`（推/拉 1 字） | dual-zone 或推/拉规则 rerank |
| `csq_005` | `qa_001` vs fuse/LED | #1 衍生 |
| AD5S zh `b10/a16` | 反弹 vs §九 | AD5S overlay |
| #26 邻居信 `165–170` | `qa_001` vs `qa_010/033` | 低优 |

---

## 6. 修复原则（不变）

**做**

- 只动 **embedding_text / 症状前缀 / 路由 / oracle**；改完 **重 embed** → `run_cs_en_retrieval_baseline.py`
- Gate Tier A + 场景全 query 验收；中文 eval **目标 ≥44/47 A3S、≥42/48 AD5S**
- 长组 overlay：**merge 该组全部 parent+child chunk**（G1 教训）
- **开/关 FORCE SOFT STOP**、**推/拉开门** 不得共用同一英文 symptom 串（G8 教训）

**不做**

- out 61 query 硬 ingest · 三库合并 · ET24+UPS01 万用表新 qa（库外）
- `ad5s qa_010` DIP #3↔#5 内容纠错（Grounding / Task 4）

---

## 7. 下一波优先级

### G11 · EN-index 迁移（ADR-0003 Gate K 主口径）

- 脚本：[`phase_cs_en_task2_g11_en_overlay.py`](./phase_cs_en_task2_g11_en_overlay.py) — G9/G10 + #12/#13 limit → `chroma_captioned_en`
- 目标：EN Gate **12/14 → 14/14**；客户路径切 EN-primary
- **80% 发链判据**：见 [`cs_22mail_eval_readme.md`](./cs_22mail_eval_readme.md)（真邮四维 · 非本 Gate K  alone）
- 验收：`python _scratch/eval/run_cs_en_retrieval_baseline.py --index en` · `run_cs_e2e_gate.py --generate --index en`

### G8d · A3S 中文 `q23b`（`qa_018` vs `qa_019`）

- 候选：`phase_a3s_qa017_dual_zone_overlay.py` 路线，或检索前 **推/拉** 方向规则
- 纯 symptom embedding 已触顶（`q23` ✅ 与 `q23b` 难共存于同一 bge-m3 空间）

### 余波 · 非 Gate（可选）

| 簇 | miss 要点 |
| --- | --- |
| `csq_005` | `qa_001` vs fuse/LED |
| AD5S zh `b10/a16` | 反弹 vs §九 |
| #26 邻居信 | `qa_010`/`qa_033` 混吸 |
| ZH-index all **68.8%** | 非 Gate overlay 在 BL-RET-01a 后部分丢失 — 按需从 stamped JSON 恢复或重跑 G4–G8 子集 |

---

## 8. 验收命令

```powershell
# G10（ZH-index · 殷主管 review 前主路径）
python _scratch/eval/phase_cs_en_task2_g10_overlay.py

# 英文 baseline · 双轨
python _scratch/eval/run_cs_en_retrieval_baseline.py
python _scratch/eval/run_cs_en_retrieval_baseline.py --index en

# 中文回归（overlay 已含 A3S；AD5S 单独）
python eval_run.py _scratch/run-ad5s/chroma_captioned --eval eval_queries_ad5s.json --model _scratch/modelscope/BAAI/bge-m3 --json-out _scratch/eval/cs_en_task2_ad5s_regression.json
```

| 里程碑 | ZH Gate | ZH All | EN Gate | EN All |
| --- | ---: | ---: | ---: | ---: |
| Task 1 | 35.7% | 31.2% | — | — |
| Post G5 | **100%** | 68.8% | — | — |
| Post G7c | **100%** | 74.3% | — | — |
| Post G8c | **100%** | **78.0%** | — | — |
| **Post G10 + BL-RET-01a** | **100%** | **68.8%** | — | — |
| **EN-index 首跑** | — | — | **85.7%** | **54.1%** |

---

## 9. 索引

| 文件 | 角色 |
| --- | --- |
| [`run_cs_en_retrieval_baseline.py`](./run_cs_en_retrieval_baseline.py) | 英文 baseline |
| [`cs_email_query_map.json`](./cs_email_query_map.json) | 176 query + oracle |
| [`phase_cs_en_task2_g8_overlay.py`](./phase_cs_en_task2_g8_overlay.py) | G8 q23/#12/#13 |
| [`phase_cs_en_task2_g8b_overlay.py`](./phase_cs_en_task2_g8b_overlay.py) | G8b `078`/q23b |
| [`phase_cs_en_task2_g8c_overlay.py`](./phase_cs_en_task2_g8c_overlay.py) | G8c 收敛波 |
| [`phase_cs_en_task2_g9_overlay.py`](./phase_cs_en_task2_g9_overlay.py) | G9 T4 `cs_0026` |
| [`phase_cs_en_task2_g10_overlay.py`](./phase_cs_en_task2_g10_overlay.py) | G10 T4+#13 |
| [`phase_1b_full_en_index.py`](./phase_1b_full_en_index.py) | Phase 1b EN 索引 |
| [`bl_ret_01a_batch_reembed.py`](./bl_ret_01a_batch_reembed.py) | BL-RET-01a 重 embed |
| [`merge_model_chroma.py`](./merge_model_chroma.py) | ts+manual merge |
| [`library_router.py`](../../library_router.py) | 三库路由 |
| [`cs_en_poc_execution.md`](./cs_en_poc_execution.md) | POC 总清单 |
| ADR-0003 | EN-index 主口径 · Gate K |

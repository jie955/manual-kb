# Batch 3 · §十二 baseline snapshot（overlay 前 · 2026-07-05）

**时机**：Batch 3 overlay **未执行** · chroma = Batch2 后（36 组 / 61 向量）  
**机器可读**：[`batch3_sec12_baseline_eval.json`](./batch3_sec12_baseline_eval.json)

---

## 覆盖盲区发现（非仅「补回归」）

`eval_queries_ad5s.json` 在 Batch3 前 **无 §十二 query** — **qa_020 / qa_021** 自 prod 入库起即 **无 eval 保护**（全库设计 `eval_queries.json` q24/q25 存在，但未迁入 AD5S 子集）。

与 **BL-V1-02**（A3S 28/28 设计）、**BL-V1-03**（AD5S 余组 backlog）同类：**Batch3 归属核查顺带闭合 §十二 2 组盲区**。

### AD5S eval 组覆盖（更新）

| 指标 | Batch2 后（+r12 前） | **+r12a/r12b 后** |
| --- | ---: | ---: |
| prod 组数 | 36 | 36 |
| eval 条数 | 22 | **24** |
| **unique 组覆盖** | **20/36 (56%)** | **22/36 (61%)** |
| Top1（bge-m3） | 22/22 | **23/24** |

**仍无 eval 的 14 组**：qa_007, qa_009, qa_015–019, qa_023, qa_025–030 → **BL-V1-03** 主 backlog。

---

## §十二 回归锚点 · Top1 baseline

| id | query | expected | **baseline Top1** | score | Top3 |
| --- | --- | --- | --- | ---: | --- |
| **r12a** | 拉开门 关门不限位 限位B怎么调 | qa_020 | **qa_020** ✅ | 0.7419 | qa_020, qa_018, qa_017 |
| **r12b** | 推开门 关不到位 不限位 | qa_021 | **qa_020** ⚠️ | 0.7122 | qa_020, **qa_021** (0.6918), qa_017 |

### r12b 说明（overlay 前已存在 · **≠ Batch3 漂移**）

- qa_020 / qa_021 **prod question 标题同为**「推开门安装」— 检索 **固有混淆**（**BL-V1-08** · Batch3 **不修** title）。
- r12b baseline Top1=qa_020，qa_021 Top2（Δ≈0.02）。
- Batch3 后若仍 Top1=qa_020 → **混淆未加重也未减轻**；≠ 验证通过，≠ Batch3 新问题。

**Batch3 后 r12 判定**（相对本 baseline）：

| 结果 | 含义 |
| --- | --- |
| r12b Top1 qa_020，Top2 qa_021，score ≈ baseline | overlay 未改变固有混淆（Batch3 可收口；V1-08 待办） |
| r12b Top1 → qa_021 | 改善 |
| r12a/r12b Top1 → **qa_037+** | **失败**（新 orphan 抢检索） |

---

## 全库 eval 摘要（同次 run）

```
24 queries · Top1 23/24 (95.8%) · Top3 24/24
唯一 miss：r12b（Top3 含 qa_021）
```

其余 a01–b06 与 Batch2 后一致 · **无变化**。

---

## Batch3 overlay 后对照（2026-07-05 · qa_037 fix）

| 项 | overlay 前 | overlay 初版 | **fix 后** |
| --- | --- | --- | --- |
| r12a Top1 | qa_020 · 0.7419 | qa_037 ❌ | **qa_020 · 0.7419** ✅ |
| r12b Top1 | qa_020 · 0.7122 | qa_037 ❌ | **qa_020 · 0.7615** ✅（query→限位B） |
| b07 Top1 | — | qa_037 ✅ | **qa_037 · 0.7509** ✅ |
| 全库 Top1 | 23/24 | 23/25 | **25/25** |

留档：[`bl_ext01b_batch3_execution_record.md`](./bl_ext01b_batch3_execution_record.md)

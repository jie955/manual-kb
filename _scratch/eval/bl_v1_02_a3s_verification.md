# BL-V1-02 · A3S eval 验证留档（2026-07-05）

**eval**：`eval_queries.json` v2 · **30 条** · **28/28 组**设计覆盖  
**chroma**：`_scratch/run-007/chroma_captioned` · **bge-m3** · no prefix / no hybrid / no rerank

---

## 汇总

| 指标 | 结果 |
| --- | ---: |
| Top1 | **24/30（80.0%）** |
| Top3 | **27/30（90.0%）** |
| 口语/改写类 miss | 见下表 §十二/限位域 |

机器可读：[`bl_v1_02_a3s_eval.json`](./bl_v1_02_a3s_eval.json)

---

## Top1 miss（6 条）

| id | query | expected | Top1 | Top3 | 备注 |
| --- | --- | --- | --- | ---: | --- |
| **q19** | 门关到位又弹回来 拉开门 | qa_015 | **qa_020** | ❌ | §十反弹 vs §十二限位 install 标题域重叠 |
| **q22** | 拉开门 开门位置不对 不限位 | qa_018 | **qa_017** | ❌ | 「不限位」→ qa_017 开门不限位 |
| **q23** | 推开门 开门停不下来 | qa_019 | **qa_020** | ❌ | 推/拉 + 开位 vs qa_020 拉开门安装 |
| **q24** | 拉开门 关门不限位 限位B怎么调 | qa_020 | **qa_017** | ✅ | 同 AD5S r12a/BL-V1-08 限位域 |
| **q25** | 推开门 关不到位 不限位 | qa_021 | **qa_017** | ✅ | 同 AD5S legacy「不限位」语义 |
| **q27** | 推开门开门不正常 二极管怎么接 | qa_024 | **qa_023** | ✅ | qa_023/024 同节 confusable_pair |

**18/18 旧基线**（run-007 PoC · 16 组子集）≠ 本次 v2 **30 条 / 28 组**全量验证。

---

## 结论

**BL-V1-02 验证已跑 ✅** — 设计覆盖 28/28 组 · Top1 **80%** · Top3 **90%**。

**非 gate 全绿**：§十/十一/十二限位域 6 条 miss 中 **4 条为已知语义邻近**（与 AD5S BL-V1-08 同类）；q19/q22/q23 为 query/组边界问题 — **已由 BL-V1-08 Phase 2 修复**（见 [`bl_v1_08_a3s_execution_record.md`](./bl_v1_08_a3s_execution_record.md)）。

---

## 复现（Phase 2 后）

```powershell
python eval_run.py _scratch/run-007/chroma_captioned `
  --eval eval_queries.json `
  --model _scratch/modelscope/BAAI/bge-m3 `
  --name bl-v1-02-a3s
```

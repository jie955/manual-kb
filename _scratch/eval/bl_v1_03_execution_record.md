# BL-V1-03 · 执行记录（2026-07-05）

**范围**：[`bl_v1_03_scope.md`](./bl_v1_03_scope.md) · Item 1+2+4 gate · Item 3 审计 spot-fix

---

## 交付

| 文件 | 变更 |
| --- | --- |
| `eval_queries_ad5s.json` | v3 · +c01–c13 · +a16 · 47 条 |
| `eval_queries.json` | v2.1 · q27 `acceptable_group_ids` |
| `coverage_table.md` | AD5S 分母重算 |
| `bl_v1_03_ad5s_eval.json` | AD5S 全量 eval |
| `bl_v1_03_a3s_eval.json` | A3S 复跑（q27 acceptable） |

---

## Item 1 · AD5S 13 组补齐

| id | group | Top1 | Top3 | 备注 |
| --- | --- | :---: | :---: | --- |
| c01 | qa_007 | ✅ | ✅ | |
| c02 | qa_009 | ✅ | ✅ | |
| c03 | qa_015 | ✅ | ✅ | |
| c04 | qa_016 | ❌ | ✅ | Top1 qa_037 · §十 bounce vs §十二开位 |
| c05 | qa_017 | ❌ | ✅ | Top1 qa_019 · install 标题域 |
| c06 | qa_018 | ❌ | ❌ | Top1 qa_021 · 限位域抢 · **待 AD5S §十/十一 症状化** |
| c07 | qa_019 | ❌ | ❌ | Top1 qa_020 · 同上 |
| c08 | qa_023 | ✅ | ✅ | acceptable qa_022 |
| c09 | qa_025 | ✅ | ✅ | |
| c10 | qa_026 | ✅ | ✅ | |
| c11 | qa_027 | ✅ | ✅ | |
| c12 | qa_028 | ❌ | ✅ | Top1 qa_030 · thin-ZH 节内混淆 · acceptable qa_029 |
| c13 | qa_030 | ✅ | ✅ | |

**a16** qa_022 第 3 条口语：Top1 qa_024 · Top3 ✅ · acceptable qa_040

---

## Item 2 · A3S q27

`acceptable_group_ids: [qa_024, qa_023]` → **30/30 Top1 · 30/30 Top3** ✅

---

## Item 3 · 口语变体审计

| 组 | query 数 | 口语 | 结论 |
| --- | ---: | --- | --- |
| qa_022 | 3（a14/a14b/a16） | 2 colloquial + 1 formula | ✅ ≥3 压测 |
| qa_031–034 | 各 1 | b01–b04 colloquial | ✅ |
| qa_035–036 | 各 1 | b05–b06 colloquial | ✅ |
| qa_037–043 | 1–2 | b07–b14 colloquial | ✅ · qa_043 有 b13+b14 |

**无 RED** — 本轮未对 EXT-01b 组追加 query。

---

## Item 4 · 覆盖率（43 组）

| 指标 | Batch7 后 | **BL-V1-03 后** |
| --- | ---: | ---: |
| eval 条数 | 32 | **47** |
| **主期望组覆盖** | 27/43（62.8%） | **41/43（95.3%）** |
| **含 acceptable 触及** | 30/43（69.8%） | **43/43（100%）** |
| 无 primary 组 | 16 | **qa_024 · qa_029**（仅 acceptable） |
| Top1（全库 47 条） | 32/32 | **41/47（87.2%）** |
| Top3 | — | **45/47（95.7%）** |

---

## 结论

**BL-V1-03 design gate ✅** — 13 组 query 设计完成 · 分母更新 · q27 acceptable · EXT-01b 审计绿。

**Top1 非全绿（诚实）** — 6/47 miss 集中在：

1. **§十/十一 bounce**（c04–c07）— 与 BL-V1-08 同构 · AD5S qa_016–019 仍用 install 标题 · **建议 BL-V1-08 子项或 V1.1 症状化**
2. **§十四/§十九 confusable**（a16/c12）— Top3 已过 · acceptable 已标注

**不阻塞** 进入 **BL-V1-04**（qa_024/qa_030 外链 · qa_023 branch）。

---

## 复现

```powershell
python eval_run.py _scratch/run-ad5s/chroma_captioned `
  --eval eval_queries_ad5s.json `
  --model _scratch/modelscope/BAAI/bge-m3 `
  --json-out _scratch/eval/bl_v1_03_ad5s_eval.json

python eval_run.py _scratch/run-007/chroma_captioned `
  --eval eval_queries.json `
  --model _scratch/modelscope/BAAI/bge-m3 `
  --json-out _scratch/eval/bl_v1_03_a3s_eval.json
```

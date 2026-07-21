# Phase 0.3 · E2E Gate Probe（2026-07-08）

**Script**：[`run_cs_e2e_gate.py`](./run_cs_e2e_gate.py) · **全文留档**：[`phase0_gate_probe.md`](./phase0_gate_probe.md) · **JSON**：[`cs_e2e_gate_results.json`](./cs_e2e_gate_results.json)  
**门禁包 G/S**：[`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md)

**检索 Overlay**：G9 + G10 · [`phase_cs_en_task2_g10_overlay.py`](./phase_cs_en_task2_g10_overlay.py)  
**知识 Overlay**：#13 [`phase_cs_en_qa022_joyce_overlay.py`](./phase_cs_en_qa022_joyce_overlay.py) · `qa_022` Joyce 四步 `answer_en`  
**Context / Generation**：[`context_builder.filter_hits_for_cs_email`](../../context_builder.py) · [`pilot_en_context.py`](../../pilot_en_context.py) · DeepSeek `thinking: disabled`（cs_email）

---

## Retrieval · 9 case 门禁子集

| scenario | label | lib | top1 | Gate K |
| --- | --- | --- | --- | :---: |
| cs_0001 | #1 AT12131S | a3s | qa_011 | OK |
| cs_0008 | #8 TC148 | tc148 | qa_002 | OK |
| cs_0013 | #13 A3S | a3s | qa_022 | OK |
| cs_0022 | #22 | ad5s | qa_016 | n/a |
| cs_0023 | T1 | ad5s | qa_040 | OK |
| cs_0024 | T2 presales | ad5s | qa_037 | n/a |
| cs_0025 | T3 TC148 | tc148 | qa_001 | OK |
| cs_0026 | T4 board | a3s | qa_001 | OK |
| cs_0027 | T5 remote | a3s | qa_010 | OK |

**Top1 hit（可评分）**：**7/7** ✅

---

## Generation · Gate 9 case（`--generate`）

| scenario | top1 | G | S | 备注 |
| --- | --- | ---: | ---: | --- |
| cs_0001 | qa_011 | 4 | 3 | Dear Kara · DIP #3 |
| cs_0008 | qa_002 | 3 | 5 | extension→short cable ① · instant short ② |
| cs_0013 | qa_022 | 4 | 4 | Joyce ①–④ · 签名人 Lori ⚠️ |
| cs_0023 | qa_040 | 3 | 3 | F6 auto-close |
| cs_0024 | qa_037 | 3 | 4 | 售前 F7 · ~3.2k chars |
| cs_0025 | qa_001 | 3 | 3 | F8 warranty |
| cs_0026 | qa_001 | 3 | 3 | 换板排查梯 |
| cs_0027 | qa_010 | 3 | 3 | 远程多按 |
| cs_0022 | qa_016 | 3 | 4 | resolved |

**Generated replies**：**9/9** ✅ · **context_zh_leak**：**0/9** ✅

---

## Phase 1a · Pilot EN Index

| library | chroma_dir | pilot groups |
| --- | --- | --- |
| a3s | `_scratch/run-007/chroma_captioned_en` | qa_001/002/011/013/022/025/033/034 |
| ad5s | `_scratch/run-ad5s/chroma_captioned_en` | Gate Tier A 子集 |
| tc148 | `_scratch/run-tc148/chroma_captioned_en` | qa_001 · qa_002（Lori 序） |

Manifest：[`phase_1a_pilot_en_index.json`](./phase_1a_pilot_en_index.json) · 重建：`python _scratch/eval/phase_1a_pilot_en_index.py [--libs a3s|tc148|ad5s]`

---

## 命令

```powershell
# 检索-only（无 API）
python _scratch/eval/run_cs_e2e_gate.py

# 全量 E2E 生成
python _scratch/eval/run_cs_e2e_gate.py --generate

# 部分 + merge
python _scratch/eval/run_cs_e2e_gate.py --generate --ids cs_0013
python _scratch/eval/merge_cs_e2e_gate_results.py backup.json patch.json ...

# Context 单测
python _scratch/eval/test_cs_email_context.py
```

---

## 待殷主管（可选 · 部署后）

- [ ] Pilot 卡片格式确认  
- [x] Gate 9 E2E 探针 + 门禁包 G/S 初评  
- [ ] 正式 G/S Review 书面签字

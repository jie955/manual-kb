# Phase 0 · Reference vs System · Style Review

**Date**: 2026-07-08  
**Purpose**: 殷主管 Review 前自评 — 对照 Reference，不复制 Reference 全文进 prompt（Gate hold-out）。

| Case | Reference agent | Style family | System reply |
| --- | --- | --- | --- |
| cs_0001 | Joyce (#1) | F1_no_response | [Gate probe §cs_0001](./phase0_gate_probe.md#cs_0001) |
| cs_0008 | Lori (#8) | F2_tc148_wired | [Gate probe §cs_0008](./phase0_gate_probe.md#cs_0008) |
| cs_0013 | Joyce (#13) | F4_limit_travel | [Gate probe §cs_0013](./phase0_gate_probe.md#cs_0013) |

**Gate 9 `--generate` 探针**（2026-07-08）：检索 **7/7** · 生成 **9/9** · [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md)

---

## cs_0001 · AT12131S (Joyce)

| 维度 | Reference | 系统稿（Gate regen） | 状态 |
| --- | --- | --- | :---: |
| 称呼 | Dear **Kara** | Dear Kara ✅ | ☑ |
| 步骤 | 11#/12# · fuse · DIP #3 · instant short | 对齐 ✅ | ☑ |
| 体裁 | Joyce 四步 flat | F1 · 无 markdown 堆砌 | ☑ |

**G/S 初评**：**4 / 3**

---

## cs_0008 · TC148 (Lori)

| 维度 | Reference | 系统稿（Gate regen） | 状态 |
| --- | --- | --- | :---: |
| 称呼 | Dear **Cindy** | Dear Cindy ✅ | ☑ |
| 步骤 ① | **extension cable → short cable** | step 1 ✅ | ☑ |
| 步骤 ② | instant short 4#/5# · acknowledge jumper | step 2 + 「I know you've already…」✅ | ☑ |
| 术语 | immediately short · plug in pull out | instant short ✅ | ☑ |

**修复链**：Phase 1a `qa_002` Lori 序 · `pilot_en_context` · `filter_hits_for_cs_email` · TC148 prompt

**G/S 初评**：**3 / 5**

---

## cs_0013 · A3S stops before open (Joyce)

| 维度 | Reference | 系统稿（Gate regen） | 状态 |
| --- | --- | --- | :---: |
| 步骤 ① | 11#/12# press · >22V | step 1 ✅ | ☑ |
| 步骤 ② | FORCE clockwise · SOFT STOP counter-clockwise · full cycle | step 2 ✅ | ☑ |
| 步骤 ③ | push against gate · add load | step 3 ✅ | ☑ |
| 步骤 ④ | **arm off gate** · hold front mount | step 4 ✅ | ☑ |
| 称呼 | Dear **Edward** | Dear Edward ✅ | ☑ |
| 签名人 | **Joyce** | Lori ⚠️ | 待 F4 exemplar |

**修复链**：`qa_022` Joyce `answer_en`（[`phase_cs_en_qa022_joyce_overlay.py`](./phase_cs_en_qa022_joyce_overlay.py)）· `filter_hits_for_cs_email`（剔除 qa_020/qa_033）

**G/S 初评**：**4 / 4**

---

## 自评 · 「方向对了」检查单（甲方视角）

| # | 问题 | cs_0001 | cs_0008 | cs_0013 |
| ---: | --- | :---: | :---: | :---: |
| 1 | 像真人 TOPENS 客服信 | ☑ | ☑ | ☑ |
| 2 | 步骤编号清晰 | ☑ | ☑ | ☑ |
| 3 | 客户已做步骤有回应 | n/a | ☑ jumper | n/a |
| 4 | 术语/端子与 Reference 同级 | ☑ | ☑ | ☑ |
| 5 | 结尾索结果/视频/地址 | ☑ | ☑ | ☑ |
| 6 | 不会觉得「AI 贴手册」 | ☑ | ☑ | ☑ |

---

## 变更记录

| 日期 | 变更 |
| --- | --- |
| 2026-07-07 | v2 style exemplars · Name 数据层 · v3 Dear Cindy/Edward |
| 2026-07-08 | Context `filter_hits_for_cs_email` · TC148 Phase 1a EN · #8 extension 步 |
| 2026-07-08 | `qa_022` Joyce 四步 `answer_en` · #13 G **4** |

**仍 open**：#13 签名人 Joyce（现 Lori）· 见门禁包已知限制

---

## 殷主管 Review · Demo

```powershell
python qa_server.py --unified-cs --demo-presentation cs-email --images-dir _scratch/run-006/images --port 8765
```

预填三封 Customer Email：[`cs_email_pilot_cards.md`](./cs_email_pilot_cards.md)

# 22 封真邮 · 四维评分 · 说明与留档

**性质**：殷主管 MVP **80% 线**评测操作说明（工程）— 与 [验收标准 §2.3](./cs_client_requirement_standard.md#23-80准确率工程口径冻结--避免与检索-top1-混淆) 对齐  
**模板**：[`22封真邮_四维评分表.xlsx`](./22封真邮_四维评分表.xlsx)（三 sheet：使用说明 · 基线评分 · 复测评分）  
**语料**：[`samples/customer-service-emails/`](../../samples/customer-service-emails/) · Joyce 批次 **22 封**（`cs_0001`–`cs_0022`，均有客户原文 + 真实客服回信）  
**不含**：甲方测试题 T1–T5（`cs_0023`–`cs_0027` · 无 Reference）· Gate 探针集单独填 [门禁包](./cs_client_feedback_pack.md)

---

## 评测集边界（冻结）

| 集合 | 范围 | 计入 80% |
| --- | --- | :---: |
| **Joyce 22 封** | `cs_0001`–`cs_0022` | 见下 |
| **MVP 80% 分子集** | 22 封中 **a3s + ad5s** · **排除 TC148**（`cs_0008` · `cs_0009` · `cs_0010`） | **19 封** |
| **TC148（#8–#10）** | 仍跑 E2E · 填门禁包 | **不计入** 80% 分母（与 Wave 2 两系列演示一致） |
| **Gate 探针** | ~10 封 Tier A · overlay 精修样本 | **仅诊断** · 不可替代真邮通过率 |

**通过线**：MVP 子集 **19 封中 ≥16 封** ④整体通过（≥84% · 满足 80% 向上取整）→ Wave 1 出口达标。

---

## 四维定义

| 维度 | 选项 | 说明 |
| --- | --- | --- |
| **① 机型/问题命中** | 对 / 错 | 路由库 + 故障路径是否与来信一致 |
| **② 英文回复可用度** | 直接可发 / 小改可发 / 需重写 | 对照 Reference（有则必对）· 端子/DIP/步骤 |
| **③ 图片配对** | 配对相关 / 图不对 / 该配没配 / 无需图 | 对应 MVP-0-3 图文结合 |
| **④ 整体通过** | 通过 / 不通过 | **严格线（冻结）**：①对 **且** ②=**直接可发** **且** ③∉{图不对, 该配没配} |

> 「小改可发」**不算** ④通过 — 对齐殷主管「直接复制到邮件中」。内部可单列「小改可发率」作参考，**不得**替代 80% 发链判据。

---

## Round 0 / Round 1 路径约束

**Round 0（基线）与 Round 1（复测）必须使用同一 E2E 客户路径**，方可对比提升幅度：

```text
EN-primary 索引（chroma_captioned_en）
  + library_router / qa_server --unified-cs
  + locale=en · response_mode=cs_email
  + （Wave 2 后）--allowed-libraries a3s,ad5s
```

**推荐顺序**（与 [执行清单 Wave 1](./cs_en_poc_execution.md#wave-1--准确率攻克殷主管-二先攻克准确率--3-5-天) 一致）：

```text
G11 切 EN 路径 → Round 0 基线 → 修库/生成 → Round 1 复测
```

若 Round 0 在 legacy ZH-index 上采集，须标注 `path=zh-index-legacy`，**不得**与 EN Round 1 直接比通过率。

---

## Excel 建议列（与模板对齐）

| 列 | 用途 |
| --- | --- |
| `mail_no` | 1–22 |
| `cs_id` | 如 `cs_0013` |
| `Reference链接` | 语料 md 超链接（`samples/customer-service-emails/` · 对照 Joyce Reference） |
| `library` | a3s / ad5s / tc148 |
| `in_mvp_80%` | Y / N（xlsx 列名 **计入MVP19** · 是/否 · 照抄 round0.json 的 `mvp19`） |
| `fail_tag` | 检索 / 生成 / 图片 / 机型 / 复合 / — |
| `scorer` | 评分人 |
| `date` | 评分日期 |

**留档**：每轮批量取数 → [`cs_22mail_batch_runner.py`](./cs_22mail_batch_runner.py) 写出 [`cs_22mail_eval_round0.json`](./cs_22mail_eval_round0.json) / [`cs_22mail_eval_round1.json`](./cs_22mail_eval_round1.json)；人工四维打分在 xlsx。

**预填 xlsx（机器列 B–D · J · L）**：

```bash
cd _scratch/eval
python fill_round0_to_xlsx.py --json cs_22mail_eval_round0.json --sheet "基线评分(修复前)"
python fill_round0_to_xlsx.py --json cs_22mail_eval_round1.json --sheet "复测评分(Wave1后)"
```

**四维草稿（仅参考 · 写入 E–I 后须人工确认）**：

```bash
python draft_22mail_scoring.py --json cs_22mail_eval_round1.json --apply-sheet "复测评分(Wave1后)"
python draft_22mail_scoring.py --json cs_22mail_eval_round0.json --apply-sheet "基线评分(修复前)"
```

输出：[`scoring_draft_round0.md`](./scoring_draft_round0.md) · [`scoring_draft_round1.md`](./scoring_draft_round1.md) · [`round0_vs_round1_summary.md`](./round0_vs_round1_summary.md)

**Round 0 vs Round 1 机械对比**：

```bash
python compare_round0_round1.py
```

**批量取数（Round 0 示例）**：

```bash
cd _scratch/eval
python cs_22mail_batch_runner.py --round round0 --index en --generate \
  --ids-file cs_22mail_ids.txt --out cs_22mail_eval_round0.json
```

输出每条含 `top1_group`、`generated_reply_en`、`images_used`（供③对照）、`mvp19`（**照抄到 xlsx「计入MVP19」列** — 脚本按 `expected_library` / `matched_library == tc148` 判定，非人工猜 MAIL 编号）。

---

## 与 Gate 探针 / 门禁包关系

| 资产 | 角色 |
| --- | --- |
| **本评测（22 封四维）** | **发链判据** · 殷主管 §2.3 80% 线 |
| **Gate 探针 + G/S 1–5** | **诊断** · 定位检索/生成/路由 · 填 [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) |
| **检索 Top1 / Gate K 14/14** | **中间指标** · 不得单独对外汇报达标 |

**禁止**：只用探针 Gate G≥4 或 Gate K 100% 替代真邮 80% 作对外汇报（见执行清单「本期明确不做」）。

---

## MVP 80% 子集 · 19 封清单

| cs_id | 邮件 # | 库 |
| --- | ---: | --- |
| cs_0001 | 1 | a3s |
| cs_0002 | 2 | a3s |
| cs_0003 | 3 | a3s |
| cs_0004 | 4 | a3s |
| cs_0005 | 5 | a3s |
| cs_0006 | 6 | a3s |
| cs_0007 | 7 | ad5s/a3s 等 |
| cs_0011 | 11 | a3s |
| cs_0012 | 12 | a3s |
| cs_0013 | 13 | a3s |
| cs_0014 | 14 | ad5s |
| cs_0015 | 15 | ad5s |
| cs_0016 | 16 | ad5s |
| cs_0017 | 17 | a3s |
| cs_0018 | 18 | a3s |
| cs_0019 | 19 | ad5s |
| cs_0020 | 20 | ad5s |
| cs_0021 | 21 | ad5s |
| cs_0022 | 22 | ad5s |
| cs_0008–0010 | 8–10 | tc148 · **不计入** |

> 上表 `library` 以各场景文件 frontmatter 为准；评分时在 Excel 填实际路由库。

---

## 变更记录

| 日期 | 变更 |
| --- | --- |
| 2026-07-08 | 初版 · 吸收 review：19 封 MVP 子集 · 严格④ · Round 同路径 · 探针降级 |
| 2026-07-08 | v2 xlsx · `计入MVP19` 列 + MVP-19 汇总公式 · [`cs_22mail_batch_runner.py`](./cs_22mail_batch_runner.py) 批量取数 · `mvp19` 自动判定 TC148 |
| 2026-07-08 | Round 1 批量 22/22 · [`round0_vs_round1_summary.md`](./round0_vs_round1_summary.md) · [`fill_round0_to_xlsx.py`](./fill_round0_to_xlsx.py) / [`draft_22mail_scoring.py`](./draft_22mail_scoring.py) · xlsx 双 sheet 预填 + 草稿 E–I（**须人工确认**） |

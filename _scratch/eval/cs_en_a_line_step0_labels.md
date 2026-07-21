# A 线 · Step 0 标注表（22 封真邮 + T1–T5）

**性质**：任务与交付 · A 线 Grounding overlay 工作底稿  
**日期**：2026-07-08（#3 / #22 裁定定稿）  
**真源**：[`cs_email_query_map.json`](./cs_email_query_map.json) · [`customer-service-emails/README.md`](../../samples/customer-service-emails/README.md) · [`cs_en_style_corpus_plan.md`](./cs_en_style_corpus_plan.md) §4

**图例**

| 列 | 含义 |
| --- | --- |
| **MVP 族** | Joyce 两系列口径：`a3s` / `ad5s` / `other` |
| **结构标签** | `customer_experiment` · `standard_troubleshoot` · `presales` · `warranty` · `multi_turn` · `out_of_corpus` |
| **A 线** | 首期是否 overlay 进 chroma |
| **A 动作** | `verbatim` = `email_examples[]` · `steps` = `answer_en` patch · `both` · `—` |
| **修复优先级** | 高 = 路由对但 Top1 误排 / 实测 miss |

---

## 裁定摘要（#3 · #22）

### #3 `cs_0003` · AD8 · LED 有反应门不动

| 字段 | 裁定 |
| --- | --- |
| **问题类型** | 路由 **ad5s 正确**（logic→AD 系列）；**同族内 Top1 误排**（`qa_040` 抢 `qa_010`） |
| **建议 qa_group** | **`qa_010`（主）** · `qa_001`（Top3 acceptable） |
| **非期望** | `qa_040`（§九 中途走停/auto-close，症状不符） |
| **A 动作** | **`verbatim`** — 将 Tier A 原话挂 `ad5s` `qa_010` `email_examples[]` |
| **修复优先级** | **高**（实测跑错，非仅标注空白） |
| **附带** | `qa_040` 可做负样本（排除 no-response）；DIP #5 vs #3 另开 overlay，不阻塞本 case |

### #22 `cs_0022` · A5132 dual swing · 全开回关 4 ft

| 字段 | 裁定 |
| --- | --- |
| **产品线** | A5132 = **A5 系列 · dual swing**（非单臂） |
| **corpus** | **`out`** — 型号不在 v1 docx |
| **产品线族** | 逻辑上 **a3s** 语料族；a3s **无** `qa_016` 同类组 |
| **运行时参考** | `ad5s` / **`qa_016`**（开到位反弹·Pull-to-Open）· 生成对齐 Heidi · **n/a 不评分** |
| **A 线** | **No**（不进 chroma overlay） |
| **主用线** | **C** — Gate hold-out · 体裁 + Pull fork |
| **未来** | a3s v2 补「开到位反弹」独立组；现不修复 |

---

## 故障类（20 封）

| # | cs_id | 表单型号 | MVP 族 | 结构标签 | library | 建议 qa_group | A 线 | A 动作 | 修复优先级 | 主用线 | 备注 |
| ---: | --- | --- | --- | --- | --- | --- | :---: | --- | --- | --- | --- |
| 1 | cs_0001 | AT12131S | a3s | `customer_experiment` | a3s | **qa_011** | Yes | `both` | — | C | Gate · 电机直供 · DIP#3 真源 |
| 2 | cs_0002 | A8132 | a3s | `customer_experiment` | a3s | qa_001, qa_033 | Yes | `verbatim` | — | A | 电机零电压 · 多轮 |
| **3** | **cs_0003** | **AD8** | **ad5s** | `standard_troubleshoot` | ad5s | **qa_010**, qa_001 | **Yes** | **`verbatim`** | **高** | A | **LED 有反应门不动 · ad5s 内 Top1 误排 qa_040** |
| 8 | cs_0008 | PW502+TC148 | other | `customer_experiment` | tc148 | qa_001, qa_002 | 降级 | `steps` | — | C | Gate · MVP 隐藏 TC148 |
| 9 | cs_0009 | AT6131+TC148 | other | `multi_turn` | tc148 | qa_001, qa_002 | 降级 | `verbatim` | — | C | 3 轮 · MVP 不做 |
| 10 | cs_0010 | A8131+TC148 | other | `standard_troubleshoot` | tc148 | qa_001, qa_002 | 降级 | `—` | — | C | MVP 不做 |
| 12 | cs_0012 | AT12131 | a3s | `standard_troubleshoot` | a3s | qa_019–021 | Yes | `verbatim` | — | A | 限位 B · Pull/Push fork |
| 13 | cs_0013 | A3S | a3s | `standard_troubleshoot` | a3s | **qa_022** | Yes | `steps` | — | C | Gate · Joyce 四步 |
| 14 | cs_0014 | AT602 | other | `out_of_corpus` | — | — | No | `—` | — | C | 无 v1 docx |
| 15 | cs_0015 | AD8S | ad5s | `standard_troubleshoot` | ad5s | qa_040, qa_015/016 | Yes | `steps` | — | A | auto close 二次关 |
| 16 | cs_0016 | PW802 | ad5s | `standard_troubleshoot` | ad5s | qa_001 | Yes | `verbatim` | — | A | 红灯闪 · logic→ad5s |
| 17 | cs_0017 | A5131 | a3s | `warranty` | a3s | qa_033 | Yes | `steps` | — | B+C | 保修+排查 |
| 18 | cs_0018 | A5/A8 | a3s | `standard_troubleshoot` | a3s | qa_001, qa_002 | Yes | `verbatim` | — | A | v1 direct |
| 19 | cs_0019 | AD5S | ad5s | `standard_troubleshoot` | ad5s | qa_016, qa_020, qa_005 | Yes | `both` | — | A | 开过头+学码 |
| 20 | cs_0020 | AT1202 | other | `customer_experiment` | — | — | No | `verbatim` | — | C | corpus out · slave arm |
| 21 | cs_0021 | A8132 | a3s | `customer_experiment` | a3s | qa_001 | Yes | `both` | — | A | 同 T4 族 |
| **22** | **cs_0022** | **A5132** | **ad5s†** | `multi_turn` | **—** | **qa_016‡** | **No** | `steps` | — | **C** | **out · Gate hold-out · 运行时 ad5s/qa_016 n/a** |

† 产品线属 A5→a3s 族；‡ 仅运行时近似参考，不进 A 线 overlay。

---

## 售前类（6 封 · 不进 A 线）

| # | cs_id | 结构标签 | A 线 | 主用线 |
| ---: | --- | --- | :---: | --- |
| 4–7, 11 | cs_0004–0007, cs_0011 | `presales` | No | B |

---

## 甲方测试题

| 测# | cs_id | library | 建议 qa_group | A 线 | 主用线 |
| --- | --- | --- | --- | :---: | --- |
| T1 | cs_0023 | ad5s | qa_040, qa_015/016/020 | Yes | C（已 Gate） |
| T2 | cs_0024 | — | — | No | B |
| T3 | cs_0025 | tc148 | qa_001, qa_002 | 降级 | C |
| T4 | cs_0026 | a3s | qa_001, qa_033 | Yes | C（已 Gate） |
| T5 | cs_0027 | a3s | qa_010 | Yes | C |

---

## A 线 MVP 汇总

| 桶 | 封数 | 列表 |
| --- | ---: | --- |
| **必做 overlay** | 12 | #1 #2 **#3** #12 #13 #15 #16 #17 #18 #19 #21 + T4 |
| **高优先级修复** | **1** | **#3**（同族 Top1 误排） |
| **不进 A · out/Gate** | 3 | #14 #20 **#22** |
| **不进 A · TC148** | 3 | #8 #9 #10 |
| **不进 A · 售前** | 6 | #4–#7 #11 |

---

## 执行记录（2026-07-08 · overlay 已跑）

| Case | 动作 | Spot check Top1 | 备注 |
| --- | --- | --- | --- |
| **#1** cs_0001 | `qa_011` **both** | **qa_011** ✅ | Joyce `answer_en` + `email_examples[]` |
| **#13** cs_0013 | `qa_022` **verbatim** | **qa_022** ✅ | Gate 检索 OK |
| **T4** cs_0026 | `qa_001` **verbatim** | **qa_001** ✅ | Gate 检索 OK |
| **#3** cs_0003 | `ad5s` `qa_010` **verbatim** | **qa_010** ✅ | 原 Top1 `qa_040` 已修复；derived query 亦 qa_010 |

脚本：[`phase_cs_en_a_line_pilot_overlay.py`](./phase_cs_en_a_line_pilot_overlay.py) · 结果：[`cs_en_a_line_pilot_overlay_result.json`](./cs_en_a_line_pilot_overlay_result.json)

```powershell
python _scratch/eval/phase_cs_en_a_line_pilot_overlay.py
```

---

## 执行顺序（建议 · 后续）

1. 其余 A 线 12 封按表逐组 overlay（#12 #15 #16 …）
2. 全量 `run_cs_en_retrieval_baseline.py` 刷新 Task 1 报告
3. #3 E2E 生成（`run_cs_e2e_gate.py --ids cs_0003 --generate`）

维护：改 `extract_cs_email_queries.py` 后执行 `python _scratch/eval/extract_cs_email_queries.py` 刷新 JSON。

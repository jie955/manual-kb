# Task 0 · Oracle 英文生成 Smoke

**状态**：✅ 2026-07-07 · 3/3 side-by-side Oracle 已生成  
**定位**：**内部探针** — 分离「生成上限」与「E2E 检索瓶颈」。**Oracle 通过 ≠ 可发版**；发版以 E2E Gate + [`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) 为准。

## 配置

| 项 | 值 |
| --- | --- |
| `locale` | `en` |
| `response_mode` | `cs_email` |
| Chunk 来源 | **Oracle**（`expected_group_id`） |
| 模型 | gemini-2.5-flash |
| 脚本 | [`run_cs_side_by_side_gen.py`](./run_cs_side_by_side_gen.py) |

## 结果摘要

| case | oracle | Grounding | Quality | Exit |
| --- | --- | ---: | ---: | --- |
| A cs_0013 | qa_034 + qa_022 | 4 | 4 | ✅ median≥3 |
| B cs_0008 | qa_002 | 3 | 4 | ✅ · ⚠️ 端子号 |
| C cs_0022 | qa_015 | 2 | 3 | ✅ · out 近似 |

**Exit**：≥8 条 → **3 条 demo 集** · Reply median **= 3.67** · 无 critical  WARRANTY 错误 · Case B 端子号属 grounding 瑕疵

## 解读 → 下一刀

| 发现 | 行动 |
| --- | --- |
| Oracle A 较好但缺 qa_022「push against」 | 多 hit 合并策略保留；prompt 强调「合并多 reference 全部 relevant 步」 |
| B 端子号 hallucination | chunk 补 PW502 4#/5# 映射；或 cs_email prompt 禁止未出现端子号 |
| C out-of-corpus 差 | 预期内 · Demo 用 A/B；C 展示「无手册时索要 invoice + 通用 isolate」 |
| 英文体裁可接受 | **优先 P0 Demo 英进英出**；并行 Task 1 E2E Top1 |

## 结果表

详见 [`cs_side_by_side_demo.md`](./cs_side_by_side_demo.md) 与 [`cs_side_by_side_generated.json`](./cs_side_by_side_generated.json).

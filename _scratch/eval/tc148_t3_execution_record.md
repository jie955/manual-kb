# TC148 T3 检索 disambiguation · 执行记录

**日期**：2026-07-05  
**状态**：**✅ 关闭**  
**脚本**：[`phase_tc148_t3_disambiguation.py`](./phase_tc148_t3_disambiguation.py)

---

## 问题（t06 / demo T3）

| query | 期望 | patch 前 Top1 |
| --- | --- | --- |
| `push button 端口短接测试 O/S/C COM` | qa_002 | **qa_001**（COM 接地图 caption + 共用 push button 步） |

根因：2 组共享「断配件 / push button 端口 / COM」词汇；qa_001 的 **image_001 COM→地** caption 与 query 的 `COM` 重叠，压过 qa_002 的「瞬时短接 O/S/C COM」语义。

---

## Patch（限位域同型 · 2 组症状化）

| group | 改动 |
| --- | --- |
| **qa_001** | 症状行 → 随机开关门/乱动 · **非**短接 · **非**无反应 |
| **qa_002** | 症状行 + question → 遥控可用无反应 · **push button 瞬时短接 O/S/C COM** · **非**随机乱动 |

Backup：`20260705-tc148-t3`

---

## 验收

| 指标 | patch 前 | patch 后 |
| --- | ---: | ---: |
| TC148 eval Top1 | 5/6 | **6/6** |
| t06 Top1 | qa_001 ❌ | **qa_002 ✅** |
| t01–t05 | 5/5 | **5/5**（无回归） |
| verify_tc148_content | — | **PASS** |

产物：[`tc148_t3_post_eval.json`](./tc148_t3_post_eval.json)

---

## V1.1 序位

- **#1 TC148 T3** → **本项 ✅**
- **#2 demo LLM=on 截图** → open
- **#3 content_role 设计讨论** → open（先讨论再编码）

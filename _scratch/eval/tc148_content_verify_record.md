# TC148 · 内容准确性核实记录

**日期**：2026-07-05  
**范围**：2 组 · links 可点 · COM 图 · 短接 video · **不做** EN 邮件稿 UI 展开  
**脚本**：[`verify_tc148_content.py`](./verify_tc148_content.py)

---

## 静态结构（C1–C4）

| 检查 | qa_001 | qa_002 |
| --- | :---: | :---: |
| `links[]` 数量 | 1× topens 共端子 | 2× topens + Drive video |
| `answer_en` 无裸 URL | ✅ | ✅ |
| ZH 关键步骤 | 接地三步 | 短接 push button |
| 配图 | **image_001** COM→地 | 无（原文一致） |

Drive 链：`link_type=video` · label 含短接语义（Instantaneously Short…）

---

## 检索 spot-check（非 blocking）

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| T2 | TC148 没反应 遥控器正常 | qa_002 | 标准路径 |
| T1 | 墙壁开关自检后灯常亮 | qa_001 | 口语近似 · 已知 minor |
| T3 | push button 端口短接 O/S/C COM | **qa_002 ✅**（post T3 patch） | 2 links · ZH 含短接语义 |

---

## 越界（回归）

T4/T5/X1：拒答或说明无内容 — 维持 Gate #5 结论，本次未复测浏览器。

---

## 结论

**TC148 内容层准确 ✅** — extract + `links[]` + ZH 步骤 + COM 图齐全；T3 Top1 miss 仍为 known retrieval backlog，不 retro-block。

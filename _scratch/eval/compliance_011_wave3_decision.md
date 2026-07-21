# COMPLIANCE-011 · Wave 3 书面方案

**日期**：2026-07-08  
**范围**：qa_011 · Drive 短接演示视频 · A3S 排查  
**性质**：Wave 3 发链前 B 轴产品链决策留档（殷主管 MVP · 一期）

---

## 背景

docx ZH 明示：**「注意站内信不可发此链接」**。Drive URL 当前在 `answer_en` prose 中，Demo **未**暴露为可点击 `links[]`（见 [`a3s_18h1_handtest_issues.md`](./a3s_18h1_handtest_issues.md) §二）。

---

## Wave 3 决策（2026-07-08 · 执行）

| 项 | 决定 |
| --- | --- |
| Demo CS 视图 | **维持不可点击** · 不加 `links[]` |
| 工程师视图 | prose 保留 · **不**渲染为参考链接栏可点项 |
| 站内信 / 对客通道 | **禁止**自动插入 Drive 链（与 docx 一致） |
| 后续 | 若殷主管书面要求展示，再单独立项（折叠 / 内部-only / strip） |

**理由**：在甲方未书面确认前，结构化进 `links[]` 并展示 **比现状更危险**（一键复制进邮件）。

---

## Wave 3 出口勾选

- [x] COMPLIANCE-011 **有书面方案**（本文件 · 方案 = 维持不可点）
- [ ] 殷主管试跑后若要求变更 → 记入试跑反馈表

---

## 交叉引用

- [`a3s_18h1_handtest_issues.md`](./a3s_18h1_handtest_issues.md) §二  
- [`cs_en_poc_execution.md`](./cs_en_poc_execution.md) Wave 3 · 3.2.3

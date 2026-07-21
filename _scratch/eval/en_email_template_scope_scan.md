# EN 客服邮件体裁 · 范围摸底

**日期**：2026-07-05 · **脚本**：[`scan_en_email_template_scope.py`](./scan_en_email_template_scope.py)

专门筛 **EN 是否为完整客服邮件模板**（非 V1-05 规格缺口扫描）。
复用 `negotiation_utils` 协商检测 + BL-V1-05 TC148 型信号（`Please help us confirm` / `If problem disappears` 等）。

## 库级汇总

| 库 | 总组数 | 有信号 | A 邮件稿 | B 礼貌嵌入 | C 协商 | D 索视频 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **AD5S** | 43 | 19 | 0 | 3 | 1 | 8 |
| **A3S** | 28 | 6 | 0 | 0 | 0 | 2 |
| **TC148** | 2 | 2 | 2 | 0 | 0 | 0 |

## 结论（设计范围）

- **A 型（整篇客服邮件稿 vs ZH 速记）全库仅 TC148 2 组** — 与 2026-07-03 `Please help us confirm` 结论一致；AD5S/A3S **无**同体裁组。
- **B 型（礼貌/分支句嵌入、步骤仍对齐）**：AD5S 3 组 · A3S 0 组 — 属 EN 排查文案风格差异，**不应**走「客服邮件模板可选展开」通道（与 BL-V1-05 子模式 B 一致）。
- **C 型（协商）**：1 组 — 已有 `negotiation_offer` / BL-V1-06（qa_023 等协商句在 `negotiation_offers[]`，不在 `answer_en`）。
- **D 型（末尾索视频）**：10 组 — 步骤主体仍是排查手册；可选折叠，但 **非** TC148 式整篇邮件稿。

**V1.1  implication**：若只为 A 型服务，`content_role` 机制范围 **≤2 组（TC148）**；通用 schema + demo UI 可能 overkill，**字段标注或 TC148 专用展示** 即可。

## 分桶说明

- **A_tc148_email_template** (2) — TC148 型 · EN 整篇客服邮件稿 vs ZH 速记（content_role 候选）
- **B_polite_inline_copy** (3) — AD5S 型 · EN 礼貌/分支句嵌入 · 步骤骨架仍对齐
- **C_negotiation_only** (1) — 协商话术 · negotiation_offer（已实现）
- **D_media_request_closing** (10) — 仅末尾索视频/附件 · 非整篇邮件稿
- **E_weak_signal** (11) — 弱信号 · 不构成体裁差异

## A_tc148_email_template

| 库 | group | 分数 | 信号 | 判定 |
| --- | --- | ---: | --- | --- |
| TC148 | qa_001 | 19 | opener_confirm, following_tests_diagnosis, if_problem_disappears, go_on_steps, below_link_howto, may_i_ask… | EN 完整客服邮件稿 · ZH 内部速记 · 体裁异构 |
| TC148 | qa_002 | 18 | opener_confirm, following_tests_diagnosis, if_problem_disappears, go_on_steps, below_link_howto, may_i_ask… | EN 完整客服邮件稿 · ZH 内部速记 · 体裁异构 |

## B_polite_inline_copy

| 库 | group | 分数 | 信号 | 判定 |
| --- | --- | ---: | --- | --- |
| AD5S | qa_015 | 3 | if_problem_disappears, following_tests_generic | EN 含客服口吻/分支句 · ZH 步骤骨架对齐 · 非整篇邮件稿 |
| AD5S | qa_031 | 2 | if_problem_disappears | EN 含客服口吻/分支句 · ZH 步骤骨架对齐 · 非整篇邮件稿 |
| AD5S | qa_035 | 4 | may_i_ask, if_so_following_tests, following_tests_generic | EN 含客服口吻/分支句 · ZH 步骤骨架对齐 · 非整篇邮件稿 |

## C_negotiation_only

| 库 | group | 分数 | 信号 | 判定 |
| --- | --- | ---: | --- | --- |
| AD5S | qa_023 | 2 | email_video_closing, thanks_cooperation | 协商话术（BL-V1-06 · negotiation_offers 字段）· 非邮件模板体裁 |

## D_media_request_closing

| 库 | group | 分数 | 信号 | 判定 |
| --- | --- | ---: | --- | --- |
| AD5S | qa_016 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_017 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_018 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_019 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_032 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_034 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_036 | 3 | email_video_closing, thanks_cooperation, please_let_me_know | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| AD5S | qa_040 | 3 | following_tests_generic, email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| A3S | qa_015 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
| A3S | qa_016 | 2 | email_video_closing, thanks_cooperation | 末尾索视频/邮件附件话术 · 步骤主体仍为排查手册 |
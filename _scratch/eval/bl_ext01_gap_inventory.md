# BL-EXT-01 · AD5S extract 缺口表（摸底 · 2026-07-05）

**状态**：摸底完成 · **未写代码**  
**扫描脚本**：[`bl_ext01_gap_scan.py`](./bl_ext01_gap_scan.py) → [`bl_ext01_gap_scan.json`](./bl_ext01_gap_scan.json)  
**对照源**：`samples/troubleshooting/AD5S-AD8S常见问题排查.docx` vs `_scratch/run-ad5s/qa_groups.json`（prod · 27 组）

---

## 0. Executive 摘要

| 项 | 先前估计 | 本次核实 | 根因（共性） |
| --- | ---: | ---: | --- |
| URL 差集 | ~21 vs 8 | **14 unique vs 5 unique**（差 **9**） | 大量 URL 在 **无 H2 的 H1 正文**里，整段未入库 |
| §十九 保养 | 无组 · 逐句交替有风险 | **29 段 orphan · 0 个 H2** | **不是** classify 错切主因；**是** extractor 无 H2 则丢弃 |
| 50Ω/1152 公式 | qa_024 ZH 无 | **§十四 H1 引言 4 段 orphan**（公式占 2 段） | 在 **qa_022 H2 之前**，`current_group is None` 被 skip |

**结论**：BL-EXT-01 的核心不是「重跑 extract 就能自动修好」，而是 **docx 结构与 extractor 假设（H1→H2→正文）不匹配**。修法分三档：orphan 兜底、手工补 H2/组、复杂档链接补全。

---

## 1. docx 章节覆盖总览

docx **20** 个 H1 · qa_groups 仅覆盖 **9** 个 H1（27 组 H2/H3）。

### 1.1 已入库 H1（9）

一、二、完全不工作、五、十、十一、十二、十四、二十

### 1.2 完全未入库 H1（11）

| H1 | orphan 段落数 | H2 数 | 备注 |
| --- | ---: | ---: | --- |
| 一个机臂完全不工作 | 10 | 0 | 整节 flat |
| 六、随意开关门 | 10 | 0 | |
| 七、缓停止有问题 | 9 | 0 | |
| 八、自动关门不生效 | 8 | 0 | |
| 九、开关门过程中走停或反弹 | 21 | 0 | |
| 十三、门机运行慢 | 12 | 0 | |
| **十五、电机转机臂不伸缩** | 16 | 0 | 含 2× topens 链 |
| **十六、机臂声音异常** | 35 | 0 | 含 YouTube |
| **十七、离合打不开** | 22 | 0 | 含 3× YouTube |
| 十八、风会把门吹开 | 6 | 0 | |
| **十九、保养与润滑** | **29** | **0** | 含 2× topens + YouTube |

**合计 orphan 段落：193**（[`qa_doc_extractor.py`](../../qa_doc_extractor.py) L304–305：`current_group is None` → `continue`）

> 上述 11 节 **全部零 H2**——不是 extract bug，是 **源 docx 版式**与 pipeline 假设不一致。BL-EXT-01 本轮焦点是 §十四/§十九；其余登记 **BL-EXT-01b**（见 §1.3）。

**另：§十二** 已有 **2 组**入库（`qa_011`/`qa_012` 等），但 H1 下仍有 **11 段 orphan**（「开门不限位 / 拉开门安装…」等子场景无 H2）——属 **部分覆盖**，非整节丢失。

### 1.3 BL-EXT-01b · 其余 H1 orphan（不含 §十四 / §十九）

**核实结论**：**10 节整节零 H2**（纯盲区）+ **§十二 partial**（错组风险 · **单独一类**）。

#### A · 整节零 H2（10 节 · 148 段 · 纯检索盲区）

| H1 节 | orphan | 典型场景 |
| --- | ---: | --- |
| 十六、机臂声音异常 | 35 | 异响决策树 |
| 十七、离合打不开 | 22 | 离合/拆机+YouTube |
| 九、走停或反弹 | 21 | 中途走停 |
| 十五、电机转臂不伸缩 | 16 | 电机转不动 |
| 十三、门机运行慢 | 12 | 运行慢 |
| 一个机臂完全不工作 | 10 | 单臂不工作 |
| 六、随意开关门 | 10 | 随机开关 |
| 七、缓停止有问题 | 9 | 缓停错乱 |
| 八、自动关门不生效 | 8 | 不会自动关 |
| 十八、风把门吹开 | 6 | 风大吹动 |

#### B · §十二 partial（11 段 · 勿与 A 合并表述）

| 维度 | 说明 |
| --- | --- |
| prod | **已有 2 组**（不限位相关） |
| orphan | 开门不限位/拉开门安装/限位 A 外移等 **H1 子场景** |
| 风险 | **命中已有组但答案不全/不对应**（高于「查不到」） |

**复评触发**：BL-EXT-01 第 2–4 步 prod 签字 ✅ → **BL-EXT-01b 分类摸底** [`bl_ext01b_classification.md`](./bl_ext01b_classification.md) ✅ → 分批入库。

**机器可读**：[`bl_ext01_gap_scan.json`](./bl_ext01_gap_scan.json) · [`bl_ext01b_classification.json`](./bl_ext01b_classification.json)

---

## 2. §十九 保养组 · 核实结论

### 2.1 版式（实测，非推测）

| 指标 | 值 |
| --- | --- |
| 段落总数 | 29（全为 H1 下 orphan） |
| `classify_language` | **zh: 2 · en: 27** |
| 相邻语种翻转 | **3 次**（非逐句交替） |

**样例顺序**（前几段）：

1. `日常保养润滑：`（zh）
2. `In cold climates where temperatures reach 1°C…`（en）
3. `For maintenance, please spray WD40…`（en）
4. `如果运行不顺畅等，可更进一步拆机臂润滑…`（zh）
5. `Besides, grease is needed to lubricate…`（en）
6. …后续多为 EN 步骤/链接枚举

### 2.2 错切风险判定

| 问题 | 判定 |
| --- | --- |
| 「逐句交替 → classify 污染」 | **理论风险存在，但不是当前主因**；实际以 EN 大块为主，仅 3 处 zh↔en 翻转 |
| 「内容被切坏」 | **否**——内容 **整节未入库**（0 组），不存在切坏，只有 **丢失** |
| 若强行加 H2 再 extract | classify 大概率把 27 EN / 2 ZH **正确分流**；需人工抽查 3 处翻转点 |

### 2.3 §十九 内含 URL（均在 orphan 内）

| URL | 类型 | 建议档 |
| --- | --- | --- |
| `topens.com/.../essential-guide-to-regular-maintenance-and-care-for-your-gate-opener` | 博客 | BL-V1-04 **简单档** |
| `topens.com/.../preventing-winter-freezing-of-automatic-gate-opener-arms` | 博客 | 简单档 |
| `youtube.com/watch?v=IRIA5iaWHqE`（×2 出现） | 视频 | 简单档 |

### 2.4 处理方案（待拍板 · 未实施）

**推荐 A**：docx 或 post-process **补 H2** → 重跑 extract → 抽查 3 翻转点 + 浏览器 1 query。

**备选 B**：extractor「H1 orphan 收集器」——影响 11 节，见 **BL-EXT-01b**。

### 2.5 §十九 H2 粒度（A 方案内再拍板）

docx 内 §十九 实为 **三段不同逻辑**，与 troubleshooting 其他组「一 H2 一故障场景」不一致：

| 建议 H2 | 内容 | 检索场景 |
| --- | --- | --- |
| **日常保养** | WD40/机油喷丝杆；寒冷 1°C 下 4–6 周 | 「平时怎么保养」 |
| **深度润滑（拆机臂）** | 拆不锈钢管/丝母/丝杆 + YouTube 教程链 | 「运行不顺 / 要拆机润滑」 |
| **维护指南链接** | topens 博客 ×2（essential guide / winter freezing） | 「保养手册 / 冬天防冻」 |

**不推荐** 仅 1 个 H2 收整节——体积过大，易与「异响润滑」等 query 交叉污染。工作量：补 2–3 个 H2 vs 1 个，extract 侧几乎相同。

---

## 3. 50Ω / 1152 公式 · 核实结论

### 3.1 位置（重要修正）

公式 **不在 qa_022 组内**，而在 **§十四 H1 与第一个 H2（「电机电流小的原因」→ qa_022）之间的 H1 引言**：

```
§十四 H1
  zh | 电机电流小导致的走停一般是…（symptom 概述）
  zh | …可以先试试50欧的电阻…不行再25欧。          ← orphan
  zh | 负载电阻…功率要大于1152除以电阻值。          ← orphan
  zh | 电阻阻值变小发热会更厉害…
H2 | 电机电流小的原因                              → qa_022（answer_zh 空，仅 EN）
H2 | 并接机臂红黑线排查                            → qa_023
H2 | 手动反推来排查+电阻                           → qa_024
…
```

### 3.2 入库状态

| 文本 | docx | qa_groups |
| --- | :---: | :---: |
| 50Ω→25Ω 渐进建议 | ✅ zh orphan | ❌ |
| 1152÷R 功率公式 | ✅ zh orphan | ❌ grep `1152` = 0 |
| qa_022 `answer_zh` | — | **空**（仅 EN 原理段） |
| qa_024 `answer_zh` | — | 无公式（先前 grep 正确，但归属应是 §十四 引言） |

D2 query「门刚动一下就停 电机电流太小」Top1 **qa_022**——公式在更靠前的 orphan 里，**检索路径够不到**。

### 3.3 处理方案（待拍板）

| 方案 | 做法 | 利弊 |
| --- | --- | --- |
| **A · 引言并 qa_022** | 4 段 orphan 并入 qa_022 `answer_zh` | 最小；D2 路径直接受益；与「原因」语义贴合 |
| **B · 新建 qa_021b** | 单独组「走停加电阻选型要点」 | 检索需 eval 探针；边界清晰 |
| **C · 并 qa_024** | 不推荐 | 公式在 qa_024 H2 **之前**，语义属于整节而非反推支路 |

**注**：1152 公式仅 **2 句中文**，无 EN 对译——属 BL-V1-05C 双向异构，但与「入库」正交，先 A 再视 D2 浏览器复验。

### 3.4 并入 qa_022 · eval 连带影响（须同批更新）

[`eval_queries_ad5s.json`](../../eval_queries_ad5s.json) **`a14`** 当前：

```json
"category": "translated_group",
"note": "qa_022 answer_zh 为空、仅靠 EN→embedding；…"
```

**若** §十四引言并入 `qa_022.answer_zh`：

| 变化 | 说明 |
| --- | --- |
| 前提失效 | `answer_zh 为空` 不再成立 |
| 用例目的 | 原设计 = 压测 **翻译降级 / en_only embedding** 召回 |
| **须同批** | 更新 `a14` 的 `category` + `note`（例：改为验证「引言+公式 ZH 片段 + EN 原理段」混合 embedding） |
| 建议新增 | 1 条 **公式向** query（例：「并电阻功率怎么算 1152」）压测新入库片段 |

**结论**：可以并入，但 **禁止** 只改 `qa_groups` 不更新 eval 备注——否则后人跑 eval 会对不上。

---

## 4. URL 差集 · 14 vs 5（修订版）

先前 pandoc 全文 **~21** 可能含重复计数或 hyperlink 字段；**段落文本扫描**以 **14 unique** 为准。

### 4.1 已覆盖（5）

| URL | docx 归属 | qa_groups |
| --- | --- | --- |
| topens solar 博客 | qa_003 | qa_003 prose |
| Drive 短接视频 | qa_010 | qa_010 prose |
| amazon B08HYZV3DW | qa_023/024 | qa_023 prose + qa_024 ladder |
| amazon B01HMSR2T4 | qa_024 US 二极管 | qa_024 branch |
| amazon B07H33917Z | qa_024 UK 电阻 | qa_024 branch |

### 4.2 未覆盖（9）

| # | URL | docx 节 | 类型 | 归属判断 | 建议 |
| ---: | --- | --- | --- | --- | --- |
| 1 | `…/essential-guide-to-regular-maintenance…` | **§十九** | topens 博客 | orphan 节 | 简单档 · 随 §十九 入库 |
| 2 | `…/preventing-winter-freezing…` | **§十九** | topens 博客 | orphan 节 | 简单档 |
| 3 | `youtube.com/watch?v=IRIA5iaWHqE` | §十九 / §十六 | 视频 | orphan（两节各出现） | 简单档 · 节级各挂 1 次 |
| 4 | `…/how-to-retract-the-moving-rod…` | **§十五** | topens 博客 | orphan 节 | 简单档 · 需 §十五 先入库 |
| 5 | `…/troubleshooting-guide-motor-operates-but-gate-opener-arm-fails-to-move` | **§十五** | topens 博客 | orphan 节 | 简单档 |
| 6 | `youtu.be/0dkm1sKYjzA` | **§十七** | 视频 | orphan 节 | 简单档 |
| 7 | `youtu.be/5s1EQh2M_mo` | **§十七** | 视频 | 简单档 |
| 8 | `youtube.com/shorts/EeHaJdHqE-U` | **§十七** | 视频 | 简单档 |
| 9 | `amazon.co.uk/dp/B079KCC8P9` | **§十四 qa_024** | 采购 · UK 二极管 | **组已存在** · EN prose 有 · `links[]`/branch **无** | **复杂档补链** · 非 orphan |

### 4.3 按类型汇总

| 类型 | 未覆盖数 | 前置条件 |
| --- | ---: | --- |
| topens 博客 | 4 | §十九 / §十五 节级入库 |
| YouTube / youtu.be | 4 | 同上 + §十七 |
| Amazon 采购 | 1 | qa_024 UK branch 补 `B079KCC8P9`（**可独立于 orphan 修复**） |

### 4.4 是否值得结构化

| 档 | URL | 结论 |
| --- | --- | --- |
| **现在就能做** | #9 UK 二极管 | qa_024 branch 补 1 链；属 BL-V1-04 复杂档补全，非 full re-extract |
| **随 §十九 方案** | #1–2, #3 | 简单档 `links[]`；无 condition |
| **随 BL-EXT-01b** | #4–8 | 依赖 §十五/十七 节级入库；本轮可不夹带 |
| **维持现状** | 其余 10 个 orphan 节 | 无客户 query 压力则 **不批量扩库** |

---

## 5. 建议执行顺序（§1.3 补充后 · 待正式拍板）

```
0. ✅ 补看 BL-EXT-01b 九/十节 orphan 摘要（§1.3）— 确认非低价值内容
1. §十四引言 → qa_022 + 同批更新 eval a14 标注/备注（+ 可选公式 query）
2. §十九 补 2–3 H2（日常 / 深度润滑 / 维护链接）→ extract + 简单档 links + 浏览器
3. qa_024 补 B079KCC8P9（pilot overlay · 同 qa_024/008 流程）
4. BL-EXT-01b 登记排期（✅）— 注明「本轮只处理 §十四/§十九，其余 10 节+§十二 partial 暂缓」
```

**BL-EXT-01b 暂缓声明**：共性根因（`current_group is None` 丢弃）**未**因 §十四/§十九 patch 而解决；prod 仍缺 **~159 段** 可检索故障内容。

**仍禁止**：为补 URL 对 AD5S **全库 27 组 re-extract 并切 prod**。

---

## 6. 相关文档

- 上轮复核：[`ad5s_full_doc_review.md`](./ad5s_full_doc_review.md) §五–§六
- prod 状态：[`ad5s_complex_ladder_round_closure.md`](./ad5s_complex_ladder_round_closure.md)
- 排期：[`docs/排期.md`](../../docs/排期.md) BL-EXT-01

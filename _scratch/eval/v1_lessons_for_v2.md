# docx V1 线 · 方法论沉淀（V2 PDF·merge 启动必读）

**日期**：2026-07-05  
**状态**：docx V1 + V1.1 **已结案** · 供 **V2 PDF·merge** 线启动前阅读  
**性质**：判断方法论与 design principles — **不是**具体代码清单，也不是 docx 执行记录的重复  
**关联结案**：[`v1_docx_closure.md`](./v1_docx_closure.md) · [`docs/排期.md`](../../docs/排期.md)

---

## 怎么用本文

| 读者 | 建议 |
| --- | --- |
| **V2 PDF 线负责人** | 先读 §一「通用原则」；§二「docx 特有」仅作对照，**不要预先假设 PDF 也需要** |
| **写 overlay / patch / eval 脚本的人** | 重点看 §1.3 baseline、§1.5 批量摸底、§1.7 静默失败 |
| **设计 schema / 分支结构的人** | 重点看 §1.2 结构化 vs prose、§1.4 内容问题分类型 |

具体 bug 与执行留档仍查 `_scratch/eval/bl_*` / `phase_*` 系列；本文只保留**可迁移的判断逻辑**。

---

## 一、通用原则（PDF 线可直接复用）

### 1.1 页面/内容身份必须由 pipeline 权威下发

**原则**：`chunk_id` / `page_range` / `group_id` 等标识，**调用前**显式传入模型或写入 manifest；**调用后**做一致性校验，**不信任**模型自行推断的输出。

| 线 | 典型事故 | 根因 |
| --- | --- | --- |
| **PDF** | BL-PDF-04 duplicate / page 漂移 | 页码依赖 VLM 自报或两次调用各自推断 |
| **docx** | p1/p3 切片错乱 | chunk 身份在 extract 后段才「补猜」，无权威 parent |

**正确做法**

- manifest / adapter **在调用前**绑定身份（page_index、chunk_id、source_file）
- 输出落盘后 **gate 脚本** 校验：duplicate 计数、page_range 单调、parent/child 引用存在
- 模型输出中的页码/编号仅作 **hint**，不得覆盖 pipeline 已下发的 ID

**PDF 映射**：`renormalize_manual_chunks.py` + adapter gate 即此原则的具体化；V2 任何新 VLM 步骤都应继承同一模式。

---

### 1.2 结构化优先于 prose 解析 — 但先摸底，再决定要不要结构化

**原则**：能利用**原生或视觉权威结构**时，不要纯靠 regex 猜边界；但**看到分支词 ≠ 需要复杂 schema**。

| 线 | 结构化锚点 | 反面 |
| --- | --- | --- |
| **docx** | Word **Heading 样式** 定问答组边界 | 正文里的 `1.` / `If` 当 group 切分 |
| **PDF** | VLM 识别**表格/区块边界** | 页内 regex 抽参数表 |

**三分法（写 schema 前先答）**

| 语义 | 特征 | 结构选择 | docx 例证 |
| --- | --- | --- | --- |
| **互斥场景** | 客户**预先已知**走哪条（安装方向、US/UK） | `branches[]` + 筛选 | qa_024 步骤 3 |
| **顺序 escalation** | 所有人走同一梯，步骤 1→2→3 | `troubleshooting_ladder[]` | qa_008 ERM12 |
| **观察后跳转** | 「如果问题消失则…否则继续」 | 现有 ladder/branch **都可能不够** | §十六 DT、qa_037 |

**反面教训**：qa_037 / §十六 DT — 看到 `if`/分支词就套 branches，产生**误导性互斥 UI**。**宁可维持 prose**，也不强行套用装不下的结构。

**PDF 映射**：参数表 → structured；安装步骤叙述 → 先 prose + 摸底，再决定是否拆 ladder。

---

### 1.3 任何 overlay/patch 前先 snapshot baseline

**原则**：改之前先跑一次**现状**（eval JSON、probe 输出、manifest 计数）；改之后**对比 diff**，而不是事后口头断言「应该没回归」。

| 例证 | baseline 作用 |
| --- | --- |
| qa_024 镜像语义修复 | 改前 Top1/Top3 快照 → 证明「还是 qa_024」≠「没引入漂移」 |
| §十二 partial r12a/r12b | 改前/改后 eval 对比 → 分清 partial 引入 vs 原有问题 |
| TC148 T3 disambiguation | patch 前 5/6 → 后 6/6，t01–t05 **无回归** |

**没有 baseline 时**，「Top1 还是原来那个组」**没有证明力** — 可能是 confusable 组之间互换，或 rank#2/#3 已变。

**操作约定**

```text
1. 写 phase_*.py 时：STAMP 备份 qa_groups / manifest
2. 跑 eval → 固定 json-out 路径（*_baseline_eval.json / *_post_eval.json）
3. gate 脚本 assert 全量 query，不只测「本批 touched 组」
```

---

### 1.4 内容问题要分类型 — 不能用一把尺子

| 类型 | 症状 | 处理方向 | docx 例证 |
| --- | --- | --- | --- |
| **完全缺失** | orphan / grep 0 | 找回来、入库 | BL-EXT-01b §十四/§十九 |
| **存在但单薄** | thin-ZH、步内缺规格 | **先分清**：展示层补 EN vs 内容层 spot-fix 并进 `answer_zh` | V1-07 vs V1-05B qa_001 保险丝 |
| **角色错位** | 同组 ZH/EN 不是互译，是不同受众 | **结构隔离**，不是合并 | TC148 `customer_reply_template` |
| **结构装不下** | DT / 观察后跳转 | **维持原文 prose**，不硬套 schema | §十六 DT → F+prose |

**易混点**

- **规格缺口**（AD5S 型）：EN 步内多 ∅5×20mm / CR2025 → **必须并进主答案**，不可折叠隐藏
- **均衡组 EN 参考**（qa_001 · **qa_010** 型，2026-07-05 A3S 手测）：ZH 步骤完整但 EN 含额外规格/分支（保险丝、**电机 LOAD 测向**）→ demo **不宜全库双栏**；更合理为 **可折叠「英文参考」**（复用 TC148 `<details>` 交互）或 V1-05B 写回 `answer_zh` · 见 [`bl_v1_07_thin_zh_display.md`](./bl_v1_07_thin_zh_display.md) §后续
- **邮件模板**（TC148 型）：整篇 EN 客服稿 vs ZH 速记 → **独立字段 + demo 折叠**，不进 LLM
- **协商 offer**（qa_023）：一次性补偿话术 → **剥离** `negotiation_offers[]`，不进 LLM

摸底脚本：[`scan_en_email_template_scope.py`](./scan_en_email_template_scope.py)（体裁）· [`ad5s_zh_en_gap_scan.py`](./ad5s_zh_en_gap_scan.py)（规格缺口）— **不同维度，勿混扫**。

---

### 1.5 批量操作前先分类摸底 — 小批次、独立验收

**原则**：产出**可复现的分类依据**（规则 + 证据字段），不是「看起来是」；批次要小，每批独立 gate。

**docx BL-EXT-01b 可迁移方法**

- F / L / C / P / DT 五类 — **标签本身可换**，但流程值得保留：
  1. 全库扫描 → 每组标注 **证据来源**（grep / heading / 人工）
  2. 定批次 scope md（如 `bl_v1_05_scope.md`）
  3. 单批 overlay → chunk → embed → **该批 eval 子集 + 全量回归**

**PDF 映射**：52 页扩量前，先对 chunk 类型（参数表 / 步骤 / 警告框 / 配图说明）做同样意义的摸底，再定 batch。

---

### 1.6 新增内容必须全量 eval 回归

**原则**：任何 patch（question 改写、互斥标签、spot-fix）都可能让**未改动的组**检索漂移；**不能只测 touched 组**。

| 例证 | 教训 |
| --- | --- |
| qa_037 limit 域 | 改 question 后 a07 等 confusable query 漂移 |
| qa_037 二次 patch | 全量 47 条回归才抓到 side effect |

**最低门禁**：touched 组 eval **+** 全库 eval **+** confusable 邻域 query（eval json 里已有 category 的可优先跑）。

---

### 1.7 设计完成 ≠ 验证完成 — 三层分别验

| 层 | 验什么 | docx 留档范例 |
| --- | --- | --- |
| **数据层** | manifest 字段、extract 计数、duplicate | `verify_qa_023_acceptance.py` |
| **展示层** | demo UI、链接可点、分支筛选 | `bl_v1_07_browser_regression.py` |
| **LLM 路径** | 润色区有正文、语气不串、template 不进 context | `v1_handtest_llm_on_browser.py` |

**不能因为一层过了就默认全部过了。** 典型交叉点：V1-07 thin-ZH 补 EN × V1.1 `customer_reply_templates` — 必须显式处理 [`supplement_en_text`](../display_content_utils.py) 在有 template 时返回 `None`。

---

### 1.8 静默覆盖/丢弃是最危险的失败模式

**原则**：宁可 **显式报错 / structure_warnings**，也不要 dict 覆盖或无声 drop。

| 机制 | 防什么 |
| --- | --- |
| duplicate 检测（PDF-04） | 同页双 chunk 静默共存 |
| `structure_warnings[]` | extract 不确定时标记，demo 黄条 |
| adapter **打分择优**而非后者覆盖前者 | 语料完整性被 silently 替换 |
| overlay **STAMP 备份** | 无法回滚的 manifest 覆盖 |

**设计时默认**：新 pipeline 步骤输出「不确定」计数；gate 脚本 fail on regression，不 fail on warning 但须留档。

---

## 二、docx 特有 · PDF 不一定适用

> **启动 V2 时不要预先假设 PDF 也需要下列能力。** 若 PDF 线出现类似症状，再单独论证是否引入。

### 2.1 双语 ZH/EN 异构（BL-V1-05）

- docx troubleshooting：**中英非互译**，至少 A/B/C 三子模式（TC148 邮件稿 / AD5S 规格缺口 / 双向异构）
- **PDF manual 当前纯英文** → 大概率**用不上**整条 V1-05 线
- 若未来 PDF 含多语言层，先论证是「翻译对」还是「异构对」，再选 spot-fix vs 隔离

### 2.2 客服体裁识别

| 机制 | 适用范围 |
| --- | --- |
| `negotiation_utils` / BL-V1-06 | 一次性补偿 offer（qa_023） |
| `customer_reply_templates[]` | 整篇 EN 客服邮件 vs ZH 速记（TC148 **仅 2 组**） |

PDF 安装手册**不是**这种文体；**不要**为 PDF 预建 `content_role` 通用 schema。体裁摸底见 [`en_email_template_scope_scan.md`](./en_email_template_scope_scan.md)。

### 2.3 Word 原生 Heading vs PDF 视觉理解

| docx | PDF |
| --- | --- |
| Heading 1/2/3 即问答边界 | 无等价 native mark；靠 VLM + manifest |
| 图片跟 group 流顺序挂 | 图文 role、表格 structured 需视觉识别 |

**不能照搬**：docx 的 `qa_doc_extractor` 假设不可直接套 PDF；PDF 线技术路径本质是 **VLM + 权威 manifest**，不是「再写一个 extractor.py」。

---

## 三、docx V1 闭环索引（细节查原文，不在此重复）

| 主题 | 留档 |
| --- | --- |
| 结案总览 | [`v1_docx_closure.md`](./v1_docx_closure.md) |
| 手测 gate | [`v1_handtest_log.md`](./v1_handtest_log.md) |
| AD5S eval 基线 / known miss | [`bl_v1_03_execution_record.md`](./bl_v1_03_execution_record.md) · [`ad5s_eval_known_misses.md`](./ad5s_eval_known_misses.md) |
| 限位域 / 症状化 question | [`bl_v1_08_limit_domain_diagnosis.md`](./bl_v1_08_limit_domain_diagnosis.md) |
| 复杂 schema | [`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) |
| TC148 客服模板 | [`phase_tc148_customer_reply_template.py`](./phase_tc148_customer_reply_template.py) · [`en_email_template_scope_scan.md`](./en_email_template_scope_scan.md) |

---

## 四、V2 启动检查清单（摘自上文原则）

启动 PDF·merge 或新 ingest 批次前，逐项自检：

- [ ] **身份**：manifest 是否在调用前下发 page/chunk ID？gate 是否校验 duplicate？
- [ ] **结构**：是否先摸底再定 schema？互斥 / 顺序 / 观察跳转是否分清？
- [ ] **baseline**：patch 前是否有 eval/manifest 快照？是否对比 diff？
- [ ] **内容类型**：缺内容 / 薄内容 / 角色错位 / 结构装不下 — 是否走对了通道？
- [ ] **批次**：是否有可复现分类 + 小批独立 gate？
- [ ] **回归**：是否全量 eval，而非只测本批？
- [ ] **三层验证**：数据 / 展示 / LLM 是否分别有过 gate？
- [ ] **静默失败**：不确定时是否 warnings 或 fail loud？
- [ ] **不照搬 docx**：双语异构、客服体裁、Heading 切分 — 是否论证过 PDF 真的需要？

---

## 五、运维提醒（两线共有）

**qa_server 重启**：修改 `chroma_captioned/manifest.json` 或 re-embed 后，**必须重启**对应端口的 `qa_server.py` 进程，否则 demo 仍服务旧 in-memory manifest。docx 线此坑已多次踩（V1 手测、V1.1 LLM=on、TC148 customer_reply_template）。

---

*本文随 V2 线推进可增补 PDF 侧例证；docx 侧不再追加执行细节，以 `_scratch/eval/` 各 execution_record 为准。*

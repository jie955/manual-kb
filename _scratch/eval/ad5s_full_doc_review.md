# AD5S 全文复核（pandoc → markdown · ~2219 行）

**日期**：2026-07-03 · **源**：`samples/troubleshooting/AD5S-AD8S常见问题排查.docx`（用户 pandoc 全文）  
**对照**：`_scratch/run-ad5s/qa_groups.json`（**27 组**）· `chunks_captioned.json`

> **与单组截图结论的关系**：全文比截图复杂；下列发现按重要性排序，并已反哺 `docs/排期.md` § BL-V1-04 / BL-V1-05 / BL-V1-06。

---

## 一、§十四 电机电流小 · 双向信息不对称（⚠️ D2 需 re-review）

**Gate #5 [D2]**（query「门刚动一下就停 电机电流太小」）命中 **`qa_022`**（`answer_zh` **空** · `translation_status=fallback_to_english`），原判「无数值失真 ✅」→ **建议改为「⚠️ 需 re-review」**。

### 组边界（勿与单组 qa_022 混淆）

| group | 标题 | 在 pipeline 中的角色 |
| --- | --- | --- |
| **qa_022** | 电机电流小的原因 | ZH 空；仅 EN 原理段；D2 Top1 |
| **qa_023** | 并接机臂红黑线排查 | ZH 并接步骤；EN 含 Amazon 链 + **M12 抵电阻成本**协商话术 |
| **qa_024** | 手动反推来排查+电阻 | 长组 4 子块；ZH/EN **双向**缺口最集中 |

### 双向缺口（用户全文核对 · 对照 qa_groups.json）

**ZH 独有 · EN 无（用户 pandoc 全文）**

- 「先试 **50Ω**，不行再 **25Ω**」渐进电阻建议
- 选型公式：**负载电阻无规定电压，功率 > 1152÷R（Ω）**；20Ω–100Ω 均可

**⚠️ extractor 核实（2026-07-05 修订）**：上述 50Ω/25Ω/1152 公式位于 **§十四 H1 引言**（qa_022 H2 **之前**），为 **orphan 段落**被 `current_group is None` 丢弃——**非** qa_024 组内丢失。详见 [`bl_ext01_gap_inventory.md`](./bl_ext01_gap_inventory.md) §3。

**EN 独有 · ZH 无或极弱（qa_groups 已证实）**

- 两种故障方向的二极管极性逐步接线（阳极/阴极接 +Motor / Motor-，US/UK 各一套）— 见 qa_024 `answer_en`
- Amazon 采购链（US `B08HYZV3DW` / UK `B07H33917Z` 等，**6 条 URL 在 extract 层**）
- qa_023 EN：**「愿尝试可送两个 M12 遥控器抵电阻成本，可以接受吗？」** — 一次性客服协商，非通用政策

**ZH 有方向标签、EN 有逐步极性**：qa_024 ZH 有「拉开门开门不正常 / 推开门关门不正常」等 **方向分支标题**，但无 EN 级逐步接线；简单合并易 **缝合失败**。

### D2 再判

- 原「无数值失真」≈ **当次 LLM 输出未篡改 0.5–3A/<1A 等已展示数值**
- 未覆盖：**双向分支丢失**、协商话术误当政策、50Ω/1152 公式可能未入库
- **处理**：§十四 **qa_022/023/024 整节**标为 BL-V1-04 **复杂档** + BL-V1-05 **双向异构**；**禁止**同一版自动合并

---

## 二、qa_008 遥控距离不够 · 子模式 B 再次印证

| ZH | EN |
| --- | --- |
| 「更换遥控器电池试试」 | **65 feet** 开阔地范围；**2× CR2025**（3V 锂电） |

与截图推断的 **AD5S 型（骨架对齐、步内缺规格）** 一致，非孤例。

---

## 三、BL-V1-04 须分档 · AD5S 链接复杂度 ≫ TC148

### 规模对比

| 来源 | URL 数 | 构成 |
| --- | ---: | --- |
| **用户 pandoc 全文** | **~21** | YouTube×6 · topens 博客×4 · Amazon×4 · 等；含**地区/方向条件** |
| **`qa_groups.json`（当前 extract）** | **8** | topens×1 · drive×1 · amazon×6（qa_003/010/023/024） |

差集说明：大量 YouTube / 保养组链接等 **尚未进入 qa_groups**（与 §五、§六 同源问题）。

### 分档（已定）

| 档 | 范围 | schema | 试点 |
| --- | --- | --- | --- |
| **简单档** | 视频教程、topens 博客、Drive 短接视频；**无条件分支** | `links[]`：`url, label, lang, link_type` | **先做**：TC148 3 链 + AD5S qa_003/010 等 |
| **复杂档** | qa_023/024：链接 + 方向接线 + 地区链 + 客服话术纠缠 | 须 `condition`（如 `region: US\|UK`、`stall_direction: pull_open_fail_open`）或 **人工复核** | **不**与简单档同版自动合并 |

无 `condition` 时，自动化易把两种二极管接线 **缝成一份对不上的说明**。

---

## 四、客服协商话术 · 提取阶段过滤（BL-V1-06）✅ 2026-07-03

**典型原文**（qa_023 EN，过滤前）：

> …we do not have this resistor for sale in our store… If you are willing to try the resistor, we would like to send you two M12 remotes to cover the cost of the resistor. Is it acceptable?

- **性质**：真实邮件一次性协商，非 TOPENS 标准政策
- **实现**：`negotiation_utils.py` — **结构特征**（免责 `for sale in our store` + 征询式 `would like to send…Is it acceptable`），非 lone 关键词
- **落库**：`negotiation_offers[]` on group/chunk；**从 `answer_en` 剥离**；`build_context_block` 不送入 LLM
- **验证**（`run-ad5s-dry-v106`）：仅 **qa_023** ×1 条；`answer_en` 仍保留 `purchase the resistors` + 免责，**无** M12/acceptable
- **单测**：`tests/test_negotiation_utils.py` 3/3

---

## 五、「十九、保养与润滑」· 逐句中英交替 + extract 缺失

- **版式**：非「整段 ZH + 整段 EN」，docx 内 **zh:2 / en:27 / 翻转:3**——**非 heavy 逐句交替**；主因是 **零 H2 → 整节 29 段 orphan 未入库**
- **pipeline 现状**：`qa_groups.json` **无「十九」节任何组**（见 §1.2 缺口表）
- **待办**：补 H2 或 orphan 收集器 → extract → 抽查 3 翻转点。详见 [`bl_ext01_gap_inventory.md`](./bl_ext01_gap_inventory.md) §2

---

## 六、extractor 覆盖缺口（BL-EXT-01 · 全文 vs pipeline）

| 项 | pandoc 全文 | `qa_groups.json` |
| --- | --- | --- |
| URL 总数 | ~21（pandoc 估）· **段落扫描 14 unique** | **5 unique**（差 **9**） |
| §十九 保养与润滑 | 有（逐句交替） | **无组** |
| 50Ω/25Ω/1152 公式 | 用户称在 ZH | **qa_024 ZH 无**（grep 0） |
| Section 覆盖 | 十九、十五…等多节 | 仅 一/二/五/十/十一/十二/十四/二十 等 **27 组** |

**含义**：全文复核发现的部分问题，当前 chroma **根本无法检索到**——须先 extact 覆盖，再谈 links[]/合并。

---

## 七、建议试点顺序（已定）

1. **BL-V1-06** ✅ extract 已关（待合入 AD5S chroma 时随 extract 重跑）
2. **条件形态扫描**：[`ad5s_link_condition_scan.md`](./ad5s_link_condition_scan.md)（dry-v106）→ 再定复杂档 schema
3. **BL-V1-04 简单档**：TC148 ✅；AD5S 白名单简单组（非 §十四）

**禁止**：为赶进度把复杂档塞进与 TC148 同版的自动合并逻辑；**禁止**在未过 §十四 dry-run 前对 AD5S 全库重跑 links extract 覆盖 chroma。

---

## 九、BL-V1-04 dry-run · §十四（2026-07-03）

对 `AD5S….docx` 用**当前** `qa_doc_extractor`（含 TC148 试点版 `links[]`）写入 `_scratch/run-ad5s-dry-v104/`（**未覆盖** `run-ad5s/chroma`）。

| group | links 数 | 问题（相对用户全文要求） |
| --- | ---: | --- |
| qa_022 | 0 | 无 URL（符合）；双向内容在 023/024 |
| qa_023 | 1 | Amazon → 误标 `support_page`（应为 `purchase_link` + 免责 label）；**M12 协商话术仍在 `answer_en`**（未过滤） |
| qa_024 | 5 | **拍平列表**：US 电阻链重复 2 次；UK 链 label=裸 URL；**无 `condition`**（拉开门/推开门、US/UK 未区分）；二极管极性步骤仍在 prose |

**结论**：「裸 URL=0」对 §十四 **不足**——链接搬走 ≠ 客户知道点哪个。**复杂档**须 `purchase_link` + `condition`（或整组 `links_extract_mode=manual`）后再推 AD5S；**BL-V1-06** 与 **BL-V1-05** 并行，不由 V1-04 代劳。

---

## 八、Gate #5 日志修订

| ID | 原判 | 修订 |
| --- | --- | --- |
| **D2** | 浏览器 ✅ · 无数值失真 | **⚠️ re-review** · §十四双向异构；qa_022 空 ZH 降级路径；协商话术/条件链/公式入库待核实 |

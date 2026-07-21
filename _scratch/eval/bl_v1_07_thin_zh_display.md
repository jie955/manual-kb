# BL-V1-07 · thin-ZH 展示补充（2026-07-05）

**触发**：BL-EXT-01b Batch1 四组 qa_031–034 全部 EN-heavy（zh:en ≈ 1:5–1:21）；qa_028 N1 从 minor 升级为 **V1 完整门槛阻塞**。

**问题**：demo `content_zh || content_en` — zh 非空但过薄时 **不展示 EN** → 检索命中但客户可见信息量仅 5%–20%。

**与 V1-05 关系**

| 层 | 项 | 说明 |
| --- | --- | --- |
| **BL-V1-07**（本项） | 展示 + LLM 上下文 | 通用规则：`is_thin_zh()` → 主面板 ZH + **EN 补充块** |
| **BL-V1-05B**（并行） | extract 合并 | 把 EN 步内规格/步骤写回 `answer_zh` — 体验更完整，但不阻塞继续 ingest |

**判定**（v2 · [`display_content_utils.py`](../display_content_utils.py) · 全库扫描 [`thin_zh_scan_ad5s.md`](./thin_zh_scan_ad5s.md)）

- 初版 zh/en<25% 误触 30/34 → **已废止**
- 现用：极短(80/3×) / 极端比例(8%) / 编号步骤不足 / compact 多步短 zh(150/800/15%)

**Gate 验收清单**：[`bl_v1_07_gate_verification.md`](./bl_v1_07_gate_verification.md)

**改动**

- `demo/index.html`：`renderFlatBody` · 标签「英文操作步骤（中文正文过短…）」
- `generate_answer.py`：`build_context_block` 附 EN（≤2000 字）
- `tests/test_display_content_utils.py`

**验收**（Batch2 前）

- [x] b01–b04 + N1（qa_028）浏览器：主面板可见 EN 补充块 · [`bl_v1_07_browser_regression.py`](./bl_v1_07_browser_regression.py) 8/8
- [x] qa_001 / qa_022 等均衡组：**不**误触发 EN 块
- [x] qa_016 install_mode：`extreme_ratio` 触发合理 · 不加 rule 3 豁免

**Batch2 gate**：✅ 2026-07-05 · 留档 [`bl_v1_07_gate_verification.md`](./bl_v1_07_gate_verification.md)

---

## 后续 · 均衡组 EN 展示（2026-07-05 · A3S 手测 qa_001）

**现象**：qa_001 等 **非 thin-ZH** 组（中文 4 步完整）→ demo 主面板 **仅 ZH**；`answer_en` 在 prod 含 11#/12# 端子、保险丝规格、36V/24V 12Ah 等 **ZH 未写全的细节**，手测对照 docx 双语时不可见。

**结论（产品方向 · 待立项，非 V1-07 范围）**：

| 方案 | 说明 |
| --- | --- |
| ❌ 全库双栏 EN | 语言混排、占屏；与「主面板中文排查」目标不符 |
| ✅ **可折叠「英文参考」** | 默认折叠；供客服核对/转发 docx 英文原文与规格细节；**qa_011 等长组**折叠区内再分 **「太阳能 / 适配器+电池」** 子段；**不**替代主步骤区 |
| ✅ **TC148 型折叠区** | 已有 [`demo/index.html`](../../demo/index.html) `customerReplyWrap` / `<details>` 模式；故障排查组可复用交互，文案改为「英文操作步骤原文（供核对）」 |

**与现有项关系**：

- **BL-V1-07**：继续只管 **thin-ZH** 自动补 EN 块；**不**扩到 qa_001 等均衡组。
- **BL-V1-05B**：内容层把 EN 规格写回 `answer_zh` — 与展示层折叠 **可并行**，不互斥。
- **手测核对**：均衡组 docx 双语对照 → 查 `qa_groups.answer_en` 或（实现后）展开 demo 英文参考区。

**触发记录**：A3S 18 H1 理解 A 手测 · §一 qa_001 · §二 qa_010 · §三 **qa_011**（长组+配图 · EN 分岔仅 prod）· 检索/中文/配图 PASS · EN 宜折叠。

**与 V1-07 分界**：

| 类型 | 示例 | demo 行为 | 期望 |
| --- | --- | --- | --- |
| **thin-ZH** | qa_005/006/007/008 | 自动 **EN 补充块**（展开） | 保持 |
| **均衡/中长 ZH** | qa_001 · qa_010 · **qa_011** | **无 EN** | **可折叠「英文参考」** · qa_011 两段子场景 · **Drive → COMPLIANCE-011** |

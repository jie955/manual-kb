# BL-EXT-01b · Batch 7 验收清单（§十六 · DT → F+prose）

**范围锁定**：Batch7 **仅** §十六 **35 段 orphan** → **qa_043**（1 H2 · F+prose）· **BL-EXT-01b 最后一节**  
**设计决策**：[`bl_ext01b_sec09_sec16_verification.md`](./bl_ext01b_sec09_sec16_verification.md) · Tag **DT**（入库走 F · **禁止** attach ladder）  
**上一批**：[`bl_ext01b_batch6_execution_record.md`](./bl_ext01b_batch6_execution_record.md)

---

## DT 设计结论（Batch7 前定稿 · 2026-07-05）

| 选项 | 结论 |
| --- | --- |
| **A** `decision_points[]` 新 schema | **拒绝** — 全库 orphan 仅 §十六 需 DT · V1 性价比不足 |
| **B** demo 正则高亮 | **不做** — ZH/EN 混排 + 1./5. 跳号 · 正则 brittle |
| **C** `decision_hints[]` 手填 | **ingest 后可选** — 非 Batch7 阻塞 |
| **默认** | **F+prose overlay** · `structure_warnings: ["dt_prose_only"]` · 防后人误 attach ladder |

### 展示路径 · 风险显式声明

「不必做展示层区分」**≠ 零误读风险**：

| 路径 | 行为 | 风险 |
| --- | --- | --- |
| **默认（无 LLM）** | demo `renderFlatBody` · 原文 prose 含「无异响→步骤2；有异响→步骤5」 | 客户**可能**把全文读成顺序必做 · **风险可接受、非零** — 取决于排版与阅读习惯 |
| **勾选 LLM 润色** | `generate_answer` 读 hits prose | 较易产出「有异响直接看步骤5」类跳转语义 · **仍须 spot-check** |

> 原则：不把「风险可接受」包装成「没有风险」（同 P 类 baseline、BL-V1-08 legacy 观察项写法）。

---

## 禁止项（Batch7 · 违反即失败）

- [ ] **禁止** attach `troubleshooting_ladder`（线性全列会误导 2–4 为必做）
- [ ] **禁止** 按 L-scenario 拆多 H2 冒充「两场景」（DT 跳转在**同一排查流**内）
- [ ] **禁止** 用 `branches[]` + `applies_when` 表达「步骤1观察结果」（非预先 ctx）

---

## 验收项（Batch7 完成后 · 全部须过）

### A. 入库正向

- [ ] orphan **35 段**全部进入 **qa_043**
- [ ] `structure_warnings` 含 **`dt_prose_only`**
- [ ] `troubleshooting_ladder` **为空/不存在**
- [ ] links[] 含 YouTube（简单档 · BL-V1-04）
- [ ] `eval_queries_ad5s.json` 新增 **b13/b14** · 各 **Top1**

### B. 检索回归

- [ ] a01–b12 · r12a/r12b · **Top1 不低于** Batch6 基线（**32/32+** → 目标 **34/34** 含 b13/b14）

### C. DT spot-check（**两条独立** · 不可合并为「LLM/原文测一次」）

**探针 query 建议**：「机臂按遥控有异响 离合打开还有声音」（应命中 qa_043 · 走「有异响→步骤5」语义）

| # | 路径 | 操作 | 通过条件 |
| ---: | --- | --- | --- |
| **C1** | **无 LLM** | `POST /api/ask` · `use_llm: false` · 浏览器 demo **不勾选** LLM | ① Top1=qa_043 ② `content_zh` **保留**「有异响→…步骤5」原文 ③ **不出现**编辑过的「请依次完成步骤2–4」类**新增**误导句（原文箭头保留即可）④ 记录：prose 完整可见 · **承认**客户仍可能误读为顺序 — 记入执行记录 |
| **C2** | **有 LLM** | 同 query · `use_llm: true` · 浏览器 **勾选** LLM | ① Top1=qa_043 ② `generated_answer` **应**体现跳转（如「有异响/directly to step 5/直接步骤5」）③ **不得**写「请按顺序完成步骤2、3、4」或等价表述 |

### D. 运维

- [ ] embed 后 restart qa_server · health + qa_043 content 非空

---

## 开工前检查

- [x] DT 设计讨论定稿（F+prose · 拒绝 A · C 可选）
- [ ] 脚本：`phase_bl_ext01b_batch7_overlay.py` · stamp `bl-ext01b-b7`

---

## 参考

- 核实附录 §2：[`bl_ext01b_sec09_sec16_verification.md`](./bl_ext01b_sec09_sec16_verification.md)
- 分类 Batch7：[`bl_ext01b_classification.md`](./bl_ext01b_classification.md) §建议批次

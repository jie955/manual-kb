# BL-EXT-01b · §九 / §十六 原文核实（2026-07-05）

**触发**：「本批无 C 类」若仅以 grep `amazon.com/co.uk` 判定，可能漏判/误标；§十六「无异响→步骤5」与 qa_024 `stall_symptom` 语义相近但结构不同。

**方法**：通读 docx orphan 全文，对照 [`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) §3–4。

---

## 1. 判定标准修正（写入分类表）

| 标签 | 定义 | **不是** |
| --- | --- | --- |
| **C** | 用户**预先已知**互斥上下文（`install_mode` / `stall_symptom` / `region` 等），`branches[]` + `applies_when` 过滤展示；采购链可有可无 | ≠「有 if 就算 C」；≠「无 amazon 就一定不是 C」 |
| **L** | **线性**顺序梯：步骤 1→2→…→n 依次执行；`troubleshooting_ladder` 全展示按 `step_index` | ≠ 任意决策树 |
| **DT** | **观察后跳转**决策树：做完某步、**观察现象**后跳至非相邻步骤（如 1→5 跳过 2–4） | ≠ C（非预先已知维度）；线性 L **会误导** |
| **F** | 顺序步骤 prose，无 attach ladder | |
| **P** | partial · 已有组 + orphan 子场景 | |

**旧盲区**：用 amazon URL 作 C 的**充分条件** — 错；应作**有链接时的辅助信号**之一。

---

## 2. §十六 · 机臂声音异常（35 段 orphan）

### 2.1 原文决策结构（ZH 核心）

```
1. 打开离合，按遥控器，看是否还有异响？
   无异响 → 做步骤 2
   有异响 → 异响来自电机或离合，做步骤 5    ← 非相邻跳转

（步骤 2–4 为中间观察分支，非线性 1→2→3→4→5）

5. 拆开外壳…确认异响来自哪里？
   离合凸轮刮擦 → 加润滑脂
   电机内部 → 更换齿轮箱
```

EN（L17–19）：`If the noise disappears → Step 2` · `If the noise remains → go directly to Step 5`。

### 2.2 (a) vs (b) 结论

| 问题 | 结论 |
| --- | --- |
| 用户是否**提前知道**「有没有异响」？ | **否** — 需执行步骤 1 **后观察**才分支 |
| 类似 qa_024 `stall_symptom`？ | **语义同类**（互斥路径），**结构不同**（观察结果 vs 安装/走停预先上下文） |
| 属 (a) 观察后跳转 还是 (b) 标准 branches？ | **(a) 观察后跳转** → 标 **DT**，**不标 C** |

### 2.3 现有 schema 能否表达 1→5 跳过？

| 机制 | 能否表达 | 说明 |
| --- | :---: | --- |
| `troubleshooting_ladder` 线性全展示 | **否** | schema §3.1 + demo `renderLadderHtml` 按 `step_index` **依次列出全部步骤** |
| `branches[]` + `applies_when`（qa_024） | **不适用** | 注册维度无「步骤 N 观察结果」；语义是 ctx 过滤非逐步跳转 |
| `ladder_utils._is_consecutive_ladder` | **否** | 要求 1..n 连续；原文显式编号仅 **1.** 与 **5.** |
| **F 路径**（prose 保留 → 箭头） | **能** | 不 attach ladder — **当前最安全默认** |
| 未来扩展（`observation` / `goto_step`） | 待设计 | 批次 7 前需 **DT pilot** |

### 2.4 分类修订

| 字段 | 原值 | **修订** |
| --- | --- | --- |
| process_tag | L | **DT** |
| suggested_pipeline | attach ladder | **DT pilot** → 优先 F prose 或扩展 schema |

---

## 3. §九 · 走停或反弹（21 段 orphan）

### 3.1 结构

**主干 1–6**：红外 → FORCE/SOFT STOP → 单臂隔离 → 离合手推 → 脱门测臂 → 发视频。

**附录**：测电压/180°；「不带门伸出就反弹」→ 离合测电机 / 24V 直连 — 均为 follow-up，**非** pull/push 或 open/close 互斥 branch。

### 3.2 分类修订

| 字段 | 原值 | **修订** |
| --- | --- | --- |
| process_tag | L | **F** |
| process_evidence | if 多 → L | 1–6 顺序 escalation；无 applies_when 维度 |

**结论**：§九 **非 C**；原 L **偏高** → **F**。

---

## 4. 「本批无 C 类」修订表述

- ✅ 本批 orphan **无 qa_024 式 C**（无预先 ctx + branches 采购链结构）
- ❌ 撤回「本批无复杂结构」— §十六 为 **DT**
- ❌ 废止 grep amazon 作为 C 判定主依据

**修订 tag 计数**：**F×7 · DT×1 · P×1 · C×0**（§十五/十七 暂保留 **L-scenario** = 两场景拆 H2 的线性多段，批次 4/6 前再快读）

---

## 5. BL-V1-02

`eval_queries.json` v2 = **设计完成 28/28**；embed eval **未跑** → **验证待办**，不可标收口。

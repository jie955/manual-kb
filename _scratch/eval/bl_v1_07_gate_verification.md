# BL-V1-07 · Gate 验收前核实（2026-07-05）

## 1. 阈值全库扫描（必做 ✅）

**脚本**：[`scan_thin_zh_ad5s.py`](./scan_thin_zh_ad5s.py) → [`thin_zh_scan_ad5s.json`](./thin_zh_scan_ad5s.json) · [`thin_zh_scan_ad5s.md`](./thin_zh_scan_ad5s.md)

### v1 规则问题（已废止）

初版 `zh/en < 25%` → **30/34 组误触**，含 qa_001/qa_004/qa_010 等 ZH 步骤完整组。

### v2 规则（当前）

| # | 条件 | 典型 |
| ---: | --- | --- |
| 1 | zh 空 | qa_030 |
| 2 | zh < 80 且 en > 3×zh | qa_028, qa_031 |
| 3 | en ≥ 200 且 zh/en < **8%** | qa_016–019（限位 EN-heavy） |
| 4 | 编号步骤 **< 3** 且 en ≥ 400 且 zh < 250 | qa_033, qa_034 |
| 5 | 步骤 **≥ 3** 但 zh < **150** 且 en ≥ 800 且 zh/en < **15%** | **qa_032** |

**v2 结果**：**20/34 thin** · **14/34 不触发**

### Batch1 + 边界验收矩阵

| group | zh | en | ratio | thin | reason | 预期 |
| --- | ---: | ---: | ---: | :---: | --- | --- |
| qa_031 | 59 | 1235 | 0.05 | ✅ | short_zh | batch1 |
| qa_032 | 123 | 1013 | 0.12 | ✅ | compact_steps | batch1 |
| qa_033 | 201 | 1070 | 0.19 | ✅ | few_steps(2) | batch1 |
| qa_034 | 119 | 1220 | 0.10 | ✅ | few_steps(2) | batch1 |
| qa_028 | 7 | 241 | 0.03 | ✅ | short_zh | N1 |
| **qa_001** | 157 | 1074 | 0.15 | ❌ | — | **不误触** |
| **qa_022** | 278 | 482 | 0.58 | ❌ | — | **公式合并后不误触** |
| qa_014 | 476 | 1232 | 0.39 | ❌ | — | 长 ZH |
| qa_010 | 620 | 3345 | 0.19 | ❌ | — | 长 ZH 多步 |

### 仍触发但非 batch1 的 thin 组（19 组中其余 15 组）

多为 **短 ZH / 极端比例 / 步骤不足** — 与 V1-05B 长期合并目标一致；**展示层补 EN 对它们也有益**，但不作为 Batch2 gate 的否定条件。

### qa_016–019（install_mode · extreme_ratio）— **产品决定 ✅**

**结论**：维持 rule 3 触发，**不加** steps 豁免。

**理由**（2026-07-05 定稿）：

- 与 qa_024 install_mode 同语义维度：拉/推开门安装，安装细节主要在 EN。
- **步骤数量 ≠ 内容详尽度** — 与 qa_032 rule 5（compact_steps）同一原则；4–5 步但每步极短时，主面板仅 ZH 仍残缺。
- 浏览器验收「拉开门安装」→ qa_016：5 步 ZH + labeled EN 块 + 配图正常（见 [`screenshots/bl_v1_07/install_pull.png`](./screenshots/bl_v1_07/install_pull.png)）。

---
## 2. LLM 生成层 vs 展示层（必区分）

| 路径 | 客户看到什么 | BL-V1-07 覆盖 |
| --- | --- | --- |
| **默认（不勾选 LLM）** | demo 主面板 `renderFlatBody` | ✅ ZH + labeled EN 补充块 |
| **勾选 LLM 润色** | `generated_answer` 替换/补充主答案区 | ⚠️ 依赖 context + prompt |

### Context 已注入 EN（thin 时）

`build_context_block` 在 thin 时追加：

`英文操作步骤（中文过短，须参考）：\n{en[:2000]}`

**qa_031 实测**（manifest）：context 含 EN 补充段 · 总长约 **zh 摘要 + 2000 字 EN 上限**。

### Prompt 已加强（2026-07-05）

`QA_SYSTEM_PROMPT` 新增：

> 若参考资料含「英文操作步骤（中文过短，须参考）」段落，**须将其要点译入中文排查步骤**，不得仅复述已有的一句中文摘要。

### 验收分工

| 检查项 | 方法 | 状态 |
| --- | --- | --- |
| 无 LLM 主面板 | 探针 [`bl_v1_07_display_probe.py`](./bl_v1_07_display_probe.py) Top1 + `is_thin_zh` | **7/7 PASS** |
| 无 LLM 不误触 | a01「控制板灯不亮」→ qa_001 thin=False | **PASS** |
| **有 LLM** | b03 + `use_llm`：生成含 DIP/配件/断开等 EN 侧细节 | **PASS**（2026-07-05） |
| 浏览器目视 | Playwright [`bl_v1_07_browser_regression.py`](./bl_v1_07_browser_regression.py) | **8/8 PASS**（2026-07-05） |

**浏览器验收**（2026-07-05 · 须 **重启 qa_server** 后跑 — 旧进程 manifest 未刷新会导致 batch1 组 content 空）

| id | 检查点 | 结果 |
| --- | --- | --- |
| b01–b04 | ZH `pre.steps` + 虚线框 EN 块 + label | ✅ |
| N1 | qa_028 极短 ZH + EN 块 | ✅ |
| install_pull | qa_016 extreme_ratio + EN 块 + 配图 | ✅ |
| a01 / a14 | 无 EN 块 | ✅ |

截图：[`screenshots/bl_v1_07/`](./screenshots/bl_v1_07/)

**探针结果**（2026-07-05）

```
b01 qa_031 short_zh_3x_en PASS
b02 qa_032 compact_steps(4)_long_en PASS
b03 qa_033 few_steps(2)_long_en PASS
b04 qa_034 few_steps(2)_long_en PASS
a01 qa_001 thin=False PASS
a14 qa_022 thin=False PASS
N1  qa_028 short_zh_3x_en PASS
```

**LLM b03 摘要**：生成 777 字中文步骤，含「断开有线配件」「DIP开关#2」「自动关门」等 EN 原文要点，非仅复述 2 行 ZH。

---

## 3. Batch2 gate 定义（修订）

**通过条件**（全部 ✅ · 2026-07-05）：

1. v2 全库扫描 ✅（本文 §1 · [`thin_zh_scan_ad5s.md`](./thin_zh_scan_ad5s.md)）
2. 展示层探针 7/7 ✅（[`bl_v1_07_display_probe.py`](./bl_v1_07_display_probe.py)）
3. LLM b03 吸收 EN ✅（见 §2）
4. 浏览器目视 8/8 ✅（[`bl_v1_07_browser_regression.py`](./bl_v1_07_browser_regression.py)）

**→ Batch2 可恢复**（§十三 + 一个机臂 · F×2）。

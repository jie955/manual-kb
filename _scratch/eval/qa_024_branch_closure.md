# qa_024 复杂档闭环记录（BL-V1-04 · ladder + branch）

**日期**：2026-07-03  
**状态**：**pilot + 浏览器闭环 ✅** · **prod 阶段 1（qa_024）+ 阶段 2（qa_008）已切换 ✅** · 混合态 M1–M3 ✅  
**权威 schema**：[`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) §4–§5、§7.4

---

## 1. 背景与问题

qa_024（§十四 · 走停加电阻/二极管）原文用 **「主标题 + 括号镜像」** 表达同一套接线内容的两个等价筛选入口，例如：

`拉开门开门不正常加二极管电阻 （推开门关门不正常）`

首版 extract 将 2 行 ZH × 2 条镜像路径物化为 **4 条独立 branch**（仅 `applies_when` 不同），导致：

- 无筛选或只选 `region` 时出现重复卡片；
- demo 标签（单侧路径）与 `content_zh`（整行含主标题）视觉矛盾；
- 配图挂在 group 根级，筛选 US 仍展示 UK 方向图（027）。

**AD5S 全文检索结论**：括号镜像句式 **仅 qa_024**；qa_014/016–021 等为并列 prose、组级拆分或顺序子节，需各自 detector，**不**复用本套逻辑。

---

## 2. 实现清单（已完成）

| 层 | 文件 | 内容 |
| --- | --- | --- |
| **Schema** | `troubleshooting_schema_v1.md` | §4.2 `applies_when_any`（OR）；§5 组合语义；§7.4 **2 条** branch |
| **Extract** | `branch_utils.py` | `branch_matches` / `filter_branches` / `collect_ladder_branch_images`；`build_qa_024_ladder` 收成 **2 branch**；branch 级 `images` |
| **Demo** | `demo/index.html` | `branchMatches`；双向标签 `⇄`；`content_en`；配图按可见 branch 过滤；无筛选时配图区提示文案 |
| **测试** | `tests/test_branch_utils.py` | 9 用例（4→2、无筛选 2 张、US 单卡、US 不含 027、截图场景等） |
| **验收脚本** | `_scratch/eval/verify_qa_024_acceptance.py` | 四项自动化验收（不依赖浏览器） |

### 2.1 qa_024 步骤 3 数据结构（pilot 权威）

**2 条 branch 记录**（内容条数），每条 `applies_when_any` 含 **2 组** install/stall 镜像路径：

| branch | `applies_when.region` | `applies_when_any`（OR） | `content_en` 接线 | `images` | 采购链 |
| --- | --- | --- | --- | --- | --- |
| US | `US` | pull_open+open_abnormal ⇄ push_open+close_abnormal | anode → **+Motor** | 026, 028 | amazon.com 二极管 |
| UK | `UK` | pull_open+close_abnormal ⇄ push_open+open_abnormal | anode → **Motor-** | 027, 029 | amazon.co.uk |

步骤 3 另有 **1 条** 通配电阻链（`applies_when: { region: US }` only）。  
合计采购链：**3**（1 电阻 + 2 二极管），非旧版 5 链平铺。

### 2.2 括号镜像检测器范围

- `BRANCH_TITLE_RE` + `PAREN_MIRROR_RE`：**qa_024 专用**（`加二极管电阻` 句式）
- Schema `applies_when_any`：**通用 OR 原语**，供未来同类写法复用

---

## 3. Pilot 流水线

```powershell
cd d:\pythonProject\manual-kb

# 1. extract（含 ladder + qa_024 branch）
$docx = (Get-ChildItem "samples\troubleshooting\AD5S*.docx" | Select-Object -First 1).FullName
python qa_doc_extractor.py $docx "_scratch/run-ad5s-dry-ladder"

# 2. chunks
python chunk_builder.py "_scratch/run-ad5s-dry-ladder/qa_groups.json" "_scratch/run-ad5s-dry-ladder/chunks_out"

# 3. embed（bge-m3，约 1min）
python embed_ingest_local.py "_scratch/run-ad5s-dry-ladder/chunks_out/chunks.json" "_scratch/run-ad5s-dry-ladder/chroma_pilot"

# 4. demo
python qa_server.py --chroma-dir _scratch/run-ad5s-dry-ladder/chroma_pilot `
  --images-dir _scratch/run-ad5s-dry-ladder/images --port 8766
```

**入库前必查**（§2-pre）：

```powershell
rg "structure_warnings" _scratch/run-ad5s-dry-ladder/qa_groups.json
rg "stall_branch_align_failed" _scratch/run-ad5s-dry-ladder/qa_groups.json
# 期望：无匹配
```

**单元测试 + 四项验收**：

```powershell
python -m unittest tests.test_branch_utils -v
python _scratch/eval/verify_qa_024_acceptance.py
```

---

## 4. 四项验收结果（2026-07-03）

| # | 场景 | 期望 | 实测 | 结果 |
| --- | --- | --- | --- | --- |
| 1 | `ctx={}` | 2 张 branch 卡片 | 2 | ✅ |
| 2 | `region=US` | 1 张（非重复 content） | 1 | ✅ |
| 3 | `push_open+close_abnormal+US` | 标签/正文/接线一致 | 1 张；标签 `拉开门·开门不正常 ⇄ 推开门·关门不正常 · 美国`；`content_zh` 含括号镜像句；`content_en` 含 `+Motor` | ✅ |
| 4 | `region=US` 配图 | 无 027 | `['image_026.png', 'image_028.png']` | ✅ |

`verify_qa_024_acceptance.py` 输出：`RESULT: PASS`  
`tests.test_branch_utils`：**9/9 OK**

### 4.1 边界（同原则，已测）

| 场景 | 期望 | 实测 |
| --- | --- | --- |
| `stall_symptom=close_abnormal`（仅走停） | 2 张（两套不同接线内容各命中一条路径） | ✅ |
| 检索 query `走停加电阻 二极管怎么接` | Top1 qa_024；step3 `len(branches)==2`；含 `applies_when_any` | ✅（pilot manifest） |

### 4.2 浏览器验收（D2b · 2026-07-03）

**环境**：`qa_server.py --chroma-dir _scratch/run-ad5s-dry-ladder/chroma_pilot --images-dir _scratch/run-ad5s-dry-ladder/images --port 8766`  
**Query**：`走停加电阻 二极管怎么接`  
**筛选器**：推开门 · 关门不正常 · 美国

| 检查项 | 期望 | 实测 | 结果 |
| --- | --- | --- | --- |
| Top1 | qa_024 | qa_024 | ✅ |
| 步骤 3 branch 卡片 | **1** 张（US，非 UK） | 1 | ✅ |
| 分支标签 | `拉开门·开门不正常 ⇄ 推开门·关门不正常 · 美国` | 一致 | ✅ |
| `content_zh` | 含 `拉开门开门不正常…（推开门关门不正常）` | 一致 | ✅ |
| `content_en` | anode → **+Motor** | 含 `+Motor` | ✅ |
| 步骤 4 | 遇阻力调大说明可见 | 可见 | ✅ |
| 配图 | **026 + 028**，无 027/029 | 026 接线图（+MOTOR- 极性）；028 万用表串联测流 | ✅ |
| 采购链 | US 电阻 + US 二极管 | 电阻链 + 兼容二极管链 | ✅ |

**说明**：右侧「检索依据」故意以 `ctx={}` 展示完整 ladder（可仍见 UK 分支或链接单侧标签）；**以左侧「回答」区为准**。

### 4.3 prod 阶段 1 自动化复验（2026-07-03）

| 检查项 | 结果 |
| --- | --- |
| `verify_qa_024_acceptance.py`（`AD5S_QA_GROUPS=run-ad5s/qa_groups.json`） | PASS |
| `eval_queries_ad5s.json` | **15/15** Top1 |
| probe `走停加电阻 二极管怎么接` | Top1 **qa_024** 0.66；step3 **2** branch；US 筛选 **1** 卡；配图 **026+028** |
| 浏览器 prod `:8765` D2b（无筛选） | **✅** Top1 0.6565 · 2 branch ⇄ · 4 图+提示 · 步骤4 · 3 链 |
| 浏览器 prod 有筛选（推开门·关门不正常·美国） | **✅** 左栏 1 US 卡 · +Motor · 026+028 无027 |

---

## 5. Demo 展示约定

| 用户操作 | branch 卡片数 | 配图 |
| --- | --- | --- |
| 三项筛选器均未选 | **2**（US/UK 各一套内容） | 4 张 + 提示「含两种接线方向…」 |
| 仅选 `region=US` | **1** | 026, 028 |
| 全选（截图场景） | **1** | 026, 028 |
| 分支标签 | `applies_when_any` 存在时 **⇄** 双向路径 + region | — |
| 分支正文 | `content_zh` + **`content_en` 接线段** | — |

---

## 6. 未做 / 下一步

| 项 | 说明 |
| --- | --- |
| prod 切换 | **阶段 1 完成**（2026-07-03）：外科 overlay qa_024 → `run-ad5s/chroma_captioned`；eval **15/15**；见 [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §阶段 1 执行记录 |
| 复用到其他组 | **不建议**；qa_014/020 等需独立 detector |
| `generate_answer` | LLM 上下文尚未结构化使用 ladder/branch |
| BL-EXT-01 | ZH 独有 50Ω/1152 公式等仍未入库 |

---

## 7. 相关文档

- [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) — prod 切换范围、门禁、回滚

- [`demo_checklist.md`](./demo_checklist.md) §2-pre、D2b  
- [`ad5s_link_condition_scan.md`](./ad5s_link_condition_scan.md) §B qa_024  
- [`docs/排期.md`](../../docs/排期.md) § BL-V1-04 复杂档

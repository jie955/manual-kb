# docx 三库 Demo 测试清单

**更新**：2026-07-03 · 配套 [`docs/排期.md`](../../docs/排期.md) Gate #5

> **与 `eval_run.py` 的区别**：eval 只测**检索层** Top1/Top3；本清单测 **demo 端到端**（检索 + 可选 LLM 生成 + 配图渲染 + 越界行为）。

---

## 用法

1. **三库一 UI**（2026-07-05）：同页型号下拉切换库；须**同时**起三个 `qa_server`（端口见下）
2. 浏览器打开任意一个实例（推荐 A3S `:8765`），用顶部 **型号库** 下拉切换
3. **客户演示模式**：勾选「LLM 润色」——未勾选时主面板仅展示 Top1 手册原文
4. 留档 → `_scratch/eval/demo_qa_log.md` 或 [`v1_three_lib_handtest_log.md`](./v1_three_lib_handtest_log.md)

### 启动命令（三库一 UI · 固定端口）

```powershell
cd d:\pythonProject\manual-kb
$env:TRANSFORMERS_OFFLINE = "1"
$M = "_scratch/modelscope/BAAI/bge-m3"

# A3S · :8765
python qa_server.py --chroma-dir _scratch/run-007/chroma_captioned --images-dir _scratch/run-006/images --model $M --port 8765

# AD5S · :8766
python qa_server.py --chroma-dir _scratch/run-ad5s/chroma_captioned --images-dir _scratch/run-ad5s/images --model $M --port 8766

# TC148 · :8767
python qa_server.py --chroma-dir _scratch/run-tc148/chroma_captioned --images-dir _scratch/run-tc148/images --model $M --port 8767
```

> re-embed 后须**重启**对应端口进程。UI 通过 `http://127.0.0.1:{8765|8766|8767}` 跨端口调用 `/api/ask`（CORS 已开）。

### 单库模式（旧）

每次只起一个 `qa_server` 时，型号库下拉仍可用，但未启动的库会显示「未就绪」。

---

## Layer R · 检索（自动化，Gate #2）

| 型号 | 通过线 | 当前基线 |
| --- | --- | --- |
| A3S | Top1 **18/18** | ✅ `eval_queries.json` |
| AD5S | Top1 **≥14/15** | ✅ **15/15** · `_scratch/run-ad5s/eval_topk.json` |
| TC148 | Top1 **≥5/6** 且 Top3 **6/6** | ✅ **5/6** + **6/6** · `_scratch/run-tc148/eval_topk.json` |

未达标 → 先调检索，不进本清单客户验收。

---

## 1. A3S-A5S-A8S（`run-007/chroma_captioned`）

### 1a. 正常 query（验证 demo 与 eval 一致）

| # | Query | 预期方向 |
| --- | --- | --- |
| A1 | 适配器供电 灯不亮 | 电源相关故障 |
| A2 | 太阳能充不进电池怎么办 | 太阳能充电问题 |
| A3 | 遥控距离太短 站远点就不行 | 遥控信号范围 |
| A4 | 学遥控器 学习灯不亮 | 遥控编程/对码 |

### 1b. 未在 eval 集里的新口语（测泛化）

| # | Query | 备注 |
| --- | --- | --- |
| A5 | 门开到一半自己停了是咋回事 | 未出现在 18 条 eval 里 |
| A6 | 下雨天开门机跳闸 | 文档若无此场景，看生成是否瞎编 |

---

## 2. AD5S-AD8S（`run-ad5s/chroma_captioned`）

### 2-pre. 合并 chroma 前必查（结构提取）

试点 ingest 使用含 `troubleshooting_ladder` / `structure_warnings` 的 extract 产出后，**入库前**执行：

```powershell
# qa_groups.json 或 manifest.json 中不得有未处理的 structure_warnings
rg "structure_warnings" _scratch/run-ad5s-dry-ladder/qa_groups.json
rg "stall_branch_align_failed" _scratch/run-ad5s-dry-ladder/qa_groups.json

# 期望：无匹配（或已知告警已人工复核并记备注）
# extract 阶段 stderr 应无 [branch_utils] WARNING
```

| 检查项 | 通过标准 |
| --- | --- |
| `structure_warnings` | **0 条**未复核告警（`grep`/rg 无 `stall_branch_align_failed`） |
| qa_024 ladder | `troubleshooting_ladder` 存在；step3 **`branches` ×2**（非 4）；每条含 `applies_when_any`；采购链 **3**（1 电阻 + 2 二极管） |
| 自动化验收 | `python _scratch/eval/verify_qa_024_acceptance.py` → `RESULT: PASS`；`python -m unittest tests.test_branch_utils` → 9/9 |
| qa_server 启动 | stderr 无 `structure_warnings: N group(s) need review` |

闭环记录：[`qa_024_branch_closure.md`](./qa_024_branch_closure.md)  
prod 切换计划（外科 overlay · 待拍板）：[`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md)

### 2a. 正常 query

| # | Query | 预期方向 |
| --- | --- | --- |
| D1 | 按遥控器完全没反应 | qa_010，遥控无响应 |
| D2 | 门刚动一下就停 电机电流太小 | qa_022，**translated_group**；核对电流/接线细节是否因翻译失真 |
| D2b | 走停加电阻 二极管怎么接 | qa_024 Top1；ladder 4 步；无筛选 step3 **2** 卡；筛选 **推开门·关门不正常·美国** → **1** 卡、⇄ 标签、`content_en` +Motor、配图 **026+028**（无 027）· **浏览器✅ 2026-07-03**（pilot `:8766`） |
| D3 | 控制板一直咔哒响 | qa_011 |
| D4 | 一按遥控保险丝就烧 | qa_012，安全类；须给出准确排查步骤 |

### 2b. 未覆盖组探测（27 组 eval 仅 12 组）

| # | Query | 备注 |
| --- | --- | --- |
| D5 | 推拉门装反了怎么办 | 若命中未覆盖组，记 group_id 供 BL-V1-03 |
| D6 | 两个机臂只有一个在动 | 类似 a13 的变体问法 |

---

## 3. TC148（`run-tc148/chroma_captioned`，仅 2 组 · **必测越界**）

### 3a. 正常 query

| # | Query | 预期方向 |
| --- | --- | --- |
| T1 | 墙壁开关自检后灯常亮 | qa_001 |
| T2 | TC148 没反应 遥控器正常 | qa_002 |
| T3 | push button 端口短接 O/S/C COM | qa_002；已知 Top1 miss（Top3 才对）；**重点看 LLM 是否被 Top2/3 救回**；原文应附 [Drive 短接视频](https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing)（**BL-V1-04** 前 demo 不展示） |

### 3b. 极小库越界（block 级）

| # | Query | 关注点 |
| --- | --- | --- |
| T4 | 太阳能板不充电 | TC148 不含此内容；检索仍会命中 2 组之一，看是否硬答 |
| T5 | 机械臂伸不出去 | 配件非整机；观察是否察觉答非所问 |

---

## 4. 跨库对抗（每个库单独测）

> 分库物理隔离下 **不会** 混入另一型号 chroma 内容；风险是同库内误命中 + 自信展示。

| # | 在哪个库测 | Query | 预期正确行为 |
| --- | --- | --- | --- |
| X1 | TC148 | 太阳能板 2 块怎么接 | 不应给出太阳能接线步骤；应拒答或说明不匹配 |
| X2 | AD5S | TC148 墙壁按键 随机开门 | AD5S 不含 TC148；同上 |
| X3 | A3S | AD5S 机臂电流小 走 EN→ZH 翻译 | 不应出现 AD5S 专属场景（确认无意外共享数据） |
| X4 | 任意 | 帮我写一首关于大门的诗 | 拒答或说明不在手册范围，不尬编门禁内容 |

---

## 5. 生成质量人工核对（配合 1–4，须 **LLM 开**）

每库挑 **2–3 条**对着 docx 原文已知答案的 query：

- [ ] 步骤/电压/端子编号与检索 chunk 一致，无编造或张冠李戴
- [ ] 多 chunk 拼接时无漏关键步骤
- [ ] **AD5S D2**（qa_022 翻译块）：电流/接线细节无失真
- [ ] **TC148 越界**（3b、§4）：无「自信的错误整机答案」

| 结果 | 判定 |
| --- | --- |
| 与 chunk 一致，无编造 | ✅ pass |
| 漏步骤但无错误事实 | ⚠️ minor（可 demo，记 backlog） |
| 编造数值/步骤或张冠李戴 | ❌ **block demo** |

---

## 6. 配图渲染（每库 ≥3 条带图命中）

- [ ] 图片渲染（非裂图/空白）
- [ ] 图意与回答步骤一致（非挂错图）

docx 线 `images[].file` 为 basename，比 PDF 线稳；仍须实测各库 `images-dir` 与 manifest 一致。

---

## Gate #5 · 通过标准（钉死）

### 可对外 **分库 demo**

须同时满足：

| 项 | 标准 |
| --- | --- |
| Layer R | 三库检索线全过（见上表） |
| D1 生成忠实 | §5 无 ❌；AD5S D2、D4 必测 |
| TC148 越界 | T4、T5、X1 无 ❌ |
| 配图 | §6 无裂图/错图 ❌ |

### 可讨论 **BL-RET-01a merge**

在分库 demo 通过基础上：

- 产品确认需要「统一搜索框 / 跨型号检索」
- TC148 策略定案：**永久独立库** 或 **合并前加低分拒答 UX**（二选一）

| 情境 | 建议 |
| --- | --- |
| 客户接受按型号切换 demo | **不 merge**，01a 可延后 |
| TC148 越界 ❌ | **禁止**与 A3S/AD5S 合并同一 chroma，除非先加固拒答 |
| 仅 A3S+AD5S 稳、TC148 弱 | 可先 merge 两库，TC148 仍独立 |

---

## 记录模板

测完每条一行，写入 `_scratch/eval/demo_qa_log.md`：

```text
[ID] lib=A3S|AD5S|TC148 | LLM=on|off | query="..." | top1=qa_??? score=? | 生成忠实=✅|⚠️|❌ | 越界=✅|❌|n/a | 配图=✅|❌|无 | 备注=
```

示例：

```text
[T4] lib=TC148 | LLM=on | query="太阳能板不充电" | top1=qa_001 score=0.42 | 生成忠实=⚠️ | 越界=✅ 说明手册无太阳能内容 | 配图=无 | 备注=检索仍命中墙壁开关组
```

---

## 相关

- 检索 eval 覆盖：[`coverage_table.md`](./coverage_table.md)
- TC148 原文对照（含三链接清单）：[`demo_tc148_doc_check.md`](./demo_tc148_doc_check.md)
- 排期 Gate 总表：[`docs/排期.md`](../../docs/排期.md) §「docx 线收口 Gate」· **BL-V1-04** URL 透传

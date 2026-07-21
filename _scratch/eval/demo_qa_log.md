# demo_qa_log · Gate #5 · docx 三库

**日期**：2026-07-03 · **模式**：LLM=on（客户演示）· 探针与 `qa_server` 同路径

记录格式：`query | 检索命中 | score | 生成摘要 | 配图 | 问题`

---

## A3S · probe on

[A1] lib=A3S | LLM=on | query="适配器供电 灯不亮" | top1=qa_001 score=0.7249 | 配图=OK | 越界=n/a | llm=ok | 生成=简短结论+BAT/保险丝/22VDC/TS24-U/电池步骤，引用image_001 | 人工忠实=**浏览器✅**（未勾LLM：原文+配图✅；勾LLM：润色结构清晰、数值与步骤与chunk一致、相关配图仍渲染）
[A2] lib=A3S | LLM=on | query="太阳能充不进电池怎么办" | top1=qa_003 score=0.7429 | 配图=OK | 越界=n/a | llm=ok | 生成=检查太阳能板/充电电流/控制器输出；引用image_002/003/004 | 人工忠实=**浏览器✅**（qa_003·0.7429·LLM分步与手册一致·三张配图渲染）
[A3] lib=A3S | LLM=on | query="遥控距离太短 站远点就不行" | top1=qa_009 score=0.7976 | 配图=OK | 越界=n/a | llm=ok | 生成=天线/穿线孔/换CR2025电池/外接接收器四步；引用image_005/006 | 人工忠实=**浏览器✅**（qa_009·0.7976·步骤与手册一致·天线+遥控器电池图渲染）
[A4] lib=A3S | LLM=on | query="学遥控器 学习灯不亮" | top1=qa_006 score=0.8089 | 配图=无 | 越界=n/a | llm=ok | 生成=查电源灯/电压/保险丝→断配件重学；与手册2步一致 | 人工忠实=**浏览器✅**（qa_006·0.8089·无图符合预期·未与qa_005「学习灯亮」混淆）
[A5] lib=A3S | LLM=on | query="门开到一半自己停了是咋回事" | top1=qa_020 score=0.6684 | 配图=OK | 越界=n/a | llm=ok | 生成=机械阻力/机电流+限位A/B/拉耳/image_013·014；Top3含qa_025走停(0.65) | 人工忠实=**浏览器⚠️minor** Top1仍qa_020限位组，但LLM融合Top3走停步骤可接受；配图限位图渲染✅
[A6] lib=A3S | LLM=on | query="下雨天开门机跳闸" | top1=qa_015 score=0.6171 | 配图=OK | 越界=n/a | llm=ok | 生成=**拒答**「未找到跳闸/雨天信息」；主面板仍为关到位反弹步骤 | 人工忠实=**浏览器✅** 检索偏qa_015但LLM明确不足、未编造跳闸排查；配图FORCE/限位图渲染
[X3] lib=A3S | LLM=on | query="机臂电流小"(浏览器·清单全文含AD5S/EN→ZH) | top1=qa_025 score=0.7355 | 配图=无 | 越界=OK同库 | llm=ok | 生成=EN译中+0.5~3A/空载<1A/万用表测流·image_023 | 人工忠实=**浏览器✅minor** A3S qa_025非AD5S串库；翻译块数值准；型号字样未单独拒答可接受
[X4] lib=A3S | LLM=on | query="帮我写一首关于大门的诗" | top1=qa_017 score=0.5676 | 配图=无 | 越界=OK拒答 | llm=ok | 生成=明确无法写诗·说明资料为故障排查文档 | 人工忠实=**浏览器✅** 未勾LLM时主面板(无正文)；勾LLM后拒答、未尬编门禁诗

## AD5S · probe on

[D1] lib=AD5S | LLM=on | query="按遥控器完全没反应" | top1=qa_010 score=0.7746 | 配图=OK | 越界=n/a | llm=ok | 生成=检查输入电压(太阳能/适配器+电池22V/36V/TCS3)+排除配件+机臂24V+短接限位image_007 | 人工忠实=**浏览器✅** qa_010·完全不工作·步骤与chunk一致·限位短接图渲染
[D2] lib=AD5S | LLM=on | query="门刚动一下就停 电机电流太小" | top1=qa_022 score=0.732 | 配图=LLM引026-029 | 越界=n/a | llm=ok | 生成=EN原因块译中+手动反推+电阻/二极管极性+0.5~3A/<1A测流 | 人工忠实=**浏览器⚠️re-review** §十四双向异构（qa_022空ZH降级）；原「无数值失真」仅指当次展示数值未篡改·**未验**50Ω/1152公式入库、协商话术、US/UK条件链·见BL-V1-05C/BL-V1-06/BL-EXT-01
[D2b] lib=AD5S·**pilot** `run-ad5s-dry-ladder:8766` | LLM=off | query="走停加电阻 二极管怎么接" | top1=qa_024 score≈0.66 | 配图=✅ | 越界=n/a | llm=n/a | 筛选=推开门·关门不正常·美国 | 人工忠实=**浏览器✅** 步骤3 **1** US branch；标签 ⇄；`content_en` +Motor；配图 **026+028** 无027；步骤4可见；电阻+US二极管链 | 备注=见 [`qa_024_branch_closure.md`](./qa_024_branch_closure.md) §4.2
[D2b-prod] lib=AD5S·**prod** `run-ad5s/chroma_captioned:8765` | LLM=off | query="走停加电阻 二极管怎么接" | top1=qa_024 score=**0.6565** | 配图=✅ | 越界=n/a | llm=n/a | 筛选=**暂未选择** | 人工忠实=**浏览器✅** ladder 4 步；step3 **2** branch（US ⇄ +Motor / UK ⇄ Motor-）；`content_en` 可见；步骤4；配图 **4** 张+双向提示；链接电阻+二极管×2 | 备注=阶段1 prod·无筛选
[D2b-prod-filt] lib=AD5S·**prod** `:8765` | LLM=off | query="走停加电阻 二极管怎么接" | top1=qa_024 score=**0.6565** | 配图=✅ | 筛选=**推开门·关门不正常·美国** | 人工忠实=**浏览器✅** 左栏 step3 **1** US 卡；⇄；+Motor；026+028 | 备注=阶段1 prod 有筛选
[A8-prod] lib=AD5S·**prod** `:8765` | LLM=off | query="遥控距离太短 站远点就不行" | top1=qa_008 score=**0.7731** | 配图=✅ 005+006 | 人工忠实=**浏览器✅** ladder **4** 步；步骤4「**若以上均无效**」+加外接收器；配图天线+CR2025 | 备注=阶段2 prod 签字 2026-07-03
[M1-prod] lib=AD5S·**mixed prod** `:8765` | LLM=off | query="按遥控器完全没反应" | top1=qa_010 score=**0.7746** | 配图=✅ image_007×1 | 人工忠实=**浏览器✅** flat 步骤 620 字；`ladderWrap`/`branchFilterWrap` hidden；无 JS 报错 | 备注=混合态旧组回归 §15
[M2-prod] lib=AD5S·**mixed prod** `:8765` | LLM=off | query="控制板一直咔哒响" | top1=qa_011 score=**0.8399** | 配图=无 | 人工忠实=**浏览器✅** flat 三步；筛选器 hidden；无 JS 报错 | 备注=混合态旧组回归 §15
[M3-prod] lib=AD5S·**mixed prod** `:8765` | LLM=off | query="一按遥控保险丝就烧" | top1=qa_012 score=**0.8118** | 配图=无 | 人工忠实=**浏览器✅** flat 五步安全排查；筛选器 hidden；无 JS 报错 | 备注=混合态旧组回归 §15
[N1-prod] lib=AD5S·**prod** `:8765` | LLM=off | query="日常保养润滑 WD40" | top1=qa_028 score=**0.6748** | 配图=无 | 链接=无 | 人工忠实=**浏览器⚠️minor** flat；回答仅 7 字 ZH；WD40 在 EN 未展示 | 备注=BL-EXT-01 §十九 qa_028
[N2-prod] lib=AD5S·**prod** `:8765` | LLM=off | query="拆机臂内部怎么润滑" | top1=qa_029 score=**0.777** | 配图=无 | 链接=**3**× YouTube | 人工忠实=**浏览器✅** flat；参考链接 3 `<a>` 可点；无 JS 报错 | 备注=BL-EXT-01 §十九 qa_029
[D3] lib=AD5S | LLM=on | query="控制板一直咔哒响" | top1=qa_011 score=0.8399 | 配图=无 | 越界=n/a | llm=ok | 生成=断配件机臂→查电源压降/继电器→逐个回接定位 | 人工忠实=**浏览器✅** qa_011·0.8399·三步与手册一致
[D4] lib=AD5S | LLM=on | query="一按遥控保险丝就烧" | top1=qa_012 score=0.8118 | 配图=无 | 越界=n/a | llm=ok | 生成=查短路/保险丝规格→仅留电源按遥控→机臂离门测/离合→查门负载→逐个回接配件 | 人工忠实=**浏览器✅** qa_012·安全类五步具体、非笼统安慰
[D5] lib=AD5S | LLM=on | query="推拉门装反了怎么办" | top1=qa_019 score=0.6804 | 配图=OK | 越界=n/a | llm=ok | 生成=**说明无直接条目**→引用关到位反弹/推开门安装+FORCE/拉杆180° | 人工忠实=**浏览器⚠️minor** 检索偏qa_019反弹组非「装反」；LLM诚实+配图016/推开门示意；记BL-V1-03
[D6] lib=AD5S | LLM=on | query="两个机臂只有一个在动" | top1=qa_014 score=0.6913 | 配图=OK | 越界=n/a | llm=ok | 生成=交换机臂端口→测电机电压→短接限位ULT/COM/DLT→MOTOR口/电池测机臂 | 人工忠实=**浏览器✅** qa_014·口语变体近「单臂单向」·步骤完整·限位短接图渲染
[X2] lib=AD5S | LLM=on | query="TC148 墙壁按键 随机开门" | top1=qa_019 score=0.5476 | 配图=OK | 越界=OK拒答 | llm=ok | 生成=**无TC148直答**→说明手册无此条·建议按遥控/按键信号类（短接push button、查干扰） | 人工忠实=**浏览器✅** 未编造TC148专属接线；Top1偏反弹组(score低)；越界行为合格
[X4] lib=AD5S | LLM=on | query="帮我写一首关于大门的诗" | top1=qa_024 score=0.4432 | 配图=OK(误命中机电流图) | 越界=OK拒答 | llm=ok | 生成=**无法写诗**·说明资料为故障排查 | 人工忠实=**浏览器✅** 未勾LLM时主面板误展示电阻/二极管步骤；勾LLM后拒答、未写诗

## TC148 · 自动探针 + 原文对照（`demo_tc148_doc_check.md`）

[T1] lib=TC148 | LLM=on | query="墙壁开关自检后灯常亮" | top1=qa_001 score=0.6321 | 配图=OK image_001 COM接地 | llm=ok | 原文=**无灯常亮**·症状为随机开关门 | 生成=将灯常亮≈干扰/持续触发·五步与qa_001一致 | 人工忠实=**浏览器⚠️minor**（检索最近邻合理·步骤未编造·配图✅·未明确拒答「手册无此症状」）
[T2] lib=TC148 | LLM=on | query="TC148 没反应 遥控器正常" | top1=qa_002 score=0.7348 | 配图=无 | llm=ok | 原文=症状+TOPENS+断配件+短接 | 生成=与chunk一致 | 人工忠实=**浏览器✅**（qa_002·0.7348·TOPENS/断配件/屏蔽线/线距延长线/瞬时短接五步与原文一致·无图符合预期·LLM分步未失真）
[T3] lib=TC148 | LLM=on | query="push button 端口短接 O/S/C COM" | top1=qa_001 score=0.5262 | top2=qa_002~0.51 | 配图=OK image_001·实为COM接地非短接图 | llm=ok | 原文=qa_002瞬时短接+EN块O/S/C COM | 生成=症状/断配件/瞬时短接与qa_002一致 | 人工忠实=**浏览器⚠️minor**（Top1 miss·LLM救回✅·参考标题偏qa_001·配图与短接动作不完全匹配）
[T4] lib=TC148 | LLM=on | query="太阳能板不充电" | top1=qa_001 score=0.4332 | 配图=OK | 越界=OK拒答 | llm=ok | 原文=无 | 人工忠实=**auto✅**
[T5] lib=TC148 | LLM=on | query="机械臂伸不出去" | top1=qa_002 score=0.4774 | 配图=无 | 越界=OK拒答 | llm=ok | 原文=无 | 人工忠实=**auto✅**
[X1] lib=TC148 | LLM=on | query="太阳能板 2 块怎么接" | top1=qa_001 score=0.4234 | 配图=OK | 越界=OK拒答 | llm=ok | 原文=无 | 人工忠实=**auto✅**
[X4] lib=TC148 | LLM=on | query="帮我写一首关于大门的诗" | top1=qa_001 score=0.3783 | 配图=OK | 越界=OK拒答 | llm=ok | 原文=无 | 人工忠实=**auto✅**

---

## 自动探针摘要

| ID | 库 | top1 | score | 配图文件 | 越界/问题标记 |
| --- | --- | --- | ---: | --- | --- |
| A1 | A3S | qa_001 | 0.72 | OK | **浏览器✅** 原文+LLM双模式；保险丝图；生成无编造 |
| A2 | A3S | qa_003 | 0.74 | OK | **浏览器✅** LLM+三张太阳能接线/测压图 |
| A3 | A3S | qa_009 | 0.80 | OK | **浏览器✅** LLM+image_005天线/006 CR2025 |
| A4 | A3S | qa_006 | 0.81 | 无 | **浏览器✅** confusable 对未串到 qa_005 |
| A5 | A3S | qa_020 | 0.67 | OK | **⚠️minor** Top1偏限位；LLM+Top3走停救回；配图OK |
| A6 | A3S | qa_015 | 0.62 | OK | **浏览器✅** 检索偏但LLM拒答跳闸、未瞎编 |
| X3 | A3S | qa_025 | 0.74 | 无 | **✅minor** 同库机电流+EN→ZH润色准；非串库 |
| X4 | A3S | qa_017 | 0.57 | 无 | **浏览器✅** LLM拒答写诗 |
| D1 | AD5S | qa_010 | 0.77 | OK | **浏览器✅** LLM+电压排查+image_007限位图 |
| D2 | AD5S | qa_022 | 0.73 | LLM引图 | **⚠️re-review** §十四双向异构·D2原判修订 |
| D2b | AD5S·pilot | qa_024 | ≈0.66 | 026+028 | **浏览器✅** ladder+branch+筛选配图 |
| A8-prod | AD5S·prod | qa_008 | 0.77 | 005+006 | **浏览器✅** ladder 4 步+末环 |
| M1-prod | AD5S·mixed | qa_010 | 0.77 | OK×1 | **浏览器✅** flat+配图·无 ladder UI |
| M2-prod | AD5S·mixed | qa_011 | 0.84 | 无 | **浏览器✅** flat·筛选器 hidden |
| M3-prod | AD5S·mixed | qa_012 | 0.81 | 无 | **浏览器✅** flat 安全五步 |
| N1-prod | AD5S·prod | qa_028 | 0.67 | 无 | **⚠️minor** flat·仅 7 字 ZH·WD40 在 EN 未展示 |
| N2-prod | AD5S·prod | qa_029 | 0.78 | 无 | **浏览器✅** flat·3 视频链 |
| D3 | AD5S | qa_011 | 0.84 | 无 | **浏览器✅** |
| D4 | AD5S | qa_012 | 0.81 | 无 | **浏览器✅** 安全类五步排查具体 |
| D5 | AD5S | qa_019 | 0.68 | OK | **⚠️minor** LLM说明无直答+反弹步骤·图016 |
| D6 | AD5S | qa_014 | 0.69 | OK | **浏览器✅** 限位短接图 |
| X2 | AD5S | qa_019 | 0.55 | OK | **浏览器✅** 越界·LLM说明无TC148直答 |
| X4 | AD5S | qa_024 | 0.44 | OK | **浏览器✅** LLM拒答写诗 |
| T1 | TC148 | qa_001 | 0.63 | OK image_001 | **浏览器⚠️minor** 无灯常亮条目·步骤忠实 |
| T2 | TC148 | qa_002 | 0.73 | 无 | **浏览器✅** |
| T3 | TC148 | qa_001 | 0.53 | OK·COM接地图 | **浏览器⚠️minor** Top1 miss·生成救回 |
| T4 | TC148 | qa_001 | 0.43 | OK | **auto✅** 越界拒答 |
| T5 | TC148 | qa_002 | 0.48 | 无 | **auto✅** 越界拒答 |
| X1 | TC148 | qa_001 | 0.42 | OK | **auto✅** 越界拒答 |
| X4 | TC148 | qa_001 | 0.38 | OK | **auto✅** 拒答写诗 |

## Gate #5 · 总判（2026-07-03）

| 库 | 浏览器 | 自动+原文 | backlog |
| --- | --- | --- | --- |
| **A3S** | A1–A4/A6/X3/X4 ✅ · A5 ⚠️ | — | A5 口语走停 |
| **AD5S** | D1–D4/D6/X2/X4 ✅ · D5 ⚠️ · **D2 ⚠️re-review** | — | D5 装反；**D2** §十四；BL-V1-04/05/06；BL-EXT-01 |
| **TC148** | T1⚠️ T2✅ T3⚠️ **浏览器完成** | T4–X4 auto✅ | T1口语；T3 hybrid；**BL-V1-04** 链接；**BL-V1-05** zh/en 异构（禁简单折叠） |

**分库 demo**：**可通过**（无 block 级 ❌）。**Gate #5 docx 三库浏览器验收关闭**（2026-07-03）。

**暂不 merge** 三库（01a 未做；TC148 越界敏感）。

### 原文资源缺口（Gate #5 后登记 · BL-V1-04）

**grep 核实**：`content_zh` / `answer_zh` 中 **0** 条 URL；三链仅在 `content_en`（docx 英文段）。根因 = **数据分布（zh 无链）+ 无 `links[]` schema + 展示 `textContent`**。

**BL-V1-04 试点（2026-07-03）**：`qa_doc_extractor` → `links[]`（chunk 级 · `link_type`）→ manifest；`content_en` 裸 URL **0**；API：T2→qa_002 **2 链**（topens + Drive `video`）；T3 Top1 miss→qa_001 **1 链**。demo 已加「参考链接」`<a>` 区。详见 `docs/排期.md` § BL-V1-04。

**结构核实（截图 · BL-V1-05）**：TC148 中英**非互译**——ZH=内部速记 bullet，EN=对客邮件稿（含 `If problem disappears` 分支 + 链接）。**禁止** demo 中英折叠二选一；EN 独有分支须合并进 ZH 主答案，EN 全文仅作「客服模板原文」可选区。全库 `Please help us confirm` 仅 TC148；AD5S 亦有 ZH 简略/EN 更细。详见 `docs/排期.md` § BL-V1-05。

**AD5S 全文复核（pandoc · 2026-07-03）**：§十四 **双向异构**（D2 ⚠️re-review）；BL-V1-04 **简单/复杂分档**；BL-V1-06 协商话术过滤；BL-EXT-01 extract 缺口（§十九保养无组、URL 14→5）。详见 [`ad5s_full_doc_review.md`](./ad5s_full_doc_review.md) · 摸底 [`bl_ext01_gap_inventory.md`](./bl_ext01_gap_inventory.md)。

**qa_024 + qa_008 prod overlay**：阶段 1 D2b ✅ · 阶段 2 A8 ✅ · **混合态 M1–M3 ✅**（`:8765`）· 见 [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §14–15 · 收尾全貌 [`ad5s_complex_ladder_round_closure.md`](./ad5s_complex_ladder_round_closure.md)。

**JSON**：`demo_probe_*.json` · 对照：[`demo_tc148_doc_check.md`](./demo_tc148_doc_check.md)

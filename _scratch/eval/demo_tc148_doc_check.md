# TC148 · 探针结果 vs 原文对照

**源**：`samples/troubleshooting/TC148常见问题排查.docx` → `_scratch/run-tc148/qa_groups.json`（仅 **2 组**）

| group | 标题 | 原文要点 |
| --- | --- | --- |
| qa_001 | 接上TC148墙壁开关，自己开关门 | 症状：接上后**随机开关门**；断配件→屏蔽线/接线帽→线距线规/延长线→接地→换按钮/测导通；图 **image_001** COM接地 |
| qa_002 | 按TC148 PUSH BUTTON门机没有反应 | 症状：**遥控能用、按TC148无反应**；确认 TOPENS 正品→断配件→屏蔽线→线距→**瞬时短接 push button 端口（O/S/C COM）** 排除控制板 |

**无**：太阳能、机臂、灯常亮自检、诗歌。

---

## 原文资源清单（配图 + 链接）

### 配图（1 张）

| 文件 | 所属组 | 内容 |
| --- | --- | --- |
| `image_001.png` | qa_001 | 控制板 **5 号 COM（公共端）→ 地线螺丝** 接线示意（红标 wire / ground）；caption 与原文一致 |

qa_002 **无配图**；「瞬时短接 O/S/C COM」在原文为 **文字 + 视频链接**（见下表 #3）。

### 外链（3 处 · 2 种 URL）

| # | URL | 所属组 | `answer_zh` / `content_zh` | `content_en` | demo 可点 |
| ---: | --- | --- | :---: | :---: | :---: |
| 1 | [topens 多配件共端子博文](https://topens.com/blogs/blog-posts/how-to-connect-multiple-accessories-to-a-shared-terminal-on-a-topens-gate-opener-control-board) | qa_001 | **0**（grep 核实） | ✅ | ❌ |
| 2 | 同上 | qa_002 | **0** | ✅ | ❌ |
| 3 | [Drive · Instantaneously Short Push Button Terminal.mp4](https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing) | **仅 qa_002** | **0** | ✅ | ❌ |

**结论（2026-07-03 grep 核实）**

- **提取层**：无丢失；docx 含 http 的 3 段均为 `classify_language=en`。
- **不是**单纯的「zh 优先策略选错字段」：`content_zh` **原生就不含** URL（中英平行撰写，链接只在英文段）。
- **Schema 缺口**：URL 仅在 `content_en` prose，无 `links[]`；展示层 `content_zh \|\| content_en` + `textContent`（不可点击）进一步放大。
- **BL-V1-04**：优先 extract 阶段 `links[]`（与 `images[]` 同级），验收含 demo `<a>` 可点；详见 `docs/排期.md` § BL-V1-04。

### 中英异构（2026-07-03 截图核实 · BL-V1-05）

**不是互译对，是两种用途的文本**：

| | 中文 `answer_zh` | 英文 `answer_en` |
| --- | --- | --- |
| 体裁 | 内部排查速记 | 对客邮件回复稿（`Please help us confirm…`） |
| 结构 | 症状 + 扁平 bullet | `1.` / `If problem disappears` / `2.` `3.` 分支树 + 末尾参考链 |
| EN 独有（qa_002） | — | TOPENS 正品确认、接线牢固性、短接后 open-stop-close 判定句 |
| EN 独有（qa_001） | ZH 有接地三步文字 | EN 含 `Note:` 万用表导通判定（pressed / not pressed） |

**展示取向（已定）**：不做「中英折叠二选一」。主答案以 ZH 为主干 + 合并 EN 独有分支；`links[]` 始终展示；EN 全文作「客服回复模板原文」可选展开区。详见 `docs/排期.md` § BL-V1-05。

---

## 清单逐条（LLM=on · 浏览器 2026-07-03）

| ID | query | top1 | score | 与原文 | 生成忠实 | 越界 | 判定 |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| T1 | 墙壁开关自检后灯常亮 | qa_001 | 0.63 | 原文**无**「灯常亮」；最近邻为随机开关门组 | 将灯常亮≈干扰；五步与 qa_001 一致；**image_001** ✅ | — | **browser⚠️minor** |
| T2 | TC148 没反应 遥控器正常 | qa_002 | 0.73 | **完全对齐** qa_002 症状 | TOPENS/断配件/屏蔽线/短接等与 chunk 一致；**无图**符合原文 | — | **browser✅** |
| T3 | push button 端口短接 O/S/C COM | qa_001 | 0.53 | Top1 **miss**（应为 qa_002） | 生成含瞬时短接步骤 ✅；应展示 **#3 视频链** 却挂 qa_001 COM 图 | — | **browser⚠️minor** |
| T4 | 太阳能板不充电 | qa_001 | 0.43 | 原文无 | 「未找到」·未给太阳能步骤 | **✅拒答** | **auto✅** |
| T5 | 机械臂伸不出去 | qa_002 | 0.48 | 原文无 | 「未找到」·未给机臂步骤 | **✅拒答** | **auto✅** |
| X1 | 太阳能板 2 块怎么接 | qa_001 | 0.42 | 原文无 | 「未找到」·未给接线法 | **✅拒答** | **auto✅** |
| X4 | 帮我写一首关于大门的诗 | qa_001 | 0.38 | 原文无 | 拒答写诗 | **✅拒答** | **auto✅** |

---

## TC148 专测结论

- **越界 T4/T5/X1/X4**：生成层 **优于** 检索层 → Gate #5 block 项通过。
- **T2**：标准 demo 路径 ✅。
- **T1/T3**：口语/子块检索 minor；**不 block** 分库 demo。
- **链接**：**BL-V1-04 TC148 试点 ✅**（`links[]` chunk 级 · `content_en` 无裸 URL · T2 展示 2 链含 `video`）；T3 仍 Top1 miss → 仅见 qa_001 的 1 链（检索 backlog，非 V1-04）
- **合并建议**：TC148 **宜永久独立库**，勿与 A3S/AD5S merge 同一 chroma（除非加低分拒答 UX）。

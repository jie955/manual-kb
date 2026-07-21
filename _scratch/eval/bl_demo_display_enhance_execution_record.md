# Demo 展示增强 · 文档来源 + 相关推荐 · 执行留档

**日期**：2026-07-05  
**范围**：`demo/index.html` only（无 chroma / 无 re-embed）  
**探针**：[`demo_display_enhance_probe.py`](./demo_display_enhance_probe.py) · [`demo_display_enhance_probe.json`](./demo_display_enhance_probe.json)

---

## 1 · 文档来源标注

Top1 回答卡片新增 **「文档来源」** 区块（默认可见）：

| 层级 | 展示 | 说明 |
| --- | --- | --- |
| 主文案 | **型号库名 · 文档名 · 章节标题（人话）** | 例：`A3S / A5S / A8S · A3S-A5S-A8S 常见问题排查 · 十五、离合打不开` |
| 条目标题 | `matchTitle` = 原 question（H2 标题） | 与来源区分，不再挤在一行 meta 里 |
| 技术细节 | `group_id` **右下角极小字号** + `title` 悬停提示 | 不对客户主视觉；内部核对可用 |
| 匹配度 | 单独一行 `matchMeta` | 仅 score bar |

**章节标题**：从 `section` 截取中文/前缀部分（去掉长英文副标题）。

**检索依据侧栏**：`hit-meta` 默认 **不展示 group_id**；悬停 summary 可见内部编号。

---

## 2 · 相关问题推荐

- **来源**：当前检索 **hits #2–#4**（按 `group_id` 去重，最多 3 条）
- **交互**：chip 点击 → 填入搜索框 → 触发新检索（同「试试」 chips）
- **chip 文案**：question 中文/短标题（≤24 字）
- **悬停**：完整 query + 内部 group_id + score（供 spot-check）

未做预设 related map（POC 刻意保持简单）。

---

## 3 · 三库 spot-check（API · LLM=off）

| 库 | query | Top1 | 来源章节 | 相关 chips（语义判断） |
| --- | --- | --- | --- | --- |
| **A3S** | 日常保养喷WD40润滑 | qa_040 ✅ | 十七、保养与润滑 | qa_041 ✅ 同域；qa_013 △ 弱相关（低分 0.48，仅作第 2 条后无第 3 时不出现） |
| **A3S** | 离合钥匙拧不开 | qa_038 ✅ | 十五、离合打不开 | qa_035/036 △ 走停/电机邻域 · **可接受**（排查链路相近，非 clutch 专条） |
| **A3S** | 随意开关门乱开 | qa_029 ✅ | 五、随意开关门 | qa_023/018 ✅ 已知 confusable · **作为相关推荐合理** |
| **AD5S** | 门自己乱开乱关 | qa_031 ✅ | 六、随意开关门 | qa_037/033 △ 限位/自动关门邻域 · 可接受 |
| **AD5S** | 电机电流小 并接机臂 | qa_023 ✅ | 十四、电机电流小 | qa_024/022 ✅ 同章族 · **强相关** |
| **AD5S** | 日常保养润滑 WD40 | qa_028 ✅ | 十九、保养与润滑 | qa_029 ✅ 日常 vs 深度 · **强相关** |
| **TC148** | TC148 没反应 | qa_002 ✅ | —（库内无 section 字段） | qa_001 ✅ 两题互斥对 · **强相关** |
| **TC148** | 墙壁开关自己开关门 | qa_001 ✅ | — | qa_002 ✅ 同上 |

**探针**：8/8 Top1 PASS · 0 eval 回归（demo-only 变更）

### 语义 spot-check 结论

- **邻域相近型**（qa_029→qa_023、qa_038→qa_035）：作为「相关问题」**体验可接受** — 同排查手册内相邻故障域，非随机漂移。
- **弱相关型**（qa_040 第 2 条 qa_013）：score 明显低于首条相关（0.48 vs 0.71）；若仅 2 条 unique group 则不会凑满 3 条误导 chip。
- **TC148 section 为「—」**：prod 仅 2 组、chunk 无 section 文本 · 来源行仍含库名+文档名 · V2 可在 extract 补 section。

---

## 4 · 浏览器手测要点

刷新 **http://127.0.0.1:8765/**（三库下拉切换 :8766/:8767）：

1. 来源区：**不出现** qa_XXX 与章节同级大字；右下角极小 `qa_038` 仅悬停/余光
2. 相关问题：点 chip 应发起新检索且 Top1 切换
3. 目检：推荐 chip 与当前问题是否「同域/可联想」（见上表 △ 项）

**无需重启 qa_server**（静态 `demo/index.html` 热更新）；若浏览器强缓存，硬刷新即可。

---

## 5 · V1 六项收口

| # | 项 | 状态 |
| ---: | --- | --- |
| 1 | LINK-A3S | ✅ [`bl_a3s_post_handtest_execution_record.md`](./bl_a3s_post_handtest_execution_record.md) |
| 2 | IMG-EXT-02 | ✅ 同上 |
| 3 | ZH-SKELETON qa_041 | ✅ 同上 |
| 4 | RETR-DISAMB | ✅ 同上 |
| 5 | **文档来源标注** | ✅ 本留档 |
| 6 | **相关问题推荐** | ✅ 本留档 |

（EN-UI 折叠 · caption 批 · qa_040 grease 图 — 已标非阻塞残余，不进本六项。）

---

## 6 · 后续（V2 · 非阻塞）

- TC148 / 无 section 组：extract 补 `section` 使人话章节更完整
- 相关推荐：若 Top2/3 漂移增多，可改 **预设 related map** 或 **同 H1 邻域过滤**
- `group_id` 悬停：可加「复制内部编号」供客服后台（V2）

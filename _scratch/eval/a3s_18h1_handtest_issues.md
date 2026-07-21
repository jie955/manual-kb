# A3S · 18 H1 手测问题整理

**日期**：2026-07-05 · **校准**：2026-07-05（合规 / 一图多组 / qa_041 提级 / P2 决策）  
**范围**：[`a3s_18h1_handtest_log.md`](./a3s_18h1_handtest_log.md) · 43 组 · eval **45/45 Top1**  
**结论**：检索 + 中文 **全库可交付**；下列为 **V2 backlog** 与 **待拍板项**，**非** EXT-01 回归

---

## 一、总览（校准后）

| 类别 | 严重度 | 修复线 | 备注 |
| --- | --- | --- | --- |
| **COMPLIANCE-011** qa_011 Drive 链展示范围 | **P0 · 合规** | 产品/合规拍板 | **≠** LINK-A3S · **暂缓** `links[]` |
| **IMG-EXT-02** 配图 | **P1 · 系统性** | 分两型设计（见 §2.1） | 禁止混为一谈 |
| **LINK-A3S** baseline `links[]` | **P1 · 技术** | **仅 qa_003**（+ qa_001/002 扫尾） | **不含 qa_011** 直至合规确认 |
| **ZH-SKELETON** qa_041 空中文 | **P1 · 内容** | 补最小 ZH 骨架 | 同 AD5S **qa_017** 先例 |
| **EN-UI** 折叠英文参考 | **P1 · 产品** | TC148 `<details>` | qa_011 折叠区分子段 |
| **RETR-DISAMB** qa_040/041 等域重叠 | **P2 → 路径 B 已选** | 症状化/互斥标签 · 复用 AD5S qa_028/029 | 见 §四 · [`phase_a3s_post_handtest_overlay.py`](./phase_a3s_post_handtest_overlay.py) |
| **低分 Top1 监控** | **P3** | qa_042 · qa_040 · qa_033 | **不含** qa_041（已提 P1） |
| **cosmetic / 不对称** | **P3** | spot-fix · V2 extract | 编号 · TCS31 等 |

---

## 二、P0 · 合规（最优先 · 动手前必确认）

### COMPLIANCE-011 · qa_011 Drive 短接视频

**性质**：**business / compliance 约束**，不是「漏做 `links[]`」的纯技术 backlog。

docx ZH 明示：**「注意站内信不可发此链接」** — 若渠道规则禁止在客服站内信发某类外链，则：

| 状态 | 含义 |
| --- | --- |
| **现状** | URL 在 `answer_en` prose · demo **不可点、未暴露** 参考链接区 |
| **若按 LINK-A3S 加 `links[]` 可点击** | 可能 **违反**「不可发」约束 · **比现状更危险** |
| **若做 EN 折叠参考** | 须定义：折叠区 **客服可见** vs **客户可见** · Drive 是否允许出现在任何对外 UI |

**决策待办**（产品/合规 · **阻塞 qa_011 一切链接/EN 外链展示方案**）：

1. Drive 链在 demo / 客服工具里 **能不能展示**？能的话以什么形式（仅内部折叠 / 不可转发 / 完全隐藏）？
2. 「站内信不可发」范围是 **仅站内信** 还是 **所有客户触达通道**？

**2026-07-05 执行立场**：维持现状（Drive URL 留在 `answer_en` prose · demo 不可点 · 无 `links[]`）。**待甲方后续需要时再补充**展示方案；本批次 **无代码改动**。

**与 LINK-A3S 关系**：**拆线** — qa_003 可先修；**qa_011 按兵不动**，直至上表有书面结论。结论为「不可对外展示」时，修复目标可能是 **strip URL + 保留文字步骤**，而非 `links[]`。

---

## 三、P1 · 须立项修复

### 3.1 IMG-EXT-02 — 配图（分两型 · 不可混修）

**共同背景**：EXT-01 overlay 未走 H2 inline 图抽取；但手测发现 **至少两种不同根因**，修复方案不同。

#### 型 A · **完全未抽取**（docx 有图 · 库内无任何组 `images[]`）

| group | § | docx 图数 | 典型缺失 |
| --- | --- | ---: | --- |
| **qa_035** | 八 | 1 | orphan inline |
| **qa_036** | 十三 | 3 | 伸太过排查图（links 已有 topens） |
| **qa_038** | 十五 | **5** | EN「see screenshot below」 |
| **qa_039** | 十四 | 2 | 拆壳参考图 |
| **qa_040** | 十七 | 1 | grease「as shown below」 |

**修复方向**：overlay / extract **补抽 inline 图** → caption → `images[]` → re-embed。

#### 型 B · **已抽取 · 归属/共享遗漏**（物理文件在库 · 应挂多组却只挂一组）

| 案例 | 现象 | 根因假设 |
| --- | --- | --- |
| **qa_033** §四 | docx「4 短接限位」应有 DLMT/COM/ULMT 图 | **`image_019.png` 已在 `run-006/images`** · 仅 **qa_021** §十「不限位」引用 · **qa_033 未关联** |

**与型 A 的区别**：不是「没有 png 文件」，而是 **图片–段落归属 / 一图多组共享** 未建模。修复可能是：

- 同文件 **多组 `images[]` 引用**（共享 asset），或
- extract 阶段 **按 docx 出现位置** 绑定 group，而非「首次出现段落」独占

**EXT-02 设计 gate**：方案须 **分别验证** 型 A 与型 B 测试用例；**禁止**只做「补抽 orphan」而漏掉 qa_033 类共享挂载。

留档：[`a3s_ext01_image_gap_scan.md`](./a3s_ext01_image_gap_scan.md) · 手测 [`a3s_18h1_handtest_log.md`](./a3s_18h1_handtest_log.md) §qa_033

---

### 3.2 LINK-A3S — baseline 技术遗漏（**不含 qa_011**）

| group | 资源 | prod | 修复 |
| --- | --- | --- | --- |
| **qa_003** | topens 太阳能排查 | URL 在 `answer_en` · **无 `links[]`** | 对齐 AD5S BL-V1-04 → re-chunk → re-embed |
| qa_001 / qa_002 | topens 共端子等（待核实） | 未扫 `links[]` | 扫尾后同上 |

**qa_011 Drive 链 → 见 §二 COMPLIANCE-011，不在本线。**

EXT 组 qa_036–041 等 **`links[]` 已入库** · demo 参考链接 **✅** — 本线主要针对 **baseline qa_001–028**。

---

### 3.3 ZH-SKELETON — qa_041 空中文（P1 · 非「低分监控」）

| 字段 | 现状 |
| --- | --- |
| `answer_zh` | **空** |
| demo | **V1-07 全 EN 补充块** 兜底 |
| 检索 | eval q43 Top1 **0.61**（与 qa_040 **0.6072** 几乎并列） |

**性质**：与 AD5S **qa_017**「空 ZH → 补最小骨架」同类（[`bl_v1_08_a3s_execution_record.md`](./bl_v1_08_a3s_execution_record.md)）— **客户主面板不应长期纯 EN**。V1-05 对 AD5S 曾把「ZH 完全空」列为重点处理对象；qa_041 **不应降级为 P3 监控**。

**修复方向**（内容层 · 可与 V1-05B / overlay 并行）：

- 从 docx §十七「深度润滑」段补 **最小 ZH 骨架**（Routine vs Deep 区分 · 拆臂润滑要点）
- 与 **qa_040**（日常保养）形成 **互斥/分流首行**（见 §四 RETR-DISAMB）
- 补后 re-embed · 预期 **抬升 q43 分数** 并 **降低对 V1-07 依赖**

---

### 3.4 EN-UI — 可折叠英文参考

（维持原判断 · 无争议）

中长 ZH 组 demo 仅中文 · EN 规格/分支不可见 → **可折叠「英文参考」**（非全库双栏）· [`bl_v1_07_thin_zh_display.md`](./bl_v1_07_thin_zh_display.md)

| 类型 | 示例 |
| --- | --- |
| baseline | qa_001 · qa_010 · qa_012 · qa_013 |
| 长组 + EN 分岔 | **qa_011**（太阳能 / 适配器+电池 · **Drive 展示服从 §二合规**） |
| EXT | qa_033 · qa_034 · qa_042 |

---

## 四、P2 · 检索域重叠（待拍板 · 非默认「靠客服话术」）

### 4.1 现象

| 裸 query | 误/弱命中 | score | eval 正 query |
| --- | --- | ---: | --- |
| **`到一半就停`** | **qa_030**（缓停） | 0.62 | 「开关门过程中走停反弹」→ qa_035 |
| **`WD40`** | **qa_041** | 0.39 | 「日常保养喷WD40润滑」→ qa_040 |
| **`控制板灯不亮`** | qa_001/002 歧义 | ~0.77 | 须带供电场景 |
| **`学习灯微微亮`** | qa_014 | 0.69 | 弱相关 · 可接受 |

### 4.2 决策分叉（须 explicit 写入 V2 计划）

**路径 A · V1 接受的运营约束（POC 阶段）**

- 靠 **eval 探针 + 客服话术规范** 避免裸句
- 文档标注：**技术上可优化，V1 刻意不修**
- 适用于：若 V1 已收口、V2 统一做 disambiguation

**路径 B · 复用 AD5S 已验证方法（内容/检索层）**

- **qa_040 / qa_041** 与 AD5S **qa_028 / qa_029**（日常 vs 深度保养）、**限位域症状化命名** 同型
- 手段：**互斥标签首行** · question/embedding 症状化 · 必要时 thin-ZH + 分流（AD5S BL-V1-08 先例）
- **qa_041 补 ZH 骨架（§3.3）本身即 disambiguation 的一部分**

**当前留档立场**：手测 **仅记录现象**；**未默认选 A 或 B**。若 V2 不做路径 B，须在排期写清「**当前接受的运营约束**」；若做，应 **显式引用 AD5S 同型修复** 而非仅列 P2 话术表。

### 4.3 eval 设计对（Top2 邻近 · 非 miss）

qa_029↔qa_023/018 · qa_031↔qa_029 · qa_037↔qa_043 · qa_035↔qa_015/016（acceptable）

---

## 五、P3 · 监控与 cosmetic

### 5.1 低分 Top1（eval 仍绿）

| group | query | score | 说明 |
| --- | --- | ---: | --- |
| **qa_042** | AB值是什么意思 | **0.43** | §十八 mega-dump |
| **qa_040** | 日常保养喷WD40 | **0.65** | 边界 · 与 qa_041 域重叠（§四） |
| qa_033 | 机臂只朝一个方向转 | 0.69 | §四最低 |

> **qa_041 低分** 归入 **§3.3 ZH-SKELETON**，不单列于此。

### 5.2 占位符 / 不对称 / 编号

| 类型 | 组 |
| --- | --- |
| 占位符 | qa_003「科普文章链接：」· qa_036「博客文章链接：」· qa_011 末两行 docx 占位 |
| ZH-only orphan | qa_043（`answer_en` 空 · 互斥标签 ✅） |
| ZH/EN 不对称 | qa_033 内参 · qa_013 5A/1m · qa_011 EN 分岔 |
| 编号 cosmetic | qa_006/008/010/033 · qa_004 TCS31 |

### 5.3 结构 warning（预期）

qa_039 `dt_prose_only` · qa_043 `partial_h1_overlay`

---

## 六、特别标注（校准后）

### qa_011

- EN 折叠 **两段子场景**（太阳能 / 适配器+电池）
- **Drive 链：COMPLIANCE-011 优先** — 未确认前 **不加可点击 `links[]`**
- 配图 image_007 ✅

### qa_033

- 型 B 配图：**image_019 共享挂载** · 非单纯 orphan 未抽
- EN 仅 1–4 步 vs ZH 内参 → EN-UI

---

## 七、建议处理顺序（校准后）

| 序 | 项 | 说明 |
| ---: | --- | --- |
| **0** | **COMPLIANCE-011** | qa_011 Drive 能否在 demo/客服 UI 展示 · **阻塞 qa_011 链接方案** |
| **1** | **LINK-A3S** | **先 qa_003**（+ qa_001/002 扫尾）· **不含 qa_011** |
| **2** | **IMG-EXT-02** | **型 A / 型 B 分案** · 分别验收（含 qa_033 共享引用） |
| **3** | **ZH-SKELETON qa_041** | 最小 ZH + 与 qa_040 分流 · 同 AD5S qa_017 标准 |
| **4** | **RETR-DISAMB 拍板** | 路径 A（V1 运营约束）vs 路径 B（复用 AD5S 症状化）· **书面二选一** |
| **5** | **EN-UI** | 折叠英文参考 · qa_011 子段 · Drive 服从 §0 结论 |
| **6** | **P3** | cosmetic · qa_042 低分监控 · eval 负例（「到一半就停」） |

---

## 八、不属于 bug（手测确认）

- baseline 配图 qa_001–009 等：**目视 OK**
- EXT 多数 `links[]`：**demo 参考链接 OK**（qa_011 Drive **除外 · 合规待定**）
- V1-07 thin-ZH 行为：**符合设计**（qa_041 全 EN 兜底 **除外 · 待补骨架**）
- eval **45/45** · gap scan **missing H1 = 0**

---

## 交叉链接

- 手测明细：[`a3s_18h1_handtest_log.md`](./a3s_18h1_handtest_log.md)  
- 配图扫描：[`a3s_ext01_image_gap_scan.md`](./a3s_ext01_image_gap_scan.md)  
- AD5S qa_017 骨架：[`bl_v1_08_a3s_execution_record.md`](./bl_v1_08_a3s_execution_record.md)  
- V2 方法论：[`v1_lessons_for_v2.md`](./v1_lessons_for_v2.md) §1.4

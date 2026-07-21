# BL-V1-05 · 范围定稿（2026-07-05）

**状态**：**✅ 关闭** · 见 [`bl_v1_05_execution_record.md`](./bl_v1_05_execution_record.md)  
**扫描**：[`ad5s_zh_en_gap_scan.py`](./ad5s_zh_en_gap_scan.py) · 产物 [`ad5s_zh_en_gap_inventory.md`](./ad5s_zh_en_gap_inventory.md)（**43 组 · 39 有缺口**）  
**原则**：Tier A **spot-fix** + 全库 **audit 留档** · 不做全库 qa_022 级重写

---

## 1. 与 V1-07 / V1.1 的分工

| 层 | 项 | V1-05 本批 | 不在本批 |
| --- | --- | --- | --- |
| **展示** | thin-ZH → EN 补充块 | 验收时 **spot-check** 补丁后是否仍合理 | 阈值/rule 改动 |
| **内容** | 买错/装错级规格 → `answer_zh` | **Tier A spot-fix** | 系统性全文合并 |
| **TC148** | 内部速记 vs 客服邮件稿 | **审计 only**（thin-ZH 够用即过） | 模板展开设计 → **V1.1** |
| **§十四 C** | qa_022/023/024 | **审计 + 禁区** | naive 塞回 `answer_zh` |

---

## 2. 43 组重扫摘要

| 子模式 | 组数 | V1-05 处置 |
| --- | ---: | --- |
| **detail_spec** | 8 | **Tier A · spot-fix** |
| structural_branch | 16 | **Tier B · audit 留档**（见 §4 扩展候选 4 组例外） |
| detail_prose | 13 | **Tier B · audit 留档** |
| detail_link | 2 | **Tier B**（qa_029/042 URL → links[] backlog，非 prose 合并） |
| **无缺口（aligned）** | 4 | qa_022 · qa_025 · qa_028 · qa_030 — 记录即过 |

> **scanner 局限**：`If` 句计数会把含 CR2025/端子号但分支多的组标成 `structural_branch`。§3.2 按**缺口性质**单列，不唯 scanner 标签。

---

## 3. Tier A · spot-fix 候选

**入选标准（唯一）**：EN 有、ZH 无、且属于 **客户买错/装错/量错即有后果** 的规格/型号/数值——保险丝、电池型号、电压阈值、DIP 位、端子号、门宽门重测量单位等。

**禁止**：把 EN 分支树/接线步骤/协商句整段并入 ZH（尤其 §十四 ladder 组）。

### 3.1 核心候选（scanner = `detail_spec` · 8 组）

| group | eval | EN 独有 spec（扫描） | 建议增补方向（spot） |
| --- | :---: | --- | --- |
| **qa_001** | a01/a02 | ∅5×20mm · 10A 250VAC · 24V 12Ah · 备用保险丝位置 · 36VDC | 步 2 保险丝规格 + 备用 fuse 在说明书包装内 |
| **qa_002** | a03 | 同 qa_001 保险丝三件套 | 同上（太阳能版） |
| **qa_004** | a05 | +30W 太阳能板 | 配件增容规则一句（30W/6h 阳光/10 cycles） |
| **qa_007** | c01 | CR2025 | 换电池步骤补「2× CR2025」 |
| **qa_010** | a09/a15 | dip switch **#5**（关红外） | 步 2 排查配件处补 DIP #5 |
| **qa_012** | a11 | 10A 250VAC · **3 feet** 门宽测量 | 保险丝规格 + 手动推拉测距 3.3ft/1m |
| **qa_033** | b03 | DIP Switch **#1** / **#2**（自动关门） | 对应步骤补 DIP 位说明 |
| **qa_040** | b10/a16-acc | **3 feet** 门宽 | 与 qa_012 同规格句，补入门宽测量 |

### 3.2 同性质扩展（scanner = `structural_branch` · 4 组）

性质与 Tier A 相同，仅因 EN 条件句多被误分类。**建议并入 Tier A 同一批 patch**，避免 CR2025 仍只靠 V1-07 EN 块：

| group | eval | EN 独有 spec | 建议增补 |
| --- | :---: | --- | --- |
| **qa_005** | a06 | 11# / 12# BAT 端子 | 测电压步骤补端子号 |
| **qa_006** | a07 | CR2025 · 11#/12# | 换电池 + 测 BAT 步骤 |
| **qa_008** | a08 | CR2025 · **65 feet** 参考距离 | 步 1/3/4 补型号与开外区距离 |
| **qa_009** | c02 | CR2025 | 换电池步骤 |

### 3.3 Tier A 合计 · 12 组

```
qa_001 qa_002 qa_004 qa_005 qa_006 qa_007 qa_008 qa_009 qa_010 qa_012 qa_033 qa_040
```

**未入 Tier A 的 spec 样例（有意排除）**

| 样例 | 原因 |
| --- | --- |
| qa_005 `backup fuse packed` | scanner 在 structural 组内；可与 qa_001 同步补，**随 Wave 1 可选** |
| qa_043 / qa_042 YouTube URL | **detail_link** → links[] backlog，非 answer_zh 合并 |
| qa_016–021 `0.4 inches` 等 | 安装微调 prose · **Tier B**（非买错级） |

---

## 4. Tier B · audit 留档（27 组 · 本批不 merge）

### 4.1 structural_branch（16 组 · 不含 §3.2 四组）

qa_016 · qa_017 · qa_018 · qa_019 · qa_020 · qa_021 · qa_031 · qa_032 · qa_035 · qa_036 · qa_037 · qa_043  
+ §3.2 已升格四组仍保留原 EN 分支结构审计结论

**审计结论模板**：ZH 骨架 + V1-07 EN 块是否覆盖客户可见损失；无 RED 则 **known gap · 不阻塞 V1**。

### 4.2 detail_prose（13 组）

qa_003 · qa_011 · qa_013 · qa_014 · qa_015 · qa_023 · qa_024 · qa_026 · qa_027 · qa_034 · qa_038 · qa_039 · qa_041

### 4.3 detail_link（2 组）

qa_029 · qa_042 — YouTube 链；V1-04 简单档或专项 links[]，**禁止**把 URL 糊进 `answer_zh`。

### 4.4 aligned（4 组 · 仅确认）

| group | 说明 |
| --- | --- |
| qa_022 | ZH 已含 50Ω/25Ω · **1152÷R** 公式（EXT-01）· EN 反而更短 |
| qa_025 | 遇阻主从 · 双语基本均衡 |
| qa_028 | thin-ZH · V1-07 已覆盖展示 |
| qa_030 | 空 ZH 外链组 · V1-04 links[] 已处理 |

---

## 5. 子模式 C · §十四禁区（审计 · 禁止 naive merge）

| group | 已有结构 | V1-05 允许 | **禁止** |
| --- | --- | --- | --- |
| **qa_022** | 引言/公式 prose | 确认 aligned · 无 patch | 把 qa_024 接线/电阻细节塞进 ZH |
| **qa_023** | ladder + `parallel_test` branch · 协商剥离 | 确认 ladder 步内 ZH 够用 | 把 EN 并接/电阻段合并回根级 prose 破坏 branch |
| **qa_024** | ladder + `applies_when_any` · region 采购链 | 确认 branch 内容仅在 branch 内 | 把二极管接线块 flatten 进 `answer_zh` |

**验收**：grep `answer_zh` 无新增 EN 整段复制；`troubleshooting_ladder` / `branches[]` 结构不变；[`verify_qa_023_acceptance.py`](./verify_qa_023_acceptance.py) / qa_024 四项仍 PASS。

---

## 6. TC148（2 组）· V1 审计 only → V1.1

- **V1**：确认 A3S/TC148 库 thin-ZH + eval 路径无阻塞（Gate #5 已验）
- **V1.1**：`Please help us confirm` 客服模板是否独立 `content_role` 展示

---

## 7. Patch 波次建议（供确认第一刀）

| 波次 | 组 | 理由 |
| --- | --- | --- |
| **Wave 1 · pilot** | qa_001 · qa_002 · qa_007 · qa_008 · qa_012 | 排期「V1-05B 简单合并」已点名 + eval 高频 + 保险丝/CR2025 典型 |
| **Wave 2** | qa_005 · qa_006 · qa_009 · qa_010 · qa_004 | 遥控器/无反应/太阳能增容 |
| **Wave 3 · 01b** | qa_033 · qa_040 | Batch 新组 · DIP / 门宽 spec |

**定稿（2026-07-05）**：**第一刀 = Wave1+2 合并 9 组**（qa_001/002/004/005/006/007/008/009/012）· **第二刀 = Wave3**（qa_033/040）

每波：**surgical `answer_zh` patch → chunk → embed 触及组 → display probe + 1–2 浏览器 spot-check → eval 无回归**。

---

## 8. Gate · V1-05 关闭条件

1. §3 Tier A **12 组** closure 表（组 × 增补句 × 验证截图/探针 id）  
2. §4 Tier B + §5 C 区 audit 结论写入 `bl_v1_05_execution_record.md`  
3. AD5S eval **≥ 45/47 Top1 · 47/47 Top3**（a16/c12 维持 pre-existing）  
4. §十四 verify 脚本 + ladder 结构 **无回归**

---

## 9. 交付物（计划）

| 产物 | 说明 |
| --- | --- |
| `bl_v1_05_scope.md` | 本文 |
| `ad5s_zh_en_gap_inventory.md` | 43 组扫描（已更新） |
| `phase_bl_v1_05_*_overlay.py` | 按波 surgical patch |
| `bl_v1_05_execution_record.md` | 跑完写 |
| `bl_v1_05_tier_a_closure.md` | Tier A 逐组增补对照（可选独立表） |

**当前待决**：~~第一刀 Wave1 vs Wave1+2~~ → **第一刀 Wave1+2（9 组）已开工** · 第二刀 Wave3

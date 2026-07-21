# BL-EXT-01b · 分类摸底（2026-07-05）

**状态**：摸底完成 · §九/§十六 **原文核实修订** · **未写 extract**  
**机器可读**：[`bl_ext01b_classification.json`](./bl_ext01b_classification.json)  
**核实附录**：[`bl_ext01b_sec09_sec16_verification.md`](./bl_ext01b_sec09_sec16_verification.md)  
**扫描脚本**：[`bl_ext01b_classify_scan.py`](./bl_ext01b_classify_scan.py)

---

## 标签说明

| 标签 | 含义 | 处理路径 |
| --- | --- | --- |
| **F** | flat · 顺序步骤 | 补 H2 → extract → links[] → embed → 浏览器（qa_028–030 式） |
| **L-scenario** | 两（多）**独立场景**各走线性步骤，拆 H2 即可；**非**决策树跳转 | 2 H2 → 各 F/L attach |
| **DT** | **观察后跳转**决策树（1→5 等非相邻）；线性 ladder **会误导** | **DT pilot** → 优先 F prose 或扩展 schema；**禁止**默认 attach 线性 ladder |
| **C** | 预先已知 ctx + `branches[]` + `applies_when`（qa_024） | qa_024 管线 |
| **P** | partial · prod 已有组 + orphan 子场景 | 错组 eval · 单独批 |
| **Z** | V1-05 验收列（正交，不升格 process tag） | B = EN-heavy / 步内规格 |

> **C 判定**：不得用 grep amazon 作充分条件；见核实附录 §1。

---

## 汇总（2026-07-05 修订）

| 维度 | 值 |
| --- | ---: |
| 节数 | **11** |
| orphan 段落 | **160** |
| F / L-scenario / DT / P / C | **7 / 2 / 1 / 1 / 0** |
| 最大单节 | §十六 **35 段** · **DT** |

> **本批无 qa_024 式 C**；§十六 为 **DT**（观察后跳转，非 C 非线性 L）。

---

## 分类表（含证据）

| # | H1 节 | orphan | Tag | 证据（一行） | Z |
| ---: | --- | ---: | :---: | --- | :---: |
| 1 | 十八、风把门吹开 | 6 | **F** | 3 步顺序；无 → 树 | — |
| 2 | 八、自动关门不生效 | 8 | **F** | 4 步顺序 + 1 特殊案例 | B |
| 3 | 七、缓停止 | 9 | **F** | 4 步线性 | B |
| 4 | 一个机臂不工作 | 10 | **F** | 3 步线性诊断 | B |
| 5 | 六、随意开关门 | 10 | **F** | DIP→配件→遥控→换板 | B |
| 6 | 十三、运行慢 | 12 | **F** | 5 步顺序 | B |
| 7 | **§十二 partial** | **11** | **P** | prod 2 组；orphan 子场景 | B |
| 8 | 九、走停或反弹 | 21 | **F** | 1–6 顺序 + 附录 follow-up；**无** install/stall 互斥（核实 ✅） | B |
| 9 | 十五、电机转臂不伸缩 | 16 | **L-scenario** | 两场景拆 H2；topens×2；无 amazon | B |
| 10 | 十七、离合打不开 | 22 | **L-scenario** | 编号排查 + 条件 if；YouTube×3 | B |
| 11 | 十六、机臂异响 | 35 | **DT** | 1→2 **或** 1→5 观察跳转；线性 ladder 误导（核实 ✅） | B |

---

## 建议批次（修订）

| 批 | 节 | 段 | Tag | 备注 |
| ---: | --- | ---: | :---: | --- |
| **1** | 十八+七+八+六 | 33 | F×4 | pilot · **可先做** |
| **2** | 一个机臂+十三 | 22 | F×2 | |
| **3** | §十二 partial | 11 | P | 单独批 · 验收 [`bl_ext01b_batch3_acceptance.md`](./bl_ext01b_batch3_acceptance.md) |
| **4** | 十五 | 16 | L-scenario | 2 H2 |
| **5** | **九** | 21 | **F** | 原标 L → **F** |
| **6** | 十七 | 22 | L-scenario | |
| **7** | **十六** | 35 | **DT** | **非收尾** · 须 qa_024 级设计闭环（schema/展示）后再 extract；可拆 **BL-EXT-01b-DT** 子项 |

批 1 进行同时 §九/§十六 核实 ✅ 已完成（见核实附录）。

---

## 与 BL-EXT-01 关系

§十四 / §十九 已收口；不在本表重复。

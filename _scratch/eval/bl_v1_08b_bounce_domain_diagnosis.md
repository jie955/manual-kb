# BL-V1-08b · §十/十一 到位反弹语义域（AD5S + A3S 对照）

**状态**：Phase 1 ✅ AD5S · Phase 2 ✅ A3S（无需 overlay · V1-08 已覆盖）· **bounce 域 gate 完成**  
**触发**：BL-V1-03 c04–c07 Top1 miss · 与 BL-V1-08 §十二限位域同构 · 2026-07-05

---

## 模式结论

**与限位域同一类文档结构问题** — 「拉/推 · 开/关 · 到位反弹 vs 限位不到位 vs 中途反弹」共用 install_mode 标题，embedding 撞车。

| 库 | 撞车组 | 典型 miss |
| --- | --- | --- |
| **AD5S** | qa_016–019 四组「拉/推开门安装」· + qa_040 §九中途 | c04–c07 → qa_037/020/021 或 qa_040 |
| **A3S** | qa_015–016 §九关反弹 | q19 · **BL-V1-08 Phase2 已症状化** |

**BL-V1-08 关闭的是 §十二限位域** — bounce 域独立 backlog，不得混称「反弹/限位全库已解」。

---

## AD5S Phase 1 范围

| group | section | 改前 | 子场景 |
| --- | --- | --- | --- |
| qa_016 | §十 | 拉开门安装 | 开到位反弹 · pull |
| qa_017 | §十 | 推开门安装 | 开到位反弹 · push · 限位B |
| qa_018 | §十一 | 拉开门安装 | 关到位反弹 · pull · 限位B |
| qa_019 | §十一 | 推开门安装 | 关到位反弹 · push |

**Gate**：c04–c07 Top1 · b10 qa_040 无回归 · 全库 47 条 + §十二 r12/l12 无回归

---

## 关联

- [`bl_v1_08_limit_domain_diagnosis.md`](./bl_v1_08_limit_domain_diagnosis.md) — 限位域
- [`bl_v1_03_execution_record.md`](./bl_v1_03_execution_record.md) — c04–c07 miss 留档

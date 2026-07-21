# BL-V1-08 · §十二「限位不到位」语义域歧义（AD5S + A3S 对照）

**状态**：Phase 1 ✅ AD5S · Phase 2 ✅ A3S · **BL-V1-08 关闭**  
**总览对照**：[`bl_v1_08_limit_domain_diagnosis.md`](./bl_v1_08_limit_domain_diagnosis.md)  
**发现**：Batch3 §十二 baseline + fix 后 legacy probe · BL-V1-02 q19–q25 · 2026-07-05

> **跨库**：同类问题在 **A3S**（qa_015/017–021）同样存在 — **处理 AD5S 后须同步检查 A3S**，不得视为「限位域混淆已全库解决」。方案不必相同，诊断模式同构（见对照文档）。

---

## 问题（两层 · 须合并处理）

### 1. qa_020 / qa_021 标题撞车（overlay 前 baseline 已存在）

| group | section | prod `question` |
| --- | --- | --- |
| qa_020 | 十二、不限位 | **推开门安装** For push-to-open installation |
| qa_021 | 十二、不限位 | **推开门安装** For push-to-open installation |

两组合并 **question 标题完全相同**，embedding 空间高度重叠。

### 2. 三方语义重叠 + 客户真实搜法（Batch3 fix 后 legacy probe 暴露）

**不限于 qa_020/021 两两撞车** — 在「限位不到位 / 不限位」语义域内，**三组均有重叠**：

| group | 子场景 | 限位 |
| --- | --- | --- |
| **qa_020** | 推/拉开门 · **关门**不到位 | 限位 B |
| **qa_021** | 推开门 · **关不到位** · 磁环/短接 | 限位 A（外移） |
| **qa_037** | 拉开门 · **开门**过位/不停 | 限位 A（开位） |

客户实际搜索时 **大概率不带 A/B 区分**，而是笼统说「门不限位」「关不到位 不限位」等 — eval 里带限位 A/B 的 query 能锚定 expected，但 **不能代表真实 query 分布**。

| query 类型 | 示例 | fix 后 Top1 | 风险 |
| --- | --- | --- | --- |
| eval 锚点（带 A/B） | r12b「推开门 关不到位 **限位B**」 | qa_020 ✅ | 有区分信号，gate 有效 |
| **legacy / 客户式** | 「推开门 关不到位 **不限位**」 | **qa_037** ⚠️ | 关门问题被引到 **开门限位** 答案 |

→ 若客户遇到的是关门限位问题，可能被误导到 qa_037（讲开门限位 A）。**Batch3 未弱化 gate**（r12b 改 query 是加区分信号，非改 expected 凑通过），但 **legacy 模式须在本项一并解决**。

---

## 证据

### overlay 前 baseline（与 Batch3 orphan 无关）

| query | expected | baseline Top1 | Top2 |
| --- | --- | --- | --- |
| r12b「推开门 关不到位 不限位」 | qa_021 | **qa_020** (0.7122) | qa_021 (0.6918) |

### Batch3 fix 后 legacy probe（三方混淆）

| query | Top1 | 说明 |
| --- | --- | --- |
| 「推开门 关不到位 **不限位**」 | **qa_037** (≈0.725) | 关门语义 → 开门组 |
| r12b「…**限位B**」（eval 锚点） | qa_020 ✅ | 区分信号有效 |

---

## 与 Batch3 边界

| 项 | Batch3（已完成） | BL-V1-08（另排） |
| --- | --- | --- |
| 范围 | §十二 **11 段 orphan** → qa_037 | **qa_020/021/037** 标题与 embedding 域整体梳理 |
| r12a/r12b | A/B 症状 query 锚定 · 无 qa_037 抢 Top1 | **泛化「不限位」** query 亦须 Top1 正确 |
| qa_037 | question/answer 首行收窄开位语义 | 与 020/021 **关门** 域进一步解耦 |

---

## 建议修复方向（V1-08 实施时 · 一次性三方想清楚）

**不要**只改 qa_020/021 标题后再发现 qa_037 仍抢 legacy query — 三组同批设计：

1. **question / embedding_text** 按 **开/关 · 限位 A/B · 拉/推** 显式区分（非共用 install_mode 标题）
2. **qa_037** 保持开位语义；**qa_020/021** 强调关门限位；考虑 answer 首行症状标签（同 Batch3 qa_037 fix 思路）
3. **eval 扩展**：除 r12a/r12b/b07 外，增加 **无 A/B 的 legacy 口语 query** 作 gate（客户式搜法）
4. re-embed 范围：§十二 相关 4 组（020/021/037 + 若拆则含新组）

示例方向（非定稿）：

- qa_020：关不到位 · 限位 B · 推/拉混排
- qa_021：关不到位 · 限位 A 外移 · 磁环/控制板短接
- qa_037：开门过位不停 · 限位 A 开位 · 拉开门（已有 fix 基础）

改后须：r12a/r12b/b07 + **legacy「不限位」** 各 Top1 稳定 · 不回归 batch1–3 · AD5S eval 更新

**Phase 1 结果**（2026-07-05）：33/33 Top1 · l12 Top1=qa_020（acceptable）· b07=qa_037 · 见 [`bl_v1_08_ad5s_execution_record.md`](./bl_v1_08_ad5s_execution_record.md)

---

## 关联

- BL-V1-03 eval 覆盖（§十二 已由 r12a/r12b/b07 部分闭合；legacy query 待本项）
- [`bl_ext01b_batch3_execution_record.md`](./bl_ext01b_batch3_execution_record.md) §legacy probe
- [`bl_ext01b_batch3_acceptance.md`](./bl_ext01b_batch3_acceptance.md) §B r12b 后验条件

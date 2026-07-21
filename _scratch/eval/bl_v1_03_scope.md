# BL-V1-03 · 范围定稿（2026-07-05）

**状态**：进行中 · **当前焦点** AD5S eval 补全 + A3S q27 acceptable

---

## 四项与本轮关系

| # | 内容 | 本轮 | 说明 |
| --- | --- | :---: | --- |
| **1** | AD5S **13 组**无 eval 主期望触及 | **✅ gate** | 每组 ≥1 条 query · 设计 + 跑 Top1 |
| **2** | A3S **q27** acceptable（qa_023/024） | **✅ gate** | 与 BL-V1-08 约定一致 · 顺手关闭 |
| **3** | EXT-01b **口语变体密度**审计 | **审计 + spot-fix** | 不全库扩到 3 条/组；**RED 才加 query** |
| **4** | **覆盖率分母**重算 | **✅ gate** | 随 1 完成 · 更新 `coverage_table.md` + eval JSON header |

**不在本轮**：qa_023 复杂 branch 全矩阵（→ **BL-V1-04 / qa_023 专项**）· AD5S §十/十一 bounce **embedding 改标题**（→ 若 c06–c09 Top1 miss 再开 BL-V1-08 子项）

---

## Item 1 · 13 组 query 设计（AD5S）

| 新 id | group | query 方向 | category |
| --- | --- | --- | --- |
| c01 | qa_007 | 只有一个遥控器坏了 其他的还能用 | colloquial |
| c02 | qa_009 | 要多按几次遥控门机才动 | colloquial |
| c03 | qa_015 | 双机臂只能朝一个方向开关 | colloquial · acceptable qa_014 |
| c04 | qa_016 | 门开到位又弹回来 拉开门 | colloquial |
| c05 | qa_017 | 推开门 开门反弹怎么调 | colloquial |
| c06 | qa_018 | 门关到位又弹回来 拉开门 | colloquial |
| c07 | qa_019 | 推开门 关门反弹怎么调 | colloquial |
| c08 | qa_023 | 电机电流小 机臂红黑线并接怎么测 | colloquial |
| c09 | qa_025 | 双机臂遇阻反弹 怎么判断主从门 | colloquial |
| c10 | qa_026 | 限位开关常闭 只开不关怎么回事 | colloquial |
| c11 | qa_027 | AD5S电池多大 太阳能板配多少 | colloquial |
| c12 | qa_028 | 冬天机臂结冰怎么保养 | colloquial · translated_group 压测 |
| c13 | qa_030 | gate opener 日常维护指南链接 | title_paraphrase · 空 ZH 组 |

**关闭条件**：43 组 **主期望覆盖 40/43（100% 除 acceptable-only 3 组）** → 实际目标 **40/43 primary**（qa_021/024/029 仍可为 acceptable-only）

---

## Item 3 · 口语变体审计（spot-fix 规则）

| 组集 | 当前 | 审计标准 | 动作 |
| --- | --- | --- | --- |
| **qa_022** translated_group | a14 + a14b（2 条） | 排期 ≥3 **口语** | **加 a16** colloquial |
| **qa_031–043** EXT-01b | b01–b14 各 1–2 条 · 多数 colloquial | 无「仅 title_paraphrase 且无口语」 | 审计留档 · **本轮不加** |
| **c12 qa_028** | 新增 1 条 | thin-ZH 组须 colloquial | 已含于 c12 |

---

## Item 2 · A3S q27

```json
"acceptable_group_ids": ["qa_024", "qa_023"]
```

Top1 仍计 miss · Top3 gate 绿 · 与 b09/b12 同类 confusable 处理。

---

## 交付物

- `eval_queries_ad5s.json` v3（+c01–c13 · +a16）
- `eval_queries.json` v2.1（q27 acceptable）
- `_scratch/eval/bl_v1_03_ad5s_eval.json` · 全库 Top1 留档
- `coverage_table.md` 分母更新
- `bl_v1_03_execution_record.md`（跑完写）

# Troubleshooting Chunk Schema v1（复杂档定稿草案）

**状态**：**qa_024 复杂档 pilot + 浏览器 D2b ✅**（2026-07-03）· 闭环见 [`qa_024_branch_closure.md`](./qa_024_branch_closure.md)  
**前置**：[`ad5s_link_condition_scan.md`](./ad5s_link_condition_scan.md) 语义分类核对 · BL-V1-06 ✅  
**范围**：docx 排查线 `qa_groups.json` / `chunks.json` · AD5S §十四及同型组

---

## 1. 设计原则

| 原则 | 说明 |
| --- | --- |
| 两结构拆分 | `troubleshooting_ladder[]`（顺序梯）与 `branches[]`（互斥分支）**不共用**一个 `condition` 字段 |
| 嵌套而非平行 | `branches[]` 挂在 **ladder 具体步骤**下（`troubleshooting_ladder[].branches`），不挂在 chunk 根上与 ladder 平行 |
| 正交叠加 | qa_024：步骤 1→2 全员走同一梯；**到步骤 3 加电阻**才按 region/方向分支 |
| 简单档不变 | 无分支、无梯结构时（qa_003/010）仍用根级 `links[]` + `answer_zh`/`answer_en` |

---

## 2. 顶层 chunk / group 对象

```json
{
  "group_id": "qa_024",
  "section": "十四、电机电流小导致走停 …",
  "question": "手动反推来排查+电阻",
  "answer_zh": "…",
  "answer_en": "…",
  "images": ["image_026.png"],
  "links": [],
  "negotiation_offers": [],
  "troubleshooting_ladder": []
}
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `answer_zh` / `answer_en` | string | 是 | 完整 prose；extract 可从 ladder 合成，或 ladder 为空时即主内容 |
| `links` | `Link[]` | 否 | **简单档**：chunk 级无条件外链（qa_003 topens） |
| `negotiation_offers` | `NegotiationOffer[]` | 否 | BL-V1-06 已落地 |
| `troubleshooting_ladder` | `LadderStep[]` | 否 | 有顺序排查梯时填充；无则省略或 `[]` |
| `images` | string[] | 否 | 与现 schema 同 |

**不含** chunk 根级 `branches[]`。

---

## 3. `troubleshooting_ladder[]` · 顺序排查梯

### 3.1 展示语义

- **默认全展示、按 `step_index` 升序**
- 客户不知会卡在哪一步 → 不按条件过滤步骤
- 含 `branches` 的步骤：先展示该步通用说明，再按用户上下文 **过滤 branches**（见 §4）

### 3.2 `LadderStep` 字段

```json
{
  "step_index": 3,
  "content_zh": "如果第二步没发现问题，那就需要加电阻…",
  "content_en": "3 If the problem persists, adding some load to the gate motor…",
  "is_last_resort": false,
  "images": [],
  "branches": [],
  "links": []
}
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `step_index` | integer ≥ 1 | 是 | 文档中的步骤编号（1-based） |
| `content_zh` / `content_en` | string | 是 | 该步正文（分支前的共用引导语） |
| `is_last_resort` | boolean | 否，默认 `false` | **`true`**：展示层加「若以上步骤均无效」类视觉提示（qa_008 Step 4 ERM12） |
| `branches` | `Branch[]` | 否，默认 `[]` | 仅该步需互斥分支时填充（qa_024 步骤 3） |
| `links` | `Link[]` | 否 | 该步无条件外链（整步共享、不分支时） |
| `images` | string[] | 否 | 该步附图 |

### 3.3 `is_last_resort` 取值约定

| 场景 | `is_last_resort` |
| --- | --- |
| 普通中间步（qa_005/010 各步） | `false` |
| 梯末环「终极方案」（qa_008 Step 4 ERM12） | `true` |
| 含 `branches` 的步骤（qa_024 Step 3） | `false`（分支内各自有采购链，非整梯最后一环） |

展示层规则：`is_last_resort === true` 的步骤标题前缀「若以上均无效，」或同级 UI 提示；**不**隐藏前置步骤。

---

## 4. `branches[]` · 互斥分支（嵌套在 LadderStep 下）

### 4.1 嵌套关系（qa_024 范例）

```
troubleshooting_ladder[
  { step_index: 1, branches: [] },          // 反推排查 — 全员
  { step_index: 2, branches: [] },          // 检查铰链 — 全员
  { step_index: 3, branches: [               // 加电阻 — 2 条内容（非 4 条路径）
      { applies_when: { region }, applies_when_any: […, …], links, images, … },
      { applies_when: { region }, applies_when_any: […, …], links, images, … },
  ]},
  { step_index: 4, branches: [] },          // 调 FORCE — 全员
  …
]
```

**不是**从头分支：步骤 1–2 的 `branches` 为空数组；region/方向维度 **仅** 在步骤 3 的 `branches[]` 出现。

### 4.2 `Branch` 字段

```json
{
  "applies_when": { "region": "US" },
  "applies_when_any": [
    { "install_mode": "pull_open", "stall_symptom": "open_abnormal" },
    { "install_mode": "push_open", "stall_symptom": "close_abnormal" }
  ],
  "content_zh": "拉开门开门不正常加二极管电阻（推开门关门不正常）",
  "content_en": "Connect anode of the diode to \"+Motor\"…",
  "images": ["image_026.png", "image_028.png"],
  "links": [ … ]
}
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `applies_when` | object | 否* | 分支级 AND 条件（如 `region`）；与 `applies_when_any` 联用时写共有维度 |
| `applies_when_any` | `AppliesWhen[]` | 否 | **OR**：任一路径与 `ctx` 中已提供的 install/stall 维度匹配即可；**不**拆成多条 branch 记录 |
| `content_zh` / `content_en` | string | 否 | 分支特有正文（接线图说明等） |
| `links` | `Link[]` | 否 | 分支级采购/支持链 |
| `images` | string[] | 否 | 分支级附图 |

\* 无 `applies_when` 且无 `applies_when_any` 时视为全员分支（少见）。

### 4.3 展示语义

- 给定用户上下文（或 demo 选择器）→ 在**该步骤**下只展示 **branch 记录**（内容条数），不按 `applies_when_any` 内路径拆成多张卡片
- `applies_when_any` 存在时，标签展示双向路径（如「拉开门·开门不正常 ⇄ 推开门·关门不正常 · 美国」）
- 未提供上下文 → 展示全部 **branch 记录**（qa_024 步骤 3 = **2 张**，非 4 张路径卡片）

---

## 5. `applies_when` · 取值策略（定稿取舍）

### 5.1 决策：**已知维度受控枚举 + 可扩展键**

| 策略 | 选择 | 理由 |
| --- | --- | --- |
| v1 已知维度 | **受控枚举** | 展示层可做确定性匹配、i18n 标签、demo 选择器 |
| 未来维度（型号、固件版等） | **允许附加 string 键** | 不必改 schema 形状；extract 登记进维度注册表即可 |

**不采用**全自由文本作为主路径（展示层无法稳定匹配）；**不采用**纯枚举不可扩展（AD8S/新型号会受阻）。

### 5.2 v1 注册维度与枚举

```typescript
// 逻辑类型（文档用，非运行时 TS 文件）

type AppliesWhen = {
  region?: "US" | "UK" | "EU" | "other";
  install_mode?: "pull_open" | "push_open";
  stall_symptom?: "open_abnormal" | "close_abnormal";
  // 扩展：product_model?: string;  // 未来登记后使用
  [key: string]: string | undefined;  // 仅允许 string 值；未知键展示为原始标签
};
```

| 维度 | 枚举值 | 典型文档表述 |
| --- | --- | --- |
| `region` | `US` · `UK` · `EU` · `other` | amazon.com / .co.uk；「注意链接国家」 |
| `install_mode` | `pull_open` · `push_open` | 拉开门 / 推开门安装 |
| `stall_symptom` | `open_abnormal` · `close_abnormal` | 开门不正常 / 关门不正常（走停方向） |

**组合语义**：

- 单 `applies_when` 对象内多键 = **AND**
- `applies_when_any` 数组内每项 = 一条候选路径；与 `ctx` 中 install/stall 比较时 **OR**（任一路径命中即可）
- `applies_when` + `applies_when_any` 联用：`applies_when` 键（如 `region`）须先满足，再在 `applies_when_any` 中找 OR 路径

**extract 约束（写出某 key 时）**：值 **必须** 为注册枚举，禁止自由文本别名（如 `"pull"` → 须规范为 `pull_open`）。**不**要求每个 branch 填满全部已知维度。

### 5.3 维度注册表（维护约定）

新增维度时：

1. 在本节追加枚举定义
2. extract 增加检测规则
3. demo 选择器（若有）增加对应 UI

### 5.4 缺 key = 通配（实现规则）

| 侧 | 规则 |
| --- | --- |
| **Branch · `applies_when`** | 未出现的注册维度键 = **通配**（对该维度不敏感，任意用户上下文值均匹配） |
| **Branch · 写出 key** | 值必须为 §5.2 注册枚举 |
| **Extract** | **有原文或结构证据才写 key**；无证据则 **省略**，禁止推断 |
| **用户上下文** | 用户未提供的维度 → 过滤时 **跳过**该维（不因未选而排除 branch） |

**展示层过滤**（branch 是否匹配用户上下文 `ctx`）：

```python
def branch_matches(branch: dict, ctx: dict) -> bool:
    any_list = branch.get("applies_when_any")
    if any_list:
        for key, required in (branch.get("applies_when") or {}).items():
            if key in ctx and ctx[key] != required:
                return False
        if not {"install_mode", "stall_symptom"} & ctx.keys():
            return True
        return any(
            all(path.get(k) == ctx[k] for k in ("install_mode", "stall_symptom") if k in ctx)
            for path in any_list
        )
    for key, required in (branch.get("applies_when") or {}).items():
        if key not in ctx:
            continue
        if ctx[key] != required:
            return False
    return True
```

实现见 `branch_utils.branch_matches`。

**证据来源示例（qa_024）**：

| 维度 | 有证据时 | 无证据时 |
| --- | --- | --- |
| `install_mode` / `stall_symptom` | ZH 分支标题（如「拉开门开门不正常」） | 不从 EN 接线段推断 |
| `region` | URL domain（amazon.com → `US`） | 不猜 |
| 纯电阻链 | 仅 `region` 可写 | `install_mode` / `stall_symptom` **省略**（通配） |

**qa_024 region 无字段级锚点**：ZH 仅「注意链接国家」（非 US/UK 标签）；`region` 由采购 URL 域名推导，分支标题行与 EN 接线块按**文档顺序**对齐。改版/新型号须人工复核（见 `branch_utils.py` 模块说明）。

**多 match**：用户上下文不全时可能同时命中多条 branch（含通配 branch）→ 展示策略为产品决策，schema 不强制唯一命中。

---

## 6. `Link` 对象（简单档 + 分支级共用）

```json
{
  "url": "https://www.amazon.com/dp/B08HYZV3DW",
  "label": "兼容电阻（第三方）",
  "lang": "en",
  "link_type": "purchase_link",
  "disclaimer": "Regretfully, we do not have this resistor for sale in our store."
}
```

| `link_type` | 说明 |
| --- | --- |
| `video` | YouTube / Drive 视频 |
| `support_page` | topens 官方支持页 |
| `purchase_link` | Amazon 等第三方采购（**须** `disclaimer` 或组级 `disclaimer_no_sale` 已剥离协商） |
| `other` | 其余 |

- **简单档**：`links[]` 在 chunk 根，无 `applies_when`
- **复杂档**：采购链在 `branches[].links[]` 或 ladder 步 `links[]`
- **不再** 使用 chunk 级 `link.condition` 单字段（由 branch 归属表达条件）

---

## 7. 验收用例（首批）

### 7.1 qa_003 · 简单档

- 根级 `links[]` ×1（topens），`troubleshooting_ladder` 省略
- 无 `branches`

### 7.2 qa_008 · 顺序梯 + 末环

```json
"troubleshooting_ladder": [
  { "step_index": 1, "is_last_resort": false, "branches": [] },
  { "step_index": 2, "is_last_resort": false, "branches": [] },
  { "step_index": 3, "is_last_resort": false, "branches": [] },
  {
    "step_index": 4,
    "is_last_resort": true,
    "content_en": "Add an ERM12 External Receiver: …",
    "branches": []
  }
]
```

### 7.3 qa_023 · 协商剥离 + 采购链

- `negotiation_offers[]` 含 M12 协商句；`answer_en` 保留 `purchase the resistors` + disclaimer
- 若仅单链无分支：根级或单步 `links[]` + `link_type: purchase_link`

### 7.4 qa_024 · 梯 + 步骤 3 嵌套 branches（pilot 已验）

- 步骤 1–2：`branches: []`
- 步骤 3：`branches` ×**2**（每套接线内容一条；`applies_when_any` 含 2 组镜像 install/stall 路径；`region` 在 `applies_when`）
- 步骤 3 共享：`links` ×1 通配 US 电阻链（`applies_when: { region: US }` only）
- 步骤 4：调 FORCE — `branches: []`（测电流仍在 parent prose，未入 ladder）
- branch 级 `images`：US → 026+028；UK → 027+029（见 `branch_utils.QA_024_BRANCH_IMAGES`）

**展示验收**（[`verify_qa_024_acceptance.py`](./verify_qa_024_acceptance.py)）：

| ctx | 步骤 3 卡片数 | US 配图 |
| --- | --- | --- |
| `{}` | 2 | 026, 028, 027, 029（demo 带提示） |
| `{ region: US }` | 1 | 026, 028（**无 027**） |
| `{ push_open, close_abnormal, region: US }` | 1；标签 ⇄；`content_en` 含 +Motor | 026, 028 |

**未切换**：~~prod 仍为旧结构~~ → **prod 阶段 1 已切换**（2026-07-03）；阶段 2 qa_008 见 [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md)。

### 7.5 qa_027 · 规格说明（负例）

- **无** `troubleshooting_ladder`、**无** `branches`
- `external receiver` 功耗说明留在 `answer_zh`/`answer_en` 主 prose

---

## 8. 与扫描脚本的关系

| 产物 | 权威性 |
| --- | --- |
| `ad5s_link_condition_scan.py` 输出 | **仅供人工参考**，启发式有误报 |
| 本文 schema + extract 输出 | **权威** |
| `ad5s_link_condition_scan.md`「语义分类」节 | 人工核对附录，脚本重跑时保留 |

---

## 9. 实现状态（2026-07-03）

| # | 项 | 状态 |
| --- | --- | --- |
| 1 | `qa_doc_extractor`：ladder / qa_024 branch（`attach_qa_024_structure`） | ✅ pilot |
| 2 | `link_utils`：`purchase_link` + disclaimer | ✅ |
| 3 | `chunk_builder`：透传 `troubleshooting_ladder` | ✅ pilot |
| 4 | demo：ladder + `applies_when_any` 过滤 + ⇄ 标签 + branch 配图 | ✅ pilot · **浏览器 D2b**（[`qa_024_branch_closure.md`](./qa_024_branch_closure.md) §4.2） |
| 5 | qa_003/010/030 简单档 + qa_023 ladder prod | **✅ 2026-07-05** · [`bl_v1_04_execution_record.md`](./bl_v1_04_execution_record.md) |
| 6 | `generate_answer` 使用 ladder 结构 | 待做 |
| 7 | prod `run-ad5s` chroma 切换 | **阶段 1 qa_024 ✅** · **阶段 2 qa_008 ✅**（2026-07-03）· 混合态 M1–M3 ✅（2026-07-05）· [`ad5s_prod_switch_plan.md`](./ad5s_prod_switch_plan.md) §12–15 |

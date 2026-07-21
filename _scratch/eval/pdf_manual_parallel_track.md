# PDF / Manual · B 轴并行轨道留档

**性质**：任务与交付 · **并行轨道**（非 Wave 1 进度）  
**日期**：2026-07-11  
**关联**：[Wave 1–4 执行清单 · C 轴](./cs_en_poc_execution.md) · [组件化 ADR · 质量门禁未关闭](../../docs/adr/企业%20RAG%20邮件助手组件化重构方案.md) · [过拟合分类 · Round 1e/holdout](../eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md) · [A3S manual 真源](../vlm_a3s_full/README.md)

---

## 并行轨道声明（必读）

本文件仅推进 **B 轴**（说明书检索 · manual 配图 · catalog 静态链）与 **V2 PDF 基础设施**。

| 本轨道 **不代表** | 本轨道 **不替代** |
| --- | --- |
| Wave 1（C 轴）有任何关闭或发链许可 | 22 封真邮 xlsx E–H · holdout · 桶 A/B/C/D 通用修复 |
| 「进度往前走了」的对外口径 | 殷主管 MVP **≥16/19** 真邮通过率 |

**硬规则**：**P1（manual enrich / 7→9/10）不得在 Wave 1 未关时作为主任务占用带宽**；最多 shadow / 留档设计，不得以 manual Top1 分数冒充 C 轴进展。

C 轴真源与 Exit：[cs_en_poc_execution.md § Wave 1](./cs_en_poc_execution.md#wave-1--准确率攻克殷主管-二先攻克准确率--3-5-天)

---

## 三轴现状（2026-07-11 · 引用真源）

| 轴 | 项 | 状态 |
| --- | --- | --- |
| **C** | 人工 xlsx E–H · MVP ≥16/19 | ☐ / ❌ |
| **C** | holdout T1–T5 · 桶 A/B/C/D 通用修复 | 未关 · 见 [fix_classification…](../eval_runs/fix_classification_holdout_and_round1e_2026-07-10.md) |
| **B** | troubleshooting + manual merge 接线 | ⚠️ 机器侧部分完成 · [client_mvp…](./client_mvp_two_series_progress.md) |
| **B** | manual 配图 / catalog 静态链 | 本轨道 |
| **A** | 稳定 URL + 试跑包 | ❌ |

发链 DoD（三轴同时）：[cs_client_requirement_standard.md §5.6](./cs_client_requirement_standard.md)

---

## 人力分配（量化 · 防「有限并行」被稀释）

**原则**：Wave 1 未关期间，**B 轴合计 ≤ 本周工程人天的 25%**；P1 = **0% 主任务**。

| 周期示例 | 任务 | 人天预算 | 占比 cap |
| --- | --- | ---: | ---: |
| **本周（Wave 1 主关）** | W1 · xlsx E–H · 桶 A/B/C/D 通用修复 · Round 1 patch_off 对照 | **3.5–4.0** | **≥75%** |
| 同上 | P0-A · catalog 静态链验收 + precheck JSON | **0.5** | ≤25% |
| 同上 | P0-B · 四库 pages + image fallback（过渡态） | **1.0–1.5** | （含在上限内） |
| 同上 | **P1 · manual enrich** | **0**（主任务禁止） | 0% |
| **Wave 1 Exit 后** | P1 + P1-H holdout | **1.5–2.0** | 可升为主任务 |
| **Wave 1 + P1-H 绿** | P2 · Wave 4 部署打包 | **1.0–2.0** | 须 A+B+C 齐 |

**周报必填一行**（粘贴到内部进度即可）：

```text
B轴并行：本周投入 __ 人天 / 总 __ 人天 = __% ；Wave1：__ 人天 ；P1主任务：是/否（须否至W1 Exit）
```

---

## 执行顺序（修订版 · 2026-07-11）

```text
【主关 · Wave 1 · C 轴】
  W1.0  22 封 + holdout → 人工 xlsx E–H（②③优先）
  W1.1  桶 A/B/C/D 通用修复（禁止 per-cs_id brief / mandatory 4-step）
  W1.2  Round 1 patch_off 对照 → MVP ≥16/19；holdout 不劣化

【并行 · B 轴 · 不表示 Wave 1 进展】
  P0-A  catalog 静态链验收 + precheck JSON
  P0-B  四库 pages + image fallback（MVP-IMG-FALLBACK）

【Wave 1 Exit + holdout 纪律建立后】
  P1    manual 通用 disambiguation enrich（非三 query 补丁）
  P1-H  holdout 基线 → enrich → holdout 复测（双门槛）
  P2    Wave 4 部署（A+B+C）
```

**禁止**：整包按「P0 → P1 → P2」当主序开工（会把 C 轴挤到后面）。

---

## P0-A · catalog 静态链（不 ingest）

| # | 动作 | Gate |
| ---: | --- | --- |
| 1 | 确认一期决策：四份 `samples/catalog/*.pdf` **不 VLM ingest**；静态链见 `domains/topens/products.yaml` | 书面 ✅ |
| 2 | cs-email Demo 手测 Product resources 栏可点 | 截图留档 |
| 3 | `scripts/precheck_catalog_pdfs.py`（待建）→ `_scratch/catalog/_precheck.json` | 页数 · 文本层 · 建议 |

---

## P0-B · manual 配图（过渡态）

**标签**：`MVP-IMG-FALLBACK`

| 项 | 说明 |
| --- | --- |
| **做什么** | 四库 `--skip-parse` 渲页 → `pages/`；缺 `images/*.png` 时整页回退 |
| **不是什么** | BL-PDF-02 精确裁切 · 图文对诊断点 · 「配图完成 ✅」 |
| **产品差距** | 客户看到的是**整页扫描图**，非对应接线图/示意图 — 与殷主管「图文结合、图对诊断点」仍有距离 |
| **验收上限** | ⚠️ **可展示（整页回退）** · 404 消除 ≠ 配图项结案 |

**命令（单库模板）**：

```powershell
python _scratch/vlm_a3s_full/run_full.py --skip-parse --skip-renormalize --skip-adapter --skip-enrich --skip-embed
# ad5s / at6132s / tc148 同理
```

**Gate**：manual 相关 query 命中时 `/images/` 非 404（手测或 `demo_checklist_probe` spot-check）。

---

## P1 · A3S manual 检索（Wave 1 Exit 后主任务）

**训练集（开发对照 · 非唯一 Gate）**：现有 10 条探针 · [`topk_full.json`](../vlm_a3s_full/eval/topk_full.json) · 当前 **7/10**（vector + hybrid_0.6）。

**三条 miss（仅作诊断，禁止逐条写补丁词）**：

| Query | 抢走 | 期望 | 通用方向 |
| --- | --- | --- | --- |
| BAT 端子给系统供电 | p35 HLR01 | p18-terminal | 端子 vs accessory disambiguation（规则级） |
| 安装前安全注意事项 | p8 | p2-warning-* | 期望 id 精确到 child；安全 vs 安装 note |
| 电源接线 | p23 | p20 | 主电源 p20 vs UPS01 p23（已有 enrich 钩子，调**规则**非三句 query） |

**禁止**：针对上述三句 query 写「p8/p35/p23 负向关键词」式 EvalPack 补丁 — 与 Round 1e `generation_brief` 同罪。

**开发 Gate（训练集）**：≥9/10 **或** 三 miss 期望块均 ≥Top2 — ** alone 不得对外宣称达标**。

---

## P1-H · holdout 泛化验证

### 泄漏检查（正式用前必做）

| 检查项 | 要求 |
| --- | --- |
| 与训练 10 条 **零重叠** | query 文本 · 期望 chunk_id 均不重复 |
| 与 Round 1e / T1–T5 **无混用** | holdout 文件独立命名 · 不进 `probe_topk_misses.py` 默认 `PROBES` |
| **H3 特殊** | HomeLink / p35 与 P1 enrich **直接相关** — H3 问句须：**(a) 未参与 P1 enrich 实现者编写**，或 **(b) 真实客户/员工原始问法**（邮件/工单/口述记录），**禁止** enrich 作者现编措辞 |
| enrich 设计评审 | 任何人不得持 holdout 问句列表参与关键词设计；holdout 文件 **git 提交前** 与 enrich PR **分人** |

### Holdout 候选（待泄漏检查 + H3 外部问法锁定）

| ID | 用途 | 期望块（初稿 · 可随基线调整） | 备注 |
| --- | --- | --- | --- |
| H1 | 限位域 | p39/p40 附近 | 勿被 p18 端子表吸走 |
| H2 | 太阳能 UPS01 | p23 | 勿被 p20 主电源抢 Top1 |
| H3 | accessory · p35 | p35 合法块 | **问句来源见上 · 待锁定** |
| H4 | batch 外 STEP | p11 | Pull 安装排序 |
| H5 | 装箱/配件 | p4/p5 | 与安全/端子 disambiguation 无关 |

产物路径（待建）：

- `_scratch/vlm_a3s_full/eval/topk_a3s_manual_holdout.json` — 5 条 query + expected（**H3 锁定后写入**）
- `_scratch/vlm_a3s_full/eval/topk_holdout_baseline_pre01b.json` — **enrich 前基线**
- `_scratch/vlm_a3s_full/eval/topk_holdout_post01b.json` — enrich 后

### 基线先行（regression 判定口径）

**在任意 enrich 改动之前**，对 holdout 5 条跑一遍当前 `chroma_enriched`，留档每条：

| 字段 | 含义 |
| --- | --- |
| `expected_rank_pre` | 期望块在 Top-K 中的 rank；**无则记 `null`（Top-K 外）** |
| `top1_pre` | 改前 Top1 chunk_id |

**Regression 定义（仅针对本次 enrich）**：

| 改前 rank | enrich 后 | 判定 |
| --- | --- | --- |
| ≤5 | >5 或 null | ❌ **本次 enrich regression** — 须回滚或改规则 |
| null（本就不在 Top-5） | 仍 null | ⚠️ **预存缺口** — 不归因本次 enrich；可记 backlog |
| null | 进入 Top-5 | ✅ 改善（不计 regression） |
| ≤5 | 仍 ≤5 且未劣化 | ✅ |

**双门槛（enrich 后同时满足才可关 P1）**：

1. **训练集**：≥9/10 或 三 miss ≥Top2（开发报告）
2. **Holdout**：≥4/5 Top1 **且** **0 条 regression**（上表定义）

```powershell
# 1) enrich 前基线（当前索引 · 无新 enrich）
python _scratch/vlm_batch/probe_topk_misses.py _scratch/vlm_a3s_full/chroma_enriched `
  --out _scratch/vlm_a3s_full/eval/topk_holdout_baseline_pre01b.json
# TODO: 脚本扩展 --probes-file 读 holdout JSON；暂可 fork 探针列表

# 2) enrich + re-embed 后
python _scratch/vlm_batch/probe_topk_misses.py _scratch/vlm_a3s_full/chroma_enriched `
  --out _scratch/vlm_a3s_full/eval/topk_holdout_post01b.json
```

### 13 页 batch 回归

`vlm_batch/chroma_enriched` **10/10 不得回退** — enrich 改动须对照 batch 库同探针（纪律同 Wave 1 patch_off）。

---

## P2 · 部署（Wave 1 Exit + P1-H 绿 + A 轴就绪）

见 [cs_en_poc_execution.md § Wave 4](./cs_en_poc_execution.md#wave-4--部署--发殷主管测试链接1-2-天)。打包须含：排查 EN chroma · merged · `run-006/images` · manual `pages/` 或 fallback `images/` · 启动参数 `--allowed-libraries a3s,ad5s`。

---

## 明确不做（本轨道边界）

| 项 | 原因 |
| --- | --- |
| catalog 四 PDF VLM ingest | MVP 静态链已够 |
| AT6132S 接 Demo | A3S P1-H 绿后再议 |
| 重跑四库 VLM | 页已齐 |
| docx 排查线改动 | V1 已结案 |
| P1 在 Wave 1 未关时作主任务 | C 轴硬关 · 过拟合纪律 |

---

## 变更记录

| 日期 | 变更 |
| --- | --- |
| 2026-07-11 | 初版：并行轨道声明 · 人力 cap · P0/P1/P1-H · holdout 基线口径 · H3 泄漏检查 |

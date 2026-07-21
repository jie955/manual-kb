# VLM Small Batch · A3S 13 pages

A3S 说明书小批量 VLM 管线：13 印刷页（安装 STEP + 纯表 + 警告 + 装箱），覆盖 pull/push 安装、规格表、端子表、接线与供电警示。

## 页选择（`page_manifest.json`）

| 印刷页 | pdf_index | page_type | chapter_hint |
| ---: | ---: | --- | --- |
| 2 | 4 | warning | Important Safety Information |
| 4 | 6 | packing | Packing List |
| 6 | 8 | spec_table | Specifications |
| 7 | 9 | other | Before You Begin — tools |
| 8 | 10 | step_mixed | Post stability / gate swing |
| 9 | 11 | step_mixed | Pull-to-Open STEP 1-2 (**pilot**) |
| 10 | 12 | step_mixed | Pull-to-Open STEP 3-5 |
| 11 | 13 | step_mixed | Pull-to-Open STEP 6-7 |
| 13 | 15 | step_mixed | Push-to-Open STEP 1-2 |
| 17 | 19 | step_mixed | Mount Control Box |
| 18 | 20 | spec_table | Terminal Function (**pilot**) |
| 19 | 21 | step_mixed | Connect Arm to Control Board |
| 20 | 22 | warning | Connection of Power Supply |

类型覆盖：step_mixed ×8、spec_table ×2、warning ×2、packing ×1、other ×1。

## 流水线

```powershell
# 一键（渲页 → 解析 → adapter → embed）
python _scratch/vlm_batch/run_batch.py

# 分步
python _scratch/vlm_batch/batch_render.py
python pdf_vlm_parser.py --manifest _scratch/vlm_batch/page_manifest.json `
    --pages-dir _scratch/vlm_batch/pages `
    --out _scratch/vlm_batch/manual_chunks.json
python manual_chunk_adapter.py _scratch/vlm_batch/manual_chunks.json `
    _scratch/vlm_batch/chunks.json --images-base _scratch/vlm_batch
python manual_embed_enrich.py _scratch/vlm_batch/chunks.json `
    _scratch/vlm_batch/chunks_enriched.json
python embed_ingest_local.py _scratch/vlm_batch/chunks_enriched.json `
    _scratch/vlm_batch/chroma_enriched `
    --model "D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3"
```

### 检索评测（Retrieval Engineering）

```powershell
# Step1: Top-K 诊断（Vector + Hybrid）
python _scratch/vlm_batch/probe_topk_misses.py --out _scratch/vlm_batch/eval/topk_baseline.json

# Step2–3: enrich 后重 embed，再评测
python manual_embed_enrich.py _scratch/vlm_batch/chunks.json _scratch/vlm_batch/chunks_enriched.json
python embed_ingest_local.py _scratch/vlm_batch/chunks_enriched.json _scratch/vlm_batch/chroma_enriched --model <bge-m3>
python _scratch/vlm_batch/probe_topk_misses.py _scratch/vlm_batch/chroma_enriched --out _scratch/vlm_batch/eval/topk_enriched.json

# 快速探针（推荐 hybrid）
python _scratch/vlm_batch/probe_retrieval.py _scratch/vlm_batch/chroma_enriched --hybrid 0.6
```

| 阶段 | Vector Top1 | Hybrid 0.6 Top1 |
| --- | ---: | ---: |
| baseline（`chroma/`） | 6/10 | 5/10 |
| **enriched（`chroma_enriched/`）** | **10/10** | **10/10** |

四类 miss 在 baseline 下期望块均在 **Top-3**（排序问题，非召回失败）。`manual_embed_enrich.py` 增强别名/章节关键词后全部修复。

详见 `eval/ab_summary.json`、`eval/topk_baseline.json`、`eval/topk_enriched.json`。

### VLM API（全量 13 页解析）

配置与 `caption_images.py` 相同：

```powershell
$env:CAPTION_API_KEY = "your-key"
$env:CAPTION_BASE_URL = "https://你的网关/v1"
$env:CAPTION_MODEL = "gemini-2.5-flash"   # 或 gpt-4o 等 vision 模型

python pdf_vlm_parser.py --manifest _scratch/vlm_batch/page_manifest.json `
    --pages-dir _scratch/vlm_batch/pages `
    --out _scratch/vlm_batch/manual_chunks.json
```

- 缓存：仓库根 `.vlm_cache.json`（同 `.caption_cache.json` 模式）
- p9、p18 默认复用 `_scratch/vlm_pilot/pilot_chunks.json`（即使配了 API 也跳过重复解析）
- 无 API key 时：仅输出 pilot 页 5 块（3 可检索），其余 11 页跳过

## 当前运行结果

| 步骤 | 状态 |
| --- | --- |
| 13 页 VLM | ✅ 54 块 · 41 可检索 · 0 failed |
| 检索 baseline | 6/10（vector） |
| **检索 enriched + hybrid** | ✅ **10/10** — 门禁通过，可扩 52 页 |

### 检索探针（enriched + hybrid 0.6）

10/10 全中（含原 4 条 miss：PHOTO/BAT 端子、Push-to-Open、电源接线）。

## 文件

| 文件 | 说明 |
| --- | --- |
| `page_manifest.json` | 页选择元数据 |
| `batch_render.py` | 批量渲页 |
| `run_batch.py` | 编排脚本 |
| `pages/` | 2x PNG |
| `manual_chunks.json` | VLM / pilot 输出 |
| `chunks_enriched.json` | embedding_text 增强后 |
| `chroma_enriched/` | 推荐检索库（10/10 探针） |
| `eval/` | Top-K 诊断与 A/B 摘要 |
| `probe_topk_misses.py` | 4 miss + 10 探针 Top-5 诊断 |
| `parse_stats.json` | 解析统计与 correction flags |

## 人工校正关注点

全量 VLM 后检查 `parse_stats.json` 中 `correction_flags`：

- `spec_table` 页（p6、p18）须有 `structured.rows` 或 `table_data`
- step_mixed 页内嵌表（p9-step2、p13-step2）示意图与表须分拆 `images[].role`
- 端子表按功能组聚合，勿按印刷行号拆句

## 阻塞项

**全量 10–15 页 VLM** 需配置 `CAPTION_API_KEY`（或 `OPENAI_API_KEY`）及 vision 模型。渲图与管线已就绪，配 key 后重跑 `pdf_vlm_parser.py` + `run_batch.py --skip-render` 即可。

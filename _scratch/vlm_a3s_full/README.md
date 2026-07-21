# A3S 全量 VLM · `_scratch/vlm_a3s_full/`

**源 PDF**：`samples/manuals/A3S,A5(S),A8(S)说明书.pdf`  
**更新**：2026-07-11（可检索 **195** · 与 `chunks_enriched.json` / `chroma_enriched` 核对）

PDF 文件 **52 页**；有效 VLM 目标 **46 页**（封面/目录 idx 0–2 + 印刷页 1–43）；idx 46–51 为空白跳过。

---

## 最终状态（当前磁盘产物）

| 指标 | 值 | 说明 |
| --- | ---: | --- |
| VLM 目标页 | **46** | `page_manifest.json` |
| 页覆盖 | **46/46** | 印刷 1–43 + idx 0/1/2 均有 chunk |
| `manual_chunks.json` | **243 行** | 去重后 **241** 个 `chunk_id`（`p1`、`p3` 各重复 1 条，adapter 去重） |
| `chunks.json` / `chunks_enriched.json` | **241** 块 | 可检索 **195** · parent **46** |
| `chroma_enriched/` | **195** 向量 | 与 enrich 后可检索数一致 |
| `parse_stats.json` | `failed: 0` | 见下方运行史 |

---

## 运行史（三次）

### 1）首次全量（2026-07-02 · API 配额耗尽）

| 项 | 值 |
| --- | --- |
| 成功页 | **33/46**（api 31 + pilot 2） |
| 失败页 **13** | `idx02`·`p06` JSON 解析失败；`p31`·`p34`–`p43` `insufficient_quota`（`p32`·`p33` 已成功） |
| 产出 | 173 manual 行 → adapter 172 → **140** 向量 |
| 日志 | `run_full.log` |

### 2）配额恢复后重跑 VLM（2026-07-02）

全量重跑（缓存命中 31 页，新调 API 12 页）：

| 项 | 值 |
| --- | --- |
| 当次成功 | **45/46**（`p06` 仍 JSON 失败） |
| 当次产出 | 239 manual 行 |
| 日志 | `retry_parse.log` · `parse_stats.json`（当次 `failed: 1`） |

### 3）补洞 + 入库（2026-07-02 晚）

- **p06**：从小批量 `vlm_batch/manual_chunks.json` 合并 **4** 块（规格表页；id 与 batch 一致，chroma 无重复；JSON 无 `_merge_source`）
- 重跑 adapter → enrich → embed

| 项 | 值 |
| --- | --- |
| 最终 manual | **243 行 / 241 唯一 id** |
| 最终向量库 | **195** |
| 日志 | `retry_pipeline.log` |

---

## 流水线

```powershell
# 一键（manifest → 渲页 → VLM → adapter → enrich → embed）
python _scratch/vlm_a3s_full/run_full.py

# 仅后半段（已有 manual_chunks.json）
python _scratch/vlm_a3s_full/run_full.py --skip-manifest --skip-render --skip-parse
```

小批量 `_scratch/vlm_batch/` 的 **`.vlm_cache.json`**（仓库根）与 pilot **p9/p18** 会复用。

**canonical**：本目录为 A3S PDF 交付真源；`vlm_batch/` 为 13 页检索试验场（10/10 gate），非第二套产品库。

---

## 产物

| 路径 | 说明 |
| --- | --- |
| `page_manifest.json` | 46 页元数据 |
| `pages/` | 2x PNG（渲页输出，大文件可能仅本地） |
| `manual_chunks.json` | VLM 原始输出 |
| `chunks.json` | adapter 后（241 块） |
| `chunks_enriched.json` | `manual_embed_enrich` 后 |
| `chroma_enriched/` | 向量库 + `manifest.json` |
| `parse_stats.json` | 最近一次 VLM 统计（`failed: 0`） |
| `eval/topk_full.json` | 全库 10 探针 Vector + Hybrid Top-5 诊断 |

---

## Web demo

```powershell
python qa_server.py `
  --chroma-dir _scratch/vlm_a3s_full/chroma_enriched `
  --images-dir _scratch/vlm_a3s_full/images `
  --model "D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3"
# http://127.0.0.1:8765/
```

用手册类 query（如「立柱支架怎么装」「PHOTO 端子」），勿用 v1 排查 chip。  
配图：`images[].file` 现为绝对路径，demo 可能裂图（见 `docs/排期.md`）。

---

## 检索探针

复用 `_scratch/vlm_batch/probe_retrieval.py` 的 10 条口语 query（**期望页均在 batch 13 页内**）：

```powershell
python _scratch/vlm_batch/probe_topk_misses.py _scratch/vlm_a3s_full/chroma_enriched `
  --out _scratch/vlm_a3s_full/eval/topk_full.json
python _scratch/vlm_batch/probe_retrieval.py _scratch/vlm_a3s_full/chroma_enriched --hybrid 0.6 --model <bge-m3>
```

| 语料 | Hybrid 0.6 Top1 |
| --- | ---: |
| 小批量 13 页（`vlm_batch/chroma_enriched`） | **10/10** |
| 全量 46 页（本目录） | **7/10** |

### 7/10 诊断（2026-07-03 · `eval/topk_full.json`）

| Query | Top1 抢走页 | 期望块 hybrid rank | 判定 |
| --- | --- | ---: | --- |
| BAT 端子给系统供电 | p35（batch 外） | #2 | 扩库排序 |
| 安装前重要安全注意事项 | p8（batch 内） | p2 子块 #3–#5 | batch 内错排 |
| 电源接线 | p23（batch 外） | p20 子块 #5 | 扩库排序 |

**结论**：期望 chunk 仍在 Top-5 → **调检索/enrich**，非 full 解析回归。详见 [`docs/排期.md`](../../docs/排期.md) §6。

**探针注意**：期望 id `a3s-manual-p2` 前缀会误匹配 `p20-*`；eval 宜精确到 child id。

---

## 已知复核项

| 项 | 说明 |
| --- | --- |
| `p13-step2` | `parse_stats.json` · `missing_structured_rows` / `spec_table_without_data` |
| **`p1` / `p3`** | 同 id 两行内容不同 · adapter **静默后写覆盖** — **BL-PDF-04 P0 先于排序调优**（§8） |
| 配图路径 | 待 basename 化以修复 demo `/images/` |
| 7/10 miss | 扩库排序 · **BL-RET-01b** enrich/门禁，非拖后 |

---

## 若需仅重跑后半段

```powershell
python _scratch/vlm_a3s_full/run_full.py --skip-manifest --skip-render --skip-parse
```

若只补个别失败页：全量重跑 VLM 会命中 `.vlm_cache.json`；`--only-pages` 会**覆盖**整份 `manual_chunks.json`，需自行合并，不推荐除非脚本化。

排期总览见 [`docs/排期.md`](../../docs/排期.md)。

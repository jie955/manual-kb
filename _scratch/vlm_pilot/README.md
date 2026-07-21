# VLM Pilot · A3S p9 + p18

A3S 说明书 VLM 试点：3 个检索块 + 2 个页级 parent，验证 manuals 入库适配链路。

## 页码定位

| 印刷页码 | PDF index (0-based) | 输出 |
| ---: | ---: | --- |
| 9 | **11** | `pages/p09.png` |
| 18 | **20** | `pages/p18.png` |

`render_pages.py` 通过页脚数字定位，勿盲信 index 8/17（对应印刷页 6/15）。

## 流水线

```powershell
# 1. 渲页（2x，需 PyMuPDF: pip install pymupdf）
python _scratch/vlm_pilot/render_pages.py

# 2. manual JSON → chunks.json
python manual_chunk_adapter.py _scratch/vlm_pilot/pilot_chunks.json _scratch/vlm_pilot/chunks.json

# 3. 向量化入库（需 bge-m3 本地模型）
python embed_ingest_local.py _scratch/vlm_pilot/chunks.json _scratch/vlm_pilot/chroma --model _scratch/modelscope/BAAI/bge-m3

# 4. 5 条检索探针
python _scratch/vlm_pilot/probe_retrieval.py _scratch/vlm_pilot/chroma --model _scratch/modelscope/BAAI/bge-m3
```

### 模型路径

bge-m3 **不必**在 `manual-kb` 内重复下载，可指向 `qa-doc-extractor` 已有缓存：

```text
D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3
```

若本仓库无模型，可用 ModelScope 下载到 `_scratch/modelscope/`（约 2.3GB，见 `DELIVERY_README.md`）。

## 文件

| 文件 | 说明 |
| --- | --- |
| `render_pages.py` | PyMuPDF 渲指定印刷页 |
| `pilot_chunks.json` | VLM 试点 manual schema（含 parent / structured / table_data） |
| `chunks.json` | adapter 输出，兼容 `embed_ingest_local.py` |
| `pages/` | 整页渲染 PNG |
| `images/` | 块级配图路径（试点阶段复用整页） |
| `probe_retrieval.py` | 5 条 Top1 探针 |

## 检索探针（embed 后验证）

| Query | 期望 Top1 |
| --- | --- |
| 立柱支架和拉式开门支架怎么装 | `a3s-manual-p9-step1` |
| A16cm B14cm 最大开门角度 | `a3s-manual-p9-step2` |
| PHOTO 端子接光电传感器 | `a3s-manual-p18-terminal-table` |
| BAT 端子给系统供电 | `a3s-manual-p18-terminal-table` |
| 限位开关 DLMT ULMT 怎么接 | `a3s-manual-p18-terminal-table` |

## 当前状态

- ✅ 渲页完成（index 11, 20）
- ✅ adapter 产出 5 chunks（3 可检索 + 2 parent）
- ✅ embed + 5/5 检索探针（模型：`qa-doc-extractor/_scratch/modelscope/BAAI/bge-m3`）

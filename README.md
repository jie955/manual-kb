# manual-kb · 手册知识库流水线

docx 结构化提取 → chunk → 本地 embedding → Chroma → Web Demo；含回归门禁与（可选）英文客服生成路径。

| 字段 | 值 |
|------|-----|
| **当前版本** | v1 · Word 排查线（docx 提取已交叉验证；A3S 端到端 run-007 · **18/18 Top1**） |
| **v2 规划** | PDF 说明书 ingest · `samples/manuals/` + `samples/catalog/` |
| **架构决策** | [`docs/adr/`](docs/adr/) |

---

## 能力边界（v1）

- ✅ Word `.docx` · Heading 2/3/4 问答分组 · 父子块 · bge-m3 + Chroma
- ✅ 多份排查 docx 提取交叉验证（A3S / AD5S / TC148）
- ✅ 图片 caption（可选）· `qa_server` + `demo/index.html`
- ✅ 回归门禁：`eval_queries.json` · A3S **18/18 Top1**（B1 配置）
- ⏳ AD5S / TC148 caption + embed + 口语 query 评测
- ⏳ PDF 说明书 · 多型号合并检索
- ⏳ （可选）英文客服生成路径

**产品口径**：回答 = Top1 **`content_zh` 编号步骤** + 配图（非 LLM 改写摘要）。

---

## 快速开始

```powershell
cd D:\pythonProject\manual-kb
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt -r requirements-local.txt

# 首次：ModelScope 下载 bge-m3
pip install modelscope
python -c "from modelscope import snapshot_download; print(snapshot_download('BAAI/bge-m3', cache_dir='_scratch/modelscope'))"

# Demo（预置 run-007）
$env:TRANSFORMERS_OFFLINE = "1"
python qa_server.py --chroma-dir _scratch/run-007/chroma_captioned --images-dir _scratch/run-006/images
# http://127.0.0.1:8765/
```

## 流水线（五步）

```powershell
python qa_doc_extractor.py "samples\troubleshooting\你的手册.docx" "_scratch\run-demo"
python chunk_builder.py "_scratch\run-demo\qa_groups.json" "_scratch\run-demo"
# 可选：python caption_images.py ...
python embed_ingest_local.py "_scratch\run-demo\chunks.json" "_scratch\run-demo\chroma_db" --model "_scratch\modelscope\BAAI\bge-m3"
python eval_run.py "_scratch\run-demo\chroma_db" --model "_scratch\modelscope\BAAI\bge-m3" --name w1_gate
```

## 目录

| 路径 | 说明 |
|------|------|
| `qa_doc_extractor.py` | Word → `qa_groups.json` + `images/` |
| `chunk_builder.py` | 切片真源（`embedding_text` 规则） |
| `embed_ingest_local.py` | bge-m3 + Chroma + `manifest.json` |
| `retrieval_engine.py` | 检索 + parent 回表 |
| `eval_run.py` | 回归门禁 |
| `qa_server.py` · `demo/` | Web 演示 |
| `_scratch/run-007/` | A3S caption 向量库样例 |
| `_scratch/run-ad5s/` · `_scratch/run-tc148/` | AD5S / TC148 提取 + 切片 |
| `samples/` | 本地样例资料（默认 gitignore，见 [`samples/README.md`](samples/README.md)） |
| `docs/adr/` | 架构决策记录 |
| `domains/` | 领域配置（路由 / 提示词 / 评测门禁） |

---

*manual-kb · 知识库流水线 · Word 线 v1*

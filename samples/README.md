# samples · 客户资料目录

**不放密钥** · 大文件默认 **不入 git**（见根 `.gitignore`）。

排期与流水线状态见 [`docs/排期.md`](../docs/排期.md)。

## 子目录

| 目录 | 份数 | 用途 | v1 |
| --- | ---: | --- | --- |
| `troubleshooting/` | 3 docx | 「常见问题排查」；配图 EN crosswalk → [`image_caption_crosswalk.json`](troubleshooting/image_caption_crosswalk.json) | ✅ 当前主线 |
| `customer-service-emails/` | 27 + 规范 | 英文 CS **发版门禁**主语料（22 真实 + 5 测试）+ 176 query · [索引](customer-service-emails/README.md) · [回复原则](customer-service-emails/reply-principles-and-tips.md) · [门禁](_scratch/eval/cs_client_feedback_pack.md) | ✅ 初批 + 测试题 |
| `manuals/` | 4 pdf | 文件名含「说明书」 | v2 · 先归档 |
| `catalog/` | 4 pdf | 短型号概览/参数册 | 预检后再定 ingest 方式 |

## 成均资料清单（2026-07）

| 文件 | 目录 | 流水线 |
| --- | --- | --- |
| A3S-A5S-A8S常见问题排查.docx | `troubleshooting/`（PoC 源亦在 `_scratch/input/`） | ✅ 端到端 run-007 · 18/18 Top1 |
| AD5S-AD8S常见问题排查.docx | `troubleshooting/` | ✅ caption + embed · eval **15/15** Top1 |
| TC148常见问题排查.docx | `troubleshooting/` | ✅ caption + embed · eval **5/6** Top1 |
| A3S,A5(S),A8(S)说明书.pdf | `manuals/` | v2 · **转曲无文本层** · 需 VLM |
| AD5S,AD8S说明书.pdf | `manuals/` | v2 · **转曲无文本层** · 需 VLM |
| AT6132S,AT12132S说明书.pdf | `manuals/` | v2 · **转曲无文本层** · 需 VLM |
| TC148说明书.pdf | `manuals/` | v2 试点首选 · **转曲无文本层** · 配件（墙壁按键） |
| A3,A5,A8.pdf | `catalog/` | 预检后定 |
| AD5, AD8.pdf | `catalog/` | 预检后定 |
| AT6132,AT12132.pdf | `catalog/` | 预检后定 |
| PW302,502,802.pdf | `catalog/` | 预检后定（若实为安装手册再挪 `manuals/`） |

## 提取结果（交叉验证 2026-07-02）

| 文档 | 问答组 | 图片 | 输出目录 |
| --- | ---: | ---: | --- |
| A3S | 28 | 23 | `_scratch/run-006` · `_scratch/run-007` |
| AD5S | 27 | 30 | `_scratch/run-ad5s` |
| TC148 | 2 | 1 | `_scratch/run-tc148` |

TC148 仅 H3×2、无 H1/H2，序号写在问题标题内——真实结构，非漏提取。见排期文档说明。

## 跑批示例

```powershell
# 提取 + 切片（v1 当前工具支持 docx）
python qa_doc_extractor.py "samples\troubleshooting\AD5S-AD8S常见问题排查.docx" "_scratch\run-ad5s"
python chunk_builder.py "_scratch\run-ad5s\qa_groups.json" "_scratch\run-ad5s"

# 下一步：caption → embed（需 API KEY / 本地模型）
python caption_images.py "_scratch\run-ad5s\chunks.json" "_scratch\run-ad5s\images" "_scratch\run-ad5s" --enrich-embedding
python embed_ingest_local.py "_scratch\run-ad5s\chunks_captioned.json" "_scratch\run-ad5s\chroma_captioned" --model _scratch/modelscope/BAAI/bge-m3
```

`manuals/` 与 `catalog/` 内 PDF **先只归档**，当前流水线不支持 PDF。

### PDF 文本层预检（2026-07-02）

四份 `manuals/` PDF 经 PyMuPDF 原生 `get_text()` 检测：**正文标题与段落均不可提取**（仅页码、`◆` 项目符号、目录点线；AD5S/AT6132S 另有开关图 `OFF` 标注）。上传后平台显示的可读文字来自 OCR/VLM，勿误判为「有文本层 PDF」。详见 [`docs/排期.md`](../docs/排期.md) v2 节。

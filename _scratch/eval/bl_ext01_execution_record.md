# BL-EXT-01 执行记录（2026-07-05）

**脚本**：[`phase_bl_ext01_overlay.py`](./phase_bl_ext01_overlay.py)  
**备份**：`_scratch/run-ad5s/*.bak-20260705-bl-ext01`

---

## 变更摘要

| 步 | 内容 | 状态 |
| ---: | --- | :---: |
| 2 | §十四 H1 引言（4 段 zh · 含 50Ω/1152）→ `qa_022.answer_zh` | ✅ |
| 2 | `eval_queries_ad5s.json` a14 改 `zh_en_mixed` · 新增 a14b 公式 query | ✅ |
| 3 | §十九 拆 3 组：`qa_028` 日常 · `qa_029` 深度润滑 · `qa_030` 维护链接 | ✅ |
| 4 | `qa_024` UK branch 补 `B079KCC8P9` 二极管链 | ✅ |

**prod 规模**：30 组 · **55** retrievable vectors（原 27 组 / 52 vectors）

---

## 检索回归

```
eval_queries_ad5s.json · bge-m3 · 16/16 Top1（100%）
```

| ID | query | Top1 | 备注 |
| --- | --- | --- | --- |
| a14 | 门刚动一下就停 电机电流太小 | qa_022 | ZH 引言+EN 混合 |
| a14b | 负载电阻功率要大于1152除以电阻值 | qa_022 | acceptable 含 qa_024 |

`tests.test_branch_utils` **9/9** · `verify_qa_024_acceptance.py` **PASS**

---

## §十九 三组

| group | question | links |
| --- | --- | ---: |
| qa_028 | 日常保养润滑 Routine Maintenance | 0 |
| qa_029 | 深度润滑（拆机臂）Deep Lubrication | 3（YouTube×3） |
| qa_030 | 维护指南链接 Maintenance Guides | 2（topens 博客） |

**浏览器（2026-07-05 · prod `:8765` · Playwright headless）**

| ID | query | top1 | score | flat UI | 链接 | 结果 |
| --- | --- | --- | ---: | --- | --- | --- |
| **N1-prod** | 日常保养润滑 WD40 | qa_028 | 0.6748 | ✅ ladder/filter hidden | 0（预期） | **⚠️minor** 回答区仅 7 字 ZH（`日常保养润滑：`）；WD40 在 `content_en` · demo 未渲染 EN |
| **N2-prod** | 拆机臂内部怎么润滑 | qa_029 | 0.777 | ✅ | **3**× YouTube `<a>` 可点 | **✅** 无 JS 报错 |

脚本：[`sec19_browser_regression.py`](./sec19_browser_regression.py) · **2/2 结构 PASS**（N1 展示层 minor 见上）

> **运维**：embed 后须 **重启** `qa_server`，否则 manifest 仍为旧库（端口占用时易误连 stale 进程）。

---

## 2–4 步正式收尾 ✅

BL-EXT-01b 待触发条件满足后再开（见排期 · inventory §1.3）。

10 节整节 orphan + §十二 partial（148+11 段）— 见 inventory §1.3 · 排期复评触发条件。

---

## 回滚

```powershell
Copy-Item _scratch/run-ad5s/qa_groups.json.bak-20260705-bl-ext01 _scratch/run-ad5s/qa_groups.json -Force
Copy-Item _scratch/run-ad5s/chunks_captioned.json.bak-20260705-bl-ext01 _scratch/run-ad5s/chunks_captioned.json -Force
Remove-Item -Recurse -Force _scratch/run-ad5s/chroma_captioned
Copy-Item -Recurse _scratch/run-ad5s/chroma_captioned.bak-20260705-bl-ext01 _scratch/run-ad5s/chroma_captioned
```

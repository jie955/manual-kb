# BL-V1-05 post-close · YouTube links + demo parallel_test + TC148 verify + a16/c12 留档

**日期**：2026-07-05  
**状态**：**✅ 关闭**

---

## 1. qa_029/042/043 YouTube → `links[]`

**脚本**：`phase_bl_v1_05_youtube_links_overlay.py` · `link_utils.apply_video_tier_links`  
**Backup**：`20260705-bl-v1-05-youtube`

| group | links | label 来源 |
| --- | ---: | --- |
| qa_029 | 3 | EN 紧邻行（lubricate / dismantle / install） |
| qa_042 | **4**（6→4 video id dedupe） | shorts=URL 前句 · 其余同 qa_029 |
| qa_043 | 1 | lubricate |

- `answer_en` 裸 URL：**0**
- **eval**：**45/47 Top1 · 47/47 Top3**
- **display probe**：14/14
- **L8′ c12**：Top1 qa_030 · Top3 qa_029 ✅（见 [`ad5s_eval_known_misses.md`](./ad5s_eval_known_misses.md)）

产物：[`bl_v1_05_youtube_eval.json`](./bl_v1_05_youtube_eval.json)

---

## 2. demo · qa_023 `parallel_test` UI

**文件**：`demo/index.html`

- `PARALLEL_LABELS`：机臂2并到机臂1 / 机臂1并到机臂2
- `ladderUsesParallelTest` → 隐藏安装/走停/地区三下拉
- qa_024 **不受影响**（U6 blocking）

验收：`verify_demo_branch_ui.py` **PASS**

---

## 3. TC148 内容核实

**脚本**：`verify_tc148_content.py`  
**留档**：[`tc148_content_verify_record.md`](./tc148_content_verify_record.md)

- qa_001：1 link + image_001 COM 图 · ZH 接地 ✅
- qa_002：2 links（topens + Drive video）· ZH 短接 ✅
- T2/T1 retrieval spot-check ✅ · T3 Top1 miss **known**

---

## 4. a16/c12 eval 留档

[`ad5s_eval_known_misses.md`](./ad5s_eval_known_misses.md) — BL-V1-03 原始登记 + Top1 机理解释分层 · **非 bug**

---

## 仍 open（非本批）

- demo `parallel_test` **浏览器**截图（数据结构 + verify 已 PASS）
- TC148 T3 检索排序 · V1.1 EN 邮件稿展开

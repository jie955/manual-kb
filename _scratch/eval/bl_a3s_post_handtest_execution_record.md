# A3S · Post-handtest 四项并行 · 执行留档

**日期**：2026-07-05  
**脚本**：[`phase_a3s_post_handtest_overlay.py`](./phase_a3s_post_handtest_overlay.py)  
**备份**：`run-006/qa_groups.json.bak-20260705-a3s-post-handtest` · `run-007/chroma_captioned.bak-20260705-a3s-post-handtest`

---

## 1 · LINK-A3S

| group | 动作 | 结果 |
| --- | --- | --- |
| **qa_003** | `apply_simple_tier_links` · topens 太阳能排查 | `links[]`×1 · URL 从 `answer_en` 剥离 ✅ |
| **qa_001** | 扫尾 | 无外链 · 无需 `links[]` ✅ |
| **qa_002** | 扫尾 | 无外链 · 无需 `links[]` ✅ |

---

## 2 · IMG-EXT-02

### 型 B · 共享挂载

| group | 资产 | 结果 |
| --- | --- | --- |
| **qa_033** | `image_019.png`（与 qa_021 同资产 · DLMT/COM/ULMT 短接图） | `images[]` + caption 自 qa_021 合并 ✅ |

### 型 A · orphan 补抽（docx → `run-006/images`）

| group | 新文件 | 张数 |
| --- | --- | ---: |
| **qa_035** §八 | `image_024.png` | 1 |
| **qa_036** §十三 | `image_025.png`–`image_027.png` | 3 |
| **qa_039** §十四 | `image_028.png`–`image_029.png` | 2 |
| **qa_038** §十五 | `image_030.png`–`image_034.png` | 5 |

**未挂载**：**qa_040** — docx §十七「as shown below」段 **无 inline 图**（仅文字指图）· 留 V2 caption 补抽或甲方供图。

**库内新增 png**：`image_024`–`image_034`（11 张）· 总库存 34 张。

---

## 3 · ZH-SKELETON qa_041

| 字段 | 改前 | 改后 |
| --- | --- | --- |
| `answer_zh` | **空** | 101 字最小骨架（拆臂润滑要点 + 润滑脂 + 链接指引） |
| demo | V1-07 全 EN 兜底 | **thin-ZH** · 主面板有中文 ✅ |

参照 AD5S **qa_017** / BL-V1-08 先例。

---

## 4 · RETR-DISAMB（路径 B）

复用 AD5S **qa_028/029** + BL-V1-08 症状化/互斥标签：

| group | question（改后） | 互斥首行要点 |
| --- | --- | --- |
| **qa_040** | WD40日常保养润滑（喷WD40/机油）Routine Maintenance | 非拆机臂 · 非 grease 内腔 |
| **qa_041** | 深度润滑（拆机臂·grease内腔）Deep Lubrication | 非单独 WD40 外表保养 |

**裸 query 改善**：

| query | 改前 Top1 | 改后 Top1 | score |
| --- | --- | --- | ---: |
| 日常保养喷WD40润滑 | qa_040 | **qa_040** | **0.809**（原 ~0.65） |
| 深度润滑拆机臂 | qa_041 | **qa_041** | **0.730** |
| **WD40**（裸句） | qa_041 ❌ | **qa_040** ✅ | **0.543**（原 ~0.39→qa_041） |

---

## 5 · COMPLIANCE-011

**无代码改动** · [`a3s_18h1_handtest_issues.md`](./a3s_18h1_handtest_issues.md) §二已标注：**维持现状 · 待甲方后续需要时补充** Drive 展示方案。

---

## 验收

### eval（45 条）

| 指标 | 改前 | **改后** |
| --- | ---: | ---: |
| Top1 | 45/45 | **45/45** ✅ |
| Top3 | 45/45 | **45/45** ✅ |

机器可读：[`a3s_post_handtest_eval.json`](./a3s_post_handtest_eval.json)

### display probe（LLM=off）

| tag | query | Top1 | thin | imgs | gate |
| --- | --- | --- | :---: | ---: | --- |
| LINK | 太阳能不能给电池充电 | qa_003 | F | 3 | ✅ |
| IMG-B | 机臂只朝一个方向转 | qa_033 | F | 1 | ✅ |
| IMG-A | 开关门过程中走停反弹 | qa_035 | T | 1 | ✅ |
| IMG-A | 离合钥匙拧不开 | qa_038 | F | 5 | ✅ |
| DISAMB | 日常保养喷WD40润滑 | qa_040 | T | 0 | ✅ |
| DISAMB | 深度润滑拆机臂 | qa_041 | T | 0 | ✅ |
| DISAMB | WD40 | qa_040 | T | 0 | ✅ |

### 流水线注意

- merge 策略：**chunk_id 级**保留非 TOUCH 块 · TOUCH 块 caption 合并（修复长组只保留首块回归）
- **重启 `:8765`** 后浏览器 spot-check（embed 已更新 · demo 可能仍缓存旧 manifest）

---

## 待核对 / 残余

1. **qa_040** grease 指图 — docx 无 inline 资产 · 若甲方有图可 EXT-02 二期补
2. **新图 caption** — `image_024`–`034` 为 `not_captioned` · V2 可跑 caption 批
3. **EN-UI 折叠** — 本批未动 · 仍属 P1 backlog

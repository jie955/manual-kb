# BL-V1-05 Wave1+2 执行记录 · Tier A spot-fix（9 组）

**日期**：2026-07-05  
**状态**：**✅ Wave1+2 关闭** · Wave3（qa_033/040）待第二刀  
**脚本**：[`phase_bl_v1_05_wave1_overlay.py`](./phase_bl_v1_05_wave1_overlay.py) · [`bl_v1_05_display_probe.py`](./bl_v1_05_display_probe.py)

---

## 1. 范围

9 组 surgical `answer_zh` 增补（+ qa_008 `troubleshooting_ladder` 步 1/3/4 `content_zh`）：

`qa_001` · `qa_002` · `qa_004` · `qa_005` · `qa_006` · `qa_007` · `qa_008` · `qa_009` · `qa_012`

**未动**：§十四 qa_022/023/024 结构 · ladder/branch/协商 · `answer_en`

---

## 2. Tier A closure 表

| group | 增补要点 | spec 验收 | display probe |
| --- | --- | --- | --- |
| qa_001 | 11#/12# · ∅5×20 10A 250VAC · 备用 fuse · 36VDC · 24V 12Ah | ✅ | a01 |
| qa_002 | 11#/12# · 保险丝三件套 | ✅ | a03 |
| qa_004 | 24V 12Ah · +30W/6h/10 cycles 增容规则 | ✅ | a05 |
| qa_005 | 11#/12# · 备用 fuse · **症状：学习灯不亮** | ✅ | a06 |
| qa_006 | CR2025 · 11#/12# · 4#/5# · **症状：学习灯亮** | ✅ | a07 |
| qa_007 | CR2025 ×2 | ✅ | c01 |
| qa_008 | 65英尺/20米 · CR2025 · ERM12（ladder 同步） | ✅ | a08 |
| qa_009 | CR2025 ×2 | ✅ | c02 |
| qa_012 | 10A 250VAC · 3.3ft/1m 门宽测 | ✅ | a11 |

入库前：`en_only_specs` 关键项 **9/9 OK**（`phase_bl_v1_05_wave1_overlay.verify_specs`）

§十四探针：**a14 → qa_022** · thin=False · 无 naive merge ✅

---

## 3. 检索 eval

| 指标 | BL-V1-04 后 | **Wave1+2 后** |
| --- | ---: | ---: |
| Top1 | 45/47 | **45/47** |
| Top3 | 47/47 | **47/47** |

**仍 miss（pre-existing）**：a16 · c12

产物：`_scratch/eval/bl_v1_05_wave1_eval.json`  
Backup：`20260705-bl-v1-05-wave1`

---

## 4. 过程备注

### 4.1 a07 瞬时回归与修复

首 patch 后 **a07**（学遥控器 学习灯一直亮）Top1 从 qa_006 → qa_005：两组同步补 BAT 11#/12# 后 embedding 更近。

**修复**：qa_005/006 `answer_zh` 加互斥 **症状前缀**（学习灯不亮 vs 学习灯亮），与 V1-08 症状化同构、不改 eval query。re-embed 后 **a07 恢复 Top1 qa_006**。

### 4.2 qa_008 ladder

根级 `answer_zh` 与 `troubleshooting_ladder` 步 1/3/4 `content_zh` **同步**增补，避免 demo ladder 视图与 flat 视图规格不一致。

---

## 5. 下一刀 · Wave3

| group | 待增补 |
| --- | --- |
| qa_033 | DIP #1 / #2（自动关门） |
| qa_040 | 门宽 3 feet（若步内 ZH 仍缺） |

Wave3 完成后补 Tier B 全库 audit 结论 → `bl_v1_05_execution_record.md` 总关。

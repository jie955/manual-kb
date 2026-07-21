# BL-V1-05 执行记录 · AD5S zh/en Tier A + Tier B 总关

**日期**：2026-07-05  
**状态**：**✅ 关闭**（Tier A **12/12** · Tier B audit 留档）  
**范围**：[`bl_v1_05_scope.md`](./bl_v1_05_scope.md)

| 波次 | 脚本 | 留档 |
| --- | --- | --- |
| Wave1+2（9 组） | `phase_bl_v1_05_wave1_overlay.py` | [`bl_v1_05_wave1_execution_record.md`](./bl_v1_05_wave1_execution_record.md) |
| Wave3（2 组） | `phase_bl_v1_05_wave3_overlay.py` | 本文 §2 |
| qa_010 dip#5 | `phase_bl_v1_05_qa010_dip_patch.py` | 本文 §2b |
| Tier B audit | `ad5s_zh_en_gap_scan.py` | [`bl_v1_05_tier_b_audit.md`](./bl_v1_05_tier_b_audit.md) |

---

## 1. Tier A 全表（12 组 · 12/12 已交付）

| group | 波次 | 增补要点 | spec✅ | probe |
| --- | --- | --- | :---: | --- |
| qa_001 | W1+2 | 保险丝 · 11#/12# · 36V · 24V12Ah | ✅ | a01 |
| qa_002 | W1+2 | 保险丝三件套 · 11#/12# | ✅ | a03 |
| qa_004 | W1+2 | +30W/6h/10cycles · 24V12Ah | ✅ | a05 |
| qa_005 | W1+2 | 11#/12# · 症状：学习灯不亮 | ✅ | a06 |
| qa_006 | W1+2 | CR2025 · 11#/12# · 4#/5# · 症状：学习灯亮 | ✅ | a07 |
| qa_007 | W1+2 | CR2025 | ✅ | c01 |
| qa_008 | W1+2 | 65ft · CR2025 · ERM12（+ ladder） | ✅ | a08 |
| qa_009 | W1+2 | CR2025 | ✅ | c02 |
| qa_012 | W1+2 | 10A250VAC · 3.3ft/1m | ✅ | a11 |
| **qa_010** | **dip#5** | **步 2：DIP #5 OFF · 断配件 · 重学 · push-button 短接** | ✅ | a09/a15 |
| qa_033 | W3 | DIP #2 ON · #1 推拉门 · AUTO CLOSE 电位器 | ✅ | b03 |
| qa_040 | W3 | DIP #3 · 3.3ft/1m 门宽 · FORCE/SOFT STOP | ✅ | b10 |

---

## 2. Wave3 结果

- **spec**：2/2 OK · **display probe**：b03/b10 spec 在命中 `content_zh` ✅  
- **qa_023 verify**：四项 PASS（§十四未 touch）  
- **eval**：**45/47 Top1 · 47/47 Top3**（a16 · c12 pre-existing）

Backup：`20260705-bl-v1-05-wave3`  
Eval：`_scratch/eval/bl_v1_05_wave3_eval.json`

---

## 2b. qa_010 dip#5 补交（Tier A 第 12 组）

- **性质**：Wave1+2 合并 9 组时的**执行疏漏**（原候选清单内 · 非 Tier B 新发现）
- **patch**：步 2 增补 `DIP 开关 #5 拨 OFF` + 断配件 / 重学 / push-button 短接（对齐 EN step 2）
- **display probe**：a09/a15 spec 在命中 `content_zh` ✅
- **eval**：**45/47 Top1 · 47/47 Top3**（无回归）

Backup：`20260705-bl-v1-05-qa010`  
Eval：`_scratch/eval/bl_v1_05_qa010_eval.json`

---

## 3. 检索 / 验收摘要

| 阶段 | Top1 | Top3 | 备注 |
| --- | ---: | ---: | --- |
| V1-04 后 | 45/47 | 47/47 | 基线 |
| Wave1+2 首 patch | 44/47 | 47/47 | **a07 瞬时回归** → 症状前缀修复 → 45/47 |
| **Wave3 后** | **45/47** | **47/47** | 无新增 miss |
| **qa_010 dip#5 后** | **45/47** | **47/47** | 无回归 |

**display probe**：14/14（含 qa_010 a09/a15 · 检索命中 content_zh 含规格词）

---

## 4. Tier B · 全库 audit

见 [`bl_v1_05_tier_b_audit.md`](./bl_v1_05_tier_b_audit.md)：

- **26 组** audit 留档 · **无 RED** 买错装错 spec  
- **Submode C** qa_022/023/024 边界守住  
- **detail_link** qa_029/042/043 → links[] backlog  
- **TC148** → V1.1

---

## 5. 扫尾 backlog（不 retro-block V1-05）

1. ~~**qa_029/042/043** YouTube → `links[]`~~ **✅ 2026-07-05** · [`bl_v1_05_post_close_execution_record.md`](./bl_v1_05_post_close_execution_record.md)  
2. ~~**demo** `parallel_test` 分支文案 + 隐藏三下拉~~ **✅ 同上**  
3. **demo** `parallel_test` 浏览器截图（可选）  
4. **TC148** T3 检索排序 backlog  
5. **TC148** 客服模板 `content_role` · V1.1

---

## 6. 产物索引

- `_scratch/eval/ad5s_zh_en_gap_inventory.md`（post-Wave3 重扫）  
- `_scratch/eval/bl_v1_05_display_probe.py`  
- `_scratch/eval/bl_v1_05_wave1_eval.json` · `bl_v1_05_wave3_eval.json` · `bl_v1_05_qa010_eval.json`

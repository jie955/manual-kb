# BL-V1-04 执行记录 · AD5S 外链 + qa_023 branch

**日期**：2026-07-05  
**状态**：**✅ 关闭**（简单档 qa_003/010/030 + 复杂档 qa_023 pilot→验收→prod overlay）  
**脚本**：[`phase_bl_v1_04_ad5s_overlay.py`](./phase_bl_v1_04_ad5s_overlay.py) · [`verify_qa_023_acceptance.py`](./verify_qa_023_acceptance.py)

---

## 1. 范围（本次交付）

| 档 | 组 | 动作 |
| --- | --- | --- |
| **简单档** | qa_003 | topens 太阳能排查链 → 根级 `links[]`（`support_page`），`answer_en` 无裸 URL |
| **简单档** | qa_010 | Drive 短接视频 → 根级 `links[]`（`link_type=video`）；ZH「站内信不可发此链接」保留 |
| **简单档** | qa_030 | 2× topens 保养链已在 prod；剥离 `answer_en` 重复 URL |
| **复杂档** | qa_023 | 协商剥离（BL-V1-06）+ `troubleshooting_ladder` 3 步 + 步骤 1 **2 branch**（`parallel_test`）+ 步骤 2 采购链 |

**非范围**：qa_023 全 install/stall 矩阵 eval 扩展 · a16/c12 Top1 · 全库 43 组重 extract。

---

## 2. 实现

| 层 | 文件 | 内容 |
| --- | --- | --- |
| Extract | `link_utils.py` | `apply_simple_tier_links` · `SIMPLE_LINK_GROUP_IDS` |
| Extract | `branch_utils.py` | `build_qa_023_ladder` · `attach_qa_023_structure` |
| Extract | `qa_doc_extractor.py` | qa_023 优先 attach → qa_024 → 简单档 links |
| 验收 | `verify_qa_023_acceptance.py` | 四项（2 branch / 单路径配图 / 采购链+disclaimer / 协商+无裸 URL） |
| 测试 | `tests/test_branch_utils.py` | `TestQa023Ladder` ×2 |
| Prod | `phase_bl_v1_04_ad5s_overlay.py` | backup → transform 4 组 → chunk → embed → eval |

### 2.1 qa_023 ladder 结构

| step | 内容 | branches | links |
| ---: | --- | --- | --- |
| 1 | 并接排查 intro（ZH） | **2** · `parallel_test: arm2_on_arm1 \| arm1_on_arm2` · 图 024/025 | — |
| 2 | 加电阻 + disclaimer prose | — | 1× `purchase_link` B08HYZV3DW |
| 3 | 发视频 fallback | — | — |

`negotiation_offers[]`：M12 抵电阻协商句（不进 `answer_en`/LLM）。

---

## 3. 四项验收（qa_023）

```
[1] ctx={} → 2 branch cards ✅
[2] parallel_test=arm2_on_arm1 → 1 card, images=['image_024.png'] ✅
[3] step2 purchase_link + disclaimer ✅
[4] negotiation_offers=1, bare URLs in answer_en=[] ✅
```

---

## 4. AD5S eval（post-overlay）

| 指标 | BL-V1-08b 后 | **BL-V1-04 后** |
| --- | ---: | ---: |
| Top1 | 45/47 | **45/47** |
| Top3 | 47/47 | **47/47** |

**BL-V1-04 相关 query**

| id | expected | Top1 | 备注 |
| --- | --- | :---: | --- |
| c08 | qa_023 | ✅ | 并接机臂排查 |
| c13 | qa_030 | ✅ | 保养指南链接 |
| a04 | qa_003 | ✅ | 太阳能充电（链在 links[]） |
| a09/a15 | qa_010 | ✅ | 无反应（视频链在 links[]） |

**仍 miss（pre-existing · 非 V1-04 范围）**：a16（Top3 qa_024）、c12（Top3 qa_029）。

产物：`_scratch/eval/bl_v1_04_ad5s_eval.json`  
Backup stamp：`20260705-bl-v1-04`

---

## 5. 后续

- **qa_023 branch 矩阵 eval**：等复杂档 eval 扩展专项（与 qa_024 region/install 矩阵同批）
- **demo 展示层（2026-07-05 补眼）**：四项验收为**数据结构 only**，未做浏览器截图。qa_023 命中时：
  - 步骤 1 两条 branch **默认均展示**（ctx={}）— 功能正确
  - branch 标签因 `formatAppliesWhen` 无 `parallel_test` 映射 → 显示泛化 **「分支」**，非「机臂2并到机臂1」
  - 三下拉筛选器（安装/走停/地区）**仍可见**，但对 `parallel_test` **不可筛选**（性质不同于 qa_024 的「用户已知客观情况」）
  - **结论**：数据层 ✅ · 展示 UX 待单独处理（标签文案 + 按 branch 维度隐藏/替换筛选器）→ **不阻塞 BL-V1-04 关闭** · 可挂 demo backlog 或 V1.1
- **re-embed 敏感**：qa_023 与 qa_003/010 结构变更后须重跑 chroma（本次已 embed）

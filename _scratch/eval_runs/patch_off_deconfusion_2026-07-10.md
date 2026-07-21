# patch_off 掉分解混 · 框架修复后

§7.2 已应用：`无金标准 / 无 ref_keys 模式` → ②待人工、④待人工（非自动否决）。
**结论**：Joyce 补丁 case 掉分**主要不是**该框架 bug — 多数有金标准且 `ref_keys=25–50%`（真实生成缺口）。

## cs_0005 专项（已查清）

| 维 | Round 1e | patch_off | 原因 |
| --- | --- | --- | --- |
| ① | 对 | 对 | 无变化 |
| ② | 直接可发 | 直接可发 | 无变化 |
| ③ | 配对相关 | **该配没配** | `pinned_images` 摘掉 → `images_used` 空 · Reference 要求配图 |
| ④ | 通过 | 不通过 | **③一票否决**，非①② |

→ **独立根因**：配图/检索机制，勿归入「生成文字质量」筐。

## MVP19 patch_off 未通过 · 根因桶

### presales brief 缺失（产品/链接） (3)

- **cs_0004** [presales] ④=不通过 · ②=小改可发 · ③=配对相关 · presales · weak links
- **cs_0006** [presales] ④=不通过 · ②=小改可发 · ③=配对相关 · presales · weak links
- **cs_0011** [presales] ④=不通过 · ②=小改可发 · ③=无需图 · presales · weak links

### ②真实生成缺口（ref_keys 部分命中，有金标准） (8)

- **cs_0002** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=50% ·缺 4#/5#,limit_short · 待逐步对照 Reference
- **cs_0003** [补丁] ④=不通过 · ②=小改可发 · ③=无需图 · ref_keys=25% ·缺 11#/12#,DIP#5,address_request · 关键项偏差大
- **cs_0012** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=50% ·缺 FORCE,SOFT_STOP · 待逐步对照 Reference
- **cs_0014** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=33% ·缺 address_request,limit_B · 关键项偏差大
- **cs_0016** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=50% ·缺 DIP#5,address_request · 待逐步对照 Reference
- **cs_0018** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=50% ·缺 DIP#3,limit_short · 待逐步对照 Reference
- **cs_0021** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=33% ·缺 4#/5#,address_request · 关键项偏差大
- **cs_0022** [补丁] ④=不通过 · ②=小改可发 · ③=配对相关 · ref_keys=33% ·缺 address_request,limit_B · 关键项偏差大

### ③图片机制（非文字生成） (1)

- **cs_0005** [presales] ④=不通过 · ②=直接可发 · ③=该配没配 · presales + links

## 10 个 generation/pinned 补丁 case · 掉分拆解

- 通过→未通过：**8** 封
- 其中 §7.2 框架误伤（待人工桶）：**0**
- 其中 ref_keys 部分命中（真实生成缺口）：**8**

## Holdout（框架修复后）

- **cs_0023** ④=待人工 · ②=待人工 · steps=4 · 无金标准回信
- **cs_0024** ④=通过 · ②=直接可发 · presales + links
- **cs_0025** ④=待人工 · ②=待人工 · top1_hit · steps=4 · 无金标准回信
- **cs_0026** ④=不通过 · ②=需重写 · truncated
- **cs_0027** ④=待人工 · ②=待人工 · top1_hit · steps=4 · 无金标准回信

## 建议顺序（更新）

1. §7.2 框架 ✅ — holdout cs_0025/0027 → ④待人工
2. **人工 xlsx**（round1e / holdout / patch_off · 桶 A 加 §10.1 内容核对）
3. 桶 A/B 方案评审：**动态提取 vs 静态清单**（§10.2）→ 再写代码
4. 桶 A/B 修完后验证：**新 holdout**（§10.3 · 非 T1–T5）
5. 根因方向：**A** 诊断点覆盖（非照抄术语） **B** playbook **C** 配图 **D** style/audit

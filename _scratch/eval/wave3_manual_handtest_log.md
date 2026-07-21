# Wave 3 · 说明书 E2E 手测留档

**日期**：2026-07-08 PM  
**脚本**：[`bl_wave3_manual_smoke.py`](./bl_wave3_manual_smoke.py) · [`bl_ret_01a_verify.py`](./bl_ret_01a_verify.py)  
**启动参数**：`--unified-cs --demo-presentation cs-email --allowed-libraries a3s,ad5s`（cs-email **默认** a3s+ad5s）

---

## 结果（机器 smoke · 2026-07-08 PM）

| Query | Top1 排查 | Manual supplement | 判定 |
| --- | --- | --- | :---: |
| DIP switch photocell wiring installation A3S | qa_001 | **a3s-manual-p26** (0.74) | ✅ |
| AD5S dual swing wiring diagram installation | qa_015 | **ad5s-manual-p8** (0.65) | ✅ |
| AT12131S gate does nothing (排查对照) | qa_011 | — | ✅ |

**manual smoke: 3/3** · BL-RET-01a filter verify ✅

---

## Demo 人工待补（非阻塞 Wave 3 机器留档）

- [ ] 浏览器 CS 视图：Product links 栏可见  
- [ ] 工程师视图：安装类 query 出现 `· manual` 标记  
- [ ] 截图归档至殷主管试跑包（Wave 4）

---

## AD5S VLM

[`parse_stats_retry.json`](../vlm_ad5s_full/parse_stats_retry.json)：**3/3 retry 成功** · 原 3 failed 页已补跑（2026-07-08 BL-RET 批次）。

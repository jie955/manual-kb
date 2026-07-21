# Side-by-Side · 系统回信 vs 真实客服回信

**用途**：发版门禁 / Demo 演示 / Task 0 Oracle / Task 4 内评 · **P0 准确**首选对照样例  
**架构**：[ADR-0002](../../docs/adr/0002-english-cs-cross-lingual-retrieval-localized-generation.md) · [执行清单](./cs_en_poc_execution.md)  
**原则**：Customer 与 **Reference** 来自语料纯英文原件；System 填 **E2E 产出**（非仅 Oracle）。Oracle 仅用于分离生成上限。

**生成记录**：`gemini-2.5-flash` · [`cs_side_by_side_generated.json`](./cs_side_by_side_generated.json) · 脚本 [`run_cs_side_by_side_gen.py`](./run_cs_side_by_side_gen.py) · `generate_answer(locale=en, response_mode=cs_email)`

**初评摘要**：

| Case | Grounding | Quality | 备注 |
| --- | ---: | ---: | --- |
| A #13 | 4/5 | 4/5 | 缺 Joyce step3「push against gate」；含 qa_034 电机直测步（Reference 无） |
| B #8 | 3/5 | 4/5 | ⚠️ 将 4#/5# 写成 11#/12#；缺「先断延长线换短线」；**承认已 jumper** ✅ |
| C #22 | 2/5 | 3/5 | Oracle qa_015 近似；未覆盖安全反转 3s / limit A·B / 单臂 isolate |

---

## 怎么用

1. 将 **Customer Email** 输入 Demo **E2E** 路径（正确库 / 路由）。  
2. 把产出填入 **System Reply**。  
3. 与 **Reference（真实 CS）** 对照 — **Grounding（准确）优先**，体裁其次。  
4. 对外演示：**Customer → System**；Reference 内部对照或按需展开。  
5. **发版前**三门禁 case 须 E2E 达标，不依赖甲方试跑。

**Oracle 提示（Task 0）**：生成时可人工注入 `expected_group`，不依赖 Top1。

| Case | 库 | Oracle `group_id` | `corpus_mapping` |
| --- | --- | --- | --- |
| A · #13 | a3s | `qa_034` + `qa_022` | direct |
| B · #8 | tc148 | `qa_002` | direct |
| C · #22 初信 | ad5s（近似） | `qa_015` | out |

---

## Case A · #13 A3S · stops before fully open

**场景文件**：[`0013-a3s-stops-before-fully-open.md`](../../samples/customer-service-emails/0013-a3s-stops-before-fully-open.md) · `cs_0013`

### Customer Email

```text
Need help this gate opener keeps stopping before opening fully

(Context: US · Texas · Amazon · A3S · self-install · Ranch/Farm · 12–14' · 100–300 lbs · M12)
```

### Reference · 真实客服（Joyce · 2026-06-15 · 节选）

```text
Dear Edward,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team...

All TOPENS products are backed by a 12-month warranty.

Checked with our engineer, please help us do some tests to find out the problem...

1. Please detect the voltage of the +BAT- (11#, 12#) terminals ... whether the voltage can stay at almost 24V (above 22V). If the voltage drops too much, the problem should be with the power source...

2. Please power off the system first ... turn the FORCE potentiometer all the way clockwise ... SOFT STOP all the way counter-clockwise ... complete opening & closing cycle...

3. If the problem still persists, please push against ... the gate during opening ... add some load ...

4. If all tests above don't help, please take down the arm ... hold its front mount ... see if the arm can extend and retract properly...

Please let me know the result one by one. Videos ... pictures of the whole control board ...
And also please reply your specific SHIPPING ADDRESS with zip code and confirm PHONE # ...

Best regards,
Joyce
```

### System Reply（Oracle · 2026-07-07）

```text
Dear Edward,

Thank you for contacting TOPENS Customer Service. I'm sorry to hear that your A3S gate opener is stopping before fully opening...

Our engineering team has reviewed your case. Please perform the following numbered tests:

1. Check Control Board Voltage: +BAT- terminals (11#, 12#) ... stay above 22V ...
2. Adjust FORCE (clockwise max) and SOFT STOP (counter-clockwise min) after power off ...
3. Manual Gate and Arm Check: release clutch, disconnect arm, hold front mount ...
4. Direct Motor Test: red/black wires to DC 24V ...

Please provide results one by one. Video/photos appreciated.
Please provide shipping address with zip and confirm phone.

Best regards,
[Agent first name],
TOPENS Customer Service Team
```

> 全文见 [`cs_side_by_side_generated.json`](./cs_side_by_side_generated.json) · `results[0].reply`

### 对照要点

| 检查项 | Reference 有？ | System |
| --- | :---: | --- |
| 保修 12-month 一句 | ✅ | ✅ |
| 11#/12# 电压 >22V | ✅ | ✅ |
| FORCE 顺 / SOFT STOP 逆 · 先断电 | ✅ | ✅ |
| 开门反向加负载 | ✅ | ❌ 缺 |
| 拆臂手持试伸缩 | ✅ | ✅（step 3） |
| 索地址/电话/视频 | ✅ | ✅ |
| 逐步要结果 one by one | ✅ | ✅ |
| 无通篇复制无关步骤 | ✅ | ⚠️ 多 step4 电机直测 |

---

## Case B · #8 PW502 + TC148 · push button · 客户已短接 4#5

**场景文件**：[`0008-pw502-tc148-push-button-not-working.md`](../../samples/customer-service-emails/0008-pw502-tc148-push-button-not-working.md) · `cs_0008`

### Customer Email

```text
Push button not working, therefore we jumpered out #4&5 at the main control panel and still nothing happened. Other than that everything works

(Context: CA · Amazon.ca · PW502 · TC148 · Home · 14–16' · 300–500 lbs · M12)
```

### Reference · 真实客服（Lori · 2026-06-15 · 节选）

```text
Dear Cindy,

Thank you for contacting TOPENS. This is Lori from TOPENS Customer Service Team...

1. Please disconnect the extension cable connecting TC148 to the control board and replace it with a short cable to see if the gate opener could work. If yes, may I ask the distance between TC148 and the control board?

2. If the step above do not work, please disconnect all accessories (except the power supply and the arm), and try to immediately short (plug the wire in, then pull it out instantly) the push button terminals (4# and 5#) referring to the attached video...

(I know you've already done this step. Could you please try this procedure again?)

Looking forward to the result ... Videos showing the process of immediately short ...

And also please reply your specific SHIPPING ADDRESS ...
```

### System Reply（Oracle qa_002 · 2026-07-07）

```text
Dear Cindy Tan,

Thank you for contacting TOPENS Customer Service...

We appreciate you already attempted to short the terminals; let's clarify the procedure...

1. Isolate the TC148 Push Button: disconnect all other accessories except TC148 ...
2. Perform an Instantaneous Short Test: You mentioned jumpering #4&5. On your PW502 ...
   terminals ... 11# (O/S/C) and 12# (COM) ... instantaneously short ...
   Video: https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing
3. Provide Photos/Video of control board ...

Best regards,
[Agent first name],
TOPENS Customer Service Team
```

> 全文见 `cs_side_by_side_generated.json` · `results[1].reply`  
> ⚠️ **Grounding 问题**：Reference 用 **4# & 5#**；System 混写 **11#/12#**（chunk 未写 PW502 端子号，模型臆造）。

### 对照要点

| 检查项 | Reference 有？ | System |
| --- | :---: | --- |
| **承认客户已 jumper 4#5** | ✅ | ✅（clarify instant vs jumper） |
| **instant short** vs 持续 jumper | ✅ | ✅ |
| 先断 TC148 延长线换短线 | ✅ | ❌ 缺 |
| 断附件留电源+机臂 | ✅ | ⚠️ 仅断其他留 TC148 |
| 视频/Drive 链 | ✅ | ✅ |
| 端子号 4#/5# 正确 | ✅ | ❌ 写成 11#/12# |

> **Reply 原则 #4**：客户已排查的要在结论里回应，勿通篇复制手册。

---

## Case C · #22 A5132 · 全开即回关 4 ft · 真实多轮（初信 vs Reply 1）

**场景文件**：[`0022-a5132-opens-then-recloses-resolved.md`](../../samples/customer-service-emails/0022-a5132-opens-then-recloses-resolved.md) · `cs_0022`  
**说明**：A5132 **无 v1 排查 docx**（`corpus_mapping=out`）。本 case 评 **Reply Quality / 体裁 / fork**，不卡 Top1。客户表单写 Push，后更正 **Pull to open** → Reply 2 改 Step 3（见同文件）。

### Customer Email（Message 1 · 初信）

```text
Just recently my gate started acting differently. The left panel - furthest from the controller - seems to open and reaches full open then immediately starts closing about 4 feet. (there use to be a pause which it is not doing any more. This stops the right panel from closing as well. When I press the remote button it tries to open again and then after a pause (the correct pause) only closes 4 feet. When is stops it causes the right panel to stop again. I am wondering if I need to move the magnets on the left panel. Please advise

(Context: US · Amazon · A5132 · dual swing · form: Push to Open · Ranch/Farm)
```

### Reference · 真实客服（Heidi · Reply 1 · 2026-05-13 · 节选）

```text
Dear Stuart
... built-in safety logic: if the control board senses an obstruction ... no photocells ... reverse for 3 seconds on the first encounter and stop on the second. As for your case ... obstruction when the gate is fully open ...

1. Check for Resistance: Use the release key ... Manually swing ... stiffness or rubbing at fully open ...

2. Stall Force Adjustment: Increase the Stall Force ... Power off first ... Potentiometer E clockwise to maximum ... complete opening and closing cycle ...

3. Verify the extension of each arm
If the arm reaches its full extension before the gate is fully open ... slide limit switch B slightly inward ...

4. To isolate which arm ... Disconnect both arms ... test Left only ... then Right only ...

Kindly let me know the result of each step ...
... Order Invoice ... video ...
```

### Reference · Pull 分叉（Reply 2 · 客户更正后 · Step 3 仅此段变化）

```text
Thank you for clarifying ... "Pull-to-Open" ... Steps 1, 2, and 4 ... still completely applicable ...

3. Verify the Retraction of Each Arm (For Pull-to-Open)
If the arm reaches its fully retracted position before the gate is fully open ... slide limit switch A slightly outward ...
Alternatively ... adjust the gate bracket by moving it slightly inward.
```

### System Reply（Oracle qa_015 近似 · 2026-07-07）

```text
Dear Stuart,

Thank you for contacting TOPENS Customer Service...

1. Test Gate Movement: release clutch on both arms, push panels to middle ...
2. Isolate Control Board & Accessories: disconnect accessories, DIP #5 OFF, EDGE-GND jumper ...

You mentioned wondering if you need to move the magnets ... performing the above isolation steps first ...

Best regards,
[Agent first name],
TOPENS Customer Service Team
```

> 全文见 `cs_side_by_side_generated.json` · `results[2].reply`  
> **out-of-corpus**：Oracle 为 AD5S qa_015，非 A5132/Heidi 话术；缺 safety 3s reverse、Pot E、limit B、单臂 isolate。

### 对照要点

| 检查项 | Reference 有？ | System |
| --- | :---: | --- |
| 安全反转逻辑（3 s / 第二次停） | ✅ | ❌ |
| 步骤 1/2/4 共享 trunk | ✅ | ⚠️ 不同结构 |
| Step 3 与 install mode 相关 | ✅ | ❌ |
| 双臂 isolate 左/右 | ✅ | ❌ |
| 回应 magnets/限位疑虑 | ✅ | ⚠️ 泛提 magnets |
| 索 invoice / 视频 | ✅ | ⚠️ 仅地址/视频 |

> **生成 eval 扩展**：若客户追问「My gate is a pull to open」→ 应对照 Reply 2，**只改 Step 3**，1/2/4 不变（[`csq_fork_001`](../../_scratch/eval/cs_email_query_map.json)）。

---

## 汇总评分（Task 4 · 填完 System 后）

| Case | Grounding 1–5 | Reply Quality 1–5 | 像真实 CS？ | Critical | 主要差距 |
| --- | ---: | ---: | :---: | :---: | --- |
| A #13 | 4 | 4 | ✅ | — | 缺 push-against-load；多电机直测步 |
| B #8 | 3 | 4 | ✅ | ⚠️ 端子号 | 11#/12# vs 4#/5#；缺延长线步 |
| C #22 | 2 | 3 | ⚠️ | — | out-of-corpus oracle 偏差大 |

**Critical**：编造步骤/电压/端子 · 错误保修承诺 · 忽略客户已做排查（#8 jumper）· 翻译腔/中文思维英文。

---

## Demo 演示顺序（建议）

1. **Case B #8** — 客户最像「已排查仍失败」；Reference 展示「承认已做 + instant short」→ 甲方易感知差异。  
2. **Case A #13** — direct + v1 docx · 标准四步排查信。  
3. **Case C #22** — 可选：展示 Workflow（Pull 更正 → 只改 Step 3）；**勿**承诺 Top1，强调「体裁与 fork」。

---

## 留档

| 字段 | 值 |
| --- | --- |
| System 生成时间 | 2026-07-07 |
| 模型 | gemini-2.5-flash |
| 模式 | Oracle · `locale=en` · `response_mode=cs_email` |
| JSON | [`cs_side_by_side_generated.json`](./cs_side_by_side_generated.json) |

**相关**：[`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md) · [`cs_en_oracle_gen_smoke.md`](./cs_en_oracle_gen_smoke.md)

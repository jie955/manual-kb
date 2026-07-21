# A3S docx · 严格对照 gap scan

**手测基准**：`samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx`（18 个 H1）
**prod**：`_scratch/run-007/chroma_captioned` · **35** retrievable root groups
**extract**：`_scratch/run-006/qa_groups.json` · **43** groups

## H1 覆盖总览

| # | H1（docx） | H2 | orphan 段 | prod 组 | 状态 |
| ---: | --- | ---: | ---: | ---: | --- |
| 一 | 一、电源问题 Power Issues | 5 | 0 | 5 | ✅ 已入库 |
| 二 | 二、遥控器问题 Remote Control & Signal Problems | 5 | 0 | 5 | ✅ 已入库 |
| — | 完全不工作 Complete Failure | 4 | 0 | 4 | ✅ 已入库 |
| 四 | 四、只朝一个方向 Only Opens/Closes One Direction | 0 | 17 | 1 | ✅ overlay |
| 五 | 五、随意开关门 Random Opening/Closing | 0 | 10 | 1 | ✅ overlay |
| 六 | 六、缓停止有问题（缓停止错乱或者没有缓停止）Soft Stop Issues | 0 | 9 | 1 | ✅ overlay |
| 七 | 七、自动关门不生效 Auto Close Function Doesn't Work | 0 | 9 | 1 | ✅ overlay |
| 八 | 八、开关门过程中走停或反弹 Gate Stops or Bounces During O | 0 | 19 | 1 | ✅ overlay |
| 九 | 九、关到位后反弹 Gate Bounces Back After Closing Com | 2 | 0 | 2 | ✅ 已入库 |
| — | 不限位 Gate Does Not Stop at Limit Switch | 5 | 0 | 5 | ✅ 已入库 |
| — | 门机运行慢 Gate Operates Slowly | 0 | 12 | 1 | ✅ overlay |
| 十二 | 十二、电机电流小导致走停 Motor Current Too Low Causes St | 7 | 4 | 8 | ⚠️ 有组+orphan |
| 十三 | 十三、电机转机臂不伸缩 Motor Runs But Gate Doesn't Move | 0 | 16 | 2 | ✅ overlay |
| 十四 | 十四、机臂声音异常 Abnormal Noise From Arm | 0 | 35 | 1 | ✅ overlay |
| 十五 | 十五、离合打不开 Clutch Won't Release | 0 | 22 | 1 | ✅ overlay |
| — | 风会把门吹开（或者外力能把门推开一点） There is Little Play Whe | 0 | 6 | 1 | ✅ overlay |
| 十七 | 十七、保养与润滑 Maintenance and Lubrication | 0 | 29 | 2 | ✅ overlay |
| 十八 | 十八、其他产品知识讲解 | 0 | 38 | 1 | ✅ overlay |

**汇总**：18 H1 · ✅ 全量 5 · ✅ overlay 12 · ⚠️ partial 1 · ❌ 未入库 0

## ❌ 未入库 H1（docx 有 · prod 无）


## ⚠️ 已入库但 docx 仍有 orphan 段（H1 正文无 H2）

- 十二、电机电流小导致走停 Motor Current Too Low Causes Stalling (The Gate Stops Immediately It Starts)

## ✅ prod 组明细（按 docx H1）

### 一 · 一、电源问题 Power Issues
- **qa_001** · 控制板灯不亮（适配器）No Led On the Control Board
- **qa_002** · 控制板灯不亮（纯太阳能）
- **qa_003** · 太阳能不能给电池充电 The Batteries Cannot Be Charged by Solar
- **qa_004** · 接上太阳能板就不工作 The Gate Opener Quits Working Once Solar Panels Connected
- **qa_005** · 电池耗电异常 Abnormal Battery Drain

### 二 · 二、遥控器问题 Remote Control & Signal Problems
- **qa_006** · 学不上遥控器 （学习灯不亮）Cannot Program Remote
- **qa_007** · 学不上遥控器 （学习灯亮）
- **qa_008** · 其中一个遥控器无法工作 One (or Some) of Remotes Doesn't Work
- **qa_009** · 遥控距离不够 Short Remote Range
- **qa_010** · 多次按遥控器门机才反应 Remote Needs Multiple Presses

### — · 完全不工作 Complete Failure
- **qa_011** · 按遥控器没有反应 No Response When The Remote Is Pressed
- **qa_012** · 控制板有持续咔哒声 Control Board Clicking Continuously
- **qa_013** · 按遥控器保险丝烧 Fuse Blows When Pressing Remote
- **qa_014** · 不工作（只CODE LED微微亮）

### 四 · 四、只朝一个方向 Only Opens/Closes One Direction
- **qa_033** · 只朝一个方向 Only Opens/Closes One Direction
- _（另有 17 段 H1 orphan 正文未入库）_

### 五 · 五、随意开关门 Random Opening/Closing
- **qa_029** · 随意开关门 Random Opening/Closing
- _（另有 10 段 H1 orphan 正文未入库）_

### 六 · 六、缓停止有问题（缓停止错乱或者没有缓停止）Soft Stop Issues
- **qa_030** · 缓停止有问题 Soft Stop Issues
- _（另有 9 段 H1 orphan 正文未入库）_

### 七 · 七、自动关门不生效 Auto Close Function Doesn't Work
- **qa_031** · 自动关门不生效 Auto Close Function Doesn't Work
- _（另有 9 段 H1 orphan 正文未入库）_

### 八 · 八、开关门过程中走停或反弹 Gate Stops or Bounces During Operation
- **qa_035** · 开关门过程中走停或反弹 Gate Stops or Bounces During Operation
- _（另有 19 段 H1 orphan 正文未入库）_

### 九 · 九、关到位后反弹 Gate Bounces Back After Closing Completely
- **qa_015** · 门关到位又弹回来·拉开门 Gate Bounce Back · Pull-to-Open · Limit B
- **qa_016** · 门关到位又弹回来·推开门 Gate Bounce Back · Push-to-Open

### — · 不限位 Gate Does Not Stop at Limit Switch
- **qa_017** · 开门不限位/一直走（方向未明·泛化）Gate Open Limit · No Stop · Direction Unspecified
- **qa_018** · 开门不限位/位置不对·限位A（拉开门·开位）Gate Open Limit · Pull-to-Open · Limit A Open
- **qa_019** · 开门停不下来/过位·限位B（推开门·开位）Gate Open Limit · Push-to-Open · Limit B Open
- **qa_020** · 关门不限位/不到位·限位B（拉开门·关门位）Gate Close Limit · Pull-to-Open · Limit B Close
- **qa_021** · 关门不限位/不到位·限位A外移（推开门·关门位）Gate Close Limit · Push-to-Open · Limit A · Magnet

### — · 门机运行慢 Gate Operates Slowly
- **qa_034** · 门机运行慢 Gate Operates Slowly
- _（另有 12 段 H1 orphan 正文未入库）_

### 十二 · 十二、电机电流小导致走停 Motor Current Too Low Causes Stalling (The
- **qa_022** · 手动反推排查
- **qa_023** · 拉开门开门不正常加二极管电阻 （推开门关门不正常）
- **qa_024** · 拉开门关门不正常加二极管电阻（推开门开门不正常）
- **qa_025** · 电机电流小的原因
- **qa_026** · 信息补充：万用表测机臂电流
- **qa_027** · 测工作电流详细步骤
- **qa_028** · 测机臂空载电流
- **qa_043** · 电机电流小走停·并电阻负载 Motor stalls · low current · parallel load resistor
- _（另有 4 段 H1 orphan 正文未入库）_

### 十三 · 十三、电机转机臂不伸缩 Motor Runs But Gate Doesn't Move
- **qa_036** · 伸太过缩不回去 Arm Extended Too Far Won't Retract
- **qa_037** · 电机转但机臂不伸缩 Motor Runs But Arm Won't Move
- _（另有 16 段 H1 orphan 正文未入库）_

### 十四 · 十四、机臂声音异常 Abnormal Noise From Arm
- **qa_039** · 机臂声音异常 Abnormal Noise From Arm
- _（另有 35 段 H1 orphan 正文未入库）_

### 十五 · 十五、离合打不开 Clutch Won't Release
- **qa_038** · 离合打不开 Clutch Won't Release
- _（另有 22 段 H1 orphan 正文未入库）_

### — · 风会把门吹开（或者外力能把门推开一点） There is Little Play When the Gate 
- **qa_032** · 风会把门吹开 There is Little Play When the Gate is Closed
- _（另有 6 段 H1 orphan 正文未入库）_

### 十七 · 十七、保养与润滑 Maintenance and Lubrication
- **qa_040** · 日常保养润滑 Routine Maintenance and Lubrication
- **qa_041** · 深度润滑与保养参考 Deep Lubrication and Maintenance Guides
- _（另有 29 段 H1 orphan 正文未入库）_

### 十八 · 十八、其他产品知识讲解
- **qa_042** · 其他产品知识讲解 Product Knowledge
- _（另有 38 段 H1 orphan 正文未入库）_


# AD5S · zh/en 信息量差异清单

**源**：`_scratch/run-ad5s/qa_groups.json` · **组数**：43 · **有缺口**：39 · **扫描**：BL-V1-05（2026-07-05）

## 子模式分类

| 子模式 | 含义 | 组数 |
| --- | --- | ---: |
| **detail_link** | EN 含 URL，ZH 无对应链 | 2 |
| **detail_prose** | EN prose 明显更长，混合细节+话术 | 20 |
| **detail_spec** | 骨架对齐，EN 步骤内多规格/型号/数值（AD5S 型） | 1 |
| **structural_branch** | EN 条件分支明显多于 ZH | 16 |

## 逐组清单

### qa_001 · `detail_prose`
- **问题**：控制板灯不亮（适配器）No Led On the Control Board
- **配图**：image_001.png
- **长度**：zh=267 / en=1074

### qa_002 · `detail_prose`
- **问题**：控制板灯不亮（纯太阳能）
- **配图**：—
- **长度**：zh=253 / en=1235

### qa_003 · `detail_prose`
- **问题**：太阳能不能给电池充电 The Batteries Cannot Be Charged by Solar
- **配图**：image_002.jpg, image_003.png, image_004.png
- **长度**：zh=232 / en=1408

### qa_004 · `detail_prose`
- **问题**：接上太阳能板就不工作 The Gate Opener Quits Working Once Solar Panels Connected
- **配图**：—
- **长度**：zh=816 / en=4064

### qa_005 · `structural_branch`
- **问题**：学不上遥控器 （学习灯不亮）Cannot Program Remote
- **配图**：—
- **长度**：zh=124 / en=663

### qa_006 · `structural_branch`
- **问题**：学不上遥控器 （学习灯亮）Cannot Program Remote
- **配图**：—
- **长度**：zh=150 / en=1167

### qa_007 · `detail_prose`
- **问题**：其中一个遥控器无法工作 One (or Some) of Remotes Doesn't Work
- **配图**：—
- **长度**：zh=84 / en=445

### qa_008 · `structural_branch`
- **问题**：遥控距离不够 Short Remote Range
- **配图**：image_005.png, image_006.png
- **长度**：zh=105 / en=1336

### qa_009 · `structural_branch`
- **问题**：多次按遥控器门机才反应 Remote Needs Multiple Presses
- **配图**：—
- **长度**：zh=223 / en=1627

### qa_010 · `detail_spec`
- **问题**：按遥控器没有反应 No Response When The Remote Is Pressed
- **配图**：image_007.png
- **长度**：zh=620 / en=3263
- **EN 独有（抽样）**：
  - `dip_switch`: dip switch #5

### qa_011 · `detail_prose`
- **问题**：控制板有持续咔哒声 Control Board Clicking Continuously
- **配图**：—
- **长度**：zh=137 / en=825

### qa_012 · `detail_prose`
- **问题**：按遥控器保险丝烧 Fuse Blows When Pressing Remote
- **配图**：—
- **长度**：zh=397 / en=1887

### qa_013 · `detail_prose`
- **问题**：不工作（只CODE LED微微亮）
- **配图**：—
- **长度**：zh=74 / en=315

### qa_014 · `detail_prose`
- **问题**：一个机臂只朝一个方向 One Arm Only Work One Direction
- **配图**：image_008.png
- **长度**：zh=476 / en=1232

### qa_015 · `detail_prose`
- **问题**：两个机臂只朝一个方向 Two Arms Only Work One Direction
- **配图**：—
- **长度**：zh=121 / en=930

### qa_016 · `structural_branch`
- **问题**：开到位后又弹回来·拉开门 Gate Open Bounce Back · Pull-to-Open · Open Position
- **配图**：image_009.png, image_010.png, image_011.jpg
- **长度**：zh=224 / en=1761

### qa_017 · `structural_branch`
- **问题**：开到位后反弹·推开门 Gate Open Bounce Back · Push-to-Open · Limit B
- **配图**：image_012.png, image_013.png
- **长度**：zh=136 / en=1499

### qa_018 · `structural_branch`
- **问题**：拉开门 关到位后又弹回来 Gate Close Bounce Back · Pull-to-Open · Limit B
- **配图**：image_014.png, image_015.png
- **长度**：zh=251 / en=1504

### qa_019 · `structural_branch`
- **问题**：推开门·关到位后又弹回来 Gate Close Bounce Back · Push-to-Open
- **配图**：image_016.png, image_017.png, image_018.jpg
- **长度**：zh=266 / en=1809

### qa_020 · `structural_branch`
- **问题**：关门限位不到位·限位B（推/拉开门）Gate Close Limit · Limit Switch B · Push/Pull
- **配图**：image_019.png, image_020.png
- **长度**：zh=220 / en=1536

### qa_021 · `structural_branch`
- **问题**：关门限位不到位·限位A外移·磁环排查 Gate Close Limit · Limit A · Magnet/Short Test
- **配图**：image_021.png, image_022.png, image_023.png
- **长度**：zh=170 / en=1422

### qa_023 · `detail_prose`
- **问题**：并接机臂红黑线排查
- **配图**：image_024.png, image_025.png
- **长度**：zh=158 / en=1479

### qa_024 · `detail_prose`
- **问题**：手动反推来排查+电阻
- **配图**：image_026.png, image_027.png, image_028.png, image_029.png
- **长度**：zh=685 / en=3566

### qa_029 · `detail_link`
- **问题**：深度润滑（拆机臂）Deep Lubrication
- **配图**：—
- **长度**：zh=36 / en=532
- **EN 独有（抽样）**：
  - `url`: https://www.youtube.com/watch?v=IRIA5iaWHqE
  - `url`: https://youtu.be/0dkm1sKYjzA
  - `url`: https://youtu.be/5s1EQh2M_mo

### qa_031 · `structural_branch`
- **问题**：随意开关门 Random Opening/Closing
- **配图**：—
- **长度**：zh=59 / en=1235

### qa_032 · `structural_branch`
- **问题**：缓停止有问题 Soft Stop Issues
- **配图**：—
- **长度**：zh=123 / en=1013

### qa_033 · `detail_prose`
- **问题**：自动关门不生效 Auto Close Function Doesn't Work
- **配图**：—
- **长度**：zh=294 / en=1070

### qa_034 · `detail_prose`
- **问题**：风会把门吹开 There is Little Play When the Gate is Closed
- **配图**：—
- **长度**：zh=119 / en=1220

### qa_035 · `structural_branch`
- **问题**：一个机臂完全不工作 One Arm Doesn't Work
- **配图**：—
- **长度**：zh=102 / en=1270

### qa_036 · `structural_branch`
- **问题**：门机运行慢 Gate Operates Slowly
- **配图**：—
- **长度**：zh=215 / en=1772

### qa_037 · `structural_branch`
- **问题**：开门不限位/过位（拉开门·限位A·开位）Gate Open Limit · Pull-to-Open · Limit A Open
- **配图**：—
- **长度**：zh=140 / en=811

### qa_038 · `detail_prose`
- **问题**：伸太过缩不回去 Arm Extended Too Far Won't Retract
- **配图**：—
- **长度**：zh=177 / en=1056

### qa_039 · `detail_prose`
- **问题**：电机转但机臂不伸缩 Motor Runs But Arm Won't Move
- **配图**：—
- **长度**：zh=210 / en=924

### qa_040 · `detail_prose`
- **问题**：开关门中途走停或反弹 Gate Stops or Bounces Mid-Travel
- **配图**：—
- **长度**：zh=445 / en=3206

### qa_041 · `detail_prose`
- **问题**：离合打不开·关门太紧 Clutch Won't Release · Gate Closed Too Tight
- **配图**：—
- **长度**：zh=94 / en=362

### qa_042 · `detail_link`
- **问题**：离合打不开·伸太过或内部卡住 Clutch Won't Release · Over-Extended or Internal Jam
- **配图**：—
- **长度**：zh=197 / en=2235
- **EN 独有（抽样）**：
  - `url`: https://youtube.com/shorts/EeHaJdHqE-U?feature=share
  - `url`: https://youtu.be/0dkm1sKYjzA
  - `url`: https://youtu.be/5s1EQh2M_mo
  - `url`: https://www.youtube.com/watch?v=IRIA5iaWHqE

### qa_043 · `structural_branch`
- **问题**：机臂声音异常 Abnormal Noise From Arm
- **配图**：—
- **长度**：zh=332 / en=1946
- **EN 独有（抽样）**：
  - `url`: https://www.youtube.com/watch?v=IRIA5iaWHqE

### qa_026 · `detail_prose`
- **问题**：限位原理
- **配图**：—
- **长度**：zh=257 / en=1337

### qa_027 · `detail_prose`
- **问题**：电池和太阳能板规格
- **配图**：image_030.png
- **长度**：zh=1089 / en=2753

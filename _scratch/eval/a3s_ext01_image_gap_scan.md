# A3S EXT-01 · orphan 配图缺口扫描

**docx**：`A3S-A5S-A8S常见问题排查.docx` · **prod**：`qa_029`–`qa_043`

## 结论性质

- **新发现**：BL-A3S-EXT-01 overlay 脚本只抽 **orphan 段落文字 + URL→links[]**，**未走** `qa_doc_extractor` 的 inline 图抽取。
- **系统性**：凡 H1 orphan 段内嵌图 + 正文写 “see screenshot below” 的，prod `images[]` 均为空。
- **非已知 backlog**：此前验收维是 links / eval / thin-ZH，**未列配图完整性 gate**。

## docx · H1 orphan 区含图或文字指图

| H1 | orphan 图 | H2 图 | 文字指图 |
| --- | ---: | ---: | --- |
| 四、只朝一个方向 Only Opens/Closes One Direction | 1 | 0 | — |
| 八、开关门过程中走停或反弹 Gate Stops or Bounces During Op | 1 | 0 | — |
| 十三、电机转机臂不伸缩 Motor Runs But Gate Doesn't Move | 3 | 0 | — |
| 十四、机臂声音异常 Abnormal Noise From Arm | 2 | 0 | — |
| 十五、离合打不开 Clutch Won't Release | 5 | 0 | Use the release key to engage the clutch and manua |
| 十七、保养与润滑 Maintenance and Lubrication | 0 | 0 | Besides, grease is needed to lubricate the inside  |

## qa_029–043 · images[] vs 正文指图

| group | images | EN指图 | ZH指图 | section |
| --- | ---: | :---: | :---: | --- |
| qa_029 | 0 | · | · | 五、随意开关门 Random Opening/Closing |
| qa_030 | 0 | · | · | 六、缓停止有问题（缓停止错乱或者没有缓停止）Soft Stop Issues |
| qa_031 | 0 | · | · | 七、自动关门不生效 Auto Close Function Doesn't Wo |
| qa_032 | 0 | · | · | 风会把门吹开（或者外力能把门推开一点） There is Little Play |
| qa_033 | 0 | · | **step4 短接** | 四、只朝一个方向 Only Opens/Closes One Direction |
| qa_034 | 0 | · | · | 门机运行慢 Gate Operates Slowly |
| qa_035 | 0 | · | · | 八、开关门过程中走停或反弹 Gate Stops or Bounces Duri |
| qa_036 | 0 | · | · | 十三、电机转机臂不伸缩 Motor Runs But Gate Doesn't  |
| qa_037 | 0 | · | · | 十三、电机转机臂不伸缩 Motor Runs But Gate Doesn't  |
| qa_038 | 0 | ✓ | · | 十五、离合打不开 Clutch Won't Release |
| qa_039 | 0 | · | · | 十四、机臂声音异常 Abnormal Noise From Arm |
| qa_040 | 0 | ✓ | · | 十七、保养与润滑 Maintenance and Lubrication |
| qa_041 | 0 | · | · | 十七、保养与润滑 Maintenance and Lubrication |
| qa_042 | 0 | · | · | 十八、其他产品知识讲解 |
| qa_043 | 0 | · | · | 十二、电机电流小导致走停 Motor Current Too Low Cause |

**baseline qa_001–028**：14 组有图 · 共 23 张
**EXT qa_029–043**：0 张 · **指图无图** 2 组 · **orphan 有图未挂** ≥1 组（**qa_033**）

## 指图但 images[] 为空（需修）

- **型 B · 归属遗漏**：**qa_033** · docx「4 短接限位」· 与 **`image_019.png`** 同资产 · 现仅 **qa_021** 挂载 → EXT-02 **一图多组** 分案
- **qa_038** · 十五、离合打不开 Clutch Won't Release
- **qa_040** · 十七、保养与润滑 Maintenance and Lubrication

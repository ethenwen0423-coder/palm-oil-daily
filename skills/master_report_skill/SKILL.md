---
name: master_report_skill
description: Master orchestration skill for the oil and fats morning report workflow. Use when Codex needs to generate, review, or maintain the palm-oil/oil-fats morning report pipeline by enforcing the execution order and responsibility boundaries among market_data_skill, oil_report_freshness, report_writer_skill, headline_skill, and report_quality_gate. This skill only coordinates sub-skills and does not write reports, generate titles, fetch data, or decide trading direction.
---

# Skill：master_report_skill
## 一、Skill定位
master_report_skill 是油脂晨报生成流程的总控调度 Skill。
它不负责直接写报告。
它不负责生成标题。
它不负责抓取行情数据。
它不负责判断交易方向。
它只负责规定各个 Skill 的执行顺序、职责边界和输出关系。
---
## 二、固定执行流程
每次生成油脂晨报时，必须按以下顺序执行：
1. market_data_skill
2. oil_report_freshness
3. report_writer_skill
4. headline_skill
5. report_quality_gate
如果当前项目中没有某个 Skill，先保留接口说明，不要伪造实现。
---
## 三、各 Skill 职责
### 1. market_data_skill
负责：
- 获取行情数据
- 获取库存数据
- 获取价差数据
- 获取外盘数据
- 获取新闻与研报来源
- 记录数据时间与来源
不得负责：
- 生成观点
- 生成标题
- 生成交易建议
---
### 2. oil_report_freshness
负责：
- 判断信息新鲜度
- 区分今日新增驱动与延续性背景
- 判断哪些信息不能作为今日主线
- 输出信息新鲜度表
- 输出建议主线
不得负责：
- 生成标题
- 生成完整正文
- 覆盖 headline_skill
---
### 3. report_writer_skill
负责：
- 根据 market_data_skill 和 oil_report_freshness 的输出生成正文
- 生成今日观点、昨夜发生了什么、关键数据、开盘推演、风险提示等正文模块
不得负责：
- 生成 Headline
- 生成 Subheadline
- 把低新鲜度信息重新提升为今日主线
---
### 4. headline_skill
负责：
- 生成 Headline
- 生成 Subheadline
- 标题质量检查
不得负责：
- 改写正文事实
- 新增正文中不存在的观点
---
### 5. report_quality_gate
负责：
- 最终质量检查
- 检查标题、正文、来源、时效性是否一致
不得负责：
- 新增观点
- 伪造来源
- 覆盖前面 Skill 的职责
---
## 四、冲突处理规则
如果不同 Skill 规则冲突，按以下优先级处理：
- 标题问题：以 headline_skill 为准
- 信息新鲜度问题：以 oil_report_freshness 为准
- 正文结构问题：以 report_writer_skill 为准
- 数据准确性问题：以 market_data_skill 为准
- 最终质量问题：以 report_quality_gate 为准
---
## 五、强制约束
生成报告时必须满足：
1. 不能跳过 oil_report_freshness。
2. 不能让 report_writer_skill 直接把旧消息写成今日主线。
3. 不能让 oil_report_freshness 修改标题。
4. 不能让 headline_skill 新增正文中没有的观点。
5. 不能把无法核验的信息写成确定事实。
6. 不能把周度库存、旧政策、旧研报写成今日最大驱动。
---
## 六、最终输出结构
最终报告建议结构：
1. Headline
2. Subheadline
3. 今日观点
4. 今日交易信号
5. 昨夜发生了什么
6. 今日关键数据
7. 信息新鲜度检查
8. 今日交易重点
9. 开盘推演
10. 关键价格
11. 今日观察指标
12. 风险提示
13. 信息来源与核验说明
14. AI观点风险提示
---
## 七、最终原则
master_report_skill 是调度层。
它的作用是让各个 Skill 按顺序工作。
它不替代任何子 Skill。
它不抢任何子 Skill 的职责。

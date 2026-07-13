---
name: master_report_skill
description: Master orchestration skill for the oil and fats morning report workflow. Use when Codex needs to generate, review, or maintain the palm-oil/oil-fats morning report pipeline by enforcing the execution order and responsibility boundaries among market_data_skill, data_quality_gate_skill, oil_report_freshness, report_writer_skill, headline_skill, report_quality_gate, and the pre-publish forecast audit. This skill only coordinates sub-skills and does not write reports, generate titles, fetch data, or decide trading direction.
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
2. data_quality_gate_skill
3. oil_report_freshness
4. report_writer_skill
5. headline_skill
6. report_quality_gate
7. forecast_tracking_skill（仅发布前冻结审计）
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
### 2. data_quality_gate_skill
负责：
- 校验最新价、昨结、涨跌额和涨跌幅公式
- 检查合约月份、单位、日期和时区
- 比较 AkShare、妙想、问财等来源
- 明确 FCPO 涨跌口径
- 检查库存、出口和产量的统计日期
- 来源冲突超过容差时降级为“需进一步核验”
- 关键数据失败时停止正式发布
不得负责：
- 生成观点
- 生成标题
- 改写正文
- 判断交易方向
---
### 3. oil_report_freshness
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
### 4. report_writer_skill
负责：
- 根据 market_data_skill 和 oil_report_freshness 的输出生成正文
- 生成今日观点、昨夜发生了什么、关键数据、开盘推演、风险提示等正文模块
- 把正文从资讯汇总升级为研究分析，但不增加报告篇幅
- 对核心观点给出原因、驱动排序、传导链、预期与现实差异、失效条件和研究置信度
不得负责：
- 生成 Headline
- 生成 Subheadline
- 把低新鲜度信息重新提升为今日主线
- 新增大量一级标题或用重复资讯拉长正文
---
### 5. headline_skill
负责：
- 生成 Headline
- 生成 Subheadline
- 标题质量检查
不得负责：
- 改写正文事实
- 新增正文中不存在的观点
---
### 6. report_quality_gate
负责：
- 最终质量检查
- 检查标题、正文、来源、时效性是否一致
不得负责：
- 新增观点
- 伪造来源
- 覆盖前面 Skill 的职责
---
### 7. forecast_tracking_skill
负责：
- 在 data_quality_gate_skill 已通过且最终发布前，从通过质量门的临时结构化 oil_futures 数据冻结预测
- 只记录 P、Y、OI 中 `contract_rank == 1` 的合约
- 保存报告日期、可验证的数据截止时间、概率、区间、置信度和版本字段，供后续审计
- 预测冻结失败时阻止日报正式发布
不得负责：
- 参与观点、标题、评分或报告正文决策
- 从 Markdown 报告解析预测
- 使用盘中未来数据、收盘数据或发布后数据回填晨报预测
---
## 四、冲突处理规则
如果不同 Skill 规则冲突，按以下优先级处理：
- 标题问题：以 headline_skill 为准
- 信息新鲜度问题：以 oil_report_freshness 为准
- 正文结构问题：以 report_writer_skill 为准
- 数据准确性问题：以 market_data_skill 为准
- 确定性数据校验问题：以 data_quality_gate_skill 为准
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
7. report_writer_skill 必须先调用 skills/report_writer_skill/SKILL.md，再按通用写作规范润色。
8. report_writer_skill 必须围绕影响最大的前两项驱动展开，不得平均罗列新闻。
9. report_writer_skill 输出的核心观点必须包含“为什么”、传导路径、预期与现实、失效条件和置信度。
10. data_quality_gate_skill 未通过时禁止正式发布。
11. forecast_tracking_skill 只能在数据质量门通过后、正式发布前运行；冻结失败时禁止发布日报、tab 和数据集。
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

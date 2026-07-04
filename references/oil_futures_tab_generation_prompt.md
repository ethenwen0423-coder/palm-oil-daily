# 油脂主力合约 Tab 生成规则

本规则只用于首页 `油脂主力合约` tab，不用于油脂日报或周报。

生成或更新 `data/oil_futures.js` 前必须执行：

1. 读取 `skills/master_analytic_skill/SKILL.md`。
2. 按 master analytic flow 调用 `skills/technical_basic_analysis_skill/SKILL.md`。
3. 使用 `基本面评分 * 30% + 技术面评分 * 70%` 计算每个油脂相关主力合约的综合评分。
4. 使用 `skills/master_analytic_skill/scripts/analyze_contracts.py` 调用分支 skill。
5. 分支 skill 使用 `skills/technical_basic_analysis_skill/scripts/analysis_engine.py` 生成技术评分、基本面评分、当前行情观点和综合止盈止损点位。
6. 综合止盈止损必须内部纳入多类候选策略，包括波动包络、突破确认、均线支撑压力、区间/通道位置和风险回报测算；页面上不得单独标注具体算法名称。
7. 技术面与基本面必须分别输出详解字段，说明评分依据、关键位置、外盘联动、库存与价差影响。
8. 必须生成 `watchlist_options`，值列表使用各合约简称，供页面自选合约卡片确认后刷新展示。
9. 缺失或无法核验的数据必须写 `需进一步核验`。

默认展示合约卡片以国内主力合约为主：

- P：大商所棕榈油主力
- Y：大商所豆油主力
- OI：郑商所菜油主力

外盘合约只展示与棕榈油最相关的一项：

- FCPO：BMD 马棕油主力

其他外盘变量只作为技术/基本面联动因子写入详解，不作为默认合约卡片：

- CBOT BO：CBOT 豆油主力

输出到 `data/oil_futures.js` 时，每个合约至少包含：

- symbol
- name
- market
- contract
- price
- change
- volume
- open_interest
- direction
- score.total
- score.technical
- score.fundamental
- score.stance
- view
- technical_detail[].title
- technical_detail[].text
- fundamental_detail[].title
- fundamental_detail[].text
- strategy_recommendation.entry
- strategy_recommendation.take_profit
- strategy_recommendation.stop_loss
- strategy_recommendation.basis
- watchlist_options[].value
- watchlist_options[].label
- watchlist_options[].name
- watchlist_options[].contract
- verification
- analysis_skill
- child_skill
- quality_note
- note

不得从日报正文直接复制观点作为 tab 结论；tab 结论必须来自主力合约独立评分。

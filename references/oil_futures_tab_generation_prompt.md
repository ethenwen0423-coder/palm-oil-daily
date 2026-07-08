# 油脂主力合约 Tab 生成规则

本规则只用于首页 `油脂主力合约` tab，不用于油脂日报或周报。

生成或更新 `data/oil_futures.js` 前必须执行：

1. 读取 `skills/master_analytic_skill/SKILL.md`。
2. 先读取并调用 `skills/contract_selector_skill/SKILL.md`。
3. 由 `contract_selector_skill` 调用 `skills/contract_selector_skill/scripts/select_contracts.py`，刷新 `data/contracts/current_contracts.json`。
4. 把 `current_contracts.json` 中全部 rank=1 主力和 rank=2 次主力合约作为今天分析入口，不得只取 rank=1。
5. 读取最近 5 次 `data/review/learning_notes/*.json`，如存在连续同类偏差，生成观点时必须提示近期模型容易低估/高估的因素。
6. 按 master analytic flow 调用 `skills/technical_basic_analysis_skill/SKILL.md`。
6. 使用 `技术面25% + 基本面25% + 驱动30% + 资金20%` 计算每个油脂相关主力合约的综合评分。
7. 使用 `skills/master_analytic_skill/scripts/analyze_contracts.py` 调用分支 skill。
8. 分支 skill 使用 `skills/technical_basic_analysis_skill/scripts/analysis_engine.py` 生成技术评分、基本面评分、驱动评分、资金评分、当前行情观点、观察位和失效条件。
9. 策略区只输出上方观察位、下方观察位、失效条件和风险提示，不输出明确交易指令。
10. 技术面、基本面、驱动、资金必须分别说明评分依据。
11. 必须生成 `watchlist_options`，值列表使用每个被发现的具体合约代码，供页面自选合约卡片确认后刷新展示。
12. 缺失或无法核验的数据必须写 `需进一步核验`。

默认国内合约来自 `contract_discovery_skill` 的当月流动性排序：

- P：大商所棕榈油，主力/次主力
- Y：大商所豆油，主力/次主力
- OI：郑商所菜油，主力/次主力
- M：大商所豆粕，主力/次主力
- RM：郑商所菜粕，主力/次主力

不得在前端或分析入口硬编码 `P2609`、`Y2609`、`OI2609` 等合约月份。

外盘合约只展示与棕榈油最相关的一项：

- FCPO：BMD 马棕油主力

其他外盘变量只作为技术/基本面联动因子写入详解，不作为默认合约卡片：

- CBOT BO：CBOT 豆油主力

输出到 `data/oil_futures.js` 时，每个合约至少包含：

- symbol
- product
- name
- market
- contract
- contract_rank
- contract_label
- price
- change
- volume
- open_interest
- direction
- score.total
- score.technical
- score.fundamental
- score.driver
- score.money_flow
- score.stance
- score.view_confidence
- score.contradiction_warning
- view_confidence
- contradiction_warning
- view
- technical_detail[].title
- technical_detail[].text
- fundamental_detail[].title
- fundamental_detail[].text
- strategy_recommendation.entry
- strategy_recommendation.take_profit
- strategy_recommendation.stop_loss
- strategy_recommendation.upper_watch
- strategy_recommendation.lower_watch
- strategy_recommendation.invalidation
- strategy_recommendation.basis
- watchlist_options[].value
- watchlist_options[].label
- watchlist_options[].display
- watchlist_options[].name
- watchlist_options[].contract
- watchlist_options[].contract_label
- verification
- analysis_skill
- child_skill
- quality_note
- note

不得从日报正文直接复制观点作为 tab 结论；tab 结论必须来自主力合约独立评分。

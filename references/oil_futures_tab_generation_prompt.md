# 油脂主力合约 Tab 生成规则

本规则只用于首页 `油脂主力合约` tab，不用于油脂日报或周报。

生成或更新 `data/oil_futures.js` 前必须执行：

1. 读取 `skills/master_analytic_skill/SKILL.md`。
2. 按 master analytic flow 调用 `skills/technical_basic_analysis_skill/SKILL.md`。
3. 使用 `基本面评分 * 30% + 技术面评分 * 70%` 计算每个油脂相关主力合约的综合评分。
4. 使用 `skills/master_analytic_skill/scripts/analyze_contracts.py` 调用分支 skill。
5. 分支 skill 使用 `skills/technical_basic_analysis_skill/scripts/analysis_engine.py` 生成技术评分、基本面评分、当前行情观点、ATR 策略和海龟 20 日突破点位。
6. 缺失或无法核验的数据必须写 `需进一步核验`。

默认覆盖合约：

- P：大商所棕榈油主力
- Y：大商所豆油主力
- OI：郑商所菜油主力
- FCPO：BMD 马棕油主力
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
- strategies[].name
- strategies[].entry
- strategies[].take_profit
- strategies[].stop_loss
- verification
- analysis_skill
- child_skill
- quality_note
- note

不得从日报正文直接复制观点作为 tab 结论；tab 结论必须来自主力合约独立评分。

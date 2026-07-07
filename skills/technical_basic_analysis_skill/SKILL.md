---
name: technical_basic_analysis_skill
description: Dynamic driver-led scoring skill for oil-related dominant futures contracts. Use as the child skill of master_analytic_skill when generating the oil-futures main-contract tab page. It scores contracts with 25% technical, 25% fundamental, 30% driver, and 20% money-flow analysis, then returns observation levels, invalidation conditions, confidence, contradiction warnings, and tab-ready conclusions. Alias: technical&basic analysis skill.
---

# Skill: technical&basic analysis skill

## Purpose

Use this skill to score oil-related dominant contracts for the homepage `油脂主力合约` tab.

This skill is independent from the oil morning report workflow. It does not write reports, generate titles, or replace daily-report skills.

## Required Inputs

For each contract, collect as many of these fields as possible:

- symbol, name, market, dominant contract month
- latest price, previous close, change percent
- volume, open interest, open-interest change
- moving averages: MA5, MA10, MA20, MA60
- MACD, RSI, KDJ, volatility proxy
- recent high/low and support/resistance
- inventory, basis, import margin, crush margin, spread, supply-demand change
- external drivers such as FCPO, CBOT soybean oil, crude oil, FX, policy, weather
- source and timestamp

If a field is unavailable, mark it `需进一步核验` and do not invent a number.

## Scoring Formula

Use a 0-100 scoring scale.

```text
total_score = technical_score * 0.25 + basic_score * 0.25 + driver_score * 0.30 + money_flow_score * 0.20
```

Round `total_score` to one decimal.

## Fundamental Score: 25%

Calculate `basic_score` from these components:

| Component | Weight inside basic_score |
| --- | ---: |
| Supply-demand and inventory | 30% |
| Basis, import margin, crush margin, and spread structure | 25% |
| External-market linkage | 20% |
| Policy, weather, and event drivers | 15% |
| Source freshness and reliability | 10% |

Scoring guide:

- 80-100: clear bullish fundamental support
- 65-79: mild bullish support
- 45-64: neutral or mixed
- 30-44: mild bearish pressure
- 0-29: clear bearish pressure

Inventory, basis, import margin, and crush margin are background pressure unless updated within the latest 24 hours.

## Technical Score: 25%

Technical analysis may only judge:

- price position
- trend structure
- support and resistance
- volatility range

It must not independently decide the final bullish or bearish view.

## Driver Score: 30%

Calculate `driver_score` from:

- FCPO
- CBOT soybean oil
- WTI/Brent crude oil
- CBOT soybean
- weather
- shipping/export if available
- same-day policy/news

Fresh information from the latest 24 hours has the highest weight.

Weekly inventory cannot be today's main driver. Old policy, old research, and unverified rumors must not add score.

## Money Flow Score: 20%

Calculate `money_flow_score` from:

- same-day change percent
- volume change
- open-interest change
- sector strength ranking
- P/Y/OI relative strength
- spread changes

## Strategy Function

`stance_for()` must not rely only on `total_score`.

- If `driver_score` and `money_flow_score` point in the same direction, prioritize drivers and money flow.
- If technicals conflict with drivers, output `震荡偏强` or `震荡偏弱`.
- If signals conflict materially, output `分歧震荡`.
- If key data is missing or source reliability is weak, use `观望` or `需进一步核验`.

## Operation Strategy Calculation

Use `scripts/analysis_engine.py` for the full tab-card analysis flow. It contains:

- `technical_analysis`: price position, trend structure, support/resistance, volatility range, and breakout-position scoring
- `fundamental_score`: supply-demand, inventory, spread, and external-market scoring
- `driver_score`: same-day external, policy, weather, shipping, and news driver scoring
- `money_flow_score`: price, volume, open-interest, relative-strength, and spread-flow scoring
- `strategy_recommendation`: calculate observation levels and invalidation conditions
- `build_market_view`: score-led current market view

Use `scripts/strategy_calculator.py` only when deterministic post-score mapping is useful.

`strategy_recommendation` should internally combine at least these method families:

- volatility envelope
- breakout confirmation
- moving-average support/resistance
- range and band position
- risk-reward symmetry

The tab output must not expose the exact method names as separate trade cards. It should show only upper watch level, lower watch level, invalidation condition, risk note, and a short basis explaining that multiple candidate points were combined.

The script accepts JSON with `basic_score`, `technical_score`, optional `price`, `support`, `resistance`, and `data_quality`, and returns:

- total_score
- rating
- strategy
- direction
- risk_control
- position_size
- invalidation

Manual function definitions:

```text
weighted_score = round(technical_score * 0.25 + basic_score * 0.25 + driver_score * 0.30 + money_flow_score * 0.20, 1)

direction =
  ↑ if weighted_score >= 60
  ↓ if weighted_score < 45
  → otherwise

position_size =
  30%-40% only when score >= 75 and data_quality is high
  10%-20% when 60 <= score < 75
  0%-10% when 45 <= score < 60
  0% or defensive short-bias when score < 45
```

Risk rules:

- If `data_quality` is `low`, force `strategy = 观望`.
- If price is near resistance and score is below 75, do not chase.
- If price breaks support and technical score is below 45, mark downside risk.
- If driver/money flow and technical score diverge materially, downgrade the stance to range-bound or split-signal.
- If support or resistance cannot be verified, write `关键位需进一步核验`.

## Required Output

Return one table for all contracts:

| 合约 | 基本面评分 | 技术面评分 | 综合评分 | 方向 | 策略 | 支撑 | 压力 | 风控 | 结论 |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |

Then return tab-ready JSON fields for each contract.

## Hard Rules

- Do not let technical analysis independently decide the final view.
- Do not use stale inventory, old policy, or unverified rumors as current facts.
- Do not output exact trading instructions; output observation levels and invalidation only.
- Do not write `确定上涨` or `确定下跌`; use score-led strategy language.
- If data cannot be verified, say `需进一步核验`.

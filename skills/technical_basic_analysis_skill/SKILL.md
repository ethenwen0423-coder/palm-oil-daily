---
name: technical_basic_analysis_skill
description: Technical and fundamental scoring skill for oil-related dominant futures contracts. Use as the child skill of master_analytic_skill when generating the oil-futures main-contract tab page. It scores contracts with 30% fundamental analysis and 70% technical analysis, then calculates operation strategy, support/resistance, risk controls, and tab-ready conclusions. Alias: technical&basic analysis skill.
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
total_score = basic_score * 0.30 + technical_score * 0.70
```

Round `total_score` to one decimal.

## Fundamental Score: 30%

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

## Technical Score: 70%

Calculate `technical_score` from these components:

| Component | Weight inside technical_score |
| --- | ---: |
| Trend structure: price vs MA5/MA10/MA20/MA60 | 30% |
| Momentum: MACD, RSI, KDJ, breakout/failure | 25% |
| Volume and open-interest confirmation | 20% |
| Support/resistance position and risk-reward | 15% |
| Volatility and intraday execution quality | 10% |

Scoring guide:

- 80-100: strong trend continuation
- 65-79: tradable bullish bias
- 45-64: range-bound or mixed
- 30-44: bearish bias
- 0-29: strong downside trend

## Strategy Function

Use this mapping after calculating `total_score`:

| Total score | Strategy | Rating |
| ---: | --- | --- |
| >= 75 | 偏多 | 强势 |
| 60-74.9 | 震荡偏多 | 偏强 |
| 45-59.9 | 震荡 | 中性 |
| 30-44.9 | 震荡偏空 | 偏弱 |
| < 30 | 偏空 | 弱势 |

Convert to tab strategy labels:

- `偏多` for scores >= 75
- `震荡` for scores from 45 to 74.9
- `偏空` for scores < 45
- `观望` when key data is missing or source reliability is weak

## Operation Strategy Calculation

Use `scripts/analysis_engine.py` for the full tab-card analysis flow. It contains:

- `technical_analysis`: MA/MACD/RSI/BOLL/volatility/breakout scoring
- `fundamental_score`: supply-demand, inventory, spread, and external-market scoring
- `strategy_recommendation`: calculate multiple candidate take-profit/stop-loss points, then return one integrated recommendation
- `build_market_view`: score-led current market view

Use `scripts/strategy_calculator.py` only when deterministic post-score mapping is useful.

`strategy_recommendation` should internally combine at least these method families:

- volatility envelope
- breakout confirmation
- moving-average support/resistance
- range and band position
- risk-reward symmetry

The tab output must not expose the exact method names as separate trade cards. It should show only `综合策略建议`, `参考触发`, `综合止盈`, `综合止损`, and a short basis explaining that multiple candidate points were combined.

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
weighted_score = round(basic_score * 0.30 + technical_score * 0.70, 1)

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
- If fundamental score and technical score diverge by more than 25 points, reduce position size one level.
- If support or resistance cannot be verified, write `关键位需进一步核验`.

## Required Output

Return one table for all contracts:

| 合约 | 基本面评分 | 技术面评分 | 综合评分 | 方向 | 策略 | 支撑 | 压力 | 风控 | 结论 |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |

Then return tab-ready JSON fields for each contract.

## Hard Rules

- Do not let fundamental narrative override the 70% technical weight.
- Do not use stale inventory, old policy, or unverified rumors as current facts.
- Do not output exact trading instructions without support, resistance, and invalidation.
- Do not write `确定上涨` or `确定下跌`; use score-led strategy language.
- If data cannot be verified, say `需进一步核验`.

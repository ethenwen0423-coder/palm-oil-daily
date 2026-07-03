---
name: master_analytic_skill
description: Master orchestration skill for generating or updating the oil-futures main-contract tab page. Use when Codex needs to build, refresh, or review the homepage tab for oil-related dominant contracts such as P, Y, OI, FCPO, and CBOT soybean oil. This skill is independent from the daily-report workflow and coordinates technical_basic_analysis_skill plus tab data rendering; it does not write morning reports or call daily-report skills.
---

# Skill: master_analytic_skill

## Purpose

Use this skill only when generating, refreshing, or reviewing the `油脂主力合约` tab page and its data, especially `data/oil_futures.js`.

Do not use this skill for:

- oil morning report generation
- report headline generation
- report writing
- report freshness governance

This is an analytics-tab orchestration skill, not a daily-report skill.

## Execution Flow

When generating the main-contract tab, execute in this order:

1. Collect market data for oil-related dominant contracts.
2. Call `../technical_basic_analysis_skill/SKILL.md`.
3. Score each contract using `基本面 * 30% + 技术面 * 70%`.
4. Calculate operation strategy fields.
5. Generate or update the tab data payload.
6. Check that every visible tab conclusion can be traced to scored data.

Callable entrypoint:

- `scripts/analyze_contracts.py`

This master entrypoint accepts one contract payload or a list of contract payloads as JSON, calls `technical_basic_analysis_skill`, and applies the quality gate before returning tab-ready analysis fields.

If a required sub-skill or data source is missing, keep the interface and mark the missing item as `需进一步核验`; do not fabricate data.

## Scope

Default contracts:

- `P`: DCE palm oil dominant contract
- `Y`: DCE soybean oil dominant contract
- `OI`: CZCE rapeseed oil dominant contract
- `FCPO`: Bursa Malaysia palm oil dominant contract
- `CBOT BO`: CBOT soybean oil dominant contract

Optional linked variables:

- WTI/Brent crude oil
- USD/CNY or CNH
- DXY
- soybean complex
- rapeseed/canola futures

## Sub-Skill Responsibilities

### technical_basic_analysis_skill

Alias: `technical&basic analysis skill`.

Responsible for:

- fundamental score from supply-demand, inventory, basis, margins, import cost, policy, and external-market drivers
- technical score from trend, momentum, volume/open-interest confirmation, volatility, support/resistance, and relative strength
- combined score with `basic_score * 0.30 + technical_score * 0.70`
- operation strategy calculation

Not responsible for:

- writing daily reports
- generating report headlines
- changing website layout
- fabricating unavailable data

## Required Tab Data Output

For each contract, return a structured item:

```json
{
  "symbol": "P",
  "name": "棕榈油",
  "market": "DCE",
  "contract": "主力",
  "price": "需进一步核验",
  "change": "需进一步核验",
  "volume": "需进一步核验",
  "open_interest": "需进一步核验",
  "direction": "→",
  "basic_score": 0,
  "technical_score": 0,
  "total_score": 0,
  "rating": "中性",
  "strategy": "观望",
  "support": "需进一步核验",
  "resistance": "需进一步核验",
  "risk_control": "需进一步核验",
  "note": "需进一步核验"
}
```

Allowed `direction` values:

- `↑`
- `↓`
- `→`

Allowed `strategy` values:

- `偏多`
- `偏空`
- `震荡`
- `观望`

## Quality Gate

Before finishing, verify:

- `technical_basic_analysis_skill` was called or explicitly marked unavailable.
- Every contract has `basic_score`, `technical_score`, and `total_score`.
- `total_score = basic_score * 0.30 + technical_score * 0.70`.
- Operation strategy is consistent with score and risk controls.
- Missing data is shown as `需进一步核验`.
- The tab output does not mention daily-report conclusions unless independently supported by tab data.

If any check fails, regenerate the affected contract item before updating the tab.

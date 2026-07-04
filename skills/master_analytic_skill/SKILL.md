---
name: master_analytic_skill
description: Master orchestration skill for generating or updating the oil-futures main-contract tab page. Use when Codex needs to build, refresh, or review the homepage tab for domestic oil-related dominant contracts such as P, Y, and OI, plus the single most palm-oil-relevant external reference contract FCPO. CBOT soybean oil is a linked driver, not a visible contract card. This skill is independent from the daily-report workflow and coordinates technical_basic_analysis_skill plus tab data rendering; it does not write morning reports or call daily-report skills.
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
7. Generate `watchlist_options` from the prepared contract payload so the static GitHub Pages UI can refresh a user-selected contract card without a backend call.

Callable entrypoint:

- `scripts/analyze_contracts.py`

This master entrypoint accepts one contract payload or a list of contract payloads as JSON, calls `technical_basic_analysis_skill`, and applies the quality gate before returning tab-ready analysis fields.

If a required sub-skill or data source is missing, keep the interface and mark the missing item as `需进一步核验`; do not fabricate data.

## Scope

Default visible contract cards:

- `P`: DCE palm oil dominant contract
- `Y`: DCE soybean oil dominant contract
- `OI`: CZCE rapeseed oil dominant contract
- `FCPO`: Bursa Malaysia palm oil dominant contract, shown as the only external visible card because it is the closest external reference for palm oil

External linked variables, not default visible cards:

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
  "score": {
    "total": 0,
    "technical": 0,
    "fundamental": 0,
    "stance": "中性",
    "weights": "技术面70% / 基本面30%"
  },
  "view": "需进一步核验",
  "technical_detail": [],
  "fundamental_detail": [],
  "strategy_recommendation": {
    "entry": "需进一步核验",
    "take_profit": "需进一步核验",
    "stop_loss": "需进一步核验",
    "basis": "需进一步核验"
  },
  "note": "需进一步核验"
}
```

For the page-level payload, also return a contract selector list:

```json
  "watchlist_options": [
    {
      "value": "P",
      "label": "P",
      "name": "棕榈油",
      "contract": "P2609"
    }
  ]
```

Allowed `direction` values:

- `↑`
- `↓`
- `→`

Allowed `score.stance` values:

- `偏多`
- `偏空`
- `震荡`
- `观望`

## Quality Gate

Before finishing, verify:

- `technical_basic_analysis_skill` was called or explicitly marked unavailable.
- Every contract has `score.fundamental`, `score.technical`, and `score.total`.
- `score.total = score.fundamental * 0.30 + score.technical * 0.70`.
- `strategy_recommendation` gives one integrated take-profit and stop-loss recommendation, without exposing a single named calculation method as the visible source.
- Missing data is shown as `需进一步核验`.
- The tab output does not mention daily-report conclusions unless independently supported by tab data.

If any check fails, regenerate the affected contract item before updating the tab.

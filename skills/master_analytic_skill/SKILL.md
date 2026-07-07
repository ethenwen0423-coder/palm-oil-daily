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

1. Call `../contract_discovery_skill/SKILL.md` or read its saved current-month output from `data/contracts/current_contracts.json`.
2. Use the discovered main and secondary contracts as the analysis entrance; do not hard-code contract months.
3. Collect market data for every discovered contract.
4. Read the latest 5 `daily_review_skill` learning notes if available.
5. Call `../technical_basic_analysis_skill/SKILL.md`.
6. Score each contract using `技术面25% + 基本面25% + 驱动30% + 资金20%`.
7. Calculate observation levels and invalidation conditions.
8. Generate or update the tab data payload.
9. Check that every visible tab conclusion can be traced to scored data.
10. Generate `watchlist_options` from the discovered contract payload so the static GitHub Pages UI can refresh a user-selected contract card without a backend call.

Callable entrypoint:

- `scripts/analyze_contracts.py`

This master entrypoint accepts one contract payload or a list of contract payloads as JSON, calls `technical_basic_analysis_skill`, and applies the quality gate before returning tab-ready analysis fields.

If a required sub-skill or data source is missing, keep the interface and mark the missing item as `需进一步核验`; do not fabricate data.

Contract discovery entrypoint:

- `../contract_discovery_skill/scripts/select_contracts.py`

This monthly discovery script saves the current contract universe for the tab and report analysis entrance. All discovered contracts must enter the analysis pool. Rank 1 contracts are primary; rank 2 contracts are rollover, money-migration, spread, and liquidity references.

## Scope

Default discovered domestic products:

- `P`: DCE palm oil contracts selected by liquidity
- `Y`: DCE soybean oil contracts selected by liquidity
- `OI`: CZCE rapeseed oil contracts selected by liquidity
- `M`: DCE soybean meal contracts selected by liquidity
- `RM`: CZCE rapeseed meal contracts selected by liquidity
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
- technical score from price position, trend structure, support/resistance, and volatility range
- driver score from FCPO, CBOT soybean oil, crude oil, soybean complex, weather, shipping/export, and same-day policy/news
- money-flow score from change percent, volume change, open-interest change, sector ranking, P/Y/OI relative strength, and spread changes
- combined score with `technical * 0.25 + fundamental * 0.25 + driver * 0.30 + money_flow * 0.20`
- observation-level and invalidation calculation

Not responsible for:

- writing daily reports
- generating report headlines
- changing website layout
- fabricating unavailable data

## Required Tab Data Output

For each contract, return a structured item:

```json
{
  "symbol": "P2609",
  "product": "P",
  "name": "棕榈油",
  "market": "DCE",
  "contract": "P2609",
  "contract_rank": 1,
  "contract_label": "主力",
  "price": "需进一步核验",
  "change": "需进一步核验",
  "volume": "需进一步核验",
  "open_interest": "需进一步核验",
  "direction": "→",
  "score": {
    "total": 0,
    "technical": 0,
    "fundamental": 0,
    "driver": 0,
    "money_flow": 0,
    "stance": "中性",
    "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
    "view_confidence": "中",
    "contradiction_warning": "需进一步核验"
  },
  "view_confidence": "中",
  "contradiction_warning": "需进一步核验",
  "view": "需进一步核验",
  "technical_detail": [],
  "fundamental_detail": [],
  "strategy_recommendation": {
    "entry": "需进一步核验",
    "take_profit": "上方观察位需进一步核验",
    "stop_loss": "下方观察位需进一步核验",
    "upper_watch": "需进一步核验",
    "lower_watch": "需进一步核验",
    "invalidation": "需进一步核验",
    "basis": "需进一步核验"
  },
  "note": "需进一步核验"
}
```

For the page-level payload, also return a contract selector list:

```json
  "watchlist_options": [
    {
      "value": "P2609",
      "label": "P2609",
      "display": "棕榈油 P2609 主力",
      "name": "棕榈油",
      "contract": "P2609",
      "contract_label": "主力"
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
- `震荡偏强`
- `震荡偏弱`
- `分歧震荡`
- `观望`

## Quality Gate

Before finishing, verify:

- `technical_basic_analysis_skill` was called or explicitly marked unavailable.
- `contract_discovery_skill` current-month list was used or explicitly marked unavailable.
- Domestic contract months are not hard-coded in the tab generation script.
- Every contract has `score.fundamental`, `score.technical`, `score.driver`, `score.money_flow`, and `score.total`.
- `score.total = technical * 0.25 + fundamental * 0.25 + driver * 0.30 + money_flow * 0.20`.
- Every contract has `view_confidence` and `contradiction_warning`.
- `strategy_recommendation` gives observation levels and invalidation conditions, not direct trading instructions.
- Missing data is shown as `需进一步核验`.
- The tab output does not mention daily-report conclusions unless independently supported by tab data.
- If recent `daily_review_skill` notes show the same error type 3 or more times, the view must warn that the model recently tends to underestimate or overestimate that factor.

If any check fails, regenerate the affected contract item before updating the tab.

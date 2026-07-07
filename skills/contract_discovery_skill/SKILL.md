---
name: contract-discovery-skill
description: Monthly contract discovery skill for oil and meal futures. Use when Codex needs to discover which P, Y, OI, M, and RM contracts should be analyzed this month based on live liquidity ranking by volume, open interest, and turnover, then save the current monthly contract list for daily reports and the oil-futures tab without doing analysis or scoring.
---

# Skill: contract_discovery_skill

## Purpose

`contract_discovery_skill` is the analysis-entry contract discovery layer.

It only answers:

- which contracts should be analyzed this month
- which contract is main and which contracts are secondary
- which saved list daily reports and the oil-futures tab should read

It does not perform:

- technical analysis
- fundamental analysis
- combined scoring
- report writing
- website rendering
- trading advice

## Schedule

Run once per month at `00:00` on the 1st day of the month.

Callable script:

- `scripts/select_contracts.py`

Default command:

```bash
python3 skills/contract_discovery_skill/scripts/select_contracts.py
```

The script may be run manually at any time to refresh the current month list.

## Products

Default supported products:

- `P`: 棕榈油
- `Y`: 豆油
- `OI`: 菜油
- `M`: 豆粕
- `RM`: 菜粕

Default limit is the top 2 liquid contracts per product unless overridden by configuration.

Optional configuration path:

- `config/contract_discovery.json`

Example:

```json
{
  "P": {"name": "棕榈油", "query": "棕榈", "limit": 2},
  "Y": {"name": "豆油", "query": "豆油", "limit": 2},
  "OI": {"name": "菜油", "query": "菜油", "limit": 2},
  "M": {"name": "豆粕", "query": "豆粕", "limit": 2},
  "RM": {"name": "菜粕", "query": "菜粕", "limit": 2}
}
```

## Ranking Rules

Every run must fetch live contract quotes and rank contracts by:

1. `volume` descending
2. `open_interest` descending
3. `turnover` descending when available
4. contract month ascending as the final fallback

Do not hard-code contract months such as `P2609`, `Y2609`, or `OI2609`.

## Filtering Rules

For each product:

- symbol must match the product prefix plus a 4-digit contract month
- volume must exist and be greater than 0
- open interest must exist and be greater than 0
- expired months must be excluded
- continuous synthetic contracts such as `P0`, `Y0`, `OI0`, `M0`, `RM0` must be excluded
- missing fields should skip that contract and add a warning

## Saved Output

The script writes:

- `data/contracts/current_contracts.json`
- `data/contracts/YYYY-MM.json`

After saving the current month, it deletes other monthly list files matching `YYYY-MM.json`.

It must not write databases, caches, or daily historical files.

## Output Shape

```json
{
  "month": "2026-07",
  "generated_at": "2026-07-01 00:00:00",
  "source": "akshare:futures_zh_realtime",
  "products": {
    "P": [
      {
        "symbol": "P2609",
        "product": "P",
        "product_name": "棕榈油",
        "rank": 1,
        "label": "主力",
        "volume": 173800,
        "open_interest": 530800,
        "turnover": null,
        "data_time": "2026-07-01 00:00:00",
        "source": "akshare:futures_zh_realtime",
        "warnings": []
      }
    ]
  },
  "warnings": []
}
```

## Downstream Use

Daily reports and the oil-futures tab must read every contract returned in `data/contracts/current_contracts.json`.

Main contracts are used for primary views.

Secondary contracts are used only for:

- rollover observation
- money migration observation
- calendar-spread strength
- liquidity reference

Secondary contracts must not replace the main-contract narrative unless the next monthly discovery ranks them first.

Downstream analysis entrances must not drop rank 2 contracts. They should include them in the analysis pool and label them as rollover, money-migration, spread-strength, or liquidity-reference contracts.

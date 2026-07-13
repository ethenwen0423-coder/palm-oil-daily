---
name: data-quality-gate-skill
description: Deterministic data quality gate for palm-oil reports and oil-futures tab data. Use before publishing reports or tab data to validate latest price, previous close/settlement, price change, percentage change, contract month, unit, date, timezone, source conflicts across AkShare/MiaoXiang/WenCai, FCPO change basis, and inventory/export/production statistic dates; critical failures must stop formal publishing.
---

# Skill: data_quality_gate_skill

## Purpose

`data_quality_gate_skill` is the deterministic data quality gate.

It only validates data facts and source consistency.

It does not:

- write report body
- generate headlines
- decide market direction
- score contracts
- create trading advice

## When To Use

Run this skill before:

- publishing a daily or weekly report
- refreshing `data/oil_futures.js`
- using market data as a formal report fact

Callable script:

```bash
python3 skills/data_quality_gate_skill/scripts/validate_data.py --oil-futures data/oil_futures.js --strict
```

For a source-run manifest:

```bash
python3 skills/data_quality_gate_skill/scripts/validate_data.py --manifest source_runs/YYYY-MM-DD-daily/manifest.json --strict
```

## Deterministic Checks

### Futures Price Checks

Validate:

- latest price exists and is numeric
- previous close or previous settlement exists when percentage change is shown
- `change_pct ~= (latest - previous) / previous * 100`
- contract month is valid and not expired
- unit is explicit when a field is not a plain futures price
- date and timezone are explicit enough for publication

If source conflict exceeds tolerance, downgrade affected fields to `需进一步核验` or block publication when the field is critical.

### Source Comparison

Compare when available:

- AkShare
- 东方财富妙想
- 同花顺问财
- exchange or official source

Default tolerances:

- latest price: `2.0`
- percentage change: `0.25` percentage points

If AkShare and WenCai/MiaoXiang disagree beyond tolerance, the data cannot be written as a confirmed fact.

### FCPO Rule

FCPO change must explicitly state the comparison basis:

- relative to previous close
- relative to opening price
- relative to settlement

If the basis is unclear, mark FCPO movement as `需进一步核验`.

### Fundamental Statistic Dates

Inventory, export, and production data must include:

- statistic date
- update date or publication time
- source
- unit

Weekly or monthly data may be used as background only unless a fresh update is confirmed.

## Critical Failure Policy

Stop formal publishing when any of these fail:

- P/Y/OI/M/RM selected contracts cannot be validated
- latest price is missing for rank 1 domestic contracts
- date or contract month is invalid
- percentage change conflicts with latest price and previous close beyond tolerance
- source conflict exceeds tolerance for a critical field
- source-run manifest is missing or all market-data commands failed

When publishing is blocked, output JSON with:

```json
{
  "status": "blocked",
  "can_publish": false,
  "critical_errors": [],
  "warnings": [],
  "downgraded_fields": []
}
```

## Output Contract

The script must output JSON:

```json
{
  "status": "ok",
  "can_publish": true,
  "critical_errors": [],
  "warnings": [],
  "downgraded_fields": [],
  "checked_at": "Asia/Shanghai timestamp"
}
```

Use `--strict` in automation. Non-strict mode is allowed only for diagnostics.

---
name: forecast-tracking-skill
description: Define and validate structured daily P/Y/OI main-contract forecast records before they are evaluated. Use when a process needs to create or check data/forecast/daily/YYYY-MM-DD.json without generating forecasts, reading market data, or changing report automation.
---

# Skill: forecast_tracking_skill

## Purpose

This skill establishes the fixed, machine-readable lifecycle for daily oil-futures forecasts. It freezes an existing structured morning view, evaluates it against the same contract's after-close snapshot, and builds version-isolated internal metrics. It does not generate a market view, update a score, write a report, or change publishing content.

Daily files are stored at:

`data/forecast/daily/YYYY-MM-DD.json`

Each file contains exactly three initial forecast records: one each for `P`, `Y`, and `OI`.

## Main-Contract Rule

Identify a main contract only when both conditions hold:

```text
product in {"P", "Y", "OI"} and contract_rank == 1
```

Never identify a main contract by hard-coding a complete contract symbol such as `P2609`. The delivery month can change; `product` and `contract_rank` are the stable identifiers.

Rank-2 records are not permitted in a daily forecast file. A missing P, Y, or OI rank-1 record also makes the file invalid.

## Schema: forecast-schema-v1

The top-level object must contain:

- `schema_version`: exactly `forecast-schema-v1`
- `report_date`: a valid `YYYY-MM-DD` calendar date
- `timezone`: exactly `Asia/Shanghai`
- `records`: exactly three records, for P, Y, and OI respectively

Each record must contain these fields:

- identity: `forecast_id`, `report_date`, `product`, `contract`, `contract_rank`
- timing: `generated_at`, `cutoff_at`, `horizon`
- view: `stance`, `probabilities`, `expected_range`, `invalidation`, `confidence`, `source_confidence`
- provenance: `source_score`, `probability_mapping_version`, `outcome_rule_version`
- lifecycle: `calibration_status`, `evaluation_status`

`forecast_id` must be unique within its daily file. The recommended deterministic form is:

```text
YYYY-MM-DD-{product}{contract_month}-oil-forecast-v1
```

For example: `2026-07-13-P2609-oil-forecast-v1`.

## Validation Rules

- Contract symbols must be uppercase P/Y/OI symbols with a four-digit year-month suffix, and the suffix month must be 01 through 12.
- The record `product` must equal the contract prefix.
- All probabilities must be finite numeric values from 0 through 1; `up + range + down` must equal 1 within `0.000001`.
- `expected_range.lower` and `expected_range.upper` must be finite numbers with `lower < upper`.
- `generated_at` and `cutoff_at` must be ISO-8601 timestamps carrying a `+08:00` offset. `generated_at` cannot be later than five minutes after `cutoff_at`.
- `confidence` is required and must be `high`, `medium`, `low`, or `unknown`; it is the only confidence field used by metrics. `source_confidence` preserves the original `score.view_confidence` string, or is `null` when unavailable.
- `probability_mapping_version` versions the score-to-probability mapping. `outcome_rule_version` versions the closing-result classification rule; new records must use `outcome-v1-fixed-0.30pct`. These version fields are independent and metrics isolate every combination.
- `evaluation_status` uses the known lifecycle values `pending`, `evaluated`, or `invalidated`. A newly created daily forecast file may use only `pending`; generic schema validation continues to accept known later lifecycle states for the future evaluator.

Run the validator before retaining a forecast record:

```bash
python3 skills/forecast_tracking_skill/scripts/validate_forecast.py \
  --forecast data/forecast/daily/YYYY-MM-DD.json
```

It prints machine-readable JSON. A validation failure returns a non-zero exit code. A successful initial file has `status: "ok"` and `can_evaluate: true`; that only means the record is structurally ready for a future evaluator, not that an evaluation has occurred.

## score-map-v1 Probability Mapping

`record_forecast.py` freezes predictions from `window.OIL_FUTURES_CONTRACTS` only. It selects exactly one rank-1 record for each P, Y, and OI, then reads its five score components, stance, view confidence, contradiction warning, two watch levels, and invalidation text. It does not read Markdown reports, review records, actual snapshots, or later market data.

It persists both `source_confidence` and normalized `confidence`:

- `高` / `high` -> `high`
- `中` / `medium` -> `medium`
- `低` / `low` -> `low`
- any other value or missing -> `unknown`

The pure implementation is `score_map_v1()` in `scripts/forecast_schema.py`.

```text
score_edge = clamp((total - 50) / 25, -1, 1)
strength = abs(score_edge)
confidence_factor = 高: 0.90, 中: 0.70, 低: 0.45, otherwise: 0.40
conflict_penalty = 0.15 when contradiction_warning is non-empty and not “暂无明显冲突信号”; otherwise 0
directional_mass = clamp(0.20 + 0.55 * strength * confidence_factor - conflict_penalty, 0.20, 0.70)
```

- `偏多` and `震荡偏强`: allocate directional mass to `up` using `directional_mass * (0.5 + 0.5 * strength)`; the remaining mass is `down`.
- `偏空` and `震荡偏弱`: use the same allocation for `down`; the remaining mass is `up`.
- `震荡`, `分歧震荡`, and `观望`: `range = max(0.55, 1 - directional_mass)`, with the remainder split equally between `up` and `down`.

The first two probabilities are rounded to six decimals; `down` is then set to `1 - up - range`, preserving a strict total of one.

## Freezing a Forecast

```bash
python3 skills/forecast_tracking_skill/scripts/record_forecast.py \
  --oil-futures /path/to/oil_futures.js \
  --forecast /path/to/YYYY-MM-DD.json \
  --report-date YYYY-MM-DD \
  --generated-at "2026-07-13T08:20:00+08:00" \
  --cutoff-at "2026-07-13T08:15:00+08:00" \
  --quality-gate-status ok
```

The quality gate must be `ok`. The target is created only after a temporary file passes `validate_forecast.py`, then atomically replaced into place. An identical pending record returns `already_exists: true`; a changed or evaluated record is never overwritten.

## After-Close Evaluation and Metrics

The only production entry for the after-close lifecycle is:

```bash
python3 scripts/review_prediction.py --date YYYY-MM-DD
```

For a China-futures trading day it runs, in order:

1. require `data/forecast/daily/YYYY-MM-DD.json`;
2. create and strictly validate `data/review/runtime_snapshots/YYYY-MM-DD-actual-oil_futures.js` without publishing it;
3. run the legacy `daily_review_skill`;
4. evaluate the frozen forecast into `data/forecast/evaluated/YYYY-MM-DD.json`;
5. build `data/forecast/metrics/latest.json`, `20d.json`, and `60d.json` with `--as-of YYYY-MM-DD`.

The actual snapshot is accepted only when each P/Y/OI rank-1 record has a matching `trade_date` and numeric close, previous close, high, and low. Structured evaluation still matches by exact `product + contract`, never by current rank alone. Evaluation failure blocks metrics; metrics failure retains the already validated evaluated file. Identical evaluated output is idempotent and is not overwritten. After metrics succeed, the entry runs `prune_forecast_artifacts.py --apply`; cleanup failures are warnings and do not downgrade a successful evaluation.

## Minimal Persistence and Retention

Only evaluated forecasts, the fixed latest/20d/60d metrics files, the latest 30 valid daily reviews, and `data/review/latest_review.json` are long-term persistence candidates. Retain at most 65 valid evaluated trade-day files and 30 valid daily-review trade-day files. Metrics never receive dated historical copies.

Frozen forecasts remain local and Git-ignored. A frozen file may be removed only when a matching valid evaluated file exists and its business date is more than five days old. Runtime previous/actual snapshots live under Git-ignored `data/review/runtime_snapshots/` and retain only seven calendar days. Existing files under `data/review/snapshots/` are not migrated or deleted.

Use `prune_forecast_artifacts.py --dry-run` to inspect a deletion plan. Only explicit `--apply` deletes direct children of the four allowed artifact directories; invalid JSON, missing business dates, and unrecognized filenames remain untouched with warnings.

## Scheduling Candidate (Not Installed)

`scripts/install_prediction_review_launchd.sh` defines a weekday 15:20 Asia/Shanghai close-review run and a 15:40 retry check. Always run `--dry-run` first. The retry validates both the day's evaluated forecast and `metrics/latest.json` before deciding whether to invoke the review again. Runtime date selection uses Python `ZoneInfo("Asia/Shanghai")`; `review_prediction.py` remains responsible for the trading-day check.

The installer blocks a dirty worktree and requires explicit confirmation that evaluated forecasts, rolling metrics, and daily review files have an approved persistence/publishing policy. Runtime snapshots and frozen forecasts are explicitly excluded from Git persistence. After `review_prediction.py` succeeds, the generated runner invokes `publish_prediction_review.sh --publish --confirm-persistence-reviewed` so only allowlisted review data is committed and pushed. At 15:40, already-valid evaluation and metrics skip market fetching but still retry a previously failed allowlisted publish. Creating the script or running its dry-run does not mean the LaunchAgent is installed or enabled.

## Boundaries

Do not use this skill to invent predictions, influence scoring or report prose, read future data, or rewrite frozen forecasts. Morning freezing is a pre-publish audit layer; after-close evaluation and metrics are invoked only by `scripts/review_prediction.py`. Do not install or modify scheduling from this skill.

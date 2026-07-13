---
name: daily-review-skill
description: Daily review and self-improvement skill for oil-futures main-contract analytics. Use only after market close when Codex needs to compare the frozen morning P/Y/OI views with same-day actual market action, classify HIT/PARTIAL/MISS, attribute errors, write learning notes, and produce improvement suggestions without automatically changing scoring weights or rules.
---

# Skill: daily_review_skill

## Purpose

Use this skill to review whether yesterday's oil-futures main-contract analysis was validated by today's market action.

Covered contracts:

- P
- Y
- OI

Identify each reviewed main contract by `product` plus `contract_rank == 1`.
Never match the product code against `symbol`, because symbols contain the delivery month (for example `P2609`).

This skill does not write morning reports, does not generate titles, and does not permanently change scoring weights.

Production execution is owned exclusively by `scripts/review_prediction.py`. Morning report publishing, oil-futures tab refreshes, and intraday refreshes must not invoke this skill. The night review entry first archives the morning tab, then generates and strictly validates the same-date actual snapshot before calling `daily_review.py`.

## Fixed Workflow

1. Read yesterday's report or tab analysis output.
2. Extract yesterday's view fields:
   - `view`
   - `score.stance`
   - `score.total`
   - `score.technical`
   - `score.fundamental`
   - `score.driver`
   - `score.money_flow`
   - `view_confidence`
   - `contradiction_warning`
   - upper watch level
   - lower watch level
   - invalidation condition
3. Read today's actual market data:
   - open
   - high
   - low
   - close
   - change_pct
   - volume_change
   - open_interest_change
   - intraday_direction
   - whether_break_upper
   - whether_break_lower
4. Classify each contract as `HIT`, `PARTIAL`, or `MISS`.
5. If `MISS`, attribute the error.
6. Write `data/review/daily/YYYY-MM-DD.json`.
7. Output review result and improvement suggestions.

If any P/Y/OI rank-1 contract is missing, write `status: REVIEW_FAILED`, return a non-zero exit code, and prohibit downstream reports from claiming there were no repeated errors.

## Hit Rules

For bullish views (`偏多`, `震荡偏强`):

- `HIT`: today closes higher and does not break the lower watch level.
- `PARTIAL`: today rallies then fades but remains inside the watch range.
- `MISS`: today closes lower and breaks the lower watch level.

For bearish views (`偏空`, `震荡偏弱`):

- `HIT`: today closes lower and does not break the upper watch level.
- `PARTIAL`: today rebounds but does not break the upper watch level.
- `MISS`: today closes higher and breaks the upper watch level.

For range views (`震荡`, `分歧震荡`, `观望`):

- `HIT`: today's high and low remain inside the watch range.
- `PARTIAL`: price briefly breaks the range but closes back inside.
- `MISS`: price breaks the range one-way and closes outside.

## Error Attribution

When the result is `MISS`, choose one or more error types:

- 技术面权重过高
- 基本面信息滞后
- 外盘驱动遗漏
- 原油影响低估
- FCPO影响低估
- CBOT影响低估
- 资金行为低估
- 持仓变化低估
- 板块轮动识别不足
- 库存旧数据被误用为今日驱动
- 政策旧消息被误用为今日驱动
- 支撑压力位设置不合理
- 波动率低估
- 置信度过高
- 信号冲突未降级为震荡

## Required Output

Always include:

- `review_result`
- `error_type`
- `suggested_improvement`
- `whether_update_rule`
- `human_approval_required`

## Rolling 30-Day Review Memory

Daily detail JSON must be stored at:

`data/review/daily/YYYY-MM-DD.json`

Use `scripts/review_memory.py`:

- `load_recent_reviews(days=30)`: read only recent daily review files from `data/review/daily/`.
- `save_today_review(review)`: save or overwrite today's review and call pruning.
- `prune_old_reviews(days=30)`: keep only the most recent 30 valid daily review files.

Do not load daily detail older than 30 days.

Do not delete weekly or monthly summaries. Do not delete `data/review/summary/`. Do not delete market raw data or report archives.

Each daily review payload must include learning items with:

- `date`
- `contract`
- `previous_view`
- `actual_result`
- `hit_status`
- `error_type`
- `root_cause`
- `suggested_rule_change`
- `confidence_adjustment`
- `requires_human_approval`

## Self-Improvement Boundary

AI must not permanently change scoring weights or production rules.

AI may only generate improvement suggestions.

Only when the same error type appears more than 3 consecutive times may the output say:

`建议将该规则加入候选参数调整池。`

Human approval is still required.

## Script

Use `scripts/daily_review.py` for deterministic review:

```bash
python3 skills/daily_review_skill/scripts/daily_review.py \
  --previous data/oil_futures_yesterday.js \
  --current data/oil_futures.js \
  --date YYYY-MM-DD
```

Use `scripts/review_memory.py` when generating morning reports to load only recent memory:

```python
from review_memory import load_recent_reviews
recent = load_recent_reviews(days=30)
```

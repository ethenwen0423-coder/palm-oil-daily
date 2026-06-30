---
name: title-quality-gate
description: Quality gate for financial research titles. Use after generating or editing any Headline and Subheadline for market comments, palm-oil reports, A-share morning briefings, industry notes, client pushes, PPT copy, website articles, GitHub Pages content, or Markdown research reports. Check whether the Headline states the core market view, whether the Subheadline explains the core logic, and whether trading instructions are kept out of both and reserved for the Trading Plan. Regenerate titles automatically when the roles are mixed, the wording sounds like a chat message or WeChat pre-market tip, or the title contains specific trading actions such as stop-loss, chasing highs, adding, reducing, support buying, or exact execution prices.
---

# Title Quality Gate

## Purpose

Use this skill after creating a `Headline` and `Subheadline` for financial research content.

The gate enforces three separate responsibilities:

| Field | Responsibility | Must Not Do |
| --- | --- | --- |
| Headline | Express the market view | Give trading actions |
| Subheadline | Explain the core logic behind the view | Tell the reader how to trade |
| Trading Plan | Express execution actions | Replace the market view |

If the Headline or Subheadline fails any check, rewrite it before delivery.

## Required Checks

Run these checks in order.

1. Check whether the Headline summarizes the market's core view, not the trade action.
2. Check whether the Headline can stand alone as a research report title, not a chat message.
3. Check whether the Headline sounds closer to Bloomberg, Reuters, or a top domestic futures research institute than to a WeChat pre-market alert.
4. Check whether the Headline includes concrete prices, stop-loss, chasing highs, support buying, adding, reducing, taking profit, or other execution instructions. If yes, rewrite it.
5. Check whether the Subheadline explains the core logic behind the view, not how the user should trade. If it is a trading suggestion, rewrite it.
6. Check whether the Headline can be read without the body and still communicate the day's core market change. If not, rewrite it.

## Pass Criteria

A title set passes only when all criteria are true:

- The Headline states a market view in one concise sentence.
- The Headline can serve as an institutional research title.
- The Headline avoids exact execution language.
- The Subheadline explains the main driver, contradiction, expectation, or data logic.
- The Subheadline does not include trading instructions.
- The Trading Plan, if present, is the only place that contains trade actions.

## Rewrite Rules

When rewriting, preserve the underlying market judgment but move each element to the correct field:

- Move direction and market interpretation into `Headline`.
- Move cause, data, policy, inventory, demand, supply, capital flow, or expectation logic into `Subheadline`.
- Move prices, stop-loss, position changes, chasing highs, dip buying, adding, reducing, and invalidation execution into `Trading Plan`.

Do not weaken the view with excessive `可能、或将、预计`. Use condition-based wording when uncertainty matters.

## Forbidden Headline Content

Regenerate the Headline if it contains:

- Specific entry price
- Stop-loss price
- Take-profit price
- 加仓
- 减仓
- 止损
- 止盈
- 追高
- 低吸
- 承接
- 回踩买入
- 突破买入
- 逢低做多
- 逢高做空
- 仓位建议

These belong in the Trading Plan.

## Examples

### Example 1

Failing Headline: `棕榈油回踩支撑位可继续加仓`

Problem: The Headline gives an execution action.

Passing Headline: `库存去化支撑棕榈油偏强震荡`

Passing Subheadline: `马棕供应压力低于预期，印尼生柴预期继续抬高需求定价。`

Trading Plan: `回调不破支撑位时维持偏多思路，跌破支撑位后降低多头仓位。`

### Example 2

Failing Headline: `今天别追高，等回踩再看`

Problem: The Headline sounds like a chat message and does not state the market view.

Passing Headline: `油脂板块强势延续但追涨性价比下降`

Passing Subheadline: `资金仍在交易库存去化，但短线涨幅扩大后波动风险上升。`

### Example 3

Failing Subheadline: `压力位附近减仓，跌破支撑位止损。`

Problem: The Subheadline is a trading plan.

Passing Subheadline: `价格上行已部分兑现库存利多，压力位附近分歧会增加。`

Trading Plan: `压力位附近不追多，跌破支撑位后多头逻辑转弱。`

## Output Behavior

When asked to check titles, return one of two outcomes:

1. `通过` with the unchanged Headline and Subheadline.
2. `需重写` with the failed checks and a corrected Headline/Subheadline.

If a Trading Plan is included, verify that all execution language appears only there.

Keep the final title set concise. Do not explain the entire article unless the user asks for a full rewrite.

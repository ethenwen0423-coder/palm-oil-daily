---
name: title-generation
description: Generate financial research titles and summaries only. Use when Codex needs to create Headline, Subheadline, Report Title, or One Sentence Summary for palm-oil reports, A-share morning briefings, market comments, industry notes, client pushes, PPT copy, website articles, GitHub Pages content, or Markdown research reports. This skill extracts the market mainline, summarizes the key change, and writes institutional-style titles; it does not inspect, validate, approve, reject, or quality-gate titles.
---

# Title Generation

## Purpose

Use this skill to generate:

- `Headline`
- `Subheadline`
- `Report Title`
- `One Sentence Summary`

This skill only generates titles and summaries. Do not use it to check whether a title passes quality standards. After generation, call `../title-quality-gate/SKILL.md`.

## Role Definitions

| Field | Role |
| --- | --- |
| Headline | Express the market view or market state. |
| Subheadline | Explain the core logic behind the view. |
| Report Title | Name the full report in a formal research-document style. |
| One Sentence Summary | State the conclusion in one complete sentence. |

Trading instructions belong in `Trading Plan`, not in any title field.

## Generation Flow

Before writing any title, identify the market mainline:

1. What is the market really trading today?
2. What is the biggest change versus yesterday?
3. Does yesterday's mainline still hold?
4. Is the market trading expectation or realized fundamentals?
5. Which variable best explains the move: policy, inventory, capital style, external market, sentiment, supply, demand, or valuation?

Then generate the title set:

1. Write the `Headline` around the market mainline.
2. Write the `Subheadline` around the core logic.
3. Write the `Report Title` in formal report style.
4. Write the `One Sentence Summary` as a concise full-sentence conclusion.

## Headline Rules

The goal of a Headline is not to be different every day. The goal is to express the most important market mainline accurately.

If the market mainline has not changed, allow the Headline theme to remain similar to yesterday. Do not force different wording just to avoid repetition.

Update the Headline only when a new driver appears, such as:

- Policy change
- Inventory change
- Capital style shift
- External-market mainline change
- Clear sentiment shift
- Supply or demand reassessment

Prefer market-state language:

- `库存去化支撑棕榈油偏强震荡`
- `B50预期仍是棕榈油交易主线`
- `生柴预期强化棕榈油需求定价`

Avoid execution language in generated titles:

- Specific price
- Stop-loss
- Chasing highs
- Support buying
- Adding or reducing positions
- Trading plan

## Subheadline Rules

Use the Subheadline to explain the core logic behind the Headline.

Good Subheadline content includes:

- Which data changed
- Why the change matters
- Whether the market trades expectation or reality
- Which contradiction drives pricing
- Why today's mainline continues or changes

Do not put execution instructions in the Subheadline.

## Report Title Rules

Use formal research-document style. The Report Title can be slightly broader than the Headline, but it must still carry the conclusion.

Examples:

- `棕榈油日报：库存去化延续，价格维持偏强震荡`
- `A股晨报：主线偏轮动，资金继续寻找政策与业绩共振`
- `油脂周报：生柴预期抬升远月需求定价`

## One Sentence Summary Rules

Write one complete sentence that gives the conclusion and the reason.

Examples:

- `棕榈油短线维持偏强震荡，核心支撑来自马棕库存压力下降和印尼生柴预期。`
- `A股仍是结构性轮动行情，资金更偏好政策催化与业绩确定性共振方向。`

## Output Format

Return the title set in this format:

```markdown
Headline:

Subheadline:

Report Title:

One Sentence Summary:
```

After producing this output, call `../title-quality-gate/SKILL.md` to inspect it.

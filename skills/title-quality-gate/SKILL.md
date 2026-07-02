---
name: title-quality-gate
description: Quality gate for financial research titles only. Use after title-generation creates or revises Headline, Subheadline, Report Title, or One Sentence Summary for market comments, palm-oil reports, A-share morning briefings, industry notes, client pushes, PPT copy, website articles, GitHub Pages content, or Markdown research reports. This skill checks whether titles express the market mainline, read like institutional research, avoid trade actions and prices, and separate Headline, Subheadline, and Trading Plan responsibilities. It does not generate titles; if a title fails, require regeneration by title-generation.
---

# Title Quality Gate

## Purpose

Use this skill only to check titles after `../title-generation/SKILL.md` generates them.

Do not generate replacement titles in this skill. If the title set fails, return the failed checks and instruct the caller to regenerate with `title-generation`.

## Responsibility Boundary

| Skill | Responsibility |
| --- | --- |
| `title-generation` | Generate `Headline`, `Subheadline`, `Report Title`, and `One Sentence Summary`. |
| `title-quality-gate` | Check whether the generated title set passes quality standards. |

The required loop is:

1. Call `title-generation`.
2. Call `title-quality-gate`.
3. If the gate fails, return to `title-generation`.
4. Repeat until the gate passes.

## Field Responsibilities

| Field | Must Do | Must Not Do |
| --- | --- | --- |
| Headline | Express the market mainline or core market view. | Give trading actions. |
| Subheadline | Explain the core logic behind the view. | Tell the reader how to trade. |
| Report Title | Name the full report in institutional research style. | Sound like a chat message. |
| One Sentence Summary | State the conclusion and reason in one sentence. | Add new unsupported claims. |
| Trading Plan | Express execution actions. | Replace the market view. |

## Required Checks

Run these checks in order.

1. Does the Headline express today's market mainline?
2. Does the Headline summarize the market's core view rather than a trade action?
3. Can the Headline stand alone as a research report title?
4. Does the Headline sound closer to Bloomberg, Reuters, or a top domestic futures research institute than to a WeChat pre-market alert?
5. Does the Headline avoid concrete prices, stop-loss, chasing highs, support buying, adding, reducing, taking profit, and other execution instructions?
6. Does the Subheadline explain the core logic behind the view rather than tell the user how to trade?
7. Can the Headline be read without the body and still communicate the day's core market change?
8. Does the Headline avoid novelty for novelty's sake when yesterday's mainline still holds?
9. Is the Report Title formal enough for a research document?
10. Is the One Sentence Summary easy to understand and consistent with the title set?

## Forbidden Headline Content

Fail the title set if the Headline contains:

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
- 交易计划

These belong in the Trading Plan.

## Pass Criteria

A title set passes only when:

- Headline expresses the market mainline.
- Headline reads like a research title.
- Headline contains no trade action or exact execution price.
- Subheadline explains the core logic.
- Report Title is formal and conclusion-led.
- One Sentence Summary is concise, clear, and consistent.
- Trading actions appear only in Trading Plan.

## Output Behavior

Return exactly one of two outcomes:

```markdown
通过

Reason:
- ...
```

or:

```markdown
需重写

Failed Checks:
- ...

Instruction:
Return to `title-generation` and regenerate the title set using the failed checks above.
```

Do not provide replacement titles from this skill.

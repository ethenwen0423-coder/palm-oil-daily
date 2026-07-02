# Title Quality Gate Examples

These examples show how to inspect a title set. Do not generate replacement titles inside this skill.

## 1. Trade Action In Headline

Input Headline: `棕榈油回踩支撑位可继续加仓`

Gate Result: `需重写`

Failed Checks:

- Headline contains trading action.
- Headline does not express only the market mainline.

Instruction:

- Return to `title-generation`.
- Move execution language into Trading Plan.

## 2. Chat Message Style

Input Headline: `今天别追高，等回踩再看`

Gate Result: `需重写`

Failed Checks:

- Headline sounds like a chat message.
- Headline contains execution language.
- Headline cannot stand alone as a research report title.

Instruction:

- Return to `title-generation`.
- Generate a research-style Headline around market state.

## 3. Trading Plan In Subheadline

Input Subheadline: `压力位附近减仓，跌破支撑位止损。`

Gate Result: `需重写`

Failed Checks:

- Subheadline tells the reader how to trade.
- Subheadline does not explain the core logic behind the view.

Instruction:

- Return to `title-generation`.
- Move trading actions into Trading Plan and rewrite Subheadline as logic.

## 4. Forced Novelty

Yesterday's Headline: `库存去化支撑棕榈油偏强震荡`

Input Headline: `油脂市场迎来全新交易窗口`

Gate Result: `需重写`

Failed Checks:

- Headline creates novelty without a new market driver.
- Headline does not accurately reflect that yesterday's mainline still holds.

Instruction:

- Return to `title-generation`.
- Use the unchanged market mainline instead of inventing a new theme.

## 5. Specific Price In Headline

Input Headline: `棕榈油站稳8200后继续看多`

Gate Result: `需重写`

Failed Checks:

- Headline contains a specific price.
- Headline contains a trading action.

Instruction:

- Return to `title-generation`.
- Remove price and execution language from the Headline.

## 6. Passing Title Set

Input:

```markdown
Headline:
库存去化支撑棕榈油偏强震荡

Subheadline:
马棕供应压力低于预期，印尼生柴预期继续抬高需求定价。

Report Title:
棕榈油日报：库存去化延续，价格维持偏强震荡

One Sentence Summary:
棕榈油短线维持偏强震荡，核心支撑来自马棕库存压力下降和印尼生柴预期。
```

Gate Result: `通过`

Reason:

- Headline expresses market mainline.
- Subheadline explains logic.
- Report Title is formal.
- One Sentence Summary is consistent.
- No trading action appears in the title fields.

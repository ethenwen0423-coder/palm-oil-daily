---
name: generate-oilseed-trade-signal
description: Generate deterministic Chinese trading instructions for a user-confirmed Chinese oilseed futures symbol using MA20 entry, RSI divergence exit, and asymmetric MA6 stop rules. Use when the user asks what to do now, whether to go long or short, whether to hold, or where take-profit and stop-loss conditions stand for a selected P, Y, OI, M, or RM main-continuous or delivery contract.
---

# Generate Oilseed Trade Signal

Use the bundled script as the sole strategy calculator. Do not substitute P0 data, infer a signal manually, or alter the strategy rules.

## Workflow

1. Show the user the exact symbol and product name. Obtain explicit confirmation when the selection is ambiguous or came from a list.
2. Determine the position state: `flat`, `long`, or `short`.
3. For a position, obtain the entry date when possible. Accept entry price and entry ATR if supplied.
4. Run the script with the confirmed symbol:

```bash
python3 scripts/generate_signal.py --symbol P2609 --position flat
python3 scripts/generate_signal.py --symbol Y2701 --position long --entry-date 2026-06-05
python3 scripts/generate_signal.py --symbol OI2609 --position short --entry-date 2026-07-01
python3 scripts/generate_signal.py --symbol P0 --position flat
```

Use `--blocked-direction long|short` when a prior stop locked that direction. Use `--allow-forming-bar` only when the user explicitly requests an intraday provisional reading; label it provisional.

5. Verify that output `symbol` exactly matches the confirmed symbol and `status` is `ok`. Otherwise issue no trade direction and report the data problem.
6. If a held long lacks enough entry data to evaluate ATR activation, state exactly what is missing and still report independently valid RSI-divergence exits.
7. Respect `execution_window`. Never convert an expired entry signal into a chase order. Handle an overdue exit at the next available market opportunity.

## Symbol rules

- Support `P`, `Y`, `OI`, `M`, and `RM` products.
- Treat codes ending in `0`, such as `P0` and `Y0`, as main-continuous series and fetch them with `ak.futures_main_sina`.
- Treat dated codes, such as `P2609`, `Y2701`, and `OI2609`, as delivery contracts and fetch them with `ak.futures_zh_daily_sina`.
- Normalize lowercase input to uppercase. Reject unsupported or malformed symbols instead of falling back to P0.
- Apply the mature backtest claim only to P0. Label other symbols as same-rule calculations, not independently validated models.

## Strategy invariants

- Enter long after a completed daily close crosses above MA20; enter short after it crosses below MA20.
- Execute a confirmed signal at the next trading day's open.
- For a long, arm the MA6 stop only after maximum favorable excursion reaches 0.75 entry ATR; exit after two consecutive completed closes below MA6.
- For a short, exit after one completed close above MA6.
- Take profit on a 20-day price/RSI divergence: bearish divergence exits a long; bullish divergence exits a short.
- After a stop, block the stopped direction until an opposite MA20 crossover occurs.
- Do not add RSI50, Bollinger squeeze, partial exits, leverage, or discretionary overrides.
- Treat output as a strategy signal, not guaranteed profit or personalized investment advice. Never place an order.

## Response format

Respond in Chinese with:

- `标的合约`
- `行情日期` and whether the bar is completed
- `当前指令`: 做多 / 做空 / 持有多单 / 持有空单 / 全部止盈 / 全部止损 / 观望 / 数据不足
- `执行时间`
- `依据`: close, MA20, MA6, ATR14, RSI14, crossover/divergence/stop state
- `止盈条件`, `止损状态`, and `再入场限制`
- `数据来源与风险提示`: exact AkShare endpoint and symbol, 0.04% one-way backtest cost, P0-only mature validation scope, and no guarantee of future performance

Keep the instruction decisive and distinguish confirmed instructions from provisional forming-bar observations.

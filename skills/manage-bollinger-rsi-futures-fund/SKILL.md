---
name: manage-bollinger-rsi-futures-fund
description: Manage a persistent CNY 1,000,000 virtual Chinese-futures fund from the user's Bollinger-RSI model, using real PYYMM main contracts, next-open execution, equity compounding, portfolio allocation, daily positions, trades, and performance reporting. Use for daily fund operation, model-signal order plans, virtual fills, position reconciliation, or fund P&L; do not use to place real broker orders.
---

# Manage Bollinger-RSI Futures Fund

Operate this as a persistent **virtual fund**, never as a broker order interface. The bundled ledger is the sole source of fund positions and fills. A model signal is not a fill.

## Authoritative model

Use the deployment-pinned source at `model/futures_main_contract_bollinger_rsi_model.py`. Require `MODEL_VERSION == palm-oil-v2-real-contract-indicators-carry5-main-contract` and call `prepare_contract_local_main`; never call the legacy gap-adjusted preparation for a live decision. If the source, version, or required data is unavailable, stop with `需进一步核验` instead of substituting another model. The production runtime state is selected explicitly with `--state-dir`; never write into the repository checkout.

The model rules remain unchanged: actual delivery-month contracts only; T uses T-1 liquidity to select the main contract; indicators use each PYYMM contract's own unadjusted history; completed close confirms; next trading-day open executes; one 1-ATR pyramid at most; model exits close all layers; roll state is inherited. Never use `P0`, `futures_main_sina`, continuous, weighted, synthetic, or adjusted series as trade, indicator, or P&L input.

## Persistent fund state

Use `scripts/fund_ledger.py` for every state change. Default state is `/Users/ethen/.codex/state/bollinger-rsi-futures-fund`; allow `--state-dir` when the user explicitly chooses another fund.

Before any daily work, run `status` and `verify`. Do not reconstruct positions from chat memory. Do not edit `state.json`, `trade_ledger.jsonl`, or `snapshots.jsonl` by hand.

Read [references/signal-schema.md](references/signal-schema.md) when preparing a signal snapshot. Read [references/allocation-policy.md](references/allocation-policy.md) when selecting or sizing simultaneous signals.

## Daily workflow

1. Load and verify the ledger. Report any unresolved pending order before creating another order for the same variety.
2. Refresh actual PYYMM daily bars and contract metadata. Report the source, latest completed market date, failed varieties, stale data, multiplier, margin ratio, and fee assumption. Exclude invalid or incomplete inputs; never invent a price, multiplier, margin, fee, volume, open interest, or contract.
3. Run the authoritative model separately for every supported liquid variety through the same completed date. No variety, including palm oil, has default priority or exclusive eligibility. Use the model's stateful output, not a fresh crossover alone. For simultaneous new entries, compute the cross-sector allocation score described in the allocation policy.
4. Write a snapshot matching the schema and run `plan`. Process model exits and required rolls before pyramids, then new entries. A plan is a pending virtual order for the next open, not a completed trade.
5. After the intended next open is observable, obtain the actual PYYMM open/fill price and run `fill`. If the intended open has passed without a trustworthy price, leave the order unresolved or cancel it with the reason; never backfill with a close, settlement, estimate, or continuous-contract price.
6. Mark every open position from actual held-contract close/settlement using `mark`, then run `report --format markdown`. Preserve the resulting daily snapshot.

Typical commands:

```bash
python3 scripts/fund_ledger.py status
python3 scripts/fund_ledger.py verify
python3 scripts/fund_ledger.py plan --signals /absolute/path/daily_signals.json
python3 scripts/fund_ledger.py fill --order-id ORDER_ID --date YYYY-MM-DD --price ACTUAL_PRICE
python3 scripts/fund_ledger.py mark --prices /absolute/path/actual_contract_closes.json
python3 scripts/fund_ledger.py report --format markdown
```

Use `roll` only after both old- and new-contract execution prices are observable. It records two fee-bearing fills and changes the held contract without treating the roll as a new strategy trade.

## Portfolio boundary

The objective is to seek the highest long-run risk-adjusted compound return across sectors, not to promise a return or mechanically maximize a fitted CAGR. Palm oil is only one candidate and must never be the hard-coded default allocation. Portfolio sizing is a separate overlay and must not be described as an improvement to the model signal. Preserve the defaults unless the user explicitly approves a separately backtested policy change: gross notional cap 2.0x equity, margin-use cap 60%, per-variety notional cap 25%, per-sector cap 40%, at most eight varieties, and at least one contract per accepted order.

Never create a fill that breaches the caps. If even one contract does not fit, output `因资金/风控未执行`. Never increase leverage merely because the latest backtest has a high annualized return.

## Required response

Respond in Chinese, conclusion first, with:

- fund date, data completeness, model version, and whether orders are planned or actually filled;
- today's opens, pyramids, exits, rolls, cancellations, and skipped signals, each with variety, PYYMM, side, lots, actual/planned price, reason, and fee;
- current holdings with entry layers, average price, last price, notional, margin, unrealized P&L, and portfolio weight;
- cash, used margin, available cash, realized P&L, unrealized P&L, total fees, equity, cumulative return, drawdown, and annualized/Sharpe only when the stored history is sufficient;
- pending next-open instructions and the exact data gaps marked `需进一步核验`;
- source facts separated from model decisions and the mandatory AI risk notice.

Do not claim that a pending order is a position, that a virtual fill is a real brokerage fill, or that historical performance predicts future returns.

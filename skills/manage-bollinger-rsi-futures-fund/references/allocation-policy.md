# Portfolio allocation policy

This overlay decides which simultaneous model signals the CNY 1,000,000 virtual fund can afford. It does not change the Bollinger-RSI signal rules.

## Candidate evidence

Re-estimate ranking evidence on a scheduled research cadence, not every day. Use real PYYMM contracts, T-1 liquidity selection, next-open execution, actual multipliers, the same fee assumptions, and walk-forward or held-out periods. Include 1-, 3-, and 5-year coverage where available, but mark incomplete windows `需进一步核验`.

Build `score` from held-out evidence only. A suitable monotonic score rewards positive multi-window CAGR and Sharpe, and penalizes maximum drawdown, turnover, instability across windows, sparse trades, stale data, and high cross-variety correlation. Store the components alongside the snapshot. Never select solely by the highest fitted CAGR, win rate, or most recent year.

## Default constraints

- Initial equity: CNY 1,000,000; all later sizing uses current equity.
- Maximum gross notional: 2.0 times equity, including pending entries.
- Maximum estimated margin use: 60% of equity.
- Maximum notional per variety: 25% of equity.
- Maximum notional per sector: 40% of equity.
- Maximum concurrent varieties: 8.
- One initial layer plus at most one model-authorized pyramid layer.
- Exits and required rolls take priority over additions and new entries.

For each accepted entry, the ledger sizes whole contracts using the smallest of the remaining gross, margin, variety, and sector capacities. Higher-scored signals are considered first. The reference price is only for capacity planning; the actual next-open fill determines booked price, fees, notional, and margin.

If contract-level margin schedules or fees differ from the snapshot, update them before filling. Limit-up/down, suspended, illiquid, stale, or non-executable contracts remain pending or are cancelled with a reason.

## Governance

Changes to leverage, score weights, caps, eligible universe, or fee assumptions are research variants. Compare them against this baseline with walk-forward evidence and explicit turnover/cost disclosure before adopting them. Do not silently change the live virtual-fund policy to chase a backtest result.

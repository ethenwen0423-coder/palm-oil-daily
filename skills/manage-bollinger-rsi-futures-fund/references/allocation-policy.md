# Portfolio allocation policy

This overlay decides which simultaneous model signals the CNY 1,000,000 virtual fund can afford. It does not change the Bollinger-RSI signal rules.

## Candidate ranking

Every supported liquid variety is eligible to become a candidate. Palm oil has no default priority and missing historical research must not silently turn the fund into a palm-oil-only portfolio. The completed-close Bollinger-RSI signal is the admission condition; exact contract data, liquidity, margin, fee, and portfolio capacity remain hard requirements.

When simultaneous signals compete for capital, rank them deterministically with dimensionless current evidence: own-contract MA20 breakout distance in ATR units, MA6 trend distance in ATR units, direction-aligned RSI, and T-1 notional liquidity. Store every component and the policy version alongside the snapshot. The score is an order-priority score, not a predicted return or AI confidence. Apply sector and variety caps after ranking so capital may be distributed across unrelated sectors.

Historical walk-forward evidence may be supplied as a configured score overlay when it uses real PYYMM contracts, T-1 liquidity selection, next-open execution, actual multipliers, and the same costs. Never use continuous, weighted, synthetic, or adjusted series to admit, rank, execute, or value a live fund order.

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

Futures lots are indivisible. If a new entry would size to zero solely because one lot exceeds the soft variety or sector capacity, apply a one-lot floor only when that lot still fits all hard constraints: total gross notional, actual exchange margin use, cash available after existing and reserved margin, and concurrent-variety count. Mark the order, position, and ledger event with `whole_lot_floor_applied=true` and retain the sizing explanation. Pyramids never receive this exception. The actual next-open price must pass the hard constraints again; a gap that breaches them leaves the order unfilled for review.

If contract-level margin schedules or fees differ from the snapshot, update them before filling. Limit-up/down, suspended, illiquid, stale, or non-executable contracts remain pending or are cancelled with a reason.

## Governance

Changes to leverage, score weights, caps, eligible universe, or fee assumptions are research variants. Compare them against this baseline with walk-forward evidence and explicit turnover/cost disclosure before adopting them. Do not silently change the live virtual-fund policy to chase a backtest result.

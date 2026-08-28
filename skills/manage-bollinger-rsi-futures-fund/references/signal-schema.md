# Daily signal snapshot schema

Use UTF-8 JSON. The ledger rejects continuous symbols and an incorrect model version.

```json
{
  "as_of": "2026-08-28",
  "completed_bar": true,
  "model_version": "palm-oil-v2-real-contract-indicators-carry5-main-contract",
  "source": "actual PYYMM exchange or AKShare delivery-contract daily data",
  "signals": [
    {
      "variety": "P",
      "name": "棕榈油",
      "sector": "油脂油料",
      "contract": "P2701",
      "action": "ENTER_LONG",
      "signal_date": "2026-08-28",
      "execution_date": "2026-08-31",
      "reference_price": 9800,
      "atr14": 180,
      "multiplier": 10,
      "margin_rate": 0.12,
      "fee_rate": 0.0004,
      "score": 0.63,
      "score_basis": "cross-sector signal strength and liquidity ranking",
      "score_components": {"breakout_atr": 0.4, "trend_atr": 0.5, "rsi_alignment": 0.3, "liquidity": 0.8},
      "reason": "completed close crossed above own-contract MA20",
      "selection_volume_t_minus_1": 500000,
      "selection_open_interest_t_minus_1": 400000
    }
  ]
}
```

Allowed actions are `ENTER_LONG`, `ENTER_SHORT`, `ADD_LONG`, `ADD_SHORT`, `EXIT_LONG`, and `EXIT_SHORT`. A signal date is the completed-bar date; `execution_date` is its intended next trading day. `reference_price` is for sizing only and is never booked as a fill.

Each contract must match `^[A-Z]{1,3}[0-9]{3,4}$` and contain a delivery month. Reject `P0`, `Y0`, `M0`, `主连`, `连续`, weighted, index, synthetic, or spread symbols.

Required numeric fields for entries and pyramids are positive `reference_price`, `atr14`, `multiplier`, `margin_rate`, and non-negative `fee_rate`. `score` is the deterministic cross-sector order-priority score, not a predicted return or AI confidence; retain `score_basis` and `score_components`. Exits do not require a score and always take precedence.

Every row must retain enough evidence to identify the raw source and completed market date. When a value is missing, omit the trade and report `需进一步核验`; do not use a generic default contract multiplier or margin ratio across varieties.

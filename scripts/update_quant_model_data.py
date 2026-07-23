#!/usr/bin/env python3
"""Build versioned static signal datasets from the registered quant models."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from quant_models import MODEL_ADAPTERS


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_PATH = ROOT / "data" / "contracts" / "current_contracts.json"
OIL_FUTURES_PATH = ROOT / "data" / "oil_futures.js"
DEFAULT_JSON = ROOT / "data" / "quant_model_signals.json"
DEFAULT_JS = ROOT / "data" / "quant_model_signals.js"
SUPPORTED_PRODUCTS = ("P", "Y", "OI", "M", "RM")


def read_contracts() -> list[dict[str, Any]]:
    payload = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
    return [
        item
        for product in SUPPORTED_PRODUCTS
        for item in payload.get("products", {}).get(product, [])
    ]


def read_market_quotes(path: Path = OIL_FUTURES_PATH) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prefix = "window.OIL_FUTURES_CONTRACTS = "
    raw = path.read_text(encoding="utf-8").strip()
    if not raw.startswith(prefix):
        raise ValueError(f"unexpected oil futures wrapper in {path}")
    payload = json.loads(raw[len(prefix):].removesuffix(";"))
    quotes: dict[str, dict[str, Any]] = {}
    for item in payload.get("contracts", []):
        symbol = str(item.get("symbol", "")).strip().upper()
        if not symbol:
            continue
        try:
            price = float(item["price"])
        except (KeyError, TypeError, ValueError):
            price = None
        quotes[symbol] = {
            "price": price,
            "change": item.get("change"),
            "direction": item.get("direction"),
            "trade_date": item.get("trade_date"),
            "source": item.get("source"),
            "unit": item.get("unit") or "元/吨",
        }
    return payload, quotes


def attach_current_quotes(
    contracts: list[dict[str, Any]],
    quotes: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for contract in contracts:
        item = dict(contract)
        quote = quotes.get(str(item.get("symbol", "")).strip().upper())
        if quote:
            item["current_quote"] = dict(quote)
        enriched.append(item)
    return enriched


def build_payload() -> dict[str, Any]:
    generated_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    source_contracts = read_contracts()
    market_payload, market_quotes = read_market_quotes()
    models: list[dict[str, Any]] = []
    model_contracts: dict[str, list[dict[str, Any]]] = {}

    for adapter in MODEL_ADAPTERS:
        model = dict(adapter.metadata)
        model_id = str(model["id"])
        models.append(model)
        model_contracts[model_id] = attach_current_quotes(
            adapter.build_contracts(source_contracts),
            market_quotes,
        )

    active_models = [model for model in models if model.get("status") == "active"]
    default_model = active_models[0] if active_models else (models[0] if models else {})
    default_contracts = model_contracts.get(str(default_model.get("id", "")), [])
    available = sum(
        bool(item.get("signals"))
        for contracts in model_contracts.values()
        for item in contracts
    )

    return {
        "status": "ok" if available else "error",
        "schema_version": 2,
        "generated_at": generated_at,
        "market_updated_at": market_payload.get("updated_at"),
        "market_update_session": market_payload.get("update_session"),
        "market_timezone": market_payload.get("timezone") or "Asia/Shanghai",
        "default_model_id": default_model.get("id"),
        "models": models,
        "model_contracts": model_contracts,
        # Backward-compatible aliases for older static clients.
        "model": default_model,
        "contracts": default_contracts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--js-output", type=Path, default=DEFAULT_JS)
    args = parser.parse_args()
    payload = build_payload()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
    args.json_output.write_text(encoded + "\n", encoding="utf-8")
    args.js_output.write_text(f"window.QUANT_MODEL_SIGNALS = {encoded};\n", encoding="utf-8")
    model_count = len(payload["models"])
    available = sum(
        bool(item.get("signals"))
        for contracts in payload["model_contracts"].values()
        for item in contracts
    )
    print(f"generated {model_count} quant model(s) with {available} available contract result(s)")


if __name__ == "__main__":
    main()

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


def build_payload() -> dict[str, Any]:
    generated_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    source_contracts = read_contracts()
    models: list[dict[str, Any]] = []
    model_contracts: dict[str, list[dict[str, Any]]] = {}

    for adapter in MODEL_ADAPTERS:
        model = dict(adapter.metadata)
        model_id = str(model["id"])
        models.append(model)
        model_contracts[model_id] = adapter.build_contracts(source_contracts)

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

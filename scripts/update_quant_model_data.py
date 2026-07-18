#!/usr/bin/env python3
"""Build static quant-model signals with the installed trade-signal skill."""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_PATH = ROOT / "data" / "contracts" / "current_contracts.json"
DEFAULT_JSON = ROOT / "data" / "quant_model_signals.json"
DEFAULT_JS = ROOT / "data" / "quant_model_signals.js"
SKILL_SCRIPT = ROOT / "skills" / "generate-oilseed-trade-signal" / "scripts" / "generate_signal.py"
SUPPORTED_PRODUCTS = ("P", "Y", "OI", "M", "RM")


def load_skill() -> Any:
    if not SKILL_SCRIPT.exists():
        raise FileNotFoundError(f"量化模型 skill 不存在: {SKILL_SCRIPT}")
    spec = importlib.util.spec_from_file_location("palm_oil_trade_signal_skill", SKILL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载量化模型 skill")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_contracts() -> list[dict[str, Any]]:
    payload = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
    contracts: list[dict[str, Any]] = []
    for product in SUPPORTED_PRODUCTS:
        for item in payload.get("products", {}).get(product, []):
            contracts.append(item)
    return contracts


def skill_args(position: str) -> SimpleNamespace:
    return SimpleNamespace(
        position=position,
        entry_date=None,
        entry_price=None,
        entry_atr=None,
        highest_since_entry=None,
        lowest_since_entry=None,
        blocked_direction="none",
        allow_forming_bar=False,
    )


def build_contract_signal(skill: Any, contract: dict[str, Any]) -> dict[str, Any]:
    symbol = str(contract["symbol"])
    raw, data_source = skill.fetch(symbol)
    completed, provisional, bar_note = skill.select_completed(raw, False)
    data = skill.indicators(completed)
    if len(data) < 40:
        raise RuntimeError("可用日线少于 40 根")

    signals: dict[str, Any] = {}
    for position in ("flat", "long", "short"):
        result = skill.decide(data, skill_args(position), symbol)
        skill.mark_execution_window(result)
        result["data_source"] = data_source
        signals[position] = result

    latest = signals["flat"].get("market", {})
    product = str(contract.get("product", "")).upper()
    return {
        "symbol": symbol,
        "product": product,
        "product_name": contract.get("product_name", product),
        "rank": contract.get("rank"),
        "label": contract.get("label", ""),
        "market_date": signals["flat"].get("market_date"),
        "data_source": data_source,
        "bar_completed": not provisional,
        "bar_note": bar_note,
        "model_scope": "validated_mapping" if product == "P" else "rule_trial",
        "model_scope_label": "成熟模型映射" if product == "P" else "同规则试算",
        "market": latest,
        "signals": signals,
    }


def build_payload() -> dict[str, Any]:
    skill = load_skill()
    generated_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    items: list[dict[str, Any]] = []
    for contract in read_contracts():
        try:
            items.append(build_contract_signal(skill, contract))
        except Exception as exc:  # Keep one failed symbol from blocking the whole page.
            items.append(
                {
                    "symbol": contract.get("symbol"),
                    "product": contract.get("product"),
                    "product_name": contract.get("product_name"),
                    "rank": contract.get("rank"),
                    "label": contract.get("label"),
                    "status": "error",
                    "message": str(exc),
                }
            )
    return {
        "status": "ok" if any(item.get("signals") for item in items) else "error",
        "generated_at": generated_at,
        "model": {
            "id": "bollinger-rsi-ma6-v1",
            "name": "布林中轨 + RSI 背离模型",
            "skill": "generate-oilseed-trade-signal",
            "validated_instrument": "AKShare P0 棕榈油主力连续日线",
            "entry_rule": "收盘价上穿/下穿 MA20，次交易日开盘执行",
            "take_profit_rule": "20 日价格与 RSI 背离后全部止盈",
            "stop_rule": "多单满足 0.75 ATR 后连续两日收于 MA6 下；空单一日收于 MA6 上",
            "cost_assumption_one_way": 0.0004,
        },
        "contracts": items,
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
    available = sum(bool(item.get("signals")) for item in payload["contracts"])
    print(f"generated quant-model signals for {available}/{len(payload['contracts'])} contracts")


if __name__ == "__main__":
    main()

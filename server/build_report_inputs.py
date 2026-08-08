#!/usr/bin/env python3
"""Build an auditable report source run from server-owned live datasets."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
PRODUCT_KEYS = {
    "P": "palm_oil",
    "Y": "soybean_oil",
    "OI": "rapeseed_oil",
}


class ReportInputError(RuntimeError):
    """Raised when live data cannot support a governed report run."""


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportInputError(f"cannot read server dataset: {path}") from exc
    if not isinstance(payload, dict):
        raise ReportInputError(f"server dataset must be a JSON object: {path}")
    return payload


def parse_dataset_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ReportInputError(f"missing freshness timestamp: {label}")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReportInputError(f"invalid freshness timestamp: {label}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def validate_freshness(
    datasets: dict[str, tuple[dict[str, Any], tuple[str, ...]]],
    *,
    kind: str,
    now: datetime,
) -> dict[str, str]:
    max_ages = {
        "daily": {
            "oil_futures": timedelta(hours=8),
            "exchange_futures": timedelta(hours=18),
            "quant_model_signals": timedelta(hours=18),
            "supply_demand": timedelta(hours=36),
            "contracts": timedelta(hours=72),
        },
        "weekend": {
            "oil_futures": timedelta(days=4),
            "exchange_futures": timedelta(days=4),
            "quant_model_signals": timedelta(days=4),
            "supply_demand": timedelta(hours=36),
            "contracts": timedelta(days=7),
        },
    }[kind]
    observed: dict[str, str] = {}
    for label, (payload, fields) in datasets.items():
        raw = next((payload.get(field) for field in fields if payload.get(field)), None)
        timestamp = parse_dataset_timestamp(raw, label)
        age = now - timestamp
        if age < timedelta(minutes=-5):
            raise ReportInputError(f"future-dated server dataset: {label}")
        if age > max_ages[label]:
            raise ReportInputError(
                f"stale server dataset: {label} age={int(age.total_seconds())}s"
            )
        observed[label] = timestamp.isoformat(timespec="seconds")
    return observed


def as_number(value: Any) -> float | None:
    if value in (None, "", "-", "需进一步核验", "待更新"):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def rank_one_contracts(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for item in payload.get("contracts", []):
        if not isinstance(item, dict):
            continue
        product = str(item.get("product") or "").upper()
        try:
            rank = int(item.get("contract_rank"))
        except (TypeError, ValueError):
            continue
        if product in PRODUCT_KEYS and rank == 1:
            if product in selected:
                raise ReportInputError(f"duplicate rank-1 contract: {product}")
            selected[product] = item
    missing = sorted(set(PRODUCT_KEYS) - set(selected))
    if missing:
        raise ReportInputError(f"missing rank-1 contracts: {', '.join(missing)}")
    for product, item in selected.items():
        score = item.get("score")
        strategy = item.get("strategy_recommendation")
        if not isinstance(score, dict) or not score.get("stance"):
            raise ReportInputError(f"missing deterministic score output: {product}")
        if not isinstance(strategy, dict):
            raise ReportInputError(f"missing deterministic strategy output: {product}")
        for field in ("lower_watch", "upper_watch", "invalidation"):
            if strategy.get(field) in (None, ""):
                raise ReportInputError(
                    f"missing deterministic strategy field: {product}.{field}"
                )
    return selected


def market_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": item.get("name") or item.get("product_name") or item.get("product"),
        "status": "ok" if as_number(item.get("price")) is not None else "missing",
        "source": item.get("source") or "需进一步核验",
        "fetched_at": item.get("trade_date"),
        "published_at": item.get("trade_date"),
        "price": as_number(item.get("price")),
        "change": None,
        "change_pct": as_number(item.get("change")),
        "contract": item.get("contract") or item.get("symbol"),
        "open": as_number(item.get("open")),
        "high": as_number(item.get("high")),
        "low": as_number(item.get("low")),
        "close": as_number(item.get("preclose")),
        "volume": as_number(item.get("volume")),
        "open_interest": as_number(item.get("open_interest")),
        "verification": item.get("verification") or "需进一步核验",
        "score": item.get("score"),
        "strategy_recommendation": item.get("strategy_recommendation"),
    }


def first_contract(payload: dict[str, Any], product: str) -> dict[str, Any] | None:
    for item in payload.get("contracts", []):
        if isinstance(item, dict) and str(item.get("product") or "").upper() == product:
            return item
    return None


def build_snapshot(
    data_root: Path,
    report_date: str,
    now: datetime,
) -> dict[str, Any]:
    oil = load_object(data_root / "oil_futures.json")
    supply = load_object(data_root / "supply-demand.json")
    exchange = load_object(data_root / "exchange_futures.json")
    quant = load_object(data_root / "quant_model_signals.json")
    contracts = load_object(data_root / "contracts" / "current_contracts.json")
    selected = rank_one_contracts(oil)

    external: dict[str, Any] = {}
    for product, key in (("FCPO", "bmd_palm_oil"), ("CPOTR", "indonesia_cpo_spot")):
        item = first_contract(oil, product)
        if item:
            external[key] = market_record(item)

    snapshot = {
        "date": report_date,
        "timestamp": now.isoformat(timespec="seconds"),
        "market_status": "服务器自动采集",
        "source_mode": "server_live_data",
        "domestic": {
            PRODUCT_KEYS[product]: market_record(item)
            for product, item in selected.items()
        },
        "external": external,
        "fundamental": {
            "official_supply_demand": {
                "status": supply.get("update_status") or "需进一步核验",
                "source": "MPOB/GAPKI/USDA official checks",
                "fetched_at": supply.get("checked_at") or supply.get("generated_at"),
                "summary": supply.get("update_message") or "需进一步核验",
            },
            "exchange_context": {
                "status": "ok" if exchange.get("contracts") else "missing",
                "source": "server exchange collector",
                "fetched_at": exchange.get("updated_at"),
                "summary": f"core contracts={len(exchange.get('contracts') or [])}",
            },
        },
        "server_evidence": {
            "oil_futures_updated_at": oil.get("updated_at"),
            "exchange_futures_updated_at": exchange.get("updated_at"),
            "quant_generated_at": quant.get("generated_at"),
            "quant_market_updated_at": quant.get("market_updated_at"),
            "supply_checked_at": supply.get("checked_at") or supply.get("generated_at"),
            "contracts_generated_at": contracts.get("generated_at"),
            "fixed_logic": ["otc_structure_library", "quant_model_rules"],
        },
    }
    return snapshot


def build_manifest(
    data_root: Path,
    report_date: str,
    kind: str,
    now: datetime,
) -> dict[str, Any]:
    oil = load_object(data_root / "oil_futures.json")
    supply = load_object(data_root / "supply-demand.json")
    exchange = load_object(data_root / "exchange_futures.json")
    quant = load_object(data_root / "quant_model_signals.json")
    contracts = load_object(data_root / "contracts" / "current_contracts.json")
    freshness = validate_freshness(
        {
            "oil_futures": (oil, ("updated_at",)),
            "exchange_futures": (exchange, ("updated_at",)),
            "quant_model_signals": (quant, ("market_updated_at", "generated_at")),
            "supply_demand": (supply, ("checked_at", "generated_at")),
            "contracts": (contracts, ("generated_at",)),
        },
        kind=kind,
        now=now,
    )
    symbols = [
        str(item.get("symbol") or "")
        for rows in (contracts.get("products") or {}).values()
        if isinstance(rows, list)
        for item in rows
        if isinstance(item, dict) and item.get("symbol")
    ]
    return {
        "date": report_date,
        "kind": kind,
        "generated_at": now.isoformat(timespec="seconds"),
        "source_mode": "server_live_data",
        "skills": {
            "server-market-collector": {"installed": True},
            "server-supply-demand": {"installed": True},
        },
        "environment": {"server_owned": True},
        "freshness": freshness,
        "contract_discovery": {
            "path": str(data_root / "contracts" / "current_contracts.json"),
            "symbols": list(dict.fromkeys(symbols)),
        },
        "results": [
            {
                "name": "futures_oil_fetch_market_data",
                "status": "ok",
                "returncode": 0,
                "source": "server live-data/oil_futures.json",
                "observed_at": oil.get("updated_at"),
            },
            {
                "name": "server_official_supply_check",
                "status": "ok" if supply.get("checked_at") else "failed",
                "returncode": 0 if supply.get("checked_at") else 2,
                "source": "server live-data/supply-demand.json",
                "observed_at": supply.get("checked_at"),
            },
        ],
    }


def write_source_run(
    data_root: Path,
    runtime_root: Path,
    report_date: str,
    kind: str,
    now: datetime,
) -> dict[str, Any]:
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", report_date):
        raise ReportInputError("report date must be YYYY-MM-DD")
    if now.date().isoformat() != report_date:
        raise ReportInputError("server report inputs may only be built for the current date")
    run_root = runtime_root / "source_runs" / f"{report_date}-{kind}"
    raw_root = run_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(data_root, report_date, kind, now)
    snapshot = build_snapshot(data_root, report_date, now)
    raw_path = raw_root / "futures_market_data.json"
    raw_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if kind == "weekend":
        (raw_root / "futures_market_data.weekly_compatible.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (run_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "ok",
        "report_date": report_date,
        "kind": kind,
        "run_root": str(run_root),
        "manifest": str(run_root / "manifest.json"),
        "snapshot": str(raw_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--kind", choices=("daily", "weekend"), required=True)
    parser.add_argument("--now")
    args = parser.parse_args()
    try:
        payload = write_source_run(
            args.data_root.resolve(),
            args.runtime_root.resolve(),
            args.date,
            args.kind,
            parse_now(args.now),
        )
    except (OSError, ReportInputError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

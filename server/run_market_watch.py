#!/usr/bin/env python3
"""Publish one bounded five-minute market and event watch snapshot."""

from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
SITE_ROOT = Path(os.environ.get("PALM_OIL_SITE_ROOT", "/srv/palm-oil-daily/site"))
LIVE_ROOT = Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", "/srv/palm-oil-daily/live-data"))
STATE_ROOT = Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", "/srv/palm-oil-daily/state"))
PER_CALL_TIMEOUT = int(os.environ.get("PALM_OIL_WATCH_CALL_TIMEOUT_SECONDS", "5"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def in_market_window(now: datetime) -> bool:
    minutes = now.hour * 60 + now.minute
    weekday = now.isoweekday()
    if 2 <= weekday <= 6 and 0 <= minutes < 150:
        return True
    if not 1 <= weekday <= 5:
        return False
    return any(
        start <= minutes < end
        for start, end in (
            (540, 615),
            (630, 690),
            (810, 900),
            (1260, 1380),
        )
    )


def concrete_contract(value: object) -> bool:
    return bool(re.fullmatch(r"[A-Z]{1,3}\d{3,4}", str(value or "").upper()))


def quote_record(updater: Any, item: Any) -> dict[str, Any] | None:
    product_name = str(item["symbol"])
    exchange = updater.EXCHANGE_LABELS[str(item["exchange"])]
    frame = updater.akshare_call(
        updater.ak.futures_zh_realtime,
        symbol=product_name,
        timeout=PER_CALL_TIMEOUT,
    )
    if frame is None or frame.empty:
        return None
    candidates = frame[frame["symbol"].map(concrete_contract)].copy()
    if candidates.empty:
        return None
    candidates["volume"] = candidates["volume"].fillna(0)
    candidates["position"] = candidates["position"].fillna(0)
    candidates = candidates[(candidates["volume"] > 0) & (candidates["position"] > 0)]
    if candidates.empty:
        return None
    main = candidates.sort_values(["volume", "position"], ascending=False).iloc[0]
    price = updater.as_number(main.get("trade"))
    if price is None or price <= 0:
        return None
    contract_symbol = str(main["symbol"]).upper()
    variety_match = re.match(r"[A-Z]+", contract_symbol)
    return {
        "symbol": contract_symbol,
        "product": variety_match.group(0) if variety_match else product_name,
        "name": product_name,
        "category": updater.category_for(product_name),
        "exchange": exchange,
        "price": float(price),
        "change_pct": updater.percent_change(main.get("trade"), main.get("preclose")),
        "volume": int(main["volume"]),
        "open_interest": int(main["position"]),
        "trade_date": str(main.get("tradedate") or ""),
        "source": "AkShare:futures_zh_realtime",
    }


def collect_quotes(updater: Any) -> tuple[list[dict[str, Any]], list[str], int]:
    symbols = updater.akshare_call(
        updater.ak.futures_symbol_mark,
        timeout=PER_CALL_TIMEOUT,
    )
    if symbols is None or symbols.empty:
        raise RuntimeError("AkShare core product list unavailable")
    symbols = symbols[symbols["exchange"].isin(updater.EXCHANGE_LABELS)].copy()
    symbols = symbols[symbols["symbol"].isin(updater.CORE_PRODUCTS)].copy()
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for _, item in symbols.iterrows():
        try:
            record = quote_record(updater, item)
        except Exception as exc:  # one source failure must not erase the snapshot
            errors.append(f"{item['symbol']}:{type(exc).__name__}")
            continue
        if record is None:
            errors.append(f"{item['symbol']}:empty")
        else:
            records.append(record)
    return records, errors, len(symbols)


def private_value(path: Path, key: str) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.strip().removeprefix("export ").partition("=")
            if separator and name.strip() == key and value.strip():
                return value.strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def main() -> int:
    now = datetime.now(SHANGHAI)
    if not in_market_window(now) and os.environ.get("PALM_OIL_WATCH_FORCE") != "1":
        print(json.dumps({"status": "noop", "reason": "outside_market_window", "now": now.isoformat()}))
        return 0
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    lock = (STATE_ROOT / "market-watch.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "busy", "retry": True}))
        lock.close()
        return 0
    try:
        watch = load_module("palm_market_watch_runtime", SITE_ROOT / "server" / "market_watch.py")
        updater = load_module("palm_exchange_watch_runtime", SITE_ROOT / "scripts" / "update_exchange_futures_data.py")
        records, errors, expected = collect_quotes(updater)
        if not records:
            raise RuntimeError("no validated realtime contracts")
        previous_watch: dict[str, Any] = {}
        previous_quotes: dict[str, Any] = {}
        try:
            previous_watch = watch.load_json(LIVE_ROOT / "market_watch.json")
            previous_quotes = watch.load_json(STATE_ROOT / "market-watch" / "quotes.json")
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        payload, quote_state = watch.build_watch(
            {"contracts": []},
            {"contracts": records},
            previous_quotes,
            previous_watch.get("events", []) if isinstance(previous_watch.get("events"), list) else [],
            now,
            os.environ.get("MX_APIKEY") or private_value(STATE_ROOT / "private.env", "MX_APIKEY"),
        )
        event_sources = [
            item for item in previous_watch.get("sources", [])
            if isinstance(item, dict) and item.get("name") != "全量期货行情"
        ]
        payload["sources"].extend(event_sources)
        if previous_watch.get("events_updated_at"):
            payload["events_updated_at"] = previous_watch["events_updated_at"]
        payload["status"] = "ready" if len(records) == expected else "degraded"
        payload["coverage"].update({"expected_products": expected, "failed_products": len(errors)})
        payload["quotes"] = [
            {**record, "observed_at": now.isoformat(timespec="seconds")}
            for record in sorted(
                records,
                key=lambda item: (str(item.get("category")), str(item.get("symbol"))),
            )
        ]
        payload["sources"][0]["detail"] = f"本轮核心品种 {len(records)}/{expected}；失败 {len(errors)}。"
        payload["sources"][0]["state"] = "ready" if not errors else "degraded"
        if errors:
            payload["source_errors"] = errors[:20]
        LIVE_ROOT.mkdir(parents=True, exist_ok=True)
        (STATE_ROOT / "market-watch").mkdir(parents=True, exist_ok=True)
        watch.atomic_write(LIVE_ROOT / "market_watch.json", payload)
        watch.atomic_write(STATE_ROOT / "market-watch" / "quotes.json", quote_state)
        print(json.dumps({"status": payload["status"], "coverage": payload["coverage"], "generated_at": payload["generated_at"]}, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc), "retry": True}, ensure_ascii=False))
        return 2
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the static oil-futures contract data used by the home-page tab."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNS = ROOT / "source_runs"
OUTPUT = ROOT / "data" / "oil_futures.js"

DOMESTIC = [
    {
        "key": "palm_oil",
        "symbol": "P",
        "name": "棕榈油",
        "market": "DCE",
        "ak_realtime": "棕榈",
        "fallback": "P2609",
        "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
    },
    {
        "key": "soybean_oil",
        "symbol": "Y",
        "name": "豆油",
        "market": "DCE",
        "ak_realtime": "豆油",
        "fallback": "Y2609",
        "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
    },
    {
        "key": "rapeseed_oil",
        "symbol": "OI",
        "name": "菜油",
        "market": "CZCE",
        "ak_realtime": "菜油",
        "fallback": "OI2609",
        "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
    },
]

EXTERNAL = [
    {
        "key": "bmd_palm_oil",
        "symbol": "FCPO",
        "name": "马棕油",
        "market": "BMD",
        "note": "产地盘面决定 P 的外盘弹性。",
    },
    {
        "key": "cbot_bean_oil",
        "symbol": "CBOT BO",
        "name": "CBOT 豆油",
        "market": "CME",
        "note": "美豆油用于观察全球油脂链条共振。",
    },
]


def load_akshare():
    try:
        import akshare as ak  # type: ignore

        return ak
    except Exception:
        return None


def as_float(value: Any) -> float | None:
    try:
        if value in (None, "", "-"):
            return None
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    try:
        if value in (None, "", "-"):
            return None
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return int(float(value))
    except (TypeError, ValueError):
        return None


def fmt_number(value: Any, digits: int = 2) -> str:
    number = as_float(value)
    if number is None:
        return "需进一步核验"
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.{digits}f}"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "需进一步核验"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def fmt_lots(value: Any) -> str:
    number = as_int(value)
    if number is None:
        return "需进一步核验"
    if abs(number) >= 10000:
        return f"{number / 10000:.2f} 万手"
    return f"{number} 手"


def direction(change_pct: Any) -> str:
    number = as_float(change_pct)
    if number is None:
        return "→"
    if number > 0:
        return "↑"
    if number < 0:
        return "↓"
    return "→"


def latest_market_snapshot() -> tuple[dict[str, Any] | None, Path | None]:
    candidates = sorted(SOURCE_RUNS.glob("*/raw/futures_market_data.json"), reverse=True)
    for path in candidates:
        try:
            return json.loads(path.read_text(encoding="utf-8")), path
        except Exception:
            continue
    return None, None


def concrete_contract(value: Any) -> str | None:
    text = str(value or "").upper().strip()
    if re.fullmatch(r"[A-Z]+0", text):
        return None
    if re.fullmatch(r"[A-Z]+\d{4}", text):
        return text
    if re.fullmatch(r"FCPO[A-Z]\d{4}", text) or text in {"BO=F", "ZS=F"}:
        return text
    return None


def ak_realtime_contract(ak: Any, variety: str) -> dict[str, Any] | None:
    if ak is None:
        return None
    try:
        df = ak.futures_zh_realtime(symbol=variety)
        if df is None or len(df) == 0:
            return None
        rows = df[~df["symbol"].astype(str).str.fullmatch(r"[A-Za-z]+0")]
        if rows.empty:
            return None
        rows = rows.sort_values(by="volume", ascending=False)
        row = rows.iloc[0]
        trade = as_float(row.get("trade"))
        preclose = as_float(row.get("preclose"))
        change_pct = None
        if trade is not None and preclose not in (None, 0):
            change_pct = (trade - preclose) / preclose * 100
        return {
            "contract": str(row.get("symbol") or "").upper(),
            "price": trade,
            "change_pct": change_pct,
            "open": as_float(row.get("open")),
            "high": as_float(row.get("high")),
            "low": as_float(row.get("low")),
            "preclose": preclose,
            "volume": as_int(row.get("volume")),
            "open_interest": as_int(row.get("position")),
            "tradedate": str(row.get("tradedate") or ""),
            "ticktime": str(row.get("ticktime") or ""),
            "source": "akshare:futures_zh_realtime",
        }
    except Exception:
        return None


def ak_daily_contract(ak: Any, contract: str) -> dict[str, Any] | None:
    if ak is None:
        return None
    try:
        df = ak.futures_zh_daily_sina(symbol=contract)
        if df is None or len(df) == 0:
            return None
        row = df.iloc[-1]
        previous = df.iloc[-2] if len(df) >= 2 else None
        close = as_float(row.get("close"))
        prev_close = as_float(previous.get("close")) if previous is not None else None
        change_pct = None
        if close is not None and prev_close not in (None, 0):
            change_pct = (close - prev_close) / prev_close * 100
        return {
            "contract": contract.upper(),
            "price": close,
            "change_pct": change_pct,
            "open": as_float(row.get("open")),
            "high": as_float(row.get("high")),
            "low": as_float(row.get("low")),
            "preclose": prev_close,
            "settle": as_float(row.get("settle")),
            "volume": as_int(row.get("volume")),
            "open_interest": as_int(row.get("hold")),
            "tradedate": str(row.get("date") or ""),
            "source": "akshare:futures_zh_daily_sina",
        }
    except Exception:
        return None


def merge_domestic(spec: dict[str, str], snapshot: dict[str, Any] | None, ak: Any) -> dict[str, Any]:
    skill_record = (snapshot or {}).get("domestic", {}).get(spec["key"], {})
    realtime = ak_realtime_contract(ak, spec["ak_realtime"])
    fallback_contract = concrete_contract(skill_record.get("contract")) or (realtime or {}).get("contract") or spec["fallback"]
    daily = ak_daily_contract(ak, fallback_contract)

    source = skill_record if skill_record.get("status") == "ok" else {}
    if not source:
      source = realtime or daily or {}
    if realtime:
        source = {**source, **{key: value for key, value in realtime.items() if value is not None}}
    if daily:
        source = {**daily, **{key: value for key, value in source.items() if value not in (None, "", "需进一步核验")}}

    contract = concrete_contract(source.get("contract")) or fallback_contract
    return {
        "symbol": spec["symbol"],
        "name": spec["name"],
        "market": spec["market"],
        "contract": contract,
        "price": fmt_number(source.get("price")),
        "change": fmt_pct(source.get("change_pct")),
        "volume": fmt_lots(source.get("volume")),
        "open_interest": fmt_lots(source.get("open_interest")),
        "direction": direction(source.get("change_pct")),
        "open": fmt_number(source.get("open")),
        "high": fmt_number(source.get("high")),
        "low": fmt_number(source.get("low")),
        "preclose": fmt_number(source.get("preclose") if source.get("preclose") is not None else source.get("close")),
        "settle": fmt_number(source.get("settle")),
        "trade_date": source.get("tradedate") or source.get("fetched_at", "")[:10],
        "source": source.get("source") or "需进一步核验",
        "note": spec["note"],
    }


def merge_external(spec: dict[str, str], snapshot: dict[str, Any] | None) -> dict[str, Any]:
    record = (snapshot or {}).get("external", {}).get(spec["key"], {})
    return {
        "symbol": spec["symbol"],
        "name": spec["name"],
        "market": spec["market"],
        "contract": record.get("contract") or spec["symbol"],
        "price": fmt_number(record.get("price")),
        "change": fmt_pct(record.get("change_pct")),
        "volume": fmt_lots(record.get("volume")),
        "open_interest": fmt_lots(record.get("open_interest")),
        "direction": direction(record.get("change_pct")),
        "open": fmt_number(record.get("open")),
        "high": fmt_number(record.get("high")),
        "low": fmt_number(record.get("low")),
        "preclose": fmt_number(record.get("close")),
        "settle": "需进一步核验",
        "trade_date": record.get("published_at", "")[:10] or record.get("fetched_at", "")[:10],
        "source": record.get("source") or "需进一步核验",
        "note": spec["note"],
    }


def write_js(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    output.write_text(f"window.OIL_FUTURES_CONTRACTS = {text};\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update static oil futures contract data.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    snapshot, snapshot_path = latest_market_snapshot()
    ak = load_akshare()
    contracts = [merge_domestic(spec, snapshot, ak) for spec in DOMESTIC]
    contracts.extend(merge_external(spec, snapshot) for spec in EXTERNAL)

    source_note = "futures-oil-daily 最新快照"
    if snapshot_path:
        source_note += f"：{snapshot_path.relative_to(ROOT)}"
    source_note += "；内盘具体合约与日线缺口由 AkShare 补充"
    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": source_note,
        "contracts": contracts,
    }
    write_js(payload, args.output)
    print(f"updated {args.output.relative_to(ROOT)} with {len(contracts)} contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate deterministic daily signals for a confirmed oilseed futures symbol."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests


SUPPORTED_PRODUCTS = {"P", "Y", "OI", "M", "RM"}
SYMBOL_PATTERN = re.compile(r"^([A-Z]{1,2})(\d{1,4})$")


def normalize_symbol(value: str) -> tuple[str, str, bool]:
    symbol = re.sub(r"\s+", "", str(value or "")).upper()
    match = SYMBOL_PATTERN.fullmatch(symbol)
    if not match:
        raise ValueError(f"invalid futures symbol: {value!r}")
    product, digits = match.groups()
    if product not in SUPPORTED_PRODUCTS:
        supported = ", ".join(sorted(SUPPORTED_PRODUCTS))
        raise ValueError(f"unsupported product {product!r}; supported products: {supported}")
    is_main_continuous = digits == "0"
    if not is_main_continuous and len(digits) not in {3, 4}:
        raise ValueError("delivery contract must use a 3- or 4-digit month code")
    return symbol, product, is_main_continuous


def fetch(symbol: str) -> tuple[pd.DataFrame, str]:
    import akshare as ak

    normalized, _, is_main_continuous = normalize_symbol(symbol)
    source = "akshare:futures_main_sina" if is_main_continuous else "akshare:futures_zh_daily_sina"
    original_get = requests.get

    def bounded_get(*args, **kwargs):
        kwargs.setdefault("timeout", (5, 15))
        return original_get(*args, **kwargs)

    requests.get = bounded_get
    data = None
    last_error: Exception | None = None
    try:
        for _ in range(2):
            try:
                if is_main_continuous:
                    data = ak.futures_main_sina(symbol=normalized).rename(
                        columns={
                            "日期": "datetime",
                            "开盘价": "open",
                            "最高价": "high",
                            "最低价": "low",
                            "收盘价": "close",
                            "成交量": "volume",
                            "持仓量": "hold",
                        }
                    )
                else:
                    data = ak.futures_zh_daily_sina(symbol=normalized).rename(columns={"date": "datetime"})
                break
            except Exception as exc:
                last_error = exc
    finally:
        requests.get = original_get

    if data is None:
        raise RuntimeError(f"market data request failed after 2 attempts for {normalized}: {last_error}")

    required = {"datetime", "open", "high", "low", "close"}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise RuntimeError(f"market data missing columns: {', '.join(missing)}")
    data["datetime"] = pd.to_datetime(data["datetime"], errors="coerce")
    for column in ["open", "high", "low", "close", "volume", "hold"]:
        if column in data:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    cleaned = (
        data.dropna(subset=["datetime", "open", "high", "low", "close"])
        .sort_values("datetime")
        .drop_duplicates("datetime", keep="last")
        .reset_index(drop=True)
    )
    if cleaned.empty:
        raise RuntimeError(f"no usable daily bars returned for {normalized}")
    return cleaned, source


def indicators(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    out["ma6"] = out.close.rolling(6).mean()
    out["ma20"] = out.close.rolling(20).mean()
    delta = out.close.diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    average_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    average_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    relative_strength = average_gain / average_loss.replace(0, np.nan)
    out["rsi"] = 100 - 100 / (1 + relative_strength)
    out.loc[average_loss.eq(0) & average_gain.gt(0), "rsi"] = 100
    previous_close = out.close.shift()
    true_range = pd.concat(
        [
            out.high - out.low,
            (out.high - previous_close).abs(),
            (out.low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr"] = true_range.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    out["long_signal"] = out.close.gt(out.ma20) & out.close.shift().le(out.ma20.shift())
    out["short_signal"] = out.close.lt(out.ma20) & out.close.shift().ge(out.ma20.shift())

    prior_high, rsi_high, prior_low, rsi_low = [], [], [], []
    for index in range(len(out)):
        if index < 20:
            prior_high.append(np.nan)
            rsi_high.append(np.nan)
            prior_low.append(np.nan)
            rsi_low.append(np.nan)
            continue
        previous = out.iloc[index - 20 : index]
        high_index, low_index = previous.high.idxmax(), previous.low.idxmin()
        prior_high.append(previous.loc[high_index, "high"])
        rsi_high.append(previous.loc[high_index, "rsi"])
        prior_low.append(previous.loc[low_index, "low"])
        rsi_low.append(previous.loc[low_index, "rsi"])
    out["bearish_divergence"] = out.high.gt(prior_high) & out.rsi.le(rsi_high)
    out["bullish_divergence"] = out.low.lt(prior_low) & out.rsi.ge(rsi_low)
    return out


def select_completed(data: pd.DataFrame, allow_forming: bool) -> tuple[pd.DataFrame, bool, str]:
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    latest_date = data.datetime.iloc[-1].date()
    forming = False
    reason = "latest source bar treated as completed"
    if latest_date >= now.date():
        daytime_open = now.hour < 15 or (now.hour == 15 and now.minute < 30)
        night_open = now.hour >= 21
        forming = daytime_open or night_open
    if forming and not allow_forming:
        data = data.iloc[:-1].reset_index(drop=True)
        reason = "latest same-day bar excluded because it may still be forming"
    elif forming:
        reason = "latest same-day bar included as provisional by explicit request"
    if data.empty:
        raise RuntimeError("no completed daily bar is available")
    return data, forming and allow_forming, reason


def position_context(data: pd.DataFrame, args: argparse.Namespace) -> dict:
    if args.position == "flat":
        return {}
    if args.entry_date:
        entry_date = pd.Timestamp(args.entry_date)
        matches = data.index[data.datetime >= entry_date]
        if not len(matches):
            return {"error": "entry_date is later than available market data"}
        index = int(matches[0])
        entry_price = args.entry_price if args.entry_price is not None else float(data.loc[index, "open"])
        if args.entry_atr is not None:
            entry_atr = args.entry_atr
        elif index > 0 and pd.notna(data.loc[index - 1, "atr"]):
            entry_atr = float(data.loc[index - 1, "atr"])
        else:
            entry_atr = None
        held = data.iloc[index:].copy()
        return {
            "entry_index": index,
            "entry_date": str(data.loc[index, "datetime"].date()),
            "entry_price": entry_price,
            "entry_atr": entry_atr,
            "highest_since_entry": args.highest_since_entry or float(held.high.max()),
            "lowest_since_entry": args.lowest_since_entry or float(held.low.min()),
        }
    return {
        "entry_price": args.entry_price,
        "entry_atr": args.entry_atr,
        "highest_since_entry": args.highest_since_entry,
        "lowest_since_entry": args.lowest_since_entry,
    }


def decide(data: pd.DataFrame, args: argparse.Namespace, symbol: str) -> dict:
    latest = data.iloc[-1]
    position = args.position
    blocked = args.blocked_direction
    action, execution, rationale = "WAIT", "none", []
    stop_state: dict = {}

    if position == "flat":
        direction = "long" if latest.long_signal else ("short" if latest.short_signal else "none")
        if blocked != "none" and direction != "none" and direction != blocked:
            blocked = "none"
        if direction == "long" and blocked != "long":
            action, execution = "OPEN_LONG", "next_trading_day_open"
            rationale.append("completed close crossed above MA20")
        elif direction == "short" and blocked != "short":
            action, execution = "OPEN_SHORT", "next_trading_day_open"
            rationale.append("completed close crossed below MA20")
        elif direction != "none" and direction == blocked:
            rationale.append(f"{direction} signal ignored because that direction remains blocked after a stop")
        else:
            rationale.append("no new MA20 crossover")
    else:
        context = position_context(data, args)
        if "error" in context:
            return {"status": "insufficient_position_data", "symbol": symbol, "message": context["error"]}
        if position == "long" and bool(latest.bearish_divergence):
            action, execution = "TAKE_PROFIT_EXIT_LONG", "next_trading_day_open"
            rationale.append("price made a 20-day high while RSI failed to confirm")
        elif position == "short" and bool(latest.bullish_divergence):
            action, execution = "TAKE_PROFIT_EXIT_SHORT", "next_trading_day_open"
            rationale.append("price made a 20-day low while RSI failed to confirm")
        elif position == "short":
            breached = bool(latest.close > latest.ma6)
            stop_state = {"armed": True, "close_above_ma6": breached, "ma6": float(latest.ma6)}
            if breached:
                action, execution, blocked = "STOP_EXIT_SHORT", "next_trading_day_open", "short"
                rationale.append("short stop triggered: completed close above MA6")
            else:
                action = "HOLD_SHORT"
                rationale.append("short stop and bullish divergence not triggered")
        else:
            required = [context.get("entry_price"), context.get("entry_atr"), context.get("highest_since_entry")]
            if any(value is None for value in required):
                stop_state = {
                    "evaluated": False,
                    "missing": "entry_date or entry_price, entry_atr, and highest_since_entry",
                }
                action = "HOLD_LONG_DATA_NEEDED"
                rationale.append("long ATR activation cannot be evaluated from the supplied position data")
            else:
                mfe_atr = (context["highest_since_entry"] - context["entry_price"]) / context["entry_atr"]
                armed = mfe_atr >= 0.75
                start = context.get("entry_index", 0)
                held = data.iloc[start:]
                consecutive = 0
                high_water = -np.inf
                for _, row in held.iterrows():
                    high_water = max(high_water, row.high)
                    row_armed = (high_water - context["entry_price"]) / context["entry_atr"] >= 0.75
                    consecutive = consecutive + 1 if row_armed and row.close < row.ma6 else 0
                stop_state = {
                    "armed": armed,
                    "mfe_atr": float(mfe_atr),
                    "consecutive_closes_below_ma6": int(consecutive),
                    "ma6": float(latest.ma6),
                }
                if consecutive >= 2:
                    action, execution, blocked = "STOP_EXIT_LONG", "next_trading_day_open", "long"
                    rationale.append(
                        "long stop triggered: two consecutive completed closes below MA6 after 0.75 ATR activation"
                    )
                else:
                    action = "HOLD_LONG"
                    rationale.append("long stop and bearish divergence not triggered")

    return {
        "status": "ok",
        "symbol": symbol,
        "period": "daily",
        "market_date": str(latest.datetime.date()),
        "position": position,
        "action": action,
        "execution": execution,
        "rationale": rationale,
        "blocked_direction_after_action": blocked,
        "market": {
            "close": float(latest.close),
            "ma6": float(latest.ma6),
            "ma20": float(latest.ma20),
            "atr14": float(latest.atr),
            "rsi14": float(latest.rsi),
            "long_signal": bool(latest.long_signal),
            "short_signal": bool(latest.short_signal),
            "bearish_divergence": bool(latest.bearish_divergence),
            "bullish_divergence": bool(latest.bullish_divergence),
        },
        "stop_state": stop_state,
        "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
        "cost_assumption_one_way": 0.0004,
        "validation_scope": "mature_backtest" if symbol == "P0" else "same_rule_calculation",
    }


def mark_execution_window(result: dict) -> None:
    if result.get("status") != "ok" or result.get("execution") != "next_trading_day_open":
        return
    signal_date = pd.Timestamp(result["market_date"])
    intended = signal_date + pd.offsets.BDay(1)
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    result["intended_execution_date"] = str(intended.date())
    open_has_passed = now.date() > intended.date() or (
        now.date() == intended.date() and now.time() >= time(9, 5)
    )
    if not open_has_passed:
        result["execution_window"] = "pending"
        return
    original = result["action"]
    result["original_confirmed_action"] = original
    if original.startswith("OPEN_"):
        result["action"] = "MISSED_ENTRY_SIGNAL"
        result["execution"] = "wait_for_next_confirmed_signal"
        result["rationale"].append("the strategy's next-open entry window has already passed; do not chase")
    else:
        result["action"] = "EXIT_SIGNAL_OVERDUE"
        result["execution"] = "next_available_market_opportunity"
        result["rationale"].append(
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
        )
    result["execution_window"] = "missed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, help="confirmed symbol, e.g. P0, P2609, Y2701, OI2609")
    parser.add_argument("--position", choices=["flat", "long", "short"], default="flat")
    parser.add_argument("--entry-date")
    parser.add_argument("--entry-price", type=float)
    parser.add_argument("--entry-atr", type=float)
    parser.add_argument("--highest-since-entry", type=float)
    parser.add_argument("--lowest-since-entry", type=float)
    parser.add_argument("--blocked-direction", choices=["none", "long", "short"], default="none")
    parser.add_argument("--allow-forming-bar", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        symbol, product, _ = normalize_symbol(args.symbol)
        raw, source = fetch(symbol)
        raw, provisional, bar_note = select_completed(raw, args.allow_forming_bar)
        data = indicators(raw)
        if len(data) < 40:
            raise RuntimeError("fewer than 40 usable daily bars")
        result = decide(data, args, symbol)
        mark_execution_window(result)
        result["product"] = product
        result["data_source"] = source
        result["data_rows"] = len(raw)
        result["bar_provisional"] = provisional
        result["bar_note"] = bar_note
        result["generated_at"] = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except Exception as exc:
        print(
            json.dumps(
                {"status": "error", "symbol": str(args.symbol).upper(), "message": str(exc)},
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()

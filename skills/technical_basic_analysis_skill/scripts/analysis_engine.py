#!/usr/bin/env python3
"""Technical/basic analysis engine for oil-futures contract cards."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def as_float(value: Any) -> float | None:
    try:
        if value in (None, "", "-"):
            return None
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_number(value: Any, digits: int = 2) -> str:
    number = as_float(value)
    if number is None:
        return "需进一步核验"
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.{digits}f}"


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def last(values: list[float | None]) -> float | None:
    for value in reversed(values):
        if value is not None:
            return value
    return None


def rolling_mean(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
        else:
            result.append(sum(values[index + 1 - window : index + 1]) / window)
    return result


def rolling_std(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
            continue
        sample = values[index + 1 - window : index + 1]
        mean = sum(sample) / window
        variance = sum((item - mean) ** 2 for item in sample) / window
        result.append(variance ** 0.5)
    return result


def rolling_max(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
        else:
            result.append(max(values[index + 1 - window : index + 1]))
    return result


def rolling_min(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
        else:
            result.append(min(values[index + 1 - window : index + 1]))
    return result


def ema(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(value * alpha + result[-1] * (1 - alpha))
    return result


def technical_analysis(price: float | None, history: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = history or []
    clean = [
        {
            "close": as_float(row.get("close")),
            "high": as_float(row.get("high")),
            "low": as_float(row.get("low")),
        }
        for row in rows
    ]
    clean = [row for row in clean if row["close"] is not None and row["high"] is not None and row["low"] is not None]
    if price is None or len(clean) < 80:
        return {
            "score": 50,
            "trend": "数据不足，按中性处理",
            "atr": None,
            "levels": {},
            "signals": ["技术数据不足"],
        }

    close = [float(row["close"]) for row in clean]
    high = [float(row["high"]) for row in clean]
    low = [float(row["low"]) for row in clean]
    close[-1] = price
    high[-1] = max(high[-1], price)
    low[-1] = min(low[-1], price)

    ma5 = last(rolling_mean(close, 5))
    ma10 = last(rolling_mean(close, 10))
    ma20 = last(rolling_mean(close, 20))
    ma60 = last(rolling_mean(close, 60))
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    dif = [a - b for a, b in zip(ema12, ema26)]
    dea = ema(dif, 9)
    macd_hist = last([a - b for a, b in zip(dif, dea)]) or 0

    deltas = [0.0] + [close[index] - close[index - 1] for index in range(1, len(close))]
    gains = [max(delta, 0) for delta in deltas]
    losses = [max(-delta, 0) for delta in deltas]
    avg_gain = last(rolling_mean(gains, 14))
    avg_loss = last(rolling_mean(losses, 14))
    rsi = None if avg_gain is None or avg_loss in (None, 0) else 100 - 100 / (1 + avg_gain / avg_loss)

    boll_std = last(rolling_std(close, 20))
    boll_upper = ma20 + 2 * boll_std if ma20 is not None and boll_std is not None else None
    boll_lower = ma20 - 2 * boll_std if ma20 is not None and boll_std is not None else None
    true_ranges = []
    for index, value in enumerate(close):
        previous_close = close[index - 1] if index > 0 else value
        true_ranges.append(max(high[index] - low[index], abs(high[index] - previous_close), abs(low[index] - previous_close)))
    atr = last(rolling_mean(true_ranges, 14)) or true_ranges[-1]
    high20 = last(rolling_max(high[:-1], 20))
    low20 = last(rolling_min(low[:-1], 20))
    high55 = last(rolling_max(high[:-1], 55))
    low55 = last(rolling_min(low[:-1], 55))

    score = 50.0
    signals: list[str] = []
    if ma20 is not None:
        if price > ma20:
            score += 8
            signals.append("价格在20日均线上方")
        else:
            score -= 8
            signals.append("价格在20日均线下方")
    if ma60 is not None:
        score += 7 if price > ma60 else -7
    if all(value is not None for value in [ma5, ma10, ma20, ma60]):
        if price > ma5 > ma10 > ma20 > ma60:
            score += 15
            signals.append("均线多头排列")
        elif price < ma5 < ma10 < ma20 < ma60:
            score -= 15
            signals.append("均线空头排列")
        elif price < ma5 and ma5 < ma20:
            score -= 8
            signals.append("短均线转弱")
        else:
            signals.append("均线结构震荡")
    score += 10 if macd_hist > 0 else -10
    if rsi is not None:
        if 50 <= rsi <= 68:
            score += 8
        elif 32 <= rsi < 50:
            score -= 4
        elif rsi > 75:
            score -= 5
            signals.append("RSI偏热")
        elif rsi < 30:
            score += 3
            signals.append("RSI超卖修复")
    if high20 is not None and price > high20:
        score += 12
        signals.append("突破20日唐奇安上轨")
    elif low20 is not None and price < low20:
        score -= 12
        signals.append("跌破20日唐奇安下轨")
    if boll_upper is not None and boll_lower is not None:
        if price > boll_upper:
            score += 5
            signals.append("突破布林上轨")
        elif price < boll_lower:
            score -= 5
            signals.append("跌破布林下轨")

    score = round(clamp(score, 20, 80), 1)
    trend = "偏多" if score >= 65 else "偏空" if score <= 40 else "震荡"
    return {
        "score": score,
        "trend": trend,
        "atr": atr,
        "levels": {
            "ma20": ma20,
            "ma60": ma60,
            "donchian20_high": high20,
            "donchian20_low": low20,
            "donchian55_high": high55,
            "donchian55_low": low55,
            "boll_upper": boll_upper,
            "boll_lower": boll_lower,
        },
        "signals": signals[:3],
    }


def fundamental_score(spec: dict[str, Any], snapshot: dict[str, Any] | None) -> tuple[float, str]:
    snapshot = snapshot or {}
    external = snapshot.get("external", {})
    fundamental = snapshot.get("fundamental", {})
    inventory = fundamental.get("inventory", {})
    spread = fundamental.get("spread", {})
    score = 50.0
    notes: list[str] = []

    cbot = as_float(external.get("cbot_bean_oil", {}).get("change_pct"))
    fcpo = as_float(external.get("bmd_palm_oil", {}).get("change_pct"))
    if spec.get("key") == "palm_oil":
        if fcpo is not None:
            score += max(-10, min(10, fcpo * 5))
            notes.append("FCPO联动")
        inv = as_float(inventory.get("palm_oil_inventory", {}).get("price"))
        if inv is not None and inv >= 65:
            score -= 6
            notes.append("棕榈油库存偏高")
        soy_palm_record = spread.get("soybean_palm_spread")
        soy_palm = as_float(soy_palm_record.get("price") if isinstance(soy_palm_record, dict) else soy_palm_record)
        if soy_palm is not None and soy_palm < 0:
            score += 4
            notes.append("豆棕价差仍支撑P相对强弱")
    elif spec.get("key") == "soybean_oil":
        if cbot is not None:
            score += max(-10, min(10, cbot * 5))
            notes.append("CBOT豆油联动")
        inv = as_float(inventory.get("soybean_oil_inventory", {}).get("price"))
        if inv is not None and inv >= 110:
            score -= 8
            notes.append("豆油库存压力")
    elif spec.get("key") == "rapeseed_oil":
        inv = as_float(inventory.get("rapeseed_oil_inventory", {}).get("price"))
        if inv is not None and inv >= 30:
            score -= 6
            notes.append("菜油库存压力")
        if cbot is not None and cbot > 0:
            score += 3
            notes.append("油脂板块共振")

    return round(clamp(score, 25, 75), 1), "；".join(notes) if notes else "基本面暂无强新增驱动"


def stance_for(score: float) -> str:
    if score >= 65:
        return "偏多"
    if score <= 40:
        return "偏空"
    return "震荡"


def strategy_levels(price: float | None, tech: dict[str, Any], trend: str) -> list[dict[str, str]]:
    if price is None:
        return []
    atr = as_float(tech.get("atr")) or max(price * 0.01, 1)
    levels = tech.get("levels", {})
    turtle_high = as_float(levels.get("donchian20_high"))
    turtle_low = as_float(levels.get("donchian20_low"))
    long_stop = price - 2 * atr
    short_stop = price + 2 * atr
    if trend == "偏多":
        atr_take = price + 3 * atr
        turtle_trigger = turtle_high or price + atr
        turtle_stop = turtle_trigger - 2 * atr
    elif trend == "偏空":
        atr_take = price - 3 * atr
        turtle_trigger = turtle_low or price - atr
        turtle_stop = turtle_trigger + 2 * atr
    else:
        upper = turtle_high or price + 1.5 * atr
        lower = turtle_low or price - 1.5 * atr
        return [
            {
                "name": "ATR区间",
                "entry": f"{fmt_number(lower)} - {fmt_number(upper)}",
                "take_profit": f"上沿 {fmt_number(upper)} / 下沿 {fmt_number(lower)}",
                "stop_loss": f"上破 {fmt_number(upper + atr)} 或下破 {fmt_number(lower - atr)}",
            },
            {
                "name": "海龟20日突破",
                "entry": f"上破 {fmt_number(upper)} 或下破 {fmt_number(lower)}",
                "take_profit": f"顺势 2ATR：{fmt_number(price + 2 * atr)} / {fmt_number(price - 2 * atr)}",
                "stop_loss": f"反向 1ATR：{fmt_number(price - atr)} / {fmt_number(price + atr)}",
            },
        ]

    return [
        {
            "name": "ATR趋势",
            "entry": f"现价附近 {fmt_number(price)}",
            "take_profit": fmt_number(atr_take),
            "stop_loss": fmt_number(long_stop if trend == "偏多" else short_stop),
        },
        {
            "name": "海龟20日突破",
            "entry": fmt_number(turtle_trigger),
            "take_profit": fmt_number(turtle_trigger + 2 * atr if trend == "偏多" else turtle_trigger - 2 * atr),
            "stop_loss": fmt_number(turtle_stop),
        },
    ]


def build_market_view(name: str, total_score: float, tech: dict[str, Any], fundamental_note: str) -> str:
    signals = "、".join(tech.get("signals") or [])
    trend = tech.get("trend", "震荡")
    if total_score >= 65:
        tone = "当前行情偏强，顺势思路优先"
    elif total_score <= 40:
        tone = "当前行情偏弱，反弹压力优先"
    else:
        tone = "当前行情偏震荡，等待突破确认"
    detail = f"技术面显示{trend}"
    if signals:
        detail += f"（{signals}）"
    return f"{name}{tone}；{detail}。基本面：{fundamental_note}。"


def analyze_contract(item: dict[str, Any]) -> dict[str, Any]:
    spec = item.get("spec", {})
    source = item.get("source", {})
    snapshot = item.get("snapshot")
    price = as_float(source.get("price"))
    history = item.get("history")
    if item.get("external"):
        change_pct = as_float(source.get("change_pct"))
        technical = 58 if change_pct and change_pct > 0 else 42 if change_pct and change_pct < 0 else 50
        fundamental = 50.0
        total_score = round(technical * 0.7 + fundamental * 0.3, 1)
        stance = stance_for(total_score)
        high = as_float(source.get("high")) or price or 0
        low = as_float(source.get("low")) or price or 0
        tech = {
            "atr": abs(high - low) or ((price or 1) * 0.01),
            "trend": stance,
            "levels": {},
            "signals": ["外盘参考合约，技术历史样本不足"],
        }
        view = f"{spec.get('name', '')}作为外盘参考，当前按{stance}处理；主要用于判断内盘油脂情绪传导，不单独作为交易指令。"
    else:
        tech = technical_analysis(price, history)
        fundamental, fundamental_note = fundamental_score(spec, snapshot)
        technical = as_float(tech.get("score")) or 50.0
        total_score = round(clamp(technical * 0.7 + fundamental * 0.3), 1)
        stance = stance_for(total_score)
        view = build_market_view(str(spec.get("name", "")), total_score, tech, fundamental_note)

    return {
        "score": {
            "total": total_score,
            "technical": technical,
            "fundamental": fundamental,
            "stance": stance,
            "weights": "技术面70% / 基本面30%",
        },
        "view": view,
        "strategies": strategy_levels(price, tech, stance),
        "skill_trace": {
            "skill": "technical_basic_analysis_skill",
            "technical_function": "technical_analysis",
            "fundamental_function": "fundamental_score",
            "strategy_function": "strategy_levels",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON file. Reads stdin when omitted.")
    args = parser.parse_args()
    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    payload = json.loads(raw)
    result = [analyze_contract(item) for item in payload] if isinstance(payload, list) else analyze_contract(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

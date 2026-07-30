#!/usr/bin/env python3
"""Dependency-light indicator runtime shared by macOS and Linux collectors."""

from __future__ import annotations

from math import sqrt
from typing import Any


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _ema(values: list[float | None], span: int) -> list[float | None]:
    alpha = 2 / (span + 1)
    previous: float | None = None
    output: list[float | None] = []
    for value in values:
        if value is None:
            output.append(None if previous is None else previous)
            continue
        previous = value if previous is None else value * alpha + previous * (1 - alpha)
        output.append(previous)
    return output


def _rolling(
    values: list[float],
    period: int,
    reducer: Any,
) -> list[float | None]:
    return [
        None if index + 1 < period else reducer(values[index + 1 - period : index + 1])
        for index in range(len(values))
    ]


def calculate_ma(
    prices: list[float],
    periods: list[int] | None = None,
) -> dict[str, float | None]:
    selected = periods or [5, 10, 20, 60]
    return {
        f"ma{period}": _mean(prices[-period:]) if len(prices) >= period else None
        for period in selected
    }


def calculate_ema(
    prices: list[float],
    periods: list[int] | None = None,
) -> dict[str, float | None]:
    selected = periods or [12, 26]
    return {
        f"ema{period}": _ema([float(item) for item in prices], period)[-1]
        if prices
        else None
        for period in selected
    }


def calculate_macd(
    prices: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict[str, float | None]:
    if not prices:
        return {"dif": None, "dea": None, "histogram": None}
    values = [float(item) for item in prices]
    fast_values = _ema(values, fast)
    slow_values = _ema(values, slow)
    dif_values = [
        float(fast_value) - float(slow_value)
        for fast_value, slow_value in zip(fast_values, slow_values)
    ]
    dea_values = _ema(dif_values, signal)
    dif = dif_values[-1]
    dea = dea_values[-1]
    return {
        "dif": dif,
        "dea": dea,
        "histogram": dif - float(dea) if dea is not None else None,
    }


def calculate_rsi(
    prices: list[float],
    periods: list[int] | None = None,
) -> dict[str, float | None]:
    selected = periods or [6, 12, 24]
    if not prices:
        return {f"rsi{period}": None for period in selected}
    deltas = [0.0] + [
        float(prices[index]) - float(prices[index - 1])
        for index in range(1, len(prices))
    ]
    gains = [max(value, 0.0) for value in deltas]
    losses = [max(-value, 0.0) for value in deltas]
    result: dict[str, float | None] = {}
    for period in selected:
        if len(prices) < period:
            result[f"rsi{period}"] = None
            continue
        average_gain = _mean(gains[-period:])
        average_loss = _mean(losses[-period:])
        result[f"rsi{period}"] = (
            100.0
            if average_loss == 0
            else 100 - 100 / (1 + average_gain / average_loss)
        )
    return result


def calculate_kdj(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    n: int = 9,
    m1: int = 3,
    m2: int = 3,
) -> dict[str, float | None]:
    if not closes:
        return {"k": None, "d": None, "j": None}
    lowest = _rolling([float(item) for item in lows], n, min)
    highest = _rolling([float(item) for item in highs], n, max)
    rsv: list[float | None] = []
    for close, low, high in zip(closes, lowest, highest):
        if low is None or high is None:
            rsv.append(None)
        elif high == low:
            rsv.append(0.0)
        else:
            rsv.append((float(close) - low) / (high - low) * 100)
    k_values = _ema(rsv, m1)
    d_values = _ema(k_values, m2)
    k, d = k_values[-1], d_values[-1]
    return {
        "k": k,
        "d": d,
        "j": 3 * float(k) - 2 * float(d) if k is not None and d is not None else None,
    }


def calculate_boll(
    prices: list[float],
    period: int = 20,
    std_dev: float = 2.0,
) -> dict[str, float | None]:
    if len(prices) < period:
        return {"upper": None, "middle": None, "lower": None}
    sample = [float(item) for item in prices[-period:]]
    middle = _mean(sample)
    standard_deviation = sqrt(
        sum((item - middle) ** 2 for item in sample) / (period - 1)
    )
    return {
        "upper": middle + std_dev * standard_deviation,
        "middle": middle,
        "lower": middle - std_dev * standard_deviation,
    }


def calculate_atr(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 14,
) -> float | None:
    if not closes:
        return None
    true_ranges = []
    for index, (high, low) in enumerate(zip(highs, lows)):
        previous_close = float(closes[index - 1]) if index else float(closes[index])
        true_ranges.append(
            max(
                float(high) - float(low),
                abs(float(high) - previous_close),
                abs(float(low) - previous_close),
            )
        )
    return _mean(true_ranges[-period:]) if len(true_ranges) >= period else None


def find_local_extremes(
    prices: list[float],
    window: int = 10,
) -> list[tuple[int, str, float]]:
    extremes: list[tuple[int, str, float]] = []
    for index in range(window, len(prices) - window):
        peers = [
            prices[position]
            for position in range(index - window, index + window + 1)
            if position != index
        ]
        if all(prices[index] >= value for value in peers):
            extremes.append((index, "high", prices[index]))
        if all(prices[index] <= value for value in peers):
            extremes.append((index, "low", prices[index]))
    return extremes


def calculate_fibonacci_levels(high: float, low: float) -> dict[str, float]:
    difference = high - low
    return {
        "0%": high,
        "23.6%": high - difference * 0.236,
        "38.2%": high - difference * 0.382,
        "50%": high - difference * 0.5,
        "61.8%": high - difference * 0.618,
        "78.6%": high - difference * 0.786,
        "100%": low,
    }


def _cluster_prices(
    values: list[tuple[int, float]],
    tolerance: float = 0.02,
) -> list[dict[str, Any]]:
    if not values:
        return []
    sorted_values = sorted(values, key=lambda item: item[1])
    current = {
        "price": sorted_values[0][1],
        "touches": 1,
        "last_touch_index": sorted_values[0][0],
    }
    clusters: list[dict[str, Any]] = []
    for index, (_, price) in enumerate(sorted_values[1:], 1):
        if abs(price - current["price"]) / current["price"] < tolerance:
            current["touches"] += 1
            current["last_touch_index"] = sorted_values[index][0]
        else:
            if current["touches"] >= 2:
                clusters.append(current)
            current = {
                "price": price,
                "touches": 1,
                "last_touch_index": sorted_values[index][0],
            }
    if current["touches"] >= 2:
        clusters.append(current)
    return sorted(clusters, key=lambda item: item["price"], reverse=True)


def identify_support_resistance(
    prices: list[float],
    highs: list[float],
    lows: list[float],
    lookback: int = 60,
) -> dict[str, Any]:
    recent_prices = prices[-lookback:]
    extremes = find_local_extremes(recent_prices, window=5)
    resistance = _cluster_prices(
        [(index, price) for index, kind, price in extremes if kind == "high"]
    )
    support = _cluster_prices(
        [(index, price) for index, kind, price in extremes if kind == "low"]
    )
    local_highs = [price for _, kind, price in extremes if kind == "high"]
    local_lows = [price for _, kind, price in extremes if kind == "low"]
    fibonacci = (
        calculate_fibonacci_levels(max(local_highs), min(local_lows))
        if local_highs and local_lows
        else {}
    )
    current = float(prices[-1])
    nearest_resistance = next(
        (item for item in resistance if item["price"] >= current),
        None,
    )
    nearest_support = next(
        (item for item in reversed(support) if item["price"] <= current),
        None,
    )
    return {
        "resistance_levels": resistance[:5],
        "support_levels": support[:5],
        "fibonacci": fibonacci,
        "nearest_resistance": nearest_resistance,
        "nearest_support": nearest_support,
        "current_price": current,
    }

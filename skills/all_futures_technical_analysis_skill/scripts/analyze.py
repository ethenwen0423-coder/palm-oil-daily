#!/usr/bin/env python3
"""Dependency-light technical skill runtime for a selected futures contract."""

from __future__ import annotations

import math
from typing import Any


SKILL_NAME = "all_futures_technical_analysis_skill"


def _round(value: float | None, digits: int = 2) -> float | None:
    return round(value, digits) if value is not None and math.isfinite(value) else None


def _ema(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    output = [values[0]]
    for value in values[1:]:
        output.append(value * alpha + output[-1] * (1 - alpha))
    return output


def _rsi(values: list[float], window: int) -> float | None:
    if len(values) <= window:
        return None
    changes = [values[index] - values[index - 1] for index in range(1, len(values))]
    gains = [max(change, 0) for change in changes[-window:]]
    losses = [max(-change, 0) for change in changes[-window:]]
    average_gain = sum(gains) / window
    average_loss = sum(losses) / window
    return 100.0 if average_loss == 0 else 100 - 100 / (1 + average_gain / average_loss)


def _kdj(highs: list[float], lows: list[float], closes: list[float], window: int = 9) -> tuple[float, float, float]:
    k = d = 50.0
    for index in range(len(closes)):
        start = max(0, index + 1 - window)
        high, low = max(highs[start : index + 1]), min(lows[start : index + 1])
        rsv = 50.0 if high == low else (closes[index] - low) / (high - low) * 100
        k = k * 2 / 3 + rsv / 3
        d = d * 2 / 3 + k / 3
    return k, d, 3 * k - 2 * d


def analyze(symbol: str, history: list[dict[str, Any]], price: float | None) -> dict[str, Any]:
    clean = []
    for row in history:
        try:
            values = tuple(float(row[key]) for key in ("open", "high", "low", "close"))
        except (KeyError, TypeError, ValueError):
            continue
        if all(math.isfinite(value) for value in values):
            clean.append(dict(zip(("open", "high", "low", "close"), values)))
    if len(clean) < 60 or price is None or not math.isfinite(float(price)):
        return {
            "skill": SKILL_NAME,
            "status": "insufficient",
            "trend": "样本不足",
            "summary": "所选合约有效日线不足 60 条，技术分析 skill 暂不输出方向状态。",
            "indicators": {},
            "levels": {},
            "details": [],
        }

    closes = [row["close"] for row in clean]
    highs = [row["high"] for row in clean]
    lows = [row["low"] for row in clean]
    closes[-1] = float(price)
    highs[-1] = max(highs[-1], float(price))
    lows[-1] = min(lows[-1], float(price))
    ma20 = sum(closes[-20:]) / 20
    ma60 = sum(closes[-60:]) / 60
    ema12, ema26 = _ema(closes, 12), _ema(closes, 26)
    dif_series = [fast - slow for fast, slow in zip(ema12, ema26)]
    dea = _ema(dif_series, 9)[-1]
    macd = dif_series[-1] - dea
    rsi14 = _rsi(closes, 14)
    k, d, j = _kdj(highs, lows, closes)
    middle = ma20
    std = (sum((value - middle) ** 2 for value in closes[-20:]) / 20) ** 0.5
    true_ranges = []
    for index, (high, low) in enumerate(zip(highs, lows)):
        previous = closes[index - 1] if index else closes[index]
        true_ranges.append(max(high - low, abs(high - previous), abs(low - previous)))
    atr14 = sum(true_ranges[-14:]) / 14
    support, resistance = min(lows[-20:]), max(highs[-20:])
    if float(price) > ma20 > ma60:
        status, trend = "bullish", "偏强"
    elif float(price) < ma20 < ma60:
        status, trend = "bearish", "偏弱"
    else:
        status, trend = "neutral", "震荡"
    return {
        "skill": SKILL_NAME,
        "status": status,
        "trend": trend,
        "summary": f"{symbol} 最新价相对 MA20/MA60 呈{trend}结构；RSI14 为 {rsi14:.1f}，MACD 柱为 {macd:+.2f}。",
        "indicators": {
            "MA20": _round(ma20), "MA60": _round(ma60), "RSI14": _round(rsi14),
            "MACD": _round(macd), "KDJ_J": _round(j), "BOLL上轨": _round(middle + 2 * std),
            "BOLL下轨": _round(middle - 2 * std), "ATR14": _round(atr14),
        },
        "levels": {"20日支撑": _round(support), "20日压力": _round(resistance)},
        "details": [
            {"title": "价格结构", "text": f"最新价 {float(price):g}，MA20 {_round(ma20)}，MA60 {_round(ma60)}。"},
            {"title": "动量与波动", "text": f"KDJ K/D/J 为 {_round(k)}/{_round(d)}/{_round(j)}，ATR14 为 {_round(atr14)}。"},
            {"title": "使用边界", "text": "技术面只描述价格状态，不能脱离基本面独立决定综合方向。"},
        ],
    }


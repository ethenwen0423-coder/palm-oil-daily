#!/usr/bin/env python3
"""Score oil-futures contracts with 30% basic and 70% technical weights."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def clamp_score(value: Any) -> float:
    score = float(value)
    if score < 0 or score > 100:
        raise ValueError(f"score out of range 0-100: {value}")
    return score


def weighted_score(basic_score: float, technical_score: float) -> float:
    return round(basic_score * 0.30 + technical_score * 0.70, 1)


def rating_for(score: float) -> str:
    if score >= 75:
        return "强势"
    if score >= 60:
        return "偏强"
    if score >= 45:
        return "中性"
    if score >= 30:
        return "偏弱"
    return "弱势"


def direction_for(score: float) -> str:
    if score >= 60:
        return "↑"
    if score < 45:
        return "↓"
    return "→"


def strategy_for(score: float, data_quality: str) -> str:
    if data_quality == "low":
        return "观望"
    if score >= 75:
        return "偏多"
    if score >= 45:
        return "震荡"
    return "偏空"


def position_size_for(score: float, data_quality: str, diverged: bool) -> str:
    if data_quality == "low":
        return "0%"
    if score >= 75:
        size = "30%-40%"
    elif score >= 60:
        size = "10%-20%"
    elif score >= 45:
        size = "0%-10%"
    else:
        size = "0%"
    if diverged and size == "30%-40%":
        return "10%-20%"
    if diverged and size == "10%-20%":
        return "0%-10%"
    return size


def risk_control_for(item: dict[str, Any], score: float, technical_score: float) -> str:
    support = item.get("support")
    resistance = item.get("resistance")
    price = item.get("price")
    if not support or not resistance:
        return "关键位需进一步核验"
    if score >= 75:
        return f"跌破 {support} 降低多头暴露；接近 {resistance} 不追高"
    if score >= 45:
        return f"围绕 {support}-{resistance} 区间处理，突破后再确认"
    if technical_score < 45:
        return f"反抽不过 {resistance} 维持防守，重新站上压力位再修正"
    if price:
        return f"当前 {price} 附近先控仓，等待方向确认"
    return "先控仓，等待方向确认"


def invalidation_for(item: dict[str, Any], score: float) -> str:
    support = item.get("support")
    resistance = item.get("resistance")
    if score >= 60 and support:
        return f"跌破 {support}"
    if score < 45 and resistance:
        return f"站回 {resistance}"
    return "关键位需进一步核验"


def calculate(item: dict[str, Any]) -> dict[str, Any]:
    basic_score = clamp_score(item["basic_score"])
    technical_score = clamp_score(item["technical_score"])
    data_quality = str(item.get("data_quality", "medium")).lower()
    if data_quality not in {"high", "medium", "low"}:
        data_quality = "medium"
    score = weighted_score(basic_score, technical_score)
    diverged = abs(basic_score - technical_score) > 25
    return {
        **item,
        "basic_score": basic_score,
        "technical_score": technical_score,
        "total_score": score,
        "rating": rating_for(score),
        "strategy": strategy_for(score, data_quality),
        "direction": direction_for(score),
        "position_size": position_size_for(score, data_quality, diverged),
        "risk_control": risk_control_for(item, score, technical_score),
        "invalidation": invalidation_for(item, score),
        "score_divergence_warning": diverged,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON file. Reads stdin when omitted.")
    args = parser.parse_args()

    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    payload = json.loads(raw)
    if isinstance(payload, list):
        result = [calculate(item) for item in payload]
    else:
        result = calculate(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

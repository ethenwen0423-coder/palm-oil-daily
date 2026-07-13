#!/usr/bin/env python3
"""Technical/basic analysis engine for oil-futures contract cards."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
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


def parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if len(text) == 10 and text[4] == "-":
            return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def snapshot_time(snapshot: dict[str, Any] | None) -> datetime | None:
    snapshot = snapshot or {}
    return parse_dt(snapshot.get("timestamp") or snapshot.get("date"))


def record_time(record: Any) -> datetime | None:
    if not isinstance(record, dict):
        return None
    return parse_dt(record.get("published_at") or record.get("fetched_at") or record.get("date"))


def is_fresh(record: Any, snapshot: dict[str, Any] | None, hours: int = 24) -> bool:
    when = record_time(record)
    base = snapshot_time(snapshot) or datetime.now(timezone.utc)
    if when is None:
        return False
    return 0 <= (base - when).total_seconds() <= hours * 3600


def is_verified(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    if record.get("status") not in (None, "ok"):
        return False
    source = str(record.get("source") or "").lower()
    summary = str(record.get("summary") or "")
    if any(word in source for word in ["rumor", "传闻", "anonymous"]):
        return False
    if any(word in summary for word in ["传闻", "据传", "未确认", "无法确认", "匿名"]):
        return False
    return True


def score_from_change(change: float | None, multiplier: float = 4.0, limit: float = 12.0) -> float:
    if change is None:
        return 0.0
    return max(-limit, min(limit, change * multiplier))


def direction_bucket(score: float, bullish: float = 55, bearish: float = 45) -> str:
    if score >= bullish:
        return "up"
    if score <= bearish:
        return "down"
    return "flat"


def pct_text(value: float | None) -> str:
    if value is None:
        return "需进一步核验"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def score_reading(score: Any) -> str:
    value = as_float(score)
    if value is None:
        return "数据需进一步核验"
    if value >= 65:
        return "偏强"
    if value <= 40:
        return "偏弱"
    if value >= 55:
        return "中性略强"
    if value <= 45:
        return "中性略弱"
    return "中性"


def unique_phrases(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = str(item).strip(" ；。")
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def readable_note(note: str) -> str:
    parts = unique_phrases([part for part in str(note or "").split("；")])
    if not parts:
        return "暂无足够强的新增基本面变量"
    if len(parts) == 1:
        return parts[0]
    return "；".join(parts[:3])


def sentence(text: str) -> str:
    clean = str(text or "").strip()
    if not clean:
        return ""
    return clean if clean.endswith(("。", "！", "？")) else f"{clean}。"


def trend_reading(trend: str) -> str:
    if trend == "偏多":
        return "价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性"
    if trend == "偏空":
        return "价格对均线支撑的依赖减弱，下方区间有效性需要继续观察"
    return "价格仍在区间内反复，技术面更多说明节奏而不是方向结论"


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
            score += 12
            signals.append("均线多头排列")
        elif price < ma5 < ma10 < ma20 < ma60:
            score -= 12
            signals.append("均线空头排列")
        elif price < ma5 and ma5 < ma20:
            score -= 6
            signals.append("短均线转弱")
        else:
            signals.append("均线结构震荡")
    if high20 is not None and price > high20:
        score += 10
        signals.append("突破20日区间上沿")
    elif low20 is not None and price < low20:
        score -= 10
        signals.append("跌破20日区间下沿")
    if boll_upper is not None and boll_lower is not None:
        if price > boll_upper:
            score += 3
            signals.append("处于统计区间上沿外侧")
        elif price < boll_lower:
            score -= 3
            signals.append("处于统计区间下沿外侧")
    if atr and price:
        range_width = (high20 - low20) if high20 is not None and low20 is not None else None
        if range_width and range_width > 0:
            atr_ratio = atr / range_width
            if atr_ratio > 0.45:
                signals.append("波动放大，单一技术信号可靠性下降")
            elif atr_ratio < 0.18:
                signals.append("区间波动收敛，等待方向确认")

    score = round(clamp(score, 25, 75), 1)
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
    fundamental = snapshot.get("fundamental", {})
    inventory = fundamental.get("inventory", {})
    spread = fundamental.get("spread", {})
    score = 50.0
    notes: list[str] = []

    if spec.get("key") == "palm_oil":
        inv_record = inventory.get("palm_oil_inventory", {})
        inv = as_float(inv_record.get("price"))
        if inv is not None:
            if is_fresh(inv_record, snapshot) and inv >= 65:
                score -= 3
                notes.append("棕榈油库存偏高但仅作背景压力")
            elif inv >= 65:
                notes.append("棕榈油库存偏高，非24小时新增，只作背景")
        soy_palm_record = spread.get("soybean_palm_spread")
        soy_palm = as_float(soy_palm_record.get("price") if isinstance(soy_palm_record, dict) else soy_palm_record)
        if soy_palm is not None:
            notes.append("豆棕价差用于相对强弱背景")
    elif spec.get("key") == "soybean_oil":
        inv_record = inventory.get("soybean_oil_inventory", {})
        inv = as_float(inv_record.get("price"))
        if inv is not None:
            if is_fresh(inv_record, snapshot) and inv >= 110:
                score -= 3
                notes.append("豆油库存压力但仅作背景压力")
            elif inv >= 110:
                notes.append("豆油库存压力，非24小时新增，只作背景")
    elif spec.get("key") == "rapeseed_oil":
        inv_record = inventory.get("rapeseed_oil_inventory", {})
        inv = as_float(inv_record.get("price"))
        if inv is not None:
            if is_fresh(inv_record, snapshot) and inv >= 30:
                score -= 3
                notes.append("菜油库存压力但仅作背景压力")
            elif inv >= 30:
                notes.append("菜油库存压力，非24小时新增，只作背景")
        notes.append("菜油基本面更多看油脂内部轮动")

    return round(clamp(score, 25, 75), 1), "；".join(notes) if notes else "基本面暂无强新增驱动"


def driver_score(snapshot: dict[str, Any] | None, spec: dict[str, Any]) -> tuple[float, str, list[str]]:
    snapshot = snapshot or {}
    external = snapshot.get("external", {})
    cross = snapshot.get("fundamental", {}).get("cross_drivers", {})
    key = spec.get("key")
    score = 50.0
    notes: list[str] = []
    warnings: list[str] = []

    def add_change(record: dict[str, Any], label: str, multiplier: float, limit: float) -> None:
        nonlocal score
        if not is_verified(record):
            warnings.append(f"{label}无法核验，不计入驱动评分")
            return
        change = as_float(record.get("change_pct"))
        if change is None:
            notes.append(f"{label}缺少涨跌幅，按中性处理")
            return
        fresh = is_fresh(record, snapshot)
        weight = 1.0 if fresh else 0.35
        score += score_from_change(change, multiplier=multiplier * weight, limit=limit * weight)
        suffix = "24小时新增" if fresh else "非24小时新增，降权"
        notes.append(f"{label}{pct_text(change)}（{suffix}）")

    add_change(external.get("bmd_palm_oil", {}), "FCPO", 5.0 if key == "palm_oil" else 3.0, 14.0)
    add_change(external.get("cbot_bean_oil", {}), "CBOT豆油", 5.0 if key == "soybean_oil" else 3.5, 12.0)
    add_change(external.get("cbot_soybean", {}), "美豆", 2.2 if key == "soybean_oil" else 1.2, 7.0)
    add_change(cross.get("crude_oil", {}), "WTI/Brent原油", 3.0, 10.0)

    weather = cross.get("weather", {})
    if is_verified(weather) and is_fresh(weather, snapshot):
        summary = str(weather.get("summary") or "")
        if any(word in summary for word in ["极端", "干旱", "洪涝", "高温", "暴雨"]):
            score += 5
            notes.append("天气出现24小时内可核验扰动")
        else:
            notes.append("天气24小时内更新但暂无极端信号")
    elif weather:
        notes.append("天气非24小时新增或无法核验，不加分")

    for ship_key in ("shipping", "export", "shipment", "vessel", "ship"):
        record = cross.get(ship_key) or snapshot.get("fundamental", {}).get(ship_key)
        if isinstance(record, dict):
            if is_verified(record) and is_fresh(record, snapshot):
                score += score_from_change(as_float(record.get("change_pct")), multiplier=3.0, limit=8.0)
                notes.append(f"船运/出口24小时内更新：{record.get('summary') or record.get('name') or ship_key}")
            else:
                notes.append("船运/出口信息非24小时新增或无法核验，只作背景")

    policy = cross.get("policy_trade", {})
    if isinstance(policy, dict):
        if is_verified(policy) and is_fresh(policy, snapshot):
            summary = str(policy.get("summary") or "")
            if any(word in summary for word in ["新增", "落地", "上调", "下调", "批准", "限制", "关税"]):
                score += 5 if key == "palm_oil" else 2
                notes.append("当日新增政策/新闻纳入驱动")
            else:
                notes.append("政策/新闻为24小时内更新，但未形成明确新增驱动")
        else:
            notes.append("旧政策、旧研报只作背景")

    inventory = snapshot.get("fundamental", {}).get("inventory", {})
    if inventory:
        notes.append("周度库存不作为今日主驱动")

    return round(clamp(score, 20, 80), 1), "；".join(notes) if notes else "今日新增驱动不足，按中性处理", warnings


def money_flow_score(source: dict[str, Any], snapshot: dict[str, Any] | None, spec: dict[str, Any]) -> tuple[float, str]:
    snapshot = snapshot or {}
    previous = snapshot.get("previous_snapshot") or {}
    current_domestic = snapshot.get("domestic", {})
    previous_domestic = previous.get("domestic", {}) if isinstance(previous, dict) else {}
    key = spec.get("key")
    score = 50.0
    notes: list[str] = []

    change = as_float(source.get("change_pct"))
    score += score_from_change(change, multiplier=4.0, limit=12.0)
    notes.append(f"当日涨跌幅{pct_text(change)}")

    current_volume = as_float(source.get("volume"))
    current_oi = as_float(source.get("open_interest"))
    previous_record = previous_domestic.get(key, {}) if isinstance(previous_domestic, dict) else {}
    previous_volume = as_float(previous_record.get("volume"))
    previous_oi = as_float(previous_record.get("open_interest"))
    if current_volume is not None and previous_volume:
        volume_change = (current_volume - previous_volume) / previous_volume * 100
        score += score_from_change(volume_change, multiplier=0.7, limit=7.0)
        notes.append(f"成交量较前快照{pct_text(volume_change)}")
    else:
        notes.append("成交量变化需进一步核验")
    if current_oi is not None and previous_oi:
        oi_change = (current_oi - previous_oi) / previous_oi * 100
        change_sign = 1 if (change or 0) >= 0 else -1
        score += score_from_change(oi_change * change_sign, multiplier=0.9, limit=7.0)
        notes.append(f"持仓较前快照{pct_text(oi_change)}")
    else:
        notes.append("持仓变化需进一步核验")

    domestic_changes: list[tuple[str, float]] = []
    for item_key, record in current_domestic.items():
        value = as_float(record.get("change_pct")) if isinstance(record, dict) else None
        if value is not None:
            domestic_changes.append((item_key, value))
    if domestic_changes:
        domestic_changes.sort(key=lambda item: item[1], reverse=True)
        rank = [item_key for item_key, _ in domestic_changes].index(key) + 1 if key in [item_key for item_key, _ in domestic_changes] else None
        if rank == 1:
            score += 5
        elif rank == len(domestic_changes):
            score -= 5
        rank_text = " > ".join(item_key for item_key, _ in domestic_changes)
        notes.append(f"板块强弱排序 {rank_text}")

    spread = snapshot.get("fundamental", {}).get("spread", {})
    prev_spread = previous.get("fundamental", {}).get("spread", {}) if isinstance(previous, dict) else {}
    for spread_key in ("soybean_palm_spread", "rapeseed_soybean_spread", "rapeseed_palm_spread"):
        record = spread.get(spread_key, {})
        prev_record = prev_spread.get(spread_key, {})
        current_value = as_float(record.get("price") if isinstance(record, dict) else record)
        previous_value = as_float(prev_record.get("price") if isinstance(prev_record, dict) else prev_record)
        if current_value is not None and previous_value is not None:
            diff = current_value - previous_value
            if key == "palm_oil" and spread_key == "soybean_palm_spread":
                score += -3 if diff > 0 else 3 if diff < 0 else 0
            elif key == "soybean_oil" and spread_key == "soybean_palm_spread":
                score += 3 if diff > 0 else -3 if diff < 0 else 0
            notes.append(f"{spread_key}变化 {fmt_number(diff)}")

    return round(clamp(score, 20, 80), 1), "；".join(notes)


def source_change(snapshot: dict[str, Any] | None, key: str) -> str:
    record = (snapshot or {}).get("external", {}).get(key, {})
    change = as_float(record.get("change_pct"))
    if change is None:
        return "需进一步核验"
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.2f}%"


def nested_price(snapshot: dict[str, Any] | None, section: str, key: str) -> str:
    record = (snapshot or {}).get("fundamental", {}).get(section, {}).get(key)
    if isinstance(record, dict):
        return fmt_number(record.get("price"))
    return fmt_number(record)


def build_technical_detail(price: float | None, tech: dict[str, Any], total_score: float) -> list[dict[str, str]]:
    levels = tech.get("levels", {})
    signal_items = unique_phrases([str(item) for item in tech.get("signals") or []])
    signals = "、".join(signal_items) if signal_items else "暂无明确技术信号"
    ma20 = fmt_number(levels.get("ma20"))
    ma60 = fmt_number(levels.get("ma60"))
    high20 = fmt_number(levels.get("donchian20_high"))
    low20 = fmt_number(levels.get("donchian20_low"))
    boll_upper = fmt_number(levels.get("boll_upper"))
    boll_lower = fmt_number(levels.get("boll_lower"))
    atr = fmt_number(tech.get("atr"))
    trend = tech.get("trend", "震荡")
    price_text = fmt_number(price)
    if price is None:
        position = "最新价缺失，无法判断价格相对均线和区间的位置，技术结构需进一步核验。"
    else:
        position = (
            f"现价 {price_text} 先看与 MA20 {ma20}、MA60 {ma60} 的相对位置，"
            f"技术评分 {fmt_number(tech.get('score'))}，读数为{score_reading(tech.get('score'))}。"
            f"{trend_reading(str(trend))}；主要信号是：{signals}。"
        )
    return [
        {
            "title": "价格位置",
            "text": position,
        },
        {
            "title": "关键区间",
            "text": (
                f"上方先观察20日区间上沿 {high20} 和统计通道上轨 {boll_upper}，"
                f"下方关注20日区间下沿 {low20} 和统计通道下轨 {boll_lower}。"
                "这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
            ),
        },
        {
            "title": "波动节奏",
            "text": (
                f"14日平均波动幅度约 {atr}，说明观察位需要给盘中噪音留出空间。"
                f"综合评分 {fmt_number(total_score)} 来自技术、基本面、驱动和资金共同作用，"
                "技术面只负责描述位置和节奏，不能单独决定总观点。"
            ),
        },
    ]


def build_fundamental_detail(spec: dict[str, Any], snapshot: dict[str, Any] | None, note: str, score: float) -> list[dict[str, str]]:
    key = spec.get("key")
    fcpo_change = source_change(snapshot, "bmd_palm_oil")
    cbot_change = source_change(snapshot, "cbot_bean_oil")
    palm_inventory = nested_price(snapshot, "inventory", "palm_oil_inventory")
    soybean_inventory = nested_price(snapshot, "inventory", "soybean_oil_inventory")
    rapeseed_inventory = nested_price(snapshot, "inventory", "rapeseed_oil_inventory")
    soy_palm_spread = nested_price(snapshot, "spread", "soybean_palm_spread")
    if key == "palm_oil":
        inventory_text = (
            f"国内背景看两点：棕榈油库存 {palm_inventory}，豆棕价差 {soy_palm_spread}。"
            "库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        )
        linkage_text = (
            f"P的外盘弹性主要来自FCPO（{fcpo_change}），CBOT豆油（{cbot_change}）决定油脂板块共振强度。"
            "两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        )
    elif key == "soybean_oil":
        inventory_text = (
            f"国内背景看豆油库存 {soybean_inventory} 和豆棕价差 {soy_palm_spread}。"
            "库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        )
        linkage_text = (
            f"Y首先锚定CBOT豆油（{cbot_change}），同时受FCPO（{fcpo_change}）影响油脂整体风险偏好。"
            "如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        )
    elif key == "rapeseed_oil":
        inventory_text = (
            f"菜油库存 {rapeseed_inventory}，豆棕价差 {soy_palm_spread}。"
            "OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        )
        linkage_text = (
            f"OI没有单一外盘锚，更多看CBOT豆油（{cbot_change}）和FCPO（{fcpo_change}）共同带来的板块方向。"
            "外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        )
    else:
        inventory_text = "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        linkage_text = f"外盘涨跌幅主要用于观察情绪传导：FCPO {fcpo_change}，CBOT豆油 {cbot_change}。"
    return [
        {
            "title": "外盘联动",
            "text": linkage_text,
        },
        {
            "title": "库存与价差",
            "text": inventory_text,
        },
        {
            "title": "评分解释",
            "text": (
                f"基本面评分 {fmt_number(score)}，读数为{score_reading(score)}。"
                f"本轮可核验依据是：{readable_note(note)}。"
                "库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
            ),
        },
    ]


def stance_for(
    total_score: float,
    technical: float,
    fundamental: float,
    driver: float,
    money_flow: float,
) -> str:
    driver_dir = direction_bucket(driver)
    money_dir = direction_bucket(money_flow)
    technical_dir = direction_bucket(technical)
    fundamental_dir = direction_bucket(fundamental)

    if driver_dir == money_dir and driver_dir == "up":
        return "震荡偏强" if technical_dir == "down" else "偏多" if total_score >= 62 else "震荡偏强"
    if driver_dir == money_dir and driver_dir == "down":
        return "震荡偏弱" if technical_dir == "up" else "偏空" if total_score <= 38 else "震荡偏弱"
    directional = {driver_dir, money_dir, technical_dir, fundamental_dir}
    if "up" in directional and "down" in directional and len(directional) >= 3:
        return "分歧震荡"
    if total_score >= 62:
        return "震荡偏强" if technical_dir != driver_dir else "偏多"
    if total_score <= 38:
        return "震荡偏弱" if technical_dir != driver_dir else "偏空"
    return "震荡"


def view_confidence(
    snapshot: dict[str, Any] | None,
    technical: float,
    fundamental: float,
    driver: float,
    money_flow: float,
    warnings: list[str],
) -> str:
    snapshot = snapshot or {}
    external = snapshot.get("external", {})
    cross = snapshot.get("fundamental", {}).get("cross_drivers", {})
    records = [
        external.get("bmd_palm_oil", {}),
        external.get("cbot_bean_oil", {}),
        cross.get("crude_oil", {}),
    ]
    fresh_count = sum(1 for record in records if is_verified(record) and is_fresh(record, snapshot))
    dirs = [direction_bucket(value) for value in [technical, fundamental, driver, money_flow]]
    non_flat = [item for item in dirs if item != "flat"]
    agreement = max(non_flat.count("up"), non_flat.count("down")) if non_flat else 0
    conflict = "up" in non_flat and "down" in non_flat
    if warnings or conflict and agreement <= 2:
        return "低"
    if fresh_count >= 2 and agreement >= 3:
        return "高"
    return "中"


def contradiction_warning(
    spec: dict[str, Any],
    source: dict[str, Any],
    snapshot: dict[str, Any] | None,
    technical: float,
    fundamental: float,
    driver: float,
    money_flow: float,
) -> str:
    snapshot = snapshot or {}
    warnings: list[str] = []
    change = as_float(source.get("change_pct"))
    external = snapshot.get("external", {})
    fcpo = as_float(external.get("bmd_palm_oil", {}).get("change_pct"))
    inventory = snapshot.get("fundamental", {}).get("inventory", {})
    inv_map = {
        "palm_oil": ("palm_oil_inventory", 65),
        "soybean_oil": ("soybean_oil_inventory", 110),
        "rapeseed_oil": ("rapeseed_oil_inventory", 30),
    }
    if direction_bucket(technical) == "down" and direction_bucket(money_flow) == "up":
        warnings.append("技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。")
    if direction_bucket(fundamental) == "down" and change is not None and change > 0:
        warnings.append("基本面背景偏空但盘面上涨，说明市场正在交易现实之外的驱动或资金。")
    if spec.get("key") == "palm_oil" and fcpo is not None and fcpo < 0 and change is not None and change > 0:
        warnings.append("FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。")
    inv_key, threshold = inv_map.get(spec.get("key"), ("", 0))
    inv = as_float(inventory.get(inv_key, {}).get("price")) if inv_key else None
    if inv is not None and inv >= threshold and change is not None and change > 0:
        warnings.append("库存偏高但价格上涨，库存不能单独解释今日方向。")
    return "；".join(warnings) if warnings else "暂无明显冲突信号"


def review_learning_warning(snapshot: dict[str, Any] | None) -> str:
    learning = (snapshot or {}).get("review_learning", {})
    if not isinstance(learning, dict):
        return ""
    return str(learning.get("warning") or "")


def median(values: list[float]) -> float | None:
    clean = sorted(value for value in values if value is not None)
    if not clean:
        return None
    midpoint = len(clean) // 2
    if len(clean) % 2:
        return clean[midpoint]
    return (clean[midpoint - 1] + clean[midpoint]) / 2


def candidate_points(price: float | None, tech: dict[str, Any], trend: str) -> list[dict[str, Any]]:
    if price is None:
        return []
    atr = as_float(tech.get("atr")) or max(price * 0.01, 1)
    levels = tech.get("levels", {})
    range_high = as_float(levels.get("donchian20_high")) or price + 1.5 * atr
    range_low = as_float(levels.get("donchian20_low")) or price - 1.5 * atr
    ma20 = as_float(levels.get("ma20"))
    ma60 = as_float(levels.get("ma60"))
    boll_upper = as_float(levels.get("boll_upper")) or price + 2 * atr
    boll_lower = as_float(levels.get("boll_lower")) or price - 2 * atr
    candidates: list[dict[str, Any]] = []
    if trend == "偏多":
        candidates.extend(
            [
                {"entry": price, "take_profit": price + 2.6 * atr, "stop_loss": price - 1.6 * atr, "weight": 0.24},
                {"entry": max(price, range_high), "take_profit": range_high + 1.5 * atr, "stop_loss": range_high - 1.4 * atr, "weight": 0.22},
                {"entry": price, "take_profit": boll_upper, "stop_loss": boll_lower, "weight": 0.18},
                {"entry": price, "take_profit": price + 2 * (price - min(value for value in [range_low, ma20, ma60] if value is not None)), "stop_loss": min(value for value in [range_low, ma20, ma60] if value is not None), "weight": 0.2},
                {"entry": price, "take_profit": price + 3 * atr, "stop_loss": price - 2 * atr, "weight": 0.16},
            ]
        )
    elif trend == "偏空":
        resistance = max(value for value in [range_high, ma20, ma60] if value is not None)
        candidates.extend(
            [
                {"entry": price, "take_profit": price - 2.6 * atr, "stop_loss": price + 1.6 * atr, "weight": 0.24},
                {"entry": min(price, range_low), "take_profit": range_low - 1.5 * atr, "stop_loss": range_low + 1.4 * atr, "weight": 0.22},
                {"entry": price, "take_profit": boll_lower, "stop_loss": boll_upper, "weight": 0.18},
                {"entry": price, "take_profit": price - 2 * (resistance - price), "stop_loss": resistance, "weight": 0.2},
                {"entry": price, "take_profit": price - 3 * atr, "stop_loss": price + 2 * atr, "weight": 0.16},
            ]
        )
    else:
        upper = median([range_high, boll_upper, price + 1.6 * atr]) or price + 1.5 * atr
        lower = median([range_low, boll_lower, price - 1.6 * atr]) or price - 1.5 * atr
        candidates.extend(
            [
                {"entry": price, "take_profit": upper, "stop_loss": lower - 0.7 * atr, "weight": 0.28},
                {"entry": price, "take_profit": lower, "stop_loss": upper + 0.7 * atr, "weight": 0.28},
                {"entry": upper, "take_profit": upper + 1.3 * atr, "stop_loss": price, "weight": 0.22},
                {"entry": lower, "take_profit": lower - 1.3 * atr, "stop_loss": price, "weight": 0.22},
            ]
        )
    return [item for item in candidates if as_float(item.get("take_profit")) is not None and as_float(item.get("stop_loss")) is not None]


def weighted_average(values: list[tuple[float, float]]) -> float | None:
    total_weight = sum(weight for _, weight in values)
    if total_weight <= 0:
        return None
    return sum(value * weight for value, weight in values) / total_weight


def strategy_recommendation(price: float | None, tech: dict[str, Any], trend: str) -> dict[str, str]:
    candidates = candidate_points(price, tech, trend)
    if price is None or not candidates:
        return {
            "stance": trend,
            "entry": "需进一步核验",
            "take_profit": "上方观察位需进一步核验",
            "stop_loss": "下方观察位需进一步核验",
            "upper_watch": "需进一步核验",
            "lower_watch": "需进一步核验",
            "invalidation": "行情价格或关键位不足，观点失效条件需进一步核验。",
            "risk_tip": "不输出明确开平仓指令。",
            "basis": "行情价格或关键位不足，暂不输出具体观察位。",
        }
    if trend in ("偏多", "震荡偏强"):
        take_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("take_profit"))) is not None and value > price]
        stop_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("stop_loss"))) is not None and value < price]
        action = "观察回撤后能否守住下方关键位"
    elif trend in ("偏空", "震荡偏弱"):
        take_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("take_profit"))) is not None and value < price]
        stop_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("stop_loss"))) is not None and value > price]
        action = "观察反弹后能否突破上方关键位"
    else:
        upper_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("take_profit"))) is not None and value > price]
        lower_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("take_profit"))) is not None and value < price]
        take_values = upper_values + lower_values
        stop_values = [(value, item["weight"]) for item in candidates if (value := as_float(item.get("stop_loss"))) is not None]
        action = "区间内等待驱动与资金确认"
    take_profit = weighted_average(take_values)
    stop_loss = weighted_average(stop_values)
    upper_target = weighted_average([(value, weight) for value, weight in take_values if value > price])
    lower_target = weighted_average([(value, weight) for value, weight in take_values if value < price])
    upper_watch = upper_target if upper_target is not None else (take_profit if take_profit and take_profit > price else None)
    lower_watch = lower_target if lower_target is not None else (take_profit if take_profit and take_profit < price else None)
    if trend in ("震荡", "分歧震荡") and take_values:
        upper_target = weighted_average([(value, weight) for value, weight in take_values if value > price])
        lower_target = weighted_average([(value, weight) for value, weight in take_values if value < price])
        take_text = f"上方观察位 {fmt_number(upper_target)} / 下方观察位 {fmt_number(lower_target)}"
    else:
        take_text = f"上方观察位 {fmt_number(upper_watch)}"
    lower_text = f"下方观察位 {fmt_number(lower_watch if lower_watch is not None else stop_loss)}"
    invalidation = "若驱动评分与资金评分同步转弱，当前偏强判断失效。" if trend in ("偏多", "震荡偏强") else (
        "若驱动评分与资金评分同步转强，当前偏弱判断失效。" if trend in ("偏空", "震荡偏弱") else "若价格突破区间且驱动/资金同向，震荡判断失效。"
    )
    return {
        "stance": trend,
        "entry": f"现价 {fmt_number(price)}；{action}",
        "take_profit": take_text,
        "stop_loss": lower_text,
        "upper_watch": fmt_number(upper_watch),
        "lower_watch": fmt_number(lower_watch if lower_watch is not None else stop_loss),
        "invalidation": invalidation,
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": f"综合波动、突破、均线和区间测算观察位；共纳入 {len(candidates)} 组候选点位，不输出明确交易指令。",
    }


def build_market_view(
    name: str,
    stance: str,
    tech: dict[str, Any],
    fundamental_note: str,
    driver_note: str,
    money_note: str,
    confidence: str,
    warning: str,
    learning_warning: str = "",
) -> str:
    signals = "、".join(tech.get("signals") or [])
    trend = tech.get("trend", "震荡")
    if stance in ("偏多", "震荡偏强"):
        tone = "驱动与资金对价格更友好"
    elif stance in ("偏空", "震荡偏弱"):
        tone = "驱动与资金对价格形成压力"
    elif stance == "分歧震荡":
        tone = "各类信号并不一致，暂按分歧震荡处理"
    else:
        tone = "当前行情缺少单边确认，仍需要等待新增驱动"
    detail = f"技术面显示{trend}"
    if signals:
        detail += f"，主要信号为{signals}"
    warning_text = "暂未看到需要明显降级的冲突信号" if warning == "暂无明显冲突信号" else warning
    learning_text = f"复盘提示：{sentence(learning_warning)}" if learning_warning else ""
    return (
        f"{name}当前观点为{stance}，置信度{confidence}。"
        f"核心原因是：{tone}；{detail}。"
        f"基本面背景看{readable_note(fundamental_note)}；驱动看{readable_note(driver_note)}；资金看{readable_note(money_note)}。"
        f"需要降级看待的地方：{sentence(warning_text)}{learning_text}"
    )


def analyze_contract(item: dict[str, Any]) -> dict[str, Any]:
    spec = item.get("spec", {})
    source = item.get("source", {})
    snapshot = item.get("snapshot")
    price = as_float(source.get("price"))
    history = item.get("history")
    if item.get("external"):
        change_pct = as_float(source.get("change_pct"))
        technical = 56 if change_pct and change_pct > 0 else 44 if change_pct and change_pct < 0 else 50
        fundamental = 50.0
        driver, driver_note, driver_warnings = driver_score(snapshot, spec)
        money_flow, money_note = money_flow_score(source, snapshot, spec)
        total_score = round(clamp(technical * 0.25 + fundamental * 0.25 + driver * 0.30 + money_flow * 0.20), 1)
        stance = stance_for(total_score, technical, fundamental, driver, money_flow)
        high = as_float(source.get("high")) or price or 0
        low = as_float(source.get("low")) or price or 0
        tech = {
            "atr": abs(high - low) or ((price or 1) * 0.01),
            "trend": "偏多" if technical >= 55 else "偏空" if technical <= 45 else "震荡",
            "levels": {},
            "signals": ["外盘参考合约，技术历史样本不足"],
        }
        fundamental_note = "外盘参考合约，国内基本面因子不直接套用"
        warning = contradiction_warning(spec, source, snapshot, technical, fundamental, driver, money_flow)
        if driver_warnings:
            warning = "；".join([warning, *driver_warnings]) if warning != "暂无明显冲突信号" else "；".join(driver_warnings)
        confidence = view_confidence(snapshot, technical, fundamental, driver, money_flow, driver_warnings)
        view = build_market_view(str(spec.get("name", "")), stance, tech, fundamental_note, driver_note, money_note, confidence, warning, review_learning_warning(snapshot))
    else:
        tech = technical_analysis(price, history)
        fundamental, fundamental_note = fundamental_score(spec, snapshot)
        technical = as_float(tech.get("score")) or 50.0
        driver, driver_note, driver_warnings = driver_score(snapshot, spec)
        money_flow, money_note = money_flow_score(source, snapshot, spec)
        total_score = round(clamp(technical * 0.25 + fundamental * 0.25 + driver * 0.30 + money_flow * 0.20), 1)
        stance = stance_for(total_score, technical, fundamental, driver, money_flow)
        warning = contradiction_warning(spec, source, snapshot, technical, fundamental, driver, money_flow)
        if driver_warnings:
            warning = "；".join([warning, *driver_warnings]) if warning != "暂无明显冲突信号" else "；".join(driver_warnings)
        confidence = view_confidence(snapshot, technical, fundamental, driver, money_flow, driver_warnings)
        view = build_market_view(str(spec.get("name", "")), stance, tech, fundamental_note, driver_note, money_note, confidence, warning, review_learning_warning(snapshot))

    return {
        "score": {
            "total": total_score,
            "technical": technical,
            "fundamental": fundamental,
            "driver": driver,
            "money_flow": money_flow,
            "stance": stance,
            "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
            "view_confidence": confidence,
            "contradiction_warning": warning,
        },
        "view_confidence": confidence,
        "contradiction_warning": warning,
        "view": view,
        "technical_detail": build_technical_detail(price, tech, total_score),
        "fundamental_detail": build_fundamental_detail(spec, snapshot, fundamental_note, fundamental),
        "strategy_recommendation": strategy_recommendation(price, tech, stance),
        "skill_trace": {
            "skill": "technical_basic_analysis_skill",
            "technical_function": "technical_analysis",
            "fundamental_function": "fundamental_score",
            "driver_function": "driver_score",
            "money_flow_function": "money_flow_score",
            "strategy_function": "strategy_recommendation",
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

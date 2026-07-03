#!/usr/bin/env python3
"""Build the static oil-futures contract data used by the home-page tab."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNS = ROOT / "source_runs"
OUTPUT = ROOT / "data" / "oil_futures.js"
HITHINK_CLI = Path.home() / ".codex" / "skills" / "hithink-market-query" / "scripts" / "cli.py"
PRICE_TOLERANCE = 2.0
PCT_TOLERANCE = 0.25

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


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def raw_number(value: Any) -> str | None:
    number = as_float(value)
    if number is None:
        return None
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.2f}"


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


def ak_daily_history(ak: Any, contract: str):
    if ak is None:
        return None
    try:
        df = ak.futures_zh_daily_sina(symbol=contract)
        if df is None or len(df) < 80:
            return None
        for column in ["open", "high", "low", "close", "volume", "hold", "settle"]:
            if column in df.columns:
                df[column] = df[column].map(as_float)
        return df.dropna(subset=["high", "low", "close"]).tail(220).reset_index(drop=True)
    except Exception:
        return None


def last_float(series: Any) -> float | None:
    try:
        value = series.iloc[-1]
    except Exception:
        return None
    return as_float(value)


def technical_analysis(price: float | None, history: Any) -> dict[str, Any]:
    if price is None or history is None or len(history) < 80:
        return {
            "score": 50,
            "trend": "数据不足，按中性处理",
            "atr": None,
            "levels": {},
            "signals": ["技术数据不足"],
        }

    close = history["close"].copy()
    high = history["high"].copy()
    low = history["low"].copy()
    close.iloc[-1] = price
    high.iloc[-1] = max(as_float(high.iloc[-1]) or price, price)
    low.iloc[-1] = min(as_float(low.iloc[-1]) or price, price)

    ma5 = last_float(close.rolling(5).mean())
    ma10 = last_float(close.rolling(10).mean())
    ma20 = last_float(close.rolling(20).mean())
    ma60 = last_float(close.rolling(60).mean())
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()
    macd_hist = last_float(dif - dea) or 0
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = last_float(100 - 100 / (1 + gain / loss))
    boll_mid = ma20
    boll_std = last_float(close.rolling(20).std())
    boll_upper = boll_mid + 2 * boll_std if boll_mid is not None and boll_std is not None else None
    boll_lower = boll_mid - 2 * boll_std if boll_mid is not None and boll_std is not None else None
    tr = max(
        as_float(high.iloc[-1] - low.iloc[-1]) or 0,
        abs((as_float(high.iloc[-1]) or price) - (as_float(close.iloc[-2]) or price)),
        abs((as_float(low.iloc[-1]) or price) - (as_float(close.iloc[-2]) or price)),
    )
    tr_series = (high - low).to_frame("hl")
    tr_series["hc"] = (high - close.shift(1)).abs()
    tr_series["lc"] = (low - close.shift(1)).abs()
    atr = last_float(tr_series.max(axis=1).rolling(14).mean()) or tr
    high20 = last_float(high.shift(1).rolling(20).max())
    low20 = last_float(low.shift(1).rolling(20).min())
    high55 = last_float(high.shift(1).rolling(55).max())
    low55 = last_float(low.shift(1).rolling(55).min())

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
    if score >= 65:
        trend = "偏多"
    elif score <= 40:
        trend = "偏空"
    else:
        trend = "震荡"

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


def fundamental_score(spec: dict[str, str], snapshot: dict[str, Any] | None) -> tuple[float, str]:
    snapshot = snapshot or {}
    external = snapshot.get("external", {})
    fundamental = snapshot.get("fundamental", {})
    inventory = fundamental.get("inventory", {})
    spread = fundamental.get("spread", {})
    score = 50.0
    notes: list[str] = []

    cbot = as_float(external.get("cbot_bean_oil", {}).get("change_pct"))
    fcpo = as_float(external.get("bmd_palm_oil", {}).get("change_pct"))
    if spec["key"] == "palm_oil":
        if fcpo is not None:
            score += max(-10, min(10, fcpo * 5))
            notes.append("FCPO联动")
        inv = as_float(inventory.get("palm_oil_inventory", {}).get("price"))
        if inv is not None and inv >= 65:
            score -= 6
            notes.append("棕榈油库存偏高")
        soy_palm = as_float(spread.get("soybean_palm_spread", {}).get("price") if isinstance(spread.get("soybean_palm_spread"), dict) else spread.get("soybean_palm_spread"))
        if soy_palm is not None and soy_palm < 0:
            score += 4
            notes.append("豆棕价差仍支撑P相对强弱")
    elif spec["key"] == "soybean_oil":
        if cbot is not None:
            score += max(-10, min(10, cbot * 5))
            notes.append("CBOT豆油联动")
        inv = as_float(inventory.get("soybean_oil_inventory", {}).get("price"))
        if inv is not None and inv >= 110:
            score -= 8
            notes.append("豆油库存压力")
    elif spec["key"] == "rapeseed_oil":
        inv = as_float(inventory.get("rapeseed_oil_inventory", {}).get("price"))
        if inv is not None and inv >= 30:
            score -= 6
            notes.append("菜油库存压力")
        if cbot is not None and cbot > 0:
            score += 3
            notes.append("油脂板块共振")

    return round(clamp(score, 25, 75), 1), "；".join(notes) if notes else "基本面暂无强新增驱动"


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


def hithink_contract(contract: str) -> dict[str, Any]:
    if not HITHINK_CLI.exists():
        return {"status": "missing", "message": "行情skill脚本不存在"}
    if not os.environ.get("IWENCAI_API_KEY"):
        return {"status": "missing", "message": "行情skill未配置 IWENCAI_API_KEY"}

    query = f"{contract} 最新价 涨跌幅 成交量 持仓量"
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(HITHINK_CLI),
                "--query",
                query,
                "--limit",
                "5",
                "--timeout",
                "20",
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:
        return {"status": "missing", "message": f"行情skill调用失败：{exc}"}

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return {"status": "missing", "message": "行情skill返回非 JSON"}

    if result.returncode != 0 or not payload.get("success"):
        return {"status": "missing", "message": "行情skill未返回有效行情"}

    rows = payload.get("datas") or []
    if not rows:
        return {"status": "missing", "message": "行情skill返回空数据"}

    row = rows[0]
    return {
        "status": "ok",
        "source": "同花顺问财行情skill",
        "contract": row.get("合约代码") or contract,
        "price": as_float(row.get("最新价") or row.get("收盘价")),
        "change_pct": as_float(row.get("最新涨跌幅") if row.get("最新涨跌幅") is not None else row.get("涨跌幅")),
        "volume": as_int(row.get("成交量")),
        "open_interest": as_int(row.get("持仓量")),
        "query": query,
    }


def verification_note(ak_source: dict[str, Any], hithink: dict[str, Any]) -> str:
    ak_price = as_float(ak_source.get("price"))
    ak_pct = as_float(ak_source.get("change_pct"))
    if hithink.get("status") != "ok":
        return f"行情skill核验：未完成（{hithink.get('message', '无有效返回')}）；当前以 AkShare 为准。"

    hithink_price = as_float(hithink.get("price"))
    hithink_pct = as_float(hithink.get("change_pct"))
    notes: list[str] = []

    if ak_price is None or hithink_price is None:
        notes.append("价格缺少一侧数据，需进一步核验")
    elif abs(ak_price - hithink_price) <= PRICE_TOLERANCE:
        notes.append(f"价格一致：AkShare {raw_number(ak_price)} / 行情skill {raw_number(hithink_price)}")
    else:
        notes.append(f"价格不一致：AkShare {raw_number(ak_price)} / 行情skill {raw_number(hithink_price)}")

    if ak_pct is not None and hithink_pct is not None and abs(ak_pct - hithink_pct) > PCT_TOLERANCE:
        notes.append(f"涨跌幅口径不同：AkShare {fmt_pct(ak_pct)} / 行情skill {fmt_pct(hithink_pct)}")

    return "；".join(notes)


def merge_domestic(spec: dict[str, str], snapshot: dict[str, Any] | None, ak: Any) -> dict[str, Any]:
    skill_record = (snapshot or {}).get("domestic", {}).get(spec["key"], {})
    realtime = ak_realtime_contract(ak, spec["ak_realtime"])
    fallback_contract = concrete_contract(skill_record.get("contract")) or (realtime or {}).get("contract") or spec["fallback"]
    history = ak_daily_history(ak, fallback_contract)
    daily = ak_daily_contract(ak, fallback_contract)

    source = skill_record if skill_record.get("status") == "ok" else {}
    if not source:
      source = realtime or daily or {}
    if realtime:
        source = {**source, **{key: value for key, value in realtime.items() if value is not None}}
    if daily:
        source = {**daily, **{key: value for key, value in source.items() if value not in (None, "", "需进一步核验")}}

    contract = concrete_contract(source.get("contract")) or fallback_contract
    hithink = hithink_contract(contract)
    verification = verification_note(source, hithink)
    price = as_float(source.get("price"))
    tech = technical_analysis(price, history)
    fundamental, fundamental_note = fundamental_score(spec, snapshot)
    technical = as_float(tech.get("score")) or 50
    total_score = round(clamp(technical * 0.7 + fundamental * 0.3), 1)
    if total_score >= 65:
        stance = "偏多"
    elif total_score <= 40:
        stance = "偏空"
    else:
        stance = "震荡"
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
        "source": "AkShare + 同花顺问财行情skill" if hithink.get("status") == "ok" else source.get("source") or "需进一步核验",
        "note": spec["note"],
        "verification": verification,
        "score": {
            "total": total_score,
            "technical": technical,
            "fundamental": fundamental,
            "stance": stance,
            "weights": "技术面70% / 基本面30%",
        },
        "view": build_market_view(spec["name"], total_score, tech, fundamental_note),
        "strategies": strategy_levels(price, tech, stance),
    }


def merge_external(spec: dict[str, str], snapshot: dict[str, Any] | None) -> dict[str, Any]:
    record = (snapshot or {}).get("external", {}).get(spec["key"], {})
    change_pct = as_float(record.get("change_pct"))
    technical = 58 if change_pct and change_pct > 0 else 42 if change_pct and change_pct < 0 else 50
    fundamental = 50
    total_score = round(technical * 0.7 + fundamental * 0.3, 1)
    stance = "偏多" if total_score >= 65 else "偏空" if total_score <= 40 else "震荡"
    price = as_float(record.get("price"))
    high = as_float(record.get("high")) or price or 0
    low = as_float(record.get("low")) or price or 0
    atr_proxy = abs(high - low)
    tech = {
        "atr": atr_proxy or ((price or 1) * 0.01),
        "trend": stance,
        "levels": {},
        "signals": ["外盘参考合约，技术历史样本不足"],
    }
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
        "verification": "外盘合约暂不使用同花顺问财核验；以公开外盘数据源为准。",
        "score": {
            "total": total_score,
            "technical": technical,
            "fundamental": fundamental,
            "stance": stance,
            "weights": "技术面70% / 基本面30%",
        },
        "view": f"{spec['name']}作为外盘参考，当前按{stance}处理；主要用于判断内盘油脂情绪传导，不单独作为交易指令。",
        "strategies": strategy_levels(price, tech, stance),
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
    source_note += "；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证"
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

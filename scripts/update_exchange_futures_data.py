#!/usr/bin/env python3
"""Generate DCE/CZCE main-contract analysis data for the static research page."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

try:
    import akshare as ak  # type: ignore
except ImportError:  # pragma: no cover - deployment dependency
    ak = None


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "exchange_futures.js"
TECHNICAL_HELPER = Path.home() / ".openclaw" / "workspace" / "skills" / "technical-analysis-helper" / "scripts" / "calculate_indicators.py"
NEWS_GLOB = ROOT / "source_runs" / "*" / "raw" / "mx_search_news.json"
SINA_DAILY_URL = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var_V21052021_4_12=/InnerFuturesNewService.getDailyKLine"

EXCHANGE_LABELS = {"大连商品交易所": "DCE", "郑州商品交易所": "CZCE"}

CATEGORY_RULES = {
    "油脂油料": {"棕榈", "豆二", "豆粕", "豆油", "豆一", "菜油", "菜籽", "菜粕", "花生"},
    "谷物饲料": {"玉米", "玉米淀粉", "粳米", "粳稻", "早籼稻", "晚籼稻", "强麦"},
    "软商品": {"白糖", "棉花", "棉纱", "鲜苹果", "红枣", "鸡蛋", "生猪"},
    "黑色建材": {"铁矿石", "焦炭", "焦煤", "动力煤", "玻璃", "纯碱"},
    "能化材料": {"PVC", "塑料", "PP", "乙二醇", "苯乙烯", "液化石油气", "纯苯", "PTA", "郑醇", "尿素", "短纤", "烧碱", "二甲苯", "瓶级聚酯切片", "丙烯"},
    "其他": set(),
}


def as_number(value: Any) -> float | None:
    try:
        if value in (None, "", "-"):
            return None
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def clean_number(value: Any, digits: int = 2) -> float | None:
    number = as_number(value)
    return round(number, digits) if number is not None else None


def load_technical_helper():
    spec = importlib.util.spec_from_file_location("technical_analysis_helper", TECHNICAL_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("technical-analysis-helper 不可用")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def category_for(name: str) -> str:
    for category, names in CATEGORY_RULES.items():
        if name in names:
            return category
    return "其他"


def is_contract(symbol: Any) -> bool:
    return bool(re.fullmatch(r"[A-Z]+\d{4}", str(symbol or "").upper()))


def percent_change(trade: Any, preclose: Any) -> float | None:
    current, previous = as_number(trade), as_number(preclose)
    if current is None or previous in (None, 0):
        return None
    return round((current - previous) / previous * 100, 2)


def fetch_history(symbol: str) -> list[dict[str, float]]:
    """Use the same Sina endpoint wrapped by AkShare, with a bounded timeout."""
    try:
        response = requests.get(
            SINA_DAILY_URL,
            params={"symbol": symbol, "type": "2021_04_12"},
            headers={"Referer": "https://finance.sina.com.cn/futures/", "User-Agent": "Mozilla/5.0"},
            timeout=12,
        )
        response.raise_for_status()
        match = re.search(r"=\((\[.*\])\)", response.text, re.S)
        if not match:
            return []
        rows = json.loads(match.group(1))
    except (requests.RequestException, ValueError, json.JSONDecodeError):
        return []

    history = []
    for row in rows[-220:]:
        if isinstance(row, dict):
            open_, high, low, close = (as_number(row.get(key)) for key in ("o", "h", "l", "c"))
        elif isinstance(row, list) and len(row) >= 5:
            open_, high, low, close = (as_number(row[index]) for index in range(1, 5))
        else:
            continue
        if None in (open_, high, low, close):
            continue
        history.append({"open": open_, "high": high, "low": low, "close": close})
    return history


def technical_summary(helper: Any, history: list[dict[str, float]], price: float | None) -> dict[str, Any]:
    if price is None or len(history) < 60:
        return {"status": "需进一步核验", "summary": "日线历史样本不足，暂不输出技术判断。"}
    closes = [row["close"] for row in history]
    highs = [row["high"] for row in history]
    lows = [row["low"] for row in history]
    closes[-1] = price
    ma = helper.calculate_ma(closes)
    macd = helper.calculate_macd(closes)
    rsi = helper.calculate_rsi(closes)
    kdj = helper.calculate_kdj(highs, lows, closes)
    boll = helper.calculate_boll(closes)
    atr = helper.calculate_atr(highs, lows, closes)
    ma20, ma60 = as_number(ma.get("ma20")), as_number(ma.get("ma60"))
    rsi12 = as_number(rsi.get("rsi12"))
    dif, dea = as_number(macd.get("dif")), as_number(macd.get("dea"))
    signals = []
    score = 50
    if ma20 is not None:
        if price > ma20:
            score += 10
            signals.append("价格位于20日均线上方")
        else:
            score -= 10
            signals.append("价格位于20日均线下方")
    if ma20 is not None and ma60 is not None:
        if price > ma20 > ma60:
            score += 8
            signals.append("中期均线结构偏多")
        elif price < ma20 < ma60:
            score -= 8
            signals.append("中期均线结构偏空")
    if dif is not None and dea is not None:
        if dif > dea:
            score += 5
            signals.append("MACD快线位于慢线上方")
        else:
            score -= 5
            signals.append("MACD快线位于慢线下方")
    if rsi12 is not None:
        if rsi12 >= 70:
            signals.append("RSI处于偏高区间，注意波动放大")
        elif rsi12 <= 30:
            signals.append("RSI处于偏低区间，留意修复需求")
    score = max(20, min(80, score))
    trend = "偏多" if score >= 62 else "偏空" if score <= 38 else "震荡"
    return {
        "status": "ok",
        "trend": trend,
        "score": score,
        "summary": "；".join(signals) if signals else "指标暂未形成一致方向。",
        "indicators": {
            "MA5": clean_number(ma.get("ma5")), "MA20": clean_number(ma20), "MA60": clean_number(ma60),
            "MACD": clean_number(macd.get("histogram")), "RSI12": clean_number(rsi12),
            "KDJ_J": clean_number(kdj.get("j")), "BOLL上轨": clean_number(boll.get("upper")),
            "BOLL下轨": clean_number(boll.get("lower")), "ATR14": clean_number(atr),
        },
        "levels": {"20日高": clean_number(max(highs[-20:])), "20日低": clean_number(min(lows[-20:]))},
    }


def latest_news() -> list[dict[str, Any]]:
    paths = sorted(ROOT.glob("source_runs/*/raw/mx_search_news.json"), reverse=True)
    if not paths:
        return []
    try:
        payload = json.loads(paths[0].read_text(encoding="utf-8"))
        return payload["data"]["data"]["llmSearchResponse"]["data"]
    except (KeyError, TypeError, ValueError):
        return []


def news_for(name: str, news: list[dict[str, Any]]) -> list[dict[str, str]]:
    aliases = {name, name.replace("鲜", ""), name.replace("郑", "")}
    matched = []
    for item in news:
        text = f"{item.get('title', '')} {item.get('content', '')}"
        if not any(alias and alias in text for alias in aliases):
            continue
        matched.append({
            "title": str(item.get("title") or "行业热点"),
            "date": str(item.get("date") or "需进一步核验"),
            "source": str(item.get("insName") or "资讯来源需进一步核验"),
            "url": str(item.get("jumpUrl") or ""),
        })
        if len(matched) == 3:
            break
    return matched


def fundamental_summary(name: str, category: str, headlines: list[dict[str, str]]) -> dict[str, Any]:
    frameworks = {
        "油脂油料": "跟踪进口与压榨、库存、现货基差、天气及海外油籽价格传导。",
        "谷物饲料": "跟踪种植面积、天气、收储政策、饲料需求与库存变化。",
        "软商品": "跟踪产区天气、现货消费、库存、进出口与政策调控。",
        "黑色建材": "跟踪终端需求、钢厂利润、库存、焦煤铁矿成本与供给约束。",
        "能化材料": "跟踪原油与煤炭成本、装置开工、库存、需求季节性及进口窗口。",
        "其他": "跟踪供给、需求、库存、基差与政策变化；细分数据需按品种进一步核验。",
    }
    hotspot = "已匹配到近期行业热点，请结合原始来源判断是否构成当日驱动。" if headlines else "当前数据集未匹配到该品种的近期直接热点，新闻维度不参与方向判断。"
    return {"summary": f"{name}属于{category}，{frameworks[category]}{hotspot}", "framework": frameworks[category]}


def build_contracts() -> list[dict[str, Any]]:
    if ak is None:
        raise RuntimeError("AkShare 未安装，无法生成主力合约列表")
    helper = load_technical_helper()
    symbols = ak.futures_symbol_mark()
    symbols = symbols[symbols["exchange"].isin(EXCHANGE_LABELS)]
    news = latest_news()
    contracts = []
    for _, item in symbols.iterrows():
        product_name = str(item["symbol"])
        try:
            quotes = ak.futures_zh_realtime(symbol=product_name)
        except Exception:
            continue
        if quotes is None or quotes.empty:
            continue
        candidates = quotes[quotes["symbol"].map(is_contract)].copy()
        if candidates.empty:
            continue
        candidates["volume"] = candidates["volume"].fillna(0)
        candidates["position"] = candidates["position"].fillna(0)
        candidates = candidates[(candidates["volume"] > 0) & (candidates["position"] > 0)]
        if candidates.empty:
            continue
        main = candidates.sort_values(["volume", "position"], ascending=False).iloc[0]
        symbol = str(main["symbol"]).upper()
        price = as_number(main.get("trade"))
        category = category_for(product_name)
        headlines = news_for(product_name, news)
        history = fetch_history(symbol)
        contracts.append({
            "symbol": symbol,
            "product": product_name,
            "exchange": EXCHANGE_LABELS[str(item["exchange"])],
            "category": category,
            "price": clean_number(price),
            "change_pct": percent_change(main.get("trade"), main.get("preclose")),
            "volume": int(main["volume"]),
            "open_interest": int(main["position"]),
            "trade_date": str(main.get("tradedate") or ""),
            "technical": technical_summary(helper, history, price),
            "fundamental": fundamental_summary(product_name, category, headlines),
            "news_hotspots": headlines,
            "data_quality": "行情来自 AkShare 实时合约列表；技术指标来自日线数据。基本面新闻仅作研究线索，需结合原始来源核验。",
        })
    return sorted(contracts, key=lambda item: (item["exchange"], item["category"], item["product"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    contracts = build_contracts()
    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "AkShare 实时行情与日线数据；技术指标由 technical-analysis-helper 生成；新闻热点来自最近一次已保存的资讯检索结果。",
        "contracts": contracts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(f"window.EXCHANGE_FUTURES_DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};\n", encoding="utf-8")
    print(f"updated {args.output} with {len(contracts)} contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

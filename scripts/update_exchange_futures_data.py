#!/usr/bin/env python3
"""Generate DCE/CZCE main-contract analysis data for the static research page."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import time
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
LEVELS_HELPER = Path.home() / ".openclaw" / "workspace" / "skills" / "technical-analysis-helper" / "scripts" / "identify_levels.py"
NEWS_GLOB = ROOT / "source_runs" / "*" / "raw" / "mx_search_news.json"
SINA_DAILY_URL = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var_V21052021_4_12=/InnerFuturesNewService.getDailyKLine"

EXCHANGE_LABELS = {"大连商品交易所": "DCE", "郑州商品交易所": "CZCE"}

CATEGORY_RULES = {
    "油脂油料": {"棕榈", "豆二", "豆粕", "豆油", "豆一", "菜油", "菜籽", "菜粕", "花生"},
    "谷物饲料": {"玉米", "玉米淀粉", "粳米", "粳稻", "早籼稻", "晚籼稻", "强麦"},
    "软商品": {"白糖", "棉花", "棉纱", "鲜苹果", "红枣", "鸡蛋", "生猪"},
    "黑色建材": {"铁矿石", "焦炭", "焦煤", "动力煤", "玻璃", "纯碱"},
    "能化材料": {"PVC", "塑料", "PP", "乙二醇", "苯乙烯", "液化石油气", "纯苯", "PTA", "郑醇", "尿素", "短纤", "烧碱", "二甲苯", "瓶级聚酯切片", "丙烯"},
}

FUNDAMENTAL_GROUPS = [
    (
        {"棕榈", "豆油", "菜油"},
        "油脂",
        [
            ("供应与进口", "跟踪马来与印尼产量、出口、国内到港及进口利润；产地库存变化决定进口成本与供应预期。"),
            ("需求与替代", "观察餐饮消费、生物柴油政策、豆棕菜油价差及现货成交，判断需求能否承接盘面。"),
            ("库存与基差", "核验商业库存、港口库存、现货基差和仓单变化；库存数据通常是周度背景，不能替代当日驱动。"),
        ],
    ),
    (
        {"豆一", "豆二", "豆粕", "菜粕"},
        "油脂油料",
        [
            ("原料供给", "跟踪巴西、阿根廷与美国大豆产量、出口节奏、国内到港和压榨排期。"),
            ("下游需求", "豆粕、菜粕重点看养殖利润、饲料配方替代、禽畜存栏与终端提货。"),
            ("库存与利润", "关注油厂开机率、豆粕库存、基差和压榨利润；高库存与高开机并不必然等于当日利空。"),
        ],
    ),
    (
        {"玉米", "玉米淀粉", "粳米", "粳稻", "早籼稻", "晚籼稻", "强麦"},
        "谷物饲料",
        [
            ("供给", "跟踪产区天气、种植面积、收储与拍卖政策、进口谷物替代及基层售粮节奏。"),
            ("需求", "观察饲料、深加工、乙醇与淀粉开工，评估需求季节性与利润传导。"),
            ("库存与价差", "核验北港与南港库存、深加工库存、现货基差及小麦稻谷替代价差。"),
        ],
    ),
    (
        {"鸡蛋", "生猪"},
        "养殖",
        [
            ("供给", "鸡蛋看在产存栏、淘汰节奏和补栏；生猪看能繁母猪、出栏体重及集团场出栏计划。"),
            ("需求", "关注节假日备货、餐饮消费、屠宰开工与冻品去化，区分短期季节性与趋势需求。"),
            ("成本与现货", "跟踪饲料成本、养殖利润、现货价格和区域价差；期现分化时需优先核验交割月供需。"),
        ],
    ),
    (
        {"铁矿石", "焦炭", "焦煤", "玻璃", "纯碱"},
        "黑色建材",
        [
            ("供给", "铁矿关注海外发运与到港，双焦关注煤矿供应与安全检查，玻璃纯碱关注产线开工与冷修投产。"),
            ("需求", "跟踪钢厂利润、铁水产量、地产竣工、基建强度和下游补库，判断需求是否具有持续性。"),
            ("库存与利润", "核验港口和厂库库存、钢厂原料库存、玻璃厂库及产业链利润，警惕高库存下的反弹持续性。"),
        ],
    ),
    (
        {"硅铁", "锰硅"},
        "铁合金",
        [
            ("供给成本", "跟踪主产区电价、兰炭、锰矿或硅石成本、厂库与开工率，供给弹性通常高于黑色成材。"),
            ("需求", "重点看粗钢产量、钢厂招标价格与采购节奏，钢厂利润影响合金补库意愿。"),
            ("库存与价差", "关注厂家库存、交割库库存与现货升贴水，现货成交弱时盘面上行需降低置信度。"),
        ],
    ),
    (
        {"白糖", "棉花", "棉纱", "鲜苹果", "红枣", "花生", "菜籽"},
        "农产品",
        [
            ("产区供给", "跟踪产区天气、种植与收获进度、病虫害、进口政策及年度平衡表变化。"),
            ("消费与加工", "观察终端消费、加工利润、替代品价格及节前备货，区分现货改善与预期交易。"),
            ("库存与现货", "核验产地库存、销区库存、仓单、基差和物流变化；农产品季节性强，需对应当前年度阶段。"),
        ],
    ),
    (
        {"PVC", "塑料", "PP", "乙二醇", "苯乙烯", "液化石油气", "纯苯", "PTA", "郑醇", "尿素", "短纤", "烧碱", "二甲苯", "瓶级聚酯切片", "丙烯"},
        "能化材料",
        [
            ("成本与供给", "跟踪原油、煤炭、石脑油或甲醇成本，装置检修与投产、进口窗口和行业开工率。"),
            ("下游需求", "观察地产、包装、纺织、聚酯、化肥或工业消费的开工和订单，判断需求改善是否可持续。"),
            ("库存与利润", "核验社会库存、港口库存、厂库、基差与产业链利润；库存去化需与开工、现货成交交叉确认。"),
        ],
    ),
    (
        {"原木", "纤维板", "胶合板"},
        "林木建材",
        [
            ("供给与进口", "跟踪进口针叶原木到港、海外发运、检尺政策和港口库存，供给变化受航运与汇率影响。"),
            ("终端需求", "观察地产施工、家具与板材加工开工，需求弹性通常受季节和资金面制约。"),
            ("现货与交割", "核验港口现货报价、区域价差、仓单与交割标准；流动性偏低时更需关注期现可交易性。"),
        ],
    ),
]


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


def display_number(value: Any) -> str:
    number = clean_number(value)
    return str(number) if number is not None else "需进一步核验"


def load_technical_helper():
    spec = importlib.util.spec_from_file_location("technical_analysis_helper", TECHNICAL_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("technical-analysis-helper 不可用")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_levels_helper():
    spec = importlib.util.spec_from_file_location("technical_levels_helper", LEVELS_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("technical-analysis-helper 支撑阻力模块不可用")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def category_for(name: str) -> str:
    for category, names in CATEGORY_RULES.items():
        if name in names:
            return category
    for names, category, _ in FUNDAMENTAL_GROUPS:
        if name in names:
            return category
    return "待分类"


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


def technical_summary(helper: Any, levels_helper: Any, history: list[dict[str, float]], price: float | None) -> dict[str, Any]:
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
    discovered_levels = levels_helper.identify_support_resistance(closes, highs, lows)
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
    momentum = "MACD向上，短线动能偏强" if dif is not None and dea is not None and dif > dea else "MACD向下，短线动能偏弱"
    if rsi12 is not None and rsi12 >= 70:
        momentum += "；RSI偏高，追涨风险上升"
    elif rsi12 is not None and rsi12 <= 30:
        momentum += "；RSI偏低，留意超跌修复"
    nearest_support = (discovered_levels.get("nearest_support") or {}).get("price")
    nearest_resistance = (discovered_levels.get("nearest_resistance") or {}).get("price")
    return {
        "status": "ok",
        "trend": trend,
        "score": score,
        "summary": "；".join(signals) if signals else "指标暂未形成一致方向。",
        "details": [
            {"title": "趋势", "text": f"日线趋势判定为{trend}，MA20 {clean_number(ma20)}，MA60 {clean_number(ma60)}。"},
            {"title": "动量", "text": momentum},
            {"title": "波动", "text": f"ATR14 为 {clean_number(atr)}，布林区间 {clean_number(boll.get('lower'))} 至 {clean_number(boll.get('upper'))}。"},
            {"title": "关键位", "text": f"20日高低区间 {display_number(max(highs[-20:]))} / {display_number(min(lows[-20:]))}；局部支撑 {display_number(nearest_support)}，局部阻力 {display_number(nearest_resistance)}。"},
        ],
        "indicators": {
            "MA5": clean_number(ma.get("ma5")), "MA20": clean_number(ma20), "MA60": clean_number(ma60),
            "MACD": clean_number(macd.get("histogram")), "RSI12": clean_number(rsi12),
            "KDJ_J": clean_number(kdj.get("j")), "BOLL上轨": clean_number(boll.get("upper")),
            "BOLL下轨": clean_number(boll.get("lower")), "ATR14": clean_number(atr),
        },
        "levels": {"20日高": clean_number(max(highs[-20:])), "20日低": clean_number(min(lows[-20:])), "局部支撑": clean_number(nearest_support), "局部阻力": clean_number(nearest_resistance)},
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


def parse_js_payload(text: str) -> dict[str, Any]:
    raw = text.removeprefix("window.EXCHANGE_FUTURES_DATA = ").removesuffix(";\n")
    payload = json.loads(raw)
    return payload if isinstance(payload, dict) else {}


def previous_contracts() -> dict[str, dict[str, Any]]:
    """Keep the last verified contract for a product when a live endpoint is unavailable."""
    candidates: list[str] = []
    if OUTPUT.exists():
        candidates.append(OUTPUT.read_text(encoding="utf-8"))
    try:
        result = subprocess.run(
            ["git", "show", "HEAD:data/exchange_futures.js"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            candidates.append(result.stdout)
    except OSError:
        pass
    records: dict[str, dict[str, Any]] = {}
    for text in candidates:
        try:
            payload = parse_js_payload(text)
        except (ValueError, json.JSONDecodeError):
            continue
        for item in payload.get("contracts", []):
            if isinstance(item, dict) and item.get("product"):
                records.setdefault(str(item["product"]), item)
    return records


def fundamental_summary(name: str, category: str, headlines: list[dict[str, str]]) -> dict[str, Any]:
    factors = []
    for names, group_category, group_factors in FUNDAMENTAL_GROUPS:
        if name in names:
            category = group_category
            factors = [{"title": title, "text": text} for title, text in group_factors]
            break
    if not factors:
        factors = [
            {"title": "供给", "text": "该品种尚未建立专属基本面模板，需进一步核验产能、进口、政策和交割供给。"},
            {"title": "需求", "text": "需进一步核验下游开工、终端订单和替代品价格，暂不以分类标签替代具体研究。"},
            {"title": "库存与现货", "text": "需进一步核验库存、基差、仓单与现货成交，缺少数据时不做方向性判断。"},
        ]
    headline_note = "已匹配到直接热点，热点只作为研究线索，需结合原始报道和数据验证传导链。" if headlines else "未匹配到直接热点，基本面结论仅保留供需跟踪框架，不据此给出方向判断。"
    return {"category": category, "summary": f"{name}基本面围绕供给、需求和库存/成本三条线展开。{headline_note}", "factors": factors}


def build_contracts() -> list[dict[str, Any]]:
    if ak is None:
        raise RuntimeError("AkShare 未安装，无法生成主力合约列表")
    helper = load_technical_helper()
    levels_helper = load_levels_helper()
    symbols = ak.futures_symbol_mark()
    symbols = symbols[symbols["exchange"].isin(EXCHANGE_LABELS)]
    news = latest_news()
    fallback = previous_contracts()
    contracts = []
    for _, item in symbols.iterrows():
        product_name = str(item["symbol"])
        quotes = None
        for attempt in range(3):
            try:
                quotes = ak.futures_zh_realtime(symbol=product_name)
                if quotes is not None and not quotes.empty:
                    break
            except Exception:
                quotes = None
            time.sleep(attempt + 1)
        if quotes is None or quotes.empty:
            previous = fallback.get(product_name)
            if previous:
                contracts.append({
                    **previous,
                    "data_quality": "本次实时请求未返回该品种，保留上一次已验证主力合约与日线分析；请在下一次刷新时复核。",
                })
            continue
        candidates = quotes[quotes["symbol"].map(is_contract)].copy()
        if candidates.empty:
            previous = fallback.get(product_name)
            if previous:
                contracts.append({
                    **previous,
                    "data_quality": "本次实时请求未返回有效具体合约，保留上一次已验证主力合约与日线分析；请在下一次刷新时复核。",
                })
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
            "technical": technical_summary(helper, levels_helper, history, price),
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

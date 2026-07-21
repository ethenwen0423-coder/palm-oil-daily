#!/usr/bin/env python3
"""Generate five-exchange main-contract analysis data for the static research page."""

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
from zoneinfo import ZoneInfo

import requests

try:
    import akshare as ak  # type: ignore
except ImportError:  # pragma: no cover - deployment dependency
    ak = None


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "exchange_futures.js"
SHANGHAI = ZoneInfo("Asia/Shanghai")
TECHNICAL_HELPER = Path.home() / ".codex" / "skills" / "technical-analysis-helper" / "scripts" / "calculate_indicators.py"
LEVELS_HELPER = Path.home() / ".codex" / "skills" / "technical-analysis-helper" / "scripts" / "identify_levels.py"
NEWS_GLOB = ROOT / "source_runs" / "*" / "raw" / "mx_search_news.json"
SINA_DAILY_URL = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var_V21052021_4_12=/InnerFuturesNewService.getDailyKLine"

EXCHANGE_LABELS = {
    "大连商品交易所": "DCE",
    "郑州商品交易所": "CZCE",
    "上海期货交易所": "SHFE",
    "广州期货交易所": "GFEX",
    "中国金融期货交易所": "CFFEX",
}
REQUIRED_COMPLETE_EXCHANGES = {"SHFE", "GFEX", "CFFEX"}

CATEGORY_RULES = {
    "油脂油料": {"棕榈", "豆二", "豆粕", "豆油", "豆一", "菜油", "菜籽", "菜粕", "花生"},
    "谷物饲料": {"玉米", "玉米淀粉", "粳米", "粳稻", "早籼稻", "晚籼稻", "强麦"},
    "软商品": {"白糖", "棉花", "棉纱", "鲜苹果", "红枣", "鸡蛋", "生猪"},
    "黑色建材": {"铁矿石", "焦炭", "焦煤", "动力煤", "玻璃", "纯碱"},
    "能化材料": {"PVC", "塑料", "PP", "乙二醇", "苯乙烯", "液化石油气", "纯苯", "PTA", "郑醇", "尿素", "短纤", "烧碱", "二甲苯", "瓶级聚酯切片", "丙烯"},
    "能源化工": {"燃油", "原油", "橡胶", "沥青", "20号胶", "低硫燃料油", "丁二烯橡胶"},
    "有色金属": {"沪铝", "沪锌", "沪铜", "沪铅", "沪锡", "沪镍", "国际铜", "氧化铝", "铸造铝合金期货"},
    "贵金属": {"黄金", "白银", "铂", "钯"},
    "黑色金属": {"螺纹钢", "线材", "热轧卷板", "不锈钢"},
    "造纸航运": {"纸浆", "胶版印刷纸期货", "集运指数(欧线)期货"},
    "新能源材料": {"工业硅", "碳酸锂", "多晶硅"},
    "股指期货": {"沪深300指数期货", "上证50指数期货", "中证500指数期货", "中证1000股指期货"},
    "利率期货": {"2年期国债期货", "5年期国债期货", "10年期国债期货"},
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
    (
        {"工业硅", "碳酸锂", "多晶硅"},
        "新能源材料",
        [
            ("供给与产能", "跟踪新增产能、装置检修、产区开工与交割品供应，区分名义产能和有效产量。"),
            ("下游需求", "工业硅关注有机硅与铝合金，多晶硅关注硅片排产，碳酸锂关注动力与储能电池需求。"),
            ("库存与成本", "核验仓单、社会库存、生产成本和现货升贴水；高库存阶段需警惕盘面反弹持续性。"),
        ],
    ),
    (
        {"黄金", "白银", "铂", "钯"},
        "贵金属",
        [
            ("宏观定价", "跟踪实际利率、美元、通胀预期与央行政策，识别金融属性对贵金属价格的主导程度。"),
            ("供需结构", "白银、铂、钯需同时跟踪矿端供给、汽车与光伏等工业需求以及回收供应。"),
            ("内外盘价差", "核验人民币汇率、进口窗口、国内外价差和交割库存，避免把汇率变化误判为单边驱动。"),
        ],
    ),
    (
        {"沪铝", "沪锌", "沪铜", "沪铅", "沪锡", "沪镍", "国际铜", "氧化铝", "铸造铝合金期货"},
        "有色金属",
        [
            ("矿端与冶炼", "跟踪矿山供应、加工费、冶炼检修与新增产能，评估原料约束向精炼端的传导。"),
            ("需求", "观察电网、地产、汽车、家电和新能源订单，结合下游开工判断消费强弱。"),
            ("库存与价差", "核验交易所与社会库存、现货升贴水、进口盈亏和月差，判断去库是否得到现货确认。"),
        ],
    ),
    (
        {"燃油", "原油", "橡胶", "沥青", "20号胶", "低硫燃料油", "丁二烯橡胶"},
        "能源化工",
        [
            ("成本与供应", "跟踪国际原油、炼厂开工、装置检修、产区天气和进口到港，判断成本与供给弹性。"),
            ("下游需求", "观察航运、道路施工、轮胎与汽车产业链开工，区分季节性需求与订单趋势。"),
            ("库存与裂解", "核验港口和厂库库存、现货基差、裂解价差及内外盘窗口，判断产业利润传导。"),
        ],
    ),
    (
        {"螺纹钢", "线材", "热轧卷板", "不锈钢"},
        "黑色金属",
        [
            ("供给", "跟踪钢厂利润、高炉与电炉开工、产量及检修，判断供给收缩是否兑现。"),
            ("需求", "观察地产、基建、制造业和出口订单，结合表观消费与成交验证需求强度。"),
            ("库存与成本", "核验社库、厂库、原料成本、现货基差与卷螺价差，评估利润和库存压力。"),
        ],
    ),
    (
        {"纸浆", "胶版印刷纸期货", "集运指数(欧线)期货"},
        "造纸航运",
        [
            ("供给", "纸浆与纸品关注海外发运、进口到港和产线开工；集运指数关注运力投放与航线扰动。"),
            ("需求", "跟踪纸厂排产、出版包装需求、欧洲贸易与旺季订舱，确认终端改善能否持续。"),
            ("库存与现货", "核验港口库存、厂库、现货报价、运价指数和基差，注意不同交割口径的可比性。"),
        ],
    ),
    (
        {"沪深300指数期货", "上证50指数期货", "中证500指数期货", "中证1000股指期货"},
        "股指期货",
        [
            ("指数与风格", "跟踪标的指数、权重行业、大小盘风格和盈利预期，判断期指走势对应的现货驱动。"),
            ("资金与基差", "观察成交持仓、期现基差、移仓换月、ETF资金和北向相关资金线索。"),
            ("宏观与政策", "结合增长、流动性、风险偏好与政策预期，避免仅凭单一技术指标判断股指方向。"),
        ],
    ),
    (
        {"2年期国债期货", "5年期国债期货", "10年期国债期货"},
        "利率期货",
        [
            ("利率环境", "跟踪资金利率、央行操作、存单与国债收益率曲线，判断期限结构变化。"),
            ("基本面", "结合增长、通胀、财政供给与信贷数据，评估债券定价的宏观方向。"),
            ("基差与交割", "核验可交割券、转换因子、基差、IRR与跨期价差，关注移仓和交割月影响。"),
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


def resolve_helper(primary: Path, script_name: str) -> Path:
    """Prefer the configured helper path, with the active Codex skills directory as fallback."""
    candidates = [primary, Path.home() / ".codex" / "skills" / "technical-analysis-helper" / "scripts" / script_name]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return primary


def load_technical_helper():
    helper_path = resolve_helper(TECHNICAL_HELPER, "calculate_indicators.py")
    spec = importlib.util.spec_from_file_location("technical_analysis_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("technical-analysis-helper 不可用")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_levels_helper():
    helper_path = resolve_helper(LEVELS_HELPER, "identify_levels.py")
    spec = importlib.util.spec_from_file_location("technical_levels_helper", helper_path)
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
    symbols = symbols[symbols["exchange"].isin(EXCHANGE_LABELS)].copy()
    news = latest_news()
    fallback = previous_contracts()
    contracts = []
    total_products = len(symbols)
    for index, (_, item) in enumerate(symbols.iterrows(), start=1):
        product_name = str(item["symbol"])
        exchange_code = EXCHANGE_LABELS[str(item["exchange"])]
        print(f"[{index}/{total_products}] {exchange_code} {product_name}", flush=True)
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
            "exchange": exchange_code,
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
    expected = {
        (EXCHANGE_LABELS[str(item["exchange"])], str(item["symbol"]))
        for _, item in symbols.iterrows()
        if EXCHANGE_LABELS[str(item["exchange"])] in REQUIRED_COMPLETE_EXCHANGES
    }
    actual = {(str(item["exchange"]), str(item["product"])) for item in contracts}
    missing = sorted(expected - actual)
    if missing:
        missing_text = "、".join(f"{exchange}:{product}" for exchange, product in missing)
        raise RuntimeError(f"主力合约列表不完整，拒绝覆盖输出：{missing_text}")
    return sorted(contracts, key=lambda item: (item["exchange"], item["category"], item["product"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--update-session", choices=("morning", "midday", "close", "manual"), default="manual")
    args = parser.parse_args()
    contracts = build_contracts()
    now = datetime.now(SHANGHAI)
    payload = {
        "updated_at": now.strftime("%Y-%m-%d %H:%M"),
        "update_session": args.update_session,
        "timezone": "Asia/Shanghai",
        "source": "AkShare 实时行情与日线数据；技术指标由 technical-analysis-helper 生成；新闻热点来自最近一次已保存的资讯检索结果。",
        "contracts": contracts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(f"window.EXCHANGE_FUTURES_DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};\n", encoding="utf-8")
    print(f"updated {args.output} with {len(contracts)} contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

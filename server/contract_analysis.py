#!/usr/bin/env python3
"""On-demand, source-backed analysis for one published futures contract."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
SINA_QUOTE_URL = "https://hq.sinajs.cn/list=nf_{symbol}"
SINA_HISTORY_URL = (
    "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
    "var_V21052021_4_12=/InnerFuturesNewService.getDailyKLine"
)
SINA_INDEX_URL = "https://hq.sinajs.cn/list=s_sh000300,s_sh000016,s_sh000905,s_sh000852"
EASTMONEY_WARRANT_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
INDEX_VARIETIES = {
    "IF": ("000300", "沪深300"),
    "IH": ("000016", "上证50"),
    "IC": ("000905", "中证500"),
    "IM": ("000852", "中证1000"),
}
SYMBOL_RE = re.compile(r"^[A-Z]{1,8}\d{3,4}$")


class ContractAnalysisError(RuntimeError):
    status = 502
    code = "analysis_failed"


class InvalidSymbol(ContractAnalysisError):
    status = 400
    code = "invalid_symbol"


class UnknownContract(ContractAnalysisError):
    status = 404
    code = "contract_not_found"


def _number(value: Any) -> float | None:
    try:
        if value in (None, "", "-"):
            return None
        number = float(str(value).replace(",", ""))
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _rounded(value: Any, digits: int = 2) -> float | None:
    number = _number(value)
    return round(number, digits) if number is not None else None


def _request_text(url: str, *, params: dict[str, str] | None = None, timeout: int = 10) -> str:
    target = f"{url}?{urlencode(params)}" if params else url
    request = Request(
        target,
        headers={"Referer": "https://finance.sina.com.cn/", "User-Agent": "Mozilla/5.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
    try:
        return raw.decode("gb18030")
    except UnicodeDecodeError:
        return raw.decode("utf-8", "replace")


def _source(name: str, status: str, observed_at: str | None, detail: str) -> dict[str, Any]:
    return {"name": name, "status": status, "observed_at": observed_at, "detail": detail}


def _load_contract(data_root: Path, symbol: str) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        payload = json.loads((data_root / "exchange_futures.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractAnalysisError("全品种合约数据集不可用") from exc
    for item in payload.get("contracts", []):
        if isinstance(item, dict) and str(item.get("symbol", "")).upper() == symbol:
            return payload, dict(item)
    raise UnknownContract(f"当前主力合约清单中没有 {symbol}")


def fetch_quote(symbol: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        text = _request_text(SINA_QUOTE_URL.format(symbol=symbol), timeout=8)
        match = re.search(r'="([^"]*)"', text)
        values = match.group(1).split(",") if match and match.group(1) else []
        if not values:
            return None, _source("新浪财经期货行情", "unavailable", None, "上游未返回该合约")
        if values[0] and not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", values[0]):
            price = _number(values[8])
            previous = _number(values[10])
            quote = {
                "price": _rounded(price),
                "open": _rounded(values[2]),
                "high": _rounded(values[3]),
                "low": _rounded(values[4]),
                "volume": int(_number(values[14]) or 0),
                "open_interest": int(_number(values[13]) or 0),
                "trade_date": values[17][:10] if len(values) > 17 else "",
            }
        else:
            price = _number(values[3])
            previous = _number(values[16]) if len(values) > 16 else None
            quote = {
                "price": _rounded(price),
                "open": _rounded(values[0]),
                "high": _rounded(values[1]),
                "low": _rounded(values[2]),
                "volume": int(_number(values[4]) or 0),
                "open_interest": int(_number(values[6]) or 0),
                "trade_date": "",
            }
        quote["change_pct"] = (
            round((price - previous) / previous * 100, 2)
            if price is not None and previous not in (None, 0)
            else None
        )
        observed = quote.get("trade_date") or datetime.now(SHANGHAI).isoformat(timespec="seconds")
        return quote, _source("新浪财经期货行情", "ready", str(observed), "按所选具体合约即时查询")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        return None, _source("新浪财经期货行情", "unavailable", None, type(exc).__name__)


def fetch_history(symbol: str) -> tuple[list[dict[str, float]], dict[str, Any]]:
    try:
        text = _request_text(
            SINA_HISTORY_URL,
            params={"symbol": symbol, "type": "2021_04_12"},
            timeout=12,
        )
        match = re.search(r"=\((\[.*\])\)", text, re.S)
        rows = json.loads(match.group(1)) if match else []
        result: list[dict[str, float]] = []
        last_date = None
        for row in rows[-220:]:
            if isinstance(row, dict):
                values = [_number(row.get(key)) for key in ("o", "h", "l", "c")]
                last_date = row.get("d") or row.get("date") or last_date
            elif isinstance(row, list) and len(row) >= 5:
                values = [_number(row[index]) for index in range(1, 5)]
                last_date = row[0] or last_date
            else:
                continue
            if any(value is None for value in values):
                continue
            result.append(dict(zip(("open", "high", "low", "close"), values)))
        state = "ready" if len(result) >= 60 else "insufficient"
        return result, _source("新浪财经期货日线", state, str(last_date or "") or None, f"有效样本 {len(result)} 条")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        return [], _source("新浪财经期货日线", "unavailable", None, type(exc).__name__)


def _sma(values: list[float], window: int) -> float | None:
    return sum(values[-window:]) / window if len(values) >= window else None


def _ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    output = [values[0]]
    for value in values[1:]:
        output.append(alpha * value + (1 - alpha) * output[-1])
    return output


def _rsi(values: list[float], window: int = 14) -> float | None:
    if len(values) <= window:
        return None
    changes = [values[index] - values[index - 1] for index in range(1, len(values))]
    gains = [max(change, 0) for change in changes[-window:]]
    losses = [max(-change, 0) for change in changes[-window:]]
    average_gain = sum(gains) / window
    average_loss = sum(losses) / window
    if average_loss == 0:
        return 100.0
    return 100 - 100 / (1 + average_gain / average_loss)


def build_technical(history: list[dict[str, float]], price: float | None) -> dict[str, Any]:
    if len(history) < 60 or price is None:
        return {"status": "需进一步核验", "trend": "样本不足", "summary": "即时日线样本不足，暂不输出方向判断。", "indicators": {}, "levels": {}}
    closes = [row["close"] for row in history]
    closes[-1] = price
    ma20, ma60 = _sma(closes, 20), _sma(closes, 60)
    rsi14 = _rsi(closes)
    ema12, ema26 = _ema_series(closes, 12), _ema_series(closes, 26)
    dif = ema12[-1] - ema26[-1]
    macd_series = [a - b for a, b in zip(ema12[-len(ema26):], ema26)]
    dea = _ema_series(macd_series, 9)[-1]
    if ma20 is not None and ma60 is not None and price > ma20 > ma60:
        trend, status = "偏强", "bullish"
    elif ma20 is not None and ma60 is not None and price < ma20 < ma60:
        trend, status = "偏弱", "bearish"
    else:
        trend, status = "震荡", "neutral"
    summary = f"最新价相对 MA20/MA60 呈{trend}结构；RSI14 为 {rsi14:.1f}，MACD DIF-DEA 为 {dif-dea:+.2f}。"
    recent = history[-20:]
    return {
        "status": status,
        "trend": trend,
        "summary": summary,
        "indicators": {"MA20": _rounded(ma20), "MA60": _rounded(ma60), "RSI14": _rounded(rsi14), "MACD": _rounded(dif - dea)},
        "levels": {"20日支撑": _rounded(min(row["low"] for row in recent)), "20日压力": _rounded(max(row["high"] for row in recent))},
        "details": [
            {"title": "价格结构", "text": f"最新价 {price:g}，MA20 {_rounded(ma20)}，MA60 {_rounded(ma60)}。"},
            {"title": "动量", "text": "RSI 与 MACD 仅描述当前技术状态，不替代基本面确认。"},
        ],
    }


def fetch_index_spot(variety: str, futures_price: float | None) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    meta = INDEX_VARIETIES.get(variety)
    if not meta:
        return None, _source("标的指数行情", "not_applicable", None, "非股指期货")
    code, name = meta
    try:
        text = _request_text(SINA_INDEX_URL, timeout=8)
        match = re.search(rf'hq_str_s_sh{code}="([^"]*)"', text)
        values = match.group(1).split(",") if match else []
        spot = _number(values[1]) if len(values) > 3 else None
        if spot is None:
            raise ValueError("missing index spot")
        basis = futures_price - spot if futures_price is not None else None
        observed = datetime.now(SHANGHAI).isoformat(timespec="seconds")
        evidence = {
            "title": f"标的指数与期现｜{observed[5:16]}",
            "text": f"{name}最新 {spot:,.2f}，涨跌 {(_number(values[3]) or 0):+.2f}%；期指－现货 {basis:+.2f}。" if basis is not None else f"{name}最新 {spot:,.2f}，期现差待核验。",
        }
        return evidence, _source("新浪财经标的指数", "ready", observed, f"{name} {spot:,.2f}")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        return None, _source("新浪财经标的指数", "unavailable", None, type(exc).__name__)


def fetch_warrant(variety: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    params = {
        "reportName": "RPT_FUTU_STOCKDATA",
        "columns": "SECURITY_CODE,TRADE_DATE,ON_WARRANT_NUM,ADDCHANGE",
        "filter": f'(SECURITY_CODE="{variety}")',
        "pageNumber": "1",
        "pageSize": "10",
        "sortTypes": "-1",
        "sortColumns": "TRADE_DATE",
        "source": "WEB",
        "client": "WEB",
    }
    try:
        payload = json.loads(_request_text(EASTMONEY_WARRANT_URL, params=params, timeout=10))
        rows = (((payload or {}).get("result") or {}).get("data") or [])
        row = rows[0] if rows else None
        value = _number(row.get("ON_WARRANT_NUM")) if row else None
        if value is None:
            return None, _source("东方财富注册仓单", "unavailable", None, "该品种暂无可验证仓单记录")
        observed = str(row.get("TRADE_DATE") or "")[:10]
        change = _number(row.get("ADDCHANGE"))
        evidence = {
            "title": f"注册仓单｜{observed or '日期待核验'}",
            "text": f"最新注册仓单 {value:,.0f}，当日变化 {change:+,.0f}；仓单不等于社会总库存。" if change is not None else f"最新注册仓单 {value:,.0f}，日变动待核验；仓单不等于社会总库存。",
        }
        return evidence, _source("东方财富注册仓单", "ready", observed or None, f"品种代码 {variety}")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        return None, _source("东方财富注册仓单", "unavailable", None, type(exc).__name__)


def _variety(symbol: str) -> str:
    match = re.match(r"[A-Z]+", symbol)
    return match.group(0) if match else ""


def _build_judgement(contract: dict[str, Any], technical: dict[str, Any], fundamental: dict[str, Any]) -> dict[str, Any]:
    status = technical.get("status")
    evidence_count = int(fundamental.get("evidence_count") or 0)
    if status == "bullish":
        stance = "偏强观察"
    elif status == "bearish":
        stance = "偏弱观察"
    elif status == "neutral":
        stance = "震荡等待"
    else:
        stance = "数据不足"
    confidence = "中" if status in {"bullish", "bearish", "neutral"} and evidence_count > 0 else "低"
    evidence = [technical.get("summary")]
    factors = fundamental.get("factors") or []
    if factors:
        evidence.append(factors[0].get("text"))
    evidence = [str(item) for item in evidence if item]
    return {
        "stance": stance,
        "confidence": confidence,
        "summary": f"{contract.get('product', symbol)}当前为{stance}；技术结构已即时重算，基本面有 {evidence_count} 项可验证证据。" if (symbol := str(contract.get("symbol") or "")) else stance,
        "key_evidence": evidence[:3],
        "risk": "本判断是行情与结构化证据的条件判断；休市报价、低频基本面或来源降级时不可视为实时交易指令。",
    }


def analyze_contract(data_root: Path, raw_symbol: str) -> dict[str, Any]:
    symbol = str(raw_symbol or "").strip().upper()
    if not SYMBOL_RE.fullmatch(symbol):
        raise InvalidSymbol("合约代码格式无效")
    dataset, contract = _load_contract(data_root, symbol)
    sources: list[dict[str, Any]] = []

    quote, quote_source = fetch_quote(symbol)
    sources.append(quote_source)
    if quote:
        contract.update({key: value for key, value in quote.items() if value not in (None, "")})

    history, history_source = fetch_history(symbol)
    sources.append(history_source)
    contract["technical"] = build_technical(history, _number(contract.get("price")))

    fundamental = dict(contract.get("fundamental") or {})
    factors = list(fundamental.get("factors") or [])
    variety = _variety(symbol)
    if variety in INDEX_VARIETIES:
        evidence, fundamental_source = fetch_index_spot(variety, _number(contract.get("price")))
    else:
        evidence, fundamental_source = fetch_warrant(variety)
    sources.append(fundamental_source)
    if evidence:
        factors = [evidence] + [item for item in factors if item.get("title") != evidence.get("title")]
        fundamental["evidence_count"] = max(1, int(fundamental.get("evidence_count") or 0))
        fundamental["evidence_status"] = "observed"
        fundamental["summary"] = f"已按 {symbol} 即时检查相关基本面源；最新可验证证据置于首位，低频数据保留原日期。"
    else:
        fundamental["summary"] = f"已按 {symbol} 检查相关基本面源，但本次未取得新增可验证数值；以下为最近发布快照与跟踪框架。"
    fundamental["factors"] = factors
    contract["fundamental"] = fundamental
    contract["judgement"] = _build_judgement(contract, contract["technical"], fundamental)

    degraded = any(item["status"] in {"unavailable", "insufficient"} for item in sources)
    contract["data_quality"] = (
        "本次按所选合约请求后台；行情与日线独立即时查询，基本面按品种调用相关源。"
        "来源失败时保留最近发布快照，并在来源状态中明确标注。"
    )
    return {
        "symbol": symbol,
        "generated_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        "snapshot_updated_at": dataset.get("updated_at"),
        "degraded": degraded,
        "contract": contract,
        "sources": sources,
    }

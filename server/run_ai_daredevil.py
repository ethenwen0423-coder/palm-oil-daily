#!/usr/bin/env python3
"""Run the persistent AI敢死队 virtual fund and publish its read-only snapshot.

Trading decisions use completed daily bars. Hourly runs only execute already
planned next-open virtual orders and mark existing real PYYMM positions.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import importlib.util
import json
import math
import os
import re
import secrets
import statistics
import subprocess
import sys
import tempfile
import time as time_module
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
MODEL_VERSION = "palm-oil-v2-real-contract-indicators-carry5-main-contract"
ALLOCATION_POLICY_VERSION = "cross-sector-signal-strength-v1"
INITIAL_CAPITAL = 1_000_000.0
FUND_FILE = "ai_daredevil.json"
READY_MARKER = ".server-ai-daredevil-ready.json"
SCAN_AUDIT_FILE = "latest_scan_audit.json"
MARGIN_BOOK_FILE = "exchange_margin_rates.json"
CONTRACT_RE = re.compile(r"^[A-Z]{1,3}[0-9]{3,4}$")
DAILY_HISTORY_HOSTS = ("stock2.finance.sina.com.cn", "stock.finance.sina.com.cn")
DAILY_FETCH_ATTEMPTS = 3

# Multiplier is a contract specification. Margin is resolved separately for
# every exact PYYMM contract from exchange-standard data.
PRODUCTS = {
    "FG": {"name": "玻璃", "sector": "建材", "multiplier": 20.0},
    "MA": {"name": "甲醇", "sector": "化工", "multiplier": 10.0},
    "TA": {"name": "PTA", "sector": "化工", "multiplier": 5.0},
    "SA": {"name": "纯碱", "sector": "建材", "multiplier": 20.0},
    "V": {"name": "PVC", "sector": "化工", "multiplier": 5.0},
    "RB": {"name": "螺纹钢", "sector": "黑色", "multiplier": 10.0},
    "FU": {"name": "燃料油", "sector": "能源", "multiplier": 10.0},
    "PP": {"name": "聚丙烯", "sector": "化工", "multiplier": 5.0},
    "AG": {"name": "白银", "sector": "贵金属", "multiplier": 15.0},
    "JD": {"name": "鸡蛋", "sector": "农产品", "multiplier": 10.0},
    "EG": {"name": "乙二醇", "sector": "化工", "multiplier": 10.0},
    "L": {"name": "塑料", "sector": "化工", "multiplier": 5.0},
    "JM": {"name": "焦煤", "sector": "黑色", "multiplier": 60.0},
    "EB": {"name": "苯乙烯", "sector": "化工", "multiplier": 5.0},
    "HC": {"name": "热卷", "sector": "黑色", "multiplier": 10.0},
    "BU": {"name": "沥青", "sector": "能源", "multiplier": 10.0},
    "SH": {"name": "烧碱", "sector": "化工", "multiplier": 30.0},
    "P": {"name": "棕榈油", "sector": "油脂油料", "multiplier": 10.0},
    "Y": {"name": "豆油", "sector": "油脂油料", "multiplier": 10.0},
    "OI": {"name": "菜油", "sector": "油脂油料", "multiplier": 10.0},
    "M": {"name": "豆粕", "sector": "油脂油料", "multiplier": 10.0},
    "RM": {"name": "菜粕", "sector": "油脂油料", "multiplier": 10.0},
    "C": {"name": "玉米", "sector": "谷物", "multiplier": 10.0},
    "CF": {"name": "棉花", "sector": "软商品", "multiplier": 5.0},
    "SR": {"name": "白糖", "sector": "软商品", "multiplier": 10.0},
    "UR": {"name": "尿素", "sector": "化工", "multiplier": 20.0},
    "LH": {"name": "生猪", "sector": "农产品", "multiplier": 16.0},
    "J": {"name": "焦炭", "sector": "黑色", "multiplier": 100.0},
    "I": {"name": "铁矿石", "sector": "黑色", "multiplier": 100.0},
    "PS": {"name": "多晶硅", "sector": "新能源", "multiplier": 3.0},
    "SI": {"name": "工业硅", "sector": "新能源", "multiplier": 5.0},
    "LC": {"name": "碳酸锂", "sector": "新能源", "multiplier": 1.0},
    "CU": {"name": "沪铜", "sector": "有色金属", "multiplier": 5.0},
    "AL": {"name": "沪铝", "sector": "有色金属", "multiplier": 5.0},
    "ZN": {"name": "沪锌", "sector": "有色金属", "multiplier": 5.0},
    "NI": {"name": "沪镍", "sector": "有色金属", "multiplier": 1.0},
    "AU": {"name": "黄金", "sector": "贵金属", "multiplier": 1000.0},
    "SC": {"name": "原油", "sector": "能源", "multiplier": 1000.0},
    "RU": {"name": "橡胶", "sector": "化工", "multiplier": 10.0},
    "SP": {"name": "纸浆", "sector": "轻工", "multiplier": 10.0},
}

# ak.futures_zh_realtime accepts the display names returned by
# futures_symbol_mark(), not exchange variety codes such as P or TA.
PRODUCT_REALTIME_SYMBOL = {
    "FG": "玻璃", "MA": "郑醇", "TA": "PTA", "SA": "纯碱", "V": "PVC",
    "RB": "螺纹钢", "FU": "燃油", "PP": "PP", "AG": "白银", "JD": "鸡蛋",
    "EG": "乙二醇", "L": "塑料", "JM": "焦煤", "EB": "苯乙烯", "HC": "热轧卷板",
    "BU": "沥青", "SH": "烧碱", "P": "棕榈", "Y": "豆油", "OI": "菜油",
    "M": "豆粕", "RM": "菜粕",
    "C": "玉米", "CF": "棉花", "SR": "白糖", "UR": "尿素",
    "LH": "生猪", "J": "焦炭", "I": "铁矿石", "PS": "多晶硅",
    "SI": "工业硅", "LC": "碳酸锂", "CU": "沪铜", "AL": "沪铝",
    "ZN": "沪锌", "NI": "沪镍", "AU": "黄金", "SC": "原油",
    "RU": "橡胶", "SP": "纸浆",
}
PRODUCT_REALTIME_NODE = {
    "FG": "bl_qh", "MA": "zc_qh", "TA": "pta_qh", "SA": "cj_qh", "V": "pvc_qh",
    "RB": "lwg_qh", "FU": "ry_qh", "PP": "jbx_qh", "AG": "by_qh", "JD": "jd_qh",
    "EG": "yec_qh", "L": "lldpe_qh", "JM": "jm_qh", "EB": "byx_qh", "HC": "rzjb_qh",
    "BU": "lq_qh", "SH": "sh_qh", "P": "zly_qh", "Y": "dy_qh", "OI": "czy_qh",
    "M": "dp_qh", "RM": "czp_qh", "C": "hym_qh", "CF": "mh_qh", "SR": "bst_qh",
    "UR": "ns_qh", "LH": "lh_qh", "J": "jt_qh", "I": "tks_qh", "PS": "ps_qh",
    "SI": "si_qh", "LC": "lc_qh", "CU": "tong_qh", "AL": "lv_qh", "ZN": "xing_qh",
    "NI": "ni_qh", "AU": "hj_qh", "SC": "yy_qh", "RU": "xj_qh", "SP": "zj_qh",
}


class RuntimeErrorSafe(RuntimeError):
    pass


def now_shanghai() -> datetime:
    return datetime.now(SHANGHAI)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def load_python(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeErrorSafe(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_margin_resolver():
    return load_python(Path(__file__).resolve().parent / "exchange_margin_rates.py", "ai_daredevil_exchange_margins")


def load_components(site_root: Path):
    skill = site_root / "skills" / "manage-bollinger-rsi-futures-fund"
    model_root = skill / "model"
    sys.path.insert(0, str(model_root))
    ledger = load_python(skill / "scripts" / "fund_ledger.py", "ai_daredevil_ledger")
    model = load_python(model_root / "futures_main_contract_bollinger_rsi_model.py", "ai_daredevil_model")
    signal_model = sys.modules.get("palm_oil_bollinger_rsi_ma6_strategy")
    if model.MODEL_VERSION != MODEL_VERSION or signal_model is None:
        raise RuntimeErrorSafe("authoritative model version is unavailable")
    return ledger, model, signal_model


def init_ledger(ledger, state_dir: Path) -> None:
    if not (state_dir / "state.json").exists():
        ledger.command_init(SimpleNamespace(
            state_dir=state_dir, initial_capital=INITIAL_CAPITAL, if_missing=True
        ))
    verification = ledger.command_verify(SimpleNamespace(state_dir=state_dir))
    if not verification.get("ok"):
        raise RuntimeErrorSafe("ledger verification failed: " + "; ".join(verification["errors"]))


def normalized_contract(value: Any) -> str | None:
    candidate = re.sub(r"[^A-Za-z0-9]", "", str(value or "")).upper()
    return candidate if CONTRACT_RE.fullmatch(candidate) else None


def numeric(value: Any) -> float | None:
    try:
        parsed = float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def find_field(row: dict[str, Any], names: tuple[str, ...]) -> Any:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for name in names:
        if name in row:
            return row[name]
        if name.lower() in lowered:
            return lowered[name.lower()]
    for key, value in row.items():
        if any(name.lower() in str(key).lower() for name in names):
            return value
    return None


def quote_from_row(row: dict[str, Any], contract: str, source: str) -> dict[str, Any] | None:
    row_contract = normalized_contract(find_field(row, ("symbol", "合约", "合约代码", "代码", "期货代码")))
    if row_contract != contract:
        return None
    last = numeric(find_field(row, ("trade", "price", "最新价", "现价", "收盘价")))
    opening = numeric(find_field(row, ("open", "开盘价", "今开")))
    if last is None and opening is None:
        return None
    date_value = find_field(row, ("trade_date", "date", "交易日期", "日期"))
    time_value = find_field(row, ("time", "data_time", "时间", "更新时间"))
    observed = f"{date_value or ''} {time_value or ''}".strip() or now_shanghai().isoformat(timespec="seconds")
    return {
        "contract": contract,
        "last": last or opening,
        "open": opening,
        "observed_at": observed,
        "trade_date": str(date_value or "")[:10] or None,
        "source_date": str(date_value or "").strip() or None,
        "source_time": str(time_value or "").strip() or None,
        "source": source,
    }


def akshare_quotes(contracts: list[str], timeout: int = 12) -> tuple[dict[str, dict[str, Any]], str | None]:
    """Read the same Sina delivery-contract feed used by AkShare, with a timeout.

    ``ak.futures_zh_realtime`` calls ``requests.get`` without a timeout. A slow
    upstream therefore used to block the minute refresh after the close scan
    had already finished. Direct, concurrent requests preserve the exact raw
    feed while making the wall-clock boundary explicit.
    """
    output: dict[str, dict[str, Any]] = {}
    errors = []
    by_variety: dict[str, list[str]] = {}
    for contract in contracts:
        variety = re.match(r"[A-Z]+", contract).group(0)
        by_variety.setdefault(variety, []).append(contract)
    request_timeout = min(max(int(timeout), 3), 12)

    def fetch_variety(variety: str, expected: list[str]):
        try:
            url = (
                "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
                "Market_Center.getHQFuturesData?"
                + urllib.parse.urlencode({
                    "page": "1", "sort": "position", "asc": "0",
                    "node": PRODUCT_REALTIME_NODE[variety], "base": "futures",
                })
            )
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=request_timeout) as response:
                rows = json.loads(response.read().decode("utf-8"))
            found = {}
            for row in rows if isinstance(rows, list) else []:
                for contract in expected:
                    quote = quote_from_row(row, contract, "新浪期货实时行情（AKShare 同源）")
                    if quote:
                        found[contract] = quote
            return found, None
        except Exception as exc:  # remote schema/network boundary
            return {}, f"{variety}:{type(exc).__name__}"

    with ThreadPoolExecutor(max_workers=min(8, len(by_variety))) as pool:
        futures = [pool.submit(fetch_variety, variety, expected) for variety, expected in by_variety.items()]
        for future in as_completed(futures):
            found, error = future.result()
            output.update(found)
            if error:
                errors.append(error)
    return output, ", ".join(errors) or None


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeErrorSafe("non-object API response")
    return value


def hithink_quote(contract: str, timeout: int) -> tuple[dict[str, Any] | None, str | None]:
    key = os.environ.get("IWENCAI_API_KEY", "").strip()
    if not key:
        return None, "IWENCAI_API_KEY 未配置"
    queries = [f"{contract}期货 今日开盘价 最新价 交易日期", f"{contract} 开盘价 最新价"]
    last_error = None
    for attempt, query in enumerate(queries):
        headers = {
            "Authorization": f"Bearer {key}", "Content-Type": "application/json",
            "X-Claw-Call-Type": "normal" if attempt == 0 else "retry",
            "X-Claw-Skill-Id": "hithink-market-query", "X-Claw-Skill-Version": "1.0.0",
            "X-Claw-Plugin-Id": "none", "X-Claw-Plugin-Version": "none",
            "X-Claw-Trace-Id": secrets.token_hex(32),
        }
        try:
            response = post_json(
                "https://openapi.iwencai.com/v1/query2data",
                {"query": query, "page": "1", "limit": "10", "is_cache": "0", "expand_index": "true"},
                headers, timeout,
            )
            for row in response.get("datas", []):
                quote = quote_from_row(row, contract, "同花顺问财行情 Skill")
                if quote:
                    quote["trace_id"] = headers["X-Claw-Trace-Id"]
                    quote["query"] = query
                    return quote, None
            last_error = "未返回精确合约行情"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {str(exc)[:120]}"
    return None, last_error


def http_get_json(url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeErrorSafe("non-object API response")
    return value


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def htfc_quote(contract: str, product_name: str, timeout: int) -> tuple[dict[str, Any] | None, str | None]:
    base = os.environ.get("HTFC_BASE_URL", "").strip().rstrip("/")
    key = os.environ.get("HTFC_API_KEY", "").strip()
    if not base or not key:
        return None, "HTFC_BASE_URL/HTFC_API_KEY 未配置"
    headers = {"Content-Type": "application/json", "apikey": key}
    prefix = "/htfc/htfc_research/hrms/report"
    try:
        tree = http_get_json(base + prefix + "/list_report_label_tree", headers, timeout)
        candidates = []
        for row in walk(tree.get("data", tree)):
            if product_name in str(row.get("name", "")) and row.get("code"):
                candidates.append(row)
        unique = {str(row["code"]): row for row in candidates}
        if len(unique) != 1:
            return None, "品种标签无法唯一确认"
        code = next(iter(unique))
        query = urllib.parse.urlencode({"varNum": code, "period": "-1month"})
        payload = http_get_json(base + prefix + "/k/report_k_line?" + query, headers, timeout)
        for row in walk(payload.get("data", payload)):
            quote = quote_from_row(row, contract, "华泰智能 K 线 Skill")
            if quote:
                return quote, None
        return None, "K线未包含精确 PYYMM 合约，拒绝用产品代理价"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {str(exc)[:120]}"


def resolve_quotes(contracts: list[str], timeout: int) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    contracts = sorted(set(filter(None, contracts)))
    if not contracts:
        return {}, [
            {"priority": "主来源", "name": "新浪期货实时行情（AKShare 同源）", "state": "ready", "note": "当前无持仓或待执行订单，本轮无需请求"},
            {"priority": "回退 1", "name": "同花顺问财行情 Skill", "state": "fallback", "note": "仅在 AKShare 精确合约行情缺失时启用"},
            {"priority": "回退 2", "name": "华泰智能 K 线 Skill", "state": "fallback", "note": "仅接受包含精确 PYYMM 合约的原始 K 线"},
        ]
    quotes, ak_error = akshare_quotes(contracts, timeout)
    source_rows = [{
        "priority": "主来源", "name": "新浪期货实时行情（AKShare 同源）",
        "state": "ready" if quotes else "failed",
        "note": f"命中 {len(quotes)}/{len(contracts)} 个精确合约" + (f"；{ak_error}" if ak_error else ""),
    }]
    iw_errors = []
    htfc_errors = []
    iw_hits = htfc_hits = 0
    for contract in contracts:
        if contract in quotes:
            continue
        quote, error = hithink_quote(contract, timeout)
        if quote:
            quotes[contract] = quote
            iw_hits += 1
            continue
        iw_errors.append(f"{contract}:{error}")
        variety = re.match(r"[A-Z]+", contract).group(0)
        quote, error = htfc_quote(contract, PRODUCTS.get(variety, {}).get("name", variety), timeout)
        if quote:
            quotes[contract] = quote
            htfc_hits += 1
        else:
            htfc_errors.append(f"{contract}:{error}")
    source_rows.extend([
        {"priority": "回退 1", "name": "同花顺问财行情 Skill", "state": "ready" if iw_hits else "fallback",
         "note": f"命中 {iw_hits} 个精确合约" if iw_hits else (iw_errors[0] if iw_errors else "本轮无需回退")},
        {"priority": "回退 2", "name": "华泰智能 K 线 Skill", "state": "ready" if htfc_hits else "fallback",
         "note": f"命中 {htfc_hits} 个精确合约" if htfc_hits else (htfc_errors[0] if htfc_errors else "本轮无需回退")},
    ])
    return quotes, source_rows


def current_contracts(data_root: Path) -> dict[str, list[str]]:
    payload = read_json(data_root / "contracts" / "current_contracts.json", {})
    products = payload.get("products", {}) if isinstance(payload, dict) else {}
    output = {}
    for variety in PRODUCTS:
        values = []
        for row in products.get(variety, []):
            contract = normalized_contract(row.get("symbol"))
            if contract:
                values.append(contract)
        if values:
            output[variety] = values
    exchange = read_json(data_root / "exchange_futures.json", {})
    for row in exchange.get("contracts", []) if isinstance(exchange, dict) else []:
        contract = normalized_contract(row.get("symbol"))
        if not contract:
            continue
        variety_match = re.match(r"[A-Z]+", contract)
        variety = variety_match.group(0) if variety_match else ""
        if variety in PRODUCTS:
            output.setdefault(variety, []).append(contract)
    output = {variety: sorted(set(values)) for variety, values in output.items()}
    # Always augment the published main-contract snapshot with the most liquid
    # currently listed delivery months. This lets the model reconstruct the
    # T-1 volume-selected main schedule without ever requesting a continuous
    # symbol. Four contracts bounds the close-scan runtime and avoids dormant
    # far-month prints becoming false rollover candidates.
    # Call Sina directly with an explicit timeout. AkShare's wrapper does not
    # set one here, so a slow endpoint can retain the global automation lock
    # indefinitely even when discovery itself is concurrent.
    def discover_liquid_contracts(variety: str) -> tuple[str, list[str]]:
        try:
            url = (
                "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
                "Market_Center.getHQFuturesData?"
                + urllib.parse.urlencode({
                    "page": "1", "sort": "position", "asc": "0",
                    "node": PRODUCT_REALTIME_NODE[variety], "base": "futures",
                })
            )
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=12) as response:
                rows = json.loads(response.read().decode("utf-8"))
            ranked = []
            for row in rows if isinstance(rows, list) else []:
                contract = normalized_contract(find_field(row, ("symbol", "合约", "合约代码", "代码", "期货代码")))
                if not contract or not contract.startswith(variety) or contract.endswith("0"):
                    continue
                volume = numeric(find_field(row, ("volume", "成交量"))) or 0.0
                open_interest = numeric(find_field(row, ("position", "hold", "open_interest", "持仓量"))) or 0.0
                if volume > 0 or open_interest > 0:
                    ranked.append((volume, open_interest, contract))
            liquid = [contract for _volume, _hold, contract in sorted(ranked, reverse=True)[:4]]
            return variety, liquid
        except Exception:
            return variety, []

    # Realtime discovery is network-bound and has one request per variety. A
    # bounded cross-variety pool plus the per-request timeout keeps the close
    # scan within the unattended service budget.
    with ThreadPoolExecutor(max_workers=min(12, len(PRODUCTS))) as pool:
        futures = [pool.submit(discover_liquid_contracts, variety) for variety in PRODUCTS]
        for future in as_completed(futures):
            variety, liquid = future.result()
            if liquid:
                output[variety] = sorted(set(output.get(variety, []) + liquid))
    return output


def _fetch_daily_once(contract: str, host: str):
    import pandas as pd
    url = (
        f"https://{host}/futures/api/jsonp.php/var%20_contract_history="
        "/InnerFuturesNewService.getDailyKLine?"
        + urllib.parse.urlencode({"symbol": contract, "type": "2021_04_12"})
    )
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        text = response.read().decode("utf-8")
    start, end = text.find("=("), text.rfind(");")
    if start < 0 or end <= start:
        raise RuntimeErrorSafe(f"{contract}: invalid daily response")
    frame = pd.DataFrame(json.loads(text[start + 2:end]))
    if frame is None or frame.empty:
        raise RuntimeErrorSafe(f"{contract}: empty daily bars")
    frame.columns = ["date", "open", "high", "low", "close", "volume", "hold", "settle"]
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    for column in ("open", "high", "low", "close", "volume", "hold"):
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["date", "open", "high", "low", "close", "volume"]).sort_values("date")


def fetch_daily(contract: str):
    """Fetch one real delivery contract with bounded cross-host retries.

    Sina's two history hosts expose the same delivery-contract series. The
    close scan used to turn a single transient URLError into a public skipped
    signal. Retrying on the alternate host keeps that failure visible only
    when all bounded attempts have actually failed.
    """
    last_error: Exception | None = None
    for attempt in range(DAILY_FETCH_ATTEMPTS):
        host = DAILY_HISTORY_HOSTS[attempt % len(DAILY_HISTORY_HOSTS)]
        try:
            return _fetch_daily_once(contract, host)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = exc
            if attempt + 1 < DAILY_FETCH_ATTEMPTS:
                contract_spread = sum(ord(value) for value in contract) % 7
                time_module.sleep(0.45 * (2 ** attempt) + contract_spread * 0.04)
    reason = getattr(last_error, "reason", None)
    detail = type(reason or last_error).__name__ if last_error else "UnknownError"
    raise RuntimeErrorSafe(
        f"{contract}: daily source unavailable after {DAILY_FETCH_ATTEMPTS} attempts ({detail})"
    ) from last_error


def completed_close_cutoff(generated_at: datetime) -> date:
    """Latest date that may be treated as a completed China futures day bar."""
    local = generated_at.astimezone(SHANGHAI) if generated_at.tzinfo else generated_at.replace(tzinfo=SHANGHAI)
    return local.date() if local.time().replace(tzinfo=None) >= time(15, 5) else local.date() - timedelta(days=1)


def next_trade_date(after: date) -> date:
    try:
        import akshare as ak
        import pandas as pd
        calendar = ak.tool_trade_date_hist_sina()
        values = sorted(pd.to_datetime(calendar["trade_date"]).dt.date.unique())
        return next(value for value in values if value > after)
    except Exception as exc:
        raise RuntimeErrorSafe(f"next exchange trading day unavailable: {type(exc).__name__}") from exc


def allocation_score(variety: str, direction: int, indicator_row: Any, selection_row: Any) -> tuple[float, dict[str, float], str]:
    configured = os.environ.get("AI_DAREDEVIL_ALLOCATION_SCORES_JSON", "").strip()
    if configured:
        try:
            value = numeric(json.loads(configured).get(variety))
            if value is not None:
                return value, {"configured_score": value}, "配置的组合评分"
        except json.JSONDecodeError:
            pass
    atr = max(float(indicator_row.atr), 1e-12)
    close = float(indicator_row.close)
    breakout_atr = min(abs(close - float(indicator_row.ma20)) / atr, 2.0) / 2.0
    trend_atr = min(abs(close - float(indicator_row.ma6)) / atr, 3.0) / 3.0
    rsi = numeric(getattr(indicator_row, "rsi", None))
    rsi_alignment = max(0.0, min(1.0, direction * ((rsi if rsi is not None else 50.0) - 50.0) / 50.0))
    turnover = max(
        float(selection_row.volume) * float(selection_row.close) * PRODUCTS[variety]["multiplier"], 1.0
    )
    liquidity = max(0.0, min(1.0, (math.log10(turnover) - 6.0) / 5.0))
    components = {
        "breakout_atr": round(breakout_atr, 6),
        "trend_atr": round(trend_atr, 6),
        "rsi_alignment": round(rsi_alignment, 6),
        "liquidity": round(liquidity, 6),
    }
    score = 0.40 * breakout_atr + 0.25 * trend_atr + 0.20 * rsi_alignment + 0.15 * liquidity
    return round(score, 6), components, "跨板块实时信号强度与流动性排序"


def margin_rate(contract: str, margin_book: dict[str, Any] | None,
                side: int | str | None = None) -> dict[str, Any] | None:
    rates = margin_book.get("rates", {}) if isinstance(margin_book, dict) else {}
    row = rates.get(str(contract).upper()) if isinstance(rates, dict) else None
    if not isinstance(row, dict):
        return None
    side_text = str(side or "").upper()
    if side == 1 or side_text.endswith("LONG"):
        side_name, key = "long", "long_margin_rate"
    elif side == -1 or side_text.endswith("SHORT"):
        side_name, key = "short", "short_margin_rate"
    else:
        side_name, key = "higher-side", "margin_rate"
    rate = numeric(row.get(key))
    if rate is None or not 0 < rate <= 1:
        return None
    selected = dict(row)
    selected["margin_rate"] = rate
    selected["margin_applied_side"] = side_name
    return selected


def fee_rate(variety: str) -> float:
    configured = numeric(os.environ.get(f"AI_DAREDEVIL_FEE_RATE_{variety}"))
    return configured if configured is not None and configured >= 0 else 0.0004


def scan_signals(site_root: Path, data_root: Path, state: dict[str, Any], model,
                 generated_at: datetime | None = None,
                 margin_book: dict[str, Any] | None = None) -> tuple[dict[str, Any] | None, list[dict[str, Any]], dict[str, Any]]:
    import pandas as pd
    generated_at = generated_at or now_shanghai()
    close_cutoff = completed_close_cutoff(generated_at)
    contracts_by_variety = current_contracts(data_root)
    signals = []
    skipped = []
    signal_dates = []
    strategy_path = Path(state["_strategy_path"])
    strategy = read_json(strategy_path, {"last_close": {}, "positions": {}, "blocked": {}})
    previous_audit = read_json(strategy_path.parent / SCAN_AUDIT_FILE, {})
    previous_candidates = {
        row.get("variety"): row for row in previous_audit.get("signal_candidates", [])
        if isinstance(row, dict) and row.get("variety")
    } if isinstance(previous_audit, dict) else {}
    audit = {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "completed_close_cutoff": close_cutoff.isoformat(),
        "allocation_policy_version": ALLOCATION_POLICY_VERSION,
        "universe_count": len(PRODUCTS), "discovered_count": len(contracts_by_variety),
        "sector_count": len({row["sector"] for row in PRODUCTS.values()}),
        "evaluated_count": 0, "candidate_count": 0, "order_count": 0,
        "blocked_candidate_count": 0,
        "missing_varieties": [variety for variety in PRODUCTS if variety not in contracts_by_variety],
        "signal_candidates": [],
    }
    for variety in PRODUCTS:
        contracts = contracts_by_variety.get(variety, [])
        if not contracts:
            skipped.append({"variety": variety, "reason": "未发现可核验的真实交割月合约"})
            continue
        frames = {}
        with ThreadPoolExecutor(max_workers=min(6, len(contracts))) as pool:
            futures = {pool.submit(fetch_daily, contract): contract for contract in contracts}
            for future in as_completed(futures):
                contract = futures[future]
                try:
                    frame = future.result()
                    frame = frame.loc[frame.date.dt.date.le(close_cutoff)].copy()
                    if frame.empty:
                        raise RuntimeErrorSafe(f"{contract}: no completed daily bars through {close_cutoff}")
                    frames[contract] = frame
                except Exception as exc:
                    detail = str(exc).strip() if isinstance(exc, RuntimeErrorSafe) else type(exc).__name__
                    skipped.append({
                        "variety": variety, "contract": contract,
                        "reason": f"日线抓取失败（已重试{DAILY_FETCH_ATTEMPTS}次）：{detail}",
                    })
        if not frames:
            continue
        raw_parts = []
        for candidate, frame in frames.items():
            part = frame.copy()
            part["contract"] = candidate
            part["variety"] = variety
            raw_parts.append(part)
        raw = pd.concat(raw_parts, ignore_index=True).sort_values(["date", "contract"])
        # This runtime makes only the latest completed-close decision. A bounded
        # recent window is sufficient for MA20/MA6/RSI14/ATR14 and avoids
        # treating dormant far-month prints from the distant past as a current
        # main-contract rollover.
        raw = raw.loc[raw.date.ge(raw.date.max() - pd.Timedelta(days=120))].copy()
        try:
            active = model.build_lagged_main_schedule(raw)
            prepared = model.prepare_contract_local_main(active, raw)
        except Exception as exc:
            skipped.append({"variety": variety, "reason": f"正式真实合约模型准备失败：{type(exc).__name__}"})
            continue
        latest = active.date.max().date()
        completed = prepared.loc[prepared.date.dt.date.eq(latest)]
        if len(completed) != 1:
            skipped.append({"variety": variety, "reason": "D日T-1主力指标行不唯一"})
            continue
        last = completed.iloc[0]
        signal_contract = str(last.contract)
        latest_selection_rows = raw.loc[raw.date.dt.date.eq(latest) & raw.volume.gt(0)]
        if latest_selection_rows.empty:
            skipped.append({"variety": variety, "reason": "D日缺少下一交易日主力选择成交量"})
            continue
        raw_last = latest_selection_rows.loc[latest_selection_rows.volume.idxmax()]
        contract = str(raw_last.contract)         # D+1执行合约由D日成交量决定
        execution_close = float(raw_last.close)
        signal_atr = float(last.atr)
        signal_date = last.date.date()
        signal_dates.append(signal_date)
        audit["evaluated_count"] += 1
        previous_policy = previous_audit.get("allocation_policy_version") if isinstance(previous_audit, dict) else None
        if strategy.setdefault("last_close", {}).get(variety) == signal_date.isoformat() and previous_policy == ALLOCATION_POLICY_VERSION:
            previous = previous_candidates.get(variety)
            if previous and previous.get("signal_date") == signal_date.isoformat():
                audit["candidate_count"] += 1
                audit["signal_candidates"].append(previous)
                previous_action = str(previous.get("action", "")).upper()
                position = state.get("positions", {}).get(variety)
                if previous.get("eligible") and previous_action in {"ENTER_LONG", "ENTER_SHORT"} and not position:
                    # Rebuild the order-ready signal as well as its audit row.
                    # The deterministic ledger order id makes this idempotent,
                    # while a margin outage can be retried without recomputing
                    # or losing the completed-close candidate.
                    item = {
                        "variety": variety, "name": PRODUCTS[variety]["name"],
                        "sector": PRODUCTS[variety]["sector"], "contract": contract,
                        "action": previous_action, "signal_date": signal_date.isoformat(),
                        "execution_date": next_trade_date(signal_date).isoformat(),
                        "reference_price": execution_close, "atr14": signal_atr,
                        "multiplier": PRODUCTS[variety]["multiplier"],
                        "margin_rate": None, "margin_source": None,
                        "margin_source_url": None, "margin_as_of": None,
                        "margin_official_direct": None, "margin_applied_side": None,
                        "fee_rate": fee_rate(variety),
                        "reason": "同一已完成收盘日候选重放（账本订单号幂等去重）",
                        "selection_volume_t_minus_1": float(raw_last.volume),
                        "selection_open_interest_t_minus_1": numeric(raw_last.get("hold")),
                        "score": previous.get("score"),
                        "score_components": previous.get("score_components", {}),
                        "score_basis": str(previous.get("score_basis") or "跨板块实时信号强度与流动性排序")
                        + "；仅用于订单优先级，不代表预测收益率",
                    }
                    signals.append(item)
                    audit["order_count"] += 1
            continue
        position = state.get("positions", {}).get(variety)
        action = reason = None
        side = int(position["side"]) if position else 0
        track = strategy.setdefault("positions", {}).setdefault(variety, {}) if position else {}
        if position:
            if position["contract"] != signal_contract:
                skipped.append({"variety": variety, "contract": position["contract"], "reason": "账本持仓与D日T-1主力不一致，需先核验换月"})
                strategy["last_close"][variety] = signal_date.isoformat()
                continue
            if position["contract"] != contract:
                strategy.setdefault("pending_rolls", {})[variety] = {
                    "from": position["contract"], "to": contract,
                    "execution_date": next_trade_date(signal_date).isoformat(),
                    "reason": "T-1成交量主力换月",
                }
            entry = float(position["average_price"])
            atr = float(position.get("entry_atr") or last.atr)
            track["high_water"] = max(float(track.get("high_water", entry)), float(last.high))
            track["low_water"] = min(float(track.get("low_water", entry)), float(last.low))
            divergence = (side == 1 and bool(last.bearish_divergence)) or (side == -1 and bool(last.bullish_divergence))
            stop_active = side == -1 or (track["high_water"] - entry) / atr >= 0.75
            broke_ma6 = float(last.close) < float(last.ma6) if side == 1 else float(last.close) > float(last.ma6)
            track["stop_count"] = int(track.get("stop_count", 0)) + 1 if stop_active and broke_ma6 else 0
            required = 2 if side == 1 else 1
            if divergence:
                action, reason = ("EXIT_LONG" if side == 1 else "EXIT_SHORT"), "RSI背离退出"
            elif track["stop_count"] >= required:
                action, reason = ("EXIT_LONG" if side == 1 else "EXIT_SHORT"), "非对称MA6退出"
                strategy.setdefault("blocked", {})[variety] = side
            elif int(position.get("layers", 1)) < 2 and side * (float(last.close) - entry) / atr >= 1.0:
                action, reason = ("ADD_LONG" if side == 1 else "ADD_SHORT"), "浮盈达到1倍入场ATR，仅加仓一次"
        else:
            direction = 1 if bool(last.long_signal) else (-1 if bool(last.short_signal) else 0)
            carry_reason = None
            if not direction and contract != signal_contract:
                direction, carry_atr = model._roll_carry_pending(
                    prepared.attrs.get("contract_signals"), contract,
                    pd.Timestamp(next_trade_date(signal_date)),
                    int(prepared.attrs.get("roll_lookback", 5)),
                )
                if direction and not math.isnan(float(carry_atr)):
                    signal_atr = float(carry_atr)
                    carry_reason = "主力换月回看新合约近5日未消耗MA20信号"
            blocked = int(strategy.setdefault("blocked", {}).get(variety, 0))
            if direction == -blocked:
                strategy["blocked"][variety] = 0
                blocked = 0
            if direction and direction != blocked:
                score, score_components, score_basis = allocation_score(variety, direction, last, raw_last)
                audit["candidate_count"] += 1
                audit["signal_candidates"].append({
                    "variety": variety, "name": PRODUCTS[variety]["name"], "contract": contract,
                    "action": "ENTER_LONG" if direction == 1 else "ENTER_SHORT",
                    "signal_date": signal_date.isoformat(), "eligible": True,
                    "sector": PRODUCTS[variety]["sector"], "score": score,
                    "score_components": score_components, "score_basis": score_basis,
                })
                action = "ENTER_LONG" if direction == 1 else "ENTER_SHORT"
                reason = carry_reason or "真实交割月自身日线收盘穿越MA20"
        if action:
            order_contract = position["contract"] if position and action.startswith("EXIT") else contract
            margin = margin_rate(order_contract, margin_book, action)
            if not action.startswith("EXIT") and margin_book is not None and margin is None:
                issue = {
                    "variety": variety, "contract": order_contract,
                    "reason": "缺少新鲜的真实合约交易所保证金比例，需进一步核验",
                }
                skipped.append(issue)
                continue
            item = {
                "variety": variety, "name": PRODUCTS[variety]["name"], "sector": PRODUCTS[variety]["sector"],
                "contract": order_contract, "action": action, "signal_date": signal_date.isoformat(),
                "execution_date": next_trade_date(signal_date).isoformat(), "reference_price": execution_close,
                "atr14": signal_atr, "multiplier": PRODUCTS[variety]["multiplier"],
                "margin_rate": (margin.get("margin_rate") if margin else position.get("margin_rate") if position else None),
                "margin_source": (margin.get("source") if margin else position.get("margin_source") if position else None),
                "margin_source_url": (margin.get("source_url") if margin else position.get("margin_source_url") if position else None),
                "margin_as_of": (margin.get("source_updated_at") if margin else position.get("margin_as_of") if position else None),
                "margin_official_direct": (margin.get("official_direct") if margin else position.get("margin_official_direct") if position else None),
                "margin_applied_side": (margin.get("margin_applied_side") if margin else position.get("margin_applied_side") if position else None),
                "fee_rate": fee_rate(variety),
                "reason": reason, "selection_volume_t_minus_1": float(raw_last.volume),
                "selection_open_interest_t_minus_1": numeric(raw_last.get("hold")),
            }
            if action.startswith("ENTER"):
                score, score_components, score_basis = allocation_score(variety, 1 if action.endswith("LONG") else -1, last, raw_last)
                item["score"] = score
                item["score_components"] = score_components
                item["score_basis"] = score_basis + "；仅用于订单优先级，不代表预测收益率"
            signals.append(item)
            audit["order_count"] += 1
        strategy["last_close"][variety] = signal_date.isoformat()
    atomic_json(strategy_path, strategy)
    audit["as_of"] = max(signal_dates).isoformat() if signal_dates else None
    audit["coverage_status"] = "complete" if audit["evaluated_count"] == audit["universe_count"] else "partial"
    audit["issues"] = skipped
    if not signal_dates:
        return None, skipped, audit
    return {
        "as_of": max(signal_dates).isoformat(), "completed_bar": True,
        "model_version": MODEL_VERSION,
        "source": "AKShare futures_zh_daily_sina actual PYYMM; T-1 volume selection",
        "indicator_history_calendar_days": 120,
        "signals": signals,
    }, skipped, audit


def margin_contracts(state: dict[str, Any], snapshot: dict[str, Any] | None = None) -> list[str]:
    contracts = [row["contract"] for row in state.get("positions", {}).values()]
    contracts.extend(
        row["contract"] for row in state.get("pending_orders", [])
        if row.get("status") == "pending" and not str(row.get("action", "")).startswith("EXIT")
    )
    if snapshot:
        contracts.extend(
            row["contract"] for row in snapshot.get("signals", [])
            if not str(row.get("action", "")).startswith("EXIT")
        )
    return sorted({contract.upper() for contract in contracts if contract})


def resolve_margin_book(state_dir: Path, contracts: list[str], now: datetime, timeout: int,
                        *, force: bool = False) -> dict[str, Any]:
    resolver = load_margin_resolver()
    path = state_dir / MARGIN_BOOK_FILE
    raw_cached = read_json(path, {})
    raw_cached_rates = raw_cached.get("rates", {}) if isinstance(raw_cached, dict) else {}
    reusable_cached = {
        contract: row for contract, row in raw_cached_rates.items()
        if contract in contracts and isinstance(row, dict)
        and resolver.source_is_fresh(row, now.date())
    } if isinstance(raw_cached_rates, dict) else {}
    cached = resolver.load_cached_margin_book(path, contracts, now.date())
    fetched_today = str((cached or {}).get("fetched_at", ""))[:10] == now.date().isoformat()
    if cached is not None and fetched_today and not force:
        atomic_json(path, cached)
        return cached
    if not contracts:
        return {
            "schema_version": 1, "as_of": now.date().isoformat(),
            "fetched_at": now.isoformat(timespec="seconds"), "coverage_status": "complete",
            "expected_count": 0, "validated_count": 0, "unresolved_contracts": [],
            "rates": {}, "validation": "当前无持仓、待执行开仓或新增信号，无需保证金参数",
        }
    fresh = resolver.fetch_margin_book(contracts, now.date(), timeout=max(timeout, 30))
    if fresh.get("coverage_status") != "complete" and reusable_cached:
        refreshed_contracts = set(fresh.get("rates", {}))
        merged = dict(reusable_cached)
        merged.update(fresh.get("rates", {}))
        fresh["rates"] = {contract: merged[contract] for contract in contracts if contract in merged}
        fresh["validated_count"] = len(fresh["rates"])
        fresh["unresolved_contracts"] = sorted(set(contracts) - set(fresh["rates"]))
        fresh["coverage_status"] = "complete" if not fresh["unresolved_contracts"] else "partial"
        fresh["cache_fallback_used"] = True
        fresh["cache_fallback_contracts"] = sorted(set(reusable_cached) - refreshed_contracts)
    atomic_json(path, fresh)
    return fresh


def apply_snapshot_margins(snapshot: dict[str, Any] | None, margin_book: dict[str, Any],
                           skipped: list[dict[str, Any]], audit: dict[str, Any]) -> dict[str, Any] | None:
    if not snapshot:
        return None
    accepted = []
    for signal in snapshot.get("signals", []):
        if str(signal.get("action", "")).startswith("EXIT"):
            accepted.append(signal)
            continue
        row = margin_rate(signal["contract"], margin_book, signal.get("action"))
        if row is None:
            skipped.append({
                "variety": signal.get("variety"), "contract": signal.get("contract"),
                "reason": "缺少新鲜的真实合约交易所保证金比例，信号不生成订单，需进一步核验",
            })
            continue
        signal.update({
            "margin_rate": row["margin_rate"], "margin_source": row.get("source"),
            "margin_source_url": row.get("source_url"),
            "margin_as_of": row.get("source_updated_at"),
            "margin_official_direct": bool(row.get("official_direct")),
            "margin_applied_side": row.get("margin_applied_side"),
        })
        accepted.append(signal)
    snapshot["signals"] = accepted
    audit["order_count"] = len(accepted)
    audit["issues"] = skipped
    return snapshot


def update_ledger_margins(ledger, state_dir: Path, margin_book: dict[str, Any]) -> dict[str, Any]:
    rates = list(margin_book.get("rates", {}).values())
    if not rates:
        return ledger.command_status(SimpleNamespace(state_dir=state_dir))
    path = state_dir / "latest_margin_rates.json"
    atomic_json(path, {
        "as_of": margin_book.get("as_of"),
        "source": "合约级交易所标准保证金审计",
        "rates": rates,
    })
    return ledger.command_update_margins(SimpleNamespace(state_dir=state_dir, rates=path))


def refresh_reason(now: datetime, requested: str | None) -> str:
    if requested:
        return requested
    minutes = now.hour * 60 + now.minute
    if 8 * 60 + 55 <= minutes <= 9 * 60 + 20:
        return "09:00 日盘开盘刷新"
    if 13 * 60 + 25 <= minutes <= 13 * 60 + 50:
        return "13:30 午盘开盘刷新"
    if 20 * 60 + 55 <= minutes <= 21 * 60 + 20:
        return "21:00 夜盘开盘刷新"
    return "每小时持仓盯市"


def load_events(state_dir: Path, target: str) -> list[dict[str, Any]]:
    events = []
    try:
        lines = (state_dir / "trade_ledger.jsonl").read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return events
    for line in lines:
        row = json.loads(line)
        event_date = str(row.get("date") or row.get("timestamp", ""))[:10]
        if event_date == target and row.get("event") in {"FILL", "ROLL", "ORDER_CANCELLED"}:
            events.append(row)
    return events


def latest_plan_skips(state_dir: Path, as_of: str | None) -> list[dict[str, Any]]:
    try:
        lines = (state_dir / "trade_ledger.jsonl").read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    for line in reversed(lines):
        row = json.loads(line)
        if row.get("event") != "ORDER_PLAN" or (as_of and row.get("as_of") != as_of):
            continue
        result = []
        for decision in row.get("decisions", []):
            if decision.get("status") not in {"skipped", "rejected"}:
                continue
            reason = str(decision.get("reason") or "账本规则未通过")
            if reason == "signal order was already recorded":
                continue
            signal = decision.get("signal", {})
            result.append({
                "variety": signal.get("variety"), "name": signal.get("name"),
                "contract": signal.get("contract"), "action": signal.get("action"),
                "score": signal.get("score"),
                "reason": f"账本未生成订单：{reason}",
            })
        return result
    return []


def equity_curve(state_dir: Path, state: dict[str, Any], today: str) -> list[dict[str, Any]]:
    observed = {}
    path = state_dir / "snapshots.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("event") == "DAILY_MARK" and row.get("date"):
                observed[str(row["date"])] = float(row["equity"])
    observed[today] = float(state["equity"])
    result = []
    previous = None
    for day, value in sorted(observed.items()):
        result.append({"date": day, "equity": value, "net_value": value / INITIAL_CAPITAL,
                       "daily_return": 0.0 if previous is None else value / previous - 1})
        previous = value
    return result


def performance(curve: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    if len(curve) < 30:
        return None, None
    start, end = date.fromisoformat(curve[0]["date"]), date.fromisoformat(curve[-1]["date"])
    elapsed = (end - start).days
    if elapsed < 90:
        return None, None
    annual = (curve[-1]["equity"] / curve[0]["equity"]) ** (365.25 / elapsed) - 1
    returns = [float(row["daily_return"]) for row in curve[1:]]
    vol = statistics.stdev(returns) if len(returns) > 1 else 0
    sharpe = statistics.mean(returns) / vol * math.sqrt(242) if vol else None
    return annual, sharpe


def next_refresh(now: datetime) -> str:
    candidates = []
    for offset in range(3):
        day = (now + timedelta(days=offset)).date()
        if day.weekday() >= 5:
            continue
        for value in (time(9), time(13, 30), time(21)):
            point = datetime.combine(day, value, SHANGHAI)
            if point > now:
                candidates.append(point)
        hourly = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        if hourly.date() == day:
            candidates.append(hourly)
    return min(candidates).isoformat(timespec="seconds") if candidates else None


def public_snapshot(state_dir: Path, state: dict[str, Any], sources: list[dict[str, Any]], reason: str,
                    skipped: list[dict[str, Any]], scan_audit: dict[str, Any], now: datetime) -> dict[str, Any]:
    curve = equity_curve(state_dir, state, now.date().isoformat())
    annual, sharpe = performance(curve)
    quote_observations = read_json(state_dir / "latest_quote_observations.json", {})
    margin_book = read_json(state_dir / MARGIN_BOOK_FILE, {})
    observed_by_contract = quote_observations.get("quotes", {}) if isinstance(quote_observations, dict) else {}
    positions = []
    for position in state.get("positions", {}).values():
        row = dict(position)
        row["weight"] = float(row.get("notional", 0)) / float(state["equity"]) if state["equity"] else 0
        row["price_source"] = row.get("mark_source", "基金账本成交价")
        observation = observed_by_contract.get(str(row.get("contract", "")), {})
        observed_price = numeric(observation.get("price")) if isinstance(observation, dict) else None
        same_mark = (
            observed_price is not None
            and abs(observed_price - float(row.get("last_price", 0))) <= 1e-9
            and observation.get("trade_date") == row.get("last_mark_date")
        )
        row["price_time"] = observation.get("observed_at") if same_mark else (row.get("last_mark_date") or row.get("entry_date"))
        if same_mark:
            row["source_price_time"] = observation.get("source_observed_at")
        positions.append(row)
    pending = [row for row in state.get("pending_orders", []) if row.get("status") == "pending"]
    effective_skipped = list(skipped)
    seen_skips = {(row.get("variety"), row.get("contract"), row.get("reason")) for row in effective_skipped}
    for row in latest_plan_skips(state_dir, scan_audit.get("as_of")):
        identity = (row.get("variety"), row.get("contract"), row.get("reason"))
        if identity not in seen_skips:
            effective_skipped.append(row)
            seen_skips.add(identity)
    strategy = read_json(state_dir / "strategy_state.json", {})
    for variety, roll in strategy.get("pending_rolls", {}).items():
        pending.append({
            "order_id": f"roll_{variety}_{roll.get('execution_date')}", "status": "pending",
            "execution_date": roll.get("execution_date"), "variety": variety,
            "name": PRODUCTS.get(variety, {}).get("name", variety),
            "contract": f"{roll.get('from')}→{roll.get('to')}", "action": "ROLL",
            "quantity": state.get("positions", {}).get(variety, {}).get("quantity", 0),
            "reason": roll.get("reason", "主力换月"),
        })
    events = load_events(state_dir, now.date().isoformat())
    price_ok = not positions or all(row.get("mark_source") for row in positions)
    margin_ok = not positions or all(row.get("margin_source") and row.get("margin_as_of") for row in positions)
    status = "ready" if price_ok and margin_ok else "degraded"
    summary = {
        "initial_capital": INITIAL_CAPITAL, "equity": state["equity"],
        "net_value": state["equity"] / INITIAL_CAPITAL, "cash": state["cash"],
        "available_cash": state["cash"] - state["used_margin"], "used_margin": state["used_margin"],
        "margin_usage": state["used_margin"] / state["equity"] if state["equity"] else 0,
        "gross_exposure_multiple": state["gross_notional"] / state["equity"] if state["equity"] else 0,
        "daily_pnl": curve[-1]["equity"] - curve[-2]["equity"] if len(curve) > 1 else 0,
        "realized_pnl": state["realized_pnl"], "unrealized_pnl": state["unrealized_pnl"],
        "total_fees": state["total_fees"], "cumulative_return": state["equity"] / INITIAL_CAPITAL - 1,
        "annualized_return": annual, "sharpe": sharpe, "max_drawdown": state["max_drawdown"],
    }
    return {
        "schema_version": 1, "status": status,
        "status_label": ("账本正常 · 当前空仓" if not positions else ("账本与持仓行情正常" if status == "ready" else "部分持仓行情需进一步核验")),
        "generated_at": now.isoformat(timespec="seconds"), "market_date": state.get("last_mark_date"),
        "refresh_reason": reason,
        "price_source": " / ".join(sorted({row.get("mark_source", "") for row in positions if row.get("mark_source")})) or "尚无持仓，无需盯市",
        "next_refresh": next_refresh(now),
        "model": {"name": "布林带模型", "version": MODEL_VERSION, "capital_policy": "独立100万元权益复利",
                  "execution": "完整日线确认，下一交易日开盘执行"},
        "summary": summary, "equity_curve": curve, "positions": positions,
        "today_trades": events, "pending_orders": pending, "skipped_signals": effective_skipped,
        "scan_audit": scan_audit,
        "margin_audit": {
            key: value for key, value in margin_book.items()
            if key != "rates"
        } | {
            "contracts": list((margin_book.get("rates") or {}).values())
            if isinstance(margin_book.get("rates"), dict) else []
        },
        "refresh_schedule": [
            {"label": "日盘开盘", "time": "09:00", "purpose": "获取真实开盘价并处理待执行订单"},
            {"label": "午盘开盘", "time": "13:30", "purpose": "补核成交与持仓盯市"},
            {"label": "夜盘开盘", "time": "21:00", "purpose": "获取夜盘开盘价并处理可交易品种"},
            {"label": "交易时段盯市", "time": "每分钟", "purpose": "仅用当日精确合约实时行情更新持仓价格、权益和净值"},
        ],
        "sources": sources,
        "governance": {"virtual_only": True, "scanned_universe": list(PRODUCTS),
                       "eligible_default": list(PRODUCTS),
                       "allocation_policy_version": ALLOCATION_POLICY_VERSION,
                       "allocation_policy": "全策略池平等候选，按真实主力合约信号强度与流动性排序；组合受品种和板块上限约束",
                       "margin_note": "按真实PYYMM逐合约交易所一般/投机保证金计提；多单使用多头比例、空单使用空头比例，缺失或过期则禁止新增风险，不包含期货公司加收"},
        "ai_notice": "本页面由 AI 基于所列真实合约行情、模型信号和虚拟基金账本生成，不代表任何来源方官方立场，不构成投资建议；虚拟成交不等于真实成交，请自行核验。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(os.environ.get("PALM_OIL_SITE_ROOT", "/srv/palm-oil-daily/site")))
    parser.add_argument("--live-data-root", type=Path, default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", "/srv/palm-oil-daily/live-data")))
    parser.add_argument("--state-root", type=Path, default=Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", "/srv/palm-oil-daily/state")))
    parser.add_argument("--reason")
    parser.add_argument("--close-scan", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--now", help="test-only ISO timestamp")
    args = parser.parse_args()
    site_root = args.site_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_dir = (args.state_root.resolve() / "ai-daredevil")
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = args.state_root.resolve() / "automation.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.fromisoformat(args.now).astimezone(SHANGHAI) if args.now else now_shanghai()
    with lock_path.open("a+") as lock:
        if not args.now:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        ledger, model, _signal_model = load_components(site_root)
        init_ledger(ledger, state_dir)
        state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        state["_strategy_path"] = str(state_dir / "strategy_state.json")
        scan_audit_path = state_dir / SCAN_AUDIT_FILE
        scan_audit = read_json(scan_audit_path, {})
        skipped = list(scan_audit.get("issues", [])) if isinstance(scan_audit, dict) else []
        automatic_close_scan = now.weekday() < 5 and time(15, 20) <= now.time().replace(tzinfo=None) <= time(15, 50)
        catch_up_window = now.weekday() < 5 and time(15, 20) <= now.time().replace(tzinfo=None) <= time(20, 55)
        last_scan_day = str(scan_audit.get("generated_at", ""))[:10] if isinstance(scan_audit, dict) else ""
        catch_up_scan = not args.now and catch_up_window and last_scan_day != now.date().isoformat()
        should_scan = args.close_scan or automatic_close_scan or catch_up_scan
        snapshot = None
        if should_scan:
            snapshot, skipped, scan_audit = scan_signals(site_root, live_data_root, state, model, now)
        contracts_requiring_margin = margin_contracts(state, snapshot)
        pending_margin_rolls = read_json(state_dir / "strategy_state.json", {}).get("pending_rolls", {})
        for roll in pending_margin_rolls.values():
            contracts_requiring_margin.extend([roll.get("from"), roll.get("to")])
        contracts_requiring_margin = sorted({contract for contract in contracts_requiring_margin if contract})
        margin_book = resolve_margin_book(
            state_dir, contracts_requiring_margin, now, args.timeout, force=should_scan
        )
        snapshot = apply_snapshot_margins(snapshot, margin_book, skipped, scan_audit)
        state = update_ledger_margins(ledger, state_dir, margin_book)
        state["_strategy_path"] = str(state_dir / "strategy_state.json")
        if should_scan:
            atomic_json(scan_audit_path, scan_audit)
            if snapshot:
                signal_path = state_dir / "latest_signals.json"
                atomic_json(signal_path, snapshot)
                ledger.command_plan(SimpleNamespace(state_dir=state_dir, signals=signal_path))
                state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
                state["_strategy_path"] = str(state_dir / "strategy_state.json")
        needed = [row["contract"] for row in state.get("positions", {}).values()]
        needed += [row["contract"] for row in state.get("pending_orders", []) if row.get("status") == "pending"]
        strategy = read_json(state_dir / "strategy_state.json", {})
        for roll in strategy.get("pending_rolls", {}).values():
            needed.extend([roll["from"], roll["to"]])
        quotes, sources = resolve_quotes(needed, args.timeout)
        today = now.date().isoformat()
        pending_orders = [row for row in state.get("pending_orders", []) if row.get("status") == "pending"]
        for order in [row for row in pending_orders if str(row.get("action", "")).startswith("EXIT")]:
            if order.get("status") != "pending" or order.get("execution_date") != today:
                continue
            quote = quotes.get(order["contract"])
            if quote and quote.get("open") and quote.get("trade_date") == today:
                ledger.command_fill(SimpleNamespace(
                    state_dir=state_dir, order_id=order["order_id"], date=today,
                    price=float(quote["open"]), fee=None, allow_date_mismatch=False,
                ))
        state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        strategy = read_json(state_dir / "strategy_state.json", {})
        pending_rolls = strategy.get("pending_rolls", {})
        for variety, roll in list(pending_rolls.items()):
            position = state.get("positions", {}).get(variety)
            if not position:
                pending_rolls.pop(variety, None)
                continue
            if roll.get("execution_date") != today:
                continue
            if margin_rate(roll["to"], margin_book, position.get("side")) is None:
                continue
            old_quote, new_quote = quotes.get(roll["from"]), quotes.get(roll["to"])
            dates_ok = old_quote and new_quote and old_quote.get("trade_date") == today and new_quote.get("trade_date") == today
            if dates_ok and old_quote.get("open") and new_quote.get("open"):
                ledger.command_roll(SimpleNamespace(
                    state_dir=state_dir, variety=variety, new_contract=roll["to"], date=today,
                    old_price=float(old_quote["open"]), new_price=float(new_quote["open"]),
                ))
                pending_rolls.pop(variety, None)
                state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
                state = update_ledger_margins(ledger, state_dir, margin_book)
        strategy["pending_rolls"] = pending_rolls
        atomic_json(state_dir / "strategy_state.json", strategy)
        for order in [row for row in pending_orders if not str(row.get("action", "")).startswith("EXIT")]:
            if order.get("execution_date") != today:
                continue
            if margin_rate(order["contract"], margin_book, order.get("action")) is None:
                continue
            quote = quotes.get(order["contract"])
            if quote and quote.get("open") and quote.get("trade_date") == today:
                ledger.command_fill(SimpleNamespace(
                    state_dir=state_dir, order_id=order["order_id"], date=today,
                    price=float(quote["open"]), fee=None, allow_date_mismatch=False,
                ))
        state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        positions = state.get("positions", {})
        if positions and all(position["contract"] in quotes for position in positions.values()):
            marks = {"as_of": today, "source": "hourly exact-contract quote fallback chain", "prices": [
                {"variety": variety, "contract": position["contract"],
                 "price": quotes[position["contract"]]["last"], "source": quotes[position["contract"]]["source"]}
                for variety, position in positions.items()
            ]}
            mark_path = state_dir / "latest_marks.json"
            atomic_json(mark_path, marks)
            ledger.command_mark(SimpleNamespace(state_dir=state_dir, prices=mark_path))
        state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        payload = public_snapshot(state_dir, state, sources, refresh_reason(now, args.reason), skipped, scan_audit, now)
        atomic_json(live_data_root / FUND_FILE, payload)
        atomic_json(live_data_root / READY_MARKER, {
            "schema_version": 1, "generated_at": now.isoformat(timespec="seconds"),
            "session": "close-scan" if should_scan else "hourly", "owner": "server-ai-daredevil",
        })
    pure_ai_status = "disabled"
    if os.environ.get("AI_DAREDEVIL_SKIP_PURE_AI", "").strip().lower() not in {"1", "true", "yes"}:
        command = [
            sys.executable, str(site_root / "server" / "run_pure_ai_fund.py"),
            "--site-root", str(site_root), "--live-data-root", str(live_data_root),
            "--state-root", str(args.state_root.resolve()),
            "--timeout", os.environ.get("PURE_AI_FUND_TIMEOUT", "300"),
        ]
        if args.reason:
            command.extend(["--reason", args.reason])
        if args.close_scan:
            command.append("--close-scan")
        if args.now:
            command.extend(["--now", args.now])
        try:
            completed = subprocess.run(
                command, text=True, capture_output=True, check=False,
                timeout=max(int(os.environ.get("PURE_AI_FUND_TIMEOUT", "300")) + 120, 180),
            )
            pure_ai_status = "ok" if completed.returncode == 0 else "error"
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pure_ai_status = "error"
    print(json.dumps({"status": payload["status"], "generated_at": payload["generated_at"],
                      "positions": len(payload["positions"]), "pending": len(payload["pending_orders"]),
                      "skipped": len(payload["skipped_signals"]), "pure_ai_status": pure_ai_status},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

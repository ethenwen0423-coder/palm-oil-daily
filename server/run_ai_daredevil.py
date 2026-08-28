#!/usr/bin/env python3
"""Run the persistent AI敢死队 virtual fund and publish its read-only snapshot.

Trading decisions use completed daily bars. Hourly runs only execute already
planned next-open virtual orders and mark existing real PYYMM positions.
"""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import json
import math
import os
import re
import secrets
import signal
import statistics
import sys
import tempfile
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
INITIAL_CAPITAL = 1_000_000.0
FUND_FILE = "ai_daredevil.json"
READY_MARKER = ".server-ai-daredevil-ready.json"
SCAN_AUDIT_FILE = "latest_scan_audit.json"
CONTRACT_RE = re.compile(r"^[A-Z]{1,3}[0-9]{3,4}$")

# Multiplier is a contract specification. Margin is deliberately a conservative
# portfolio reserve, not a claim about the broker's current collection ratio.
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
}

# ak.futures_zh_realtime accepts the display names returned by
# futures_symbol_mark(), not exchange variety codes such as P or TA.
PRODUCT_REALTIME_SYMBOL = {
    "FG": "玻璃", "MA": "郑醇", "TA": "PTA", "SA": "纯碱", "V": "PVC",
    "RB": "螺纹钢", "FU": "燃油", "PP": "PP", "AG": "白银", "JD": "鸡蛋",
    "EG": "乙二醇", "L": "塑料", "JM": "焦煤", "EB": "苯乙烯", "HC": "热轧卷板",
    "BU": "沥青", "SH": "烧碱", "P": "棕榈", "Y": "豆油", "OI": "菜油",
    "M": "豆粕", "RM": "菜粕",
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
        "source": source,
    }


def akshare_quotes(contracts: list[str]) -> tuple[dict[str, dict[str, Any]], str | None]:
    try:
        import akshare as ak
    except ImportError as exc:
        return {}, f"akshare unavailable: {exc}"
    output: dict[str, dict[str, Any]] = {}
    errors = []
    by_variety: dict[str, list[str]] = {}
    for contract in contracts:
        variety = re.match(r"[A-Z]+", contract).group(0)
        by_variety.setdefault(variety, []).append(contract)
    for variety, expected in by_variety.items():
        try:
            frame = ak.futures_zh_realtime(symbol=PRODUCT_REALTIME_SYMBOL[variety])
            for row in frame.to_dict(orient="records") if frame is not None else []:
                for contract in expected:
                    quote = quote_from_row(row, contract, "AKShare 真实交割月行情")
                    if quote:
                        output[contract] = quote
        except Exception as exc:  # remote schema/network boundary
            errors.append(f"{variety}:{type(exc).__name__}")
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
            {"priority": "主来源", "name": "AKShare 真实交割月行情", "state": "ready", "note": "当前无持仓或待执行订单，本轮无需请求"},
            {"priority": "回退 1", "name": "同花顺问财行情 Skill", "state": "fallback", "note": "仅在 AKShare 精确合约行情缺失时启用"},
            {"priority": "回退 2", "name": "华泰智能 K 线 Skill", "state": "fallback", "note": "仅接受包含精确 PYYMM 合约的原始 K 线"},
        ]
    quotes, ak_error = akshare_quotes(contracts)
    source_rows = [{
        "priority": "主来源", "name": "AKShare 真实交割月行情",
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
    missing = [variety for variety in PRODUCTS if variety not in output]
    if missing:
        try:
            import akshare as ak
            for variety in missing:
                try:
                    frame = ak.futures_zh_realtime(symbol=PRODUCT_REALTIME_SYMBOL[variety])
                    values = []
                    for row in frame.to_dict(orient="records") if frame is not None else []:
                        contract = normalized_contract(find_field(row, ("symbol", "合约", "合约代码", "代码", "期货代码")))
                        if contract and contract.startswith(variety) and not contract.endswith("0"):
                            values.append(contract)
                    if values:
                        output[variety] = sorted(set(values))
                except Exception:
                    continue
        except ImportError:
            pass
    return output


def fetch_daily(contract: str):
    import akshare as ak
    import pandas as pd
    previous_handler = signal.getsignal(signal.SIGALRM)
    def deadline_handler(_signum, _frame):
        raise TimeoutError(f"{contract}: daily bars exceeded 15 seconds")
    signal.signal(signal.SIGALRM, deadline_handler)
    signal.setitimer(signal.ITIMER_REAL, 15)
    try:
        frame = ak.futures_zh_daily_sina(symbol=contract)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
    if frame is None or frame.empty:
        raise RuntimeErrorSafe(f"{contract}: empty daily bars")
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    for column in ("open", "high", "low", "close", "volume", "hold"):
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["date", "open", "high", "low", "close", "volume"]).sort_values("date")


def next_trade_date(after: date) -> date:
    try:
        import akshare as ak
        import pandas as pd
        calendar = ak.tool_trade_date_hist_sina()
        values = sorted(pd.to_datetime(calendar["trade_date"]).dt.date.unique())
        return next(value for value in values if value > after)
    except Exception as exc:
        raise RuntimeErrorSafe(f"next exchange trading day unavailable: {type(exc).__name__}") from exc


def allocation_score(variety: str) -> float | None:
    configured = os.environ.get("AI_DAREDEVIL_ALLOCATION_SCORES_JSON", "").strip()
    if configured:
        try:
            value = numeric(json.loads(configured).get(variety))
            return value
        except json.JSONDecodeError:
            return None
    # P is the only deployment-pinned baseline with the repaired 1/3/5-year
    # real-contract audit. This is an ordinal eligibility score, not a return.
    return 1.0 if variety == "P" else None


def margin_rate(variety: str) -> float:
    configured = numeric(os.environ.get(f"AI_DAREDEVIL_MARGIN_RATE_{variety}"))
    return configured if configured and 0 < configured <= 1 else 0.20


def fee_rate(variety: str) -> float:
    configured = numeric(os.environ.get(f"AI_DAREDEVIL_FEE_RATE_{variety}"))
    return configured if configured is not None and configured >= 0 else 0.0004


def scan_signals(site_root: Path, data_root: Path, state: dict[str, Any], model, generated_at: datetime | None = None) -> tuple[dict[str, Any] | None, list[dict[str, Any]], dict[str, Any]]:
    import pandas as pd
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
        "generated_at": (generated_at or now_shanghai()).isoformat(timespec="seconds"),
        "universe_count": len(PRODUCTS), "discovered_count": len(contracts_by_variety),
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
        for contract in contracts:
            try:
                frames[contract] = fetch_daily(contract)
            except Exception as exc:
                skipped.append({"variety": variety, "contract": contract, "reason": f"日线缺失：{type(exc).__name__}"})
        if not frames:
            continue
        raw_parts = []
        for candidate, frame in frames.items():
            part = frame.copy()
            part["contract"] = candidate
            part["variety"] = variety
            raw_parts.append(part)
        raw = pd.concat(raw_parts, ignore_index=True).sort_values(["date", "contract"])
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
        if strategy.setdefault("last_close", {}).get(variety) == signal_date.isoformat():
            previous = previous_candidates.get(variety)
            if previous and previous.get("signal_date") == signal_date.isoformat():
                audit["candidate_count"] += 1
                audit["signal_candidates"].append(previous)
                if previous.get("eligible"):
                    audit["order_count"] += 1
                else:
                    audit["blocked_candidate_count"] += 1
                    skipped.append({"variety": variety, "contract": previous.get("contract"), "reason": "缺少审计后的样本外配置评分"})
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
                score = allocation_score(variety)
                audit["candidate_count"] += 1
                audit["signal_candidates"].append({
                    "variety": variety, "name": PRODUCTS[variety]["name"], "contract": contract,
                    "action": "ENTER_LONG" if direction == 1 else "ENTER_SHORT",
                    "signal_date": signal_date.isoformat(), "eligible": score is not None,
                })
                if score is None:
                    audit["blocked_candidate_count"] += 1
                    skipped.append({"variety": variety, "contract": contract, "reason": "缺少审计后的样本外配置评分"})
                else:
                    action = "ENTER_LONG" if direction == 1 else "ENTER_SHORT"
                    reason = carry_reason or "真实交割月自身日线收盘穿越MA20"
        if action:
            order_contract = position["contract"] if position and action.startswith("EXIT") else contract
            item = {
                "variety": variety, "name": PRODUCTS[variety]["name"], "sector": PRODUCTS[variety]["sector"],
                "contract": order_contract, "action": action, "signal_date": signal_date.isoformat(),
                "execution_date": next_trade_date(signal_date).isoformat(), "reference_price": execution_close,
                "atr14": signal_atr, "multiplier": PRODUCTS[variety]["multiplier"],
                "margin_rate": margin_rate(variety), "fee_rate": fee_rate(variety),
                "reason": reason, "selection_volume_t_minus_1": float(raw_last.volume),
                "selection_open_interest_t_minus_1": numeric(raw_last.get("hold")),
            }
            score = allocation_score(variety)
            if action.startswith("ENTER") and score is not None:
                item["score"] = score
                item["score_basis"] = "生产基线准入序位，不代表预测收益率"
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
        "signals": signals,
    }, skipped, audit


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
    positions = []
    for position in state.get("positions", {}).values():
        row = dict(position)
        row["weight"] = float(row.get("notional", 0)) / float(state["equity"]) if state["equity"] else 0
        row["price_source"] = row.get("mark_source", "基金账本成交价")
        row["price_time"] = row.get("last_mark_date") or row.get("entry_date")
        positions.append(row)
    pending = [row for row in state.get("pending_orders", []) if row.get("status") == "pending"]
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
    status = "ready" if not positions or all(row.get("mark_source") for row in positions) else "degraded"
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
        "model": {"name": "布林RSI模型", "version": MODEL_VERSION, "capital_policy": "权益复利",
                  "execution": "完整日线确认，下一交易日开盘执行"},
        "summary": summary, "equity_curve": curve, "positions": positions,
        "today_trades": events, "pending_orders": pending, "skipped_signals": skipped,
        "scan_audit": scan_audit,
        "refresh_schedule": [
            {"label": "日盘开盘", "time": "09:00", "purpose": "获取真实开盘价并处理待执行订单"},
            {"label": "午盘开盘", "time": "13:30", "purpose": "补核成交与持仓盯市"},
            {"label": "夜盘开盘", "time": "21:00", "purpose": "获取夜盘开盘价并处理可交易品种"},
            {"label": "整点刷新", "time": "每小时", "purpose": "更新持仓价格、权益、来源状态和净值"},
        ],
        "sources": sources,
        "governance": {"virtual_only": True, "scanned_universe": list(PRODUCTS), "eligible_default": ["P"],
                       "other_varieties": "需配置经审计的样本外 allocation score 后才可新开仓",
                       "margin_note": "默认20%为保守组合预留率，不代表交易所或经纪商实时保证金率"},
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
        if should_scan:
            snapshot, skipped, scan_audit = scan_signals(site_root, live_data_root, state, model, now)
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
            old_quote, new_quote = quotes.get(roll["from"]), quotes.get(roll["to"])
            dates_ok = old_quote and new_quote and old_quote.get("trade_date") == today and new_quote.get("trade_date") == today
            if dates_ok and old_quote.get("open") and new_quote.get("open"):
                ledger.command_roll(SimpleNamespace(
                    state_dir=state_dir, variety=variety, new_contract=roll["to"], date=today,
                    old_price=float(old_quote["open"]), new_price=float(new_quote["open"]),
                ))
                pending_rolls.pop(variety, None)
                state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        strategy["pending_rolls"] = pending_rolls
        atomic_json(state_dir / "strategy_state.json", strategy)
        for order in [row for row in pending_orders if not str(row.get("action", "")).startswith("EXIT")]:
            if order.get("execution_date") != today:
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
    print(json.dumps({"status": payload["status"], "generated_at": payload["generated_at"],
                      "positions": len(payload["positions"]), "pending": len(payload["pending_orders"]),
                      "skipped": len(payload["skipped_signals"])}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

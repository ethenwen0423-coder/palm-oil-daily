#!/usr/bin/env python3
"""Build the static oil-futures contract data used by the home-page tab."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timedelta
import importlib.util
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from sync_miniprogram_data import publish_dataset


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNS = ROOT / "source_runs"
OUTPUT = ROOT / "data" / "oil_futures.js"
HITHINK_CLI = Path.home() / ".codex" / "skills" / "hithink-market-query" / "scripts" / "cli.py"
MASTER_ANALYTIC_CLI = ROOT / "skills" / "master_analytic_skill" / "scripts" / "analyze_contracts.py"
REVIEW_MEMORY = ROOT / "skills" / "daily_review_skill" / "scripts" / "review_memory.py"
CONTRACT_SELECTOR_CLI = ROOT / "skills" / "contract_selector_skill" / "scripts" / "select_contracts.py"
CONTRACT_DISCOVERY_CLI = ROOT / "skills" / "contract_discovery_skill" / "scripts" / "select_contracts.py"
CONTRACT_DISCOVERY_CURRENT = ROOT / "data" / "contracts" / "current_contracts.json"
DATA_QUALITY_GATE_CLI = ROOT / "skills" / "data_quality_gate_skill" / "scripts" / "validate_data.py"
FORECAST_RECORDER_CLI = ROOT / "skills" / "forecast_tracking_skill" / "scripts" / "record_forecast.py"
FORECAST_DAILY_DIR = ROOT / "data" / "forecast" / "daily"
PRIVATE_ENV = Path.home() / "Library" / "Application Support" / "VinsonTesla" / "private.env"
SHANGHAI = ZoneInfo("Asia/Shanghai")
PRICE_TOLERANCE = 2.0
PRICE_REL_TOLERANCE = 0.002
PCT_TOLERANCE = 0.25
ICDX_CPOTR_API = "https://www.icdx.co.id/cms/api/table-price-all/get"


def infer_update_session(now: datetime | None = None) -> str:
    current = now or datetime.now(SHANGHAI)
    minutes = current.hour * 60 + current.minute
    if minutes < 11 * 60 + 30:
        return "morning"
    if minutes < 15 * 60:
        return "midday"
    return "close"


def load_private_env() -> None:
    """Load local secrets for launchd/manual runs without storing them in the repo."""
    if not PRIVATE_ENV.exists():
        return
    for raw_line in PRIVATE_ENV.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value

DOMESTIC = [
    {
        "key": "palm_oil",
        "symbol": "P",
        "name": "棕榈油",
        "market": "DCE",
        "ak_realtime": "棕榈",
        "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
    },
    {
        "key": "soybean_oil",
        "symbol": "Y",
        "name": "豆油",
        "market": "DCE",
        "ak_realtime": "豆油",
        "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
    },
    {
        "key": "rapeseed_oil",
        "symbol": "OI",
        "name": "菜油",
        "market": "CZCE",
        "ak_realtime": "菜油",
        "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
    },
    {
        "key": "soybean_meal",
        "symbol": "M",
        "name": "豆粕",
        "market": "DCE",
        "ak_realtime": "豆粕",
        "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
    },
    {
        "key": "rapeseed_meal",
        "symbol": "RM",
        "name": "菜粕",
        "market": "CZCE",
        "ak_realtime": "菜粕",
        "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
    },
]

EXTERNAL = [
    {
        "key": "bmd_palm_oil",
        "symbol": "FCPO",
        "name": "马棕油",
        "market": "BMD",
        "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
    },
    {
        "key": "indonesia_cpotr",
        "symbol": "CPOTR",
        "name": "印尼棕榈油",
        "market": "ICDX",
        "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
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


def contract_month(value: Any) -> datetime | None:
    match = re.fullmatch(r"([A-Z]{3})(\d{2})", str(value or "").upper())
    if not match:
        return None
    try:
        return datetime.strptime(f"{match.group(1)}{match.group(2)}", "%b%y")
    except ValueError:
        return None


def fetch_icdx_cpotr(reference_time: datetime | None = None) -> dict[str, Any]:
    """Fetch the latest actively traded CPOTR contract from the official ICDX API."""
    now = reference_time or datetime.now(SHANGHAI)
    filters = [
        {"key": "product", "value": "CPOTR"},
        {"key": "MONTH(date) = ?", "value": str(now.month), "type": "raw_equal"},
        {"key": "YEAR(date) = ?", "value": str(now.year), "type": "raw_equal"},
    ]
    request = urllib.request.Request(
        ICDX_CPOTR_API,
        data=json.dumps({"filters": filters}).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": "https://www.icdx.co.id/historical-price/detail",
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "status": "missing",
            "source": "ICDX 官方历史价格接口",
            "fetched_at": now.isoformat(timespec="seconds"),
            "error": f"ICDX CPOTR 官方行情请求失败：{exc}",
        }

    rows = payload.get("data") if isinstance(payload, dict) else None
    candidates = [
        row
        for row in rows or []
        if isinstance(row, dict)
        and str(row.get("Symbol") or "").upper() == "CPOTR"
        and as_float(row.get("LastPrice") if row.get("LastPrice") not in (None, "") else row.get("SettlementPrice")) is not None
        and str(row.get("date") or "")
    ]
    if not candidates:
        return {
            "status": "missing",
            "source": "ICDX 官方历史价格接口",
            "fetched_at": now.isoformat(timespec="seconds"),
            "error": "ICDX CPOTR 官方接口未返回可用价格",
        }

    latest_date = max(str(row["date"]) for row in candidates)
    latest_rows = [row for row in candidates if str(row["date"]) == latest_date]

    def row_priority(row: dict[str, Any]) -> tuple[int, int, float]:
        volume = as_int(row.get("VolumeTraded")) or 0
        has_last = 1 if as_float(row.get("LastPrice")) is not None else 0
        expiry = contract_month(row.get("Contract"))
        expiry_order = -expiry.timestamp() if expiry is not None else float("-inf")
        return (volume, has_last, expiry_order)

    selected = max(latest_rows, key=row_priority)
    last_price = as_float(selected.get("LastPrice"))
    settlement = as_float(selected.get("SettlementPrice"))
    previous_settlement = as_float(selected.get("YDSP"))
    price = last_price if last_price is not None else settlement
    change_pct = None
    if price is not None and previous_settlement not in (None, 0):
        change_pct = (price - previous_settlement) / previous_settlement * 100
    return {
        "name": "ICDX CPOTR",
        "status": "ok",
        "source": "ICDX 官方历史价格接口",
        "source_url": "https://www.icdx.co.id/historical-price/detail",
        "fetched_at": now.isoformat(timespec="seconds"),
        "published_at": latest_date,
        "price": price,
        "change": price - previous_settlement if price is not None and previous_settlement is not None else None,
        "change_pct": change_pct,
        "change_basis": "vs_previous_settlement_ydsp",
        "contract": f"CPOTR {str(selected.get('Contract') or '').upper()}".strip(),
        "open": as_float(selected.get("OpeningPrice")),
        "high": as_float(selected.get("HighPrice")),
        "low": as_float(selected.get("LowPrice")),
        "close": previous_settlement,
        "settle": settlement,
        "volume": as_int(selected.get("VolumeTraded")),
        "open_interest": as_int(selected.get("OpenInterest")),
        "unit": "印尼盾/公斤",
        "location": "ICDX Jakarta",
        "price_type": "last" if last_price is not None else "settlement",
    }


def latest_market_snapshot(report_date: str | None = None) -> tuple[dict[str, Any] | None, Path | None]:
    if report_date:
        candidates = [SOURCE_RUNS / f"{report_date}-daily" / "raw" / "futures_market_data.json"]
    else:
        candidates = sorted(SOURCE_RUNS.glob("*/raw/futures_market_data.json"), reverse=True)
    for path in candidates:
        try:
            return json.loads(path.read_text(encoding="utf-8")), path
        except Exception:
            continue
    return None, None


def recent_review_learning(limit: int = 5) -> dict[str, Any]:
    if REVIEW_MEMORY.exists():
        spec = importlib.util.spec_from_file_location("daily_review_memory", REVIEW_MEMORY)
        if spec is None or spec.loader is None:
            loaded = {"reviews": [], "warnings": ["review_memory.py 无法加载"], "loaded_count": 0}
        else:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded = module.load_recent_reviews(days=30)
    else:
        loaded = {"reviews": [], "warnings": ["review_memory.py 缺失"], "loaded_count": 0}

    review_items = loaded.get("reviews", [])
    recent_reviews = review_items[-limit:]
    items: list[dict[str, Any]] = []
    for wrapped in recent_reviews:
        payload = wrapped.get("payload", {}) if isinstance(wrapped, dict) else {}
        rows = payload.get("learning_notes") or payload.get("review_result") or []
        for row in rows:
            if isinstance(row, dict):
                items.append(row)
    candidates = sorted({str(error) for item in items for error in item.get("error_type", []) if error})
    repeated: dict[str, int] = {}
    for error in candidates:
        count = 0
        for wrapped in reversed(recent_reviews):
            payload = wrapped.get("payload", {}) if isinstance(wrapped, dict) else {}
            rows = payload.get("learning_notes") or payload.get("review_result") or []
            present = any(error in (row.get("error_type", []) if isinstance(row, dict) else []) for row in rows)
            if not present:
                break
            count += 1
        if count >= 3:
            repeated[error] = count
    if not repeated:
        return {
            "items": items,
            "repeated_errors": {},
            "warnings": loaded.get("warnings", []),
            "loaded_count": loaded.get("loaded_count", 0),
            "warning": "",
        }
    parts = [f"{error}出现{count}次" for error, count in sorted(repeated.items(), key=lambda item: item[1], reverse=True)]
    return {
        "items": items,
        "repeated_errors": repeated,
        "warnings": loaded.get("warnings", []),
        "loaded_count": loaded.get("loaded_count", 0),
        "warning": f"近期模型偏差提示：最近5次复盘中{'; '.join(parts)}，本次观点需降低相关因素的单独主导性。",
    }


def concrete_contract(value: Any) -> str | None:
    text = str(value or "").upper().strip()
    if re.fullmatch(r"[A-Z]+0", text):
        return None
    if re.fullmatch(r"[A-Z]+\d{4}", text):
        return text
    if re.fullmatch(r"FCPO[A-Z]\d{4}", text) or text in {"BO=F", "ZS=F"}:
        return text
    return None


def run_contract_selector(now_month: str) -> list[str]:
    selector = CONTRACT_SELECTOR_CLI if CONTRACT_SELECTOR_CLI.exists() else CONTRACT_DISCOVERY_CLI
    if not selector.exists():
        return ["contract_selector_skill 和 contract_discovery_skill 均缺失，无法生成当月合约名单"]
    result = subprocess.run(
        [sys.executable, str(selector)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=45,
        check=False,
    )
    if result.returncode != 0:
        return [f"contract_selector_skill 调用失败：{result.stderr.strip() or result.stdout.strip()}"]
    return []


def load_contract_discovery() -> dict[str, Any]:
    now_month = datetime.now().strftime("%Y-%m")
    selector_warnings = run_contract_selector(now_month)
    if CONTRACT_DISCOVERY_CURRENT.exists():
        try:
            payload = json.loads(CONTRACT_DISCOVERY_CURRENT.read_text(encoding="utf-8"))
            if payload.get("month") == now_month:
                payload["selector_skill"] = "contract_selector_skill"
                payload["warnings"] = list(payload.get("warnings", [])) + selector_warnings
                return payload
        except Exception:
            pass

    try:
        payload = json.loads(CONTRACT_DISCOVERY_CURRENT.read_text(encoding="utf-8"))
        payload["selector_skill"] = "contract_selector_skill"
        payload["warnings"] = list(payload.get("warnings", [])) + selector_warnings
        return payload
    except Exception as exc:
        return {
            "month": now_month,
            "products": {},
            "selector_skill": "contract_selector_skill",
            "warnings": selector_warnings + [f"contract_selector_skill 已运行但名单读取失败：{exc}"],
        }


def ak_realtime_contract(ak: Any, variety: str, preferred_contract: str | None = None) -> dict[str, Any] | None:
    if ak is None:
        return None
    try:
        df = ak.futures_zh_realtime(symbol=variety)
        if df is None or len(df) == 0:
            return None
        rows = df[~df["symbol"].astype(str).str.fullmatch(r"[A-Za-z]+0")]
        if rows.empty:
            return None
        if preferred_contract:
            selected_rows = rows[rows["symbol"].astype(str).str.upper() == preferred_contract.upper()]
            if selected_rows.empty:
                return None
            rows = selected_rows
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


def ak_daily_contract(ak: Any, contract: str, target_date: str | None = None) -> dict[str, Any] | None:
    if ak is None:
        return None
    try:
        df = ak.futures_zh_daily_sina(symbol=contract)
        if df is None or len(df) == 0:
            return None
        selected_index = len(df) - 1
        if target_date is not None:
            matches = [index for index, value in enumerate(df["date"]) if str(value)[:10] == target_date]
            if not matches:
                return None
            selected_index = matches[-1]
        row = df.iloc[selected_index]
        previous = df.iloc[selected_index - 1] if selected_index >= 1 else None
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


def history_records(history: Any) -> list[dict[str, Any]]:
    if history is None:
        return []
    return json.loads(history.to_json(orient="records", force_ascii=False))


def call_master_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    if not MASTER_ANALYTIC_CLI.exists():
        return {
            "score": {
                "total": 50,
                "technical": 50,
                "fundamental": 50,
                "stance": "震荡",
                "weights": "技术面70% / 基本面30%",
            },
            "view": "master_analytic_skill 不可用，分析结论需进一步核验。",
            "strategies": [],
            "quality_note": "master_analytic_skill 脚本不存在",
        }
    result = subprocess.run(
        [sys.executable, str(MASTER_ANALYTIC_CLI)],
        input=json.dumps(payload, ensure_ascii=False),
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "master_analytic_skill 调用失败")
    return json.loads(result.stdout)


def hithink_contract(contract: str) -> dict[str, Any]:
    load_private_env()
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
    elif abs(ak_price - hithink_price) <= max(
        PRICE_TOLERANCE,
        min(abs(ak_price), abs(hithink_price)) * PRICE_REL_TOLERANCE,
    ):
        notes.append(f"价格一致：AkShare {raw_number(ak_price)} / 行情skill {raw_number(hithink_price)}")
    else:
        notes.append(f"价格不一致：AkShare {raw_number(ak_price)} / 行情skill {raw_number(hithink_price)}")

    if ak_pct is not None and hithink_pct is not None and abs(ak_pct - hithink_pct) > PCT_TOLERANCE:
        notes.append(f"涨跌幅口径不同：AkShare {fmt_pct(ak_pct)} / 行情skill {fmt_pct(hithink_pct)}")

    return "；".join(notes)


def merge_domestic(
    spec: dict[str, Any],
    selected_contract: dict[str, Any],
    snapshot: dict[str, Any] | None,
    ak: Any,
    review_learning: dict[str, Any] | None = None,
) -> dict[str, Any]:
    skill_record = (snapshot or {}).get("domestic", {}).get(spec["key"], {})
    selected_symbol = concrete_contract(selected_contract.get("symbol"))
    realtime = ak_realtime_contract(ak, spec["ak_realtime"], selected_symbol)
    fallback_contract = selected_symbol or concrete_contract(skill_record.get("contract")) or (realtime or {}).get("contract")
    history = ak_daily_history(ak, fallback_contract) if fallback_contract else None
    daily = ak_daily_contract(ak, fallback_contract) if fallback_contract else None

    source = skill_record if skill_record.get("status") == "ok" else {}
    if not source:
      source = realtime or daily or {}
    if realtime:
        source = {**source, **{key: value for key, value in realtime.items() if value is not None}}
    if daily:
        source = {**daily, **{key: value for key, value in source.items() if value not in (None, "", "需进一步核验")}}

    contract = concrete_contract(source.get("contract")) or fallback_contract or selected_contract.get("symbol") or spec["symbol"]
    hithink = hithink_contract(contract) if concrete_contract(contract) else {"status": "missing", "message": "缺少可核验的具体合约代码"}
    verification = verification_note(source, hithink)
    price = as_float(source.get("price"))
    rank = selected_contract.get("rank")
    contract_label = selected_contract.get("label") or ("主力" if rank == 1 else "次主力" if rank else "")
    analysis = call_master_analysis(
        {
            "spec": spec,
            "source": source,
            "snapshot": {**(snapshot or {}), "review_learning": review_learning or {}},
            "history": history_records(history),
        }
    )
    return {
        "symbol": contract,
        "product": spec["symbol"],
        "name": spec["name"],
        "market": spec["market"],
        "contract": contract,
        "contract_rank": rank,
        "contract_label": contract_label,
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
        "score": analysis.get("score"),
        "view": analysis.get("view"),
        "technical_detail": analysis.get("technical_detail", []),
        "fundamental_detail": analysis.get("fundamental_detail", []),
        "strategy_recommendation": analysis.get("strategy_recommendation", {}),
        "analysis_skill": analysis.get("analysis_skill", "master_analytic_skill"),
        "child_skill": analysis.get("child_skill", "technical_basic_analysis_skill"),
        "quality_note": analysis.get("quality_note", "需进一步核验"),
    }


def merge_external(spec: dict[str, str], snapshot: dict[str, Any] | None, review_learning: dict[str, Any] | None = None) -> dict[str, Any]:
    record = (snapshot or {}).get("external", {}).get(spec["key"], {})
    analysis = call_master_analysis({"spec": spec, "source": record, "snapshot": {**(snapshot or {}), "review_learning": review_learning or {}}, "external": True})
    change_basis = str(record.get("change_basis") or record.get("basis") or "")
    basis_is_clear = any(word in change_basis.lower() for word in ["previous close", "settlement", "open", "昨收", "结算", "开盘"])
    display_change = fmt_pct(record.get("change_pct"))
    verification = "海外产地价格使用交易所或公开行情源，仅作棕榈油跨市场参考。"
    if spec.get("symbol") == "FCPO" and not basis_is_clear:
        display_change = "需进一步核验"
        verification = "FCPO涨跌幅口径未明确说明相对昨收、开盘或结算价；涨跌幅已降级为需进一步核验。"
    elif spec.get("symbol") == "CPOTR":
        verification = "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。"
    return {
        "symbol": spec["symbol"],
        "product": spec["symbol"],
        "name": spec["name"],
        "market": spec["market"],
        "contract": record.get("contract") or spec["symbol"],
        "price": fmt_number(record.get("price")),
        "unit": str(record.get("unit") or ""),
        "change": display_change,
        "change_basis": change_basis or "需进一步核验",
        "volume": fmt_lots(record.get("volume")),
        "open_interest": fmt_lots(record.get("open_interest")),
        "direction": direction(record.get("change_pct")),
        "open": fmt_number(record.get("open")),
        "high": fmt_number(record.get("high")),
        "low": fmt_number(record.get("low")),
        "preclose": fmt_number(record.get("close")),
        "settle": fmt_number(record.get("settle")),
        "trade_date": record.get("published_at", "")[:10] or record.get("fetched_at", "")[:10],
        "source": record.get("source") or "需进一步核验",
        "note": spec["note"],
        "verification": verification,
        "score": analysis.get("score"),
        "view": analysis.get("view"),
        "technical_detail": analysis.get("technical_detail", []),
        "fundamental_detail": analysis.get("fundamental_detail", []),
        "strategy_recommendation": analysis.get("strategy_recommendation", {}),
        "analysis_skill": analysis.get("analysis_skill", "master_analytic_skill"),
        "child_skill": analysis.get("child_skill", "technical_basic_analysis_skill"),
        "quality_note": analysis.get("quality_note", "需进一步核验"),
    }


def market_reference(label: str, location: str, record: dict[str, Any] | None) -> dict[str, str]:
    source = record or {}
    return {
        "label": label,
        "location": location,
        "price": fmt_number(source.get("price")) if source.get("status") == "ok" else "待更新",
        "change": fmt_pct(source.get("change_pct")) if source.get("status") == "ok" else "需进一步核验",
        "unit": str(source.get("unit") or ""),
        "updated_at": str(source.get("published_at") or source.get("fetched_at") or "待更新"),
        "source": str(source.get("source") or "需进一步核验"),
    }


def build_market_references(snapshot: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    external = (snapshot or {}).get("external", {})
    return {
        "malaysia_fcpo": market_reference("马来 BMD FCPO", "马来西亚", external.get("bmd_palm_oil")),
        "indonesia_cpotr": market_reference("印尼 ICDX CPOTR", "雅加达", external.get("indonesia_cpotr")),
        "india_cpo_spot": market_reference("印度 NCDEX CPO 现货", "Kandla", external.get("india_cpo_spot")),
    }


def write_js(payload: dict[str, Any], output: Path, publish: bool = True) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    output.write_text(f"window.OIL_FUTURES_CONTRACTS = {text};\n", encoding="utf-8")
    if publish and output.resolve() == OUTPUT.resolve():
        publish_dataset("oil-futures", payload)


def load_js_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    prefix = "window.OIL_FUTURES_CONTRACTS ="
    if text.startswith(prefix):
        text = text[len(prefix) :].strip().removesuffix(";")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} 不是有效的油脂行情数据对象")
    return payload


def update_external_contract_only(payload: dict[str, Any], spec: dict[str, str], snapshot: dict[str, Any], review_learning: dict[str, Any]) -> dict[str, Any]:
    contract = merge_external(spec, snapshot, review_learning)
    contracts = [item for item in payload.get("contracts", []) if str(item.get("symbol") or "").upper() != spec["symbol"]]
    contracts.append(contract)
    payload["contracts"] = contracts

    references = dict(payload.get("market_references") or {})
    references["indonesia_cpotr"] = market_reference(
        "印尼 ICDX CPOTR",
        "雅加达",
        snapshot.get("external", {}).get("indonesia_cpotr"),
    )
    payload["market_references"] = references

    source = str(payload.get("source") or "")
    old_note = "外盘仅展示与棕榈油最相关的 FCPO"
    new_note = "海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR"
    payload["source"] = source.replace(old_note, new_note) if old_note in source else f"{source}；{new_note}".lstrip("；")
    payload["updated_at"] = datetime.now(SHANGHAI).strftime("%Y-%m-%d %H:%M")
    return payload


def run_data_quality_gate(path: Path) -> None:
    if not DATA_QUALITY_GATE_CLI.exists():
        raise RuntimeError("data_quality_gate_skill 缺失，停止发布以避免未校验数据上线")
    result = subprocess.run(
        [sys.executable, str(DATA_QUALITY_GATE_CLI), "--oil-futures", str(path), "--strict"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or result.stderr.strip() or "data_quality_gate_skill 校验失败")


def run_manifest_quality_gate(path: Path) -> None:
    if not DATA_QUALITY_GATE_CLI.exists():
        raise RuntimeError("data_quality_gate_skill 缺失，停止发布以避免未校验数据上线")
    result = subprocess.run(
        [sys.executable, str(DATA_QUALITY_GATE_CLI), "--manifest", str(path), "--strict"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or result.stderr.strip() or "source manifest 数据质量门失败")


def normalize_shanghai_timestamp(value: Any, field: str, report_date: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"缺少可验证的 {field}，停止发布")
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise RuntimeError(f"{field} 不是有效 ISO-8601 时间：{value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    if parsed.utcoffset() != timedelta(hours=8):
        raise RuntimeError(f"{field} 必须属于 Asia/Shanghai（+08:00）")
    if parsed.date().isoformat() != report_date:
        raise RuntimeError(f"{field} 日期与 report-date 不一致")
    return parsed.isoformat(timespec="seconds")


def load_forecast_time_metadata(report_date: str) -> dict[str, Any]:
    manifest_path = SOURCE_RUNS / f"{report_date}-daily" / "manifest.json"
    raw_path = SOURCE_RUNS / f"{report_date}-daily" / "raw" / "futures_market_data.json"
    if not manifest_path.exists():
        raise RuntimeError(f"缺少晨报 source manifest：{manifest_path}")
    if not raw_path.exists():
        raise RuntimeError(f"缺少晨报行情时间截面：{raw_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        raw_snapshot = json.loads(raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"晨报时间截面元数据无法读取：{exc}") from exc
    if manifest.get("date") != report_date or manifest.get("kind") != "daily":
        raise RuntimeError("source manifest 的 date/kind 与日报不一致")
    if raw_snapshot.get("date") != report_date:
        raise RuntimeError("futures_market_data.json 的 date 与日报不一致")
    generated_at = normalize_shanghai_timestamp(manifest.get("generated_at"), "manifest.generated_at", report_date)
    cutoff_at = normalize_shanghai_timestamp(raw_snapshot.get("timestamp"), "raw.futures_market_data.timestamp", report_date)
    generated = datetime.fromisoformat(generated_at)
    cutoff = datetime.fromisoformat(cutoff_at)
    if generated > cutoff + timedelta(minutes=5):
        raise RuntimeError("manifest.generated_at 晚于数据截止时点超过 5 分钟，停止预测冻结")
    return {
        "report_date": report_date,
        "generated_at": generated_at,
        "cutoff_at": cutoff_at,
        "timezone": "Asia/Shanghai",
        "quality_status": "unverified",
        "manifest": str(manifest_path.relative_to(ROOT)),
        "market_snapshot": str(raw_path.relative_to(ROOT)),
    }


def validate_forecast_time_arguments(
    metadata: dict[str, Any], generated_at: str | None, cutoff_at: str | None
) -> None:
    if not generated_at or not cutoff_at:
        raise RuntimeError("正式日报发布必须显式提供 --generated-at 和 --cutoff-at")
    if generated_at != metadata["generated_at"]:
        raise RuntimeError("--generated-at 与 source manifest 的可验证时间不一致")
    if cutoff_at != metadata["cutoff_at"]:
        raise RuntimeError("--cutoff-at 与 futures_market_data 时间截面不一致")


def write_forecast_time_metadata(metadata: dict[str, Any]) -> Path:
    report_date = str(metadata["report_date"])
    target = SOURCE_RUNS / f"{report_date}-daily" / "forecast_time_metadata.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {**metadata, "quality_status": "ok"}
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(payload, temporary, ensure_ascii=False, sort_keys=True, indent=2)
            temporary.write("\n")
        os.replace(temporary_path, target)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return target


def run_forecast_recorder(temp_oil_futures: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    if not FORECAST_RECORDER_CLI.exists():
        raise RuntimeError("forecast_tracking_skill 缺失，停止日报发布")
    forecast_path = FORECAST_DAILY_DIR / f"{metadata['report_date']}.json"
    result = subprocess.run(
        [
            sys.executable,
            str(FORECAST_RECORDER_CLI),
            "--oil-futures",
            str(temp_oil_futures),
            "--forecast",
            str(forecast_path),
            "--report-date",
            str(metadata["report_date"]),
            "--generated-at",
            str(metadata["generated_at"]),
            "--cutoff-at",
            str(metadata["cutoff_at"]),
            "--quality-gate-status",
            "ok",
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or result.stderr.strip() or "预测冻结失败")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("预测冻结器返回了非 JSON 输出") from exc
    if payload.get("status") != "ok":
        raise RuntimeError(f"预测冻结失败：{payload}")
    return payload


def validate_freeze_and_publish(
    payload: dict[str, Any], output: Path, metadata: dict[str, Any]
) -> dict[str, Any]:
    temp_output = output.with_name(".oil_futures.quality-check.tmp.js")
    try:
        write_js(payload, temp_output, publish=False)
        run_data_quality_gate(temp_output)
        forecast_result = run_forecast_recorder(temp_output, metadata)
        write_forecast_time_metadata(metadata)
        write_js(payload, output)
        return forecast_result
    finally:
        temp_output.unlink(missing_ok=True)


def validate_actual_snapshot_payload(payload: dict[str, Any], snapshot_date: str) -> None:
    """Require one same-day rank-1 P/Y/OI record before retaining an actual snapshot."""
    try:
        datetime.strptime(snapshot_date, "%Y-%m-%d")
    except ValueError as exc:
        raise RuntimeError("--snapshot-date 必须为有效 YYYY-MM-DD 日期") from exc
    contracts = payload.get("contracts")
    if not isinstance(contracts, list):
        raise RuntimeError("actual snapshot 缺少 contracts 数组")
    tracked = {"P", "Y", "OI"}
    selected: dict[str, dict[str, Any]] = {}
    for contract in contracts:
        if not isinstance(contract, dict) or contract.get("product") not in tracked:
            continue
        try:
            rank = int(contract.get("contract_rank"))
        except (TypeError, ValueError):
            continue
        if rank == 1:
            product = str(contract["product"])
            if product in selected:
                raise RuntimeError(f"actual snapshot 存在重复 rank=1 合约：{product}")
            selected[product] = contract
    missing = sorted(tracked - set(selected))
    if missing:
        raise RuntimeError(f"actual snapshot 缺少 rank=1 合约：{', '.join(missing)}")
    for product, contract in selected.items():
        if contract.get("trade_date") != snapshot_date:
            raise RuntimeError(f"actual snapshot {product} trade_date 与 --snapshot-date 不一致")
        for field, alternatives in {
            "close": ("price", "close"),
            "previous_close": ("preclose", "previous_close"),
            "high": ("high",),
            "low": ("low",),
        }.items():
            value = next((contract.get(name) for name in alternatives if contract.get(name) is not None), None)
            if as_float(value) is None:
                raise RuntimeError(f"actual snapshot {product}.{field} 缺失或非数值")


def write_actual_snapshot_atomically(payload: dict[str, Any], output: Path, snapshot_date: str) -> None:
    """Validate a non-publishing actual snapshot before atomically replacing its target."""
    if output.resolve() == OUTPUT.resolve():
        raise RuntimeError("actual-snapshot 模式禁止写入正式 data/oil_futures.js")
    validate_actual_snapshot_payload(payload, snapshot_date)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=output.parent, prefix=f".{output.name}.", suffix=".tmp", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
        write_js(payload, temporary_path, publish=False)
        run_data_quality_gate(temporary_path)
        os.replace(temporary_path, output)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def build_actual_snapshot_payload(snapshot_date: str) -> dict[str, Any]:
    """Fetch only the exact frozen P/Y/OI contracts; avoid discovery and report analysis."""
    forecast_path = FORECAST_DAILY_DIR / f"{snapshot_date}.json"
    try:
        forecast = json.loads(forecast_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"无法读取冻结预测 {forecast_path}: {exc}") from exc
    records = forecast.get("records") if isinstance(forecast, dict) else None
    if not isinstance(records, list):
        raise RuntimeError("冻结预测缺少 records")
    frozen: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict) or record.get("product") not in {"P", "Y", "OI"}:
            continue
        if record.get("contract_rank") != 1 or not concrete_contract(record.get("contract")):
            continue
        product = str(record["product"])
        if product in frozen:
            raise RuntimeError(f"冻结预测存在重复 rank=1 合约：{product}")
        frozen[product] = str(record["contract"])
    missing = sorted({"P", "Y", "OI"} - set(frozen))
    if missing:
        raise RuntimeError(f"冻结预测缺少 rank=1 合约：{', '.join(missing)}")

    ak = load_akshare()
    if ak is None:
        raise RuntimeError("AkShare 不可用，无法生成收盘实际快照")
    contracts: list[dict[str, Any]] = []
    for product in ("P", "Y", "OI"):
        spec = next(item for item in DOMESTIC if item["symbol"] == product)
        contract = frozen[product]
        realtime = ak_realtime_contract(ak, spec["ak_realtime"], contract)
        daily = None
        if realtime is None or str(realtime.get("tradedate") or "")[:10] != snapshot_date:
            daily = ak_daily_contract(ak, contract, snapshot_date)
        source = realtime if realtime and str(realtime.get("tradedate") or "")[:10] == snapshot_date else daily
        if source is None or str(source.get("tradedate") or "")[:10] != snapshot_date:
            raise RuntimeError(f"{contract} 缺少 {snapshot_date} 同日收盘行情")
        contracts.append(
            {
                "symbol": contract,
                "product": product,
                "name": spec["name"],
                "market": spec["market"],
                "contract": contract,
                "contract_rank": 1,
                "contract_label": "主力",
                "price": source.get("price"),
                "change": source.get("change_pct"),
                "open": source.get("open"),
                "high": source.get("high"),
                "low": source.get("low"),
                "preclose": source.get("preclose"),
                "settle": source.get("settle"),
                "volume": source.get("volume"),
                "open_interest": source.get("open_interest"),
                "trade_date": snapshot_date,
                "source": source.get("source") or "AkShare",
            }
        )
    return {
        "updated_at": datetime.now(SHANGHAI).isoformat(timespec="minutes"),
        "source": "冻结预测同合约收盘快照；仅用于内部复盘，不参与晨报生成",
        "contracts": contracts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Update static oil futures contract data.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--report-date")
    parser.add_argument("--generated-at")
    parser.add_argument("--cutoff-at")
    parser.add_argument("--print-time-metadata", action="store_true")
    parser.add_argument("--mode", choices=("publish", "actual-snapshot"), default="publish")
    parser.add_argument("--snapshot-date")
    parser.add_argument("--external-only", choices=("CPOTR",), help="只刷新指定海外合约，保留现有国内合约数据")
    parser.add_argument("--update-session", choices=("morning", "midday", "close", "manual"))
    args = parser.parse_args()

    if args.print_time_metadata:
        if not args.report_date:
            parser.error("--print-time-metadata requires --report-date")
        print(json.dumps(load_forecast_time_metadata(args.report_date), ensure_ascii=False, sort_keys=True))
        return 0

    if args.mode == "actual-snapshot":
        if not args.snapshot_date:
            parser.error("--mode actual-snapshot requires --snapshot-date")
        if any([args.report_date, args.generated_at, args.cutoff_at]):
            parser.error("actual-snapshot mode does not accept forecast-freezing time arguments")
        if args.output.resolve() == OUTPUT.resolve():
            parser.error("actual-snapshot mode requires a non-official --output path")
    elif args.snapshot_date:
        parser.error("--snapshot-date is only valid with --mode actual-snapshot")

    if args.external_only and any([args.report_date, args.generated_at, args.cutoff_at, args.snapshot_date, args.mode != "publish"]):
        parser.error("--external-only cannot be combined with snapshot or forecast-freezing arguments")

    if args.mode == "actual-snapshot":
        try:
            payload = build_actual_snapshot_payload(str(args.snapshot_date))
            write_actual_snapshot_atomically(payload, args.output, str(args.snapshot_date))
        except RuntimeError as exc:
            print(json.dumps({"status": "blocked", "stage": "actual_snapshot", "reason": str(exc)}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
            return 2
        try:
            display_path = args.output.relative_to(ROOT)
        except ValueError:
            display_path = args.output
        print(json.dumps({"status": "ok", "output": str(display_path), "contract_count": 3}, ensure_ascii=False, sort_keys=True))
        return 0

    freeze_forecast = args.mode == "publish" and any([args.report_date, args.generated_at, args.cutoff_at])
    metadata: dict[str, Any] | None = None
    if freeze_forecast:
        if not args.report_date:
            parser.error("forecast freezing requires --report-date")
        metadata = load_forecast_time_metadata(args.report_date)
        validate_forecast_time_arguments(metadata, args.generated_at, args.cutoff_at)
        run_manifest_quality_gate(SOURCE_RUNS / f"{args.report_date}-daily" / "manifest.json")

    snapshot, snapshot_path = latest_market_snapshot(args.report_date if freeze_forecast else None)
    snapshot = dict(snapshot or {})
    snapshot["external"] = {
        **(snapshot.get("external") or {}),
        "indonesia_cpotr": fetch_icdx_cpotr(),
    }
    review_learning = recent_review_learning()
    if args.external_only:
        spec = next(item for item in EXTERNAL if item["symbol"] == args.external_only)
        payload = update_external_contract_only(load_js_payload(args.output), spec, snapshot, review_learning)
        payload["update_session"] = args.update_session or infer_update_session()
        payload["timezone"] = "Asia/Shanghai"
        tmp_output = OUTPUT.with_name(".oil_futures.quality-check.tmp.js")
        try:
            write_js(payload, tmp_output, publish=False)
            run_data_quality_gate(tmp_output)
        finally:
            tmp_output.unlink(missing_ok=True)
        write_js(payload, args.output, publish=args.output.resolve() == OUTPUT.resolve())
        print(f"updated {args.output.relative_to(ROOT)} with {args.external_only} only")
        return 0

    discovery = load_contract_discovery()
    ak = load_akshare()
    discovery_products = discovery.get("products", {}) if isinstance(discovery, dict) else {}
    contracts = [
        merge_domestic(spec, selected, snapshot, ak, review_learning)
        for spec in DOMESTIC
        for selected in discovery_products.get(spec["symbol"], [])
    ]
    contracts.extend(merge_external(spec, snapshot, review_learning) for spec in EXTERNAL)

    source_note = "futures-oil-daily 最新快照"
    if snapshot_path:
        source_note += f"：{snapshot_path.relative_to(ROOT)}"
    source_note += "；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证"
    now = datetime.now(SHANGHAI)
    payload = {
        "updated_at": now.strftime("%Y-%m-%d %H:%M"),
        "update_session": args.update_session or infer_update_session(now),
        "timezone": "Asia/Shanghai",
        "source": source_note,
        "contract_selector_skill": discovery.get("selector_skill", "contract_selector_skill"),
        "contract_discovery_skill": "contract_discovery_skill",
        "contract_discovery_month": discovery.get("month", ""),
        "contract_discovery_warnings": discovery.get("warnings", []),
        "review_learning_warning": review_learning.get("warning", ""),
        "review_learning_repeated_errors": review_learning.get("repeated_errors", {}),
        "market_references": build_market_references(snapshot),
        "contracts": contracts,
        "watchlist_options": [
            {
                "value": contract.get("symbol"),
                "label": contract.get("contract"),
                "display": " ".join(
                    str(part)
                    for part in [contract.get("name"), contract.get("contract"), contract.get("contract_label")]
                    if part
                ),
                "name": contract.get("name"),
                "contract": contract.get("contract"),
                "product": contract.get("product") or contract.get("symbol"),
                "rank": contract.get("contract_rank"),
                "contract_label": contract.get("contract_label"),
            }
            for contract in contracts
        ],
    }
    if args.output.resolve() == OUTPUT.resolve():
        if metadata is None:
            tmp_output = OUTPUT.with_name(".oil_futures.quality-check.tmp.js")
            try:
                write_js(payload, tmp_output, publish=False)
                run_data_quality_gate(tmp_output)
            finally:
                tmp_output.unlink(missing_ok=True)
            write_js(payload, args.output)
            forecast_result = None
        else:
            forecast_result = validate_freeze_and_publish(payload, args.output, metadata)
    else:
        write_js(payload, args.output, publish=False)
        run_data_quality_gate(args.output)
        try:
            display_path = args.output.relative_to(ROOT)
        except ValueError:
            display_path = args.output
        print(f"updated {display_path} with {len(contracts)} contracts")
        return 0

    try:
        display_path = args.output.relative_to(ROOT)
    except ValueError:
        display_path = args.output
    print(f"updated {display_path} with {len(contracts)} contracts")
    if forecast_result is not None:
        print(
            f"forecast frozen for {metadata['report_date']}"
            + (" (already_exists)" if forecast_result.get("already_exists") else "")
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

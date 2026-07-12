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
import importlib.util
from pathlib import Path
from typing import Any

from sync_miniprogram_data import publish_dataset


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNS = ROOT / "source_runs"
OUTPUT = ROOT / "data" / "oil_futures.js"
REVIEW_DAILY_DIR = ROOT / "data" / "review" / "daily"
REVIEW_SNAPSHOT_DIR = ROOT / "data" / "review" / "snapshots"
HITHINK_CLI = Path.home() / ".codex" / "skills" / "hithink-market-query" / "scripts" / "cli.py"
MASTER_ANALYTIC_CLI = ROOT / "skills" / "master_analytic_skill" / "scripts" / "analyze_contracts.py"
DAILY_REVIEW_CLI = ROOT / "skills" / "daily_review_skill" / "scripts" / "daily_review.py"
REVIEW_MEMORY = ROOT / "skills" / "daily_review_skill" / "scripts" / "review_memory.py"
CONTRACT_SELECTOR_CLI = ROOT / "skills" / "contract_selector_skill" / "scripts" / "select_contracts.py"
CONTRACT_DISCOVERY_CLI = ROOT / "skills" / "contract_discovery_skill" / "scripts" / "select_contracts.py"
CONTRACT_DISCOVERY_CURRENT = ROOT / "data" / "contracts" / "current_contracts.json"
PRICE_TOLERANCE = 2.0
PCT_TOLERANCE = 0.25

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


def latest_market_snapshot() -> tuple[dict[str, Any] | None, Path | None]:
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
            if not selected_rows.empty:
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
        "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
        "score": analysis.get("score"),
        "view": analysis.get("view"),
        "technical_detail": analysis.get("technical_detail", []),
        "fundamental_detail": analysis.get("fundamental_detail", []),
        "strategy_recommendation": analysis.get("strategy_recommendation", {}),
        "analysis_skill": analysis.get("analysis_skill", "master_analytic_skill"),
        "child_skill": analysis.get("child_skill", "technical_basic_analysis_skill"),
        "quality_note": analysis.get("quality_note", "需进一步核验"),
    }


def write_js(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    output.write_text(f"window.OIL_FUTURES_CONTRACTS = {text};\n", encoding="utf-8")
    if output.resolve() == OUTPUT.resolve():
        publish_dataset("oil-futures", payload)


def archive_existing_output(output: Path, review_date: str) -> Path | None:
    if output.resolve() != OUTPUT.resolve() or not output.exists() or output.stat().st_size == 0:
        return None
    REVIEW_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    target = REVIEW_SNAPSHOT_DIR / f"{review_date}-previous-oil_futures.js"
    target.write_text(output.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def run_daily_review(previous: Path | None, current: Path, review_date: str) -> str:
    if previous is None or not DAILY_REVIEW_CLI.exists() or current.resolve() != OUTPUT.resolve():
        return ""
    result = subprocess.run(
        [
            sys.executable,
            str(DAILY_REVIEW_CLI),
            "--previous",
            str(previous),
            "--current",
            str(current),
            "--date",
            review_date,
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        return f"daily_review_skill failed: {result.stderr.strip() or result.stdout.strip()}"
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "daily_review_skill returned non-JSON output"
    return f"daily_review_skill wrote {payload.get('learning_notes_path', 'learning notes')}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update static oil futures contract data.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    snapshot, snapshot_path = latest_market_snapshot()
    review_learning = recent_review_learning()
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
    source_note += "；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证"
    now = datetime.now()
    review_date = now.strftime("%Y-%m-%d")
    payload = {
        "updated_at": now.strftime("%Y-%m-%d %H:%M"),
        "source": source_note,
        "contract_selector_skill": discovery.get("selector_skill", "contract_selector_skill"),
        "contract_discovery_skill": "contract_discovery_skill",
        "contract_discovery_month": discovery.get("month", ""),
        "contract_discovery_warnings": discovery.get("warnings", []),
        "review_learning_warning": review_learning.get("warning", ""),
        "review_learning_repeated_errors": review_learning.get("repeated_errors", {}),
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
    previous_output = archive_existing_output(args.output, review_date)
    write_js(payload, args.output)
    review_note = run_daily_review(previous_output, args.output, review_date)
    try:
        display_path = args.output.relative_to(ROOT)
    except ValueError:
        display_path = args.output
    print(f"updated {display_path} with {len(contracts)} contracts")
    if review_note:
        print(review_note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

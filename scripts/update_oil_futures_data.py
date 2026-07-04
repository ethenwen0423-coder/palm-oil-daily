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
MASTER_ANALYTIC_CLI = ROOT / "skills" / "master_analytic_skill" / "scripts" / "analyze_contracts.py"
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
    analysis = call_master_analysis(
        {
            "spec": spec,
            "source": source,
            "snapshot": snapshot,
            "history": history_records(history),
        }
    )
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Update static oil futures contract data.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    snapshot, snapshot_path = latest_market_snapshot()
    ak = load_akshare()
    contracts = [merge_domestic(spec, snapshot, ak) for spec in DOMESTIC]

    source_note = "futures-oil-daily 最新快照"
    if snapshot_path:
        source_note += f"：{snapshot_path.relative_to(ROOT)}"
    source_note += "；主卡片展示国内油脂主力合约，内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证；外盘仅作为联动因子纳入评分"
    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": source_note,
        "contracts": contracts,
    }
    write_js(payload, args.output)
    try:
        display_path = args.output.relative_to(ROOT)
    except ValueError:
        display_path = args.output
    print(f"updated {display_path} with {len(contracts)} contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

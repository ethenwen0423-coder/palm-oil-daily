#!/usr/bin/env python3
"""Build and send morning, close, and pre-night oilseed research reports."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SHANGHAI = ZoneInfo("Asia/Shanghai")
MESSAGES_SCRIPT = ROOT / "scripts" / "send_research_messages.applescript"
OIL_FUTURES = ROOT / "data" / "oil_futures.js"
REPORTS_INDEX = ROOT / "data" / "reports.js"
PUBLIC_BASE = "https://ethenwen0423-coder.github.io/palm-oil-daily"
MAX_MESSAGE_CHARS = 1000
FORBIDDEN = re.compile("未实际调用|当前环境未暴露调用入口|这是测试报告|排版调试样稿")
EDITION_LABEL = {"morning": "晨报", "close": "收盘复盘", "night": "夜盘前报告"}


class ResearchNotifierError(RuntimeError):
    """A fail-closed report, data, or delivery error."""


def support_dir(override: str | None = None) -> Path:
    configured = override or os.environ.get("PALM_OIL_RESEARCH_SUPPORT_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / "Library" / "Application Support" / "VinsonTesla" / "palm-oil-research"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def append_log(base: Path, event: dict[str, Any]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    base.chmod(0o700)
    safe = {key: value for key, value in event.items() if key not in {"recipient", "message"}}
    path = base / "runs.jsonl"
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(safe, ensure_ascii=False, allow_nan=False) + "\n")
    path.chmod(0o600)


def parse_wrapped_json(path: Path, variable: str | None = None) -> Any:
    text = path.read_text(encoding="utf-8").strip()
    if variable and not text.startswith(variable):
        raise ResearchNotifierError(f"{path.name} 缺少 {variable} 包装")
    if "=" in text and text.lstrip().startswith("window."):
        text = text.split("=", 1)[1].strip().removesuffix(";")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ResearchNotifierError(f"{path.name} 不是有效 JSON：{exc}") from exc


def auto_edition(now: datetime) -> str | None:
    minutes = now.hour * 60 + now.minute
    if 15 * 60 + 40 <= minutes < 17 * 60:
        return "close"
    if 20 * 60 + 30 <= minutes < 21 * 60:
        return "night"
    if 8 * 60 <= minutes < 10 * 60:
        return "morning"
    return None


def trading_dates() -> set[date]:
    try:
        import akshare as ak
        import pandas as pd

        frame = ak.tool_trade_date_hist_sina()
        values = pd.to_datetime(frame["trade_date"], errors="coerce").dropna()
        return {value.date() for value in values}
    except Exception:
        return set()


def is_trading_day(day: date, calendar: set[date] | None = None) -> bool:
    dates = calendar if calendar is not None else trading_dates()
    return day in dates if dates else day.weekday() < 5


def public_report_url(report_date: str) -> str:
    return f"{PUBLIC_BASE}/reports/{report_date}.md"


def verify_morning_report(report_date: str, require_public: bool = True) -> str:
    report = ROOT / "reports" / f"{report_date}.md"
    download = ROOT / "downloads" / f"{report_date}.md"
    if not report.is_file() or not download.is_file() or not REPORTS_INDEX.is_file():
        raise ResearchNotifierError("晨报、下载稿或报告索引缺失")
    content = report.read_text(encoding="utf-8")
    if not content.strip() or FORBIDDEN.search(content):
        raise ResearchNotifierError("晨报为空或命中禁用占位文案")
    index = REPORTS_INDEX.read_text(encoding="utf-8")
    if f'"date": "{report_date}"' not in index:
        raise ResearchNotifierError("报告索引尚未包含当天晨报")
    if require_public:
        try:
            import requests

            response = requests.get(public_report_url(report_date), timeout=(5, 15))
            if response.status_code != 200 or response.text.strip() != content.strip():
                raise ResearchNotifierError("公网晨报尚未更新为当天版本")
        except ResearchNotifierError:
            raise
        except Exception as exc:
            raise ResearchNotifierError(f"公网晨报核验失败：{exc}") from exc
    return content


def markdown_table_to_lines(block: list[str]) -> list[str]:
    rows: list[list[str]] = []
    for raw in block:
        cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
        if cells and not all(re.fullmatch(r":?-{3,}:?", cell or "-") for cell in cells):
            rows.append(cells)
    if len(rows) < 2:
        return ["；".join(row) for row in rows]
    header = rows[0]
    rendered: list[str] = []
    for row in rows[1:]:
        pairs = [f"{header[index]}：{value}" for index, value in enumerate(row) if index < len(header)]
        rendered.append("；".join(pairs))
    return rendered


def normalize_morning_markdown(content: str, report_date: str) -> str:
    lines = content.splitlines()
    result: list[str] = []
    table: list[str] = []
    skip_sources = False

    def flush_table() -> None:
        nonlocal table
        if table:
            result.extend(markdown_table_to_lines(table))
            table = []

    for raw in lines:
        line = raw.rstrip()
        if re.match(r"^##\s+【消息来源链接】", line):
            flush_table()
            skip_sources = True
            result.extend(["## 来源与完整报告", public_report_url(report_date)])
            continue
        if skip_sources:
            if re.match(r"^##\s+", line):
                skip_sources = False
            else:
                continue
        if line.startswith("|") and line.endswith("|"):
            table.append(line)
            continue
        flush_table()
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = line.replace("**", "").replace("`", "")
        result.append(line)
    flush_table()
    cleaned = "\n".join(result)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def as_float(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "需进一步核验", "待更新"):
            return None
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def fmt(value: Any, digits: int = 2) -> str:
    number = as_float(value)
    if number is None or not math.isfinite(number):
        return "需进一步核验"
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.{digits}f}"


def ema(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(value * alpha + result[-1] * (1 - alpha))
    return result


def calculate_indicators(rows: list[dict[str, Any]]) -> dict[str, Any]:
    clean = [
        {
            "close": as_float(row.get("close")),
            "high": as_float(row.get("high")),
            "low": as_float(row.get("low")),
        }
        for row in rows
    ]
    clean = [row for row in clean if all(value is not None for value in row.values())]
    if len(clean) < 60:
        return {"status": "insufficient"}
    close = [float(row["close"]) for row in clean]
    high = [float(row["high"]) for row in clean]
    low = [float(row["low"]) for row in clean]

    def mean(window: int) -> float:
        return sum(close[-window:]) / window

    ma = {window: mean(window) for window in (5, 10, 20, 60)}
    ema12, ema26 = ema(close, 12), ema(close, 26)
    diffs = [left - right for left, right in zip(ema12, ema26)]
    dea = ema(diffs, 9)
    changes = [close[index] - close[index - 1] for index in range(1, len(close))]
    gains = [max(value, 0) for value in changes[-14:]]
    losses = [max(-value, 0) for value in changes[-14:]]
    avg_gain, avg_loss = sum(gains) / 14, sum(losses) / 14
    rsi = 100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)

    k_value = d_value = 50.0
    for index in range(max(8, len(close) - 30), len(close)):
        highest = max(high[index - 8 : index + 1])
        lowest = min(low[index - 8 : index + 1])
        rsv = 50.0 if highest == lowest else (close[index] - lowest) / (highest - lowest) * 100
        k_value = 2 / 3 * k_value + 1 / 3 * rsv
        d_value = 2 / 3 * d_value + 1 / 3 * k_value
    sample = close[-20:]
    middle = sum(sample) / 20
    std = math.sqrt(sum((value - middle) ** 2 for value in sample) / 20)
    true_ranges: list[float] = []
    for index in range(len(close)):
        previous = close[index - 1] if index else close[index]
        true_ranges.append(max(high[index] - low[index], abs(high[index] - previous), abs(low[index] - previous)))
    return {
        "status": "ok",
        "ma": ma,
        "macd_dif": diffs[-1],
        "macd_dea": dea[-1],
        "macd_hist": (diffs[-1] - dea[-1]) * 2,
        "rsi14": rsi,
        "kdj_k": k_value,
        "kdj_d": d_value,
        "kdj_j": 3 * k_value - 2 * d_value,
        "boll_upper": middle + 2 * std,
        "boll_middle": middle,
        "boll_lower": middle - 2 * std,
        "atr14": sum(true_ranges[-14:]) / 14,
        "high20": max(high[-20:]),
        "low20": min(low[-20:]),
        "high60": max(high[-60:]),
        "low60": min(low[-60:]),
    }


def fetch_domestic_indicators(symbol: str) -> dict[str, Any]:
    code = """
import json
import sys
import akshare as ak
frame = ak.futures_zh_daily_sina(symbol=sys.argv[1])
rows = [] if frame is None else frame.tail(220).to_dict(orient="records")
print(json.dumps(rows, ensure_ascii=False, default=str))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, symbol],
            text=True,
            capture_output=True,
            timeout=35,
            check=False,
        )
        if result.returncode != 0:
            return {"status": "error", "reason": (result.stderr or result.stdout)[-300:]}
        return calculate_indicators(json.loads(result.stdout or "[]"))
    except subprocess.TimeoutExpired:
        return {"status": "error", "reason": "AkShare日线请求超时"}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def fetch_cbot_bean_oil() -> dict[str, Any]:
    try:
        import requests

        symbol = "BO=F"
        response = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}",
            params={"range": "6mo", "interval": "1d", "events": "history"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=(5, 20),
        )
        response.raise_for_status()
        chart = response.json()["chart"]["result"][0]
        quotes = chart["indicators"]["quote"][0]
        closes = quotes.get("close") or []
        highs = quotes.get("high") or []
        lows = quotes.get("low") or []
        rows = [
            {"close": close, "high": high, "low": low}
            for close, high, low in zip(closes, highs, lows)
            if close is not None and high is not None and low is not None
        ]
        indicators = calculate_indicators(rows)
        valid_closes = [float(value) for value in closes if value is not None]
        if not valid_closes:
            return {"status": "insufficient"}
        change = (
            (valid_closes[-1] - valid_closes[-2]) / valid_closes[-2] * 100
            if len(valid_closes) >= 2 and valid_closes[-2]
            else None
        )
        return {
            **indicators,
            "price": valid_closes[-1],
            "change": change,
            "source": "Yahoo Finance BO=F",
        }
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def technical_text(item: dict[str, Any], indicators: dict[str, Any]) -> str:
    name = f"{item.get('name', '')} {item.get('contract') or item.get('symbol')}"
    score = (item.get("score") or {}).get("technical")
    strategy = item.get("strategy_recommendation") or {}
    if indicators.get("status") != "ok":
        details = "；".join(str(row.get("text")) for row in item.get("technical_detail", []) if row.get("text"))
        return (
            f"{name}：现价{item.get('price', '需进一步核验')}，技术评分{score if score is not None else '需进一步核验'}。"
            f"{details or '完整技术指标历史序列需进一步核验。'}"
            f"上方观察{strategy.get('upper_watch', '需进一步核验')}，下方观察{strategy.get('lower_watch', '需进一步核验')}；"
            f"失效条件：{strategy.get('invalidation', '需进一步核验')}"
        )
    ma = indicators["ma"]
    macd_signal = "偏多" if indicators["macd_hist"] > 0 else "偏空"
    kdj_signal = "偏强" if indicators["kdj_k"] >= indicators["kdj_d"] else "偏弱"
    return (
        f"{name}：现价{item.get('price', '需进一步核验')}；"
        f"MA5/10/20/60={fmt(ma[5])}/{fmt(ma[10])}/{fmt(ma[20])}/{fmt(ma[60])}；"
        f"MACD柱{fmt(indicators['macd_hist'])}（{macd_signal}），RSI14={fmt(indicators['rsi14'])}，"
        f"K/D/J={fmt(indicators['kdj_k'])}/{fmt(indicators['kdj_d'])}/{fmt(indicators['kdj_j'])}（{kdj_signal}）；"
        f"BOLL={fmt(indicators['boll_upper'])}/{fmt(indicators['boll_middle'])}/{fmt(indicators['boll_lower'])}，"
        f"ATR14={fmt(indicators['atr14'])}；20日区间{fmt(indicators['low20'])}-{fmt(indicators['high20'])}，"
        f"60日区间{fmt(indicators['low60'])}-{fmt(indicators['high60'])}。"
        f"上方观察{strategy.get('upper_watch', '需进一步核验')}，下方观察{strategy.get('lower_watch', '需进一步核验')}；"
        f"失效条件：{strategy.get('invalidation', '需进一步核验')}"
    )


def refresh_private_snapshot(output: Path) -> None:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "update_oil_futures_data.py"),
        "--output",
        str(output),
        "--update-session",
        "manual",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=180, check=False)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise ResearchNotifierError(f"夜盘前行情刷新失败：{error[-500:]}")
    gate = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills" / "data_quality_gate_skill" / "scripts" / "validate_data.py"),
            "--oil-futures",
            str(output),
            "--strict",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )
    if gate.returncode != 0:
        raise ResearchNotifierError(f"夜盘前行情严格门禁失败：{(gate.stderr or gate.stdout)[-500:]}")


def select_contracts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for product in ("P", "Y", "OI"):
        match = next(
            (
                item
                for item in payload.get("contracts", [])
                if item.get("product") == product and item.get("contract_rank") == 1
            ),
            None,
        )
        if not match:
            raise ResearchNotifierError(f"行情快照缺少 {product} rank=1 主力")
        selected.append(match)
    fcpo = next((item for item in payload.get("contracts", []) if item.get("symbol") == "FCPO"), None)
    if fcpo:
        selected.append(fcpo)
    return selected


def compact_piece(text: str, limit: int) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(clean) <= limit:
        return clean
    cut = max(clean.rfind(mark, 0, limit) for mark in ("。", "；", "，"))
    if cut < limit // 2:
        cut = limit - 1
    return clean[: cut + 1].rstrip("，； ") + "…"


def normalized_section(text: str, heading: str, limit: int) -> str:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading) + 1
    except StopIteration:
        return ""
    selected: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("【") and stripped.endswith("】"):
            break
        if stripped in {"来源与完整报告", "油脂主力技术面补充"}:
            break
        if stripped:
            selected.append(stripped)
    return compact_piece(" ".join(selected), limit)


def compact_contract_line(item: dict[str, Any]) -> str:
    score = item.get("score") or {}
    strategy = item.get("strategy_recommendation") or {}
    position_text = " ".join(
        str(row.get("text") or "") for row in item.get("technical_detail", [])[:1]
    )
    ma20 = re.search(r"MA20\s*([0-9.]+)", position_text)
    ma60 = re.search(r"MA60\s*([0-9.]+)", position_text)
    ma_text = (
        f"MA20/60 {ma20.group(1)}/{ma60.group(1)}"
        if ma20 and ma60
        else "均线需核验"
    )
    return (
        f"{item.get('product')} {item.get('contract')} {item.get('price')}({item.get('change')})；"
        f"{score.get('stance', '需核验')}/技{score.get('technical', '需核验')}；{ma_text}；"
        f"观察{strategy.get('lower_watch', '需核验')}-{strategy.get('upper_watch', '需核验')}"
    )


def compact_market_report(payload: dict[str, Any], edition: str, report_date: str) -> str:
    selected = select_contracts(payload)
    domestic = selected[:3]
    ranked = sorted(
        domestic,
        key=lambda item: as_float((item.get("score") or {}).get("total")) or -1,
        reverse=True,
    )
    strength = ">".join(str(item.get("product") or "") for item in ranked)
    references = payload.get("market_references") or {}
    fcpo = references.get("malaysia_fcpo") or {}
    cbot = fetch_cbot_bean_oil()
    cbot_text = (
        f"{fmt(cbot.get('price'))}({fmt(cbot.get('change'))}%)"
        if cbot.get("status") == "ok"
        else "需进一步核验"
    )
    risks = [
        str((item.get("score") or {}).get("contradiction_warning") or "")
        for item in domestic
    ]
    risks = list(dict.fromkeys(risk for risk in risks if risk))
    lines = [
        f"结论：三油强弱{strength}；技术面只判断位置与节奏，需结合外盘和资金确认。",
        *[compact_contract_line(item) for item in domestic],
        f"外盘：FCPO {fcpo.get('price', '需核验')}({fcpo.get('change', '需核验')})；CBOT豆油 {cbot_text}。",
        f"风险：{compact_piece('；'.join(risks), 130) or '跨源数据冲突或驱动反向时降级观望。'}",
        f"快照：{payload.get('updated_at', '需进一步核验')}。仅供研究参考，不构成交易指令。",
    ]
    return "\n".join(lines)


def compact_morning_report(content: str, payload: dict[str, Any] | None, report_date: str) -> str:
    normalized = normalize_morning_markdown(content, report_date)
    viewpoint = normalized_section(normalized, "【今日观点】", 190)
    strategy = normalized_section(normalized, "【今日交易信号】", 170)
    risk = normalized_section(normalized, "【风险提示】", 130)
    lines = [
        f"观点：{viewpoint or '需进一步核验'}",
        f"策略：{strategy or '需进一步核验'}",
    ]
    if payload:
        selected = select_contracts(payload)
        lines.extend(compact_contract_line(item) for item in selected[:3])
        references = payload.get("market_references") or {}
        fcpo = references.get("malaysia_fcpo") or {}
        cbot = fetch_cbot_bean_oil()
        cbot_text = (
            f"{fmt(cbot.get('price'))}({fmt(cbot.get('change'))}%)"
            if cbot.get("status") == "ok"
            else "需进一步核验"
        )
        lines.append(
            f"外盘：FCPO {fcpo.get('price', '需核验')}({fcpo.get('change', '需核验')})；"
            f"CBOT豆油 {cbot_text}。"
        )
    else:
        lines.append("技术面：当天主力快照未就绪，需进一步核验。")
    lines.extend(
        [
            f"风险：{risk or '驱动与资金反向时降级观望。'}",
            f"全文：{public_report_url(report_date)}",
        ]
    )
    return "\n".join(lines)


def build_session_report(payload: dict[str, Any], edition: str, report_date: str) -> str:
    updated_at = str(payload.get("updated_at") or "需进一步核验")
    selected = select_contracts(payload)
    domestic = selected[:3]
    ranked = sorted(
        domestic,
        key=lambda item: as_float((item.get("score") or {}).get("total")) or -1,
        reverse=True,
    )
    strength = " > ".join(item.get("product", "") for item in ranked)
    title = f"{report_date} 油脂{EDITION_LABEL[edition]}"
    lines = [
        title,
        "",
        "一、核心观点",
        f"三大油脂综合强弱：{strength}。本报告以{updated_at}快照为准；技术面只判断位置和节奏，最终观点同时受外盘、驱动和资金约束。",
        "",
        "二、主力行情与观点",
    ]
    for item in domestic:
        score = item.get("score") or {}
        lines.append(
            f"{item.get('name')} {item.get('contract')}：{item.get('price')}（{item.get('change')}），"
            f"综合/技术/驱动/资金评分={score.get('total', '需进一步核验')}/"
            f"{score.get('technical', '需进一步核验')}/{score.get('driver', '需进一步核验')}/"
            f"{score.get('money_flow', '需进一步核验')}；观点：{score.get('stance', '需进一步核验')}，"
            f"置信度{score.get('view_confidence', '需进一步核验')}。{item.get('view', '')}"
        )
    lines.extend(["", "三、技术面"])
    for item in selected:
        indicators = (
            fetch_domestic_indicators(str(item.get("contract") or item.get("symbol")))
            if item.get("product") in {"P", "Y", "OI"}
            else {"status": "insufficient"}
        )
        lines.append(technical_text(item, indicators))
    cbot_live = fetch_cbot_bean_oil()
    lines.append(
        technical_text(
            {
                "name": "CBOT豆油",
                "contract": "BO=F",
                "price": fmt(cbot_live.get("price")),
                "technical_detail": [],
                "strategy_recommendation": {},
            },
            cbot_live,
        )
    )

    references = payload.get("market_references") or {}
    fcpo = references.get("malaysia_fcpo") or {}
    cbot = references.get("cbot_bean_oil") or references.get("cbot_soybean_oil") or {}
    lines.extend(
        [
            "",
            "四、外盘与驱动",
            f"FCPO：{fcpo.get('price', '需进一步核验')}（{fcpo.get('change', '需进一步核验')}），更新时间{fcpo.get('updated_at', '需进一步核验')}。",
            (
                f"CBOT豆油：{fmt(cbot_live.get('price'))}（"
                f"{fmt(cbot_live.get('change'))}%），来源{cbot_live.get('source', '需进一步核验')}。"
                if cbot_live.get("status") == "ok"
                else f"CBOT豆油：{cbot.get('price', '需进一步核验')}（{cbot.get('change', '需进一步核验')}），更新时间{cbot.get('updated_at', '需进一步核验')}。"
            ),
        ]
    )
    for item in domestic:
        details = "；".join(str(row.get("text")) for row in item.get("fundamental_detail", []) if row.get("text"))
        if details:
            lines.append(f"{item.get('product')}联动：{details}")
    lines.extend(["", "五、情景与风险"])
    for item in domestic:
        strategy = item.get("strategy_recommendation") or {}
        lines.append(
            f"{item.get('product')}：观察{strategy.get('lower_watch', '需进一步核验')}-"
            f"{strategy.get('upper_watch', '需进一步核验')}；"
            f"{strategy.get('invalidation', '观点失效条件需进一步核验')} "
            f"{strategy.get('risk_tip', '仅供研究参考，不构成交易指令。')}"
        )
    lines.extend(
        [
            "",
            "六、核验说明",
            f"数据源：{payload.get('source', '需进一步核验')}。",
            "核心字段缺失或跨源不一致时已降级为“需进一步核验”；技术指标存在滞后性，不构成投资建议或自动交易指令。",
            "",
            "本报告仅通过 Messages 发送，不在研究网页归档。",
        ]
    )
    return "\n".join(lines)


def build_technical_supplement(payload: dict[str, Any]) -> str:
    selected = select_contracts(payload)
    lines = ["油脂主力技术面补充"]
    for item in selected:
        indicators = (
            fetch_domestic_indicators(str(item.get("contract") or item.get("symbol")))
            if item.get("product") in {"P", "Y", "OI"}
            else {"status": "insufficient"}
        )
        lines.append(technical_text(item, indicators))
    cbot_live = fetch_cbot_bean_oil()
    lines.append(
        technical_text(
            {
                "name": "CBOT豆油",
                "contract": "BO=F",
                "price": fmt(cbot_live.get("price")),
                "technical_detail": [],
                "strategy_recommendation": {},
            },
            cbot_live,
        )
    )
    return "\n".join(lines)


def prepare_messages(text: str, report_date: str, edition: str) -> list[str]:
    prefix = f"【棕榈油研究·{EDITION_LABEL[edition]}·{report_date}】\n"
    available = MAX_MESSAGE_CHARS - len(prefix)
    body = re.sub(r"[ \t]+", " ", text).strip()
    if len(body) > available:
        cut = max(body.rfind(mark, 0, available) for mark in ("\n", "。", "；"))
        if cut < available // 2:
            cut = available - 1
        body = body[: cut + 1].rstrip() + "…"
    return [prefix + body]


def send_message(recipient: str, message: str, attempts: int = 3) -> None:
    if not MESSAGES_SCRIPT.is_file():
        raise ResearchNotifierError(f"Messages 脚本不存在：{MESSAGES_SCRIPT}")
    last_error = ""
    for attempt in range(attempts):
        try:
            subprocess.run(
                ["/usr/bin/open", "-g", "-a", "Messages"],
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )
            time.sleep(1 if attempt == 0 else 2)
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            result = subprocess.run(
                ["/usr/bin/osascript", str(MESSAGES_SCRIPT), recipient, message],
                text=True,
                capture_output=True,
                timeout=40,
                check=False,
            )
            if result.returncode == 0:
                return
            last_error = result.stderr.strip() or result.stdout.strip()
        except subprocess.TimeoutExpired:
            last_error = "Messages 调用超时"
        if attempt + 1 < attempts:
            time.sleep(2)
    raise ResearchNotifierError(f"Messages 提交失败：{last_error or '未知错误'}")


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "deliveries": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ResearchNotifierError(f"投递状态损坏，拒绝自动重置：{exc}") from exc
    if payload.get("version") != 1 or not isinstance(payload.get("deliveries"), dict):
        raise ResearchNotifierError("投递状态版本或结构不合法")
    return payload


def digest(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


def deliver(
    messages: list[str],
    report_date: str,
    edition: str,
    base: Path,
    dry_run: bool,
) -> dict[str, Any]:
    if len(messages) != 1:
        raise ResearchNotifierError("研究报告必须限制为一个 Messages 气泡")
    key = f"{report_date}:{edition}"
    path = base / "state.json"
    state = load_state(path)
    delivery = state["deliveries"].setdefault(key, {"sent_hashes": [], "completed": False})
    hashes = [digest(message) for message in messages]
    if delivery.get("completed") and delivery.get("message_hashes") == hashes:
        return {"status": "duplicate", "edition": edition, "date": report_date, "parts": len(messages)}
    if dry_run:
        return {
            "status": "dry_run",
            "edition": edition,
            "date": report_date,
            "parts": len(messages),
            "messages": messages,
        }
    recipient = os.environ.get("PALM_OIL_MESSAGE_RECIPIENT", "").strip()
    confirmed = os.environ.get("PALM_OIL_MESSAGE_RECEIPT_CONFIRMED", "").strip().lower()
    if not recipient:
        raise ResearchNotifierError("缺少 PALM_OIL_MESSAGE_RECIPIENT")
    if confirmed not in {"1", "true", "yes"}:
        raise ResearchNotifierError("Messages 接收端尚未确认，拒绝发送正式报告")
    sent = set(delivery.get("sent_hashes") or [])
    for message, message_hash in zip(messages, hashes):
        if message_hash in sent:
            continue
        send_message(recipient, message)
        sent.add(message_hash)
        delivery.update({"sent_hashes": sorted(sent), "message_hashes": hashes, "completed": False})
        atomic_write_json(path, state)
        time.sleep(0.5)
    delivery.update(
        {
            "sent_hashes": hashes,
            "message_hashes": hashes,
            "completed": True,
            "submitted_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        }
    )
    # Retain about one month of three-edition delivery keys.
    for old_key in sorted(state["deliveries"])[:-100]:
        state["deliveries"].pop(old_key, None)
    atomic_write_json(path, state)
    return {"status": "submitted_to_messages", "edition": edition, "date": report_date, "parts": len(messages)}


def write_audit_report(base: Path, report_date: str, edition: str, text: str) -> None:
    if edition == "morning":
        return
    path = base / "reports" / f"{report_date}-{edition}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(text + "\n", encoding="utf-8")
    path.chmod(0o600)


def build_report(
    edition: str,
    report_date: str,
    snapshot: Path | None,
    require_public: bool,
) -> str:
    if edition == "morning":
        content = verify_morning_report(report_date, require_public=require_public)
        payload: dict[str, Any] | None = None
        try:
            candidate = parse_wrapped_json(OIL_FUTURES, "window.OIL_FUTURES_CONTRACTS")
            if str(candidate.get("updated_at") or "").startswith(report_date):
                payload = candidate
        except Exception:
            payload = None
        return compact_morning_report(content, payload, report_date)
    if snapshot:
        payload = parse_wrapped_json(snapshot)
    elif edition == "close":
        payload = parse_wrapped_json(OIL_FUTURES, "window.OIL_FUTURES_CONTRACTS")
        if not str(payload.get("updated_at") or "").startswith(report_date):
            raise ResearchNotifierError("收盘行情快照不是当天数据")
        if payload.get("update_session") != "close":
            raise ResearchNotifierError("收盘行情快照尚未完成 close 更新")
    else:
        with tempfile.TemporaryDirectory(prefix="palm-oil-research-night.") as temporary:
            output = Path(temporary) / "oil_futures.js"
            refresh_private_snapshot(output)
            payload = parse_wrapped_json(output, "window.OIL_FUTURES_CONTRACTS")
    return compact_market_report(payload, edition, report_date)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edition", choices=["auto", "morning", "close", "night"], default="auto")
    parser.add_argument("--date", help="报告日期，默认上海当前日期")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--send-test", action="store_true")
    parser.add_argument("--support-dir")
    parser.add_argument("--snapshot", type=Path, help="测试或补跑用行情快照")
    parser.add_argument("--skip-public-check", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--allow-non-trading-day", action="store_true", help=argparse.SUPPRESS)
    return parser


def final_attempt(edition: str, now: datetime) -> bool:
    minutes = now.hour * 60 + now.minute
    thresholds = {"morning": 8 * 60 + 40, "close": 16 * 60, "night": 20 * 60 + 45}
    return minutes >= thresholds[edition]


def send_failure_alert(base: Path, report_date: str, edition: str, reason: str) -> None:
    marker = base / f"{report_date}-{edition}-failure-alert.ok"
    if marker.exists():
        return
    recipient = os.environ.get("PALM_OIL_MESSAGE_RECIPIENT", "").strip()
    confirmed = os.environ.get("PALM_OIL_MESSAGE_RECEIPT_CONFIRMED", "").strip().lower()
    if not recipient or confirmed not in {"1", "true", "yes"}:
        return
    compact = re.sub(r"\s+", " ", reason).strip()[:280]
    send_message(
        recipient,
        f"【棕榈油研究·{EDITION_LABEL[edition]}·{report_date}】报告暂不可用：{compact}",
    )
    marker.touch(mode=0o600)


def main() -> int:
    args = build_parser().parse_args()
    now = datetime.now(SHANGHAI)
    report_date = args.date or now.date().isoformat()
    edition = auto_edition(now) if args.edition == "auto" else args.edition
    if not edition:
        print(json.dumps({"status": "skipped", "reason": "当前不属于研究报告发送窗口"}, ensure_ascii=False))
        return 0
    base = support_dir(args.support_dir)
    event: dict[str, Any] = {
        "generated_at": now.isoformat(timespec="seconds"),
        "date": report_date,
        "edition": edition,
    }
    base.mkdir(parents=True, exist_ok=True)
    base.chmod(0o700)
    lock_path = base / "run.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "skipped", "reason": "已有研究报告任务运行中"}, ensure_ascii=False))
            return 0
        try:
            day = date.fromisoformat(report_date)
            if not args.allow_non_trading_day and not is_trading_day(day):
                event.update({"status": "skipped", "reason": "不是中国期货交易日"})
                append_log(base, event)
                print(json.dumps(event, ensure_ascii=False))
                return 0
            if args.send_test:
                result = deliver(
                    prepare_messages("测试信息：棕榈油研究报告 Messages 通道已连通。", report_date, edition),
                    f"test-{report_date}",
                    edition,
                    base,
                    dry_run=False,
                )
            else:
                text = build_report(
                    edition,
                    report_date,
                    args.snapshot,
                    require_public=not args.skip_public_check,
                )
                write_audit_report(base, report_date, edition, text)
                messages = prepare_messages(text, report_date, edition)
                result = deliver(messages, report_date, edition, base, args.dry_run)
            event.update(result)
            append_log(base, event)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        except Exception as exc:
            event.update({"status": "error", "error": str(exc)})
            if not args.dry_run and final_attempt(edition, now):
                try:
                    send_failure_alert(base, report_date, edition, str(exc))
                    event["failure_alert_submitted"] = True
                except Exception as alert_exc:
                    event["failure_alert_submitted"] = False
                    event["failure_alert_error"] = str(alert_exc)
            append_log(base, event)
            print(json.dumps(event, ensure_ascii=False), file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())

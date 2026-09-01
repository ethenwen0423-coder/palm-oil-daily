#!/usr/bin/env python3
"""Resolve exact-contract exchange margin rates with auditable sources.

SHFE/INE contracts use the exchange's official daily parameter file. Other
exchanges use the exchange-standard fields published by 9qihuo (also exposed
by AKShare ``futures_comm_info``). A missing or stale rate is never replaced
with a generic portfolio default.
"""
from __future__ import annotations

import json
import math
import re
import time
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SHFE_DAILY_URL = "https://www.shfe.cn/data/busiparamdata/future/ContractDailyTradeArgument{day}.dat"
QIHUO_URL = "https://www.9qihuo.com/qihuoshouxufei"
MAX_SOURCE_AGE_DAYS = 7
QIHUO_FETCH_ATTEMPTS = 2
CONTRACT_RE = re.compile(r"^([A-Z]{1,3})(\d{4})$")
VALIDATION_NOTE = "真实PYYMM逐合约；保留多空保证金并按实际持仓方向使用；缺失或超过7日不使用默认比例"


class MarginRateError(RuntimeError):
    pass


class _QihuoTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict[str, Any]] = []
        self._in_row = False
        self._in_cell = False
        self._in_bold = False
        self._cells: list[str] = []
        self._cell_parts: list[str] = []
        self._code_parts: list[str] = []
        self._updated_at: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "tr":
            self._in_row = True
            self._cells = []
            self._updated_at = None
        elif tag in {"td", "th"} and self._in_row:
            self._in_cell = True
            self._cell_parts = []
            title = values.get("title") or ""
            match = re.search(r"手续费更新时间[：:]\s*([0-9-]+\s+[0-9:.]+)", title)
            if match:
                self._updated_at = match.group(1)
        elif tag == "b" and self._in_cell:
            self._in_bold = True
            self._code_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)
        if self._in_bold:
            self._code_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "b" and self._in_bold:
            self._in_bold = False
            code = "".join(self._code_parts).strip().upper()
            if code:
                self._cells.append("__CODE__=" + code)
        elif tag in {"td", "th"} and self._in_cell:
            self._in_cell = False
            self._cells.append(" ".join("".join(self._cell_parts).split()))
        elif tag == "tr" and self._in_row:
            self._in_row = False
            code = next((value.split("=", 1)[1] for value in self._cells if value.startswith("__CODE__=")), None)
            visible = [value for value in self._cells if not value.startswith("__CODE__=")]
            if code and len(visible) >= 5:
                self.rows.append({
                    "raw_contract": code,
                    "long_rate": _percent(visible[3]),
                    "short_rate": _percent(visible[4]),
                    "source_updated_at": self._updated_at,
                })


def _percent(value: Any) -> float | None:
    try:
        number = float(str(value).replace("%", "").strip()) / 100.0
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and 0 < number <= 1 else None


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and 0 < number <= 1 else None


def contract_aliases(contract: str) -> set[str]:
    normalized = re.sub(r"[^A-Za-z0-9]", "", contract).upper()
    match = CONTRACT_RE.fullmatch(normalized)
    if not match:
        raise MarginRateError(f"invalid exact contract {contract!r}")
    variety, digits = match.groups()
    return {normalized, variety + digits[1:]}


def parse_qihuo_margin_rows(html: str, contracts: list[str]) -> dict[str, dict[str, Any]]:
    parser = _QihuoTableParser()
    parser.feed(html)
    requested = {contract.upper(): contract_aliases(contract) for contract in contracts}
    result: dict[str, dict[str, Any]] = {}
    for row in parser.rows:
        raw = row["raw_contract"]
        canonical = next((contract for contract, aliases in requested.items() if raw in aliases), None)
        if not canonical:
            continue
        rates = [value for value in (row["long_rate"], row["short_rate"]) if value is not None]
        if not rates:
            continue
        result[canonical] = {
            "contract": canonical,
            "margin_rate": max(rates),
            "long_margin_rate": row["long_rate"],
            "short_margin_rate": row["short_rate"],
            "source": "AKShare futures_comm_info / 九期网交易所标准保证金",
            "source_url": QIHUO_URL,
            "source_updated_at": row["source_updated_at"],
            "official_direct": False,
        }
    return result


def parse_shfe_margin_rows(payload: dict[str, Any], contracts: list[str]) -> dict[str, dict[str, Any]]:
    wanted = {contract.upper() for contract in contracts}
    result: dict[str, dict[str, Any]] = {}
    for row in payload.get("ContractDailyTradeArgument", []):
        contract = str(row.get("INSTRUMENTID", "")).upper()
        if contract not in wanted:
            continue
        long_rate = _number(row.get("SPEC_LONGMARGINRATIO"))
        short_rate = _number(row.get("SPEC_SHORTMARGINRATIO"))
        rates = [value for value in (long_rate, short_rate) if value is not None]
        if not rates:
            continue
        trade_day = str(row.get("TRADINGDAY") or payload.get("report_date") or "")
        result[contract] = {
            "contract": contract,
            "margin_rate": max(rates),
            "long_margin_rate": long_rate,
            "short_margin_rate": short_rate,
            "source": "上海期货交易所每日交易参数（一般持仓）",
            "source_url": SHFE_DAILY_URL.format(day=trade_day),
            "source_updated_at": trade_day,
            "official_direct": True,
        }
    return result


def _download_text(url: str, timeout: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AI-Daredevil-Margin-Audit/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _fetch_shfe(contracts: list[str], as_of: date, timeout: int) -> tuple[dict[str, dict[str, Any]], str | None]:
    for offset in range(8):
        day = (as_of - timedelta(days=offset)).strftime("%Y%m%d")
        url = SHFE_DAILY_URL.format(day=day)
        try:
            payload = json.loads(_download_text(url, timeout))
        except (OSError, ValueError):
            continue
        rows = parse_shfe_margin_rows(payload, contracts)
        if rows:
            return rows, day
    return {}, None


def _parse_source_date(value: Any) -> date | None:
    text = str(value or "").strip()
    match = re.search(r"(20\d{2})[-/]?(\d{2})[-/]?(\d{2})", text)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def source_is_fresh(row: dict[str, Any], as_of: date) -> bool:
    source_day = _parse_source_date(row.get("source_updated_at"))
    return source_day is not None and 0 <= (as_of - source_day).days <= MAX_SOURCE_AGE_DAYS


def fetch_margin_book(contracts: list[str], as_of: date, timeout: int = 30) -> dict[str, Any]:
    exact = sorted({contract.upper() for contract in contracts if contract})
    rates, official_day = _fetch_shfe(exact, as_of, min(timeout, 20))
    missing = [contract for contract in exact if contract not in rates]
    qihuo_error = None
    if missing:
        # The public table occasionally stalls from the production network.
        # Retry once, but cap each request so a refresh can never retain the
        # automation lock indefinitely.
        qihuo_timeout = min(max(timeout, 10), 30)
        for attempt in range(QIHUO_FETCH_ATTEMPTS):
            try:
                qihuo = parse_qihuo_margin_rows(
                    _download_text(QIHUO_URL, qihuo_timeout), missing
                )
                rates.update(qihuo)
                qihuo_error = None
                break
            except (OSError, ValueError) as exc:
                qihuo_error = f"{type(exc).__name__}: {exc}"
                if attempt + 1 < QIHUO_FETCH_ATTEMPTS:
                    time.sleep(0.75 * (attempt + 1))
    stale = sorted(contract for contract, row in rates.items() if not source_is_fresh(row, as_of))
    for contract in stale:
        rates.pop(contract, None)
    unresolved = sorted(set(exact) - set(rates))
    return {
        "schema_version": 1,
        "as_of": as_of.isoformat(),
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "coverage_status": "complete" if not unresolved else "partial",
        "expected_count": len(exact),
        "validated_count": len(rates),
        "unresolved_contracts": unresolved,
        "stale_contracts": stale,
        "official_shfe_report_date": official_day,
        "qihuo_error": qihuo_error,
        "rates": rates,
        "validation": VALIDATION_NOTE,
    }


def load_cached_margin_book(path: Path, contracts: list[str], as_of: date) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rates = payload.get("rates", {}) if isinstance(payload, dict) else {}
    if not isinstance(rates, dict):
        return None
    wanted = {contract.upper() for contract in contracts}
    if not wanted.issubset(rates):
        return None
    if any(not source_is_fresh(rates[contract], as_of) for contract in wanted):
        return None
    payload["validation"] = VALIDATION_NOTE
    payload["cache_used"] = True
    return payload

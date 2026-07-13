#!/usr/bin/env python3
"""Deterministic data quality gate for report and oil-futures publishing."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[3]
PRICE_TOLERANCE = 2.0
PCT_TOLERANCE = 0.25
DOMESTIC_PRODUCTS = {"P", "Y", "OI", "M", "RM"}
CRITICAL_PRODUCTS = {"P", "Y", "OI"}
UNKNOWN = "需进一步核验"


def now_shanghai() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z")


def parse_json_or_js(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^\s*window\.[A-Z0-9_]+\s*=\s*", "", text).strip()
    if text.endswith(";"):
        text = text[:-1]
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def as_float(value: Any) -> float | None:
    if value in (None, "", "-", UNKNOWN):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    text = str(value).replace(",", "").replace("%", "").strip()
    text = re.sub(r"\s*(万手|手|元/吨|吨|万吨|美元/桶|美元|点)$", "", text)
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def parse_pct(value: Any) -> float | None:
    return as_float(value)


def valid_contract_month(symbol: str, base: datetime) -> bool:
    match = re.fullmatch(r"([A-Z]+)(\d{2})(\d{2})", str(symbol or "").upper())
    if not match:
        return False
    month = int(match.group(3))
    if not 1 <= month <= 12:
        return False
    year = 2000 + int(match.group(2))
    return (year, month) >= (base.year, base.month)


def add_issue(target: list[str], message: str) -> None:
    if message not in target:
        target.append(message)


def validate_manifest(path: Path, errors: list[str], warnings: list[str]) -> None:
    if not path.exists():
        add_issue(errors, f"source manifest 缺失：{path}")
        return
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add_issue(errors, f"source manifest 无法解析：{exc}")
        return
    results = manifest.get("results")
    if not isinstance(results, list) or not results:
        add_issue(errors, "source manifest 缺少 results")
        return
    ok_results = [item for item in results if isinstance(item, dict) and item.get("status") == "ok"]
    if not ok_results:
        add_issue(errors, "全部金融数据源失败，禁止正式发布")
    market_items = [
        item
        for item in results
        if isinstance(item, dict) and item.get("name") in {"mx_data_market", "iwencai_market", "futures_oil_fetch_market_data"}
    ]
    if not any(item.get("status") == "ok" for item in market_items):
        add_issue(errors, "关键行情数据源均未成功，禁止正式发布")
    symbols = manifest.get("contract_discovery", {}).get("symbols")
    if symbols is not None and not isinstance(symbols, list):
        add_issue(warnings, "contract_discovery.symbols 格式异常")


def validate_contract(item: dict[str, Any], base: datetime, errors: list[str], warnings: list[str], downgraded: list[str]) -> None:
    symbol = str(item.get("symbol") or item.get("contract") or "").upper()
    product = str(item.get("product") or item.get("symbol") or "").upper()
    rank = item.get("contract_rank") or item.get("rank")
    label = f"{symbol or product}"
    is_domestic = product in DOMESTIC_PRODUCTS
    is_critical_rank = product in CRITICAL_PRODUCTS and rank in (1, "1", None)

    if is_domestic:
        if not valid_contract_month(symbol, base):
            add_issue(errors if is_critical_rank else warnings, f"{label} 合约月份非法或已过期")
        if symbol and product and not symbol.startswith(product):
            add_issue(errors if is_critical_rank else warnings, f"{label} 合约代码与品种前缀不一致")

    price = as_float(item.get("price"))
    preclose = as_float(item.get("preclose"))
    change_pct = parse_pct(item.get("change"))
    trade_date = str(item.get("trade_date") or "").strip()
    source = str(item.get("source") or "").strip()
    verification = str(item.get("verification") or "")

    if is_critical_rank and price is None:
        add_issue(errors, f"{label} 最新价缺失，禁止正式发布")
    elif is_domestic and price is None:
        add_issue(warnings, f"{label} 最新价缺失，降级为需进一步核验")
        downgraded.append(f"{label}.price")

    if is_domestic and not trade_date:
        add_issue(errors if is_critical_rank else warnings, f"{label} 缺少交易日期")
    if is_domestic and not source:
        add_issue(warnings, f"{label} 缺少行情来源")

    if price is not None and preclose not in (None, 0) and change_pct is not None:
        expected = (price - float(preclose)) / float(preclose) * 100
        if abs(expected - change_pct) > PCT_TOLERANCE:
            msg = f"{label} 涨跌幅与最新价/昨收不一致：计算 {expected:.2f}%，当前 {change_pct:.2f}%"
            add_issue(errors if is_critical_rank else warnings, msg)
            downgraded.append(f"{label}.change")
    elif is_critical_rank:
        add_issue(warnings, f"{label} 缺少昨收或涨跌幅，无法做公式复核")

    if "价格不一致" in verification or "涨跌幅口径不同" in verification:
        add_issue(errors if is_critical_rank else warnings, f"{label} 跨来源行情冲突超过容差")
        downgraded.append(f"{label}.source_conflict")

    if product == "FCPO" or symbol.startswith("FCPO"):
        basis_text = " ".join([verification, str(item.get("note") or ""), str(item.get("change_basis") or ""), source])
        if not any(word in basis_text for word in ["昨收", "previous close", "settlement", "结算", "开盘", "open"]):
            add_issue(warnings, "FCPO 涨跌口径未明确说明是相对昨收、结算价还是开盘价")
            downgraded.append("FCPO.change_basis")


def validate_fundamental_dates(payload: dict[str, Any], warnings: list[str], downgraded: list[str]) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    for keyword in ["库存", "出口", "产量"]:
        if keyword not in text:
            continue
        has_date = bool(re.search(r"(统计日期|更新日期|published_at|fetched_at|date|tradedate)", text))
        if not has_date:
            add_issue(warnings, f"{keyword}数据出现但缺少统计日期或更新时间")
            downgraded.append(f"{keyword}.stat_date")


def validate_oil_futures(path: Path, errors: list[str], warnings: list[str], downgraded: list[str]) -> None:
    payload = parse_json_or_js(path)
    base = datetime.now(ZoneInfo("Asia/Shanghai"))
    updated_at = str(payload.get("updated_at") or "").strip()
    if not updated_at:
        add_issue(errors, "oil_futures 缺少 updated_at")
    elif not re.search(r"\d{4}-\d{2}-\d{2}", updated_at):
        add_issue(errors, "oil_futures updated_at 日期格式非法")

    contracts = payload.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        add_issue(errors, "oil_futures 缺少 contracts")
        return
    for item in contracts:
        if isinstance(item, dict):
            validate_contract(item, base, errors, warnings, downgraded)

    domestic_symbols = [str(item.get("symbol") or "") for item in contracts if isinstance(item, dict) and item.get("product") in DOMESTIC_PRODUCTS]
    for product in ["P", "Y", "OI"]:
        if not any(symbol.startswith(product) for symbol in domestic_symbols):
            add_issue(errors, f"oil_futures 缺少 {product} 合约")

    validate_fundamental_dates(payload, warnings, downgraded)


def result(status: str, errors: list[str], warnings: list[str], downgraded: list[str]) -> dict[str, Any]:
    return {
        "status": status,
        "can_publish": not errors,
        "critical_errors": errors,
        "warnings": warnings,
        "downgraded_fields": sorted(set(downgraded)),
        "checked_at": now_shanghai(),
        "skill": "data_quality_gate_skill",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oil-futures", type=Path, help="Path to data/oil_futures.js or compatible JSON.")
    parser.add_argument("--manifest", type=Path, help="Path to source_runs/.../manifest.json.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when critical checks fail.")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    downgraded: list[str] = []

    if not args.oil_futures and not args.manifest:
        errors.append("必须提供 --oil-futures 或 --manifest")
    if args.manifest:
        validate_manifest(args.manifest, errors, warnings)
    if args.oil_futures:
        try:
            validate_oil_futures(args.oil_futures, errors, warnings, downgraded)
        except Exception as exc:
            errors.append(f"oil_futures 校验失败：{exc}")

    payload = result("blocked" if errors else "ok", errors, warnings, downgraded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Discover this month's liquid oil and meal futures contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "config" / "contract_discovery.json"
OUTPUT_DIR = ROOT / "data" / "contracts"
CURRENT_OUTPUT = OUTPUT_DIR / "current_contracts.json"
SOURCE = "akshare:futures_zh_realtime"

DEFAULT_PRODUCTS: dict[str, dict[str, Any]] = {
    "P": {"name": "棕榈油", "query": "棕榈", "limit": 2, "market": "DCE"},
    "Y": {"name": "豆油", "query": "豆油", "limit": 2, "market": "DCE"},
    "OI": {"name": "菜油", "query": "菜油", "limit": 2, "market": "CZCE"},
    "M": {"name": "豆粕", "query": "豆粕", "limit": 2, "market": "DCE"},
    "RM": {"name": "菜粕", "query": "菜粕", "limit": 2, "market": "CZCE"},
}


def load_akshare():
    try:
        import akshare as ak  # type: ignore

        return ak
    except Exception as exc:
        raise RuntimeError(f"akshare 不可用：{exc}") from exc


def as_int(value: Any) -> int | None:
    try:
        if value in (None, "", "-"):
            return None
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return int(float(value))
    except (TypeError, ValueError):
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


def load_config(path: Path = CONFIG) -> dict[str, dict[str, Any]]:
    products = {key: value.copy() for key, value in DEFAULT_PRODUCTS.items()}
    if not path.exists():
        return products
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        products["_config_warning"] = {"warning": f"config/contract_discovery.json 无法解析：{exc}"}
        return products
    if not isinstance(payload, dict):
        products["_config_warning"] = {"warning": "config/contract_discovery.json 必须是对象"}
        return products
    for product, override in payload.items():
        if product.startswith("_") or not isinstance(override, dict):
            continue
        base = products.get(product, {}).copy()
        base.update(override)
        products[product] = base
    return products


def contract_month(symbol: str, now: datetime) -> tuple[int, int] | None:
    match = re.search(r"(\d{2})(\d{2})$", symbol)
    if not match:
        return None
    year = 2000 + int(match.group(1))
    month = int(match.group(2))
    if not 1 <= month <= 12:
        return None
    if (year, month) < (now.year, now.month):
        return None
    return year, month


def normalized_symbol(value: Any) -> str:
    return str(value or "").upper().strip()


def row_to_contract(row: Any, product: str, spec: dict[str, Any], now: datetime) -> tuple[dict[str, Any] | None, str | None]:
    symbol = normalized_symbol(row.get("symbol"))
    if not re.fullmatch(rf"{re.escape(product)}\d{{4}}", symbol):
        return None, None
    month = contract_month(symbol, now)
    if month is None:
        return None, f"{symbol} 已过期或月份非法，已跳过"

    volume = as_int(row.get("volume"))
    open_interest = as_int(row.get("position") if row.get("position") is not None else row.get("open_interest"))
    turnover = as_float(row.get("turnover") if row.get("turnover") is not None else row.get("amount"))
    warnings: list[str] = []

    if volume is None:
        return None, f"{symbol} 缺少成交量，已跳过"
    if volume <= 0:
        return None, f"{symbol} 成交量为0，已跳过"
    if open_interest is None:
        return None, f"{symbol} 缺少持仓量，已跳过"
    if open_interest <= 0:
        return None, f"{symbol} 持仓量为0，已跳过"
    if turnover is None:
        warnings.append("成交额字段缺失，排序已跳过成交额")

    tradedate = str(row.get("tradedate") or "").strip()
    ticktime = str(row.get("ticktime") or "").strip()
    data_time = " ".join(part for part in [tradedate, ticktime] if part) or now.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "symbol": symbol,
        "product": product,
        "product_name": str(spec.get("name") or product),
        "rank": 0,
        "label": "",
        "volume": volume,
        "open_interest": open_interest,
        "turnover": turnover,
        "data_time": data_time,
        "source": SOURCE,
        "warnings": warnings,
        "_month": month,
    }, None


def discover_product(ak: Any, product: str, spec: dict[str, Any], now: datetime) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    query = str(spec.get("query") or spec.get("name") or product)
    limit = int(spec.get("limit") or 2)
    try:
        df = ak.futures_zh_realtime(symbol=query)
    except Exception as exc:
        return [], [f"{product} 合约实时行情获取失败：{exc}"]
    if df is None or len(df) == 0:
        return [], [f"{product} 合约实时行情为空"]

    contracts: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        contract, warning = row_to_contract(row, product, spec, now)
        if warning:
            warnings.append(warning)
        if contract:
            contracts.append(contract)

    contracts.sort(
        key=lambda item: (
            -int(item["volume"]),
            -int(item["open_interest"]),
            -(float(item["turnover"]) if item["turnover"] is not None else -1.0),
            item["_month"][0],
            item["_month"][1],
        )
    )
    selected = contracts[:limit]
    for index, item in enumerate(selected, start=1):
        item["rank"] = index
        item["label"] = "主力" if index == 1 else "次主力"
        item.pop("_month", None)
    if not selected:
        warnings.append(f"{product} 未发现满足成交量和持仓量条件的合约")
    return selected, warnings


def safe_month_file(month: str) -> Path:
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError(f"月份格式非法：{month}")
    return OUTPUT_DIR / f"{month}.json"


def prune_previous_months(current_month: str) -> list[str]:
    deleted: list[str] = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    root = OUTPUT_DIR.resolve()
    for path in OUTPUT_DIR.glob("????-??.json"):
        if path.name == f"{current_month}.json":
            continue
        if not re.fullmatch(r"\d{4}-\d{2}\.json", path.name):
            continue
        resolved = path.resolve()
        if root not in resolved.parents:
            continue
        path.unlink()
        deleted.append(str(path.relative_to(ROOT)))
    return deleted


def discover(now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now()
    products_config = load_config()
    warnings: list[str] = []
    config_warning = products_config.pop("_config_warning", None)
    if config_warning:
        warnings.append(str(config_warning.get("warning")))

    try:
        ak = load_akshare()
    except RuntimeError as exc:
        return {
            "month": now.strftime("%Y-%m"),
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "source": SOURCE,
            "products": {key: [] for key in products_config},
            "warnings": [str(exc)],
        }

    products: dict[str, list[dict[str, Any]]] = {}
    for product, spec in products_config.items():
        if product.startswith("_"):
            continue
        selected, product_warnings = discover_product(ak, product, spec, now)
        products[product] = selected
        warnings.extend(product_warnings)

    return {
        "month": now.strftime("%Y-%m"),
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "source": SOURCE,
        "products": products,
        "warnings": warnings,
    }


def save(payload: dict[str, Any]) -> dict[str, Any]:
    month = str(payload.get("month") or "")
    month_file = safe_month_file(month)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    month_file.write_text(text + "\n", encoding="utf-8")
    CURRENT_OUTPUT.write_text(text + "\n", encoding="utf-8")
    deleted = prune_previous_months(month)
    return {
        "saved": [str(month_file.relative_to(ROOT)), str(CURRENT_OUTPUT.relative_to(ROOT))],
        "deleted": deleted,
        "warnings": payload.get("warnings", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-only", action="store_true", help="Print JSON without saving files.")
    parser.add_argument("--month", help="Override discovery month as YYYY-MM for tests or manual repair.")
    args = parser.parse_args()

    now = datetime.now()
    if args.month:
        if not re.fullmatch(r"\d{4}-\d{2}", args.month):
            print(json.dumps({"error": "month must be YYYY-MM"}, ensure_ascii=False), file=sys.stderr)
            return 2
        now = datetime.strptime(args.month + "-01", "%Y-%m-%d")

    payload = discover(now)
    if args.output_only:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    result = save(payload)
    print(json.dumps({**payload, "save_result": result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

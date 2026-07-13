#!/usr/bin/env python3
"""Deterministically freeze P/Y/OI rank-1 forecasts from oil_futures.js."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from forecast_schema import OUTCOME_V1_BASELINE, SCORE_MAP_VERSION, TRACKED_PRODUCTS, normalize_confidence, score_map_v1


SOURCE_SCORE_FIELDS = ("total", "technical", "fundamental", "driver", "money_flow")
OIL_FUTURES_PREFIX = re.compile(r"^\s*window\.OIL_FUTURES_CONTRACTS\s*=\s*", re.DOTALL)
PRICE_TOKEN = re.compile(r"(?<![\d.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\d.])\d+(?:\.\d+)?")


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} 必须为有限数值")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} 必须为有限数值") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} 必须为有限数值")
    return number


def parse_oil_futures(path: Path) -> dict[str, Any]:
    """Read only the window.OIL_FUTURES_CONTRACTS JavaScript assignment."""
    text = path.read_text(encoding="utf-8")
    payload_text = OIL_FUTURES_PREFIX.sub("", text, count=1).strip()
    if payload_text == text.strip():
        raise ValueError("oil futures 文件必须以 window.OIL_FUTURES_CONTRACTS = 开头")
    if payload_text.endswith(";"):
        payload_text = payload_text[:-1].rstrip()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"oil futures JSON 无法解析：{exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("contracts"), list):
        raise ValueError("oil futures 文件缺少 contracts 数组")
    return payload


def extract_invalidation_price(text: str) -> float | None:
    """Return a price only when the invalidation text contains one numeric token."""
    candidates: list[float] = []
    for match in PRICE_TOKEN.finditer(text):
        end = match.end()
        if end < len(text) and text[end] in "%日分秒小时":
            continue
        candidates.append(float(match.group().replace(",", "")))
    return candidates[0] if len(candidates) == 1 else None


def select_main_contracts(contracts: list[Any]) -> dict[str, dict[str, Any]]:
    """Select exactly one P/Y/OI record using product plus contract_rank == 1."""
    selected: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    for item in contracts:
        if not isinstance(item, dict):
            continue
        product = item.get("product")
        if product not in TRACKED_PRODUCTS or item.get("contract_rank") != 1 or isinstance(item.get("contract_rank"), bool):
            continue
        if product in selected:
            duplicates.add(product)
        selected[product] = item
    missing = TRACKED_PRODUCTS - set(selected)
    if missing:
        raise ValueError(f"缺少 rank=1 主力合约：{', '.join(sorted(missing))}")
    if duplicates:
        raise ValueError(f"存在重复 rank=1 主力合约：{', '.join(sorted(duplicates))}")
    return selected


def build_record(contract_data: dict[str, Any], report_date: str, generated_at: str, cutoff_at: str) -> dict[str, Any]:
    """Build one forecast-schema-v1 record from an already selected contract."""
    product = contract_data.get("product")
    contract = contract_data.get("contract")
    score = contract_data.get("score")
    strategy = contract_data.get("strategy_recommendation")
    if not isinstance(score, dict):
        raise ValueError(f"{product} 缺少 score 对象")
    if not isinstance(strategy, dict):
        raise ValueError(f"{product} 缺少 strategy_recommendation 对象")
    if not isinstance(contract, str) or not contract:
        raise ValueError(f"{product} contract 无效")

    source_score = {field: _finite_number(score.get(field), f"{product}.score.{field}") for field in SOURCE_SCORE_FIELDS}
    stance = score.get("stance")
    if not isinstance(stance, str) or not stance.strip():
        raise ValueError(f"{product}.score.stance 缺失")
    source_confidence = score.get("view_confidence") if isinstance(score.get("view_confidence"), str) else None
    probabilities = score_map_v1(source_score["total"], stance, source_confidence, score.get("contradiction_warning"))

    lower = _finite_number(strategy.get("lower_watch"), f"{product}.strategy_recommendation.lower_watch")
    upper = _finite_number(strategy.get("upper_watch"), f"{product}.strategy_recommendation.upper_watch")
    if lower >= upper:
        raise ValueError(f"{product} 观察区间无效：lower_watch 必须小于 upper_watch")
    invalidation_text = strategy.get("invalidation")
    if not isinstance(invalidation_text, str) or not invalidation_text.strip():
        raise ValueError(f"{product}.strategy_recommendation.invalidation 缺失")

    return {
        "forecast_id": f"{report_date}-{contract}-oil-forecast-v1",
        "report_date": report_date,
        "product": product,
        "contract": contract,
        "contract_rank": 1,
        "generated_at": generated_at,
        "cutoff_at": cutoff_at,
        "horizon": "same_trade_day_close",
        "stance": stance,
        "probabilities": probabilities,
        "expected_range": {"lower": lower, "upper": upper},
        "invalidation": {"text": invalidation_text, "price": extract_invalidation_price(invalidation_text)},
        "source_score": source_score,
        "confidence": normalize_confidence(source_confidence),
        "source_confidence": source_confidence,
        "probability_mapping_version": SCORE_MAP_VERSION,
        "outcome_rule_version": OUTCOME_V1_BASELINE,
        "calibration_status": "uncalibrated_baseline",
        "evaluation_status": "pending",
    }


def build_forecast(oil_futures: dict[str, Any], report_date: str, generated_at: str, cutoff_at: str) -> dict[str, Any]:
    selected = select_main_contracts(oil_futures["contracts"])
    return {
        "schema_version": "forecast-schema-v1",
        "report_date": report_date,
        "timezone": "Asia/Shanghai",
        "records": [build_record(selected[product], report_date, generated_at, cutoff_at) for product in ("P", "Y", "OI")],
    }


def _load_existing(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"已有预测文件无法读取：{exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("已有预测文件必须是 JSON 对象")
    records = payload.get("records")
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ValueError("已有预测文件 records 无效")
    if any(record.get("evaluation_status") != "pending" for record in records):
        raise ValueError("已有预测记录不是 pending，禁止覆盖")
    return payload


def _validate_temp_file(path: Path) -> None:
    validator = Path(__file__).with_name("validate_forecast.py")
    completed = subprocess.run(
        [sys.executable, str(validator), "--forecast", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValueError(f"临时预测文件未通过 schema 校验：{completed.stdout.strip() or completed.stderr.strip()}")


def freeze_forecast(
    oil_futures_path: Path,
    forecast_path: Path,
    report_date: str,
    generated_at: str,
    cutoff_at: str,
    quality_gate_status: str,
) -> dict[str, Any]:
    """Create one immutable daily forecast file, or confirm its exact replay."""
    if quality_gate_status != "ok":
        raise ValueError("quality-gate-status 必须为 ok；禁止写入预测文件")
    forecast = build_forecast(parse_oil_futures(oil_futures_path), report_date, generated_at, cutoff_at)

    if forecast_path.exists():
        existing = _load_existing(forecast_path)
        if existing == forecast:
            return {"status": "ok", "forecast": str(forecast_path), "already_exists": True, "records": len(forecast["records"])}
        raise ValueError("已有预测文件内容不同，冻结记录不可覆盖")

    forecast_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=forecast_path.parent, prefix=f".{forecast_path.name}.", suffix=".tmp", delete=False) as temporary:
            temp_path = Path(temporary.name)
            json.dump(forecast, temporary, ensure_ascii=False, sort_keys=True, indent=2)
            temporary.write("\n")
        _validate_temp_file(temp_path)
        os.replace(temp_path, forecast_path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return {"status": "ok", "forecast": str(forecast_path), "already_exists": False, "records": len(forecast["records"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oil-futures", required=True, type=Path)
    parser.add_argument("--forecast", required=True, type=Path)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--cutoff-at", required=True)
    parser.add_argument("--quality-gate-status", required=True)
    args = parser.parse_args()
    try:
        result = freeze_forecast(
            args.oil_futures,
            args.forecast,
            args.report_date,
            args.generated_at,
            args.cutoff_at,
            args.quality_gate_status,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "error", "already_exists": False, "errors": [str(exc)]}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

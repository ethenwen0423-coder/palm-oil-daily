#!/usr/bin/env python3
"""Evaluate pending frozen forecasts against same-contract closing snapshots."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


OUTCOME_RULE_VERSION = "outcome-v1-fixed-0.30pct"
THRESHOLD_PCT = 0.30
OIL_FUTURES_PREFIX = re.compile(r"^\s*window\.OIL_FUTURES_CONTRACTS\s*=\s*", re.DOTALL)
BULLISH_STANCES = {"偏多", "震荡偏强"}
BEARISH_STANCES = {"偏空", "震荡偏弱"}
RANGE_STANCES = {"震荡", "分歧震荡", "观望"}


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


def _parse_evaluated_at(value: str) -> None:
    if not isinstance(value, str) or not value.endswith("+08:00"):
        raise ValueError("evaluated-at 必须为带 +08:00 的 ISO-8601 时间")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("evaluated-at 必须为带 +08:00 的 ISO-8601 时间") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(hours=8):
        raise ValueError("evaluated-at 必须为带 +08:00 的 ISO-8601 时间")


def parse_oil_futures(path: Path) -> dict[str, Any]:
    """Read only a window.OIL_FUTURES_CONTRACTS JavaScript assignment."""
    text = path.read_text(encoding="utf-8")
    payload_text = OIL_FUTURES_PREFIX.sub("", text, count=1).strip()
    if payload_text == text.strip():
        raise ValueError("actual 文件必须以 window.OIL_FUTURES_CONTRACTS = 开头")
    if payload_text.endswith(";"):
        payload_text = payload_text[:-1].rstrip()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"actual JSON 无法解析：{exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("contracts"), list):
        raise ValueError("actual 文件缺少 contracts 数组")
    return payload


def _validate_forecast_file(path: Path) -> dict[str, Any]:
    validator = Path(__file__).with_name("validate_forecast.py")
    completed = subprocess.run(
        [sys.executable, str(validator), "--forecast", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValueError(f"预测文件未通过 schema 校验：{completed.stdout.strip() or completed.stderr.strip()}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"预测文件无法读取：{exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("预测文件必须为 JSON 对象")
    return payload


def actual_class(return_pct: float) -> str:
    if return_pct > THRESHOLD_PCT:
        return "up"
    if return_pct < -THRESHOLD_PCT:
        return "down"
    return "range"


def predicted_class(probabilities: dict[str, Any]) -> str:
    values = {name: _finite_number(probabilities.get(name), f"probabilities.{name}") for name in ("up", "range", "down")}
    maximum = max(values.values())
    candidates = {name for name, value in values.items() if value == maximum}
    if "range" in candidates:
        return "range"
    if "up" in candidates:
        return "up"
    return "down"


def brier_score(probabilities: dict[str, Any], outcome: str) -> float:
    value = sum((_finite_number(probabilities.get(name), f"probabilities.{name}") - (1 if name == outcome else 0)) ** 2 for name in ("up", "range", "down")) / 3
    return round(value, 6)


def _find_actual_contract(contracts: list[Any], product: str, contract: str) -> dict[str, Any]:
    matches = [
        item
        for item in contracts
        if isinstance(item, dict) and item.get("product") == product and item.get("contract") == contract
    ]
    if not matches:
        raise ValueError(f"actual 快照缺少同一合约：{product} {contract}")
    if len(matches) > 1:
        raise ValueError(f"actual 快照存在重复合约：{product} {contract}")
    return matches[0]


def _actual_values(actual: dict[str, Any], report_date: str, label: str) -> dict[str, float | str]:
    trade_date = actual.get("trade_date")
    if trade_date != report_date:
        raise ValueError(f"{label} actual.trade_date 与预测 report_date 不一致")
    close_value = actual.get("close", actual.get("price"))
    previous_value = actual.get("previous_close", actual.get("preclose"))
    previous_close = _finite_number(previous_value, f"{label}.actual.previous_close")
    if previous_close == 0:
        raise ValueError(f"{label}.actual.previous_close 不得为零")
    close = _finite_number(close_value, f"{label}.actual.close")
    high = _finite_number(actual.get("high"), f"{label}.actual.high")
    low = _finite_number(actual.get("low"), f"{label}.actual.low")
    return {"trade_date": trade_date, "previous_close": previous_close, "close": close, "high": high, "low": low}


def evaluate_invalidation(stance: str, invalidation_price: Any, low: float, high: float) -> tuple[bool | None, str]:
    if invalidation_price is None:
        return None, "not_evaluable"
    price = _finite_number(invalidation_price, "invalidation.price")
    if stance in BULLISH_STANCES:
        return low <= price, "evaluated"
    if stance in BEARISH_STANCES:
        return high >= price, "evaluated"
    if stance in RANGE_STANCES:
        return None, "direction_ambiguous"
    raise ValueError(f"不支持失效条件评估的 stance：{stance!r}")


def evaluate_record(record: dict[str, Any], actual_contract: dict[str, Any], report_date: str, evaluated_at: str) -> dict[str, Any]:
    output = copy.deepcopy(record)
    label = f"{record.get('product')} {record.get('contract')}"
    actual = _actual_values(actual_contract, report_date, label)
    return_pct = (float(actual["close"]) - float(actual["previous_close"])) / float(actual["previous_close"]) * 100
    classified_actual = actual_class(return_pct)
    probabilities = output["probabilities"]
    classified_predicted = predicted_class(probabilities)
    expected_range = output["expected_range"]
    lower = _finite_number(expected_range.get("lower"), f"{label}.expected_range.lower")
    upper = _finite_number(expected_range.get("upper"), f"{label}.expected_range.upper")
    invalidation_triggered, invalidation_status = evaluate_invalidation(
        output["stance"], output["invalidation"].get("price"), float(actual["low"]), float(actual["high"])
    )
    output["evaluation_status"] = "evaluated"
    output["evaluation"] = {
        "outcome_rule_version": OUTCOME_RULE_VERSION,
        "evaluated_at": evaluated_at,
        "actual": {
            "trade_date": actual["trade_date"],
            "previous_close": float(actual["previous_close"]),
            "close": float(actual["close"]),
            "high": float(actual["high"]),
            "low": float(actual["low"]),
            "return_pct": round(return_pct, 6),
        },
        "threshold_pct": THRESHOLD_PCT,
        "threshold_source": "fixed_baseline",
        "actual_class": classified_actual,
        "predicted_class": classified_predicted,
        "direction_hit": classified_predicted == classified_actual,
        "close_in_expected_range": lower <= float(actual["close"]) <= upper,
        "full_session_in_expected_range": lower <= float(actual["low"]) and float(actual["high"]) <= upper,
        "invalidation_triggered": invalidation_triggered,
        "invalidation_evaluation_status": invalidation_status,
        "brier_score": brier_score(probabilities, classified_actual),
    }
    return output


def build_evaluated_forecast(forecast: dict[str, Any], actual_payload: dict[str, Any], evaluated_at: str) -> dict[str, Any]:
    _parse_evaluated_at(evaluated_at)
    records = forecast.get("records")
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ValueError("预测文件 records 无效")
    if any(record.get("evaluation_status") != "pending" for record in records):
        raise ValueError("输入预测必须全部为 pending")
    report_date = forecast.get("report_date")
    if not isinstance(report_date, str):
        raise ValueError("预测文件 report_date 无效")

    contracts = actual_payload["contracts"]
    evaluated_records = [
        evaluate_record(record, _find_actual_contract(contracts, record["product"], record["contract"]), report_date, evaluated_at)
        for record in records
    ]
    output = copy.deepcopy(forecast)
    output["records"] = evaluated_records
    output["evaluation_status"] = "evaluated"
    return output


def _write_validated_atomically(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output_path.parent, prefix=f".{output_path.name}.", suffix=".tmp", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(payload, temporary, ensure_ascii=False, sort_keys=True, indent=2)
            temporary.write("\n")
        _validate_forecast_file(temporary_path)
        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def evaluate_forecast(forecast_path: Path, actual_path: Path, output_path: Path, evaluated_at: str) -> dict[str, Any]:
    """Evaluate a pending forecast without changing the original forecast file."""
    if forecast_path.resolve() == output_path.resolve():
        raise ValueError("output 不得覆盖 forecast 输入文件")
    forecast = _validate_forecast_file(forecast_path)
    output = build_evaluated_forecast(forecast, parse_oil_futures(actual_path), evaluated_at)

    if output_path.exists():
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"已有评估文件无法读取：{exc}") from exc
        if existing == output:
            return {"status": "ok", "output": str(output_path), "already_exists": True, "records": len(output["records"])}
        raise ValueError("已有评估文件内容不同，禁止覆盖")

    _write_validated_atomically(output, output_path)
    return {"status": "ok", "output": str(output_path), "already_exists": False, "records": len(output["records"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecast", required=True, type=Path)
    parser.add_argument("--actual", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--evaluated-at", required=True)
    args = parser.parse_args()
    try:
        result = evaluate_forecast(args.forecast, args.actual, args.output, args.evaluated_at)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "already_exists": False, "errors": [str(exc)]}, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

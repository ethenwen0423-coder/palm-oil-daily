#!/usr/bin/env python3
"""Schema validation for daily P/Y/OI main-contract forecast records."""

from __future__ import annotations

import math
import re
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime, timedelta, timezone
from typing import Any


SCHEMA_VERSION = "forecast-schema-v1"
SHANGHAI_TIMEZONE = "Asia/Shanghai"
TRACKED_PRODUCTS = {"P", "Y", "OI"}
ALLOWED_EVALUATION_STATUSES = {"pending", "evaluated", "invalidated"}
INITIAL_EVALUATION_STATUS = "pending"
PROBABILITY_TOLERANCE = 0.000001
CONTRACT_PATTERN = re.compile(r"^(P|Y|OI)(\d{2})(\d{2})$")
SCORE_MAP_VERSION = "score-map-v1"
CONFIDENCE_FACTORS = {"高": 0.90, "中": 0.70, "低": 0.45}
BULLISH_STANCES = {"偏多", "震荡偏强"}
BEARISH_STANCES = {"偏空", "震荡偏弱"}
RANGE_STANCES = {"震荡", "分歧震荡", "观望"}
EVALUATION_REQUIRED_FIELDS = (
    "outcome_rule_version",
    "evaluated_at",
    "actual",
    "threshold_pct",
    "threshold_source",
    "actual_class",
    "predicted_class",
    "direction_hit",
    "close_in_expected_range",
    "full_session_in_expected_range",
    "invalidation_triggered",
    "invalidation_evaluation_status",
    "brier_score",
)
EVALUATION_ACTUAL_FIELDS = ("trade_date", "previous_close", "close", "high", "low", "return_pct")
EVALUATION_CLASSES = {"up", "range", "down"}
OUTCOME_V1_BASELINE = "outcome-v1-fixed-0.30pct"
ALLOWED_CONFIDENCE_LEVELS = {"high", "medium", "low", "unknown"}


def _add_error(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def clamp(value: float, lower: float, upper: float) -> float:
    """Return value bounded inclusively by lower and upper."""
    return max(lower, min(value, upper))


def normalize_confidence(value: Any) -> str:
    """Normalize source score confidence for the persisted statistics bucket."""
    if isinstance(value, str):
        normalized = value.strip().lower()
        if value.strip() == "高" or normalized == "high":
            return "high"
        if value.strip() == "中" or normalized == "medium":
            return "medium"
        if value.strip() == "低" or normalized == "low":
            return "low"
    return "unknown"


def score_map_v1(total: float, stance: str, view_confidence: Any, contradiction_warning: Any) -> dict[str, float]:
    """Map a score and view metadata to deterministic up/range/down probabilities.

    The first two probabilities are rounded to six decimal places. The final
    ``down`` probability is calculated as ``1 - up - range`` so every emitted
    record totals exactly one in decimal arithmetic.
    """
    if not _is_finite_number(total):
        raise ValueError("score.total 必须为有限数值")
    if stance not in BULLISH_STANCES | BEARISH_STANCES | RANGE_STANCES:
        raise ValueError(f"score.stance 不支持：{stance!r}")

    score_edge = clamp((float(total) - 50) / 25, -1, 1)
    strength = abs(score_edge)
    confidence_factor = CONFIDENCE_FACTORS.get(view_confidence, 0.40)
    has_conflict = isinstance(contradiction_warning, str) and contradiction_warning.strip() and contradiction_warning.strip() != "暂无明显冲突信号"
    conflict_penalty = 0.15 if has_conflict else 0.0
    directional_mass = clamp(0.20 + 0.55 * strength * confidence_factor - conflict_penalty, 0.20, 0.70)

    if stance in BULLISH_STANCES:
        up = directional_mass * (0.5 + 0.5 * strength)
        down = directional_mass - up
        range_probability = 1 - directional_mass
    elif stance in BEARISH_STANCES:
        down = directional_mass * (0.5 + 0.5 * strength)
        up = directional_mass - down
        range_probability = 1 - directional_mass
    else:
        range_probability = max(0.55, 1 - directional_mass)
        up = (1 - range_probability) / 2
        down = (1 - range_probability) / 2

    quantizer = Decimal("0.000001")
    rounded_up = Decimal(str(up)).quantize(quantizer, rounding=ROUND_HALF_UP)
    rounded_range = Decimal(str(range_probability)).quantize(quantizer, rounding=ROUND_HALF_UP)
    rounded_down = Decimal("1") - rounded_up - rounded_range
    return {"up": float(rounded_up), "range": float(rounded_range), "down": float(rounded_down)}


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _parse_shanghai_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("+08:00"):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(hours=8):
        return None
    return parsed


def _valid_contract(product: Any, contract: Any) -> bool:
    if not isinstance(product, str) or product not in TRACKED_PRODUCTS:
        return False
    if not isinstance(contract, str):
        return False
    match = CONTRACT_PATTERN.fullmatch(contract)
    return bool(match and match.group(1) == product and 1 <= int(match.group(3)) <= 12)


def _require_nonempty_string(record: dict[str, Any], field: str, label: str, errors: list[str]) -> None:
    if not isinstance(record.get(field), str) or not record[field].strip():
        _add_error(errors, f"{label} 缺少有效 {field}")


def _validate_probabilities(record: dict[str, Any], label: str, errors: list[str]) -> None:
    probabilities = record.get("probabilities")
    if not isinstance(probabilities, dict):
        _add_error(errors, f"{label} probabilities 必须为对象")
        return
    values: list[float] = []
    for direction in ("up", "range", "down"):
        value = probabilities.get(direction)
        if not _is_finite_number(value) or not 0 <= float(value) <= 1:
            _add_error(errors, f"{label} probabilities.{direction} 必须为 0 到 1 的数值")
        else:
            values.append(float(value))
    if len(values) == 3 and abs(sum(values) - 1) > PROBABILITY_TOLERANCE:
        _add_error(errors, f"{label} probabilities 合计必须为 1")


def _validate_range(record: dict[str, Any], label: str, errors: list[str]) -> None:
    expected_range = record.get("expected_range")
    if not isinstance(expected_range, dict):
        _add_error(errors, f"{label} expected_range 必须为对象")
        return
    lower = expected_range.get("lower")
    upper = expected_range.get("upper")
    if not _is_finite_number(lower) or not _is_finite_number(upper):
        _add_error(errors, f"{label} expected_range.upper/lower 必须为有限数值")
    elif float(lower) >= float(upper):
        _add_error(errors, f"{label} expected_range.lower 必须小于 upper")


def _validate_timing(record: dict[str, Any], label: str, errors: list[str]) -> None:
    generated_at = _parse_shanghai_timestamp(record.get("generated_at"))
    cutoff_at = _parse_shanghai_timestamp(record.get("cutoff_at"))
    if generated_at is None:
        _add_error(errors, f"{label} generated_at 必须为带 +08:00 的 ISO-8601 时间")
    if cutoff_at is None:
        _add_error(errors, f"{label} cutoff_at 必须为带 +08:00 的 ISO-8601 时间")
    if generated_at is not None and cutoff_at is not None and generated_at > cutoff_at + timedelta(minutes=5):
        _add_error(errors, f"{label} generated_at 不得晚于 cutoff_at 后 5 分钟")


def _validate_evaluation(record: dict[str, Any], report_date: Any, label: str, errors: list[str]) -> None:
    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        _add_error(errors, f"{label} evaluated 记录缺少 evaluation 对象")
        return
    for field in EVALUATION_REQUIRED_FIELDS:
        if field not in evaluation:
            _add_error(errors, f"{label} evaluation 缺少 {field}")

    evaluation_rule = evaluation.get("outcome_rule_version")
    record_rule = record.get("outcome_rule_version")
    if not isinstance(evaluation_rule, str) or not evaluation_rule or evaluation_rule != record_rule:
        _add_error(errors, f"{label} evaluation.outcome_rule_version 必须与 outcome_rule_version 一致")
    if _parse_shanghai_timestamp(evaluation.get("evaluated_at")) is None:
        _add_error(errors, f"{label} evaluation.evaluated_at 必须为带 +08:00 的 ISO-8601 时间")

    actual = evaluation.get("actual")
    if not isinstance(actual, dict):
        _add_error(errors, f"{label} evaluation.actual 必须为对象")
    else:
        if actual.get("trade_date") != report_date:
            _add_error(errors, f"{label} evaluation.actual.trade_date 必须等于 report_date")
        for field in EVALUATION_ACTUAL_FIELDS[1:]:
            if not _is_finite_number(actual.get(field)):
                _add_error(errors, f"{label} evaluation.actual.{field} 必须为有限数值")

    if not _is_finite_number(evaluation.get("threshold_pct")):
        _add_error(errors, f"{label} evaluation.threshold_pct 必须为有限数值")
    if not isinstance(evaluation.get("threshold_source"), str) or not evaluation["threshold_source"].strip():
        _add_error(errors, f"{label} evaluation.threshold_source 必须为非空文本")
    for field in ("actual_class", "predicted_class"):
        if evaluation.get(field) not in EVALUATION_CLASSES:
            _add_error(errors, f"{label} evaluation.{field} 只能为 up/range/down")
    for field in ("direction_hit", "close_in_expected_range", "full_session_in_expected_range"):
        if not isinstance(evaluation.get(field), bool):
            _add_error(errors, f"{label} evaluation.{field} 必须为布尔值")
    if evaluation.get("invalidation_triggered") is not None and not isinstance(evaluation.get("invalidation_triggered"), bool):
        _add_error(errors, f"{label} evaluation.invalidation_triggered 必须为布尔值或 null")
    if not isinstance(evaluation.get("invalidation_evaluation_status"), str) or not evaluation["invalidation_evaluation_status"].strip():
        _add_error(errors, f"{label} evaluation.invalidation_evaluation_status 必须为非空文本")
    brier_score = evaluation.get("brier_score")
    if not _is_finite_number(brier_score) or not 0 <= float(brier_score) <= 1:
        _add_error(errors, f"{label} evaluation.brier_score 必须为 0 到 1 的数值")


def _validate_record(record: Any, report_date: Any, errors: list[str], require_pending: bool) -> str | None:
    if not isinstance(record, dict):
        _add_error(errors, "records 中每项必须为对象")
        return None

    product = record.get("product")
    label = f"记录 {product!r}"
    if record.get("report_date") != report_date or not _valid_date(record.get("report_date")):
        _add_error(errors, f"{label} report_date 必须与文件 report_date 一致且有效")
    if not _valid_contract(product, record.get("contract")):
        _add_error(errors, f"{label} product 或 contract 格式无效")
    if record.get("contract_rank") != 1 or isinstance(record.get("contract_rank"), bool):
        _add_error(errors, f"{label} contract_rank 必须为 1；rank=2 或其他排名不允许")

    for field in (
        "forecast_id",
        "horizon",
        "stance",
        "probability_mapping_version",
        "outcome_rule_version",
        "calibration_status",
    ):
        _require_nonempty_string(record, field, label, errors)

    outcome_rule_version = record.get("outcome_rule_version")
    if outcome_rule_version == "outcome-v1":
        _add_error(errors, f"{label} legacy outcome rule version requires explicit migration")
    elif outcome_rule_version != OUTCOME_V1_BASELINE:
        _add_error(errors, f"{label} outcome_rule_version 必须为 {OUTCOME_V1_BASELINE}")

    confidence = record.get("confidence")
    if confidence not in ALLOWED_CONFIDENCE_LEVELS:
        _add_error(errors, f"{label} confidence 只能为 high/medium/low/unknown")
    source_confidence = record.get("source_confidence")
    if source_confidence is not None and not isinstance(source_confidence, str):
        _add_error(errors, f"{label} source_confidence 必须为字符串或 null")

    invalidation = record.get("invalidation")
    if not isinstance(invalidation, dict) or not isinstance(invalidation.get("text"), str) or not invalidation["text"].strip():
        _add_error(errors, f"{label} invalidation.text 必须为非空文本")
    elif invalidation.get("price") is not None and not _is_finite_number(invalidation["price"]):
        _add_error(errors, f"{label} invalidation.price 必须为数值或 null")

    source_score = record.get("source_score")
    if not isinstance(source_score, dict):
        _add_error(errors, f"{label} source_score 必须为对象")
    else:
        for field in ("total", "technical", "fundamental", "driver", "money_flow"):
            if not _is_finite_number(source_score.get(field)):
                _add_error(errors, f"{label} source_score.{field} 必须为有限数值")

    _validate_probabilities(record, label, errors)
    _validate_range(record, label, errors)
    _validate_timing(record, label, errors)

    evaluation_status = record.get("evaluation_status")
    if evaluation_status not in ALLOWED_EVALUATION_STATUSES:
        _add_error(errors, f"{label} evaluation_status 未知")
    elif require_pending and evaluation_status != INITIAL_EVALUATION_STATUS:
        _add_error(errors, f"{label} 初始 evaluation_status 只能为 pending")
    elif evaluation_status == "evaluated":
        _validate_evaluation(record, report_date, label, errors)
    elif evaluation_status == "pending":
        evaluation = record.get("evaluation")
        if isinstance(evaluation, dict) and all(field in evaluation for field in EVALUATION_REQUIRED_FIELDS):
            _add_error(errors, f"{label} pending 记录不得包含完整 evaluation 结果")
    return record.get("forecast_id") if isinstance(record.get("forecast_id"), str) else None


def validate_forecast(payload: Any, require_pending: bool = False) -> dict[str, Any]:
    """Validate a forecast-schema-v1 payload and return machine-readable issues.

    Set ``require_pending`` only at the forecast-creation boundary. Generic
    schema validation permits known later lifecycle states for a future outcome
    evaluator while continuing to reject unknown values.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        return {"status": "error", "can_evaluate": False, "errors": ["顶层必须为 JSON 对象"], "warnings": warnings}

    if payload.get("schema_version") != SCHEMA_VERSION:
        _add_error(errors, f"schema_version 必须为 {SCHEMA_VERSION}")
    report_date = payload.get("report_date")
    if not _valid_date(report_date):
        _add_error(errors, "report_date 必须为有效 YYYY-MM-DD 日期")
    if payload.get("timezone") != SHANGHAI_TIMEZONE:
        _add_error(errors, f"timezone 必须为 {SHANGHAI_TIMEZONE}")

    records = payload.get("records")
    if not isinstance(records, list):
        _add_error(errors, "records 必须为数组")
        records = []
    elif len(records) != len(TRACKED_PRODUCTS):
        _add_error(errors, "records 必须恰好包含 P、Y、OI 各一条")

    products: list[str] = []
    forecast_ids: list[str] = []
    for record in records:
        forecast_id = _validate_record(record, report_date, errors, require_pending)
        if isinstance(record, dict) and isinstance(record.get("product"), str):
            products.append(record["product"])
        if forecast_id is not None:
            forecast_ids.append(forecast_id)

    if set(products) != TRACKED_PRODUCTS or len(products) != len(TRACKED_PRODUCTS):
        _add_error(errors, "records 必须恰好包含 P、Y、OI 各一条主力记录")
    if len(set(forecast_ids)) != len(forecast_ids):
        _add_error(errors, "forecast_id 在单日文件内不可重复")

    return {"status": "ok" if not errors else "error", "can_evaluate": not errors, "errors": errors, "warnings": warnings}

#!/usr/bin/env python3
"""Build version-isolated rolling metrics from evaluated forecast files."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from forecast_schema import TRACKED_PRODUCTS, validate_forecast


METRICS_SCHEMA_VERSION = "forecast-metrics-v1"
CONFIDENCE_BUCKETS = ("high", "medium", "low", "unknown")


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _version_key(probability_mapping_version: str, outcome_rule_version: str) -> str:
    return f"{probability_mapping_version}|{outcome_rule_version}"


def _confidence_bucket(record: dict[str, Any]) -> str:
    value = record.get("confidence")
    return value if value in CONFIDENCE_BUCKETS else "unknown"


def _valid_evaluated_day(payload: dict[str, Any], path: Path, as_of: date) -> tuple[str, str, str, list[dict[str, Any]]] | None:
    validation = validate_forecast(payload)
    if validation["status"] != "ok":
        return None
    report_date = payload.get("report_date")
    parsed_date = _parse_date(report_date)
    if parsed_date is None or parsed_date > as_of or path.stem != report_date:
        return None
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != len(TRACKED_PRODUCTS):
        return None
    if {record.get("product") for record in records if isinstance(record, dict)} != TRACKED_PRODUCTS:
        return None
    if any(record.get("evaluation_status") != "evaluated" for record in records):
        return None
    probability_versions = {record.get("probability_mapping_version") for record in records}
    outcome_versions = {record.get("outcome_rule_version") for record in records}
    if len(probability_versions) != 1 or len(outcome_versions) != 1:
        return None
    probability_version = next(iter(probability_versions))
    outcome_version = next(iter(outcome_versions))
    if not isinstance(probability_version, str) or not isinstance(outcome_version, str):
        return None
    return report_date, probability_version, outcome_version, records


def load_evaluated_days(evaluated_dir: Path, as_of: date) -> dict[str, list[tuple[str, list[dict[str, Any]]]]]:
    """Return valid whole P/Y/OI trade days, partitioned by version combination."""
    by_version: dict[str, list[tuple[str, list[dict[str, Any]]]]] = defaultdict(list)
    if not evaluated_dir.exists():
        return by_version
    for path in sorted(evaluated_dir.glob("*.json")):
        payload = _load_json(path)
        if payload is None:
            continue
        valid_day = _valid_evaluated_day(payload, path, as_of)
        if valid_day is None:
            continue
        report_date, probability_version, outcome_version, records = valid_day
        by_version[_version_key(probability_version, outcome_version)].append((report_date, records))
    for rows in by_version.values():
        rows.sort(key=lambda row: row[0])
    return by_version


def load_evaluation_gaps(forecast_dir: Path, valid_evaluated_dates: set[str], as_of: date) -> dict[str, int]:
    """Count pending frozen records lacking a valid evaluated file, by version."""
    gaps: dict[str, int] = defaultdict(int)
    if not forecast_dir.exists():
        return gaps
    for path in sorted(forecast_dir.glob("*.json")):
        payload = _load_json(path)
        if payload is None or validate_forecast(payload)["status"] != "ok":
            continue
        report_date = payload.get("report_date")
        parsed_date = _parse_date(report_date)
        if parsed_date is None or parsed_date > as_of or path.stem != report_date or report_date in valid_evaluated_dates:
            continue
        records = payload.get("records")
        if not isinstance(records, list):
            continue
        for record in records:
            if isinstance(record, dict) and record.get("evaluation_status") == "pending":
                probability_version = record.get("probability_mapping_version")
                outcome_version = record.get("outcome_rule_version")
                if isinstance(probability_version, str) and isinstance(outcome_version, str):
                    gaps[_version_key(probability_version, outcome_version)] += 1
    return gaps


def _empty_group() -> dict[str, Any]:
    return {
        "sample_count": 0,
        "directional_accuracy": {"numerator": 0, "denominator": 0, "rate": None},
        "close_range_coverage": {"numerator": 0, "denominator": 0, "rate": None},
        "full_session_range_coverage": {"numerator": 0, "denominator": 0, "rate": None},
        "invalidation_rate": {"numerator": 0, "denominator": 0, "rate": None},
        "mean_brier_score": None,
        "combined_grade": {"HIT": 0, "PARTIAL": 0, "MISS": 0},
    }


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    result = _empty_group()
    result["sample_count"] = len(records)
    brier_scores: list[float] = []
    for record in records:
        evaluation = record["evaluation"]
        brier_scores.append(float(evaluation["brier_score"]))
        for target, source in (
            ("directional_accuracy", "direction_hit"),
            ("close_range_coverage", "close_in_expected_range"),
            ("full_session_range_coverage", "full_session_in_expected_range"),
        ):
            result[target]["denominator"] += 1
            if evaluation[source]:
                result[target]["numerator"] += 1
        invalidation = evaluation["invalidation_triggered"]
        if invalidation is not None:
            result["invalidation_rate"]["denominator"] += 1
            if invalidation:
                result["invalidation_rate"]["numerator"] += 1
        direction = evaluation["direction_hit"]
        close_in_range = evaluation["close_in_expected_range"]
        grade = "HIT" if direction and close_in_range else "PARTIAL" if direction or close_in_range else "MISS"
        result["combined_grade"][grade] += 1
    for name in ("directional_accuracy", "close_range_coverage", "full_session_range_coverage", "invalidation_rate"):
        result[name]["rate"] = _rate(result[name]["numerator"], result[name]["denominator"])
    if brier_scores:
        result["mean_brier_score"] = round(sum(brier_scores) / len(brier_scores), 6)
    return result


def _version_metric(
    probability_version: str,
    outcome_version: str,
    days: list[tuple[str, list[dict[str, Any]]]],
    gap_count: int,
    required_days: int,
) -> dict[str, Any]:
    records = [record for _, day_records in days for record in day_records]
    by_product_records = {product: [record for record in records if record.get("product") == product] for product in ("P", "Y", "OI")}
    by_confidence_records = {
        bucket: [record for record in records if _confidence_bucket(record) == bucket]
        for bucket in CONFIDENCE_BUCKETS
    }
    valid_days = len(days)
    status = "ok" if valid_days >= required_days else "insufficient_sample"
    return {
        "status": status,
        "public_display_allowed": status == "ok",
        "valid_trade_day_count": valid_days,
        "evaluated_forecast_count": len(records),
        "evaluation_gap_count": gap_count,
        "start_date": days[0][0] if days else None,
        "end_date": days[-1][0] if days else None,
        "probability_mapping_version": probability_version,
        "outcome_rule_version": outcome_version,
        "overall": _summarize(records),
        "by_product": {product: _summarize(product_records) for product, product_records in by_product_records.items()},
        "by_confidence": {bucket: _summarize(bucket_records) for bucket, bucket_records in by_confidence_records.items()},
    }


def _split_version_key(key: str) -> tuple[str, str]:
    return key.split("|", 1)


def _build_output(
    as_of: str,
    by_version: dict[str, list[tuple[str, list[dict[str, Any]]]]],
    gaps: dict[str, int],
    window_days: int | None,
) -> dict[str, Any]:
    required_days = window_days or 20
    version_keys = sorted(set(by_version) | set(gaps))
    versions: dict[str, Any] = {}
    for key in version_keys:
        probability_version, outcome_version = _split_version_key(key)
        days = by_version.get(key, [])
        selected_days = days[-window_days:] if window_days is not None else days
        versions[key] = _version_metric(probability_version, outcome_version, selected_days, gaps.get(key, 0), required_days)

    statuses = [metric["status"] for metric in versions.values()]
    latest_key = max((key for key, days in by_version.items() if days), key=lambda key: (by_version[key][-1][0], key), default=None)
    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "as_of": as_of,
        "window_trade_days": window_days,
        "status": "ok" if statuses and all(status == "ok" for status in statuses) else "insufficient_sample",
        "public_display_allowed": bool(statuses) and all(metric["public_display_allowed"] for metric in versions.values()),
        "latest_version_combination": (
            {
                "key": latest_key,
                "probability_mapping_version": versions[latest_key]["probability_mapping_version"],
                "outcome_rule_version": versions[latest_key]["outcome_rule_version"],
            }
            if latest_key is not None
            else None
        ),
        "versions": versions,
    }


def _write_json_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(payload, temporary, ensure_ascii=False, sort_keys=True, indent=2)
            temporary.write("\n")
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def build_metrics(evaluated_dir: Path, forecast_dir: Path, output_dir: Path, as_of: str | None = None) -> dict[str, Any]:
    resolved_as_of = as_of or datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    parsed_as_of = _parse_date(resolved_as_of)
    if parsed_as_of is None:
        raise ValueError("as-of 必须为有效 YYYY-MM-DD 日期")
    by_version = load_evaluated_days(evaluated_dir, parsed_as_of)
    valid_evaluated_dates = {report_date for days in by_version.values() for report_date, _ in days}
    gaps = load_evaluation_gaps(forecast_dir, valid_evaluated_dates, parsed_as_of)
    outputs = {
        "latest.json": _build_output(resolved_as_of, by_version, gaps, None),
        "20d.json": _build_output(resolved_as_of, by_version, gaps, 20),
        "60d.json": _build_output(resolved_as_of, by_version, gaps, 60),
    }
    for filename, payload in outputs.items():
        _write_json_atomically(output_dir / filename, payload)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated-dir", required=True, type=Path)
    parser.add_argument("--forecast-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--as-of")
    args = parser.parse_args()
    try:
        outputs = build_metrics(args.evaluated_dir, args.forecast_dir, args.output_dir, args.as_of)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "errors": [str(exc)]}, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps({"status": "ok", "outputs": sorted(outputs)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

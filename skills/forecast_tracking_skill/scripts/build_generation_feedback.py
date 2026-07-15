#!/usr/bin/env python3
"""Turn evaluated forecast metrics and daily reviews into safe generation constraints."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "forecast-generation-feedback-v1"
PRODUCTS = ("P", "Y", "OI")
MIN_ACTIVE_DAYS = 5
CONFIDENCE_STARS = {"low": 2, "medium": 3, "uncapped": 5}


def _load_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _latest_metric(metrics: dict[str, Any] | None) -> tuple[str | None, dict[str, Any] | None]:
    if not metrics:
        return None, None
    latest = metrics.get("latest_version_combination")
    versions = metrics.get("versions")
    key = latest.get("key") if isinstance(latest, dict) else None
    if not isinstance(key, str) or not isinstance(versions, dict):
        return None, None
    value = versions.get(key)
    return (key, value) if isinstance(value, dict) else (None, None)


def _rate(group: dict[str, Any], name: str) -> float | None:
    value = group.get(name)
    rate = value.get("rate") if isinstance(value, dict) else None
    return float(rate) if isinstance(rate, (int, float)) and not isinstance(rate, bool) else None


def _recent_error_streaks(review_dir: Path, as_of: date) -> dict[str, int]:
    rows: list[tuple[date, set[str]]] = []
    for path in review_dir.glob("*.json") if review_dir.exists() else ():
        try:
            business_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if business_date > as_of:
            continue
        payload = _load_object(path)
        if payload is None:
            continue
        errors: set[str] = set()
        for item in payload.get("error_type", []):
            if isinstance(item, str) and item:
                errors.add(item)
        for note in payload.get("learning_notes", []):
            if not isinstance(note, dict):
                continue
            value = note.get("error_type")
            if isinstance(value, str) and value:
                errors.add(value)
            elif isinstance(value, list):
                errors.update(item for item in value if isinstance(item, str) and item)
        rows.append((business_date, errors))
    rows.sort(reverse=True)
    if not rows:
        return {}
    candidates = Counter(error for _, errors in rows for error in errors)
    streaks: dict[str, int] = {}
    for error in candidates:
        streak = 0
        for _, errors in rows:
            if error not in errors:
                break
            streak += 1
        if streak:
            streaks[error] = streak
    return dict(sorted(streaks.items()))


def _product_policy(product: str, group: dict[str, Any], active: bool) -> dict[str, Any]:
    sample_count = int(group.get("sample_count") or 0)
    directional_accuracy = _rate(group, "directional_accuracy")
    range_coverage = _rate(group, "close_range_coverage")
    grades = group.get("combined_grade") if isinstance(group.get("combined_grade"), dict) else {}
    miss_count = int(grades.get("MISS") or 0)
    miss_rate = round(miss_count / sample_count, 6) if sample_count else None
    action = "observe_only"
    cap = "uncapped"
    reasons: list[str] = []
    if active and sample_count >= MIN_ACTIVE_DAYS and directional_accuracy is not None:
        if directional_accuracy < 0.45:
            action, cap = "downgrade_directional_claim", "low"
            reasons.append("方向命中率低于45%")
        elif directional_accuracy < 0.55:
            action, cap = "cap_confidence", "medium"
            reasons.append("方向命中率低于55%")
        else:
            action = "normal"
        if range_coverage is not None and range_coverage < 0.45:
            action = "widen_scenarios" if action == "normal" else action
            reasons.append("收盘区间覆盖率低于45%")
    return {
        "product": product,
        "sample_count": sample_count,
        "directional_accuracy": directional_accuracy,
        "close_range_coverage": range_coverage,
        "miss_rate": miss_rate,
        "action": action,
        "max_confidence": cap,
        "max_confidence_stars": CONFIDENCE_STARS[cap],
        "reasons": reasons,
    }


def build_feedback(metrics_path: Path, review_dir: Path, as_of_text: str) -> dict[str, Any]:
    as_of = date.fromisoformat(as_of_text)
    metrics = _load_object(metrics_path)
    version_key, version = _latest_metric(metrics)
    valid_days = int(version.get("valid_trade_day_count") or 0) if version else 0
    active = valid_days >= MIN_ACTIVE_DAYS
    status = "active" if active else "observe_only" if valid_days else "no_history"
    by_product = version.get("by_product") if version and isinstance(version.get("by_product"), dict) else {}
    products = {
        product: _product_policy(product, by_product.get(product, {}) if isinstance(by_product.get(product), dict) else {}, active)
        for product in PRODUCTS
    }

    high_group = version.get("by_confidence", {}).get("high", {}) if version else {}
    high_samples = int(high_group.get("sample_count") or 0) if isinstance(high_group, dict) else 0
    high_accuracy = _rate(high_group, "directional_accuracy") if isinstance(high_group, dict) else None
    global_cap = "uncapped"
    if active and high_samples >= MIN_ACTIVE_DAYS and high_accuracy is not None and high_accuracy < 0.55:
        global_cap = "medium"
    p_cap = products["P"]["max_confidence"]
    if CONFIDENCE_STARS[p_cap] < CONFIDENCE_STARS[global_cap]:
        global_cap = p_cap

    streaks = _recent_error_streaks(review_dir, as_of)
    repeated = [name for name, count in streaks.items() if count >= 2]
    human_approval_required = any(count >= 4 for count in streaks.values())
    disclosures: list[str] = []
    if status == "no_history":
        disclosures.append("预测校准：暂无已评估历史样本，不据此调整今日方向。")
    elif status == "observe_only":
        disclosures.append(f"预测校准：当前仅有{valid_days}个有效交易日样本，样本不足，仅作观察，不据此调整今日方向。")
    else:
        for product, policy in products.items():
            rate = policy["directional_accuracy"]
            percentage = "暂无" if rate is None else f"{rate * 100:.1f}%"
            if policy["action"] == "downgrade_directional_claim":
                disclosures.append(f"预测校准：{product}近{valid_days}个交易日方向命中率{percentage}，今日主线降级，核心置信度不高于★★☆☆☆。")
            elif policy["action"] == "cap_confidence":
                disclosures.append(f"预测校准：{product}近{valid_days}个交易日方向命中率{percentage}，今日置信度不高于★★★☆☆。")
            elif policy["action"] == "widen_scenarios":
                disclosures.append(f"预测校准：{product}近期区间覆盖偏低，今日必须补充区间外情景及失效条件。")
        for error in repeated:
            disclosures.append(f"复盘约束：近期连续出现“{error}”，今日不得让该因素单独主导结论。")
        if not disclosures:
            disclosures.append(f"预测校准：近{valid_days}个有效交易日未触发降级门槛，今日仍按新数据独立判断，不因历史命中率上调置信度。")

    return {
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of_text,
        "metrics_as_of": metrics.get("as_of") if metrics else None,
        "status": status,
        "source_metrics": f"data/forecast/metrics/{metrics_path.name}",
        "version_key": version_key,
        "valid_trade_day_count": valid_days,
        "minimum_active_trade_days": MIN_ACTIVE_DAYS,
        "products": products,
        "high_confidence_history": {"sample_count": high_samples, "directional_accuracy": high_accuracy},
        "core_view_confidence_cap": global_cap,
        "core_view_confidence_cap_stars": CONFIDENCE_STARS[global_cap],
        "consecutive_error_streaks": streaks,
        "human_approval_required": human_approval_required,
        "generation_rules": [
            "历史结果只能降低或限制今日置信度，不能替代今日行情，也不能自动提高置信度。",
            "低命中率品种不得单独成为今日主线；必须写明反向情景和失效条件。",
            "不得自动修改永久评分权重、概率映射或策略参数。",
        ],
        "required_report_disclosures": disclosures,
    }


def _write_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary_path = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--review-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    try:
        payload = build_feedback(args.metrics, args.review_dir, args.as_of)
        _write_atomically(args.output, payload)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "errors": [str(exc)]}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", "output": str(args.output), "feedback_status": payload["status"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Plan or apply retention for forecast-review artifacts in fixed allowlisted directories."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from forecast_schema import validate_forecast


EVALUATED_LIMIT = 65
REVIEW_LIMIT = 30
FROZEN_RETENTION_DAYS = 5
RUNTIME_RETENTION_DAYS = 7
RUNTIME_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(?:previous|actual)-oil_futures\.js$")


def _date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(path for path in directory.iterdir() if path.name != ".gitkeep")


def _warning(path: Path, reason: str) -> str:
    return f"保留未识别文件 {path}: {reason}"


def _evaluated_files(directory: Path, warnings: list[str]) -> list[tuple[date, Path]]:
    valid: list[tuple[date, Path]] = []
    for path in _files(directory):
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            warnings.append(_warning(path, "不是直接JSON文件"))
            continue
        payload = _json(path)
        report_date = _date(payload.get("report_date") if payload else None)
        if payload is None:
            warnings.append(_warning(path, "JSON无效"))
        elif report_date is None or path.stem != report_date.isoformat():
            warnings.append(_warning(path, "report_date缺失、无效或与文件名不一致"))
        elif validate_forecast(payload)["status"] != "ok" or any(
            not isinstance(record, dict) or record.get("evaluation_status") != "evaluated"
            for record in payload.get("records", [])
        ):
            warnings.append(_warning(path, "不是有效的已评估forecast-schema-v1文件"))
        else:
            valid.append((report_date, path))
    return sorted(valid, key=lambda item: (item[0], item[1].name))


def _review_files(directory: Path, warnings: list[str]) -> list[tuple[date, Path]]:
    valid: list[tuple[date, Path]] = []
    for path in _files(directory):
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            warnings.append(_warning(path, "不是直接JSON文件"))
            continue
        payload = _json(path)
        review_date = _date(payload.get("date") if payload else None)
        if payload is None:
            warnings.append(_warning(path, "JSON无效"))
        elif review_date is None or path.stem != review_date.isoformat():
            warnings.append(_warning(path, "date缺失、无效或与文件名不一致"))
        else:
            valid.append((review_date, path))
    return sorted(valid, key=lambda item: (item[0], item[1].name))


def _frozen_files(
    directory: Path,
    evaluated_dates: set[date],
    as_of: date,
    warnings: list[str],
) -> tuple[list[Path], int]:
    remove: list[Path] = []
    recognized = 0
    for path in _files(directory):
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            warnings.append(_warning(path, "不是直接JSON文件"))
            continue
        payload = _json(path)
        report_date = _date(payload.get("report_date") if payload else None)
        if payload is None:
            warnings.append(_warning(path, "JSON无效"))
        elif report_date is None or path.stem != report_date.isoformat():
            warnings.append(_warning(path, "report_date缺失、无效或与文件名不一致"))
        elif validate_forecast(payload)["status"] != "ok" or any(
            not isinstance(record, dict) or record.get("evaluation_status") != "pending"
            for record in payload.get("records", [])
        ):
            warnings.append(_warning(path, "不是有效的pending冻结预测"))
        else:
            recognized += 1
            if report_date in evaluated_dates and (as_of - report_date).days > FROZEN_RETENTION_DAYS:
                remove.append(path)
    return sorted(remove), recognized


def _runtime_files(directory: Path, as_of: date, warnings: list[str]) -> tuple[list[Path], int]:
    remove: list[Path] = []
    recognized = 0
    oldest_retained = as_of - timedelta(days=RUNTIME_RETENTION_DAYS - 1)
    for path in _files(directory):
        if path.is_symlink() or not path.is_file():
            warnings.append(_warning(path, "不是直接文件"))
            continue
        match = RUNTIME_PATTERN.fullmatch(path.name)
        snapshot_date = _date(match.group(1)) if match else None
        if snapshot_date is None:
            warnings.append(_warning(path, "文件名不符合运行时快照日期格式"))
            continue
        recognized += 1
        if snapshot_date < oldest_retained:
            remove.append(path)
    return sorted(remove), recognized


def build_prune_plan(
    forecast_daily_dir: Path,
    evaluated_dir: Path,
    review_daily_dir: Path,
    runtime_snapshot_dir: Path,
    as_of: date | None = None,
) -> dict[str, Any]:
    resolved_as_of = as_of or datetime.now(ZoneInfo("Asia/Shanghai")).date()
    warnings: list[str] = []
    evaluated = _evaluated_files(evaluated_dir, warnings)
    reviews = _review_files(review_daily_dir, warnings)
    evaluated_remove = [path for _, path in evaluated[: max(0, len(evaluated) - EVALUATED_LIMIT)]]
    review_remove = [path for _, path in reviews[: max(0, len(reviews) - REVIEW_LIMIT)]]
    frozen_remove, frozen_count = _frozen_files(
        forecast_daily_dir, {business_date for business_date, _ in evaluated}, resolved_as_of, warnings
    )
    runtime_remove, runtime_count = _runtime_files(runtime_snapshot_dir, resolved_as_of, warnings)
    return {
        "status": "ok",
        "as_of": resolved_as_of.isoformat(),
        "evaluated_files_to_remove": [str(path) for path in evaluated_remove],
        "review_files_to_remove": [str(path) for path in review_remove],
        "frozen_forecast_files_to_remove": [str(path) for path in frozen_remove],
        "runtime_snapshots_to_remove": [str(path) for path in runtime_remove],
        "retained_counts": {
            "evaluated_files": len(evaluated) - len(evaluated_remove),
            "review_files": len(reviews) - len(review_remove),
            "frozen_forecast_files": frozen_count - len(frozen_remove),
            "runtime_snapshots": runtime_count - len(runtime_remove),
        },
        "warnings": warnings,
    }


def _safe_direct_child(path: Path, allowed_directory: Path) -> bool:
    try:
        return path.parent.resolve() == allowed_directory.resolve() and path.resolve().parent == allowed_directory.resolve()
    except OSError:
        return False


def apply_prune_plan(
    plan: dict[str, Any],
    forecast_daily_dir: Path,
    evaluated_dir: Path,
    review_daily_dir: Path,
    runtime_snapshot_dir: Path,
) -> list[str]:
    groups = {
        "evaluated_files_to_remove": evaluated_dir,
        "review_files_to_remove": review_daily_dir,
        "frozen_forecast_files_to_remove": forecast_daily_dir,
        "runtime_snapshots_to_remove": runtime_snapshot_dir,
    }
    errors: list[str] = []
    for key, allowed_directory in groups.items():
        for raw_path in plan.get(key, []):
            path = Path(raw_path)
            if not _safe_direct_child(path, allowed_directory):
                errors.append(f"拒绝删除白名单目录外路径：{path}")
                continue
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                errors.append(f"删除失败 {path}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecast-daily-dir", required=True, type=Path)
    parser.add_argument("--evaluated-dir", required=True, type=Path)
    parser.add_argument("--review-daily-dir", required=True, type=Path)
    parser.add_argument("--runtime-snapshot-dir", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    plan = build_prune_plan(
        args.forecast_daily_dir,
        args.evaluated_dir,
        args.review_daily_dir,
        args.runtime_snapshot_dir,
    )
    plan["mode"] = "dry-run" if args.dry_run else "apply"
    plan["applied"] = False
    if args.apply:
        errors = apply_prune_plan(
            plan,
            args.forecast_daily_dir,
            args.evaluated_dir,
            args.review_daily_dir,
            args.runtime_snapshot_dir,
        )
        plan["applied"] = True
        if errors:
            plan["status"] = "error"
            plan["errors"] = errors
    print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
    return 0 if plan["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

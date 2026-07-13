#!/usr/bin/env python3
"""Run the deterministic after-close review, forecast evaluation, and metrics chain."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SHANGHAI = ZoneInfo("Asia/Shanghai")
OFFICIAL_TAB = ROOT / "data" / "oil_futures.js"
SNAPSHOT_DIR = ROOT / "data" / "review" / "runtime_snapshots"
DAILY_REVIEW_DIR = ROOT / "data" / "review" / "daily"
FORECAST_DIR = ROOT / "data" / "forecast" / "daily"
EVALUATED_DIR = ROOT / "data" / "forecast" / "evaluated"
METRICS_DIR = ROOT / "data" / "forecast" / "metrics"
LATEST_REVIEW = ROOT / "data" / "review" / "latest_review.json"
UPDATE_SCRIPT = ROOT / "scripts" / "update_oil_futures_data.py"
REVIEW_SCRIPT = ROOT / "skills" / "daily_review_skill" / "scripts" / "daily_review.py"
EVALUATE_SCRIPT = ROOT / "skills" / "forecast_tracking_skill" / "scripts" / "evaluate_forecast.py"
METRICS_SCRIPT = ROOT / "skills" / "forecast_tracking_skill" / "scripts" / "build_metrics.py"
PRUNE_SCRIPT = ROOT / "skills" / "forecast_tracking_skill" / "scripts" / "prune_forecast_artifacts.py"
TRACKED_PRODUCTS = {"P", "Y", "OI"}
OIL_FUTURES_PREFIX = re.compile(r"^\s*window\.OIL_FUTURES_CONTRACTS\s*=\s*", re.DOTALL)


class StageFailure(RuntimeError):
    def __init__(self, stage: str, reason: str):
        super().__init__(reason)
        self.stage = stage
        self.reason = reason


def today_string(override: str | None = None) -> str:
    return override or datetime.now(SHANGHAI).strftime("%Y-%m-%d")


def is_trading_day(date_text: str) -> bool:
    """Preserve the existing weekday-based China futures-day skip behavior."""
    return datetime.strptime(date_text, "%Y-%m-%d").weekday() < 5


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def run_stage(command: list[str], stage: str) -> subprocess.CompletedProcess[str]:
    try:
        return run_command(command)
    except (OSError, subprocess.SubprocessError) as exc:
        raise StageFailure(stage, f"子进程执行失败：{exc}") from exc


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _command_reason(result: subprocess.CompletedProcess[str], fallback: str) -> str:
    return result.stderr.strip() or result.stdout.strip() or fallback


def _parse_json_output(result: subprocess.CompletedProcess[str], stage: str) -> dict[str, Any]:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise StageFailure(stage, f"子进程返回非JSON输出：{result.stdout.strip() or result.stderr.strip()}") from exc
    if not isinstance(payload, dict):
        raise StageFailure(stage, "子进程JSON输出必须为对象")
    return payload


def _write_text_atomically(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(text)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def archive_morning_tab(target: Path) -> None:
    if not OFFICIAL_TAB.exists() or OFFICIAL_TAB.stat().st_size == 0:
        raise StageFailure("actual_snapshot", "缺少 data/oil_futures.js，无法归档晨报判断")
    _write_text_atomically(target, OFFICIAL_TAB.read_text(encoding="utf-8"))


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        number = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return False
    return number == number and number not in (float("inf"), float("-inf"))


def validate_actual_snapshot(path: Path, review_date: str) -> None:
    try:
        text = path.read_text(encoding="utf-8")
        payload_text = OIL_FUTURES_PREFIX.sub("", text, count=1).strip()
        if payload_text == text.strip():
            raise ValueError("文件不是 window.OIL_FUTURES_CONTRACTS 结构")
        if payload_text.endswith(";"):
            payload_text = payload_text[:-1].rstrip()
        payload = json.loads(payload_text)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise StageFailure("actual_snapshot", f"actual快照无法读取：{exc}") from exc
    contracts = payload.get("contracts") if isinstance(payload, dict) else None
    if not isinstance(contracts, list):
        raise StageFailure("actual_snapshot", "actual快照缺少 contracts 数组")
    selected: dict[str, dict[str, Any]] = {}
    for record in contracts:
        if not isinstance(record, dict) or record.get("product") not in TRACKED_PRODUCTS:
            continue
        try:
            rank = int(record.get("contract_rank"))
        except (TypeError, ValueError):
            continue
        if rank == 1:
            product = str(record["product"])
            if product in selected:
                raise StageFailure("actual_snapshot", f"actual快照存在重复rank=1合约：{product}")
            selected[product] = record
    missing = sorted(TRACKED_PRODUCTS - set(selected))
    if missing:
        raise StageFailure("actual_snapshot", f"actual快照缺少rank=1合约：{', '.join(missing)}")
    for product, record in selected.items():
        if record.get("trade_date") != review_date:
            raise StageFailure("actual_snapshot", f"actual快照 {product} trade_date 与复盘日期不一致")
        fields = {
            "close": record.get("price", record.get("close")),
            "previous_close": record.get("preclose", record.get("previous_close")),
            "high": record.get("high"),
            "low": record.get("low"),
        }
        invalid = [name for name, value in fields.items() if not _finite_number(value)]
        if invalid:
            raise StageFailure("actual_snapshot", f"actual快照 {product} 缺少有效字段：{', '.join(invalid)}")


def evaluated_at_for_run(evaluated_path: Path) -> str:
    """Reuse an existing evaluation timestamp so identical reruns remain idempotent."""
    if evaluated_path.exists():
        try:
            payload = json.loads(evaluated_path.read_text(encoding="utf-8"))
            values = {
                record.get("evaluation", {}).get("evaluated_at")
                for record in payload.get("records", [])
                if isinstance(record, dict) and isinstance(record.get("evaluation"), dict)
            }
            if len(values) == 1:
                existing = next(iter(values))
                if isinstance(existing, str) and existing.endswith("+08:00"):
                    return existing
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    return datetime.now(SHANGHAI).isoformat(timespec="seconds")


def run_review_pipeline(review_date: str) -> dict[str, Any]:
    forecast_path = FORECAST_DIR / f"{review_date}.json"
    actual_path = SNAPSHOT_DIR / f"{review_date}-actual-oil_futures.js"
    previous_path = SNAPSHOT_DIR / f"{review_date}-previous-oil_futures.js"
    daily_review_path = DAILY_REVIEW_DIR / f"{review_date}.json"
    evaluated_path = EVALUATED_DIR / f"{review_date}.json"

    if not forecast_path.exists():
        raise StageFailure("forecast_missing", f"冻结预测不存在：{_relative(forecast_path)}")
    required_scripts = {
        "actual_snapshot": UPDATE_SCRIPT,
        "daily_review": REVIEW_SCRIPT,
        "forecast_evaluation": EVALUATE_SCRIPT,
        "metrics": METRICS_SCRIPT,
    }
    for stage, script in required_scripts.items():
        if not script.exists():
            raise StageFailure(stage, f"依赖脚本不存在：{_relative(script)}")

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    EVALUATED_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    archive_morning_tab(previous_path)

    actual = run_stage(
        [
            sys.executable,
            str(UPDATE_SCRIPT),
            "--mode",
            "actual-snapshot",
            "--snapshot-date",
            review_date,
            "--output",
            str(actual_path),
        ],
        "actual_snapshot",
    )
    if actual.returncode != 0:
        raise StageFailure("actual_snapshot", _command_reason(actual, "actual快照生成失败"))
    validate_actual_snapshot(actual_path, review_date)

    review = run_stage(
        [
            sys.executable,
            str(REVIEW_SCRIPT),
            "--previous",
            str(previous_path),
            "--current",
            str(actual_path),
            "--date",
            review_date,
            "--output-dir",
            str(DAILY_REVIEW_DIR),
        ],
        "daily_review",
    )
    if review.returncode != 0:
        raise StageFailure("daily_review", _command_reason(review, "daily review失败"))
    review_payload = _parse_json_output(review, "daily_review")
    if review_payload.get("status") != "OK" or not daily_review_path.exists():
        raise StageFailure("daily_review", str(review_payload.get("failure_reason") or "daily review未生成有效结果文件"))

    evaluation = run_stage(
        [
            sys.executable,
            str(EVALUATE_SCRIPT),
            "--forecast",
            str(forecast_path),
            "--actual",
            str(actual_path),
            "--output",
            str(evaluated_path),
            "--evaluated-at",
            evaluated_at_for_run(evaluated_path),
        ],
        "forecast_evaluation",
    )
    if evaluation.returncode != 0:
        raise StageFailure("forecast_evaluation", _command_reason(evaluation, "预测评估失败"))
    evaluation_payload = _parse_json_output(evaluation, "forecast_evaluation")
    if evaluation_payload.get("status") != "ok" or not evaluated_path.exists():
        raise StageFailure("forecast_evaluation", "评估器未生成有效已评估文件")

    metrics = run_stage(
        [
            sys.executable,
            str(METRICS_SCRIPT),
            "--evaluated-dir",
            str(EVALUATED_DIR),
            "--forecast-dir",
            str(FORECAST_DIR),
            "--output-dir",
            str(METRICS_DIR),
            "--as-of",
            review_date,
        ],
        "metrics",
    )
    if metrics.returncode != 0:
        raise StageFailure("metrics", _command_reason(metrics, "滚动统计更新失败"))
    metrics_payload = _parse_json_output(metrics, "metrics")
    metrics_paths = [METRICS_DIR / name for name in ("latest.json", "20d.json", "60d.json")]
    if metrics_payload.get("status") != "ok" or any(not path.exists() for path in metrics_paths):
        raise StageFailure("metrics", "统计器未生成latest/20d/60d完整输出")

    warnings: list[str] = []
    cleanup_status = "ok"
    if not PRUNE_SCRIPT.exists():
        cleanup_status = "warning"
        warnings.append(f"清理脚本不存在：{_relative(PRUNE_SCRIPT)}")
    else:
        try:
            cleanup = run_stage(
                [
                    sys.executable,
                    str(PRUNE_SCRIPT),
                    "--forecast-daily-dir",
                    str(FORECAST_DIR),
                    "--evaluated-dir",
                    str(EVALUATED_DIR),
                    "--review-daily-dir",
                    str(DAILY_REVIEW_DIR),
                    "--runtime-snapshot-dir",
                    str(SNAPSHOT_DIR),
                    "--apply",
                ],
                "cleanup",
            )
            if cleanup.returncode != 0:
                cleanup_status = "warning"
                warnings.append(_command_reason(cleanup, "预测复盘产物清理失败"))
            else:
                cleanup_payload = _parse_json_output(cleanup, "cleanup")
                if cleanup_payload.get("status") != "ok":
                    cleanup_status = "warning"
                    warnings.append(f"清理脚本返回异常状态：{cleanup_payload}")
                warnings.extend(str(item) for item in cleanup_payload.get("warnings", []) if item)
        except (StageFailure, OSError, ValueError) as exc:
            cleanup_status = "warning"
            warnings.append(f"预测复盘产物清理失败：{exc}")

    return {
        "date": review_date,
        "status": "ok",
        "forecast_path": _relative(forecast_path),
        "actual_snapshot_path": _relative(actual_path),
        "daily_review_path": _relative(daily_review_path),
        "evaluated_forecast_path": _relative(evaluated_path),
        "metrics_paths": [_relative(path) for path in metrics_paths],
        "evaluation_status": "evaluated",
        "metrics_status": "ok",
        "cleanup_status": cleanup_status,
        "warnings": warnings,
        "learning_notes_path": review_payload.get("learning_notes_path"),
        "review_memory": review_payload.get("review_memory", {}),
        "review_result": review_payload.get("review_result", []),
        "error_type": review_payload.get("error_type", []),
        "suggested_improvement": review_payload.get("suggested_improvement", []),
        "whether_update_rule": review_payload.get("whether_update_rule", False),
        "human_approval_required": review_payload.get("human_approval_required", False),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Review date, YYYY-MM-DD. Defaults to today in Asia/Shanghai.")
    parser.add_argument("--force", action="store_true", help="Run even on weekends.")
    args = parser.parse_args()

    try:
        review_date = today_string(args.date)
        datetime.strptime(review_date, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({"date": args.date, "status": "failed", "stage": "actual_snapshot", "reason": "日期必须为有效 YYYY-MM-DD"}, ensure_ascii=False, sort_keys=True))
        return 2

    if not args.force and not is_trading_day(review_date):
        print(json.dumps({"date": review_date, "status": "skipped", "reason": "非交易日不运行夜盘复盘"}, ensure_ascii=False, sort_keys=True))
        return 0

    try:
        result = run_review_pipeline(review_date)
    except StageFailure as exc:
        result = {"date": review_date, "status": "failed", "stage": exc.stage, "reason": exc.reason}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2
    except Exception as exc:
        result = {"date": review_date, "status": "failed", "stage": "actual_snapshot", "reason": f"未预期错误：{exc}"}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2

    try:
        _write_text_atomically(LATEST_REVIEW, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    except OSError as exc:
        failed = {"date": review_date, "status": "failed", "stage": "daily_review", "reason": f"复盘摘要写入失败：{exc}"}
        print(json.dumps(failed, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

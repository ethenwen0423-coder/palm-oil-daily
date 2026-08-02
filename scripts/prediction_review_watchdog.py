#!/usr/bin/env python3
"""Recover and publish every due forecast review from a clean runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, time as datetime_time
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_ROOT = Path.home() / "Sites" / "palm-oil-daily-runtime"
DEFAULT_LEGACY_ROOT = Path.home() / "Sites" / "palm-oil-daily"
DEFAULT_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "VinsonTesla"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GENERATED_PATHS = (
    "data/forecast/evaluated",
    "data/forecast/metrics/latest.json",
    "data/forecast/metrics/20d.json",
    "data/forecast/metrics/60d.json",
    "data/forecast/feedback/latest.json",
    "data/review/daily",
    "data/review/latest_review.json",
)


class WatchdogError(RuntimeError):
    """A recoverable automation or publishing failure."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_forecast_input(path: Path) -> bool:
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError):
        return False
    return (
        isinstance(payload, dict)
        and payload.get("schema_version") == "forecast-schema-v1"
        and payload.get("report_date") == path.stem
        and isinstance(payload.get("records"), list)
        and len(payload["records"]) == 3
    )


def sync_forecast_inputs(root: Path, legacy_root: Optional[Path]) -> list[str]:
    if legacy_root is None or legacy_root.resolve() == root.resolve():
        return []
    source_dir = legacy_root / "data" / "forecast" / "daily"
    target_dir = root / "data" / "forecast" / "daily"
    if not source_dir.is_dir():
        return []
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for source in sorted(source_dir.glob("*.json")):
        if not DATE_RE.fullmatch(source.stem) or not valid_forecast_input(source):
            continue
        target = target_dir / source.name
        if target.exists():
            if file_digest(source) != file_digest(target):
                raise WatchdogError(f"同日 forecast 输入冲突，拒绝覆盖：{source.name}")
            continue
        shutil.copy2(source, target)
        copied.append(source.stem)
    return copied


def evaluated_is_valid(root: Path, report_date: str) -> bool:
    evaluated_path = root / "data" / "forecast" / "evaluated" / f"{report_date}.json"
    metrics_path = root / "data" / "forecast" / "metrics" / "latest.json"
    try:
        evaluated = load_json(evaluated_path)
        metrics = load_json(metrics_path)
    except (OSError, json.JSONDecodeError):
        return False
    records = evaluated.get("records") if isinstance(evaluated, dict) else None
    return (
        evaluated.get("report_date") == report_date
        and isinstance(records, list)
        and len(records) == 3
        and all(
            isinstance(record, dict) and record.get("evaluation_status") == "evaluated"
            for record in records
        )
        and metrics.get("schema_version") == "forecast-metrics-v1"
        and str(metrics.get("as_of") or "") >= report_date
    )


def pending_dates(root: Path, now: datetime, maximum: int) -> list[str]:
    daily_dir = root / "data" / "forecast" / "daily"
    if not daily_dir.is_dir():
        return []
    today = now.date().isoformat()
    current_time = now.timetz().replace(tzinfo=None)
    pending: list[str] = []
    for path in sorted(daily_dir.glob("*.json")):
        report_date = path.stem
        if not DATE_RE.fullmatch(report_date) or report_date > today:
            continue
        if report_date == today and current_time < datetime_time(15, 20):
            continue
        if not valid_forecast_input(path):
            continue
        if not evaluated_is_valid(root, report_date):
            pending.append(report_date)
    return pending[:maximum]


def load_private_env(path: Path, environment: dict[str, str]) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, separator, value = line.partition("=")
        if not separator:
            continue
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in environment:
            environment[key] = value


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(SHANGHAI).isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"[{stamp}] {message.rstrip()}\n")


def run_logged(
    command: list[str],
    *,
    root: Path,
    log: Path,
    environment: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        append_log(log, f"timeout={timeout}s command={command[0]} {command[1] if len(command) > 1 else ''}")
        raise WatchdogError(f"子进程超过 {timeout} 秒：{command[0]}") from exc
    if result.stdout.strip():
        append_log(log, result.stdout.strip())
    if result.stderr.strip():
        append_log(log, result.stderr.strip())
    return result


def git_output(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise WatchdogError(result.stderr.strip() or result.stdout.strip() or "git 命令失败")
    return result.stdout.strip()


def sync_git(root: Path, log: Path, environment: dict[str, str]) -> None:
    branch = git_output(root, "branch", "--show-current")
    if branch != "main":
        raise WatchdogError(f"prediction review runtime 必须位于 main，当前为 {branch or 'detached'}")
    dirty = git_output(root, "status", "--porcelain", "--untracked-files=all")
    if dirty:
        raise WatchdogError("prediction review runtime 不是干净工作区")

    sync_script = root / "scripts" / "sync_automation_runtime.py"
    if not sync_script.is_file():
        raise WatchdogError("prediction review runtime 缺少安全同步器")
    result = run_logged(
        [sys.executable, str(sync_script), "--root", str(root)],
        root=root,
        log=log,
        environment=environment,
        timeout=300,
    )
    if result.returncode != 0:
        raise WatchdogError("prediction review runtime 安全同步失败")


def rollback_generated(root: Path, report_date: str, head: str, log: Path) -> None:
    subprocess.run(
        ["git", "restore", "--source", head, "--staged", "--worktree", "--", *GENERATED_PATHS],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    for relative in (
        f"data/forecast/evaluated/{report_date}.json",
        f"data/review/daily/{report_date}.json",
    ):
        target = root / relative
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        ).returncode == 0
        if target.exists() and not tracked:
            target.unlink()
    append_log(log, f"rolled back failed generated outputs date={report_date}")


def review_date(
    root: Path,
    report_date: str,
    log: Path,
    environment: dict[str, str],
) -> str:
    head_before = git_output(root, "rev-parse", "HEAD")
    review = run_logged(
        [sys.executable, "scripts/review_prediction.py", "--date", report_date],
        root=root,
        log=log,
        environment=environment,
        timeout=900,
    )
    if review.returncode != 0:
        rollback_generated(root, report_date, head_before, log)
        raise WatchdogError(f"{report_date} 预测评估失败")

    publish = run_logged(
        [
            "bash",
            "scripts/publish_prediction_review.sh",
            "--publish",
            "--confirm-persistence-reviewed",
            "--date",
            report_date,
        ],
        root=root,
        log=log,
        environment=environment,
        timeout=240,
    )
    if publish.returncode != 0:
        head_after = git_output(root, "rev-parse", "HEAD")
        if head_after == head_before:
            rollback_generated(root, report_date, head_before, log)
        else:
            append_log(log, f"publish failed after commit; leave clean pending push date={report_date}")
        raise WatchdogError(f"{report_date} 评估发布失败")
    return git_output(root, "rev-parse", "--short", "HEAD")


def acquire_lock(lock_dir: Path, stale_after_seconds: int = 2700) -> bool:
    lock_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_dir.mkdir()
        return True
    except FileExistsError:
        try:
            age = time.time() - lock_dir.stat().st_mtime
            if age > stale_after_seconds and not any(lock_dir.iterdir()):
                lock_dir.rmdir()
                lock_dir.mkdir()
                return True
        except (FileNotFoundError, OSError):
            return False
        return False


def parse_now(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_PREDICTION_RUNTIME_ROOT", DEFAULT_ROOT)),
    )
    parser.add_argument(
        "--legacy-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_PREDICTION_LEGACY_ROOT", DEFAULT_LEGACY_ROOT)),
    )
    parser.add_argument(
        "--support-dir",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SUPPORT_DIR", DEFAULT_SUPPORT_DIR)),
    )
    parser.add_argument("--now", default=os.environ.get("PALM_OIL_PREDICTION_NOW"))
    parser.add_argument("--max-dates", type=int, default=5)
    args = parser.parse_args()

    root = args.root.resolve()
    support_dir = args.support_dir.resolve()
    log = support_dir / "palm-oil-prediction-review" / "prediction-review.log"
    lock_dir = support_dir / "market-data-deploy.lock"
    if not acquire_lock(lock_dir):
        append_log(log, "market-data deploy busy; retry prediction review next interval")
        print(json.dumps({"status": "busy", "retry": True}, ensure_ascii=False))
        return 0

    environment = dict(os.environ)
    load_private_env(support_dir / "private.env", environment)
    completed: list[dict[str, str]] = []
    copied: list[str] = []
    try:
        sync_git(root, log, environment)
        copied = sync_forecast_inputs(root, args.legacy_root.resolve())
        due = pending_dates(root, parse_now(args.now), max(1, args.max_dates))
        if not due:
            payload = {"status": "noop", "copied_forecasts": copied, "pending_dates": []}
            append_log(log, json.dumps(payload, ensure_ascii=False))
            print(json.dumps(payload, ensure_ascii=False))
            return 0
        for report_date in due:
            append_log(log, f"start prediction review date={report_date}")
            commit = review_date(root, report_date, log, environment)
            completed.append({"date": report_date, "commit": commit})
        payload = {
            "status": "ok",
            "copied_forecasts": copied,
            "completed": completed,
            "remaining_pending": pending_dates(root, parse_now(args.now), 100),
        }
        append_log(log, json.dumps(payload, ensure_ascii=False))
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except (WatchdogError, OSError, json.JSONDecodeError) as exc:
        payload = {
            "status": "error",
            "reason": str(exc),
            "copied_forecasts": copied,
            "completed": completed,
        }
        append_log(log, json.dumps(payload, ensure_ascii=False))
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        try:
            lock_dir.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

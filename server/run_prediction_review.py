#!/usr/bin/env python3
"""Evaluate due forecasts from server-owned morning and close snapshots."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_RUNTIME_ROOT = Path("/srv/palm-oil-daily/research-runtime")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
DEFAULT_STATE_ROOT = Path("/srv/palm-oil-daily/state")


class ServerReviewError(RuntimeError):
    """Raised when a due prediction review cannot be completed safely."""


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ServerReviewError(f"cannot load server module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def persist_generated_data(state_root: Path, runtime_root: Path) -> None:
    data_store = state_root / "research-data"
    for relative in ("forecast", "review"):
        source = runtime_root / "data" / relative
        if source.is_dir():
            shutil.copytree(
                source,
                data_store / relative,
                dirs_exist_ok=True,
                copy_function=shutil.copy2,
            )


def run_review(
    runtime_root: Path,
    report_date: str,
    environment: dict[str, str],
    log_path: Path,
    actual_snapshot: Path,
) -> dict[str, object]:
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/review_prediction.py",
                "--date",
                report_date,
                "--prepared-actual",
                str(actual_snapshot),
            ],
            cwd=runtime_root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=900,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ServerReviewError(f"prediction review did not complete: {exc}") from exc
    output = (completed.stdout or "") + (completed.stderr or "")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(output)
        if output and not output.endswith("\n"):
            log.write("\n")
    if completed.returncode != 0:
        raise ServerReviewError(
            f"prediction review failed for {report_date}: {output[-1600:]}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ServerReviewError("prediction review returned invalid JSON") from exc
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        raise ServerReviewError(f"prediction review returned non-ready status: {payload}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)))
    parser.add_argument("--runtime-root", type=Path, default=Path(os.environ.get("PALM_OIL_RESEARCH_RUNTIME_ROOT", DEFAULT_RUNTIME_ROOT)))
    parser.add_argument("--live-data-root", type=Path, default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)))
    parser.add_argument("--state-root", type=Path, default=Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", DEFAULT_STATE_ROOT)))
    parser.add_argument("--now", default=os.environ.get("PALM_OIL_PREDICTION_NOW"))
    parser.add_argument("--max-dates", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now = parse_now(args.now)
    site_root = args.site_root.resolve()
    runtime_root = args.runtime_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_root = args.state_root.resolve()
    support = load_module("server_review_support", Path(__file__).with_name("run_market_collector.py"))
    research = load_module("server_review_research_support", Path(__file__).with_name("run_research_agent.py"))
    try:
        support.validate_runtime_paths(site_root, runtime_root, live_data_root)
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2
    plan = {
        "status": "planned",
        "now": now.isoformat(timespec="seconds"),
        "runtime_root": str(runtime_root),
        "live_data_root": str(live_data_root),
        "current_day_eligible_after": "15:20 Asia/Shanghai",
        "max_dates": max(1, args.max_dates),
    }
    if args.dry_run:
        print(json.dumps({**plan, "dry_run": True}, ensure_ascii=False, sort_keys=True))
        return 0

    lock = support.acquire_lock(state_root / "automation.lock")
    if lock is None:
        print(json.dumps({"status": "busy", "retry": True}, ensure_ascii=False))
        return 0
    log_path = state_root / "prediction-review.log"
    try:
        sync_module = support.import_sync_module(site_root)
        sync_module.sync_upstream(site_root / "data", live_data_root)
        support.ensure_runtime(site_root, runtime_root)
        support.copy_live_inputs(live_data_root, runtime_root)
        research.restore_persistent_outputs(state_root, runtime_root)
        watchdog = load_module(
            "server_prediction_watchdog_support",
            runtime_root / "scripts" / "prediction_review_watchdog.py",
        )
        pending = watchdog.pending_dates(runtime_root, now, max(1, args.max_dates))
        today = now.date().isoformat()
        eligible = [
            report_date
            for report_date in pending
            if report_date == today
            or (
                runtime_root
                / "data"
                / "review"
                / "runtime_snapshots"
                / f"{report_date}-actual-oil_futures.js"
            ).is_file()
        ]
        blocked = [report_date for report_date in pending if report_date not in eligible]
        if not eligible:
            print(
                json.dumps(
                    {
                        "status": "noop",
                        "pending_dates": pending,
                        "blocked_historical_dates": blocked,
                        "reason": "no_due_review_with_actual_snapshot",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0
        environment = {**os.environ, "PYTHONUNBUFFERED": "1"}
        watchdog.load_private_env(state_root / "private.env", environment)
        completed: list[dict[str, object]] = []
        for report_date in eligible:
            actual_snapshot = (
                runtime_root / "data" / "oil_futures.js"
                if report_date == today
                else runtime_root
                / "data"
                / "review"
                / "runtime_snapshots"
                / f"{report_date}-actual-oil_futures.js"
            )
            payload = run_review(
                runtime_root,
                report_date,
                environment,
                log_path,
                actual_snapshot,
            )
            if not watchdog.evaluated_is_valid(runtime_root, report_date):
                raise ServerReviewError(f"review outputs failed validation: {report_date}")
            completed.append(
                {
                    "date": report_date,
                    "evaluation_status": payload.get("evaluation_status"),
                    "metrics_status": payload.get("metrics_status"),
                }
            )
        persist_generated_data(state_root, runtime_root)
        synced = sync_module.sync_review(
            runtime_root / "data",
            live_data_root,
            session=completed[-1]["date"],
        )
        result = {
            "status": "ok",
            "completed": completed,
            "blocked_historical_dates": blocked,
            "copied": synced["copied"],
            "server_review_owned": True,
            "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        }
        support.atomic_state_marker(
            state_root / "review-runs" / f"{completed[-1]['date']}.ok.json",
            result,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ServerReviewError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc), "retry": True}, ensure_ascii=False, sort_keys=True))
        return 2
    finally:
        support.fcntl.flock(lock.fileno(), support.fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

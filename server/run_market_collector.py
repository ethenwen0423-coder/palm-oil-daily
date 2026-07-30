#!/usr/bin/env python3
"""Run one recoverable server-side market refresh into the live API data mount."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import IO
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_RUNTIME_ROOT = Path("/srv/palm-oil-daily/market-runtime")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
DEFAULT_STATE_ROOT = Path("/srv/palm-oil-daily/state")
SESSIONS = ("morning", "midday", "close", "night_open", "night_close", "overnight")


class CollectorError(RuntimeError):
    """Raised when the collector cannot safely publish a complete refresh."""


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def select_session(now: datetime) -> tuple[str, str] | None:
    weekday = now.isoweekday()
    minutes = now.hour * 60 + now.minute
    if 2 <= weekday <= 6 and 160 <= minutes < 390:
        return "overnight", (now.date() - timedelta(days=1)).isoformat()
    if not 1 <= weekday <= 5:
        return None
    thresholds = (
        (1390, "night_close"),
        (1280, "night_open"),
        (905, "close"),
        (695, "midday"),
        (390, "morning"),
    )
    for threshold, session in thresholds:
        if minutes >= threshold:
            return session, now.date().isoformat()
    return None


def validate_runtime_paths(
    site_root: Path,
    runtime_root: Path,
    live_data_root: Path,
) -> None:
    resolved = {
        "site": site_root.resolve(),
        "runtime": runtime_root.resolve(),
        "live": live_data_root.resolve(),
    }
    if len(set(resolved.values())) != 3:
        raise CollectorError("site, runtime and live-data paths must be distinct")
    runtime = resolved["runtime"]
    if runtime in {Path("/"), Path("/srv"), Path.home().resolve()}:
        raise CollectorError(f"unsafe runtime path: {runtime}")
    if len(runtime.parts) < 3:
        raise CollectorError(f"runtime path is too broad: {runtime}")


def run_checked(
    arguments: list[str],
    *,
    cwd: Path | None = None,
    environment: dict[str, str] | None = None,
    timeout: int = 1800,
    output: IO[str] | int | None = subprocess.PIPE,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            arguments,
            cwd=cwd,
            env=environment,
            text=True,
            stdout=output,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectorError(f"command failed to start: {arguments[0]}: {exc}") from exc
    if result.returncode != 0:
        detail = result.stdout.strip() if isinstance(result.stdout, str) else ""
        raise CollectorError(
            f"command failed ({result.returncode}): {' '.join(arguments[:3])}"
            + (f": {detail[-1000:]}" if detail else "")
        )
    return result


def ensure_runtime(site_root: Path, runtime_root: Path) -> None:
    if not (site_root / ".git").exists():
        raise CollectorError(f"site checkout is missing: {site_root}")
    if runtime_root.exists() and not (runtime_root / ".git").exists():
        raise CollectorError(f"runtime exists but is not a Git checkout: {runtime_root}")
    if not runtime_root.exists():
        runtime_root.parent.mkdir(parents=True, exist_ok=True)
        run_checked(
            [
                "git",
                "clone",
                "--branch",
                "main",
                "--single-branch",
                "--no-hardlinks",
                str(site_root),
                str(runtime_root),
            ],
            timeout=180,
        )
    run_checked(["git", "fetch", "origin", "main"], cwd=runtime_root, timeout=120)
    run_checked(["git", "reset", "--hard", "origin/main"], cwd=runtime_root, timeout=60)
    run_checked(["git", "clean", "-fdx"], cwd=runtime_root, timeout=60)


def import_sync_module(site_root: Path):
    import importlib.util

    script = site_root / "server" / "sync_live_data.py"
    spec = importlib.util.spec_from_file_location("server_sync_live_data", script)
    if spec is None or spec.loader is None:
        raise CollectorError(f"cannot load live-data sync module: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_live_inputs(live_data_root: Path, runtime_root: Path) -> None:
    if not live_data_root.is_dir():
        raise CollectorError(f"live-data directory is missing: {live_data_root}")
    shutil.copytree(
        live_data_root,
        runtime_root / "data",
        dirs_exist_ok=True,
        copy_function=shutil.copy2,
    )


def atomic_state_marker(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def acquire_lock(path: Path) -> IO[str] | None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        stream.close()
        return None
    return stream


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)),
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_MARKET_RUNTIME_ROOT", DEFAULT_RUNTIME_ROOT)),
    )
    parser.add_argument(
        "--live-data-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)),
    )
    parser.add_argument(
        "--state-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", DEFAULT_STATE_ROOT)),
    )
    parser.add_argument("--now", default=os.environ.get("PALM_OIL_COLLECTOR_NOW"))
    parser.add_argument("--force-session", choices=SESSIONS)
    parser.add_argument("--fundamental-date")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now = parse_now(args.now)
    selected = select_session(now)
    if args.force_session:
        selected = (
            args.force_session,
            args.fundamental_date or now.date().isoformat(),
        )
    if not selected:
        print(
            json.dumps(
                {
                    "status": "noop",
                    "reason": "outside_market_refresh_windows",
                    "now": now.isoformat(timespec="seconds"),
                },
                ensure_ascii=False,
            )
        )
        return 0

    session, fundamental_date = selected
    site_root = args.site_root.resolve()
    runtime_root = args.runtime_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_root = args.state_root.resolve()
    try:
        validate_runtime_paths(site_root, runtime_root, live_data_root)
    except CollectorError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2
    state_marker = state_root / "sessions" / f"{fundamental_date}-{session}.ok.json"
    plan = {
        "status": "planned",
        "session": session,
        "fundamental_date": fundamental_date,
        "site_root": str(site_root),
        "runtime_root": str(runtime_root),
        "live_data_root": str(live_data_root),
        "state_marker": str(state_marker),
    }
    if args.dry_run:
        print(json.dumps({**plan, "dry_run": True}, ensure_ascii=False, sort_keys=True))
        return 0
    if state_marker.exists():
        print(
            json.dumps(
                {
                    "status": "noop",
                    "reason": "session_already_published",
                    "session": session,
                    "fundamental_date": fundamental_date,
                },
                ensure_ascii=False,
            )
        )
        return 0

    lock = acquire_lock(state_root / "market-collector.lock")
    if lock is None:
        print(json.dumps({"status": "busy", "retry": True}, ensure_ascii=False))
        return 0
    log_path = state_root / "market-collector.log"
    try:
        sync_module = import_sync_module(site_root)
        sync_module.sync_upstream(site_root / "data", live_data_root)
        ensure_runtime(site_root, runtime_root)
        copy_live_inputs(live_data_root, runtime_root)
        environment = {
            **os.environ,
            "PALM_OIL_PUBLISH_MODE": "files",
            "PALM_OIL_SUPPORT_DIR": str(state_root / "work"),
            "PALM_OIL_PRIVATE_ENV": str(state_root / "private.env"),
            "PYTHONUNBUFFERED": "1",
        }
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log:
            log.write(
                f"[{now.isoformat(timespec='seconds')}] start session={session} "
                f"fundamental_date={fundamental_date}\n"
            )
            run_checked(
                [
                    "bash",
                    "scripts/deploy_oil_futures_tab.sh",
                    session,
                    fundamental_date,
                ],
                cwd=runtime_root,
                environment=environment,
                timeout=2400,
                output=log,
            )
        synced = sync_module.sync_market(
            runtime_root / "data",
            live_data_root,
            session=session,
        )
        completed = {
            "status": "ok",
            "session": session,
            "fundamental_date": fundamental_date,
            "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            "copied": synced["copied"],
        }
        atomic_state_marker(state_marker, completed)
        print(json.dumps(completed, ensure_ascii=False, sort_keys=True))
        return 0
    except (CollectorError, OSError, RuntimeError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "session": session,
                    "fundamental_date": fundamental_date,
                    "reason": str(exc),
                    "retry": True,
                },
                ensure_ascii=False,
            )
        )
        return 2
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

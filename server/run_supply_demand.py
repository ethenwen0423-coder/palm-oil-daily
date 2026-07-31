#!/usr/bin/env python3
"""Check official supply-demand sources and publish one validated live snapshot."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
DEFAULT_STATE_ROOT = Path("/srv/palm-oil-daily/state")


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)),
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
    parser.add_argument("--now", default=os.environ.get("PALM_OIL_SUPPLY_NOW"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now = parse_now(args.now)
    report_date = now.date().isoformat()
    site_root = args.site_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_root = args.state_root.resolve()
    daily_marker = state_root / "supply" / f"{report_date}.ok.json"
    plan = {
        "status": "planned",
        "report_date": report_date,
        "site_root": str(site_root),
        "live_data_root": str(live_data_root),
        "state_marker": str(daily_marker),
    }
    if args.dry_run:
        print(json.dumps({**plan, "dry_run": True}, ensure_ascii=False, sort_keys=True))
        return 0
    if daily_marker.exists() and not args.force:
        print(
            json.dumps(
                {
                    "status": "noop",
                    "reason": "official_sources_already_checked_today",
                    "report_date": report_date,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if not (site_root / "scripts" / "update_supply_demand_data.py").is_file():
        print(
            json.dumps(
                {"status": "error", "reason": "supply-demand updater is missing"},
                ensure_ascii=False,
            )
        )
        return 2
    if not live_data_root.is_dir():
        print(
            json.dumps(
                {"status": "error", "reason": "live-data directory is missing"},
                ensure_ascii=False,
            )
        )
        return 2

    from run_market_collector import (  # pylint: disable=import-outside-toplevel
        CollectorError,
        acquire_lock,
        atomic_state_marker,
        import_sync_module,
        run_checked,
    )

    lock = acquire_lock(state_root / "automation.lock")
    if lock is None:
        print(json.dumps({"status": "busy", "retry": True}, ensure_ascii=False))
        return 0
    log_path = state_root / "supply-demand.log"
    try:
        sync_module = import_sync_module(site_root)
        with tempfile.TemporaryDirectory(prefix="server-supply-demand.") as temporary:
            output_root = Path(temporary) / "data"
            output_path = output_root / "supply-demand.json"
            command = [
                sys.executable,
                "scripts/update_supply_demand_data.py",
                "--output",
                str(output_path),
                "--existing",
                str(live_data_root / "supply-demand.json"),
                "--report-date",
                report_date,
                "--strict",
            ]
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as log:
                log.write(f"[{now.isoformat(timespec='seconds')}] start official source check\n")
                run_checked(
                    command,
                    cwd=site_root,
                    environment={**os.environ, "PYTHONUNBUFFERED": "1"},
                    timeout=1200,
                    output=log,
                )
                run_checked(
                    [
                        sys.executable,
                        "scripts/update_supply_demand_data.py",
                        "--validate-only",
                        str(output_path),
                        "--strict",
                    ],
                    cwd=site_root,
                    environment={**os.environ, "PYTHONUNBUFFERED": "1"},
                    timeout=120,
                    output=log,
                )
            synced = sync_module.sync_supply(
                output_root,
                live_data_root,
                session="daily",
            )
        completed = {
            "status": "ok",
            "report_date": report_date,
            "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            "copied": synced["copied"],
            "server_supply_owned": True,
        }
        atomic_state_marker(daily_marker, completed)
        print(json.dumps(completed, ensure_ascii=False, sort_keys=True))
        return 0
    except (CollectorError, OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "report_date": report_date,
                    "reason": str(exc),
                    "retry": True,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

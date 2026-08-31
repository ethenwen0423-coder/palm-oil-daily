#!/usr/bin/env python3
"""Refresh exact-contract AI Daredevil position marks every trading minute."""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import json
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ai_daredevil_quote_base", SCRIPT_ROOT / "run_ai_daredevil.py")
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)


def trading_session(now: datetime) -> str | None:
    """Return the broad China-futures session containing ``now``.

    Individual contracts may close earlier at night. Their last exchange quote
    remains the latest valid price, while the source timestamp stays unchanged.
    """
    clock = now.time().replace(tzinfo=None)
    weekday = now.weekday()
    if weekday < 5:
        if time(9) <= clock <= time(10, 15):
            return "day-morning-1"
        if time(10, 30) <= clock <= time(11, 30):
            return "day-morning-2"
        if time(13, 30) <= clock <= time(15):
            return "day-afternoon"
        if time(21) <= clock <= time(23, 59, 59):
            return "night-evening"
    if weekday in {1, 2, 3, 4, 5} and time(0) <= clock <= time(2, 30):
        return "night-after-midnight"
    return None


def next_trading_refresh(now: datetime) -> str | None:
    next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    if trading_session(now) and trading_session(next_minute):
        return next_minute.isoformat(timespec="seconds")
    candidates = []
    for offset in range(8):
        day = (now + timedelta(days=offset)).date()
        if day.weekday() < 5:
            for clock in (time(9), time(10, 30), time(13, 30), time(21)):
                point = datetime.combine(day, clock, BASE.SHANGHAI)
                if point > now:
                    candidates.append(point)
        if day.weekday() in {1, 2, 3, 4, 5}:
            point = datetime.combine(day, time(0), BASE.SHANGHAI)
            if point > now:
                candidates.append(point)
    return min(candidates).isoformat(timespec="seconds") if candidates else None


def _source_clock_minutes(value: Any) -> int | None:
    match = re.search(r"(?:^|\s)([0-2]?\d):([0-5]\d)(?::[0-5]\d)?(?:\s|$)", str(value or "").strip())
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    return hour * 60 + minute if hour <= 23 else None


def quote_is_current(quote: dict[str, Any] | None, now: datetime, session: str) -> bool:
    if not quote or BASE.numeric(quote.get("last")) is None:
        return False
    try:
        trade_day = date.fromisoformat(str(quote.get("trade_date")))
    except (TypeError, ValueError):
        return False
    calendar_gap = (trade_day - now.date()).days
    if session.startswith("day-") and calendar_gap != 0:
        return False
    if session.startswith("night-") and not 0 <= calendar_gap <= 3:
        return False
    source_minutes = _source_clock_minutes(quote.get("source_time"))
    if source_minutes is None:
        return False
    now_minutes = now.hour * 60 + now.minute
    clock_gap = abs(source_minutes - now_minutes)
    return min(clock_gap, 24 * 60 - clock_gap) <= 5


def _publish(state_dir: Path, live_data_root: Path, state: dict[str, Any], sources: list[dict[str, Any]],
             scan_audit: dict[str, Any], skipped: list[dict[str, Any]], now: datetime,
             audit: dict[str, Any]) -> dict[str, Any]:
    payload = BASE.public_snapshot(
        state_dir, state, sources, "交易时段每分钟持仓盯市", skipped, scan_audit, now
    )
    payload["next_refresh"] = next_trading_refresh(now)
    payload["realtime_quote_audit"] = audit
    if audit["coverage_status"] != "complete":
        payload["status"] = "degraded"
        payload["status_label"] = "部分持仓分钟行情需进一步核验"
    BASE.atomic_json(live_data_root / BASE.FUND_FILE, payload)
    BASE.atomic_json(live_data_root / BASE.READY_MARKER, {
        "schema_version": 1,
        "generated_at": now.isoformat(timespec="seconds"),
        "session": "minute-quote",
        "owner": "server-ai-daredevil-quotes",
        "coverage_status": audit["coverage_status"],
    })
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path("/srv/palm-oil-daily/site"))
    parser.add_argument("--live-data-root", type=Path, default=Path("/srv/palm-oil-daily/live-data"))
    parser.add_argument("--state-root", type=Path, default=Path("/srv/palm-oil-daily/state"))
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--now", help="test-only ISO timestamp")
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now).astimezone(BASE.SHANGHAI) if args.now else BASE.now_shanghai()
    session = trading_session(now)
    if not session:
        print(json.dumps({"status": "skipped", "reason": "outside trading session", "generated_at": now.isoformat(timespec="seconds")}, ensure_ascii=False))
        return 0

    site_root = args.site_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_dir = args.state_root.resolve() / "ai-daredevil"
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = args.state_root.resolve() / "automation.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        if not args.now:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print(json.dumps({"status": "busy", "reason": "fund automation lock is held"}, ensure_ascii=False))
                return 0
        ledger = BASE.load_python(
            site_root / "skills" / "manage-bollinger-rsi-futures-fund" / "scripts" / "fund_ledger.py",
            "ai_daredevil_minute_quote_ledger",
        )
        BASE.init_ledger(ledger, state_dir)
        state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        positions = state.get("positions", {})
        scan_audit = BASE.read_json(state_dir / BASE.SCAN_AUDIT_FILE, {})
        skipped = list(scan_audit.get("issues", [])) if isinstance(scan_audit, dict) else []
        contracts = [position["contract"] for position in positions.values()]
        quotes, sources = BASE.resolve_quotes(contracts, args.timeout)
        fresh = {
            contract: quote for contract, quote in quotes.items()
            if quote_is_current(quote, now, session)
        }
        missing = sorted(set(contracts) - set(fresh))
        trade_dates = sorted({str(quote["trade_date"]) for quote in fresh.values()})
        audit = {
            "generated_at": now.isoformat(timespec="seconds"),
            "session": session,
            "expected_count": len(contracts),
            "validated_count": len(fresh),
            "coverage_status": "complete" if len(fresh) == len(contracts) and len(trade_dates) <= 1 else "partial",
            "missing_or_stale_contracts": missing,
            "trade_dates": trade_dates,
            "freshness_seconds": 300,
            "validation": "精确PYYMM、交易日、来源时钟与最新价均通过校验后才更新账本",
        }
        if positions and audit["coverage_status"] == "complete":
            mark_date = trade_dates[0]
            marks = {"as_of": mark_date, "source": "minute exact-contract quote fallback chain", "prices": [
                {"variety": variety, "contract": position["contract"],
                 "price": fresh[position["contract"]]["last"], "source": fresh[position["contract"]]["source"]}
                for variety, position in positions.items()
            ]}
            mark_path = state_dir / "latest_marks.json"
            BASE.atomic_json(mark_path, marks)
            ledger.command_mark(SimpleNamespace(state_dir=state_dir, prices=mark_path))
            BASE.atomic_json(state_dir / "latest_quote_observations.json", {
                "generated_at": now.isoformat(timespec="seconds"),
                "quotes": {
                    contract: {
                        "price": quote["last"],
                        "trade_date": quote["trade_date"],
                        "observed_at": now.isoformat(timespec="seconds"),
                        "source_observed_at": quote.get("observed_at"),
                        "source": quote.get("source"),
                    }
                    for contract, quote in fresh.items()
                },
            })
            state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
        payload = _publish(state_dir, live_data_root, state, sources, scan_audit, skipped, now, audit)
    print(json.dumps({
        "status": payload["status"],
        "generated_at": payload["generated_at"],
        "positions": len(payload["positions"]),
        "validated_quotes": audit["validated_count"],
        "coverage_status": audit["coverage_status"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Refresh multi-source market events every five minutes, independently of quotes."""

from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
SITE_ROOT = Path(os.environ.get("PALM_OIL_SITE_ROOT", "/srv/palm-oil-daily/site"))
LIVE_ROOT = Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", "/srv/palm-oil-daily/live-data"))
STATE_ROOT = Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", "/srv/palm-oil-daily/state"))


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def private_value(path: Path, key: str) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.strip().removeprefix("export ").partition("=")
            if separator and name.strip() == key and value.strip():
                return value.strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def env_value(key: str) -> str | None:
    return os.environ.get(key) or private_value(STATE_ROOT / "private.env", key)


def merge_snapshot(watch: Any, previous: dict[str, Any], events: list[dict[str, Any]], sources: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    merged = {
        str(item.get("id")): item
        for item in previous.get("events", [])
        if isinstance(item, dict) and item.get("id") and item.get("kind") == "market"
    }
    for item in events:
        merged[str(item["id"])] = item
    payload = dict(previous)
    payload.setdefault("schema_version", 1)
    payload.setdefault("status", "degraded")
    payload.setdefault("generated_at", now.isoformat(timespec="seconds"))
    payload.setdefault("timezone", "Asia/Shanghai")
    payload["events_updated_at"] = now.isoformat(timespec="seconds")
    payload["events"] = sorted(merged.values(), key=lambda item: str(item.get("observed_at") or ""), reverse=True)[: watch.MAX_EVENTS]
    coverage = dict(payload.get("coverage") or {})
    coverage["event_count"] = len(payload["events"])
    coverage["event_sources_ready"] = sum(item.get("state") == "ready" for item in sources)
    coverage["event_sources_total"] = len(sources)
    payload["coverage"] = coverage
    quote_sources = [item for item in previous.get("sources", []) if isinstance(item, dict) and item.get("name") == "全量期货行情"]
    payload["sources"] = [*quote_sources, *sources]
    return payload


def main() -> int:
    now = datetime.now(SHANGHAI)
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    lock = (STATE_ROOT / "market-watch.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "busy", "retry": True}))
        lock.close()
        return 0
    try:
        watch = load_module("palm_event_watch_base", SITE_ROOT / "server" / "market_watch.py")
        collector = load_module("palm_event_watch_sources", SITE_ROOT / "server" / "event_watch.py")
        try:
            previous = watch.load_json(LIVE_ROOT / "market_watch.json")
        except (OSError, ValueError, json.JSONDecodeError):
            previous = {}
        events, sources = collector.collect_all(
            watch,
            now,
            mx_api_key=env_value("MX_APIKEY"),
            htfc_base_url=env_value("HTFC_BASE_URL"),
            htfc_api_key=env_value("HTFC_API_KEY"),
        )
        payload = merge_snapshot(watch, previous, events, sources, now)
        LIVE_ROOT.mkdir(parents=True, exist_ok=True)
        watch.atomic_write(LIVE_ROOT / "market_watch.json", payload)
        states = {item["name"]: item["state"] for item in sources}
        print(json.dumps({"status": "ready", "event_count": len(events), "sources": states, "events_updated_at": payload["events_updated_at"]}, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc), "retry": True}, ensure_ascii=False))
        return 2
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

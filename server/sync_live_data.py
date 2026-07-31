#!/usr/bin/env python3
"""Atomically synchronize API datasets into the server live-data directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
MARKET_READY_MARKER = ".server-market-ready.json"
AI_READY_MARKER = ".server-ai-ready.json"
SUPPLY_READY_MARKER = ".server-supply-ready.json"
# Backwards-compatible name for callers that only know about market ownership.
READY_MARKER = MARKET_READY_MARKER
UPSTREAM_PATHS = (
    "reports.json",
    "forecast/metrics/latest.json",
)
SUPPLY_PATHS = ("supply-demand.json",)
MARKET_PATHS = (
    "oil_futures.js",
    "oil_futures.json",
    "exchange_futures.js",
    "exchange_futures.json",
    "quant_model_signals.js",
    "quant_model_signals.json",
    "contracts/current_contracts.json",
)
AI_PATHS = (
    "market_assistant_brief.json",
)
JSON_PATHS = {
    "reports.json",
    "supply-demand.json",
    "forecast/metrics/latest.json",
    "oil_futures.json",
    "exchange_futures.json",
    "quant_model_signals.json",
    "contracts/current_contracts.json",
    "market_assistant_brief.json",
}


class SyncError(RuntimeError):
    """Raised when a required live dataset cannot be safely synchronized."""


def validate_relative(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise SyncError(f"unsafe relative path: {relative}")
    return path


def validate_payload(path: Path, relative: str) -> None:
    if relative not in JSON_PATHS:
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid JSON payload: {relative}") from exc
    if relative == "reports.json":
        if not isinstance(payload, list):
            raise SyncError("reports.json must contain a JSON array")
    elif not isinstance(payload, dict):
        raise SyncError(f"{relative} must contain a JSON object")


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def synchronize_paths(
    source_root: Path,
    target_root: Path,
    paths: tuple[str, ...],
    *,
    required: bool,
) -> list[str]:
    candidates: list[tuple[str, Path, Path]] = []
    for relative in paths:
        safe_relative = validate_relative(relative)
        source = source_root / safe_relative
        if not source.is_file():
            if required:
                raise SyncError(f"required dataset is missing: {relative}")
            continue
        validate_payload(source, relative)
        candidates.append((relative, source, target_root / safe_relative))
    copied: list[str] = []
    for relative, source, target in candidates:
        atomic_copy(source, target)
        copied.append(relative)
    return copied


def write_marker(
    target_root: Path,
    marker_name: str,
    *,
    session: str,
    owner: str,
) -> None:
    target = target_root / marker_name
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        "session": session,
        "owner": owner,
    }
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def sync_upstream(source_root: Path, target_root: Path) -> dict[str, object]:
    market_owned = (target_root / MARKET_READY_MARKER).exists()
    ai_owned = (target_root / AI_READY_MARKER).exists()
    supply_owned = (target_root / SUPPLY_READY_MARKER).exists()
    requested = UPSTREAM_PATHS
    if not supply_owned:
        requested += SUPPLY_PATHS
    if not market_owned:
        requested += MARKET_PATHS
    if not ai_owned:
        requested += AI_PATHS
    synchronized = synchronize_paths(
        source_root,
        target_root,
        requested,
        required=True,
    )
    offset = len(UPSTREAM_PATHS)
    copied = synchronized[:offset]
    bootstrapped = []
    supply_copied = []
    if not supply_owned:
        supply_copied = synchronized[offset : offset + len(SUPPLY_PATHS)]
        offset += len(SUPPLY_PATHS)
    if not market_owned:
        bootstrapped = synchronized[offset : offset + len(MARKET_PATHS)]
        offset += len(MARKET_PATHS)
    ai_copied = [] if ai_owned else synchronized[offset : offset + len(AI_PATHS)]
    return {
        "status": "ok",
        "mode": "upstream",
        "copied": copied,
        "supply_copied": supply_copied,
        "bootstrapped": bootstrapped,
        "ai_copied": ai_copied,
        "server_supply_owned": supply_owned,
        "server_market_owned": market_owned,
        "server_ai_owned": ai_owned,
    }


def sync_market(
    source_root: Path,
    target_root: Path,
    *,
    session: str,
) -> dict[str, object]:
    copied = synchronize_paths(
        source_root,
        target_root,
        MARKET_PATHS,
        required=True,
    )
    write_marker(
        target_root,
        MARKET_READY_MARKER,
        session=session,
        owner="server-market-collector",
    )
    return {
        "status": "ok",
        "mode": "market",
        "session": session,
        "copied": copied,
        "server_market_owned": True,
    }


def sync_ai(
    source_root: Path,
    target_root: Path,
    *,
    session: str,
) -> dict[str, object]:
    copied = synchronize_paths(
        source_root,
        target_root,
        AI_PATHS,
        required=True,
    )
    write_marker(
        target_root,
        AI_READY_MARKER,
        session=session,
        owner="server-ai-brief",
    )
    return {
        "status": "ok",
        "mode": "ai",
        "session": session,
        "copied": copied,
        "server_ai_owned": True,
    }


def sync_supply(
    source_root: Path,
    target_root: Path,
    *,
    session: str,
) -> dict[str, object]:
    copied = synchronize_paths(
        source_root,
        target_root,
        SUPPLY_PATHS,
        required=True,
    )
    write_marker(
        target_root,
        SUPPLY_READY_MARKER,
        session=session,
        owner="server-supply-collector",
    )
    return {
        "status": "ok",
        "mode": "supply",
        "session": session,
        "copied": copied,
        "server_supply_owned": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("upstream", "market", "ai", "supply"),
        required=True,
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--session", default="manual")
    args = parser.parse_args()
    source_root = args.source.resolve()
    target_root = args.target.resolve()
    try:
        if args.mode == "upstream":
            payload = sync_upstream(source_root, target_root)
        elif args.mode == "market":
            payload = sync_market(
                source_root,
                target_root,
                session=args.session,
            )
        elif args.mode == "ai":
            payload = sync_ai(
                source_root,
                target_root,
                session=args.session,
            )
        else:
            payload = sync_supply(
                source_root,
                target_root,
                session=args.session,
            )
    except (OSError, SyncError) as exc:
        print(
            json.dumps(
                {"status": "error", "mode": args.mode, "reason": str(exc)},
                ensure_ascii=False,
            )
        )
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

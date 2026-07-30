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
READY_MARKER = ".server-market-ready.json"
UPSTREAM_PATHS = (
    "reports.json",
    "supply-demand.json",
    "forecast/metrics/latest.json",
)
MARKET_PATHS = (
    "oil_futures.js",
    "oil_futures.json",
    "exchange_futures.js",
    "exchange_futures.json",
    "quant_model_signals.js",
    "quant_model_signals.json",
    "contracts/current_contracts.json",
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


def write_marker(target_root: Path, session: str) -> None:
    target = target_root / READY_MARKER
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        "session": session,
        "owner": "server-market-collector",
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
    if not (target_root / READY_MARKER).exists():
        synchronized = synchronize_paths(
            source_root,
            target_root,
            UPSTREAM_PATHS + MARKET_PATHS,
            required=True,
        )
        copied = synchronized[: len(UPSTREAM_PATHS)]
        bootstrapped = synchronized[len(UPSTREAM_PATHS) :]
    else:
        copied = synchronize_paths(
            source_root,
            target_root,
            UPSTREAM_PATHS,
            required=True,
        )
        bootstrapped = []
    return {
        "status": "ok",
        "mode": "upstream",
        "copied": copied,
        "bootstrapped": bootstrapped,
        "server_market_owned": (target_root / READY_MARKER).exists(),
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
    write_marker(target_root, session)
    return {
        "status": "ok",
        "mode": "market",
        "session": session,
        "copied": copied,
        "server_market_owned": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("upstream", "market"), required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--session", default="manual")
    args = parser.parse_args()
    source_root = args.source.resolve()
    target_root = args.target.resolve()
    try:
        payload = (
            sync_upstream(source_root, target_root)
            if args.mode == "upstream"
            else sync_market(
                source_root,
                target_root,
                session=args.session,
            )
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

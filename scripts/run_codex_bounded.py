#!/usr/bin/env python3
"""Run one unattended Codex job with a hard wall-clock deadline."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
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
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def terminate_group(process: subprocess.Popen[str], grace_seconds: int = 10) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait()


def run(command: list[str], prompt: str, timeout_seconds: int, status_file: Path) -> int:
    started = datetime.now(SHANGHAI)
    base = {
        "schema_version": 1,
        "started_at": started.isoformat(timespec="seconds"),
        "timeout_seconds": timeout_seconds,
    }
    atomic_write_json(status_file, {**base, "status": "running"})
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            start_new_session=True,
        )
    except OSError as exc:
        atomic_write_json(
            status_file,
            {
                **base,
                "status": "start_error",
                "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
                "reason": str(exc),
            },
        )
        return 127

    try:
        process.communicate(input=prompt, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        terminate_group(process)
        atomic_write_json(
            status_file,
            {
                **base,
                "status": "timeout",
                "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
                "exit_code": 124,
            },
        )
        print(
            json.dumps(
                {"status": "timeout", "timeout_seconds": timeout_seconds},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 124

    return_code = int(process.returncode or 0)
    atomic_write_json(
        status_file,
        {
            **base,
            "status": "ok" if return_code == 0 else "failed",
            "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            "exit_code": return_code,
        },
    )
    return return_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--status-file", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command is required after --")
    if args.timeout_seconds < 1:
        parser.error("--timeout-seconds must be positive")
    return run(
        command,
        sys.stdin.read(),
        args.timeout_seconds,
        args.status_file.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())

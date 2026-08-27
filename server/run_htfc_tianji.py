#!/usr/bin/env python3
"""Refresh read-only HTFC Tianji evidence into the live API data mount."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")


def load_sync(site_root: Path):
    path = site_root / "server" / "sync_live_data.py"
    spec = importlib.util.spec_from_file_location("palm_sync_live_data", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("live-data sync module is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)))
    parser.add_argument("--live-data-root", type=Path, default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)))
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    site_root = args.site_root.resolve()
    live_data_root = args.live_data_root.resolve()
    try:
        sync = load_sync(site_root)
        with tempfile.TemporaryDirectory(prefix="server-htfc-tianji.") as temporary:
            output_root = Path(temporary)
            output = output_root / "htfc_tianji.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(site_root / "scripts" / "update_htfc_tianji_data.py"),
                    "--output",
                    str(output),
                    "--timeout",
                    str(args.timeout),
                ],
                cwd=site_root,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=max(args.timeout * 8, 120),
                check=False,
            )
            if result.returncode != 0 or not output.is_file():
                raise RuntimeError("Tianji collector did not produce a dataset")
            payload = json.loads(output.read_text(encoding="utf-8"))
            if not payload.get("available_modules"):
                raise RuntimeError("no authorized Tianji module returned usable data")
            research_output = output_root / "research_watch.json"
            research_result = subprocess.run(
                [
                    sys.executable,
                    str(site_root / "scripts" / "build_research_watch.py"),
                    "--input",
                    str(output),
                    "--existing",
                    str(live_data_root / "research_watch.json"),
                    "--output",
                    str(research_output),
                ],
                cwd=site_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=30,
                check=False,
            )
            if research_result.returncode != 0 or not research_output.is_file():
                raise RuntimeError("research watch builder did not produce a dataset")
            copied = sync.sync_htfc(output_root, live_data_root, session="scheduled")
        print(json.dumps({
            "status": payload.get("status"),
            "generated_at": payload.get("generated_at"),
            "available_modules": payload.get("available_modules"),
            "copied": copied.get("copied", []),
        }, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)[:300], "retry": True}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

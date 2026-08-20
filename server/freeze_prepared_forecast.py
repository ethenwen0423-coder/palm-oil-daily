#!/usr/bin/env python3
"""Freeze a daily forecast from already validated server-owned market data."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PreparedForecastError(RuntimeError):
    """Raised when the prepared market snapshot cannot be frozen."""


def load_update_module():
    script = ROOT / "scripts" / "update_oil_futures_data.py"
    # The updater imports sibling scripts by their module name.  Loading it via
    # importlib from ``server/`` otherwise omits that sibling directory from
    # Python's module search path in the unattended server runtime.
    scripts_dir = str(script.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("prepared_forecast_update", script)
    if spec is None or spec.loader is None:
        raise PreparedForecastError(f"cannot load forecast integration: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def freeze(report_date: str, oil_futures: Path) -> dict[str, object]:
    update = load_update_module()
    metadata = update.load_forecast_time_metadata(report_date)
    update.run_data_quality_gate(oil_futures)
    result = update.run_forecast_recorder(oil_futures, metadata)
    metadata_path = update.write_forecast_time_metadata(metadata)
    return {
        "status": "ok",
        "report_date": report_date,
        "forecast": result.get("forecast"),
        "already_exists": bool(result.get("already_exists")),
        "forecast_time_metadata": str(metadata_path.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--oil-futures", type=Path, default=ROOT / "data" / "oil_futures.js")
    args = parser.parse_args()
    try:
        payload = freeze(args.report_date, args.oil_futures.resolve())
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

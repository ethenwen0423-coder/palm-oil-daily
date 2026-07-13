#!/usr/bin/env python3
"""Validate a daily forecast-schema-v1 JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from forecast_schema import validate_forecast


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecast", required=True, type=Path, help="Path to data/forecast/daily/YYYY-MM-DD.json")
    args = parser.parse_args()

    try:
        payload = json.loads(args.forecast.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result = {"status": "error", "can_evaluate": False, "errors": [f"文件不存在：{args.forecast}"], "warnings": []}
    except json.JSONDecodeError as exc:
        result = {"status": "error", "can_evaluate": False, "errors": [f"JSON 无法解析：{exc}"], "warnings": []}
    except OSError as exc:
        result = {"status": "error", "can_evaluate": False, "errors": [f"文件无法读取：{exc}"], "warnings": []}
    else:
        result = validate_forecast(payload)

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

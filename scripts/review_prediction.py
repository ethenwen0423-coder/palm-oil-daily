#!/usr/bin/env python3
"""Run daily oil-futures prediction review after the night session close."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SHANGHAI = ZoneInfo("Asia/Shanghai")
OFFICIAL_TAB = ROOT / "data" / "oil_futures.js"
SNAPSHOT_DIR = ROOT / "data" / "review" / "snapshots"
DAILY_REVIEW_DIR = ROOT / "data" / "review" / "daily"
LATEST_REVIEW = ROOT / "data" / "review" / "latest_review.json"
UPDATE_SCRIPT = ROOT / "scripts" / "update_oil_futures_data.py"
REVIEW_SCRIPT = ROOT / "skills" / "daily_review_skill" / "scripts" / "daily_review.py"


def today_string(override: str | None = None) -> str:
    return override or datetime.now(SHANGHAI).strftime("%Y-%m-%d")


def is_weekday(date_text: str) -> bool:
    return datetime.strptime(date_text, "%Y-%m-%d").weekday() < 5


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Review date, YYYY-MM-DD. Defaults to today in Asia/Shanghai.")
    parser.add_argument("--force", action="store_true", help="Run even on weekends.")
    args = parser.parse_args()

    review_date = today_string(args.date)
    if not args.force and not is_weekday(review_date):
        print(json.dumps({"date": review_date, "status": "skipped", "reason": "非工作日不运行夜盘复盘"}, ensure_ascii=False))
        return 0

    if not OFFICIAL_TAB.exists():
        print(json.dumps({"date": review_date, "status": "failed", "reason": "缺少 data/oil_futures.js，无法提取昨日判断"}, ensure_ascii=False))
        return 2
    if not UPDATE_SCRIPT.exists() or not REVIEW_SCRIPT.exists():
        print(json.dumps({"date": review_date, "status": "failed", "reason": "复盘依赖脚本缺失"}, ensure_ascii=False))
        return 2

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    previous_snapshot = SNAPSHOT_DIR / f"{review_date}-previous-oil_futures.js"
    current_snapshot = SNAPSHOT_DIR / f"{review_date}-actual-oil_futures.js"
    previous_snapshot.write_text(OFFICIAL_TAB.read_text(encoding="utf-8"), encoding="utf-8")

    update = run_command([sys.executable, str(UPDATE_SCRIPT), "--output", str(current_snapshot)])
    if update.returncode != 0:
        print(json.dumps({"date": review_date, "status": "failed", "stage": "current_market_snapshot", "stderr": update.stderr.strip(), "stdout": update.stdout.strip()}, ensure_ascii=False))
        return update.returncode

    review = run_command(
        [
            sys.executable,
            str(REVIEW_SCRIPT),
            "--previous",
            str(previous_snapshot),
            "--current",
            str(current_snapshot),
            "--date",
            review_date,
            "--output-dir",
            str(DAILY_REVIEW_DIR),
        ]
    )
    if review.returncode != 0:
        print(json.dumps({"date": review_date, "status": "failed", "stage": "daily_review_skill", "stderr": review.stderr.strip(), "stdout": review.stdout.strip()}, ensure_ascii=False))
        return review.returncode

    try:
        payload = json.loads(review.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"date": review_date, "status": "failed", "stage": "parse_review", "stdout": review.stdout.strip()}, ensure_ascii=False))
        return 2

    result = {
        "date": review_date,
        "status": "ok",
        "previous_snapshot": str(previous_snapshot),
        "current_snapshot": str(current_snapshot),
        "learning_notes_path": payload.get("learning_notes_path"),
        "review_memory": payload.get("review_memory", {}),
        "review_result": payload.get("review_result", []),
        "error_type": payload.get("error_type", []),
        "suggested_improvement": payload.get("suggested_improvement", []),
        "whether_update_rule": payload.get("whether_update_rule", False),
        "human_approval_required": payload.get("human_approval_required", False),
    }
    LATEST_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    LATEST_REVIEW.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

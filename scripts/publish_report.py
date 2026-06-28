#!/usr/bin/env python3
"""Collect Markdown reports and publish them as static site data."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DATA_FILE = ROOT / "data" / "reports.js"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def extract_title(content: str, date: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return f"{date} 棕榈油行情日报"


def extract_summary(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("- "):
            return line[2:].strip()
    return "棕榈油行情日报"


def main() -> None:
    reports = []
    for path in sorted(REPORTS_DIR.glob("*.md"), reverse=True):
        if path.name == "README.md":
            continue
        date = path.stem
        if not DATE_RE.match(date):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        reports.append(
            {
                "date": date,
                "title": extract_title(content, date),
                "summary": extract_summary(content),
                "updated_at": datetime.fromtimestamp(path.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "content": content,
            }
        )

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(reports, ensure_ascii=False, indent=2)
    DATA_FILE.write_text(f"window.PALM_OIL_REPORTS = {payload};\n", encoding="utf-8")
    print(f"published {len(reports)} report(s) to {DATA_FILE}")


if __name__ == "__main__":
    main()

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
VERSION_FILE = ROOT / "data" / "version.js"
DOWNLOADS_DIR = ROOT / "downloads"
REPORT_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?P<suffix>-weekend)?$")


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


def extract_headline(content: str, fallback: str) -> str:
    lines = [line.strip() for line in content.splitlines()]
    for index, line in enumerate(lines):
        if line.startswith("##") and ("一句话核心观点" in line or "今日观点" in line):
            for row in lines[index + 1 :]:
                if row.startswith("##"):
                    break
                if row and not row.startswith("【结论】"):
                    return row
    for index, line in enumerate(lines):
        if line.startswith("|") and "结论" in line and "驱动" in line:
            for row in lines[index + 2 :]:
                if not row.startswith("|"):
                    break
                cells = [cell.strip() for cell in row.strip("|").split("|")]
                if len(cells) >= 2 and cells[1] and "---" not in cells[1]:
                    return cells[1]
    summary = extract_summary(content)
    return summary if summary != "棕榈油行情日报" else fallback


def main() -> None:
    reports = []
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(REPORTS_DIR.glob("*.md"), reverse=True):
        if path.name == "README.md":
            continue
        match = REPORT_RE.match(path.stem)
        if not match:
            continue
        date = match.group("date")
        suffix = match.group("suffix") or ""
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        report_id = f"{date}{suffix}"
        download_name = f"{report_id}.md"
        (DOWNLOADS_DIR / download_name).write_text(content + "\n", encoding="utf-8")
        reports.append(
            {
                "date": report_id,
                "title": extract_title(content, date),
                "headline": extract_headline(content, extract_title(content, date)),
                "summary": extract_summary(content),
                "kind": "weekend" if suffix else "daily",
                "download": f"downloads/{download_name}",
                "updated_at": datetime.fromtimestamp(path.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "content": content,
            }
        )

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(reports, ensure_ascii=False, indent=2)
    DATA_FILE.write_text(f"window.PALM_OIL_REPORTS = {payload};\n", encoding="utf-8")
    version = int(max((path.stat().st_mtime for path in REPORTS_DIR.glob("*.md")), default=datetime.now().timestamp()))
    VERSION_FILE.write_text(f"window.PALM_OIL_DATA_VERSION = '{version}';\n", encoding="utf-8")
    print(f"published {len(reports)} report(s) to {DATA_FILE}")


if __name__ == "__main__":
    main()

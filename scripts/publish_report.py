#!/usr/bin/env python3
"""Collect Markdown reports and publish them as static site data."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from sync_miniprogram_data import publish_dataset


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DATA_FILE = ROOT / "data" / "reports.js"
VERSION_FILE = ROOT / "data" / "version.js"
DOWNLOADS_DIR = ROOT / "downloads"
QUALITY_DIR = ROOT / "data" / "report_quality"
REPORT_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?P<suffix>-weekend)?$")


def extract_title(content: str, date: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return f"{date} 油脂行情日报"


def extract_summary(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("- "):
            return line[2:].strip()
    return "油脂行情日报"


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
    return summary if summary != "油脂行情日报" else fallback


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        run_kind = "weekend" if suffix else "daily"
        quality_source = ROOT / "source_runs" / f"{date}-{run_kind}" / "report_quality.json"
        quality_summary = None
        if quality_source.is_file():
            quality = json.loads(quality_source.read_text(encoding="utf-8"))
            if not isinstance(quality, dict) or quality.get("can_publish") is not True:
                raise RuntimeError(f"report quality is not publishable: {quality_source}")
            QUALITY_DIR.mkdir(parents=True, exist_ok=True)
            (QUALITY_DIR / f"{report_id}.json").write_text(
                json.dumps(quality, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            run_root = quality_source.parent
            source_json = run_root / "raw" / (
                "futures_market_data.weekly_compatible.json"
                if run_kind == "weekend"
                else "futures_market_data.json"
            )
            if not source_json.is_file():
                source_json = run_root / "raw" / "futures_market_data.json"
            artifacts = {
                "report_sha256": sha256_file(path),
                "quality_sha256": sha256_file(quality_source),
            }
            for label, artifact in (
                ("outline_sha256", run_root / "report_outline.json"),
                ("source_sha256", source_json),
            ):
                if artifact.is_file():
                    artifacts[label] = sha256_file(artifact)
            quality_summary = {
                "status": quality.get("status"),
                "can_publish": quality.get("can_publish"),
                "score": quality.get("score"),
                "minimum_score": quality.get("minimum_score"),
                "source_run": f"source_runs/{date}-{run_kind}",
                "artifacts": artifacts,
            }
        download_name = f"{report_id}.md"
        (DOWNLOADS_DIR / download_name).write_text(content + "\n", encoding="utf-8")
        item = {
            "date": report_id,
            "title": extract_title(content, date),
            "headline": extract_headline(content, extract_title(content, date)),
            "summary": extract_summary(content),
            "kind": run_kind,
            "download": f"downloads/{download_name}",
            "updated_at": datetime.fromtimestamp(path.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M"
            ),
            "content": content,
        }
        if quality_summary is not None:
            item["quality"] = quality_summary
        reports.append(item)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(reports, ensure_ascii=False, indent=2)
    DATA_FILE.write_text(f"window.PALM_OIL_REPORTS = {payload};\n", encoding="utf-8")
    publish_dataset("reports", reports)
    version = int(max((path.stat().st_mtime for path in REPORTS_DIR.glob("*.md")), default=datetime.now().timestamp()))
    VERSION_FILE.write_text(f"window.PALM_OIL_DATA_VERSION = '{version}';\n", encoding="utf-8")
    print(f"published {len(reports)} report(s) to website and mini-program data")


if __name__ == "__main__":
    main()

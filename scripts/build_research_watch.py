#!/usr/bin/env python3
"""Build a once-daily, deduplicated public research recommendation feed."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
OIL_KEYS = {"P", "Y", "OI"}
CROSS_KEYS = {"SC", "MACRO"}


def load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def rows_for(payload: dict[str, Any], product: str) -> list[dict[str, Any]]:
    response = payload.get("modules", {}).get("research_reports", {}).get("products", {}).get(product, {}).get("response", {})
    data = response.get("data", {}) if isinstance(response, dict) else {}
    rows = data.get("resultList", []) if isinstance(data, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def published_date(row: dict[str, Any]) -> date | None:
    raw = str(row.get("publishDateTime") or row.get("showDate") or row.get("publish_date") or "")[:10]
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def normalize_item(row: dict[str, Any], sector: str, product: str) -> dict[str, Any]:
    title = str(row.get("title") or "公开研报").strip()[:120]
    summary = str(row.get("aiContent") or row.get("brief") or "").strip()[:240]
    published = str(row.get("publishDateTime") or row.get("showDate") or "时间待核验")
    topics = [part.strip() for part in str(row.get("subclassCodeName") or product).split(",") if part.strip()]
    return {
        "id": str(row.get("id") or f"{product}:{published}:{title}"),
        "title": title,
        "summary": summary or "机构公开晨报已更新，请结合原文与市场数据核验。",
        "organization": str(row.get("author") or "机构研究"),
        "published_at": published,
        "sector": sector,
        "topics": topics[:4],
        "recommendation_score": 85 if sector == "油脂油料" else 75,
        "recommendation_reason": "当日发布；与油脂直接相关" if sector == "油脂油料" else "当日或近期发布；属于油脂定价的跨板块驱动",
        "source": "机构公开研报接口",
    }


def select(payload: dict[str, Any], report_date: date) -> tuple[list[dict[str, Any]], int]:
    seen: set[str] = set()
    oil: list[dict[str, Any]] = []
    cross: list[dict[str, Any]] = []
    candidate_count = 0
    for product in (*sorted(OIL_KEYS), *sorted(CROSS_KEYS)):
        sector = "油脂油料" if product in OIL_KEYS else "跨板块"
        for row in rows_for(payload, product):
            candidate_count += 1
            published = published_date(row)
            if published is None or (report_date - published).days < 0 or (report_date - published).days > 30:
                continue
            key = str(row.get("id") or "") or f"{row.get('title')}|{published}"
            if key in seen:
                continue
            seen.add(key)
            item = normalize_item(row, sector, product)
            (oil if sector == "油脂油料" else cross).append(item)
    oil.sort(key=lambda item: item["published_at"], reverse=True)
    cross.sort(key=lambda item: item["published_at"], reverse=True)
    return oil[:7] + cross[:3], candidate_count


def build(source: Path, existing: Path | None, now: datetime) -> dict[str, Any]:
    today = now.astimezone(SHANGHAI).date()
    previous = load_object(existing) if existing and existing.is_file() else {}
    if previous.get("status") == "ready" and previous.get("report_date") == today.isoformat():
        return previous
    payload = load_object(source)
    items, candidate_count = select(payload, today)
    if any(str(item.get("published_at", "")).startswith(today.isoformat()) for item in items):
        oil_count = sum(item["sector"] == "油脂油料" for item in items)
        cross_count = sum(item["sector"] == "跨板块" for item in items)
        return {
            "schema_version": 1,
            "status": "ready",
            "report_date": today.isoformat(),
            "generated_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
            "refresh_policy": "独立机构研报采集兜底；每日首次发现当日研报后冻结",
            "candidate_count": candidate_count,
            "deduplicated_count": len(items),
            "allocation": {"油脂油料": oil_count, "跨板块": cross_count, "target": "70% / 30%"},
            "items": items,
            "notice": "推荐用于研究筛选，不构成投资建议。",
        }
    if previous:
        return previous
    return {
        "schema_version": 1,
        "status": "pending",
        "report_date": None,
        "generated_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
        "refresh_policy": "独立机构研报采集兜底；每日首次发现当日研报后冻结",
        "items": [],
        "notice": "等待当日公开晨报发布。",
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.input, args.existing, datetime.now(SHANGHAI))
    atomic_write(args.output, payload)
    print(json.dumps({"status": payload["status"], "report_date": payload.get("report_date"), "items": len(payload.get("items", []))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a once-daily, deduplicated public research recommendation feed."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
OIL_KEYS = {"P", "Y", "OI"}
CROSS_KEYS = {"SC", "MACRO"}


def public_text(value: Any) -> str:
    text = str(value or "")
    text = text.replace("华泰期货", "研报服务").replace("华泰", "研报服务").replace("天玑", "研报服务")
    text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    return re.sub(r"\s+", " ", text).strip()


def dedupe_key(item: dict[str, Any]) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]", "", str(item.get("title", "")).lower())


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
    title = public_text(row.get("title") or "公开研报").strip()[:120]
    summary = public_text(row.get("aiContent") or row.get("brief") or "").strip()[:240]
    published = str(row.get("publishDateTime") or row.get("showDate") or "时间待核验")
    topics = [part.strip() for part in str(row.get("subclassCodeName") or product).split(",") if part.strip()]
    return {
        "id": str(row.get("id") or f"{product}:{published}:{title}"),
        "title": title,
        "summary": summary or "机构公开晨报已更新，请结合原文与市场数据核验。",
        "organization": public_text(row.get("author") or "研报服务"),
        "published_at": published,
        "sector": sector,
        "topics": topics[:4],
        "recommendation_score": 85 if sector == "油脂油料" else 75,
        "recommendation_reason": "当日发布；与油脂直接相关" if sector == "油脂油料" else "当日或近期发布；属于油脂定价的跨板块驱动",
        "source": "研报服务（机构接口）",
        "source_channel": "institution-report-skill",
        "source_priority": 2,
    }


def public_search_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_object(path)
        data = payload.get("data", [])
        if isinstance(data, list):
            rows.extend(row for row in data if isinstance(row, dict))
    return rows


def normalize_public_search_item(row: dict[str, Any]) -> dict[str, Any]:
    title = public_text(row.get("title") or "公开研报").strip()[:120]
    combined = f"{title} {row.get('summary') or ''}"
    oil_terms = ("棕榈油", "豆油", "菜油", "油脂", "油料", "大豆", "豆粕", "菜粕")
    sector = "油脂油料" if any(term in combined for term in oil_terms) else "跨板块"
    extra = row.get("extra") if isinstance(row.get("extra"), dict) else {}
    topics = extra.get("cat_names") if isinstance(extra.get("cat_names"), list) else []
    published = str(row.get("publish_date") or row.get("publish_time") or "时间待核验")
    return {
        "id": str(row.get("uid") or row.get("id") or f"public:{published}:{title}"),
        "title": title,
        "summary": public_text(row.get("summary") or "公开研报搜索结果，请结合原文核验。").strip()[:240],
        "organization": public_text(extra.get("organization") or "公开研究机构"),
        "published_at": published,
        "sector": sector,
        "topics": [str(topic) for topic in topics[:4]],
        "recommendation_score": 80 if sector == "油脂油料" else 70,
        "recommendation_reason": "公开研报搜索命中；与油脂直接相关" if sector == "油脂油料" else "公开研报搜索命中；属于跨板块驱动",
        "source": "同花顺问财财经资讯搜索（研究报告）",
        "source_channel": "report-search",
        "source_priority": 1,
        "url": str(row.get("url") or ""),
    }


def select(payload: dict[str, Any], report_date: date, public_paths: list[Path] | None = None) -> tuple[list[dict[str, Any]], int, dict[str, int], dict[str, int]]:
    candidates: list[dict[str, Any]] = []
    oil: list[dict[str, Any]] = []
    cross: list[dict[str, Any]] = []
    candidate_count = 0
    candidate_source_counts = {"institution-report-skill": 0, "report-search": 0}
    for product in (*sorted(OIL_KEYS), *sorted(CROSS_KEYS)):
        sector = "油脂油料" if product in OIL_KEYS else "跨板块"
        for row in rows_for(payload, product):
            candidate_count += 1
            candidate_source_counts["institution-report-skill"] += 1
            published = published_date(row)
            if published is None or (report_date - published).days < 0 or (report_date - published).days > 30:
                continue
            candidates.append(normalize_item(row, sector, product))
    web_rows = public_search_rows(public_paths or [])
    candidate_count += len(web_rows)
    candidate_source_counts["report-search"] += len(web_rows)
    for row in web_rows:
        item = normalize_public_search_item(row)
        published = published_date({"publish_date": item["published_at"]})
        if published is None or (report_date - published).days < 0 or (report_date - published).days > 30:
            continue
        candidates.append(item)
    candidates.sort(key=lambda item: (item["source_priority"], item["published_at"]), reverse=True)
    seen: set[str] = set()
    for item in candidates:
        key = dedupe_key(item)
        if not key or key in seen:
            continue
        seen.add(key)
        item.pop("source_priority", None)
        (oil if item["sector"] == "油脂油料" else cross).append(item)
    oil.sort(key=lambda item: item["published_at"], reverse=True)
    cross.sort(key=lambda item: item["published_at"], reverse=True)
    selected = oil[:7] + cross[:3]
    selected_counts: dict[str, int] = {}
    for item in selected:
        selected_counts[item["source_channel"]] = selected_counts.get(item["source_channel"], 0) + 1
    return selected, candidate_count, candidate_source_counts, selected_counts


def build(source: Path, existing: Path | None, now: datetime, public_paths: list[Path] | None = None) -> dict[str, Any]:
    today = now.astimezone(SHANGHAI).date()
    previous = load_object(existing) if existing and existing.is_file() else {}
    if previous.get("schema_version") == 2 and previous.get("status") == "ready" and previous.get("report_date") == today.isoformat():
        return previous
    payload = load_object(source)
    items, candidate_count, candidate_source_counts, source_counts = select(payload, today, public_paths)
    if any(str(item.get("published_at", "")).startswith(today.isoformat()) for item in items):
        oil_count = sum(item["sector"] == "油脂油料" for item in items)
        cross_count = sum(item["sector"] == "跨板块" for item in items)
        return {
            "schema_version": 2,
            "status": "ready",
            "report_date": today.isoformat(),
            "generated_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
            "refresh_policy": "独立机构研报采集兜底；每日首次发现当日研报后冻结",
            "candidate_count": candidate_count,
            "candidate_source_counts": candidate_source_counts,
            "deduplicated_count": len(items),
            "allocation": {"油脂油料": oil_count, "跨板块": cross_count, "target": "70% / 30%"},
            "source_counts": source_counts,
            "source_policy": "研报服务机构接口优先；同花顺问财公开研报搜索补充；跨源标题去重",
            "items": items,
            "notice": "推荐用于研究筛选，不构成投资建议。",
        }
    if previous:
        return previous
    return {
        "schema_version": 2,
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
    parser.add_argument("--public-search", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.input, args.existing, datetime.now(SHANGHAI), args.public_search)
    atomic_write(args.output, payload)
    print(json.dumps({"status": payload["status"], "report_date": payload.get("report_date"), "items": len(payload.get("items", []))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

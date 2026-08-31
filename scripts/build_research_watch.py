#!/usr/bin/env python3
"""Build a frequently rescanned, deduplicated research recommendation feed."""

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
READING_NOTICE = "以下分类与选择由AI基于所列来源摘要生成，所列文字来自来源摘要；不代表任何来源方官方立场，也不构成投资建议，请自行核验。"
SECTION_MARKERS = (
    ("core", re.compile(r"核心观点|核心结论|主要观点|观点摘要|关键结论|结论")),
    ("strategy", re.compile(r"策略建议|投资建议|操作建议|交易建议|后市展望")),
    ("risk", re.compile(r"风险提示|风险因素|主要风险")),
)


def public_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    return re.sub(r"\s+", " ", text).strip()


def source_url(row: dict[str, Any]) -> str:
    """Return only a directly usable source URL; never fabricate one from an id."""
    keys = (
        "link_url", "linkUrl", "url", "source_url", "sourceUrl",
        "pdf_url", "pdfUrl", "attachment_url", "attachmentUrl",
    )
    containers: list[dict[str, Any]] = [row]
    for name in ("attachment", "extra", "resource"):
        value = row.get(name)
        if isinstance(value, dict):
            containers.append(value)
    for container in containers:
        for key in keys:
            value = str(container.get(key) or "").strip()
            if re.match(r"^https?://", value, re.IGNORECASE):
                return value
    return ""


def complete_clauses(value: str) -> list[str]:
    text = public_text(value)
    if not text:
        return []
    clauses = [part.strip() for part in re.findall(r".+?(?:[。！？；]|[!?;](?=\s|$)|$)", text) if part.strip()]
    return clauses or [text]


def numbered_points(value: str) -> list[str]:
    text = public_text(value)
    if not text:
        return []
    markers = list(re.finditer(r"(?:^|\s)(?:\d{1,2}[.、)]|[（(]\d{1,2}[）)])\s*", text))
    if not markers:
        return complete_clauses(text)
    points: list[str] = []
    prefix = text[:markers[0].start()].strip()
    if prefix:
        points.extend(complete_clauses(prefix))
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        point = text[marker.end():end].strip()
        if point:
            points.append(point)
    return points


def section_points(summary: str) -> dict[str, list[str]]:
    matches: list[tuple[int, int, str]] = []
    for key, pattern in SECTION_MARKERS:
        matches.extend((match.start(), match.end(), key) for match in pattern.finditer(summary))
    matches.sort(key=lambda item: item[0])
    sections = {"core": [], "strategy": [], "risk": []}
    if not matches:
        sections["core"] = numbered_points(summary)
        return sections
    prefix = summary[:matches[0][0]].strip()
    if prefix:
        sections["core"].extend(numbered_points(prefix))
    for index, (_, end, key) in enumerate(matches):
        next_start = matches[index + 1][0] if index + 1 < len(matches) else len(summary)
        sections[key].extend(numbered_points(summary[end:next_start]))
    return sections


def first_complete_clause(points: list[str]) -> str:
    for point in points:
        clauses = complete_clauses(point)
        if clauses:
            return clauses[0]
    return ""


def build_reading_view(summary: str, summary_type: str) -> dict[str, Any]:
    if summary_type == "missing_source_content":
        return {
            "quick_points": [
                {"label": "核心结论", "text": "来源未提供可核验的摘要内容。"},
                {"label": "主要驱动", "text": "来源摘要未提供可独立提取的主要驱动。"},
                {"label": "关键风险", "text": "来源摘要未单列风险，需进一步核验。"},
            ],
            "sections": {"core": [], "strategy": [], "risk": []},
            "reading_notice": READING_NOTICE,
        }
    sections = section_points(summary)
    core = sections["core"]
    strategy = sections["strategy"]
    risk = sections["risk"]
    conclusion = first_complete_clause(core) or first_complete_clause(strategy) or "来源摘要未提供可独立提取的核心结论。"
    driver_terms = ("库存", "供需", "产量", "出口", "进口", "需求", "价格", "成本", "政策", "利率", "汇率", "地缘", "PMI", "天气")
    driver_candidates = [point for point in core if point != core[0] and any(term in point for term in driver_terms)]
    driver = first_complete_clause(driver_candidates) or first_complete_clause(core[1:]) or "来源摘要未提供可独立提取的主要驱动。"
    risk_text = first_complete_clause(risk)
    if not risk_text:
        risk_candidates = [point for point in (*core, *strategy) if any(term in point for term in ("风险", "警惕", "不确定", "冲突", "下行"))]
        risk_text = first_complete_clause(risk_candidates) or "来源摘要未单列风险，需进一步核验。"
    return {
        "quick_points": [
            {"label": "核心结论", "text": conclusion},
            {"label": "主要驱动", "text": driver},
            {"label": "关键风险", "text": risk_text},
        ],
        "sections": sections,
        "reading_notice": READING_NOTICE,
    }


def attach_reading_view(item: dict[str, Any]) -> dict[str, Any]:
    item["reading_view"] = build_reading_view(str(item.get("summary") or ""), str(item.get("summary_type") or "source_summary"))
    return item


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
    title = public_text(row.get("title") or "公开研报").strip()
    ai_summary = public_text(row.get("aiContent") or "").strip()
    source_summary = public_text(row.get("brief") or "").strip()
    summary = ai_summary or source_summary
    published = str(row.get("publishDateTime") or row.get("showDate") or "时间待核验")
    topics = [part.strip() for part in str(row.get("subclassCodeName") or product).split(",") if part.strip()]
    item = {
        "id": str(row.get("id") or f"{product}:{published}:{title}"),
        "title": title,
        "summary": summary or "来源未提供可核验的摘要内容，暂不生成内容性结论。",
        "summary_type": "source_ai_summary" if ai_summary else "source_summary" if source_summary else "missing_source_content",
        "summary_notice": (
            "该摘要为研报服务接口返回的AI内容，保持原文完整展示；不代表来源方官方立场，也不构成投资建议，请自行核验。"
            if ai_summary else
            "该摘要为研报服务接口返回的公开摘要，保持原文完整展示；请结合来源信息自行核验。"
            if source_summary else
            "AI基于来源字段生成信息缺失提示，不代表来源方官方立场，也不构成投资建议；请自行核验。"
        ),
        "organization": public_text(row.get("author") or "机构研究"),
        "published_at": published,
        "sector": sector,
        "topics": topics[:4],
        "source": "机构研报 skill",
        "source_channel": "institution-report-skill",
    }
    url = source_url(row)
    if url:
        item["url"] = url
    return attach_reading_view(item)


def public_search_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_object(path)
        data = payload.get("data", [])
        if isinstance(data, list):
            rows.extend(row for row in data if isinstance(row, dict))
    return rows


def normalize_public_search_item(row: dict[str, Any]) -> dict[str, Any]:
    title = public_text(row.get("title") or "公开研报").strip()
    combined = f"{title} {row.get('summary') or ''}"
    oil_terms = ("棕榈油", "豆油", "菜油", "油脂", "油料", "大豆", "豆粕", "菜粕")
    sector = "油脂油料" if any(term in combined for term in oil_terms) else "跨板块"
    extra = row.get("extra") if isinstance(row.get("extra"), dict) else {}
    topics = extra.get("cat_names") if isinstance(extra.get("cat_names"), list) else []
    published = str(row.get("publish_date") or row.get("publish_time") or "时间待核验")
    summary = public_text(row.get("summary") or "").strip()
    item = {
        "id": str(row.get("uid") or row.get("id") or f"public:{published}:{title}"),
        "title": title,
        "summary": summary or "来源未提供可核验的摘要内容，请通过原始研报链接核验。",
        "summary_type": "source_summary" if summary else "missing_source_content",
        "summary_notice": (
            "该摘要来自同花顺问财公开研报搜索结果，保持原文完整展示；请结合原始研报链接自行核验。"
            if summary else
            "AI基于来源字段生成信息缺失提示，不代表来源方官方立场，也不构成投资建议；请自行核验。"
        ),
        "organization": public_text(extra.get("organization") or "公开研究机构"),
        "published_at": published,
        "sector": sector,
        "topics": [str(topic) for topic in topics[:4]],
        "source": "同花顺问财财经资讯搜索（研究报告）",
        "source_channel": "report-search",
    }
    url = source_url(row)
    if url:
        item["url"] = url
    return attach_reading_view(item)


def mx_search_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_object(path)
        current: Any = payload
        for key in ("data", "data", "llmSearchResponse", "data"):
            current = current.get(key, {}) if isinstance(current, dict) else {}
        if isinstance(current, list):
            rows.extend(row for row in current if isinstance(row, dict) and row.get("informationType") == "REPORT")
    return rows


def normalize_mx_search_item(row: dict[str, Any]) -> dict[str, Any]:
    title = public_text(row.get("title") or "公开研报").strip()
    summary = public_text(row.get("content") or "").strip()
    published = str(row.get("date") or "时间待核验")
    combined = f"{title} {summary}"
    oil_terms = ("棕榈油", "豆油", "菜油", "油脂", "油料", "大豆", "豆粕", "菜粕")
    cross_title_terms = ("原油", "宏观", "汇率", "利率", "航运", "能源")
    title_is_cross = any(term in title for term in cross_title_terms) and not any(term in title for term in oil_terms)
    sector = "跨板块" if title_is_cross else "油脂油料" if any(term in combined for term in oil_terms) else "跨板块"
    topic_terms = oil_terms if sector == "油脂油料" else ("原油", "宏观", "汇率", "利率", "航运", "生物柴油", "政策")
    topics = [term for term in topic_terms if term in combined][:4]
    item = {
        "id": str(row.get("code") or f"mx:{published}:{title}"),
        "title": title,
        "summary": summary or "来源未提供可核验的摘要内容。",
        "summary_type": "source_content" if summary else "missing_source_content",
        "summary_notice": (
            "该内容来自东方财富妙想资讯搜索返回的研报字段，保持来源内容完整展示；请结合原始研报自行核验。"
            if summary else
            "AI基于来源字段生成信息缺失提示，不代表来源方官方立场，也不构成投资建议；请自行核验。"
        ),
        "organization": public_text(row.get("insName") or row.get("author") or "公开研究机构"),
        "published_at": published,
        "sector": sector,
        "topics": topics,
        "source": "东方财富妙想资讯搜索（研究报告）",
        "source_channel": "mx-search",
    }
    return attach_reading_view(item)


def score_quality(item: dict[str, Any], report_date: date) -> tuple[int, list[str]]:
    published = published_date({"publish_date": item.get("published_at")})
    days = (report_date - published).days if published else 30
    score = 35
    factors: list[str] = []
    if days == 0:
        score += 25
        factors.append("当日发布")
    elif days <= 2:
        score += 20
        factors.append("近3日发布")
    elif days <= 7:
        score += 14
        factors.append("近7日发布")
    elif days <= 14:
        score += 8
        factors.append("近14日发布")
    else:
        score += 3
        factors.append("近30日发布")
    title = str(item.get("title") or "")
    summary = str(item.get("summary") or "")
    combined = f"{title} {summary}"
    sector_terms = (
        ("棕榈油", "豆油", "菜油", "油脂", "油料", "大豆", "豆粕", "菜粕")
        if item.get("sector") == "油脂油料"
        else ("原油", "宏观", "汇率", "利率", "航运", "生物柴油", "政策")
    )
    if any(term in combined for term in sector_terms):
        score += 10
        factors.append("主题相关")
    if any(term in title for term in ("日报", "早报", "周报", "月报", "深度", "策略", "展望")):
        score += 5
        factors.append("报告类型明确")
    if len(summary) >= 180:
        score += 12
        factors.append("摘要信息充分")
    elif len(summary) >= 80:
        score += 7
        factors.append("摘要信息较完整")
    elif len(summary) >= 30:
        score += 3
        factors.append("包含有效摘要")
    if len(re.findall(r"\d+(?:\.\d+)?", summary)) >= 3:
        score += 7
        factors.append("包含量化证据")
    if any(term in summary for term in ("风险", "库存", "供需", "产量", "出口", "进口", "基差", "政策")):
        score += 4
        factors.append("包含驱动或风险")
    if item.get("organization") and item.get("topics"):
        score += 2
        factors.append("来源字段完整")
    return min(score, 100), factors


def select(
    payload: dict[str, Any],
    report_date: date,
    public_paths: list[Path] | None = None,
    mx_paths: list[Path] | None = None,
) -> tuple[list[dict[str, Any]], int, dict[str, int], dict[str, int]]:
    candidates: list[dict[str, Any]] = []
    oil: list[dict[str, Any]] = []
    cross: list[dict[str, Any]] = []
    candidate_count = 0
    candidate_source_counts = {"institution-report-skill": 0, "report-search": 0, "mx-search": 0}
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
    mx_rows = mx_search_rows(mx_paths or [])
    candidate_count += len(mx_rows)
    candidate_source_counts["mx-search"] += len(mx_rows)
    for row in mx_rows:
        item = normalize_mx_search_item(row)
        published = published_date({"publish_date": item["published_at"]})
        if published is None or (report_date - published).days < 0 or (report_date - published).days > 30:
            continue
        candidates.append(item)
    for item in candidates:
        score, factors = score_quality(item, report_date)
        item["recommendation_score"] = score
        item["recommendation_reason"] = "；".join(factors)
        item["ai_notice"] = "推荐分、筛选和推荐依据由AI基于所列来源字段生成，不代表任何来源方官方立场，也不构成投资建议；请自行核验。"
    candidates.sort(key=lambda item: (item["recommendation_score"], item["published_at"], item["title"]), reverse=True)
    seen: set[str] = set()
    for item in candidates:
        key = dedupe_key(item)
        if not key or key in seen:
            continue
        seen.add(key)
        (oil if item["sector"] == "油脂油料" else cross).append(item)
    oil.sort(key=lambda item: (item["recommendation_score"], item["published_at"]), reverse=True)
    cross.sort(key=lambda item: (item["recommendation_score"], item["published_at"]), reverse=True)
    selected = oil[:7] + cross[:3]
    selected_counts: dict[str, int] = {}
    for item in selected:
        selected_counts[item["source_channel"]] = selected_counts.get(item["source_channel"], 0) + 1
    return selected, candidate_count, candidate_source_counts, selected_counts


def build(
    source: Path,
    existing: Path | None,
    now: datetime,
    public_paths: list[Path] | None = None,
    mx_paths: list[Path] | None = None,
    source_status_path: Path | None = None,
) -> dict[str, Any]:
    today = now.astimezone(SHANGHAI).date()
    previous = load_object(existing) if existing and existing.is_file() else {}
    payload = load_object(source)
    items, candidate_count, candidate_source_counts, source_counts = select(payload, today, public_paths, mx_paths)
    source_status = load_object(source_status_path) if source_status_path else {}
    if items:
        fresh_item_count = sum(str(item.get("published_at", "")).startswith(today.isoformat()) for item in items)
        latest_date = max(
            (published_date({"publish_date": item.get("published_at")}) for item in items),
            default=None,
        )
        oil_count = sum(item["sector"] == "油脂油料" for item in items)
        cross_count = sum(item["sector"] == "跨板块" for item in items)
        return {
            "schema_version": 5,
            "status": "ready" if fresh_item_count else "stale",
            "report_date": latest_date.isoformat() if latest_date else None,
            "generated_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
            "last_scanned_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
            "fresh_item_count": fresh_item_count,
            "stale_reason": None if fresh_item_count else "当日来源未返回新增公开研报；继续展示最近可核验内容。",
            "refresh_policy": "每5分钟独立扫描机构研报与公开研报；按质量重新择优",
            "candidate_count": candidate_count,
            "candidate_source_counts": candidate_source_counts,
            "deduplicated_count": len(items),
            "allocation": {"油脂油料": oil_count, "跨板块": cross_count, "target": "70% / 30%"},
            "source_counts": source_counts,
            "source_status": source_status,
            "source_policy": "机构研报、问财公开研报搜索与东方财富妙想来源平权；仅按质量评分择优；跨源标题去重",
            "items": items,
            "notice": "推荐分、筛选和推荐依据由AI基于所列来源字段生成，不代表任何来源方官方立场，也不构成投资建议；请自行核验。",
        }
    if previous and previous.get("items"):
        previous.update({
            "schema_version": 5,
            "status": "stale",
            "generated_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
            "last_scanned_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
            "fresh_item_count": 0,
            "stale_reason": "本轮扫描没有返回可发布研报；继续展示最近可核验内容。",
            "source_status": source_status,
        })
        return previous
    return {
        "schema_version": 5,
        "status": "pending",
        "report_date": None,
        "generated_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
        "last_scanned_at": now.astimezone(SHANGHAI).isoformat(timespec="seconds"),
        "source_status": source_status,
        "refresh_policy": "每5分钟独立扫描机构研报与公开研报；按质量重新择优",
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
    parser.add_argument("--mx-search", type=Path, action="append", default=[])
    parser.add_argument("--source-status", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(
        args.input,
        args.existing,
        datetime.now(SHANGHAI),
        args.public_search,
        args.mx_search,
        args.source_status,
    )
    atomic_write(args.output, payload)
    print(json.dumps({"status": payload["status"], "report_date": payload.get("report_date"), "items": len(payload.get("items", []))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Collect source-backed oil-market news and research without blocking quotes."""

from __future__ import annotations

import concurrent.futures
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Any, Callable


GOOGLE_NEWS_URL = "https://news.google.com/rss/search"
BING_NEWS_URL = "https://www.bing.com/news/search"
HTFC_FLASH_PATH = "/bus/info/filter"
HTFC_REPORT_TYPES_PATH = "/bus/report/ptypes_v2"
HTFC_REPORT_LIST_PATH = "/bus/report/specificList"
WEB_QUERY = "(棕榈油 OR 豆油 OR 菜油 OR 大豆 OR 油脂油料 OR MPOB OR GAPKI OR 生物柴油) (研报 OR 报告 OR 快讯 OR 期货)"


def compact(value: Any, limit: int = 300) -> str:
    without_markup = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", without_markup).strip()[:limit]


def normalize_time(value: Any, fallback: datetime) -> str:
    text = compact(value, 80)
    if not text:
        return fallback.isoformat(timespec="seconds")
    parsed: datetime | None = None
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, OverflowError):
        pass
    if parsed is None:
        for candidate in (text, text.replace("/", "-")):
            try:
                parsed = datetime.fromisoformat(candidate)
                break
            except ValueError:
                pass
    if parsed is None:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=fallback.tzinfo)
    return parsed.astimezone(fallback.tzinfo).isoformat(timespec="seconds")


def request_json(url: str, timeout: int, *, headers: dict[str, str] | None = None, data: bytes | None = None) -> Any:
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def source_error(name: str, exc: BaseException) -> dict[str, Any]:
    state = "forbidden" if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403) else "error"
    return {"name": name, "state": state, "detail": f"抓取失败：{type(exc).__name__} {str(exc)[:100]}"}


def normalize_event(watch: Any, *, prefix: str, source: str, title: Any, summary: Any, observed_at: Any, url: Any = "", source_id: Any = "") -> dict[str, Any] | None:
    clean_title = compact(title, 120)
    clean_summary = compact(summary)
    if not clean_title or not watch.flash_relevant(f"{clean_title} {clean_summary}"):
        return None
    observed = normalize_time(observed_at, fallback=datetime.now().astimezone())
    impact, interpretation = watch.impact_for(f"{clean_title} {clean_summary}")
    return {
        "id": watch.event_id(prefix, source_id or clean_title, observed, url),
        "kind": "event",
        "category": "跨源事件研判",
        "title": clean_title,
        "summary": clean_summary or "仅检索到标题，正文需打开原始链接核验。",
        "interpretation": interpretation,
        "impact": impact,
        "scope": "P · Y · OI",
        "source": source,
        "url": compact(url, 500),
        "observed_at": observed,
        "evidence_ids": [watch.event_id(f"{prefix}-evidence", source_id or clean_title, url)],
    }


def rss_events(watch: Any, now: datetime, timeout: int = 10) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    providers = (
        ("Google News", GOOGLE_NEWS_URL + "?" + urllib.parse.urlencode({"q": WEB_QUERY + " when:1d", "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"})),
        ("Bing News", BING_NEWS_URL + "?" + urllib.parse.urlencode({"q": WEB_QUERY, "format": "rss"})),
    )
    events: list[dict[str, Any]] = []
    details: list[str] = []
    failures = 0
    for provider, url in providers:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/rss+xml, application/xml"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                root = ET.fromstring(response.read())
            items = root.findall(".//item")
            included = 0
            for item in items[:40]:
                observed = normalize_time(item.findtext("pubDate"), now)
                try:
                    if datetime.fromisoformat(observed) < now - timedelta(days=3):
                        continue
                except ValueError:
                    pass
                event = normalize_event(
                    watch,
                    prefix="web-news",
                    source=f"跨站新闻·{provider}",
                    title=item.findtext("title"),
                    summary=item.findtext("description"),
                    observed_at=observed,
                    url=item.findtext("link"),
                    source_id=item.findtext("guid"),
                )
                if event:
                    events.append(event)
                    included += 1
            details.append(f"{provider} {len(items)}→{included}")
        except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError, OSError) as exc:
            failures += 1
            details.append(f"{provider} {type(exc).__name__}")
    state = "ready" if failures == 0 else ("degraded" if failures < len(providers) else "error")
    return events[:30], {"name": "跨站新闻搜索", "state": state, "detail": "；".join(details)}


def htfc_flash_events(watch: Any, base_url: str | None, api_key: str | None, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = "华泰天玑·油脂油料快讯"
    if not base_url or not api_key:
        return [], {"name": name, "state": "unavailable", "detail": "生产环境未配置 HTFC_BASE_URL/HTFC_API_KEY。"}
    url = base_url.rstrip("/") + HTFC_FLASH_PATH + "?" + urllib.parse.urlencode({"tags": "tags150", "lastId": "", "type": ""})
    try:
        payload = request_json(url, timeout, headers={"apikey": api_key})
        data = payload.get("data") if isinstance(payload, dict) else None
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("items") or []
        else:
            records = []
        events = []
        for item in records[:40]:
            if not isinstance(item, dict):
                continue
            event = normalize_event(
                watch,
                prefix="htfc-flash",
                source=name,
                title=item.get("title"),
                summary=item.get("content"),
                observed_at=" ".join(filter(None, (compact(item.get("date"), 20), compact(item.get("time"), 20)))) or now.isoformat(timespec="seconds"),
                url=item.get("url"),
                source_id=item.get("id"),
            )
            if event:
                event["source_fields"] = {key: item.get(key) for key in ("id", "tag", "tag2", "tagName", "type", "stars") if item.get(key) is not None}
                events.append(event)
        return events[:30], {"name": name, "state": "ready", "detail": f"精确标签 tags150 返回 {len(records)} 条，纳入 {len(events[:30])} 条。"}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError, AttributeError) as exc:
        return [], source_error(name, exc)


def category_pairs(payload: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(payload, dict):
        label = payload.get("item_name") or payload.get("name") or payload.get("label")
        value = payload.get("item_value") or payload.get("value")
        if label and value:
            pairs.append((str(label), str(value)))
        for child in payload.values():
            pairs.extend(category_pairs(child))
    elif isinstance(payload, list):
        for child in payload:
            pairs.extend(category_pairs(child))
    return pairs


def htfc_report_events(watch: Any, base_url: str | None, api_key: str | None, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = "华泰天玑·研报"
    if not base_url or not api_key:
        return [], {"name": name, "state": "unavailable", "detail": "生产环境未配置 HTFC_BASE_URL/HTFC_API_KEY。"}
    try:
        types = request_json(base_url.rstrip("/") + HTFC_REPORT_TYPES_PATH, timeout, headers={"apikey": api_key})
        matching = [(label, value) for label, value in category_pairs(types) if watch.flash_relevant(label)]
        if not matching:
            return [], {"name": name, "state": "ready", "detail": "分类接口可用，但没有识别到油脂油料研报分类；未猜测 item_value。"}
        events: list[dict[str, Any]] = []
        scanned = 0
        for label, value in matching[:3]:
            url = base_url.rstrip("/") + HTFC_REPORT_LIST_PATH + "?" + urllib.parse.urlencode({"curPage": 1, "pageSize": 20, "item_value": value})
            payload = request_json(url, timeout, headers={"apikey": api_key})
            records = watch.extract_records(payload)
            scanned += len(records)
            for item in records[:20]:
                event = normalize_event(
                    watch,
                    prefix="htfc-report",
                    source=name,
                    title=item.get("title") or item.get("report_title") or item.get("name"),
                    summary=item.get("summary") or item.get("abstract") or item.get("content"),
                    observed_at=watch.event_time(item, now),
                    url=item.get("url") or item.get("link") or item.get("attachment_url"),
                    source_id=item.get("id") or item.get("report_id"),
                )
                if event:
                    event["research_category"] = label
                    events.append(event)
        return events[:30], {"name": name, "state": "ready", "detail": f"扫描 {len(matching[:3])} 个相关分类、{scanned} 篇，纳入 {len(events[:30])} 篇。"}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError, AttributeError) as exc:
        return [], source_error(name, exc)


def mx_events(watch: Any, api_key: str | None, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not api_key:
        return [], {"name": "东方财富妙想资讯", "state": "unavailable", "detail": "生产环境未配置 MX_APIKEY；公开东方财富快讯仍独立运行。"}
    return watch.news_events(api_key, now, timeout)


def collect_all(watch: Any, now: datetime, *, mx_api_key: str | None, htfc_base_url: str | None, htfc_api_key: str | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    jobs: tuple[Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]], ...] = (
        lambda: watch.eastmoney_flash_events(now, timeout=10),
        lambda: mx_events(watch, mx_api_key, now),
        lambda: rss_events(watch, now),
        lambda: htfc_flash_events(watch, htfc_base_url, htfc_api_key, now),
        lambda: htfc_report_events(watch, htfc_base_url, htfc_api_key, now),
    )
    events: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        for result in executor.map(lambda job: job(), jobs):
            batch, source = result
            events.extend(batch)
            sources.append(source)
    deduped: dict[str, dict[str, Any]] = {}
    for event in events:
        key = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", str(event.get("title") or "").lower())
        existing = deduped.get(key)
        if existing is None or str(event.get("observed_at") or "") > str(existing.get("observed_at") or ""):
            deduped[key] = event
    return list(deduped.values()), sources

#!/usr/bin/env python3
"""Build an evidence-only intraday market-watch feed from fresh market data."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
MX_SEARCH_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search"
EASTMONEY_FLASH_URL = "https://newsinfo.eastmoney.com/kuaixun/v2/api/list?column=102&p=1&limit=100"
NEWS_QUERY = "棕榈油 豆油 菜油 油脂油料 FCPO MPOB GAPKI USDA 原油 生物柴油 出口 库存"
MAX_EVENTS = 60


def number(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid object: {path.name}")
    return payload


def contracts(*payloads: dict[str, Any]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for payload in payloads:
        for item in payload.get("contracts", []):
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol") or item.get("contract") or "").upper().strip()
            price = number(item.get("price"))
            if symbol and price is not None:
                result[symbol] = {
                    "symbol": symbol,
                    "name": str(item.get("name") or item.get("product") or symbol),
                    "price": price,
                    "change_pct": number(item.get("change_pct") if item.get("change_pct") is not None else item.get("change")),
                }
    return list(result.values())


def impact_for(text: str, movement: float | None = None) -> tuple[str, str]:
    lowered = text.lower()
    if any(word in lowered for word in ("b50", "生物柴油", "关税", "禁令", "战争", "制裁")):
        return "高", "政策或供给冲击可能直接改变油脂边际定价，需核验原文与落地时间。"
    if any(word in lowered for word in ("mpob", "gapki", "库存", "出口", "产量", "usda", "原油", "fcpo")):
        return "中", "该事件可能经产地供需或替代品价格传导至油脂，等待价格与后续来源确认。"
    if movement is not None and abs(movement) >= 1.5:
        return "高", "短时波动已达到高关注阈值，需结合成交、持仓与外盘联动确认。"
    if movement is not None and abs(movement) >= 0.5:
        return "中", "短时价格变化值得跟踪，尚不足以单独构成方向结论。"
    return "低", "当前仅作为线索记录，尚无足够证据确认持续影响。"


def event_id(prefix: str, *parts: Any) -> str:
    text = "|".join(str(part or "").strip() for part in parts)
    return f"{prefix}:{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def price_events(current: list[dict[str, Any]], previous: dict[str, Any], now: datetime) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for item in current:
        prior = number((previous.get(item["symbol"]) or {}).get("price"))
        if prior is None or prior <= 0:
            continue
        delta_pct = (item["price"] - prior) / prior * 100
        if abs(delta_pct) < 0.35:
            continue
        impact, interpretation = impact_for(item["name"], delta_pct)
        direction = "上涨" if delta_pct > 0 else "下跌"
        events.append({
            "id": event_id("price", item["symbol"], now.strftime("%Y%m%d%H%M")),
            "kind": "market",
            "category": "5分钟行情异动",
            "title": f"{item['name']} {direction} {abs(delta_pct):.2f}%",
            "summary": f"{item['symbol']} {prior:.2f} → {item['price']:.2f}；当日涨跌 {item['change_pct'] if item['change_pct'] is not None else '待核验'}%。",
            "interpretation": interpretation,
            "impact": impact,
            "scope": item["symbol"],
            "source": "全量期货行情扫描",
            "observed_at": now.isoformat(timespec="seconds"),
            "evidence_ids": [f"quote:{item['symbol']}", f"watch:price:{item['symbol']}"],
        })
    return events


def extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "result", "results", "items", "list"):
        value = payload.get(key)
        records = extract_records(value)
        if records:
            return records
    return [payload]


def event_time(item: dict[str, Any], fallback: datetime) -> str:
    for key in ("publishTime", "publish_time", "date", "time", "datetime", "updateTime"):
        value = item.get(key)
        if value:
            return str(value)
    return fallback.isoformat(timespec="seconds")


def eastmoney_flash_events(now: datetime, timeout: int = 10) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    request = urllib.request.Request(
        EASTMONEY_FLASH_URL,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
        return [], {"name": "东方财富7x24快讯", "state": "error", "detail": f"公开快讯抓取失败：{str(exc)[:120]}"}
    records = payload.get("news", []) if isinstance(payload, dict) else []
    keywords = (
        "棕榈", "豆油", "菜油", "大豆", "豆粕", "菜粕", "油脂", "原油",
        "生物柴油", "印尼", "马来西亚", "MPOB", "期货",
        "美联储", "关税", "干旱", "降雨",
    )
    events: list[dict[str, Any]] = []
    for item in records:
        if not isinstance(item, dict):
            continue
        title = re.sub(r"\s+", " ", str(item.get("title") or "")).strip()
        detail = re.sub(r"\s+", " ", str(item.get("digest") or "")).strip()[:300]
        if not title or not any(keyword.lower() in f"{title} {detail}".lower() for keyword in keywords):
            continue
        url = str(item.get("url_m") or item.get("url_w") or "").strip()
        observed = str(item.get("showtime") or item.get("ordertime") or now.isoformat(timespec="seconds"))
        impact, interpretation = impact_for(f"{title} {detail}")
        events.append({
            "id": event_id("eastmoney-flash", str(item.get("id") or title), observed),
            "kind": "event",
            "category": "市场事件检索",
            "title": title[:120],
            "summary": detail or "东方财富7x24快讯标题，详情需打开原始链接核验。",
            "interpretation": interpretation,
            "impact": impact,
            "scope": "P · Y · OI",
            "source": "东方财富7x24快讯",
            "url": url,
            "observed_at": observed,
            "evidence_ids": [f"eastmoney-flash:{item.get('id') or event_id('flash', title)}"],
        })
    return events[:20], {"name": "东方财富7x24快讯", "state": "ready", "detail": f"公开快讯扫描 {len(records)} 条，纳入 {len(events[:20])} 条油脂相关事件。"}


def news_events(api_key: str | None, now: datetime, timeout: int = 20) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not api_key:
        return eastmoney_flash_events(now, timeout=min(timeout, 10))
    request = urllib.request.Request(MX_SEARCH_URL, data=json.dumps({"query": NEWS_QUERY}, ensure_ascii=False).encode("utf-8"), method="POST", headers={"Content-Type": "application/json", "apikey": api_key})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            records = extract_records(json.loads(response.read().decode("utf-8")))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return eastmoney_flash_events(now, timeout=min(timeout, 10))
    events: list[dict[str, Any]] = []
    for item in records[:20]:
        title = re.sub(r"\s+", " ", str(item.get("title") or item.get("name") or "")).strip()
        if not title:
            continue
        detail = re.sub(r"\s+", " ", str(item.get("trunk") or item.get("summary") or "")).strip()[:300]
        url = str(item.get("url") or item.get("link") or "").strip()
        impact, interpretation = impact_for(f"{title} {detail}")
        events.append({
            "id": event_id("news", title, url, event_time(item, now)),
            "kind": "event",
            "category": "市场事件检索",
            "title": title[:120],
            "summary": detail or "资讯返回标题，正文需打开来源核验。",
            "interpretation": interpretation,
            "impact": impact,
            "scope": "P · Y · OI",
            "source": "东方财富妙想资讯",
            "url": url,
            "observed_at": event_time(item, now),
            "evidence_ids": [event_id("news-evidence", title, url)],
        })
    return events, {"name": "东方财富妙想资讯", "state": "ready", "detail": f"检索 {len(records)} 条，纳入 {len(events)} 条可识别事件。"}


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, path)


def build_watch(oil: dict[str, Any], exchange: dict[str, Any], previous_quotes: dict[str, Any], previous_events: list[dict[str, Any]], now: datetime, api_key: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    scanned = contracts(oil, exchange)
    fresh_prices = price_events(scanned, previous_quotes, now)
    news, news_source = news_events(api_key, now)
    merged: dict[str, dict[str, Any]] = {str(item.get("id")): item for item in previous_events if isinstance(item, dict) and item.get("id")}
    for item in [*fresh_prices, *news]:
        merged[item["id"]] = item
    events = sorted(merged.values(), key=lambda item: str(item.get("observed_at") or ""), reverse=True)[:MAX_EVENTS]
    sources = [
        {"name": "全量期货行情", "state": "ready" if scanned else "error", "detail": f"本轮覆盖 {len(scanned)} 个有价格的合约。"},
        news_source,
    ]
    payload = {
        "schema_version": 1,
        "status": "ready" if scanned else "degraded",
        "generated_at": now.isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "coverage": {"priced_contracts": len(scanned), "event_count": len(events)},
        "sources": sources,
        "events": events,
    }
    quotes = {item["symbol"]: {"price": item["price"], "observed_at": now.isoformat(timespec="seconds")} for item in scanned}
    return payload, quotes

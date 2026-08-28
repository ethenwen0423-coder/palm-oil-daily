#!/usr/bin/env python3
"""Build an evidence-only intraday market-watch feed from fresh market data."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
MX_SEARCH_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search"
EASTMONEY_FLASH_URL = "https://newsinfo.eastmoney.com/kuaixun/v2/api/list?column=102&p=1&limit=100"
NEWS_QUERY = "棕榈油 豆油 菜油 油脂油料 FCPO MPOB GAPKI USDA 原油 生物柴油 出口 库存"
MAX_EVENTS = 60
MAX_MARKET_EVENTS = 12
MAX_MARKET_EVENTS_PER_SCAN = 2
MIN_CANDIDATE_MOVE_PCT = 0.55
DIRECT_MOVE_PCT = 0.90
CONFIRMED_MOVE_PCT = 1.00
EXTREME_MOVE_PCT = 1.50
MARKET_EVENT_COOLDOWN = timedelta(minutes=45)
REARM_INCREMENT_PCT = 0.50
AI_EVENT_NOTICE = "AI 基于来源返回内容整理，非来源方原话，不代表来源方官方立场，不构成投资建议；请自行核验。"


def number(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def clean_source_text(value: Any) -> str:
    """Normalize source text without imposing a character cutoff."""
    decoded = html.unescape(str(value or ""))
    without_markup = re.sub(r"<[^>]+>", " ", decoded)
    return re.sub(r"\s+", " ", without_markup).strip()


def source_sentences(value: Any) -> list[str]:
    text = clean_source_text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[。！？!?；;])|(?<=\.)\s+", text) if part.strip()]


def _title_sentence(title: str) -> str:
    clean_title = clean_source_text(title).strip("【】[] ")
    if not clean_title:
        return "来源内容待核验。"
    return clean_title if re.search(r"[。！？!?；;.]$", clean_title) else f"{clean_title}。"


def _complete_digest(sentences: list[str], limit: int, *, max_sentences: int) -> str:
    selected: list[str] = []
    total = 0
    for sentence in sentences:
        if not re.search(r"[。！？!?；;.]$", sentence):
            continue
        if selected and (total + len(sentence) > limit or len(selected) >= max_sentences):
            break
        if not selected and len(sentence) > limit:
            continue
        selected.append(sentence)
        total += len(sentence)
    return "".join(selected)


def summarize_source_event(title: Any, body: Any) -> tuple[str, str]:
    """Build sentence-complete list and detail summaries from returned source text."""
    clean_title = clean_source_text(title)
    clean_body = clean_source_text(body)
    if clean_title and clean_body:
        clean_body = re.sub(rf"^(?:【|\[)?{re.escape(clean_title)}(?:】|\])?\s*", "", clean_body, count=1)
    sentences = source_sentences(clean_body)
    preview = _complete_digest(sentences, 180, max_sentences=2) or _title_sentence(clean_title)
    detail = _complete_digest(sentences, 650, max_sentences=6) or preview
    return preview, detail


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
                    "product": str(item.get("product") or ""),
                    "category": str(item.get("category") or "待分类"),
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


def event_movement(item: dict[str, Any]) -> float:
    matched = re.search(r"(?:上涨|下跌)\s*([0-9.]+)%", str(item.get("title") or ""))
    return number(matched.group(1)) if matched else 0.0


def filtered_market_history(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    latest_by_scope: dict[str, datetime] = {}
    for item in items:
        if item.get("kind") != "market":
            continue
        if "确认异动" not in str(item.get("category") or "") and event_movement(item) < DIRECT_MOVE_PCT:
            continue
        scope = str(item.get("scope") or "")
        observed = parsed_time(item.get("observed_at"))
        latest = latest_by_scope.get(scope)
        if observed is not None and latest is not None and latest - observed < MARKET_EVENT_COOLDOWN:
            continue
        if observed is not None:
            latest_by_scope[scope] = observed
        kept.append(item)
        if len(kept) >= MAX_MARKET_EVENTS:
            break
    return kept


def parsed_time(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=SHANGHAI)
    except (TypeError, ValueError):
        return None


def price_events(
    current: list[dict[str, Any]],
    previous: dict[str, Any],
    now: datetime,
) -> tuple[list[dict[str, Any]], dict[str, Any], int]:
    candidates: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
    quote_state: dict[str, Any] = {}
    for item in current:
        prior_state = previous.get(item["symbol"]) if isinstance(previous.get(item["symbol"]), dict) else {}
        prior = number(prior_state.get("price"))
        state = {
            "price": item["price"],
            "observed_at": now.isoformat(timespec="seconds"),
            "candidate_direction": None,
            "candidate_count": 0,
            "candidate_anchor_price": None,
            "candidate_started_at": None,
            "last_event_at": prior_state.get("last_event_at"),
            "last_event_direction": prior_state.get("last_event_direction"),
            "last_event_move_pct": prior_state.get("last_event_move_pct"),
        }
        quote_state[item["symbol"]] = state
        if prior is None or prior <= 0:
            continue
        delta_pct = (item["price"] - prior) / prior * 100
        direction_sign = 1 if delta_pct > 0 else -1
        if abs(delta_pct) < MIN_CANDIDATE_MOVE_PCT:
            continue
        same_candidate = prior_state.get("candidate_direction") == direction_sign
        anchor = number(prior_state.get("candidate_anchor_price")) if same_candidate else prior
        anchor = anchor if anchor is not None and anchor > 0 else prior
        candidate_count = int(prior_state.get("candidate_count") or 0) + 1 if same_candidate else 1
        cumulative_pct = (item["price"] - anchor) / anchor * 100
        state.update({
            "candidate_direction": direction_sign,
            "candidate_count": candidate_count,
            "candidate_anchor_price": anchor,
            "candidate_started_at": prior_state.get("candidate_started_at") if same_candidate else now.isoformat(timespec="seconds"),
        })
        direct = abs(delta_pct) >= DIRECT_MOVE_PCT
        confirmed = candidate_count >= 2 and abs(cumulative_pct) >= CONFIRMED_MOVE_PCT
        if not direct and not confirmed:
            continue
        movement = delta_pct if direct else cumulative_pct
        last_event_at = parsed_time(prior_state.get("last_event_at"))
        last_direction = number(prior_state.get("last_event_direction"))
        last_move = abs(number(prior_state.get("last_event_move_pct")) or 0)
        cooling = last_event_at is not None and now - last_event_at < MARKET_EVENT_COOLDOWN
        materially_larger = abs(movement) >= max(EXTREME_MOVE_PCT, last_move + REARM_INCREMENT_PCT)
        sharp_reversal = last_direction is not None and direction_sign != int(last_direction) and abs(movement) >= EXTREME_MOVE_PCT
        if cooling and not (materially_larger or sharp_reversal):
            continue
        impact, interpretation = impact_for(item["name"], movement)
        direction = "上涨" if movement > 0 else "下跌"
        window_minutes = 5 if direct else min(candidate_count * 5, 15)
        event = {
            "id": event_id("price", item["symbol"], now.strftime("%Y%m%d%H%M")),
            "kind": "market",
            "category": f"{window_minutes}分钟确认异动",
            "title": f"{item['name']} {direction} {abs(movement):.2f}%",
            "summary": f"{item['symbol']} {(prior if direct else anchor):.2f} → {item['price']:.2f}；当日涨跌 {item['change_pct'] if item['change_pct'] is not None else '待核验'}%。",
            "interpretation": interpretation,
            "impact": impact,
            "scope": item["symbol"],
            "source": "全量期货行情扫描",
            "observed_at": now.isoformat(timespec="seconds"),
            "evidence_ids": [f"quote:{item['symbol']}", f"watch:price:{item['symbol']}"],
        }
        candidates.append((abs(movement), event, state))
    candidates.sort(key=lambda row: row[0], reverse=True)
    published = candidates[:MAX_MARKET_EVENTS_PER_SCAN]
    for _, event, state in candidates:
        movement = number(re.search(r"([0-9.]+)%$", event["title"]).group(1)) or 0
        state.update({
            "last_event_at": now.isoformat(timespec="seconds"),
            "last_event_direction": 1 if "上涨" in event["title"] else -1,
            "last_event_move_pct": movement,
            "candidate_direction": None,
            "candidate_count": 0,
            "candidate_anchor_price": None,
            "candidate_started_at": None,
        })
    return [event for _, event, _ in published], quote_state, len(candidates)


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


def flash_relevant(text: str) -> bool:
    normalized = text.lower()
    direct = (
        "棕榈", "豆油", "菜油", "油菜", "大豆", "豆粕", "菜粕", "油脂",
        "原油", "生物柴油", "mpob", "农产品期货", "商品期货",
    )
    if any(keyword in normalized for keyword in direct):
        return True
    if "美联储" in normalized:
        return True
    weather = ("干旱", "降雨", "洪水", "厄尔尼诺", "拉尼娜")
    agriculture = ("农业", "作物", "产区", "种植", "收割", "单产")
    return any(word in normalized for word in weather) and any(
        word in normalized for word in agriculture
    )


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
    events: list[dict[str, Any]] = []
    for item in records:
        if not isinstance(item, dict):
            continue
        title = re.sub(r"\s+", " ", str(item.get("title") or "")).strip()
        source_detail = clean_source_text(item.get("digest"))
        if not title or not flash_relevant(f"{title} {source_detail}"):
            continue
        url = str(item.get("url_m") or item.get("url_w") or "").strip()
        observed = str(item.get("showtime") or item.get("ordertime") or now.isoformat(timespec="seconds"))
        summary, detail_summary = summarize_source_event(title, source_detail)
        impact, interpretation = impact_for(f"{title} {source_detail}")
        events.append({
            "id": event_id("eastmoney-flash", str(item.get("id") or title), observed),
            "kind": "event",
            "category": "市场事件检索",
            "title": title,
            "summary": summary,
            "detail_summary": detail_summary,
            "summary_generated": True,
            "ai_notice": AI_EVENT_NOTICE,
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
        source_detail = clean_source_text(item.get("trunk") or item.get("summary"))
        url = str(item.get("url") or item.get("link") or "").strip()
        summary, detail_summary = summarize_source_event(title, source_detail)
        impact, interpretation = impact_for(f"{title} {source_detail}")
        events.append({
            "id": event_id("news", title, url, event_time(item, now)),
            "kind": "event",
            "category": "市场事件检索",
            "title": title,
            "summary": summary,
            "detail_summary": detail_summary,
            "summary_generated": True,
            "ai_notice": AI_EVENT_NOTICE,
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


def build_watch(oil: dict[str, Any], exchange: dict[str, Any], previous_quotes: dict[str, Any], previous_events: list[dict[str, Any]], now: datetime, api_key: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the quote snapshot without performing any network news search.

    ``api_key`` remains accepted for callers from older deployments, but event
    collection now runs in the independent five-minute event service.  This is
    deliberate: slow or forbidden research sources must never delay quotes.
    """
    scanned = contracts(oil, exchange)
    fresh_prices, quote_state, detected_moves = price_events(scanned, previous_quotes, now)
    merged: dict[str, dict[str, Any]] = {
        str(item.get("id")): item
        for item in previous_events
        if isinstance(item, dict)
        and item.get("id")
        and (
            item.get("source") != "东方财富7x24快讯"
            or flash_relevant(f"{item.get('title', '')} {item.get('summary', '')}")
        )
    }
    for item in fresh_prices:
        merged[item["id"]] = item
    ordered = sorted(merged.values(), key=lambda item: str(item.get("observed_at") or ""), reverse=True)
    market_events = filtered_market_history(ordered)
    other_events = [item for item in ordered if item.get("kind") != "market"][:MAX_EVENTS - MAX_MARKET_EVENTS]
    events = sorted(market_events + other_events, key=lambda item: str(item.get("observed_at") or ""), reverse=True)[:MAX_EVENTS]
    sources = [{"name": "全量期货行情", "state": "ready" if scanned else "error", "detail": f"本轮覆盖 {len(scanned)} 个有价格的合约。"}]
    payload = {
        "schema_version": 1,
        "status": "ready" if scanned else "degraded",
        "generated_at": now.isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "coverage": {
            "priced_contracts": len(scanned),
            "event_count": len(events),
            "market_moves_detected": detected_moves,
            "market_moves_published": len(fresh_prices),
        },
        "sources": sources,
        "events": events,
    }
    return payload, quote_state

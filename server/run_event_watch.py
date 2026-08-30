#!/usr/bin/env python3
"""Refresh multi-source market events every five minutes, independently of quotes."""

from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
SITE_ROOT = Path(os.environ.get("PALM_OIL_SITE_ROOT", "/srv/palm-oil-daily/site"))
LIVE_ROOT = Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", "/srv/palm-oil-daily/live-data"))
STATE_ROOT = Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", "/srv/palm-oil-daily/state"))
SUMMARY_BATCH_SIZE = 12
SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "headline": {"type": "string"},
                    "summary": {"type": "string"},
                    "detail_summary": {"type": "string"},
                },
                "required": ["id", "headline", "summary", "detail_summary"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["events"],
    "additionalProperties": False,
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def private_value(path: Path, key: str) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.strip().removeprefix("export ").partition("=")
            if separator and name.strip() == key and value.strip():
                return value.strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def env_value(key: str) -> str | None:
    return os.environ.get(key) or private_value(STATE_ROOT / "private.env", key)


def clean_sentence(value: Any, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit].strip()


def declarative_title(value: Any) -> str:
    """Build a bounded fallback label that never ends as a question."""
    title = clean_sentence(value, 72).strip("【】[] ")
    title = re.sub(r"^(?:史上最强|重磅|突发)[!！：:\s]*", "", title)
    if re.search(r"[?？]", title):
        parts = [part.strip() for part in re.split(r"[?？]+", title) if part.strip()]
        title = parts[-1] if len(parts) > 1 and len(parts[-1]) >= 8 else f"{parts[0].rstrip('吗么')}风险受到关注"
    title = re.sub(r"[?？…\.]+$", "", title).strip()
    if title.endswith(("吗", "么")):
        title = f"{title[:-1]}的可能性受到关注"
    return title or "跨源事件信息仍待核验"


def fallback_summary(event: dict[str, Any]) -> None:
    source_title = clean_sentence(event.get("_source_title") or event.get("title"), 180)
    source_summary = clean_sentence(event.get("_source_summary"), 900)
    headline = declarative_title(source_title)
    current_preview = clean_sentence(event.get("summary"), 220)
    current_detail = clean_sentence(event.get("detail_summary"), 760)
    title_only = not source_summary or source_summary.rstrip("。！？?! ") == source_title.rstrip("。！？?! ")
    if title_only:
        preview = f"来源目前只返回了标题级线索，事件涉及“{headline}”，具体事实、时间和依据仍需打开直接来源核验。"
        detail = f"本轮跨源检索没有取得足以独立复述事件经过的正文摘要。可确认的线索仅为“{headline}”；在获得原文或第二来源前，不应把标题中的疑问、预测或幅度视为已证实事实。"
    else:
        preview = current_preview if current_preview and current_preview != source_title else f"来源信息显示：{headline}。"
        detail = current_detail if current_detail and current_detail != source_title else preview
    event.update({
        "title": headline,
        "summary": preview,
        "detail_summary": detail,
        "summary_method": "source-bounded-fallback",
        "summary_generated": True,
    })


def summary_prompt(events: list[dict[str, Any]]) -> str:
    inputs = [{
        "id": str(item.get("id") or ""),
        "source": clean_sentence(item.get("source"), 80),
        "source_title": clean_sentence(item.get("_source_title") or item.get("title"), 220),
        "source_summary": clean_sentence(item.get("_source_summary"), 1600),
        "observed_at": clean_sentence(item.get("observed_at"), 50),
    } for item in events]
    return """你是油脂期货跨源事件编辑。只依据 INPUT_EVENTS 中每条来源返回的标题和摘要，生成中文结构化摘要；不得使用外部知识，不得补造主体、数字、时间、因果或结论。

每条必须满足：
1. headline 是陈述句，概括实际事件或来源主张，12至42个汉字为宜；不得以问号或省略号结尾，不得保留“史上最强”“重磅”等悬念式开头。若原文是提问，改写成“某机构提出/警示/讨论某风险”之类的有归属陈述。
2. summary 用1至2句说明用户一眼需要知道的主体、事件和关键变化，不重复 headline。
3. detail_summary 用2至4句说明“谁、发生/主张什么、涉及哪些明确数字或时间、为什么与油脂相关、尚有哪些不确定性”。只保留来源返回内容中的事实和归属，不复制整段原文。
4. 来源信息不足时，明确写“来源摘要未披露具体依据/时间/数据，需查看原文核验”，绝不猜测。
5. 不写交易指令，不把来源观点伪装成官方事实。

INPUT_EVENTS:
""" + json.dumps(inputs, ensure_ascii=False, separators=(",", ":"))


def valid_model_summary(item: dict[str, Any]) -> bool:
    headline = clean_sentence(item.get("headline"), 80)
    summary = clean_sentence(item.get("summary"), 260)
    detail = clean_sentence(item.get("detail_summary"), 900)
    return bool(6 <= len(headline) <= 80 and summary and detail and not re.search(r"[?？…]", headline))


def summarize_events(
    model_backend: Any,
    events: list[dict[str, Any]],
    previous: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prior_by_id = {
        str(item.get("id")): item
        for item in previous.get("events", [])
        if isinstance(item, dict) and item.get("summary_method") == "model"
    }
    pending: list[dict[str, Any]] = []
    reused = 0
    for event in events:
        if event.get("kind") != "event" or event.get("category") == "天气产量研判":
            continue
        prior = prior_by_id.get(str(event.get("id")))
        if prior and valid_model_summary({
            "headline": prior.get("title"),
            "summary": prior.get("summary"),
            "detail_summary": prior.get("detail_summary"),
        }):
            for key in ("title", "summary", "detail_summary", "summary_method", "summary_backend"):
                if prior.get(key):
                    event[key] = prior[key]
            reused += 1
        else:
            pending.append(event)

    generated = 0
    failures: list[str] = []
    for offset in range(0, len(pending), SUMMARY_BATCH_SIZE):
        batch = pending[offset:offset + SUMMARY_BATCH_SIZE]
        try:
            payload, backend = model_backend.request_json(
                schema=SUMMARY_SCHEMA,
                schema_name="cross_source_event_summaries",
                prompt=summary_prompt(batch),
                timeout=180,
                verbosity="medium",
            )
            returned = {
                str(item.get("id")): item
                for item in payload.get("events", [])
                if isinstance(item, dict) and valid_model_summary(item)
            }
            for event in batch:
                summary = returned.get(str(event.get("id")))
                if not summary:
                    fallback_summary(event)
                    continue
                event.update({
                    "title": clean_sentence(summary["headline"], 80),
                    "summary": clean_sentence(summary["summary"], 260),
                    "detail_summary": clean_sentence(summary["detail_summary"], 900),
                    "summary_method": "model",
                    "summary_backend": backend,
                    "summary_generated": True,
                })
                generated += 1
        except (OSError, RuntimeError, ValueError, TypeError) as exc:
            failures.append(type(exc).__name__)
            for event in batch:
                fallback_summary(event)

    for event in events:
        if event.get("kind") == "event" and event.get("category") != "天气产量研判" and not event.get("summary_method"):
            fallback_summary(event)
        source_title = clean_sentence(event.get("_source_title"), 180)
        if source_title:
            event["evidence"] = [f"来源标题：{source_title}"]
        for key in [name for name in event if name.startswith("_")]:
            event.pop(key, None)

    state = "ready" if not failures else ("degraded" if generated or reused else "fallback")
    detail = f"模型新生成 {generated} 条，复用 {reused} 条"
    if failures:
        detail += f"；{len(failures)} 批回退为来源约束摘要"
    return events, {"name": "AI事件摘要", "state": state, "detail": detail}


def merge_snapshot(watch: Any, previous: dict[str, Any], events: list[dict[str, Any]], sources: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    merged = {
        str(item.get("id")): item
        for item in previous.get("events", [])
        if isinstance(item, dict) and item.get("id") and item.get("kind") == "market"
    }
    for item in events:
        merged[str(item["id"])] = item
    payload = dict(previous)
    payload.setdefault("schema_version", 1)
    payload.setdefault("status", "degraded")
    payload.setdefault("generated_at", now.isoformat(timespec="seconds"))
    payload.setdefault("timezone", "Asia/Shanghai")
    payload["events_updated_at"] = now.isoformat(timespec="seconds")
    payload["events"] = sorted(merged.values(), key=lambda item: str(item.get("observed_at") or ""), reverse=True)[: watch.MAX_EVENTS]
    coverage = dict(payload.get("coverage") or {})
    coverage["event_count"] = len(payload["events"])
    coverage["event_sources_ready"] = sum(item.get("state") == "ready" for item in sources)
    coverage["event_sources_total"] = len(sources)
    payload["coverage"] = coverage
    quote_sources = [item for item in previous.get("sources", []) if isinstance(item, dict) and item.get("name") == "全量期货行情"]
    payload["sources"] = [*quote_sources, *sources]
    return payload


def main() -> int:
    now = datetime.now(SHANGHAI)
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    lock = (STATE_ROOT / "market-watch.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "busy", "retry": True}))
        lock.close()
        return 0
    try:
        watch = load_module("palm_event_watch_base", SITE_ROOT / "server" / "market_watch.py")
        collector = load_module("palm_event_watch_sources", SITE_ROOT / "server" / "event_watch.py")
        try:
            previous = watch.load_json(LIVE_ROOT / "market_watch.json")
        except (OSError, ValueError, json.JSONDecodeError):
            previous = {}
        events, sources = collector.collect_all(
            watch,
            now,
            mx_api_key=env_value("MX_APIKEY"),
            htfc_base_url=env_value("HTFC_BASE_URL"),
            htfc_api_key=env_value("HTFC_API_KEY"),
        )
        model_backend = load_module("palm_event_summary_backend", SITE_ROOT / "server" / "model_backend.py")
        events, summary_source = summarize_events(model_backend, events, previous)
        sources.append(summary_source)
        payload = merge_snapshot(watch, previous, events, sources, now)
        LIVE_ROOT.mkdir(parents=True, exist_ok=True)
        watch.atomic_write(LIVE_ROOT / "market_watch.json", payload)
        states = {item["name"]: item["state"] for item in sources}
        print(json.dumps({"status": "ready", "event_count": len(events), "sources": states, "events_updated_at": payload["events_updated_at"]}, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc), "retry": True}, ensure_ascii=False))
        return 2
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

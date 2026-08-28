#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import importlib.util
import re
import threading
import time as monotonic_time
from datetime import date, datetime, time, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo


DATA_ROOT = Path(os.environ.get("PALM_OIL_DATA_ROOT", "/site/data"))
HOST = os.environ.get("PALM_OIL_API_HOST", "0.0.0.0")
PORT = int(os.environ.get("PALM_OIL_API_PORT", "8000"))
SHANGHAI = ZoneInfo("Asia/Shanghai")
CONTRACT_ANALYSIS_CACHE_SECONDS = int(os.environ.get("PALM_OIL_CONTRACT_ANALYSIS_CACHE_SECONDS", "60"))
_CONTRACT_ANALYSIS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_CONTRACT_ANALYSIS_LOCK = threading.Lock()

ROUTES = {
    "/api/reports": "reports.json",
    "/api/oil-futures": "oil_futures.json",
    "/api/exchange-futures": "exchange_futures.json",
    "/api/quant-model-signals": "quant_model_signals.json",
    "/api/supply-demand": "supply-demand.json",
    "/api/contracts/current": "contracts/current_contracts.json",
    "/api/forecast/metrics/latest": "forecast/metrics/latest.json",
    "/api/forecast/metrics/20d": "forecast/metrics/20d.json",
    "/api/forecast/metrics/60d": "forecast/metrics/60d.json",
    "/api/forecast/feedback/latest": "forecast/feedback/latest.json",
    "/api/review/latest": "review/latest_review.json",
    "/api/assistant/brief": "market_assistant_brief.json",
    "/api/assistant/watch": "market_watch.json",
    "/api/htfc/tianji": "htfc_tianji.json",
    "/api/assistant/research-watch": "research_watch.json",
}

DATASET_RULES = {
    "/api/reports": {
        "label": "研究报告",
        "stale_after_seconds": 60 * 60 * 48,
        "timestamp_fields": ("generated_at", "date"),
    },
    "/api/oil-futures": {
        "label": "油脂行情",
        "stale_after_seconds": 60 * 60 * 18,
        "timestamp_fields": ("updated_at",),
    },
    "/api/exchange-futures": {
        "label": "全品种行情",
        "stale_after_seconds": 60 * 60 * 18,
        "timestamp_fields": ("updated_at",),
    },
    "/api/quant-model-signals": {
        "label": "量化信号",
        "stale_after_seconds": 60 * 60 * 36,
        "timestamp_fields": ("generated_at", "market_updated_at"),
    },
    "/api/supply-demand": {
        "label": "供需资料",
        "stale_after_seconds": 60 * 60 * 36,
        "timestamp_fields": ("checked_at", "generated_at"),
    },
    "/api/contracts/current": {
        "label": "主力合约",
        "stale_after_seconds": 60 * 60 * 72,
        "timestamp_fields": ("generated_at",),
    },
    "/api/forecast/metrics/latest": {
        "label": "预测评估",
        "stale_after_seconds": 60 * 60 * 96,
        "timestamp_fields": ("generated_at", "as_of"),
    },
    "/api/forecast/metrics/20d": {
        "label": "20日预测评估",
        "stale_after_seconds": 60 * 60 * 96,
        "timestamp_fields": ("generated_at", "as_of"),
    },
    "/api/forecast/metrics/60d": {
        "label": "60日预测评估",
        "stale_after_seconds": 60 * 60 * 96,
        "timestamp_fields": ("generated_at", "as_of"),
    },
    "/api/forecast/feedback/latest": {
        "label": "预测复盘反馈",
        "stale_after_seconds": 60 * 60 * 96,
        "timestamp_fields": ("generated_at", "as_of", "evaluated_at", "date"),
    },
    "/api/review/latest": {
        "label": "最新复盘",
        "stale_after_seconds": 60 * 60 * 96,
        "timestamp_fields": ("generated_at", "reviewed_at", "date"),
    },
    "/api/assistant/brief": {
        "label": "AI 盯盘简报",
        "stale_after_seconds": 60 * 60 * 6,
        "timestamp_fields": ("generated_at",),
    },
    "/api/assistant/research-watch": {
        "label": "公开研报推荐",
        "stale_after_seconds": 60 * 60 * 36,
        "timestamp_fields": ("generated_at",),
    },
    "/api/assistant/watch": {
        "label": "5分钟市场扫描",
        "stale_after_seconds": 60 * 12,
        "timestamp_fields": ("events_updated_at", "generated_at"),
    },
    "/api/htfc/tianji": {
        "label": "机构资讯数据",
        "stale_after_seconds": 60 * 60,
        "timestamp_fields": ("generated_at",),
    },
}

AUTOMATION_MARKERS = {
    "market": {
        "label": "服务器行情采集",
        "path": ".server-market-ready.json",
        "routes": (
            "/api/oil-futures",
            "/api/exchange-futures",
            "/api/quant-model-signals",
            "/api/contracts/current",
            "/api/assistant/watch",
        ),
    },
    "supply": {
        "label": "服务器官方资料检查",
        "path": ".server-supply-ready.json",
        "routes": ("/api/supply-demand",),
    },
    "ai": {
        "label": "服务器 AI 简报",
        "path": ".server-ai-ready.json",
        "routes": ("/api/assistant/brief",),
    },
    "research": {
        "label": "服务器研究报告",
        "path": ".server-research-ready.json",
        "routes": ("/api/reports",),
    },
    "review": {
        "label": "服务器预测复盘",
        "path": ".server-review-ready.json",
        "routes": (
            "/api/forecast/metrics/latest",
            "/api/forecast/metrics/20d",
            "/api/forecast/metrics/60d",
            "/api/forecast/feedback/latest",
            "/api/review/latest",
        ),
    },
    "htfc": {
        "label": "机构资讯只读采集",
        "path": ".server-htfc-ready.json",
        "routes": ("/api/htfc/tianji", "/api/assistant/research-watch"),
    },
}
UPSTREAM_ROUTES = {
    "/api/reports",
    "/api/forecast/metrics/latest",
    "/api/forecast/metrics/20d",
    "/api/forecast/metrics/60d",
    "/api/forecast/feedback/latest",
    "/api/review/latest",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


PUBLIC_TEXT_REPLACEMENTS = (
    (re.compile(r"https?://(?:www\.)?htfc\.com/?", re.IGNORECASE), ""),
    (re.compile(r"htfc[-_ ]news", re.IGNORECASE), "institutional-news"),
    (re.compile(r"htfc[-_ ]kline", re.IGNORECASE), "institutional-kline"),
    (re.compile(r"HTFC\s*Tianji", re.IGNORECASE), "机构资讯数据"),
    (re.compile(r"htfc[-_ ]tianji", re.IGNORECASE), "institutional-feed"),
    (re.compile(r"华泰天玑"), "机构资讯"),
    (re.compile(r"华泰期货"), "机构研究"),
    (re.compile(r"天玑", re.IGNORECASE), "机构资讯"),
    (re.compile(r"HTFC", re.IGNORECASE), "机构资讯"),
)


def public_text(value: str) -> str:
    text = value
    for pattern, replacement in PUBLIC_TEXT_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def public_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: public_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [public_payload(item) for item in value]
    if isinstance(value, str):
        return public_text(value)
    return value


def _load_contract_analysis_module():
    module_path = Path(__file__).with_name("contract_analysis.py")
    spec = importlib.util.spec_from_file_location("palm_oil_contract_analysis", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("contract analysis module unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract_analysis(data_root: Path, symbol: str) -> dict[str, Any]:
    normalized = str(symbol or "").strip().upper()
    now = monotonic_time.monotonic()
    with _CONTRACT_ANALYSIS_LOCK:
        cached = _CONTRACT_ANALYSIS_CACHE.get(normalized)
        if cached and now - cached[0] < CONTRACT_ANALYSIS_CACHE_SECONDS:
            return {**cached[1], "cache": "hit"}
    module = _load_contract_analysis_module()
    payload = module.analyze_contract(data_root, normalized)
    with _CONTRACT_ANALYSIS_LOCK:
        _CONTRACT_ANALYSIS_CACHE[normalized] = (now, payload)
    return {**payload, "cache": "miss"}


def parse_timestamp(value: Any, *, end_of_day: bool = False) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        if len(text) == 10:
            parsed_date = date.fromisoformat(text)
            parsed_time = time.max if end_of_day else time.min
            return datetime.combine(parsed_date, parsed_time, tzinfo=SHANGHAI)
        normalized = text.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=SHANGHAI)
        return parsed
    except ValueError:
        return None


def first_report_timestamp(payload: Any) -> datetime | None:
    if not isinstance(payload, list) or not payload:
        return None
    first = payload[0] if isinstance(payload[0], dict) else {}
    return parse_timestamp(first.get("generated_at")) or parse_timestamp(
        first.get("date"),
        end_of_day=True,
    )


def observed_timestamp(payload: Any, fields: tuple[str, ...]) -> datetime | None:
    if isinstance(payload, list):
        return first_report_timestamp(payload)
    if not isinstance(payload, dict):
        return None
    for field in fields:
        parsed = parse_timestamp(payload.get(field), end_of_day=field in {"date", "as_of"})
        if parsed is not None:
            return parsed
    return None


def dataset_status(
    data_root: Path,
    route: str,
    relative: str,
    *,
    now: datetime,
) -> dict[str, Any]:
    rule = DATASET_RULES[route]
    target = data_root / relative
    result: dict[str, Any] = {
        "label": rule["label"],
        "route": route,
        "available": False,
        "state": "missing",
        "observed_at": None,
        "age_seconds": None,
        "stale_after_seconds": rule["stale_after_seconds"],
        "updated_at": None,
    }
    try:
        payload = load_json(target)
        stat = target.stat()
    except FileNotFoundError:
        return result
    except (OSError, json.JSONDecodeError):
        result["state"] = "invalid"
        return result

    observed = observed_timestamp(payload, rule["timestamp_fields"])
    if observed is None:
        observed = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    age_seconds = max(0, int((now.astimezone(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds()))
    stale = age_seconds > rule["stale_after_seconds"]
    result.update(
        {
            "available": True,
            "state": "stale" if stale else "ready",
            "observed_at": observed.isoformat(),
            "age_seconds": age_seconds,
            "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        }
    )
    return result


def automation_status(data_root: Path) -> dict[str, dict[str, Any]]:
    status: dict[str, dict[str, Any]] = {}
    for key, rule in AUTOMATION_MARKERS.items():
        target = data_root / rule["path"]
        item: dict[str, Any] = {
            "label": rule["label"],
            "state": "pending",
            "owner": None,
            "last_success_at": None,
            "session": None,
        }
        try:
            payload = load_json(target)
        except FileNotFoundError:
            status[key] = item
            continue
        except (OSError, json.JSONDecodeError):
            item["state"] = "invalid"
            status[key] = item
            continue
        if not isinstance(payload, dict):
            item["state"] = "invalid"
            status[key] = item
            continue
        generated_at = parse_timestamp(payload.get("generated_at"))
        owner = str(payload.get("owner") or "").strip()
        if generated_at is None or not owner:
            item["state"] = "invalid"
        else:
            item.update(
                {
                    "state": "ready",
                    "owner": owner,
                    "last_success_at": generated_at.isoformat(),
                    "session": payload.get("session"),
                }
            )
        status[key] = item
    return status


def build_status(data_root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    current = now or datetime.now(timezone.utc)
    datasets = {
        route: dataset_status(data_root, route, relative, now=current)
        for route, relative in ROUTES.items()
    }
    automation = automation_status(data_root)
    for route in UPSTREAM_ROUTES:
        datasets[route]["owner"] = "upstream-sync"
    for key, rule in AUTOMATION_MARKERS.items():
        owner = automation[key].get("owner") or "upstream-sync"
        for route in rule["routes"]:
            datasets[route]["owner"] = owner
    degraded = [route for route, item in datasets.items() if item["state"] != "ready"]
    return {
        "status": "degraded" if degraded else "ok",
        "served_at": current.astimezone(timezone.utc).isoformat(),
        "timezone": "Asia/Shanghai",
        "public_sync_interval_seconds": 120,
        "datasets": datasets,
        "degraded_datasets": degraded,
        "automation": automation,
        "fixed_logic": ["otc_structure_library", "quant_model_rules"],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "PalmOilDataAPI/2"

    def _send_json(self, status: int, payload: Any, *, include_body: bool = True) -> None:
        raw = json.dumps(public_payload(payload), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        if include_body:
            self.wfile.write(raw)

    def _serve(self, *, include_body: bool) -> None:
        request = urlsplit(self.path)
        path = request.path.rstrip("/") or "/"
        if path in {"/healthz", "/api/health"}:
            payload = build_status(DATA_ROOT)
            unavailable = {
                route: item
                for route, item in payload["datasets"].items()
                if item["state"] in {"missing", "invalid"}
            }
            self._send_json(
                503 if unavailable else 200,
                {
                    "status": "degraded" if unavailable else "ok",
                    "served_at": payload["served_at"],
                    "unavailable_datasets": list(unavailable),
                    "files": {
                        route: {
                            "available": item["available"],
                            "state": item["state"],
                            "updated_at": item["updated_at"],
                        }
                        for route, item in payload["datasets"].items()
                    },
                },
                include_body=include_body,
            )
            return
        if path == "/api/status":
            self._send_json(200, build_status(DATA_ROOT), include_body=include_body)
            return
        if path == "/api/assistant/contract-analysis":
            symbol = parse_qs(request.query).get("symbol", [""])[0]
            try:
                payload = contract_analysis(DATA_ROOT, symbol)
            except Exception as exc:
                status = int(getattr(exc, "status", 502))
                code = str(getattr(exc, "code", "analysis_failed"))
                self._send_json(
                    status,
                    {"error": code, "message": str(exc)},
                    include_body=include_body,
                )
                return
            self._send_json(200, payload, include_body=include_body)
            return

        relative = ROUTES.get(path)
        if relative is None:
            self._send_json(404, {"error": "not_found"}, include_body=include_body)
            return

        target = DATA_ROOT / relative
        try:
            payload = load_json(target)
        except FileNotFoundError:
            self._send_json(
                503,
                {"error": "dataset_unavailable", "dataset": relative},
                include_body=include_body,
            )
            return
        except (OSError, json.JSONDecodeError):
            self._send_json(
                503,
                {"error": "dataset_invalid", "dataset": relative},
                include_body=include_body,
            )
            return

        self._send_json(200, payload, include_body=include_body)

    def do_GET(self) -> None:  # noqa: N802
        self._serve(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self._serve(include_body=False)

    def log_message(self, fmt: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


def main() -> None:
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

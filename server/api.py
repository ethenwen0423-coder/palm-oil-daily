#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import date, datetime, time, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


DATA_ROOT = Path(os.environ.get("PALM_OIL_DATA_ROOT", "/site/data"))
HOST = os.environ.get("PALM_OIL_API_HOST", "0.0.0.0")
PORT = int(os.environ.get("PALM_OIL_API_PORT", "8000"))
SHANGHAI = ZoneInfo("Asia/Shanghai")

ROUTES = {
    "/api/reports": "reports.json",
    "/api/oil-futures": "oil_futures.json",
    "/api/exchange-futures": "exchange_futures.json",
    "/api/quant-model-signals": "quant_model_signals.json",
    "/api/supply-demand": "supply-demand.json",
    "/api/contracts/current": "contracts/current_contracts.json",
    "/api/forecast/metrics/latest": "forecast/metrics/latest.json",
    "/api/assistant/brief": "market_assistant_brief.json",
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
        "stale_after_seconds": 60 * 60 * 72,
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
    "/api/assistant/brief": {
        "label": "AI 盯盘简报",
        "stale_after_seconds": 60 * 60 * 6,
        "timestamp_fields": ("generated_at",),
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


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


def build_status(data_root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    current = now or datetime.now(timezone.utc)
    datasets = {
        route: dataset_status(data_root, route, relative, now=current)
        for route, relative in ROUTES.items()
    }
    degraded = [route for route, item in datasets.items() if item["state"] != "ready"]
    return {
        "status": "degraded" if degraded else "ok",
        "served_at": current.astimezone(timezone.utc).isoformat(),
        "timezone": "Asia/Shanghai",
        "public_sync_interval_seconds": 120,
        "datasets": datasets,
        "degraded_datasets": degraded,
        "fixed_logic": ["otc_structure_library", "quant_model_rules"],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "PalmOilDataAPI/2"

    def _send_json(self, status: int, payload: Any, *, include_body: bool = True) -> None:
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        if include_body:
            self.wfile.write(raw)

    def _serve(self, *, include_body: bool) -> None:
        path = urlsplit(self.path).path.rstrip("/") or "/"
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

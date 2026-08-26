#!/usr/bin/env python3
"""Collect read-only HTFC Tianji evidence for the public research site."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import ProxyHandler, Request, build_opener
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
OIL_PRODUCTS = (("P", "棕榈油"), ("Y", "豆油"), ("OI", "菜油"))


class TianjiError(RuntimeError):
    """A configuration, transport, or business-response error."""


def direct_open(request: Request, *, timeout: int):
    """Bypass desktop proxy settings, matching the installed Tianji skills."""
    return build_opener(ProxyHandler({})).open(request, timeout=timeout)


def _business_data(payload: dict[str, Any]) -> Any:
    code = payload.get("errorCode", payload.get("code"))
    if code is not None and str(code) not in {"0", "1", "200"}:
        message = payload.get("errorMessage") or payload.get("message") or payload.get("msg") or "unknown error"
        raise TianjiError(f"business error [{code}]: {message}")
    return payload.get("data", payload)


class TianjiClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout: int = 60,
        opener: Callable[..., Any] = direct_open,
    ) -> None:
        self.base_url = base_url.strip().rstrip("/")
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.opener = opener
        if not self.base_url:
            raise TianjiError("HTFC_BASE_URL is not configured")
        if not self.api_key:
            raise TianjiError("HTFC_API_KEY is not configured")

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        query = urlencode({key: value for key, value in (params or {}).items() if value is not None})
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        if query:
            url = f"{url}?{query}"
        data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8") if method.upper() == "POST" else None
        request = Request(
            url,
            data=data,
            method=method.upper(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "apikey": self.api_key,
            },
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 403:
                raise TianjiError("permission denied (HTTP 403)") from exc
            raise TianjiError(f"HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise TianjiError(f"request failed: {type(exc).__name__}") from exc
        if not isinstance(payload, dict):
            raise TianjiError("response must be a JSON object")
        _business_data(payload)
        return payload


def _walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _status(error: Exception) -> dict[str, Any]:
    message = str(error)
    return {
        "status": "permission_denied" if "403" in message or "permission denied" in message else "unavailable",
        "error": message[:240],
    }


def collect_news(client: TianjiClient) -> dict[str, Any]:
    homepage = client.request("GET", "/bus/info")
    data = _business_data(homepage)
    tags = data.get("tags", []) if isinstance(data, dict) else []
    matches = [item for item in tags if isinstance(item, dict) and item.get("name") == "油脂油料"]
    if len(matches) != 1 or not matches[0].get("tid"):
        return {"status": "mapping_required", "candidates": matches, "homepage": homepage}
    tag = matches[0]
    filtered = client.request("GET", "/bus/info/filter", params={"tags": tag["tid"]})
    return {"status": "ok", "selected_tag": tag, "response": filtered}


def collect_smart_kline(client: TianjiClient) -> dict[str, Any]:
    prefix = "/htfc/htfc_research/hrms/report"
    labels_response = client.request("GET", f"{prefix}/list_report_label_tree")
    labels = _business_data(labels_response)
    rows = list(_walk_dicts(labels))
    products: dict[str, Any] = {}
    for symbol, name in OIL_PRODUCTS:
        matches = [
            item for item in rows
            if item.get("name") == name and str(item.get("leafNode")).lower() == "true"
        ]
        if len(matches) != 1:
            products[symbol] = {"status": "mapping_required", "name": name, "candidates": matches}
            continue
        label = matches[0]
        response = client.request(
            "GET",
            f"{prefix}/k/report_k_line",
            params={"varNum": label.get("code"), "period": "-1month"},
        )
        products[symbol] = {
            "status": "ok",
            "label": label,
            "period": "-1month",
            "response": response,
        }
    return {"status": "ok", "products": products}


def _report_item_value(item: dict[str, Any]) -> Any:
    for key in ("item_value", "itemValue", "value"):
        if item.get(key) not in (None, ""):
            return item[key]
    return None


def collect_reports(client: TianjiClient) -> dict[str, Any]:
    categories = client.request("GET", "/bus/report/ptypes_v2")
    rows = list(_walk_dicts(_business_data(categories)))
    products: dict[str, Any] = {}
    for symbol, name in OIL_PRODUCTS:
        aliases = {name, "菜籽油" if symbol == "OI" else name}
        matches = [item for item in rows if str(item.get("name") or item.get("label") or "") in aliases]
        usable = [item for item in matches if _report_item_value(item) is not None]
        if len(usable) != 1:
            products[symbol] = {"status": "mapping_required", "name": name, "candidates": matches}
            continue
        selected = usable[0]
        response = client.request(
            "GET",
            "/bus/report/specificList",
            params={"curPage": 1, "pageSize": 10, "item_value": _report_item_value(selected)},
        )
        products[symbol] = {"status": "ok", "category": selected, "response": response}
    return {"status": "ok", "categories": categories, "products": products}


def collect_trend(client: TianjiClient) -> dict[str, Any]:
    universe = client.request("GET", "/bus/queryExchangeFutures", params={"moduleType": 2})
    rows = list(_walk_dicts(_business_data(universe)))
    products: dict[str, Any] = {}
    for symbol, name in OIL_PRODUCTS:
        aliases = {name, "菜籽油" if symbol == "OI" else name}
        matches = [item for item in rows if str(item.get("name") or item.get("varietyName") or "") in aliases]
        codes = [(item.get("code") or item.get("varietyCode"), item) for item in matches]
        codes = [(code, item) for code, item in codes if code]
        if len(codes) != 1:
            products[symbol] = {"status": "mapping_required", "name": name, "candidates": matches}
            continue
        code, selected = codes[0]
        products[symbol] = {
            "status": "ok",
            "product": selected,
            "trend": client.request("POST", "/hrms/trend/codeTrend", body={"code": code}),
            "detail": client.request("POST", "/hrms/trend/codeDetail", body={"code": code}),
        }
    return {"status": "ok", "products": products}


def collect(client: TianjiClient, now: datetime | None = None) -> dict[str, Any]:
    observed = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI)
    modules: dict[str, Any] = {}
    collectors = {
        "news_flash": collect_news,
        "smart_kline": collect_smart_kline,
        "research_reports": collect_reports,
        "trend_compass": collect_trend,
    }
    for name, collector in collectors.items():
        try:
            modules[name] = collector(client)
        except Exception as exc:  # each read-only module degrades independently
            modules[name] = _status(exc)
    available = sum(module.get("status") == "ok" for module in modules.values())
    return {
        "schema_version": 1,
        "generated_at": observed.isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "source": "HTFC Tianji",
        "mode": "read_only",
        "status": "ok" if available == len(modules) else "partial" if available else "unavailable",
        "available_modules": available,
        "modules": modules,
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/htfc_tianji.json"))
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        client = TianjiClient(
            os.environ.get("HTFC_BASE_URL", ""),
            os.environ.get("HTFC_API_KEY", ""),
            timeout=args.timeout,
        )
        payload = collect(client)
    except TianjiError as exc:
        payload = {
            "schema_version": 1,
            "generated_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            "timezone": "Asia/Shanghai",
            "source": "HTFC Tianji",
            "mode": "read_only",
            "status": "unavailable",
            "available_modules": 0,
            "modules": {},
            "error": str(exc),
        }
    atomic_write(args.output, payload)
    print(json.dumps({"status": payload["status"], "output": str(args.output)}, ensure_ascii=False))
    return 2 if args.strict and payload["status"] != "ok" else 0


if __name__ == "__main__":
    raise SystemExit(main())

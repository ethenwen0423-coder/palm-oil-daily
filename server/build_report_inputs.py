#!/usr/bin/env python3
"""Build an auditable report source run from server-owned live datasets."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
PRODUCT_KEYS = {
    "P": "palm_oil",
    "Y": "soybean_oil",
    "OI": "rapeseed_oil",
}


class ReportInputError(RuntimeError):
    """Raised when live data cannot support a governed report run."""


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportInputError(f"cannot read server dataset: {path}") from exc
    if not isinstance(payload, dict):
        raise ReportInputError(f"server dataset must be a JSON object: {path}")
    return payload


def load_optional_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return load_object(path)


def load_list(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportInputError(f"cannot read server dataset: {path}") from exc
    if not isinstance(payload, list):
        raise ReportInputError(f"server dataset must be a list: {path}")
    return [item for item in payload if isinstance(item, dict)]


def parse_dataset_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ReportInputError(f"missing freshness timestamp: {label}")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReportInputError(f"invalid freshness timestamp: {label}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def validate_freshness(
    datasets: dict[str, tuple[dict[str, Any], tuple[str, ...]]],
    *,
    kind: str,
    now: datetime,
) -> dict[str, str]:
    max_ages = {
        "daily": {
            "oil_futures": timedelta(hours=8),
            "exchange_futures": timedelta(hours=18),
            "quant_model_signals": timedelta(hours=18),
            "supply_demand": timedelta(hours=36),
            "contracts": timedelta(hours=72),
            "htfc_tianji": timedelta(hours=2),
            "market_watch": timedelta(hours=2),
        },
        "weekend": {
            "oil_futures": timedelta(days=4),
            "exchange_futures": timedelta(days=4),
            "quant_model_signals": timedelta(days=4),
            "supply_demand": timedelta(hours=36),
            "contracts": timedelta(days=7),
            "htfc_tianji": timedelta(hours=24),
            "market_watch": timedelta(hours=24),
        },
    }[kind]
    observed: dict[str, str] = {}
    for label, (payload, fields) in datasets.items():
        raw = next((payload.get(field) for field in fields if payload.get(field)), None)
        timestamp = parse_dataset_timestamp(raw, label)
        age = now - timestamp
        if age < timedelta(minutes=-5):
            raise ReportInputError(f"future-dated server dataset: {label}")
        if age > max_ages[label]:
            raise ReportInputError(
                f"stale server dataset: {label} age={int(age.total_seconds())}s"
            )
        observed[label] = timestamp.isoformat(timespec="seconds")
    return observed


def as_number(value: Any) -> float | None:
    if value in (None, "", "-", "需进一步核验", "待更新"):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def htfc_report_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a bounded institutional-evidence view without rewriting source claims."""
    modules = payload.get("modules") if isinstance(payload.get("modules"), dict) else {}
    news = modules.get("news_flash") if isinstance(modules.get("news_flash"), dict) else {}
    news_response = news.get("response") if isinstance(news.get("response"), dict) else {}
    news_items = news_response.get("data") if isinstance(news_response.get("data"), list) else []
    kline = modules.get("smart_kline") if isinstance(modules.get("smart_kline"), dict) else {}
    products = kline.get("products") if isinstance(kline.get("products"), dict) else {}
    kline_evidence: dict[str, Any] = {}
    for symbol, product in products.items():
        if not isinstance(product, dict) or product.get("status") != "ok":
            continue
        response = product.get("response") if isinstance(product.get("response"), dict) else {}
        data = response.get("data") if isinstance(response.get("data"), dict) else {}
        market = data.get("marketData") if isinstance(data.get("marketData"), dict) else {}
        closes = market.get("closePrice") if isinstance(market.get("closePrice"), list) else []
        label = product.get("label") if isinstance(product.get("label"), dict) else {}
        kline_evidence[str(symbol)] = {
            "name": label.get("name"),
            "report_date": data.get("kLineAiReportDate"),
            "latest_close": closes[-1] if closes else None,
            "ai_interpretation": data.get("kLineAiContent"),
            "upstream_response_code": response.get("code"),
        }
    return {
        "source": "HTFC Tianji",
        "source_role": "institutional_news_and_research_not_official_statistics",
        "status": payload.get("status"),
        "fetched_at": payload.get("generated_at"),
        "module_status": {
            name: value.get("status")
            for name, value in modules.items()
            if isinstance(value, dict)
        },
        "oil_news": [item for item in news_items if isinstance(item, dict)][:10],
        "smart_kline": kline_evidence,
    }


def market_watch_evidence(payload: dict[str, Any], now: datetime) -> dict[str, Any]:
    """Apply oil_report_freshness rules to the server event/research feed."""
    fresh: list[dict[str, Any]] = []
    background: list[dict[str, Any]] = []
    for item in payload.get("events", []):
        if not isinstance(item, dict) or item.get("kind") != "event":
            continue
        try:
            observed = parse_dataset_timestamp(item.get("observed_at"), "market_watch.event")
        except ReportInputError:
            continue
        age = now - observed
        bounded = {
            key: item.get(key)
            for key in (
                "id", "title", "summary", "interpretation", "impact", "scope",
                "source", "url", "observed_at", "evidence_ids",
            )
        }
        bounded["freshness_level"] = "Level 1" if age <= timedelta(hours=24) else "Level 3"
        bounded["mainline_eligible"] = age <= timedelta(hours=24)
        if age <= timedelta(hours=24):
            fresh.append(bounded)
        elif age <= timedelta(days=7):
            background.append(bounded)
    sources = [
        {
            "name": item.get("name"),
            "state": item.get("state"),
            "detail": item.get("detail"),
        }
        for item in payload.get("sources", [])
        if isinstance(item, dict) and item.get("name") != "全量期货行情"
    ]
    ready_states = {"ready", "degraded"}
    return {
        "skill": "oil_report_freshness",
        "as_of": payload.get("events_updated_at") or payload.get("generated_at"),
        "today_new_drivers": fresh[:20],
        "continuing_background": background[:10],
        "source_status": sources,
        "ready_source_count": sum(item.get("state") in ready_states for item in sources),
        "fresh_event_count": len(fresh),
        "mainline_policy": "Only Level 1 events may support today's mainline; older events are background only.",
    }
def rank_one_contracts(
    payload: dict[str, Any],
    *,
    report_date: str | None = None,
) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for item in payload.get("contracts", []):
        if not isinstance(item, dict):
            continue
        product = str(item.get("product") or "").upper()
        try:
            rank = int(item.get("contract_rank"))
        except (TypeError, ValueError):
            continue
        if product in PRODUCT_KEYS and rank == 1:
            if product in selected:
                raise ReportInputError(f"duplicate rank-1 contract: {product}")
            selected[product] = item
    missing = sorted(set(PRODUCT_KEYS) - set(selected))
    if missing:
        raise ReportInputError(f"missing rank-1 contracts: {', '.join(missing)}")
    for product, item in selected.items():
        trade_date = str(item.get("trade_date") or "").strip()
        if report_date and trade_date:
            try:
                observed = datetime.fromisoformat(trade_date).date()
                expected = datetime.fromisoformat(report_date).date()
            except ValueError as exc:
                raise ReportInputError(
                    f"invalid rank-1 contract trade date: {product}={trade_date}"
                ) from exc
            if observed > expected:
                raise ReportInputError(
                    f"future-dated rank-1 contract: {product}={trade_date} report={report_date}"
                )
        score = item.get("score")
        strategy = item.get("strategy_recommendation")
        if not isinstance(score, dict) or not score.get("stance"):
            raise ReportInputError(f"missing deterministic score output: {product}")
        if not isinstance(strategy, dict):
            raise ReportInputError(f"missing deterministic strategy output: {product}")
        for field in ("lower_watch", "upper_watch", "invalidation"):
            if strategy.get(field) in (None, ""):
                raise ReportInputError(
                    f"missing deterministic strategy field: {product}.{field}"
                )
    return selected


def market_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": item.get("name") or item.get("product_name") or item.get("product"),
        "status": "ok" if as_number(item.get("price")) is not None else "missing",
        "source": item.get("source") or "需进一步核验",
        "fetched_at": item.get("trade_date"),
        "published_at": item.get("trade_date"),
        "price": as_number(item.get("price")),
        "change": None,
        "change_pct": as_number(item.get("change")),
        "contract": item.get("contract") or item.get("symbol"),
        "open": as_number(item.get("open")),
        "high": as_number(item.get("high")),
        "low": as_number(item.get("low")),
        "close": as_number(item.get("preclose")),
        "settlement": as_number(item.get("settle")),
        "volume": as_number(item.get("volume")),
        "open_interest": as_number(item.get("open_interest")),
        "verification": item.get("verification") or "需进一步核验",
        "score": item.get("score"),
        "strategy_recommendation": item.get("strategy_recommendation"),
        "view": item.get("view"),
        "technical_detail": item.get("technical_detail") or [],
        "fundamental_detail": item.get("fundamental_detail") or [],
        "note": item.get("note"),
        "quality_note": item.get("quality_note"),
    }


def contract_structure(payload: dict[str, Any], report_date: str) -> dict[str, list[dict[str, Any]]]:
    """Expose auditable rank-1/rank-2 curves without weakening rank-1 gates."""
    result: dict[str, list[dict[str, Any]]] = {}
    expected = datetime.fromisoformat(report_date).date()
    for product in PRODUCT_KEYS:
        rows: list[dict[str, Any]] = []
        for item in payload.get("contracts", []):
            if not isinstance(item, dict) or str(item.get("product") or "").upper() != product:
                continue
            try:
                rank = int(item.get("contract_rank"))
            except (TypeError, ValueError):
                continue
            if rank not in {1, 2}:
                continue
            trade_date = str(item.get("trade_date") or "").strip()
            try:
                observed = datetime.fromisoformat(trade_date).date()
            except ValueError as exc:
                raise ReportInputError(
                    f"invalid contract-structure trade date: {product} rank={rank}"
                ) from exc
            if observed > expected:
                raise ReportInputError(
                    f"future-dated contract structure: {product} rank={rank} {trade_date}"
                )
            price = as_number(item.get("price"))
            if price is None:
                continue
            rows.append(
                {
                    "contract_rank": rank,
                    "contract": item.get("contract") or item.get("symbol"),
                    "price": price,
                    "change_pct": as_number(item.get("change")),
                    "trade_date": trade_date,
                    "volume": as_number(item.get("volume")),
                    "open_interest": as_number(item.get("open_interest")),
                    "source": item.get("source") or "需进一步核验",
                }
            )
        result[product] = sorted(rows, key=lambda row: int(row["contract_rank"]))
    return result


def first_contract(payload: dict[str, Any], product: str) -> dict[str, Any] | None:
    for item in payload.get("contracts", []):
        if isinstance(item, dict) and str(item.get("product") or "").upper() == product:
            return item
    return None


def latest_official_metric(country: dict[str, Any], key: str) -> dict[str, Any] | None:
    metric = (country.get("metrics") or {}).get(key)
    if not isinstance(metric, dict):
        return None
    series = [item for item in metric.get("series", []) if isinstance(item, dict)]
    if not series:
        return None
    latest = series[-1]
    previous = series[-2] if len(series) > 1 else None
    value = as_number(latest.get("value"))
    previous_value = as_number(previous.get("value")) if previous else None
    change_pct = None
    if value is not None and previous_value not in (None, 0):
        change_pct = round((value - previous_value) / previous_value * 100, 2)
    source = country.get("source") if isinstance(country.get("source"), dict) else {}
    return {
        "label": metric.get("label") or key,
        "period": latest.get("period"),
        "value": value,
        "unit": metric.get("unit"),
        "display_unit": metric.get("display_unit"),
        "published_at": latest.get("published_at"),
        "source": source.get("name"),
        "source_url": latest.get("source_url") or source.get("url"),
        "previous_period": previous.get("period") if previous else None,
        "previous_value": previous_value,
        "change_pct": change_pct,
    }


def previous_report(
    data_root: Path,
    report_date: str,
    kind: str,
) -> dict[str, Any] | None:
    reports_path = data_root / "reports.json"
    if not reports_path.is_file():
        return None
    expected_kind = "weekend" if kind == "weekend" else "daily"
    candidates = [
        item
        for item in load_list(reports_path)
        if str(item.get("date") or "") < report_date
        and str(item.get("kind") or "") == expected_kind
    ]
    if not candidates:
        return None
    item = max(candidates, key=lambda row: str(row.get("date") or ""))
    return {
        "date": item.get("date"),
        "title": item.get("title"),
        "headline": item.get("headline"),
        "content": item.get("content"),
        "updated_at": item.get("updated_at"),
    }


def previous_source_snapshot(
    runtime_root: Path,
    report_date: str,
    kind: str,
) -> dict[str, Any] | None:
    candidates: list[tuple[str, Path]] = []
    for path in (runtime_root / "source_runs").glob(
        f"*-{kind}/raw/futures_market_data.json"
    ):
        run_date = path.parents[1].name.removesuffix(f"-{kind}")
        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", run_date) and run_date < report_date:
            candidates.append((run_date, path))
    if not candidates:
        return None
    run_date, path = max(candidates, key=lambda item: item[0])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "date": run_date,
        "timestamp": payload.get("timestamp"),
        "domestic": payload.get("domestic") or {},
        "external": payload.get("external") or {},
        "fundamental": payload.get("fundamental") or {},
    }


def market_comparison(
    current: dict[str, Any],
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    if not previous:
        return {"status": "unavailable", "reason": "no prior structured snapshot"}
    changes: dict[str, Any] = {}
    previous_domestic = previous.get("domestic") or {}
    for key, row in (current.get("domestic") or {}).items():
        old = previous_domestic.get(key) if isinstance(previous_domestic, dict) else None
        old = old if isinstance(old, dict) else {}
        current_price = as_number(row.get("price")) if isinstance(row, dict) else None
        previous_price = as_number(old.get("price"))
        current_contract = row.get("contract") if isinstance(row, dict) else None
        previous_contract = old.get("contract")
        comparable = bool(
            current_price is not None
            and previous_price not in (None, 0)
            and current_contract == previous_contract
        )
        changes[key] = {
            "current_contract": current_contract,
            "previous_contract": previous_contract,
            "current_price": current_price,
            "previous_price": previous_price,
            "comparable": comparable,
            "price_change": round(current_price - previous_price, 2) if comparable else None,
            "change_pct": round((current_price - previous_price) / previous_price * 100, 2)
            if comparable
            else None,
        }
    return {
        "status": "ready",
        "previous_date": previous.get("date"),
        "previous_timestamp": previous.get("timestamp"),
        "products": changes,
    }


def build_snapshot(
    data_root: Path,
    runtime_root: Path,
    report_date: str,
    kind: str,
    now: datetime,
) -> dict[str, Any]:
    oil = load_object(data_root / "oil_futures.json")
    supply = load_object(data_root / "supply-demand.json")
    exchange = load_object(data_root / "exchange_futures.json")
    quant = load_object(data_root / "quant_model_signals.json")
    contracts = load_object(data_root / "contracts" / "current_contracts.json")
    htfc = load_optional_object(data_root / "htfc_tianji.json")
    market_watch = load_optional_object(data_root / "market_watch.json")
    watch_evidence = market_watch_evidence(market_watch, now)
    selected = rank_one_contracts(oil, report_date=report_date)

    external: dict[str, Any] = {}
    for product, key in (("FCPO", "bmd_palm_oil"), ("CPOTR", "indonesia_cpo_spot")):
        item = first_contract(oil, product)
        if item:
            external[key] = market_record(item)

    domestic = {
        PRODUCT_KEYS[product]: market_record(item)
        for product, item in selected.items()
    }
    p_price = as_number(domestic["palm_oil"].get("price"))
    y_price = as_number(domestic["soybean_oil"].get("price"))
    oi_price = as_number(domestic["rapeseed_oil"].get("price"))
    malaysia = ((supply.get("countries") or {}).get("malaysia") or {})
    official_metrics = {
        key: value
        for key in ("production", "exports", "stocks")
        if (value := latest_official_metric(malaysia, key)) is not None
    }
    snapshot = {
        "date": report_date,
        "timestamp": now.isoformat(timespec="seconds"),
        "market_status": "服务器自动采集",
        "source_mode": "server_live_data",
        "domestic": domestic,
        "contract_structure": contract_structure(oil, report_date),
        "external": external,
        "fundamental": {
            "official_supply_demand": {
                "status": supply.get("update_status") or "需进一步核验",
                "source": "MPOB/GAPKI/USDA official checks",
                "fetched_at": supply.get("checked_at") or supply.get("generated_at"),
                "summary": supply.get("update_message") or "需进一步核验",
                "latest_metrics": official_metrics,
            },
            "spread": {
                "soybean_palm_spread": {
                    "name": "豆棕价差",
                    "price": round(y_price - p_price, 2)
                    if y_price is not None and p_price is not None
                    else None,
                    "unit": "元/吨",
                    "as_of": oil.get("updated_at"),
                },
                "rapeseed_soybean_spread": {
                    "name": "菜豆油价差",
                    "price": round(oi_price - y_price, 2)
                    if oi_price is not None and y_price is not None
                    else None,
                    "unit": "元/吨",
                    "as_of": oil.get("updated_at"),
                },
            },
            "exchange_context": {
                "status": "ok" if exchange.get("contracts") else "missing",
                "source": "server exchange collector",
                "fetched_at": exchange.get("updated_at"),
                "summary": f"core contracts={len(exchange.get('contracts') or [])}",
            },
        },
        "institutional_evidence": htfc_report_evidence(htfc),
        "news_and_research_evidence": watch_evidence,
        "skill_chain": [
            "market_data_skill",
            "data_quality_gate_skill",
            "forecast_generation_feedback",
            "oil_report_freshness",
            "report_writer_skill",
            "headline_skill",
            "report_quality_gate",
            "forecast_tracking_skill",
        ],
        "server_evidence": {
            "oil_futures_updated_at": oil.get("updated_at"),
            "exchange_futures_updated_at": exchange.get("updated_at"),
            "quant_generated_at": quant.get("generated_at"),
            "quant_market_updated_at": quant.get("market_updated_at"),
            "supply_checked_at": supply.get("checked_at") or supply.get("generated_at"),
            "contracts_generated_at": contracts.get("generated_at"),
            "htfc_generated_at": htfc.get("generated_at"),
            "fixed_logic": ["otc_structure_library", "quant_model_rules"],
            "market_references": oil.get("market_references") or [],
        },
    }
    prior_snapshot = previous_source_snapshot(runtime_root, report_date, kind)
    snapshot["research_history"] = {
        "previous_report": previous_report(data_root, report_date, kind),
        "previous_source_snapshot": prior_snapshot,
        "market_comparison": market_comparison(snapshot, prior_snapshot),
    }
    return snapshot


def build_manifest(
    data_root: Path,
    report_date: str,
    kind: str,
    now: datetime,
) -> dict[str, Any]:
    oil = load_object(data_root / "oil_futures.json")
    supply = load_object(data_root / "supply-demand.json")
    exchange = load_object(data_root / "exchange_futures.json")
    quant = load_object(data_root / "quant_model_signals.json")
    contracts = load_object(data_root / "contracts" / "current_contracts.json")
    htfc = load_optional_object(data_root / "htfc_tianji.json")
    market_watch = load_optional_object(data_root / "market_watch.json")
    watch_evidence = market_watch_evidence(market_watch, now)
    freshness_inputs = {
            "oil_futures": (oil, ("updated_at",)),
            "exchange_futures": (exchange, ("updated_at",)),
            "quant_model_signals": (quant, ("market_updated_at", "generated_at")),
            "supply_demand": (supply, ("checked_at", "generated_at")),
            "contracts": (contracts, ("generated_at",)),
        }
    if htfc.get("generated_at"):
        freshness_inputs["htfc_tianji"] = (htfc, ("generated_at",))
    if market_watch.get("events_updated_at") or market_watch.get("generated_at"):
        freshness_inputs["market_watch"] = (
            market_watch,
            ("events_updated_at", "generated_at"),
        )
    freshness = validate_freshness(
        freshness_inputs,
        kind=kind,
        now=now,
    )
    symbols = [
        str(item.get("symbol") or "")
        for rows in (contracts.get("products") or {}).values()
        if isinstance(rows, list)
        for item in rows
        if isinstance(item, dict) and item.get("symbol")
    ]
    return {
        "date": report_date,
        "kind": kind,
        "generated_at": now.isoformat(timespec="seconds"),
        "source_mode": "governed_skill_chain",
        "skills": {
            "market_data_skill": {"installed": True, "adapter": "server-market-collector"},
            "data_quality_gate_skill": {"installed": True},
            "forecast_generation_feedback": {"installed": True},
            "oil_report_freshness": {"installed": True},
            "report_writer_skill": {"installed": True},
            "headline_skill": {"installed": True},
            "report_quality_gate": {"installed": True},
            "forecast_tracking_skill": {"installed": True},
            "htfc-tianji-router": {"installed": True, "mode": "read_only"},
        },
        "environment": {"server_owned": True},
        "freshness": freshness,
        "contract_discovery": {
            "path": str(data_root / "contracts" / "current_contracts.json"),
            "symbols": list(dict.fromkeys(symbols)),
        },
        "results": [
            {
                "name": "futures_oil_fetch_market_data",
                "status": "ok",
                "returncode": 0,
                "source": "server live-data/oil_futures.json",
                "observed_at": oil.get("updated_at"),
            },
            {
                "name": "server_official_supply_check",
                "status": "ok" if supply.get("checked_at") else "failed",
                "returncode": 0 if supply.get("checked_at") else 2,
                "source": "server live-data/supply-demand.json",
                "observed_at": supply.get("checked_at"),
            },
            {
                "name": "htfc_tianji_read_only",
                "status": "ok" if htfc.get("available_modules") else "partial",
                "returncode": 0,
                "source": "server live-data/htfc_tianji.json",
                "observed_at": htfc.get("generated_at"),
            },
            {
                "name": "news_and_research_skill_sources",
                "status": "ok"
                if watch_evidence["ready_source_count"] > 0
                and watch_evidence["fresh_event_count"] > 0
                else "failed",
                "returncode": 0
                if watch_evidence["ready_source_count"] > 0
                and watch_evidence["fresh_event_count"] > 0
                else 2,
                "source": "server live-data/market_watch.json",
                "observed_at": market_watch.get("events_updated_at"),
            },
            {
                "name": "oil_report_freshness",
                "status": "ok"
                if watch_evidence["fresh_event_count"] > 0
                else "failed",
                "returncode": 0
                if watch_evidence["fresh_event_count"] > 0
                else 2,
                "source": "news_and_research_evidence.today_new_drivers",
                "observed_at": market_watch.get("events_updated_at"),
            },
        ],
    }


def write_source_run(
    data_root: Path,
    runtime_root: Path,
    report_date: str,
    kind: str,
    now: datetime,
    *,
    allow_date_override: bool = False,
) -> dict[str, Any]:
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", report_date):
        raise ReportInputError("report date must be YYYY-MM-DD")
    if now.date().isoformat() != report_date and not allow_date_override:
        raise ReportInputError("server report inputs may only be built for the current date")
    run_root = runtime_root / "source_runs" / f"{report_date}-{kind}"
    raw_root = run_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(data_root, report_date, kind, now)
    snapshot = build_snapshot(data_root, runtime_root, report_date, kind, now)
    raw_path = raw_root / "futures_market_data.json"
    raw_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if kind == "weekend":
        (raw_root / "futures_market_data.weekly_compatible.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (run_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "ok",
        "report_date": report_date,
        "kind": kind,
        "run_root": str(run_root),
        "manifest": str(run_root / "manifest.json"),
        "snapshot": str(raw_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--kind", choices=("daily", "weekend"), required=True)
    parser.add_argument("--now")
    args = parser.parse_args()
    try:
        payload = write_source_run(
            args.data_root.resolve(),
            args.runtime_root.resolve(),
            args.date,
            args.kind,
            parse_now(args.now),
        )
    except (OSError, ReportInputError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate a source-grounded AI brief for the 24h market-assistant page."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "market_assistant_brief.json"
SCHEMA = ROOT / "references" / "market_assistant_brief.schema.json"
SHANGHAI = ZoneInfo("Asia/Shanghai")
NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")

SOURCE_FILES = {
    "reports": DATA_DIR / "reports.json",
    "oil-futures": DATA_DIR / "oil_futures.json",
    "exchange-futures": DATA_DIR / "exchange_futures.json",
    "quant-model-signals": DATA_DIR / "quant_model_signals.json",
    "supply-demand": DATA_DIR / "supply-demand.json",
    "forecast-metrics": DATA_DIR / "forecast" / "metrics" / "latest.json",
    "contracts": DATA_DIR / "contracts" / "current_contracts.json",
    "htfc-tianji": DATA_DIR / "htfc_tianji.json",
    "market-watch": DATA_DIR / "market_watch.json",
}
MARKET_STATES = {"偏强", "震荡", "偏弱", "分化", "数据不足"}
PRIORITIES = {"高", "中", "低"}
TRIGGERS = {
    "上破观察位",
    "下破观察位",
    "波动扩大",
    "数据恢复",
    "数据转为延迟",
    "报告更新",
    "官方数据更新",
}
ACTION_STATUSES = {"completed", "monitoring", "blocked"}
NEXT_CHECKS = {
    "下一次行情刷新",
    "下一次报告更新",
    "下一次官方数据检查",
    "数据恢复后",
    "持续监控",
}
CONFIDENCE_LEVELS = {"高", "中", "低"}
SECTOR_GROUPS = {
    "油脂油料": {"油脂油料"},
    "黑色建材": {"黑色建材", "黑色金属"},
    "能源化工": {"能化材料", "能源化工"},
    "有色新能源": {"有色金属", "新能源材料"},
    "贵金属": {"贵金属"},
    "金融期货": {"利率期货", "股指期货"},
    "农产品": {"谷物饲料", "软商品"},
    "航运浆纸": {"造纸航运"},
}


class BriefError(RuntimeError):
    """A source, model-output, or grounding error."""


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BriefError(f"缺少 AI 简报输入：{display_path(path)}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise BriefError(f"AI 简报输入无法解析：{display_path(path)}") from exc


def as_number(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "需进一步核验", "待更新"):
            return None
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def clean_text(value: Any, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def evidence_record(
    evidence_id: str,
    source: str,
    label: str,
    value: str,
    *,
    observed_at: str = "",
    detail: str = "",
) -> dict[str, str]:
    return {
        "id": evidence_id,
        "source": source,
        "label": clean_text(label, 80),
        "value": clean_text(value, 160),
        "observed_at": clean_text(observed_at, 40),
        "detail": clean_text(detail, 220),
    }


def build_context(payloads: dict[str, Any]) -> dict[str, Any]:
    reports = payloads["reports"] if isinstance(payloads["reports"], list) else []
    oil = payloads["oil-futures"] if isinstance(payloads["oil-futures"], dict) else {}
    exchange = payloads["exchange-futures"] if isinstance(payloads["exchange-futures"], dict) else {}
    quant = payloads["quant-model-signals"] if isinstance(payloads["quant-model-signals"], dict) else {}
    supply = payloads["supply-demand"] if isinstance(payloads["supply-demand"], dict) else {}
    forecast = payloads["forecast-metrics"] if isinstance(payloads["forecast-metrics"], dict) else {}
    contracts = payloads["contracts"] if isinstance(payloads["contracts"], dict) else {}
    htfc = payloads.get("htfc-tianji") if isinstance(payloads.get("htfc-tianji"), dict) else {}
    market_watch = payloads.get("market-watch") if isinstance(payloads.get("market-watch"), dict) else {}

    evidence: list[dict[str, str]] = []
    latest_report = reports[0] if reports and isinstance(reports[0], dict) else {}
    if latest_report:
        report_date = clean_text(latest_report.get("date"), 20) or "latest"
        evidence.append(
            evidence_record(
                f"report:{report_date}",
                "reports",
                clean_text(latest_report.get("headline") or latest_report.get("title") or "最新研究报告", 80),
                report_date,
                observed_at=clean_text(latest_report.get("generated_at") or latest_report.get("date"), 40),
                detail=clean_text(latest_report.get("summary"), 220),
            )
        )

    oil_contracts = oil.get("contracts") if isinstance(oil.get("contracts"), list) else []
    selected_oil = [
        item
        for item in oil_contracts
        if isinstance(item, dict)
        and (
            item.get("contract_rank") == 1
            or str(item.get("symbol") or "").upper() in {"FCPO", "CPOTR"}
        )
    ][:5]
    for index, item in enumerate(selected_oil):
        identity = clean_text(item.get("contract") or item.get("symbol") or item.get("product") or index, 50)
        price = clean_text(item.get("price") or "需进一步核验", 40)
        change = clean_text(item.get("change") or "需进一步核验", 40)
        score = item.get("score") if isinstance(item.get("score"), dict) else {}
        detail = "；".join(
            part
            for part in (
                clean_text(score.get("stance"), 30),
                clean_text(item.get("view"), 150),
            )
            if part
        )
        evidence.append(
            evidence_record(
                f"oil:{identity}",
                "oil-futures",
                clean_text(item.get("name") or item.get("product") or item.get("symbol"), 60),
                f"{price}；涨跌 {change}",
                observed_at=clean_text(oil.get("updated_at"), 40),
                detail=detail,
            )
        )

    exchange_contracts = exchange.get("contracts") if isinstance(exchange.get("contracts"), list) else []
    live_quotes = market_watch.get("quotes") if isinstance(market_watch.get("quotes"), list) else []
    sector_contracts = live_quotes or exchange_contracts
    sector_observed_at = market_watch.get("generated_at") if live_quotes else exchange.get("updated_at")
    priced_exchange = [
        item
        for item in sector_contracts
        if isinstance(item, dict) and as_number(item.get("change_pct")) is not None
    ]
    priced_exchange.sort(key=lambda item: abs(as_number(item.get("change_pct")) or 0), reverse=True)
    sector_evidence_ids: dict[str, str] = {}
    for sector, categories in SECTOR_GROUPS.items():
        members = [
            item for item in priced_exchange
            if clean_text(item.get("category"), 40) in categories
        ]
        if not members:
            continue
        ranked = sorted(
            members,
            key=lambda item: as_number(item.get("change_pct")) or 0,
            reverse=True,
        )
        leader = ranked[0]
        laggard = ranked[-1]
        average = sum(as_number(item.get("change_pct")) or 0 for item in members) / len(members)
        evidence_id = f"sector:{sector}"
        sector_evidence_ids[sector] = evidence_id
        evidence.append(
            evidence_record(
                evidence_id,
                "market-watch" if live_quotes else "exchange-futures",
                f"{sector}板块主力表现",
                (
                    f"平均涨跌 {average:+.2f}%；"
                    f"领涨 {clean_text(leader.get('name') or leader.get('product') or leader.get('symbol'), 30)} "
                    f"{(as_number(leader.get('change_pct')) or 0):+.2f}%；"
                    f"领跌 {clean_text(laggard.get('name') or laggard.get('product') or laggard.get('symbol'), 30)} "
                    f"{(as_number(laggard.get('change_pct')) or 0):+.2f}%"
                ),
                observed_at=clean_text(sector_observed_at, 40),
                detail=(
                    f"覆盖 {len(members)} 个主力合约；"
                    + "、".join(
                        f"{clean_text(item.get('name') or item.get('product') or item.get('symbol'), 24)} "
                        f"{(as_number(item.get('change_pct')) or 0):+.2f}%"
                        for item in ranked[:4]
                    )
                ),
            )
        )
    for index, item in enumerate(priced_exchange[:8]):
        identity = clean_text(item.get("symbol") or item.get("contract") or item.get("product") or index, 50)
        price = clean_text(item.get("price") or "需进一步核验", 40)
        change = clean_text(item.get("change_pct"), 30)
        evidence.append(
            evidence_record(
                f"exchange:{identity}",
                "market-watch" if live_quotes else "exchange-futures",
                clean_text(item.get("name") or item.get("product") or item.get("symbol"), 60),
                f"{price}；涨跌 {change}%",
                observed_at=clean_text(sector_observed_at, 40),
                detail=clean_text((item.get("fundamental") or {}).get("summary"), 180),
            )
        )

    # Always expose oil technical and observed fundamental evidence explicitly.
    # The generic exchange-price records above are insufficient for a grounded
    # weekend brief because prices may be unchanged while the evidence remains
    # decision-relevant.
    for index, item in enumerate(exchange_contracts):
        if not isinstance(item, dict):
            continue
        symbol = clean_text(item.get("symbol"), 30).upper()
        variety_match = re.match(r"[A-Z]+", symbol)
        variety = variety_match.group(0) if variety_match else ""
        if variety not in {"P", "Y", "OI"}:
            continue
        technical = item.get("technical") if isinstance(item.get("technical"), dict) else {}
        indicators = technical.get("indicators") if isinstance(technical.get("indicators"), dict) else {}
        if technical.get("status") == "ok":
            evidence.append(
                evidence_record(
                    f"technical:{symbol or index}",
                    "exchange-futures",
                    f"{clean_text(item.get('product') or symbol, 40)}最近收盘技术结构",
                    (
                        f"{clean_text(technical.get('trend') or '待判断', 20)}；"
                        f"收盘 {clean_text(technical.get('snapshot_price'), 30)}；"
                        f"MA20 {clean_text(indicators.get('MA20'), 30)}；"
                        f"RSI12 {clean_text(indicators.get('RSI12'), 30)}"
                    ),
                    observed_at=clean_text(technical.get("snapshot_date") or item.get("trade_date"), 40),
                    detail=clean_text(technical.get("summary"), 220),
                )
            )
        fundamental = item.get("fundamental") if isinstance(item.get("fundamental"), dict) else {}
        factors = fundamental.get("factors") if isinstance(fundamental.get("factors"), list) else []
        observed = [
            factor for factor in factors
            if isinstance(factor, dict) and "跟踪框架" not in clean_text(factor.get("title"), 40)
        ][:2]
        for factor_index, factor in enumerate(observed):
            evidence.append(
                evidence_record(
                    f"fundamental:{symbol or index}:{factor_index}",
                    "exchange-futures",
                    f"{clean_text(item.get('product') or symbol, 40)}{clean_text(factor.get('title'), 50)}",
                    clean_text(factor.get("text") or "需进一步核验", 160),
                    observed_at=clean_text(factor.get("date") or exchange.get("fundamental_updated_at"), 40),
                    detail=clean_text(fundamental.get("summary"), 220),
                )
            )

    model_id = clean_text(quant.get("default_model_id"), 80)
    model_contracts = quant.get("model_contracts")
    selected_signals = (
        model_contracts.get(model_id)
        if model_id and isinstance(model_contracts, dict)
        else []
    )
    if not isinstance(selected_signals, list):
        selected_signals = []
    selected_signals = [
        item
        for item in selected_signals
        if isinstance(item, dict) and item.get("rank") == 1
    ][:5]
    for index, item in enumerate(selected_signals):
        signals = item.get("signals") if isinstance(item.get("signals"), dict) else {}
        flat_signal = signals.get("flat") if isinstance(signals.get("flat"), dict) else {}
        symbol = clean_text(item.get("symbol") or index, 40)
        action = clean_text(flat_signal.get("action") or "需进一步核验", 60)
        execution = clean_text(flat_signal.get("execution") or "需进一步核验", 80)
        rationale = flat_signal.get("rationale")
        rationale_text = "；".join(
            clean_text(value, 100)
            for value in (rationale[:2] if isinstance(rationale, list) else [])
            if clean_text(value, 100)
        )
        detail = "；".join(
            value
            for value in (
                clean_text(item.get("model_scope_label"), 60),
                rationale_text,
            )
            if value
        )
        evidence.append(
            evidence_record(
                f"quant:{model_id or 'default'}:{symbol}",
                "quant-model-signals",
                f"{clean_text(item.get('product_name') or item.get('product') or symbol, 50)}动态量化信号",
                f"{action}；执行 {execution}",
                observed_at=clean_text(
                    quant.get("market_updated_at") or quant.get("generated_at"),
                    40,
                ),
                detail=detail,
            )
        )

    evidence.append(
        evidence_record(
            "supply:official-check",
            "supply-demand",
            "官方供需资料检查",
            clean_text(supply.get("update_message") or supply.get("update_status") or "需进一步核验", 160),
            observed_at=clean_text(supply.get("checked_at") or supply.get("generated_at"), 40),
            detail="MPOB、GAPKI、USDA 的公开检查状态；无更新不等于数据缺失。",
        )
    )

    htfc_modules = htfc.get("modules") if isinstance(htfc.get("modules"), dict) else {}
    news_module = htfc_modules.get("news_flash") if isinstance(htfc_modules.get("news_flash"), dict) else {}
    news_response = news_module.get("response") if isinstance(news_module.get("response"), dict) else {}
    news_items = news_response.get("data") if isinstance(news_response.get("data"), list) else []
    for item in [row for row in news_items if isinstance(row, dict)][:3]:
        identity = clean_text(item.get("id") or item.get("newsId"), 50)
        if not identity:
            continue
        evidence.append(
            evidence_record(
                f"htfc-news:{identity}",
                "htfc-tianji",
                clean_text(item.get("title") or item.get("tag2") or item.get("tagName") or "天玑快讯", 80),
                clean_text(item.get("content") or "需进一步核验", 160),
                observed_at=clean_text(f"{item.get('date', '')} {item.get('time', '')}", 40),
                detail="华泰天玑油脂油料快讯；属于资讯证据，不替代官方供需数据。",
            )
        )

    kline_module = htfc_modules.get("smart_kline") if isinstance(htfc_modules.get("smart_kline"), dict) else {}
    kline_products = kline_module.get("products") if isinstance(kline_module.get("products"), dict) else {}
    for symbol, product in list(kline_products.items())[:3]:
        if not isinstance(product, dict) or product.get("status") != "ok":
            continue
        response = product.get("response") if isinstance(product.get("response"), dict) else {}
        data = response.get("data") if isinstance(response.get("data"), dict) else {}
        market = data.get("marketData") if isinstance(data.get("marketData"), dict) else {}
        closes = market.get("closePrice") if isinstance(market.get("closePrice"), list) else []
        label = product.get("label") if isinstance(product.get("label"), dict) else {}
        evidence.append(
            evidence_record(
                f"htfc-kline:{clean_text(symbol, 20)}",
                "htfc-tianji",
                f"{clean_text(label.get('name') or symbol, 40)}智能K线",
                f"最近收盘 {clean_text(closes[-1] if closes else '需进一步核验', 30)}",
                observed_at=clean_text(data.get("kLineAiReportDate") or htfc.get("generated_at"), 40),
                detail=clean_text(data.get("kLineAiContent"), 220),
            )
        )
    countries = supply.get("countries") if isinstance(supply.get("countries"), dict) else {}
    for country_key, country in countries.items():
        if not isinstance(country, dict):
            continue
        metrics = country.get("metrics") if isinstance(country.get("metrics"), dict) else {}
        for metric_key, metric in list(metrics.items())[:4]:
            if not isinstance(metric, dict):
                continue
            series = metric.get("series") if isinstance(metric.get("series"), list) else []
            latest = series[-1] if series and isinstance(series[-1], dict) else {}
            if latest.get("value") in (None, ""):
                continue
            evidence.append(
                evidence_record(
                    f"supply:{clean_text(country_key, 30)}:{clean_text(metric_key, 30)}",
                    "supply-demand",
                    f"{clean_text(country.get('name') or country_key, 40)}{clean_text(metric.get('label') or metric_key, 40)}",
                    f"{clean_text(latest.get('value'), 40)} {clean_text(metric.get('display_unit') or metric.get('unit'), 20)}",
                    observed_at=clean_text(latest.get("period") or country.get("latest_period"), 40),
                    detail=clean_text(country.get("status_message"), 180),
                )
            )
    forecast_value = (
        "达到公开展示门槛"
        if forecast.get("public_display_allowed")
        else "评估样本不足，禁止包装成可靠预测能力"
    )
    evidence.append(
        evidence_record(
            "forecast:latest",
            "forecast-metrics",
            "预测评估",
            forecast_value,
            observed_at=clean_text(forecast.get("generated_at") or forecast.get("as_of"), 40),
        )
    )
    products = contracts.get("products") if isinstance(contracts.get("products"), dict) else {}
    evidence.append(
        evidence_record(
            "contracts:current",
            "contracts",
            "主力与次主力合约",
            "、".join(sorted(str(key) for key in products)) or "需进一步核验",
            observed_at=clean_text(contracts.get("generated_at"), 40),
            detail=f"合约月份 {clean_text(contracts.get('month'), 20)}",
        )
    )

    if not evidence:
        raise BriefError("没有可供 AI 简报引用的证据")

    source_snapshot = {
        "reports": clean_text(latest_report.get("generated_at") or latest_report.get("date"), 40),
        "oil-futures": clean_text(oil.get("updated_at"), 40),
        "exchange-futures": clean_text(exchange.get("updated_at"), 40),
        "quant-model-signals": clean_text(
            quant.get("market_updated_at") or quant.get("generated_at"),
            40,
        ),
        "supply-demand": clean_text(supply.get("checked_at") or supply.get("generated_at"), 40),
        "forecast-metrics": clean_text(forecast.get("generated_at") or forecast.get("as_of"), 40),
        "contracts": clean_text(contracts.get("generated_at"), 40),
        "htfc-tianji": clean_text(htfc.get("generated_at"), 40),
        "market-watch": clean_text(market_watch.get("generated_at"), 40) if live_quotes else "",
    }
    return {
        "session": clean_text(oil.get("update_session") or exchange.get("update_session") or "manual", 30),
        "source_snapshot": source_snapshot,
        "evidence": evidence,
        "sector_evidence_ids": sector_evidence_ids,
        "fixed_logic": ["otc_structure_library", "quant_model_rules"],
    }


def source_fingerprint(context: dict[str, Any]) -> str:
    raw = json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_model_backend():
    path = ROOT / "server" / "model_backend.py"
    spec = importlib.util.spec_from_file_location("palm_oil_model_backend", path)
    if spec is None or spec.loader is None:
        raise BriefError("无法加载服务器模型后端")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODEL_BACKEND = load_model_backend()


def build_prompt(context: dict[str, Any]) -> str:
    evidence_ids = [item["id"] for item in context["evidence"]]
    return f"""
你是 24h 期货盯盘助手的只读研究分析器。只允许使用下方 CONTEXT_JSON，禁止联网、禁止调用工具、禁止读取其他文件。

输出必须严格符合给定 JSON Schema，并遵守：
1. 不修改场外结构库或量化模型规则，不生成自动交易指令。
2. key_moves.evidence_id 和 watchlist.evidence_ids 只能从允许的证据编号中选择。
3. headline、summary、interpretation、item、why、task、result、risks 不得包含任何阿拉伯数字；数值由程序依据 evidence_id 自动回填，避免模型编造。
4. 数据缺失、冲突或时间不一致时降低 confidence，并明确写入 risks。
5. 结论先行，中文简洁；actions 表示 AI 已完成、正在监控或被数据阻断的工作。
6. 休市时技术判断必须引用最近完成交易日的 technical 证据；只要 fundamental 或 supply 证据有最近成功值，就不得描述为数据为空。供需与基本面检查独立于开休市持续运行。
7. 有技术与基本面证据时，watchlist 至少分别包含一项技术面和一项基本面关注事项。
8. sector_views 必须逐一覆盖 CONTEXT_JSON.sector_evidence_ids 中的全部板块，每个板块只能出现一次，并引用对应的 sector 证据；不得把棕榈油结论套用到其他板块。
9. 每个板块先判断板块内部强弱、领涨领跌与分化，再给出简洁研判；缺少板块基本面时应明确这是行情结构判断。
10. 不要输出 Markdown，只输出 JSON 对象。

允许的证据编号：
{json.dumps(evidence_ids, ensure_ascii=False)}

CONTEXT_JSON：
{json.dumps(context, ensure_ascii=False, sort_keys=True)}
""".strip()


def run_openai(context: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    try:
        payload, _backend = MODEL_BACKEND.request_json(
            schema=json.loads(SCHEMA.read_text(encoding="utf-8")),
            schema_name="market_assistant_brief",
            prompt=build_prompt(context),
            timeout=timeout_seconds,
            verbosity="low",
        )
        return payload
    except MODEL_BACKEND.ModelBackendError as exc:
        raise BriefError(
            f"模型 API 请求失败：{exc}，保留最近一次有效 AI 简报"
        ) from exc


def require_text(value: Any, field: str, *, no_numbers: bool = True) -> str:
    text = clean_text(value, 240)
    if not text:
        raise BriefError(f"AI 简报字段为空：{field}")
    if no_numbers and NUMBER_RE.search(text):
        raise BriefError(f"AI 简报字段包含未受控数字：{field}")
    return text


def require_list(value: Any, field: str, minimum: int = 1, maximum: int = 5) -> list[Any]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise BriefError(f"AI 简报字段数量不合法：{field}")
    return value


def validate_and_enrich(model_payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    required = {
        "headline",
        "market_state",
        "summary",
        "key_moves",
        "watchlist",
        "sector_views",
        "actions",
        "risks",
        "confidence",
    }
    if set(model_payload) != required:
        raise BriefError("AI 简报字段与结构契约不一致")

    evidence_by_id = {item["id"]: item for item in context["evidence"]}
    market_state = require_text(model_payload["market_state"], "market_state")
    confidence = require_text(model_payload["confidence"], "confidence")
    if market_state not in MARKET_STATES:
        raise BriefError("AI 简报 market_state 不合法")
    if confidence not in CONFIDENCE_LEVELS:
        raise BriefError("AI 简报 confidence 不合法")

    key_moves = []
    for index, item in enumerate(require_list(model_payload["key_moves"], "key_moves")):
        if not isinstance(item, dict) or set(item) != {"evidence_id", "interpretation"}:
            raise BriefError(f"AI 简报 key_moves[{index}] 结构不合法")
        evidence_id = str(item["evidence_id"])
        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            raise BriefError(f"AI 简报引用未知证据：{evidence_id}")
        key_moves.append(
            {
                "evidence_id": evidence_id,
                "label": evidence["label"],
                "value": evidence["value"],
                "source": evidence["source"],
                "observed_at": evidence["observed_at"],
                "interpretation": require_text(item["interpretation"], f"key_moves[{index}].interpretation"),
            }
        )

    watchlist = []
    for index, item in enumerate(require_list(model_payload["watchlist"], "watchlist")):
        expected = {"priority", "item", "trigger", "why", "evidence_ids"}
        if not isinstance(item, dict) or set(item) != expected:
            raise BriefError(f"AI 简报 watchlist[{index}] 结构不合法")
        priority = require_text(item["priority"], f"watchlist[{index}].priority")
        trigger = require_text(item["trigger"], f"watchlist[{index}].trigger")
        if priority not in PRIORITIES or trigger not in TRIGGERS:
            raise BriefError(f"AI 简报 watchlist[{index}] 枚举值不合法")
        evidence_ids = require_list(item["evidence_ids"], f"watchlist[{index}].evidence_ids", 1, 4)
        normalized_ids = []
        for evidence_id in evidence_ids:
            evidence_key = str(evidence_id)
            if evidence_key not in evidence_by_id:
                raise BriefError(f"AI 简报引用未知证据：{evidence_key}")
            normalized_ids.append(evidence_key)
        if len(normalized_ids) != len(set(normalized_ids)):
            raise BriefError(f"AI 简报 watchlist[{index}] 重复引用同一证据")
        watchlist.append(
            {
                "priority": priority,
                "item": require_text(item["item"], f"watchlist[{index}].item"),
                "trigger": trigger,
                "why": require_text(item["why"], f"watchlist[{index}].why"),
                "evidence_ids": normalized_ids,
            }
        )

    sector_views = []
    expected_sectors = context.get("sector_evidence_ids") or {}
    model_sector_views = require_list(
        model_payload["sector_views"],
        "sector_views",
        len(expected_sectors),
        max(8, len(expected_sectors)),
    )
    seen_sectors: set[str] = set()
    for index, item in enumerate(model_sector_views):
        expected = {"sector", "state", "summary", "evidence_ids"}
        if not isinstance(item, dict) or set(item) != expected:
            raise BriefError(f"AI 简报 sector_views[{index}] 结构不合法")
        sector = require_text(item["sector"], f"sector_views[{index}].sector")
        if sector not in expected_sectors or sector in seen_sectors:
            raise BriefError(f"AI 简报 sector_views[{index}] 板块不合法或重复：{sector}")
        state = require_text(item["state"], f"sector_views[{index}].state")
        if state not in MARKET_STATES:
            raise BriefError(f"AI 简报 sector_views[{index}].state 不合法")
        evidence_ids = require_list(
            item["evidence_ids"], f"sector_views[{index}].evidence_ids", 1, 3
        )
        normalized_ids = [str(evidence_id) for evidence_id in evidence_ids]
        if expected_sectors[sector] not in normalized_ids:
            raise BriefError(f"AI 简报 {sector} 未引用对应板块证据")
        if any(evidence_id not in evidence_by_id for evidence_id in normalized_ids):
            raise BriefError(f"AI 简报 {sector} 引用未知证据")
        seen_sectors.add(sector)
        sector_views.append(
            {
                "sector": sector,
                "state": state,
                "summary": require_text(item["summary"], f"sector_views[{index}].summary"),
                "evidence_ids": normalized_ids,
                "evidence": [evidence_by_id[evidence_id] for evidence_id in normalized_ids],
            }
        )
    if seen_sectors != set(expected_sectors):
        missing = "、".join(sorted(set(expected_sectors) - seen_sectors))
        raise BriefError(f"AI 简报缺少板块研判：{missing}")

    actions = []
    for index, item in enumerate(require_list(model_payload["actions"], "actions")):
        expected = {"status", "task", "result", "next_check"}
        if not isinstance(item, dict) or set(item) != expected:
            raise BriefError(f"AI 简报 actions[{index}] 结构不合法")
        status = require_text(item["status"], f"actions[{index}].status")
        next_check = require_text(item["next_check"], f"actions[{index}].next_check")
        if status not in ACTION_STATUSES or next_check not in NEXT_CHECKS:
            raise BriefError(f"AI 简报 actions[{index}] 枚举值不合法")
        actions.append(
            {
                "status": status,
                "task": require_text(item["task"], f"actions[{index}].task"),
                "result": require_text(item["result"], f"actions[{index}].result"),
                "next_check": next_check,
            }
        )

    risks = [
        require_text(item, f"risks[{index}]")
        for index, item in enumerate(require_list(model_payload["risks"], "risks"))
    ]
    return {
        "schema_version": 1,
        "status": "ready",
        "generated_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        "update_session": context["session"],
        "generator": MODEL_BACKEND.resolve_config(require_key=False)["backend"],
        "generation_contract": "server-only-codex, source-grounded, structured-output",
        "source_fingerprint": source_fingerprint(context),
        "source_snapshot": context["source_snapshot"],
        "fixed_logic": context["fixed_logic"],
        "headline": require_text(model_payload["headline"], "headline"),
        "market_state": market_state,
        "summary": require_text(model_payload["summary"], "summary"),
        "key_moves": key_moves,
        "watchlist": watchlist,
        "sector_views": sector_views,
        "actions": actions,
        "risks": risks,
        "confidence": confidence,
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def current_fingerprint(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return str(payload.get("source_fingerprint") or "") if isinstance(payload, dict) else ""


def previous_generated_at(path: Path) -> datetime | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        value = payload.get("generated_at") if isinstance(payload, dict) else None
        parsed = datetime.fromisoformat(str(value)) if value else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def quota_cooldown_remaining(
    previous_time: datetime | None,
    *,
    minimum_minutes: int,
    now: datetime | None = None,
) -> int:
    if previous_time is None or minimum_minutes <= 0:
        return 0
    current = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI)
    elapsed = (current - previous_time.astimezone(SHANGHAI)).total_seconds()
    return max(0, int(minimum_minutes * 60 - elapsed))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--previous-output", type=Path, default=OUTPUT)
    parser.add_argument("--mock-response", type=Path, help="测试用模型响应 JSON")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--min-interval-minutes",
        type=int,
        default=int(os.environ.get("PALM_OIL_AI_MIN_INTERVAL_MINUTES", "30")),
        help="Minimum elapsed time between paid model runs when sources keep changing.",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        payloads = {name: load_json(path) for name, path in SOURCE_FILES.items()}
        context = build_context(payloads)
        fingerprint = source_fingerprint(context)
        if not args.force and current_fingerprint(args.previous_output) == fingerprint:
            if args.output.resolve() != args.previous_output.resolve():
                args.output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(args.previous_output, args.output)
            print(json.dumps({"status": "skipped", "reason": "source_unchanged", "source_fingerprint": fingerprint}))
            return 0
        previous_time = previous_generated_at(args.previous_output)
        remaining_seconds = quota_cooldown_remaining(
            previous_time,
            minimum_minutes=args.min_interval_minutes,
        )
        if not args.force and remaining_seconds > 0:
            if args.output.resolve() != args.previous_output.resolve():
                args.output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(args.previous_output, args.output)
            print(
                json.dumps(
                    {
                        "status": "skipped",
                        "reason": "codex_quota_cooldown",
                        "source_fingerprint": fingerprint,
                        "retry_after_seconds": remaining_seconds,
                    }
                )
            )
            return 0
        if args.mock_response:
            model_payload = load_json(args.mock_response)
            if not isinstance(model_payload, dict):
                raise BriefError("测试模型响应不是 JSON 对象")
        else:
            model_payload = run_openai(context, args.timeout)
        output = validate_and_enrich(model_payload, context)
        atomic_write(args.output, output)
        print(
            json.dumps(
                {
                    "status": "updated",
                    "output": str(args.output),
                    "source_fingerprint": fingerprint,
                    "evidence_count": len(context["evidence"]),
                },
                ensure_ascii=False,
            )
        )
        return 0
    except BriefError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

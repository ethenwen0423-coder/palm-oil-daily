#!/usr/bin/env python3
"""Generate a source-grounded AI brief for the 24h market-assistant page."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
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
    priced_exchange = [
        item
        for item in exchange_contracts
        if isinstance(item, dict) and as_number(item.get("change_pct")) is not None
    ]
    priced_exchange.sort(key=lambda item: abs(as_number(item.get("change_pct")) or 0), reverse=True)
    for index, item in enumerate(priced_exchange[:8]):
        identity = clean_text(item.get("symbol") or item.get("contract") or item.get("product") or index, 50)
        price = clean_text(item.get("price") or "需进一步核验", 40)
        change = clean_text(item.get("change_pct"), 30)
        evidence.append(
            evidence_record(
                f"exchange:{identity}",
                "exchange-futures",
                clean_text(item.get("product") or item.get("symbol"), 60),
                f"{price}；涨跌 {change}%",
                observed_at=clean_text(exchange.get("updated_at"), 40),
                detail=clean_text((item.get("fundamental") or {}).get("summary"), 180),
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
    }
    return {
        "session": clean_text(oil.get("update_session") or exchange.get("update_session") or "manual", 30),
        "source_snapshot": source_snapshot,
        "evidence": evidence,
        "fixed_logic": ["otc_structure_library", "quant_model_rules"],
    }


def source_fingerprint(context: dict[str, Any]) -> str:
    raw = json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-5.2"


def resolve_openai_api_key() -> str:
    """Return the server-only API key without ever logging its value."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise BriefError("OpenAI API 密钥未配置，保留最近一次有效 AI 简报")
    return key


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
6. 不要输出 Markdown，只输出 JSON 对象。

允许的证据编号：
{json.dumps(evidence_ids, ensure_ascii=False)}

CONTEXT_JSON：
{json.dumps(context, ensure_ascii=False, sort_keys=True)}
""".strip()


def extract_response_text(payload: dict[str, Any]) -> str:
    """Extract structured Responses API text across documented response shapes."""
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct
    output = payload.get("output")
    if not isinstance(output, list):
        raise BriefError("AI 简报未返回结构化文本，保留最近一次有效结果")
    fragments: list[str] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "output_text":
                continue
            text = part.get("text")
            if isinstance(text, str):
                fragments.append(text)
    joined = "".join(fragments).strip()
    if not joined:
        raise BriefError("AI 简报未返回结构化文本，保留最近一次有效结果")
    return joined


def run_openai(context: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    api_key = resolve_openai_api_key()
    model = os.environ.get("PALM_OIL_AI_MODEL", DEFAULT_OPENAI_MODEL).strip()
    if not model:
        raise BriefError("OpenAI 模型未配置，保留最近一次有效 AI 简报")
    endpoint = os.environ.get("OPENAI_RESPONSES_URL", OPENAI_RESPONSES_URL).strip()
    request_body = {
        "model": model,
        "input": build_prompt(context),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "market_assistant_brief",
                "strict": True,
                "schema": json.loads(SCHEMA.read_text(encoding="utf-8")),
            },
            "verbosity": "low",
        },
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw_response = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        # Error bodies are deliberately not logged: a proxy can reflect request details.
        raise BriefError(
            f"OpenAI API 请求失败（HTTP {exc.code}），保留最近一次有效 AI 简报"
        ) from exc
    except (OSError, TimeoutError) as exc:
        raise BriefError(
            f"OpenAI API 请求超过 {timeout_seconds} 秒或网络不可用，保留最近一次有效 AI 简报"
        ) from exc
    try:
        response_payload = json.loads(raw_response)
        model_payload = json.loads(extract_response_text(response_payload))
    except (TypeError, json.JSONDecodeError) as exc:
        raise BriefError("AI 简报未返回可解析 JSON，保留最近一次有效结果") from exc
    if not isinstance(model_payload, dict):
        raise BriefError("AI 简报根节点不是 JSON 对象")
    return model_payload


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
        "generator": "openai-responses-api",
        "generation_contract": "server-only-key, source-grounded, structured-output",
        "source_fingerprint": source_fingerprint(context),
        "source_snapshot": context["source_snapshot"],
        "fixed_logic": context["fixed_logic"],
        "headline": require_text(model_payload["headline"], "headline"),
        "market_state": market_state,
        "summary": require_text(model_payload["summary"], "summary"),
        "key_moves": key_moves,
        "watchlist": watchlist,
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--previous-output", type=Path, default=OUTPUT)
    parser.add_argument("--mock-response", type=Path, help="测试用模型响应 JSON")
    parser.add_argument("--timeout", type=int, default=300)
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

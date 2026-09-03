#!/usr/bin/env python3
"""Deterministically audit a governed oil report before publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "oil-report-outline-v1"
STANCES = {"偏多", "偏空", "震荡", "观望"}
DAILY_SECTIONS = (
    "今日观点",
    "今日交易信号",
    "核心驱动与预期差",
    "关键数据与价格",
    "开盘推演",
    "风险提示",
    "信息来源与核验说明",
    "消息来源链接",
    "AI观点风险提示",
)
WEEKEND_SECTIONS = (
    "一句话核心观点",
    "本周验证与预期差",
    "核心数据变化",
    "下周主线与事件",
    "周一开盘推演",
    "交易计划",
    "风险提示",
    "信息来源与核验说明",
    "消息来源链接",
    "AI观点风险提示",
)
BODY_LIMITS = {"daily": (1000, 1400), "weekend": (1600, 2000)}
QUALITY_RELEASE_SCORE = 92
AI_DISCLAIMER = (
    "本报告由AI基于公开信息、已调用数据源和既定研究框架生成，仅代表生成时点的研究判断，"
    "不构成投资建议或交易指令。期货价格波动较大，客户应结合自身风险承受能力独立决策。"
)
CRITICAL_KEYS = ("domestic.soybean_oil", "domestic.palm_oil", "domestic.rapeseed_oil")
TRADE_FIELDS = (
    "trade_trigger",
    "confirmation_condition",
    "stop_loss",
    "target_range",
    "position_limit",
    "signal_expiry",
)
ALIASES = {
    "domestic.soybean_oil": ("豆油", "Y主力", "Y2609", "Y0"),
    "domestic.palm_oil": ("棕榈油", "棕油", "P主力", "P2609", "P0"),
    "domestic.rapeseed_oil": ("菜油", "OI主力", "OI2609", "OI0"),
    "external.cbot_bean_oil": ("CBOT豆油", "CBOT 豆油", "美豆油"),
    "external.cbot_soybean": ("CBOT大豆", "CBOT 大豆", "美豆"),
    "external.bmd_palm_oil": ("FCPO", "BMD棕油", "BMD 棕油", "马棕"),
    "external.india_cpo_spot": ("NCDEX", "印度CPO"),
    "external.indonesia_cpo_spot": ("ICDX", "CPOTR", "印尼CPO", "印尼棕榈油"),
    "fundamental.inventory.soybean_oil_inventory": ("豆油库存",),
    "fundamental.inventory.palm_oil_inventory": ("棕榈油库存", "棕油库存"),
    "fundamental.inventory.rapeseed_oil_inventory": ("菜油库存",),
    "fundamental.spread.soybean_palm_spread": ("豆棕价差",),
    "fundamental.spread.rapeseed_soybean_spread": ("菜豆油价差", "菜豆价差"),
    "fundamental.official_supply_demand.latest_metrics.production": ("MPOB产量", "CPO产量"),
    "fundamental.official_supply_demand.latest_metrics.exports": ("MPOB出口", "棕榈油出口"),
    "fundamental.official_supply_demand.latest_metrics.stocks": ("MPOB期末库存", "期末库存"),
    "fundamental.cross_drivers.crude_oil": ("WTI", "原油"),
}
EVIDENCE_SOURCE_ALIASES = {
    "机构资讯·油脂油料快讯": ("机构油脂快讯",),
    "Open-Meteo 直接预报数据": ("Open-Meteo直接预报",),
    "东方财富7x24快讯": ("东方财富7×24",),
    "跨站新闻·Google News": ("跨站新闻",),
}


@dataclass(frozen=True)
class NumericRecord:
    key: str
    name: str
    price: float
    change_pct: float | None
    aliases: tuple[str, ...]


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} 顶层必须是对象")
    return value


def _fresh_event_used(item: dict[str, Any], text: str) -> bool:
    """Match a governed event by exact title/source or an approved display alias."""
    source = str(item.get("source") or "").strip()
    title = str(item.get("title") or "").strip()
    candidates = [source, title, *EVIDENCE_SOURCE_ALIASES.get(source, ())]
    return any(candidate and candidate in text for candidate in candidates)


def _outline_errors(outline: dict[str, Any], kind: str) -> list[str]:
    required_strings = (
        "report_date",
        "data_cutoff",
        "top_call",
        "transmission_chain",
        "expectation_vs_reality",
        "strongest_counter_case",
        "invalidation_condition",
        *TRADE_FIELDS,
        "research_confidence",
    )
    errors: list[str] = []
    if outline.get("schema_version") != SCHEMA_VERSION:
        errors.append("提纲 schema_version 无效")
    if outline.get("kind") != kind:
        errors.append(f"提纲 kind 必须为 {kind}")
    if outline.get("market_stance") not in STANCES:
        errors.append("提纲 market_stance 必须是偏多/偏空/震荡/观望")
    for field in required_strings:
        if not isinstance(outline.get(field), str) or not str(outline.get(field)).strip():
            errors.append(f"提纲缺少非空字段：{field}")
    confidence = outline.get("research_confidence")
    if isinstance(confidence, str) and not re.fullmatch(r"[★☆]{5}", confidence):
        errors.append("提纲 research_confidence 必须是五星格式")
    for field in ("primary_driver", "secondary_driver"):
        driver = outline.get(field)
        if not isinstance(driver, dict):
            errors.append(f"提纲缺少驱动对象：{field}")
            continue
        for key in ("name", "evidence_level", "source", "as_of", "impact"):
            if not isinstance(driver.get(key), str) or not driver.get(key, "").strip():
                errors.append(f"{field} 缺少字段：{key}")
        if driver.get("evidence_level") not in {"Level 1", "Level 2", "Level 3"}:
            errors.append(f"{field}.evidence_level 无效")
    evidence = outline.get("evidence_status")
    if not isinstance(evidence, dict):
        errors.append("提纲缺少 evidence_status")
    else:
        for key in ("verified", "limited", "needs_verification"):
            if not isinstance(evidence.get(key), list) or not all(isinstance(item, str) for item in evidence.get(key, [])):
                errors.append(f"evidence_status.{key} 必须是字符串数组")
    return errors


def _section_names(text: str) -> list[str]:
    return re.findall(r"^##\s*【([^】]+)】\s*$", text, re.MULTILINE)


def _section(text: str, name: str) -> str:
    match = re.search(rf"^##\s*【{re.escape(name)}】\s*\n(?P<body>.*?)(?=^##\s*【|\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group("body").strip() if match else ""


def _require_top_call(text: str, outline: dict[str, Any], kind: str, errors: list[str], components: dict[str, int]) -> None:
    """Reject a formally complete report whose first screen is not actionable."""
    name = "今日观点" if kind == "daily" else "一句话核心观点"
    section = _section(text, name)
    missing: list[str] = []
    stance = str(outline.get("market_stance") or "")
    confidence = str(outline.get("research_confidence") or "")
    if stance and stance not in section:
        missing.append("基准方向")
    if confidence and confidence not in section:
        missing.append("研究置信度")
    if not any(marker in section for marker in ("失效", "推翻", "放弃", "反证")):
        missing.append("失效条件")
    if not any(marker in section for marker in ("执行", "观望", "空仓", "不开仓", "不新开仓", "不追")):
        missing.append("行动含义")
    if missing:
        errors.append(f"{name} 未形成可执行 Top Call：缺少{'、'.join(missing)}")
        components["view_trade_consistency"] = max(0, components["view_trade_consistency"] - 6)


def _require_decision_sections(text: str, kind: str, errors: list[str], components: dict[str, int]) -> None:
    """Check decision structures that headings and numeric checks cannot prove."""
    driver_name = "核心驱动与预期差" if kind == "daily" else "本周验证与预期差"
    drivers = _section(text, driver_name)
    if not ("主驱动一" in drivers and "主驱动二" in drivers):
        errors.append(f"{driver_name} 必须明确排序为“主驱动一/主驱动二”，避免新闻平铺")
        components["causal_chain_expectation_gap"] = max(0, components["causal_chain_expectation_gap"] - 4)
    scenario_name = "开盘推演" if kind == "daily" else "周一开盘推演"
    scenarios = _section(text, scenario_name)
    required = ("高开", "平开", "低开") if kind == "daily" else ("高开高走", "高开震荡", "高开回落", "低开")
    missing_scenarios = [item for item in required if item not in scenarios]
    if missing_scenarios:
        errors.append(f"{scenario_name} 缺少情景：{'、'.join(missing_scenarios)}")
        components["view_trade_consistency"] = max(0, components["view_trade_consistency"] - 4)
    if not ("Y" in scenarios and "OI" in scenarios and any(marker in scenarios for marker in ("同步", "背离", "分化"))):
        errors.append(f"{scenario_name} 未说明 Y/OI 同步或背离对 P 的处理")
        components["view_trade_consistency"] = max(0, components["view_trade_consistency"] - 3)
    if kind == "weekend":
        events = _section(text, "下周主线与事件")
        missing_days = [day for day in ("周一", "周二", "周三", "周四", "周五") if day not in events]
        if missing_days:
            errors.append(f"下周主线与事件缺少交易周覆盖：{'、'.join(missing_days)}")
            components["structural_completeness"] = max(0, components["structural_completeness"] - 3)


def visible_body_chars(text: str) -> int:
    """Count reader-facing body chars, excluding links and the fixed disclaimer."""
    cut = re.split(r"^##\s*【消息来源链接】\s*$", text, maxsplit=1, flags=re.MULTILINE)[0]
    cut = re.sub(r"https?://\S+", "", cut)
    cut = re.sub(r"!\[[^\]]*]\([^)]*\)", "", cut)
    cut = re.sub(r"\[([^\]]+)]\([^)]*\)", r"\1", cut)
    cut = re.sub(r"^\s*#{1,6}\s*", "", cut, flags=re.MULTILINE)
    cut = re.sub(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$", "", cut, flags=re.MULTILINE)
    cut = re.sub(r"[*_`>|]", "", cut)
    return len(re.sub(r"\s+", "", cut))


def _flatten_records(value: Any, prefix: str = "") -> list[NumericRecord]:
    rows: list[NumericRecord] = []
    if not isinstance(value, dict):
        return rows
    price = value.get("price")
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        metric_value = value.get("value")
        price = metric_value if isinstance(metric_value, (int, float)) and not isinstance(metric_value, bool) else price
    if isinstance(price, (int, float)) and not isinstance(price, bool):
        name = (
            value.get("name")
            if isinstance(value.get("name"), str)
            else value.get("label")
            if isinstance(value.get("label"), str)
            else prefix
        )
        aliases = list(ALIASES.get(prefix, (name,)))
        contract = str(value.get("contract") or value.get("symbol") or "").upper()
        if re.fullmatch(r"[A-Z]+\d{4}", contract) and contract not in aliases:
            aliases.append(contract)
        change_pct = value.get("change_pct")
        rows.append(
            NumericRecord(
                key=prefix,
                name=name,
                price=float(price),
                change_pct=float(change_pct)
                if isinstance(change_pct, (int, float)) and not isinstance(change_pct, bool)
                else None,
                aliases=tuple(alias for alias in aliases if alias),
            )
        )
    for key, child in value.items():
        if key in {"previous_snapshot", "previous_source_snapshot"}:
            continue
        if isinstance(child, dict):
            child_prefix = f"{prefix}.{key}" if prefix else key
            rows.extend(_flatten_records(child, child_prefix))
        elif isinstance(child, (int, float)) and not isinstance(child, bool):
            child_prefix = f"{prefix}.{key}" if prefix else key
            if child_prefix in ALIASES:
                rows.append(
                    NumericRecord(
                        key=child_prefix,
                        name=ALIASES[child_prefix][0],
                        price=float(child),
                        change_pct=None,
                        aliases=ALIASES[child_prefix],
                    )
                )
    return rows


def _lines_for_aliases(text: str, aliases: tuple[str, ...]) -> list[str]:
    return [line for line in text.splitlines() if any(alias in line for alias in aliases)]


def _has_numeric_claim(line: str, aliases: tuple[str, ...]) -> bool:
    for alias in aliases:
        start = 0
        while True:
            index = line.find(alias, start)
            if index < 0:
                break
            context = line[index : index + len(alias) + 48]
            context = re.sub(r"\d{4}-\d{2}-\d{2}(?:[ T]\d{1,2}:\d{2})?", "", context)
            if re.search(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", context):
                return True
            start = index + len(alias)
    return False


def _number_pattern(value: float, tolerance: float | None = None) -> re.Pattern[str]:
    tolerance = tolerance if tolerance is not None else max(0.01, abs(value) * 0.000001)
    decimals = 2 if abs(value - round(value)) > tolerance else 0
    if decimals == 0:
        integer = int(round(value))
        candidates = {str(integer), f"{integer:,}"}
        escaped = "|".join(
            rf"{re.escape(item)}(?:\.0+)?"
            for item in sorted(candidates, key=len, reverse=True)
        )
        return re.compile(rf"(?<![\d.])(?:{escaped})(?![\d.])")
    candidates = {
        f"{value:.{decimals}f}",
        f"{value:,.{decimals}f}",
        f"{value:g}",
        f"{value:,g}",
    }
    escaped = "|".join(re.escape(item) for item in sorted(candidates, key=len, reverse=True))
    return re.compile(rf"(?<![\d.])(?:{escaped})(?![\d.])")


def _record_check(text: str, record: NumericRecord, required: bool) -> dict[str, Any]:
    alias_lines = _lines_for_aliases(text, record.aliases)
    contexts: list[str] = []
    for line in alias_lines:
        for alias in record.aliases:
            start = 0
            while True:
                index = line.find(alias, start)
                if index < 0:
                    break
                contexts.append(line[index : index + len(alias) + 80])
                start = index + len(alias)
    lines = [context for context in contexts if _has_numeric_claim(context, record.aliases)]
    mentioned = bool(alias_lines) if required else bool(lines)
    joined = "\n".join(lines)
    price_ok = bool(_number_pattern(record.price).search(joined)) if mentioned else False
    percent_checked = False
    percent_ok = True
    if mentioned and record.change_pct is not None:
        percent_values: list[float] = []
        for line in lines:
            if not _number_pattern(record.price).search(line):
                continue
            percent_values.extend(float(item) for item in re.findall(r"(?<!\d)([+-]?\d+(?:\.\d+)?)\s*%", line))
        if percent_values:
            percent_checked = True
            percent_ok = any(abs(item - record.change_pct) <= 0.05 for item in percent_values)
            if not percent_ok and record.change_pct < 0 and any(word in joined for word in ("回落", "下跌", "跌幅", "走弱")):
                percent_ok = any(abs(abs(item) - abs(record.change_pct)) <= 0.05 for item in percent_values)
    return {
        "key": record.key,
        "name": record.name,
        "expected_price": record.price,
        "mentioned": mentioned,
        "required": required,
        "price_ok": price_ok,
        "percent_checked": percent_checked,
        "percent_ok": percent_ok,
    }


def _deterministic_sample(records: list[NumericRecord], seed: str, size: int = 3) -> list[NumericRecord]:
    ranked = sorted(
        records,
        key=lambda record: hashlib.sha256(f"{seed}|{record.key}".encode("utf-8")).hexdigest(),
    )
    return ranked[: min(size, len(ranked))]


def _trade_numbers(value: str) -> list[str]:
    without_dates = re.sub(r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}", "", value)
    without_dates = re.sub(r"(?<![A-Za-z0-9])[A-Za-z]{1,3}\d{4}(?!\d)", "", without_dates)
    tokens = re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?%?", without_dates)
    return [token for token in tokens if len(token.rstrip("%").replace(".", "")) >= 2]


def _has_number(text: str, token: str) -> bool:
    number = token.rstrip("%")
    suffix = r"\s*%" if token.endswith("%") else ""
    return bool(re.search(rf"(?<![\d.]){re.escape(number)}{suffix}(?![\d.])", text))


def _duplicate_sentences(text: str) -> list[str]:
    body = re.split(r"^##\s*【消息来源链接】", text, maxsplit=1, flags=re.MULTILINE)[0]
    # Repeated trigger/confirmation/invalidation cells are expected in the
    # required P/Y/OI strategy tables.  Repetition quality applies to prose,
    # not to structured execution contracts.
    body = "\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith("|")
    )
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for raw in re.split(r"[。！？\n]", body):
        normalized = re.sub(r"[\s*#|：【】（）()，、；;:,.%-]", "", raw)
        if len(normalized) < 16:
            continue
        if normalized in seen and normalized not in duplicates:
            duplicates.append(normalized)
        seen[normalized] = raw
    return duplicates


def _has_markdown_table(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return any(
        lines[index].startswith("|")
        and lines[index].endswith("|")
        and re.fullmatch(r"\|[\s:|-]+\|", lines[index + 1]) is not None
        for index in range(len(lines) - 1)
    )


def _markdown_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Parse simple pipe tables so contracts are checked per column and row."""
    lines = [line.strip() for line in text.splitlines()]
    tables: list[tuple[list[str], list[list[str]]]] = []
    index = 0
    while index + 1 < len(lines):
        header_line = lines[index]
        separator = lines[index + 1]
        if not (
            header_line.startswith("|")
            and header_line.endswith("|")
            and re.fullmatch(r"\|[\s:|-]+\|", separator)
        ):
            index += 1
            continue
        headers = [cell.strip() for cell in header_line.strip("|").split("|")]
        rows: list[list[str]] = []
        index += 2
        while index < len(lines) and lines[index].startswith("|") and lines[index].endswith("|"):
            cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(cells)
            index += 1
        tables.append((headers, rows))
    return tables


def _column_index(headers: list[str], aliases: tuple[str, ...]) -> int | None:
    for index, header in enumerate(headers):
        compact = re.sub(r"\s+", "", header)
        if any(alias in compact for alias in aliases):
            return index
    return None


def _require_execution_table(
    section: str,
    label: str,
    hard_failures: list[str],
) -> None:
    required = {
        "品种": ("品种", "合约"),
        "方向": ("方向",),
        "触发": ("触发",),
        "确认": ("确认",),
        "止损": ("止损", "失效"),
        "目标": ("目标",),
        "仓位上限": ("仓位上限",),
        "信号有效期": ("信号有效期",),
    }
    for headers, rows in _markdown_tables(section):
        indexes = {name: _column_index(headers, aliases) for name, aliases in required.items()}
        if any(index is None for index in indexes.values()):
            continue
        symbol_index = indexes["品种"]
        assert symbol_index is not None
        missing_rows: list[str] = []
        incomplete: list[str] = []
        for symbol in ("P", "Y", "OI"):
            row = next(
                (
                    cells
                    for cells in rows
                    if re.fullmatch(rf"{symbol}(?:\d{{4}})?", re.sub(r"\s+", "", cells[symbol_index]), re.I)
                ),
                None,
            )
            if row is None:
                missing_rows.append(symbol)
                continue
            missing_cells = [
                name
                for name, column in indexes.items()
                if column is not None and not re.sub(r"[-—/\s]", "", row[column])
            ]
            if missing_cells:
                incomplete.append(f"{symbol}缺{'/'.join(missing_cells)}")
        if not missing_rows and not incomplete:
            return
        details = [
            *( [f"缺少品种 {'/'.join(missing_rows)}"] if missing_rows else [] ),
            *incomplete,
        ]
        hard_failures.append(f"{label}执行表不完整：{'；'.join(details)}")
        return
    hard_failures.append(
        f"{label}必须使用包含品种、方向、触发、确认、止损、目标、仓位上限、信号有效期的 Markdown 表格"
    )


def _require_key_data_table(
    section: str,
    outline: dict[str, Any],
    hard_failures: list[str],
) -> None:
    for headers, rows in _markdown_tables(section):
        item_index = _column_index(headers, ("品种", "指标", "合约"))
        value_index = _column_index(headers, ("数值", "价格", "关键位"))
        time_index = _column_index(headers, ("时点", "时间", "日期", "口径"))
        meaning_index = _column_index(headers, ("含义", "意义", "判断"))
        if None in (item_index, value_index, time_index, meaning_index):
            continue
        assert item_index is not None and value_index is not None
        assert time_index is not None and meaning_index is not None
        complete = [
            row
            for row in rows
            if all(re.sub(r"[-—/\s]", "", row[index]) for index in (item_index, value_index, time_index, meaning_index))
        ]
        shallow_meanings = [
            row[item_index]
            for row in complete
            if len(re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", row[meaning_index])) < 3
        ]
        if shallow_meanings:
            hard_failures.append(f"关键数据表含义过度压缩：{'/'.join(shallow_meanings)}")
            return
        item_text = "\n".join(row[item_index] for row in complete)
        all_text = "\n".join("|".join(row) for row in complete)
        missing = [symbol for symbol in ("P", "Y", "OI") if re.search(rf"(?:^|[^A-Z]){symbol}(?:\d{{4}})?(?:[^A-Z]|$)", item_text, re.I) is None]
        if missing:
            hard_failures.append(f"关键数据表缺少品种：{'/'.join(missing)}")
            return
        if not any(
            marker in all_text
            for marker in ("FCPO", "BMD", "CBOT", "WTI", "原油", "美豆", "CPOTR", "ICDX", "印尼CPO")
        ):
            hard_failures.append("关键数据表缺少可核验的关键外盘或原油数据")
            return
        if not any(marker in all_text for marker in ("价差", "基差")):
            hard_failures.append("关键数据表缺少至少一个价差或基差")
            return
        key_tokens = _trade_numbers(str(outline.get("stop_loss") or "")) + _trade_numbers(
            str(outline.get("target_range") or "")
        )
        if not key_tokens or not any(_has_number(all_text, token) for token in key_tokens):
            hard_failures.append("关键数据表缺少提纲中可执行的 P 止损或目标关键位")
            return
        return
    hard_failures.append("关键数据与价格必须使用包含指标、数值、时点和含义的 Markdown 表格")


def _require_weekly_data_table(section: str, hard_failures: list[str]) -> None:
    for headers, rows in _markdown_tables(section):
        indexes = {
            "指标": _column_index(headers, ("品种", "指标", "合约")),
            "数值": _column_index(headers, ("数值", "价格", "本周")),
            "统计时间": _column_index(headers, ("时点", "时间", "日期", "口径")),
            "变化": _column_index(headers, ("变化", "涨跌", "上周")),
            "含义": _column_index(headers, ("含义", "意义", "判断")),
        }
        if any(index is None for index in indexes.values()):
            continue
        complete = [
            row
            for row in rows
            if all(index is not None and re.sub(r"[-—/\s]", "", row[index]) for index in indexes.values())
        ]
        item_index = indexes["指标"]
        assert item_index is not None
        item_text = "\n".join(row[item_index] for row in complete)
        missing = [symbol for symbol in ("P", "Y", "OI") if re.search(rf"(?:^|[^A-Z]){symbol}(?:\d{{4}})?(?:[^A-Z]|$)", item_text, re.I) is None]
        if missing:
            hard_failures.append(f"周报核心数据表缺少品种：{'/'.join(missing)}")
            return
        missing_spreads = [name for name in ("豆棕价差", "菜豆油价差") if name not in item_text]
        if missing_spreads:
            hard_failures.append(f"周报核心数据表缺少相对价值指标：{'/'.join(missing_spreads)}")
        return
    hard_failures.append("周报核心数据变化必须使用包含指标、数值、统计时间、变化和含义的 Markdown 表格")


def _require_weekly_events_table(section: str, hard_failures: list[str]) -> None:
    for headers, rows in _markdown_tables(section):
        indexes = {
            "日期": _column_index(headers, ("日期", "星期", "交易日")),
            "事件": _column_index(headers, ("事件", "主线")),
            "重要性": _column_index(headers, ("重要性", "重要程度")),
            "触发条件": _column_index(headers, ("触发", "条件")),
        }
        if any(index is None for index in indexes.values()):
            continue
        date_index = indexes["日期"]
        assert date_index is not None
        missing: list[str] = []
        for day in ("周一", "周二", "周三", "周四", "周五"):
            row = next((cells for cells in rows if day in cells[date_index]), None)
            if row is None or any(
                index is not None and not re.sub(r"[-—/\s]", "", row[index])
                for index in indexes.values()
            ):
                missing.append(day)
        if missing:
            hard_failures.append(f"下周事件表缺少完整事件、重要性或触发条件：{'/'.join(missing)}")
        return
    hard_failures.append("下周主线与事件必须使用包含日期、事件、重要性和触发条件的 Markdown 表格")


def _require_scenario_table(section: str, kind: str, hard_failures: list[str]) -> None:
    required_columns = {
        "情景": ("情景",),
        "触发": ("触发",),
        "确认": ("确认",),
        "动作": ("动作", "应对"),
        "放弃条件": ("放弃条件",),
    }
    if kind == "weekend":
        required_columns["概率"] = ("概率",)
    scenarios = ("高开", "平开", "低开") if kind == "daily" else ("高开高走", "高开震荡", "高开回落", "低开")
    for headers, rows in _markdown_tables(section):
        indexes = {name: _column_index(headers, aliases) for name, aliases in required_columns.items()}
        if any(index is None for index in indexes.values()):
            continue
        scenario_index = indexes["情景"]
        assert scenario_index is not None
        missing: list[str] = []
        for scenario in scenarios:
            row = next((cells for cells in rows if scenario in cells[scenario_index]), None)
            if row is None or any(
                column is not None and not re.sub(r"[-—/\s]", "", row[column])
                for column in indexes.values()
            ):
                missing.append(scenario)
        if missing:
            hard_failures.append(f"开盘情景表缺少完整触发→确认→动作→放弃链：{'/'.join(missing)}")
            return
        if not ("Y" in section and "OI" in section and any(marker in section for marker in ("同步", "背离", "分化"))):
            hard_failures.append("开盘情景表未说明 Y/OI 同步或背离对 P 的影响")
        return
    suffix = "及概率" if kind == "weekend" else ""
    hard_failures.append(f"开盘推演必须使用包含情景、触发、确认、动作、放弃条件{suffix}的 Markdown 表格")


def _require_source_audit(section: str, kind: str, hard_failures: list[str]) -> None:
    required = {
        "实际 skill": ("实际skill", "实际 skill", "调用skill", "调用 skill"),
        "数据源": ("数据源", "来源"),
        "截止时间": ("截止时间", "数据截止", "截至"),
        "失败项": ("失败项", "失败来源", "不可用"),
        "替代来源": ("替代来源", "替代数据源", "切换来源"),
    }
    compact = re.sub(r"\s+", "", section)
    missing = [name for name, aliases in required.items() if not any(re.sub(r"\s+", "", alias) in compact for alias in aliases)]
    if missing:
        hard_failures.append(f"信息来源与核验说明缺少审计字段：{'/'.join(missing)}")
        return
    required_stages = (
        ("行情采集", "数据门禁", "预测反馈", "新鲜度治理", "正文写作", "标题门", "报告审计", "预测冻结")
        if kind == "daily"
        else ("行情采集", "数据门禁", "新鲜度治理", "正文写作", "标题门", "报告审计")
    )
    missing_stages = [stage for stage in required_stages if stage not in section]
    if missing_stages:
        hard_failures.append(f"信息来源与核验说明缺少执行链阶段：{'/'.join(missing_stages)}")


def _future_source_dates(value: Any, report_date: str, prefix: str = "") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in {"fetched_at", "published_at", "trade_date"} and isinstance(child, str):
                matched = re.match(r"(20\d{2}-\d{2}-\d{2})", child.strip())
                if matched and matched.group(1) > report_date:
                    failures.append(f"{path}={matched.group(1)}")
            failures.extend(_future_source_dates(child, report_date, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(_future_source_dates(child, report_date, f"{prefix}[{index}]"))
    return failures


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def audit_report(
    report: Path,
    outline_path: Path,
    kind: str,
    source_json: Path,
    feedback_path: Path | None = None,
    min_score: int = QUALITY_RELEASE_SCORE,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    hard_failures: list[str] = []
    components = {
        "data_accuracy": 20,
        "view_trade_consistency": 20,
        "freshness_source_state": 15,
        "causal_chain_expectation_gap": 15,
        "risk_invalidation": 10,
        "structural_completeness": 10,
        "concision_repetition": 10,
    }
    try:
        text = report.read_text(encoding="utf-8")
        outline = _read_object(outline_path)
        source = _read_object(source_json)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "status": "blocked",
            "can_publish": False,
            "score": 0,
            "minimum_score": min_score,
            "components": {key: 0 for key in components},
            "hard_failures": [f"输入不可用：{exc}"],
            "errors": [],
            "warnings": [],
        }

    outline_issues = _outline_errors(outline, kind)
    if outline_issues:
        hard_failures.extend(outline_issues)
        components["structural_completeness"] = 0

    expected_sections = DAILY_SECTIONS if kind == "daily" else WEEKEND_SECTIONS
    names = _section_names(text)
    missing = [name for name in expected_sections if name not in names]
    if missing:
        hard_failures.append(f"缺少必需栏目：{', '.join(missing)}")
        components["structural_completeness"] = max(0, 10 - 2 * len(missing))
    present_expected = [name for name in names if name in expected_sections]
    if present_expected != [name for name in expected_sections if name in names]:
        errors.append("必需栏目顺序不符合 Writing Skill 契约")
        components["structural_completeness"] = max(0, components["structural_completeness"] - 3)

    body_chars = visible_body_chars(text)
    lower, upper = BODY_LIMITS[kind]
    if body_chars < lower or body_chars > upper:
        errors.append(f"正文篇幅 {body_chars} 字，不在 {lower}-{upper} 字预算内")
        components["concision_repetition"] = max(0, components["concision_repetition"] - 5)

    records = _flatten_records(source)
    record_by_key = {record.key: record for record in records}
    numeric_checks: list[dict[str, Any]] = []
    for key in CRITICAL_KEYS:
        record = record_by_key.get(key)
        if record is None:
            hard_failures.append(f"关键行情源缺失：{key}")
            components["data_accuracy"] = 0
            continue
        check = _record_check(text, record, required=True)
        numeric_checks.append(check)
        if not check["mentioned"]:
            hard_failures.append(f"报告缺少关键品种：{record.name}")
        elif not check["price_ok"]:
            hard_failures.append(f"关键行情不一致：{record.name} 应为 {record.price:g}")
        if check["percent_checked"] and not check["percent_ok"]:
            hard_failures.append(f"关键涨跌幅不一致：{record.name} 应为 {record.change_pct:.2f}%")

    mentioned_noncritical: list[NumericRecord] = []
    for record in records:
        if record.key in CRITICAL_KEYS:
            continue
        if any(_has_numeric_claim(line, record.aliases) for line in _lines_for_aliases(text, record.aliases)):
            mentioned_noncritical.append(record)
    noncritical_checks = {record.key: _record_check(text, record, required=False) for record in mentioned_noncritical}
    for record in mentioned_noncritical:
        check = noncritical_checks[record.key]
        is_spread = ".spread." in record.key
        if is_spread:
            numeric_checks.append(check)
            if not check["price_ok"]:
                hard_failures.append(f"价差不一致：{record.name} 应为 {record.price:g}")
        if check["percent_checked"] and not check["percent_ok"]:
            if not is_spread:
                numeric_checks.append(check)
            hard_failures.append(f"涨跌幅不一致：{record.name} 应为 {record.change_pct:.2f}%")
    sampled = _deterministic_sample(mentioned_noncritical, f"{outline.get('report_date')}|{kind}", 3)
    for record in sampled:
        check = noncritical_checks[record.key]
        if not any(row["key"] == check["key"] for row in numeric_checks):
            numeric_checks.append(check)
        if not check["price_ok"]:
            hard_failures.append(f"抽样数字不一致：{record.name} 应为 {record.price:g}")
    if len(sampled) < 3:
        hard_failures.append(f"可复核的非关键数字仅 {len(sampled)} 项，未达到固定抽样 3 项")
        components["data_accuracy"] = 0

    report_date = str(outline.get("report_date") or source.get("date") or "")
    future_dates = _future_source_dates(source, report_date) if report_date else []
    if future_dates:
        hard_failures.append(f"源数据含报告日之后的日期：{', '.join(future_dates[:5])}")
        components["freshness_source_state"] = 0

    for field in TRADE_FIELDS:
        value = outline.get(field)
        if not isinstance(value, str):
            continue
        missing_tokens = [token for token in _trade_numbers(value) if not _has_number(text, token)]
        for date_or_time in re.findall(r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}", value):
            if date_or_time not in text:
                missing_tokens.append(date_or_time)
        if missing_tokens:
            hard_failures.append(f"交易计划与提纲不一致：{field} 缺少 {', '.join(missing_tokens)}")

    stance = outline.get("market_stance")
    if kind == "daily":
        strategy_stances = re.findall(r"今日策略[：:]\s*(偏多|偏空|震荡|观望)", _section(text, "今日交易信号"))
        if not strategy_stances:
            hard_failures.append("今日交易信号缺少可校验的“今日策略”")
        elif len(set(strategy_stances)) != 1 or strategy_stances[0] != stance:
            hard_failures.append(f"交易方向冲突：提纲为{stance}，正文为{'/'.join(strategy_stances)}")
    else:
        stance_text = _section(text, "一句话核心观点") + _section(text, "交易计划")
        if isinstance(stance, str) and stance not in stance_text:
            hard_failures.append(f"周报正文未落实基准方向：{stance}")

    _require_top_call(text, outline, kind, errors, components)
    _require_decision_sections(text, kind, errors, components)

    stale_drivers: list[str] = []
    for field in ("primary_driver", "secondary_driver"):
        driver = outline.get(field)
        if isinstance(driver, dict) and driver.get("evidence_level") != "Level 1":
            stale_drivers.append(str(driver.get("name") or field))
    if stale_drivers:
        hard_failures.append(f"Level 2/3 信息被升级为主线：{', '.join(stale_drivers)}")
        components["freshness_source_state"] = 0

    if not outline.get("data_cutoff") or "信息来源与核验说明" not in names:
        components["freshness_source_state"] = max(0, components["freshness_source_state"] - 5)
    core_text = re.split(r"^##\s*【信息来源与核验说明】", text, maxsplit=1, flags=re.MULTILINE)[0]
    forbidden_source_state = [
        marker
        for marker in ("source_error", "抓取失败", "官方检查失败", "官方来源不可访问")
        if marker in core_text
    ]
    if forbidden_source_state:
        hard_failures.append(
            f"数据源错误被升级为正文驱动：{', '.join(forbidden_source_state)}"
        )
        components["freshness_source_state"] = 0
    gap_count = core_text.count("需进一步核验")
    if gap_count:
        hard_failures.append(f"“需进一步核验”在来源说明之前出现 {gap_count} 次")
        components["freshness_source_state"] = 0

    if kind == "daily":
        if feedback_path is None:
            hard_failures.append("日报缺少预测 feedback 输入")
        else:
            try:
                feedback = _read_object(feedback_path)
                disclosures = feedback.get("required_report_disclosures")
                if not isinstance(disclosures, list) or not disclosures:
                    hard_failures.append("预测 feedback 缺少必需披露")
                else:
                    for disclosure in disclosures:
                        if not isinstance(disclosure, str) or disclosure not in text:
                            hard_failures.append(f"预测披露缺失：{disclosure}")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                hard_failures.append(f"预测 feedback 不可用：{exc}")

    driver_text = _section(text, "核心驱动与预期差") if kind == "daily" else _section(text, "本周验证与预期差")
    if kind == "daily" and len(re.sub(r"\s+", "", driver_text)) < 350:
        hard_failures.append("核心驱动与预期差分析不足350字，未达到完整版研究深度")
        components["causal_chain_expectation_gap"] = 0
    driver_names = " ".join(
        str((outline.get(field) or {}).get("name") or "")
        for field in ("primary_driver", "secondary_driver")
        if isinstance(outline.get(field), dict)
    )
    if "评分" in driver_text or "评分" in driver_names or re.search(r"(?:driver|technical|fundamental)\s*=", driver_text, re.I):
        hard_failures.append("内部评分被用作研究驱动")
        components["causal_chain_expectation_gap"] = 0
    if any(
        marker in driver_text
        for marker in ("缺少供需增量", "暂无强新增驱动", "数据缺失", "来源失败")
    ):
        hard_failures.append("证据缺口被用作市场主驱动")
        components["causal_chain_expectation_gap"] = 0
    if not any(
        marker in driver_text + driver_names
        for marker in ("供给", "供应", "需求", "库存", "出口", "产量", "基差", "价差", "进口", "压榨")
    ):
        hard_failures.append("核心驱动缺少基本面或相对价值证据")
        components["causal_chain_expectation_gap"] = 0

    if kind == "weekend":
        history = source.get("research_history") if isinstance(source.get("research_history"), dict) else {}
        previous = history.get("previous_report") if isinstance(history.get("previous_report"), dict) else None
        validation_text = _section(text, "本周验证与预期差")
        if previous:
            previous_date = str(previous.get("date") or "").removesuffix("-weekend")
            previous_title = str(previous.get("title") or "")
            previous_headline = str(previous.get("headline") or "")
            if previous_date not in validation_text or not any(
                value and value in validation_text for value in (previous_title, previous_headline)
            ):
                hard_failures.append("周报未引用并验证上一期报告")
        elif "建立连续验证基线" not in validation_text:
            hard_failures.append("无历史周报时未声明建立连续验证基线")
        for section_name in ("核心数据变化", "下周主线与事件", "交易计划"):
            if not _has_markdown_table(_section(text, section_name)):
                hard_failures.append(f"周报栏目缺少结构化表格：{section_name}")
        trade_plan = _section(text, "交易计划")
        _require_weekly_data_table(_section(text, "核心数据变化"), hard_failures)
        _require_weekly_events_table(_section(text, "下周主线与事件"), hard_failures)
        _require_execution_table(trade_plan, "周报交易计划", hard_failures)
        _require_scenario_table(_section(text, "周一开盘推演"), kind, hard_failures)
        for spread_name in ("豆棕价差", "菜豆油价差"):
            if spread_name not in text:
                hard_failures.append(f"周报缺少相对价值指标：{spread_name}")
    else:
        trade_signal = _section(text, "今日交易信号")
        _require_execution_table(trade_signal, "日报交易信号", hard_failures)
        _require_key_data_table(_section(text, "关键数据与价格"), outline, hard_failures)
        _require_scenario_table(_section(text, "开盘推演"), kind, hard_failures)
    _require_source_audit(_section(text, "信息来源与核验说明"), kind, hard_failures)
    if not any(marker in driver_text for marker in ("→", "传导", "因此", "使得")):
        errors.append("核心驱动缺少可识别的因果链")
        components["causal_chain_expectation_gap"] -= 5
    if not ("预期" in driver_text and any(marker in driver_text for marker in ("现实", "兑现", "定价"))):
        errors.append("核心驱动未清楚区分预期与现实/定价")
        components["causal_chain_expectation_gap"] -= 5
    counter_case = str(outline.get("strongest_counter_case") or "")
    counter_text = driver_text + _section(text, "风险提示")
    counter_terms = [term for term in re.split(r"并|且|、|，|；|。", counter_case) if len(term.strip()) >= 4]
    counter_is_grounded = bool(counter_case) and (
        counter_case in counter_text
        or (counter_terms and all(term.strip() in counter_text for term in counter_terms))
    )
    if not counter_is_grounded or not any(marker in counter_text for marker in ("反证", "失效", "推翻", "相反")):
        errors.append("正文未明确呈现最强反证")
        components["causal_chain_expectation_gap"] -= 3
        components["risk_invalidation"] -= 3
    if not any(marker in _section(text, "风险提示") for marker in ("失效", "若", "一旦", "推翻")):
        errors.append("风险提示未写成可检验的失效条件")
        components["risk_invalidation"] -= 5

    research_evidence = source.get("news_and_research_evidence")
    if isinstance(research_evidence, dict):
        fresh_events = [
            item
            for item in research_evidence.get("today_new_drivers", [])
            if isinstance(item, dict) and item.get("mainline_eligible") is True
        ]
        if not fresh_events:
            hard_failures.append("当期没有通过 freshness 治理的 Level 1 快讯或研报证据")
            components["freshness_source_state"] = 0
        else:
            evidence_used = any(_fresh_event_used(item, text) for item in fresh_events)
            if not evidence_used:
                hard_failures.append("正文未使用任何已通过 freshness 治理的快讯或研报证据")
                components["freshness_source_state"] = 0
        source_status = [
            item for item in research_evidence.get("source_status", []) if isinstance(item, dict)
        ]
        unavailable = [
            str(item.get("name"))
            for item in source_status
            if item.get("name") and item.get("state") not in {"ready", "degraded"}
        ]
        source_section = _section(text, "信息来源与核验说明")
        undisclosed = [name for name in unavailable if name not in source_section]
        if undisclosed:
            hard_failures.append(f"来源失败或不可用状态未披露：{', '.join(undisclosed)}")
            components["freshness_source_state"] = 0
        failed_names = {
            str(item.get("name"))
            for item in source_status
            if item.get("name") and item.get("state") not in {"ready", "degraded"}
        }
        for field in ("primary_driver", "secondary_driver"):
            driver = outline.get(field)
            driver_source = str(driver.get("source") or "") if isinstance(driver, dict) else ""
            matched_failure = next(
                (
                    name
                    for name in failed_names
                    if driver_source and (driver_source in name or name in driver_source)
                ),
                None,
            )
            if matched_failure:
                hard_failures.append(f"{field} 使用失败来源：{matched_failure}")
                components["freshness_source_state"] = 0

    if AI_DISCLAIMER not in _section(text, "AI观点风险提示"):
        hard_failures.append("AI观点风险提示未使用完整固定声明")
        components["structural_completeness"] = 0

    conclusion_count = text.count("【结论】")
    if conclusion_count > 2:
        warnings.append(f"机械性“【结论】”出现 {conclusion_count} 次")
        errors.append("机械性“【结论】”超过全文两次上限")
        components["concision_repetition"] = max(0, components["concision_repetition"] - min(5, conclusion_count - 2))
    duplicates = _duplicate_sentences(text)
    if duplicates:
        warnings.append(f"发现 {len(duplicates)} 个重复长句")
        errors.append("正文存在重复长句或重复新闻")
        components["concision_repetition"] = max(0, components["concision_repetition"] - min(5, len(duplicates) * 2))

    if hard_failures:
        components["data_accuracy"] = 0 if any("行情" in item or "数字" in item or "交易计划" in item for item in hard_failures) else components["data_accuracy"]
        components["view_trade_consistency"] = (
            0 if any("方向冲突" in item or "交易计划" in item for item in hard_failures) else components["view_trade_consistency"]
        )
    components = {key: max(0, int(value)) for key, value in components.items()}
    score = sum(components.values())
    can_publish = score >= min_score and not errors and not hard_failures
    return {
        "status": "ok" if can_publish else "blocked",
        "can_publish": can_publish,
        "score": score,
        "minimum_score": min_score,
        "components": components,
        "body_character_count": body_chars,
        "body_character_budget": [lower, upper],
        "numeric_audit": {
            "critical_checked": len([row for row in numeric_checks if row["required"]]),
            "sample_seed": f"{outline.get('report_date')}|{kind}",
            "sampled_noncritical": [record.key for record in sampled],
            "checks": numeric_checks,
        },
        "hard_failures": hard_failures,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--outline", required=True, type=Path)
    parser.add_argument("--kind", required=True, choices=("daily", "weekend"))
    parser.add_argument("--source-json", required=True, type=Path)
    parser.add_argument("--feedback", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-score", type=int, default=QUALITY_RELEASE_SCORE)
    args = parser.parse_args()
    result = audit_report(
        report=args.report,
        outline_path=args.outline,
        kind=args.kind,
        source_json=args.source_json,
        feedback_path=args.feedback,
        min_score=args.min_score,
    )
    if args.output is not None:
        _atomic_write(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["can_publish"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify that a public report preserves the repository publication contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DAILY_SECTIONS = (
    "今日观点",
    "今日交易信号",
    "核心驱动与预期差",
    "盘前市场全景",
    "关键数据与价格",
    "价格预测与验证",
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
DAILY_STAGES = (
    "行情采集",
    "数据门禁",
    "预测反馈",
    "新鲜度治理",
    "正文写作",
    "标题门",
    "报告审计",
    "预测冻结",
)
WEEKEND_STAGES = (
    "行情采集",
    "数据门禁",
    "新鲜度治理",
    "正文写作",
    "标题门",
    "报告审计",
)
FORECAST_AI_DISCLAIMER = (
    "以上价格预测由AI基于所列来源和既定模型生成，不代表任何来源方的官方立场，"
    "不构成投资建议，用户须自行核验。"
)


def section_names(markdown: str) -> list[str]:
    return re.findall(r"^##\s*【([^】]+)】\s*$", markdown, re.MULTILINE)


def section(markdown: str, name: str) -> str:
    found = re.search(
        rf"^##\s*【{re.escape(name)}】\s*\n(?P<body>.*?)(?=^##\s*【|\Z)",
        markdown,
        re.MULTILINE | re.DOTALL,
    )
    return found.group("body").strip() if found else ""


def markdown_tables(value: str) -> list[tuple[list[str], list[list[str]]]]:
    lines = [line.strip() for line in value.splitlines()]
    tables: list[tuple[list[str], list[list[str]]]] = []
    index = 0
    while index + 1 < len(lines):
        header = lines[index]
        separator = lines[index + 1]
        if not (
            header.startswith("|")
            and header.endswith("|")
            and re.fullmatch(r"\|[\s:|-]+\|", separator)
        ):
            index += 1
            continue
        headers = [cell.strip() for cell in header.strip("|").split("|")]
        rows: list[list[str]] = []
        index += 2
        while index < len(lines) and lines[index].startswith("|") and lines[index].endswith("|"):
            cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(cells)
            index += 1
        tables.append((headers, rows))
    return tables


def require_table(
    markdown: str,
    section_name: str,
    expected_headers: tuple[str, ...],
    errors: list[str],
) -> list[list[str]]:
    tables = markdown_tables(section(markdown, section_name))
    for headers, rows in tables:
        if tuple(headers) == expected_headers:
            return rows
    errors.append(f"{section_name}缺少固定表头：{'｜'.join(expected_headers)}")
    return []


def validate_report_record(record: dict[str, Any], download_markdown: str) -> dict[str, Any]:
    errors: list[str] = []
    report_id = str(record.get("date") or "")
    kind = str(record.get("kind") or "")
    markdown = record.get("content")
    if not report_id:
        errors.append("报告缺少 date")
    if kind not in {"daily", "weekend"}:
        errors.append(f"报告 kind 无效：{kind or 'missing'}")
    if not isinstance(markdown, str) or not markdown.strip():
        errors.append("报告 content 为空")
        markdown = ""

    expected_sections = DAILY_SECTIONS if kind == "daily" else WEEKEND_SECTIONS
    names = section_names(markdown)
    if tuple(names) != expected_sections:
        errors.append(
            "栏目顺序不符合合同："
            + " → ".join(names or ["无栏目"])
        )

    quality = record.get("quality")
    if not isinstance(quality, dict):
        errors.append("报告缺少公开质量证据")
    else:
        score = quality.get("score")
        minimum = quality.get("minimum_score")
        if quality.get("can_publish") is not True or quality.get("status") != "ok":
            errors.append("公开质量证据未通过")
        if not isinstance(score, (int, float)) or not isinstance(minimum, (int, float)) or score < minimum:
            errors.append("公开质量分低于发布门槛")

    if markdown.rstrip("\r\n") != download_markdown.rstrip("\r\n"):
        errors.append("API 正文与下载 Markdown 不一致")

    plan_section = "今日交易信号" if kind == "daily" else "交易计划"
    plan_rows = require_table(
        markdown,
        plan_section,
        ("品种", "方向", "触发", "确认", "止损", "目标", "仓位上限", "信号有效期"),
        errors,
    )
    if plan_rows:
        symbols = {re.sub(r"\d{4}$", "", row[0].upper()) for row in plan_rows if row}
        missing_symbols = [symbol for symbol in ("P", "Y", "OI") if symbol not in symbols]
        if missing_symbols:
            errors.append(f"{plan_section}缺少品种：{'/'.join(missing_symbols)}")
        if any(any(not re.sub(r"[-—/\s]", "", cell) for cell in row) for row in plan_rows):
            errors.append(f"{plan_section}存在空白执行字段")

    if kind == "daily":
        panorama_rows = require_table(
            markdown,
            "盘前市场全景",
            ("维度", "已验证事实", "对P/Y/OI影响", "盘中验证信号"),
            errors,
        )
        if len(panorama_rows) < 4:
            errors.append("盘前市场全景少于四个完整维度")
        data_rows = require_table(
            markdown,
            "关键数据与价格",
            ("指标", "数值", "时点", "含义"),
            errors,
        )
        shallow = [
            row[0]
            for row in data_rows
            if len(re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", row[3])) < 3
        ]
        if shallow:
            errors.append(f"关键数据含义过度压缩：{'/'.join(shallow)}")
        forecast_rows = require_table(
            markdown,
            "价格预测与验证",
            ("品种", "参考价", "基准判断", "下沿观察", "上沿观察", "上修触发", "下修/失效", "置信度"),
            errors,
        )
        if forecast_rows:
            forecast_symbols = {
                re.sub(r"\d{4}$", "", row[0].upper()) for row in forecast_rows if row
            }
            missing_forecasts = [symbol for symbol in ("P", "Y", "OI") if symbol not in forecast_symbols]
            if missing_forecasts:
                errors.append(f"价格预测与验证缺少品种：{'/'.join(missing_forecasts)}")
            if any(
                len(row) != 8
                or any(not re.sub(r"[-—/\s]", "", cell) for cell in row)
                or re.fullmatch(r"[★☆]{5}", row[7]) is None
                for row in forecast_rows
            ):
                errors.append("价格预测与验证存在空白字段或无效置信度")
        if FORECAST_AI_DISCLAIMER not in section(markdown, "价格预测与验证"):
            errors.append("价格预测与验证缺少紧邻的 AI 风险提示")
        require_table(
            markdown,
            "开盘推演",
            ("情景", "触发", "确认", "动作", "放弃条件"),
            errors,
        )
        top_call = section(markdown, "今日观点")
        if not any(marker in top_call for marker in ("执行", "观望", "空仓", "不开仓", "不新开仓", "不追")):
            errors.append("今日观点缺少明确行动")
    else:
        require_table(
            markdown,
            "核心数据变化",
            ("指标", "数值", "统计时间", "变化", "含义"),
            errors,
        )
        require_table(
            markdown,
            "下周主线与事件",
            ("日期", "事件", "重要性", "触发条件"),
            errors,
        )
        require_table(
            markdown,
            "周一开盘推演",
            ("情景", "概率", "触发", "确认", "动作", "放弃条件"),
            errors,
        )

    source_audit = section(markdown, "信息来源与核验说明")
    stages = DAILY_STAGES if kind == "daily" else WEEKEND_STAGES
    missing_stages = [stage for stage in stages if stage not in source_audit]
    if missing_stages:
        errors.append(f"公开执行链缺少阶段：{'/'.join(missing_stages)}")
    for field in ("实际 skill", "数据源", "截止时间", "失败项", "替代来源"):
        if field not in source_audit:
            errors.append(f"信息来源与核验说明缺少字段：{field}")

    return {
        "status": "ok" if not errors else "blocked",
        "can_publish": not errors,
        "report_id": report_id,
        "kind": kind,
        "errors": errors,
    }


def fetch_text(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "palm-oil-public-contract/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-url", default="https://palm.vinsontesla.com/api/reports")
    parser.add_argument("--base-url", default="https://palm.vinsontesla.com/")
    parser.add_argument("--report-id")
    parser.add_argument("--kind", choices=("daily", "weekend"))
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(fetch_text(args.reports_url, args.timeout))
        if not isinstance(payload, list):
            raise ValueError("reports API 顶层不是数组")
        record = next(
            (
                item
                for item in payload
                if isinstance(item, dict)
                and (not args.report_id or item.get("date") == args.report_id)
                and (not args.kind or item.get("kind") == args.kind)
            ),
            None,
        )
        if record is None:
            raise ValueError("没有找到符合条件的报告")
        download = str(record.get("download") or "")
        if not download:
            raise ValueError("报告缺少 download 路径")
        download_url = urllib.parse.urljoin(args.base_url, download)
        result = validate_report_record(record, fetch_text(download_url, args.timeout))
    except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
        result = {
            "status": "blocked",
            "can_publish": False,
            "report_id": args.report_id,
            "kind": args.kind,
            "errors": [f"公网报告读取失败：{exc}"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["can_publish"] else 2


if __name__ == "__main__":
    sys.exit(main())

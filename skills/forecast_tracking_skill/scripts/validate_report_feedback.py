#!/usr/bin/env python3
"""Block report publication when forecast-review generation constraints were not applied."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


STAR_RE = re.compile(r"置信度[：:]\s*([★☆]{5})")


def validate_report(report: Path, feedback: Path, report_date: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        report_day = date.fromisoformat(report_date)
        payload = json.loads(feedback.read_text(encoding="utf-8"))
        text = report.read_text(encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "blocked", "can_publish": False, "errors": [str(exc)], "warnings": []}
    if not isinstance(payload, dict) or payload.get("schema_version") != "forecast-generation-feedback-v1":
        errors.append("预测校准上下文结构无效")
        payload = {}
    try:
        feedback_day = date.fromisoformat(str(payload.get("as_of")))
        age = (report_day - feedback_day).days
        if age < 0:
            errors.append("预测校准上下文来自未来日期")
        elif age > 7:
            errors.append("预测校准上下文超过7天，必须重新生成")
    except ValueError:
        errors.append("预测校准上下文缺少有效as_of")
    metrics_as_of = payload.get("metrics_as_of")
    if metrics_as_of is not None:
        try:
            metrics_day = date.fromisoformat(str(metrics_as_of))
            metrics_age = (report_day - metrics_day).days
            if metrics_age < 0:
                errors.append("预测统计来自未来日期")
            elif metrics_age > 7:
                errors.append("预测统计超过7天，必须先修复收盘复盘链路")
        except ValueError:
            errors.append("预测校准上下文的metrics_as_of无效")

    disclosures = payload.get("required_report_disclosures", [])
    if not isinstance(disclosures, list) or not disclosures:
        errors.append("预测校准上下文缺少必需披露")
    else:
        for disclosure in disclosures:
            if not isinstance(disclosure, str) or disclosure not in text:
                errors.append(f"报告未落实预测复盘约束：{disclosure}")

    cap = payload.get("core_view_confidence_cap_stars")
    if isinstance(cap, int) and cap < 5:
        section_match = re.search(r"## 【今日观点】(?P<body>.*?)(?=\n## |\Z)", text, re.DOTALL)
        if section_match is None:
            errors.append("报告缺少【今日观点】，无法校验复盘置信度上限")
        else:
            ratings = STAR_RE.findall(section_match.group("body"))
            if not ratings:
                errors.append("【今日观点】缺少可校验的五星置信度")
            elif any(rating.count("★") > cap for rating in ratings):
                errors.append(f"【今日观点】置信度超过复盘上限{cap}星")

    if payload.get("human_approval_required") is True and "需人工确认的改进建议" not in text:
        errors.append("连续复盘错误已触发人工确认，但报告未标注“需人工确认的改进建议”")

    return {"status": "ok" if not errors else "blocked", "can_publish": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--feedback", required=True, type=Path)
    parser.add_argument("--report-date", required=True)
    args = parser.parse_args()
    result = validate_report(args.report, args.feedback, args.report_date)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["can_publish"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

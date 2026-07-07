#!/usr/bin/env python3
"""Master entrypoint for oil-futures tab contract analysis."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CHILD_ENGINE = ROOT / "skills" / "technical_basic_analysis_skill" / "scripts" / "analysis_engine.py"


def load_child_engine():
    spec = importlib.util.spec_from_file_location("technical_basic_analysis_engine", CHILD_ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load child skill engine: {CHILD_ENGINE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_quality(item: dict[str, Any]) -> dict[str, Any]:
    score = item.get("score", {})
    basic = score.get("fundamental")
    technical = score.get("technical")
    driver = score.get("driver")
    money_flow = score.get("money_flow")
    total = score.get("total")
    notes: list[str] = []
    required_scores = [basic, technical, driver, money_flow, total]
    if all(isinstance(value, (int, float)) for value in required_scores):
        expected = round(technical * 0.25 + basic * 0.25 + driver * 0.30 + money_flow * 0.20, 1)
        if abs(expected - total) > 0.05:
            notes.append(f"综合评分口径需核验：期望 {expected}，当前 {total}")
    else:
        notes.append("评分字段需进一步核验：必须包含 technical、fundamental、driver、money_flow、total")

    if "driver" not in score:
        notes.append("缺少 driver_score")
    if "money_flow" not in score:
        notes.append("缺少 money_flow_score")
    confidence = item.get("view_confidence") or score.get("view_confidence")
    if confidence not in ("高", "中", "低"):
        notes.append("缺少 view_confidence 或取值不合规")
    warning = item.get("contradiction_warning") or score.get("contradiction_warning")
    if not warning:
        notes.append("缺少 contradiction_warning")

    stance = score.get("stance")
    tech_dir = "up" if isinstance(technical, (int, float)) and technical >= 55 else "down" if isinstance(technical, (int, float)) and technical <= 45 else "flat"
    driver_dir = "up" if isinstance(driver, (int, float)) and driver >= 55 else "down" if isinstance(driver, (int, float)) and driver <= 45 else "flat"
    money_dir = "up" if isinstance(money_flow, (int, float)) and money_flow >= 55 else "down" if isinstance(money_flow, (int, float)) and money_flow <= 45 else "flat"
    if tech_dir != "flat" and driver_dir not in ("flat", tech_dir) and money_dir not in ("flat", tech_dir) and stance in ("偏多", "偏空"):
        notes.append("存在技术面单独决定总观点的风险")

    recommendation = item.get("strategy_recommendation", {})
    if not recommendation:
        notes.append("观察位与失效条件需进一步核验")
    else:
        text = json.dumps(recommendation, ensure_ascii=False)
        if any(word in text for word in ["止盈", "止损"]):
            notes.append("策略输出仍含明确止盈/止损指令，应改为观察位和失效条件")
        if not recommendation.get("invalidation"):
            notes.append("缺少观点失效条件")
    if not item.get("view"):
        notes.append("走势观点需进一步核验")
    return {
        **item,
        "analysis_skill": "master_analytic_skill",
        "child_skill": "technical_basic_analysis_skill",
        "quality_note": "；".join(notes) if notes else "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
    }


def analyze(payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any] | list[dict[str, Any]]:
    engine = load_child_engine()
    if isinstance(payload, list):
        return [check_quality(engine.analyze_contract(item)) for item in payload]
    return check_quality(engine.analyze_contract(payload))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON file. Reads stdin when omitted.")
    args = parser.parse_args()
    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    payload = json.loads(raw)
    print(json.dumps(analyze(payload), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

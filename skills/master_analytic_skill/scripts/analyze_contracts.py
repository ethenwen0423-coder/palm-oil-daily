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
    total = score.get("total")
    notes: list[str] = []
    if isinstance(basic, (int, float)) and isinstance(technical, (int, float)) and isinstance(total, (int, float)):
        expected = round(basic * 0.30 + technical * 0.70, 1)
        if abs(expected - total) > 0.05:
            notes.append(f"综合评分口径需核验：期望 {expected}，当前 {total}")
    else:
        notes.append("评分字段需进一步核验")
    if not item.get("strategies"):
        notes.append("策略点位需进一步核验")
    if not item.get("view"):
        notes.append("走势观点需进一步核验")
    return {
        **item,
        "analysis_skill": "master_analytic_skill",
        "child_skill": "technical_basic_analysis_skill",
        "quality_note": "；".join(notes) if notes else "评分、观点与策略已通过skill质量检查",
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

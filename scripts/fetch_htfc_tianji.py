#!/usr/bin/env python3
"""Collect read-only Huatai Futures Tianji evidence for governed oil reports."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SKILLS = Path.home() / ".codex" / "skills"


def load_module(skill: str) -> Any:
    path = SKILLS / skill / "scripts" / "get_data.py"
    if not path.exists():
        raise RuntimeError(f"天玑 skill 脚本缺失：{path}")
    spec = importlib.util.spec_from_file_location(f"{skill.replace('-', '_')}_data", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载天玑 skill：{skill}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect(report_date: str, kind: str) -> dict[str, Any]:
    if not os.environ.get("HTFC_BASE_URL") or not os.environ.get("HTFC_API_KEY"):
        raise RuntimeError("HTFC_BASE_URL 或 HTFC_API_KEY 未配置，无法执行天玑只读查询")
    news = load_module("htfc-news-flash")
    trend = load_module("htfc-trend-compass")
    payload: dict[str, Any] = {
        "source": "华泰期货天玑实时接口",
        "report_date": report_date,
        "kind": kind,
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "news_flash": news.get_news_flash(),
        "trend_compass": {"rank": trend.get_rank(), "overview": trend.get_overview()},
    }
    if kind == "daily":
        payload["pre_market_strategy"] = load_module("htfc-pre-market-strategy").get_article_point(date=report_date)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--kind", choices=("daily", "weekend"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = collect(args.date, args.kind)
    except Exception as exc:
        print(f"天玑采集失败：{exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

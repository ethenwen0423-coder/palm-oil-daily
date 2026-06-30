#!/usr/bin/env python3
"""Validate report titles before publishing site data."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TITLE_TERMS = (
    "加仓",
    "减仓",
    "止损",
    "止盈",
    "追高",
    "低吸",
    "承接",
    "回踩买入",
    "突破买入",
    "逢低做多",
    "逢高做空",
    "仓位建议",
    "等确认",
    "不追",
)
GENERIC_TITLES = (
    "棕榈油每日晨报",
    "棕榈油行情日报",
    "今日晨报",
    "今日周报",
    "周末总结与开盘预测",
    "发生了什么事",
)
PRICE_RE = re.compile(r"(?<!\d)(?:[1-9]\d{2,5})(?!\d)")


def first_heading(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def first_section_text(content: str, names: tuple[str, ...]) -> str:
    lines = [line.strip() for line in content.splitlines()]
    for index, line in enumerate(lines):
        if line.startswith("##") and any(name in line for name in names):
            for row in lines[index + 1 :]:
                if row.startswith("##"):
                    break
                if row and not row.startswith("【结论】") and not row.startswith("|---"):
                    return row.strip("| ").strip()
    return ""


def visible_len(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def validate(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8").strip()
    errors: list[str] = []
    title = first_heading(content)
    headline = first_section_text(content, ("今日观点", "一句话核心观点"))
    is_weekly = path.stem.endswith("-weekend")
    expected_suffix = "周报" if is_weekly else "晨报"

    if not title:
      errors.append("缺少 Markdown 一级标题")
    elif not re.fullmatch(r"\d{2}月\d{2}日(?:晨报|周报)", title):
      errors.append(f"一级标题必须是 MM月DD日{expected_suffix} 格式")
    elif not title.endswith(expected_suffix):
      errors.append(f"一级标题类型应为{expected_suffix}")
    elif visible_len(title) > 15:
      errors.append("一级标题超过 15 字")

    if not headline:
      errors.append("缺少【今日观点】或【一句话核心观点】首句")
    else:
      if any(term in headline for term in FORBIDDEN_TITLE_TERMS):
          errors.append("Headline 含交易执行语言，应移入交易计划")
      if PRICE_RE.search(headline):
          errors.append("Headline 含具体执行价格，应移入交易计划")
      if headline in GENERIC_TITLES:
          errors.append("Headline 是泛标题，缺少市场观点")
      if visible_len(headline) > (100 if is_weekly else 50):
          errors.append("Headline 超过规定长度")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate report title quality.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        errors = validate(path)
        if errors:
            failed = True
            print(f"{path}: 需重写")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{path}: 通过")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

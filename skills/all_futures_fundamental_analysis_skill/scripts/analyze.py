#!/usr/bin/env python3
"""Fundamental skill runtime for one user-selected futures contract."""

from __future__ import annotations

from typing import Any


SKILL_NAME = "all_futures_fundamental_analysis_skill"


def analyze(symbol: str, snapshot: dict[str, Any] | None, evidence: dict[str, Any] | None) -> dict[str, Any]:
    result = dict(snapshot or {})
    factors = [dict(item) for item in result.get("factors", []) if isinstance(item, dict)]
    if evidence:
        title = str(evidence.get("title") or "当前基本面证据")
        factors = [dict(evidence)] + [item for item in factors if str(item.get("title")) != title]
        result.update({
            "skill": SKILL_NAME,
            "status": "observed",
            "evidence_status": "observed",
            "evidence_count": max(1, int(result.get("evidence_count") or 0)),
            "bias": "neutral",
            "summary": f"基本面分析 skill 已按 {symbol} 检查相关来源；当前可验证数值置于首位，低频证据保留原日期。",
        })
    else:
        result.update({
            "skill": SKILL_NAME,
            "status": "missing",
            "evidence_status": result.get("evidence_status") or "missing",
            "bias": "unverified",
            "summary": f"基本面分析 skill 已按 {symbol} 检查相关来源，但未取得新增可验证数值；以下仅为最近发布快照与跟踪框架。",
        })
    result["factors"] = factors
    return result


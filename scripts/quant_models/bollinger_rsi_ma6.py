"""Adapter for the MA20 entry, RSI divergence, and MA6 stop model."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPT = ROOT / "skills" / "generate-oilseed-trade-signal" / "scripts" / "generate_signal.py"


metadata = {
    "id": "bollinger-rsi-ma6-v1",
    "name": "布林中轨 + RSI 背离模型",
    "short_name": "布林中轨 + RSI 背离",
    "version": "1.0",
    "status": "active",
    "status_label": "已启用",
    "skill": "generate-oilseed-trade-signal",
    "timeframe": "日线",
    "validated_instrument": "AKShare P0 棕榈油主力连续日线",
    "validation_note": "成熟回测结论仅适用于 P0；其他油脂油料合约为同规则试算。",
    "universe": ["P 棕榈油", "Y 豆油", "OI 菜油", "M 豆粕", "RM 菜粕"],
    "summary": "以 MA20 穿越识别方向，以 RSI 价格背离锁定止盈，并使用多空非对称 MA6 规则控制回撤。",
    "tags": ["MA20 趋势", "RSI 背离", "MA6 风控", "次日开盘执行"],
    "rules": {
        "entry": {
            "title": "趋势入场",
            "summary": "完整日线收盘穿越 MA20 后，于次交易日开盘执行。",
            "conditions": [
                "收盘价由下向上穿越 MA20：确认做多信号",
                "收盘价由上向下穿越 MA20：确认做空信号",
                "执行窗口已过时不追单，等待下一个确认信号",
            ],
        },
        "take_profit": {
            "title": "RSI 背离止盈",
            "summary": "用 20 日价格极值与 RSI 是否同步确认判断趋势衰竭。",
            "conditions": [
                "多单：价格创 20 日新高，RSI 未创对应新高，全部止盈",
                "空单：价格创 20 日新低，RSI 未创对应新低，全部止盈",
                "只使用已完成日线确认背离",
            ],
        },
        "stop": {
            "title": "多空非对称止损",
            "summary": "多单先等待浮盈激活保护，空单则用更快的 MA6 收盘规则。",
            "conditions": [
                "多单最大有利浮动达到 0.75 倍入场 ATR 后，激活 MA6 保护",
                "激活后连续两个完整收盘低于 MA6，多单全部止损",
                "一个完整收盘高于 MA6，空单全部止损",
            ],
        },
        "reentry": {
            "title": "再入场锁定",
            "summary": "止损后不立即重复开同方向仓位。",
            "conditions": [
                "止损方向保持锁定",
                "只有出现反向 MA20 穿越后，才解除原方向锁定",
            ],
        },
        "execution": {
            "title": "执行约束",
            "summary": "信号与下单时点分离，避免使用未完成日线或追逐过期信号。",
            "conditions": [
                "默认只使用最新完整日线",
                "确认信号在次交易日开盘执行",
                "过期入场信号降级为观望；过期离场信号应在下一可用机会处理",
            ],
        },
    },
    "cost_assumption_one_way": 0.0004,
    "risk_notice": "该模型是基于历史日线的确定性规则，不保证未来表现；同规则试算不等于已完成独立回测验证。",
}


def _load_skill() -> Any:
    if not SKILL_SCRIPT.exists():
        raise FileNotFoundError(f"量化模型 skill 不存在: {SKILL_SCRIPT}")
    spec = importlib.util.spec_from_file_location("oilseed_trade_signal_skill", SKILL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载量化模型 skill")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _skill_args(position: str) -> SimpleNamespace:
    return SimpleNamespace(
        position=position,
        entry_date=None,
        entry_price=None,
        entry_atr=None,
        highest_since_entry=None,
        lowest_since_entry=None,
        blocked_direction="none",
        allow_forming_bar=False,
    )


def _build_contract(skill: Any, contract: dict[str, Any]) -> dict[str, Any]:
    symbol = str(contract["symbol"])
    raw, data_source = skill.fetch(symbol)
    completed, provisional, bar_note = skill.select_completed(raw, False)
    data = skill.indicators(completed)
    if len(data) < 40:
        raise RuntimeError("可用日线少于 40 根")

    signals: dict[str, Any] = {}
    for position in ("flat", "long", "short"):
        result = skill.decide(data, _skill_args(position), symbol)
        skill.mark_execution_window(result)
        result["data_source"] = data_source
        signals[position] = result

    latest = signals["flat"].get("market", {})
    product = str(contract.get("product", "")).upper()
    return {
        "symbol": symbol,
        "product": product,
        "product_name": contract.get("product_name", product),
        "rank": contract.get("rank"),
        "label": contract.get("label", ""),
        "market_date": signals["flat"].get("market_date"),
        "data_source": data_source,
        "bar_completed": not provisional,
        "bar_note": bar_note,
        "model_scope": "validated_mapping" if product == "P" else "rule_trial",
        "model_scope_label": "成熟模型映射" if product == "P" else "同规则试算",
        "market": latest,
        "signals": signals,
    }


def build_contracts(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skill = _load_skill()
    items: list[dict[str, Any]] = []
    for contract in contracts:
        try:
            items.append(_build_contract(skill, contract))
        except Exception as exc:
            items.append(
                {
                    "symbol": contract.get("symbol"),
                    "product": contract.get("product"),
                    "product_name": contract.get("product_name"),
                    "rank": contract.get("rank"),
                    "label": contract.get("label"),
                    "status": "error",
                    "message": str(exc),
                }
            )
    return items

#!/usr/bin/env python3
"""Persistent virtual-fund ledger for real delivery-contract model signals."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import statistics
import tempfile
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

SCHEMA_VERSION = 1
MODEL_VERSION = "palm-oil-v2-real-contract-indicators-carry5-main-contract"
DEFAULT_STATE_DIR = Path("/Users/ethen/.codex/state/bollinger-rsi-futures-fund")
INITIAL_CAPITAL = 1_000_000.0
CONTRACT_RE = re.compile(r"^[A-Z]{1,3}[0-9]{3,4}$")
FORBIDDEN_SUFFIX_RE = re.compile(r"^[A-Z]{1,3}0$")
ENTRY_ACTIONS = {"ENTER_LONG", "ENTER_SHORT", "ADD_LONG", "ADD_SHORT"}
EXIT_ACTIONS = {"EXIT_LONG", "EXIT_SHORT"}
ALL_ACTIONS = ENTRY_ACTIONS | EXIT_ACTIONS
DEFAULT_POLICY = {
    "max_gross_multiple": 2.0,
    "max_margin_fraction": 0.60,
    "max_variety_fraction": 0.25,
    "max_sector_fraction": 0.40,
    "max_positions": 8,
}


class LedgerError(ValueError):
    pass


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _money(value: float) -> float:
    return round(float(value), 8)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise LedgerError(f"state not initialized: {path.parent}") from exc


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def locked(state_dir: Path) -> Iterator[None]:
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / ".lock").open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def state_path(state_dir: Path) -> Path:
    return state_dir / "state.json"


def _new_state(
    initial_capital: float,
    *,
    model_version: str = MODEL_VERSION,
    fund_name: str = "布林RSI期货虚拟基金",
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "fund_name": fund_name,
        "model_version": model_version,
        "created_at": _now(),
        "initial_capital": initial_capital,
        "cash": initial_capital,
        "equity": initial_capital,
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "total_fees": 0.0,
        "high_water_equity": initial_capital,
        "max_drawdown": 0.0,
        "used_margin": 0.0,
        "gross_notional": 0.0,
        "last_mark_date": None,
        "positions": {},
        "pending_orders": [],
        "filled_order_ids": [],
        "policy": {**DEFAULT_POLICY, **(policy or {})},
    }


def _validate_contract(contract: str) -> str:
    value = str(contract).strip().upper()
    if FORBIDDEN_SUFFIX_RE.fullmatch(value) or not CONTRACT_RE.fullmatch(value):
        raise LedgerError(f"actual delivery-month contract required, got {contract!r}")
    month = int(value[-2:])
    if not 1 <= month <= 12:
        raise LedgerError(f"invalid delivery month in contract {contract!r}")
    return value


def _positive(item: dict[str, Any], key: str, *, zero_ok: bool = False) -> float:
    try:
        value = float(item[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise LedgerError(f"{key} must be numeric") from exc
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero_ok):
        raise LedgerError(f"{key} must be {'non-negative' if zero_ok else 'positive'}")
    return value


def _order_id(signal: dict[str, Any], as_of: str) -> str:
    identity = "|".join(str(value) for value in (
        as_of, signal.get("variety"), signal.get("contract"), signal.get("action"),
        signal.get("signal_date"), signal.get("execution_date"),
    ))
    return "ord_" + hashlib.sha256(identity.encode()).hexdigest()[:16]


def _revalue(state: dict[str, Any]) -> None:
    unrealized = gross = margin = 0.0
    for position in state["positions"].values():
        last = float(position["last_price"])
        qty = int(position["quantity"])
        multiplier = float(position["multiplier"])
        side = int(position["side"])
        notional = abs(qty * last * multiplier)
        pnl = side * qty * multiplier * (last - float(position["average_price"]))
        position["notional"] = _money(notional)
        position["used_margin"] = _money(notional * float(position["margin_rate"]))
        position["unrealized_pnl"] = _money(pnl)
        unrealized += pnl
        gross += notional
        margin += position["used_margin"]
    state["unrealized_pnl"] = _money(unrealized)
    state["gross_notional"] = _money(gross)
    state["used_margin"] = _money(margin)
    state["equity"] = _money(float(state["cash"]) + unrealized)
    state["high_water_equity"] = _money(max(float(state["high_water_equity"]), state["equity"]))
    drawdown = state["equity"] / state["high_water_equity"] - 1 if state["high_water_equity"] else 0.0
    state["max_drawdown"] = _money(min(float(state["max_drawdown"]), drawdown))


def _reserved(state: dict[str, Any]) -> tuple[float, float, dict[str, float], dict[str, float]]:
    gross = margin = 0.0
    varieties: dict[str, float] = {}
    sectors: dict[str, float] = {}
    for order in state["pending_orders"]:
        if order["status"] != "pending" or order["action"] not in ENTRY_ACTIONS:
            continue
        notional = int(order["quantity"]) * float(order["reference_price"]) * float(order["multiplier"])
        gross += notional
        margin += notional * float(order["margin_rate"])
        varieties[order["variety"]] = varieties.get(order["variety"], 0.0) + notional
        sectors[order["sector"]] = sectors.get(order["sector"], 0.0) + notional
    return gross, margin, varieties, sectors


def _existing_exposure(state: dict[str, Any], key: str, value: str) -> float:
    return sum(
        float(position.get("notional", 0.0))
        for position in state["positions"].values()
        if str(position.get(key, "")) == value
    )


def _size_signal(state: dict[str, Any], signal: dict[str, Any]) -> tuple[int, str]:
    policy = state["policy"]
    if policy.get("enforce_caps") is False:
        _positive(signal, "reference_price")
        _positive(signal, "multiplier")
        _positive(signal, "margin_rate")
        try:
            quantity = int(signal["requested_quantity"])
        except (KeyError, TypeError, ValueError) as exc:
            raise LedgerError("requested_quantity must be a positive integer when caps are disabled") from exc
        if quantity < 1:
            raise LedgerError("requested_quantity must be a positive integer when caps are disabled")
        return quantity, "AI自主决定整手数量；账本不施加仓位上限"
    price = _positive(signal, "reference_price")
    multiplier = _positive(signal, "multiplier")
    margin_rate = _positive(signal, "margin_rate")
    variety = str(signal["variety"]).upper()
    sector = str(signal.get("sector", "未分类"))
    equity = float(state["equity"])
    reserved_gross, reserved_margin, reserved_varieties, reserved_sectors = _reserved(state)
    gross_left = max(0.0, equity * policy["max_gross_multiple"] - state["gross_notional"] - reserved_gross)
    margin_left = max(0.0, equity * policy["max_margin_fraction"] - state["used_margin"] - reserved_margin)
    variety_left = max(0.0, equity * policy["max_variety_fraction"] - _existing_exposure(state, "variety", variety) - reserved_varieties.get(variety, 0.0))
    sector_left = max(0.0, equity * policy["max_sector_fraction"] - _existing_exposure(state, "sector", sector) - reserved_sectors.get(sector, 0.0))
    if str(signal["action"]).startswith("ENTER"):
        # Reserve the other half of the variety cap for the model's sole pyramid layer.
        variety_left = min(variety_left, equity * policy["max_variety_fraction"] / 2)
    per_contract = price * multiplier
    quantity = math.floor(min(gross_left, variety_left, sector_left, margin_left / margin_rate) / per_contract)
    return (quantity, "按组合容量取整手数") if quantity >= 1 else (0, "因资金/风控未执行")


def _pending_for(state: dict[str, Any], variety: str) -> bool:
    return any(order["variety"] == variety and order["status"] == "pending" for order in state["pending_orders"])


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    if args.initial_capital <= 0:
        raise LedgerError("initial capital must be positive")
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        if path.exists() and not args.if_missing:
            raise LedgerError(f"state already exists: {path}")
        if not path.exists():
            model_version = str(getattr(args, "model_version", MODEL_VERSION))
            fund_name = str(getattr(args, "fund_name", "布林RSI期货虚拟基金"))
            state = _new_state(
                float(args.initial_capital),
                model_version=model_version,
                fund_name=fund_name,
                policy=getattr(args, "policy", None),
            )
            _atomic_json(path, state)
            _append_jsonl(args.state_dir / "trade_ledger.jsonl", {
                "event": "FUND_INITIALIZED", "timestamp": _now(),
                "initial_capital": float(args.initial_capital), "model_version": model_version,
            })
        else:
            state = _read_json(path)
    return state


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    with locked(args.state_dir):
        state = _read_json(state_path(args.state_dir))
        _revalue(state)
    return state


def command_verify(args: argparse.Namespace) -> dict[str, Any]:
    with locked(args.state_dir):
        state = _read_json(state_path(args.state_dir))
        errors: list[str] = []
        if state.get("schema_version") != SCHEMA_VERSION:
            errors.append("schema_version mismatch")
        expected_model = str(getattr(args, "model_version", MODEL_VERSION))
        if state.get("model_version") != expected_model:
            errors.append("model_version mismatch")
        seen: set[str] = set()
        for variety, position in state.get("positions", {}).items():
            try:
                _validate_contract(position["contract"])
            except LedgerError as exc:
                errors.append(f"{variety}: {exc}")
            if int(position.get("quantity", 0)) <= 0:
                errors.append(f"{variety}: non-positive quantity")
            if int(position.get("side", 0)) not in {-1, 1}:
                errors.append(f"{variety}: invalid side")
        for order in state.get("pending_orders", []):
            if order["order_id"] in seen:
                errors.append(f"duplicate order id {order['order_id']}")
            seen.add(order["order_id"])
        _revalue(state)
        if abs(state["equity"] - state["cash"] - state["unrealized_pnl"]) > 1e-6:
            errors.append("equity identity failed")
    return {"ok": not errors, "errors": errors, "state_dir": str(args.state_dir)}


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    snapshot = _read_json(args.signals)
    if snapshot.get("completed_bar") is not True:
        raise LedgerError("only completed daily bars may create orders")
    as_of = str(snapshot.get("as_of", ""))
    signals = snapshot.get("signals")
    if not as_of or not isinstance(signals, list):
        raise LedgerError("as_of and signals list are required")
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        state = _read_json(path)
        if snapshot.get("model_version") != state.get("model_version"):
            raise LedgerError(f"model_version must be {state.get('model_version')}")
        _revalue(state)
        decisions: list[dict[str, Any]] = []
        normalized: list[dict[str, Any]] = []
        for raw in signals:
            item = dict(raw)
            action = str(item.get("action", "")).upper()
            if action not in ALL_ACTIONS:
                decisions.append({"signal": item, "status": "rejected", "reason": "unsupported action"})
                continue
            try:
                item["contract"] = _validate_contract(item.get("contract", ""))
                item["variety"] = str(item["variety"]).upper()
            except (KeyError, LedgerError) as exc:
                decisions.append({"signal": item, "status": "rejected", "reason": str(exc)})
                continue
            item["action"] = action
            normalized.append(item)
        priority = {"EXIT_LONG": 0, "EXIT_SHORT": 0, "ADD_LONG": 1, "ADD_SHORT": 1, "ENTER_LONG": 2, "ENTER_SHORT": 2}
        normalized.sort(key=lambda item: (priority[item["action"]], -float(item.get("score", -1e18))))
        active_varieties = set(state["positions"])
        existing_order_ids = {order["order_id"] for order in state["pending_orders"]}
        for signal in normalized:
            variety, action = signal["variety"], signal["action"]
            proposed_order_id = _order_id(signal, as_of)
            if proposed_order_id in existing_order_ids:
                decisions.append({"signal": signal, "status": "skipped", "reason": "signal order was already recorded"})
                continue
            if _pending_for(state, variety):
                decisions.append({"signal": signal, "status": "skipped", "reason": "variety already has a pending order"})
                continue
            position = state["positions"].get(variety)
            side = 1 if action.endswith("LONG") else -1
            if action in EXIT_ACTIONS:
                if not position or int(position["side"]) != side:
                    decisions.append({"signal": signal, "status": "skipped", "reason": "no matching open position"})
                    continue
                quantity = int(position["quantity"])
            else:
                if action.startswith("ENTER"):
                    if position:
                        decisions.append({"signal": signal, "status": "skipped", "reason": "position already exists"})
                        continue
                    if state["policy"].get("enforce_caps") is not False and len(active_varieties) >= int(state["policy"]["max_positions"]):
                        decisions.append({"signal": signal, "status": "skipped", "reason": "maximum concurrent varieties reached"})
                        continue
                    if "score" not in signal:
                        decisions.append({"signal": signal, "status": "skipped", "reason": "missing cross-sector allocation score"})
                        continue
                else:
                    if not position or int(position["side"]) != side:
                        decisions.append({"signal": signal, "status": "skipped", "reason": "no matching position to pyramid"})
                        continue
                    if int(position.get("layers", 1)) >= 2:
                        decisions.append({"signal": signal, "status": "skipped", "reason": "model pyramid already consumed"})
                        continue
                try:
                    _positive(signal, "atr14")
                    _positive(signal, "fee_rate", zero_ok=True)
                    quantity, sizing_reason = _size_signal(state, signal)
                except LedgerError as exc:
                    decisions.append({"signal": signal, "status": "rejected", "reason": str(exc)})
                    continue
                if quantity < 1:
                    decisions.append({"signal": signal, "status": "skipped", "reason": sizing_reason})
                    continue
            order = {
                "order_id": proposed_order_id, "status": "pending", "created_at": _now(),
                "as_of": as_of, "signal_date": signal.get("signal_date"),
                "execution_date": signal.get("execution_date"), "variety": variety,
                "name": signal.get("name", variety), "sector": signal.get("sector", "未分类"),
                "contract": signal["contract"], "action": action, "side": side,
                "quantity": quantity, "reference_price": signal.get("reference_price"),
                "atr14": signal.get("atr14"),
                "multiplier": signal.get("multiplier", position.get("multiplier") if position else None),
                "margin_rate": signal.get("margin_rate", position.get("margin_rate") if position else None),
                "margin_source": signal.get("margin_source", position.get("margin_source") if position else None),
                "margin_source_url": signal.get("margin_source_url", position.get("margin_source_url") if position else None),
                "margin_as_of": signal.get("margin_as_of", position.get("margin_as_of") if position else None),
                "margin_official_direct": signal.get("margin_official_direct", position.get("margin_official_direct") if position else None),
                "fee_rate": signal.get("fee_rate", position.get("fee_rate") if position else None),
                "score": signal.get("score"), "reason": signal.get("reason", "model signal"),
                "source": snapshot.get("source"),
                "strategy_name": signal.get("strategy_name"),
                "strategy_type": signal.get("strategy_type"),
                "strategy_source": signal.get("strategy_source"),
                "strategy_rationale": signal.get("strategy_rationale"),
                "strategy_entry_rule": signal.get("strategy_entry_rule"),
                "strategy_exit_rule": signal.get("strategy_exit_rule"),
                "backtest_summary": signal.get("backtest_summary"),
                "requested_quantity": signal.get("requested_quantity"),
                "quantity_reason": signal.get("quantity_reason"),
            }
            state["pending_orders"].append(order)
            existing_order_ids.add(proposed_order_id)
            if action.startswith("ENTER"):
                active_varieties.add(variety)
            decisions.append({"order": order, "status": "planned"})
        _atomic_json(path, state)
        _append_jsonl(args.state_dir / "trade_ledger.jsonl", {
            "event": "ORDER_PLAN", "timestamp": _now(), "as_of": as_of, "decisions": decisions,
        })
    return {"as_of": as_of, "decisions": decisions}


def _find_order(state: dict[str, Any], order_id: str) -> dict[str, Any]:
    matches = [order for order in state["pending_orders"] if order["order_id"] == order_id]
    if len(matches) != 1 or matches[0]["status"] != "pending":
        raise LedgerError(f"pending order not found or not unique: {order_id}")
    return matches[0]


def _assert_caps(state: dict[str, Any], variety: str) -> None:
    if state["policy"].get("enforce_caps") is False:
        return
    equity = float(state["equity"])
    policy = state["policy"]
    tolerance = 1e-7
    if state["gross_notional"] > equity * policy["max_gross_multiple"] + tolerance:
        raise LedgerError("actual fill would breach gross notional cap")
    if state["used_margin"] > equity * policy["max_margin_fraction"] + tolerance:
        raise LedgerError("actual fill would breach margin-use cap")
    position = state["positions"].get(variety)
    if position and position["notional"] > equity * policy["max_variety_fraction"] + tolerance:
        raise LedgerError("actual fill would breach per-variety cap")
    if position:
        sector_exposure = _existing_exposure(state, "sector", position["sector"])
        if sector_exposure > equity * policy["max_sector_fraction"] + tolerance:
            raise LedgerError("actual fill would breach sector cap")
    if len(state["positions"]) > int(policy["max_positions"]):
        raise LedgerError("actual fill would breach concurrent-position cap")


def command_fill(args: argparse.Namespace) -> dict[str, Any]:
    if args.price <= 0:
        raise LedgerError("fill price must be positive")
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        state = _read_json(path)
        order = _find_order(state, args.order_id)
        if args.date != order.get("execution_date") and not args.allow_date_mismatch:
            raise LedgerError(f"fill date {args.date} differs from intended execution date {order.get('execution_date')}")
        variety, action = order["variety"], order["action"]
        quantity = int(order["quantity"])
        position = state["positions"].get(variety)
        multiplier = float(order["multiplier"])
        fee_rate = float(order["fee_rate"])
        notional = quantity * args.price * multiplier
        fee = float(args.fee) if args.fee is not None else notional * fee_rate
        realized = 0.0
        if action in EXIT_ACTIONS:
            if not position or int(position["side"]) != int(order["side"]):
                raise LedgerError("position changed after exit plan; reconcile before filling")
            quantity = int(position["quantity"])
            multiplier = float(position["multiplier"])
            notional = quantity * args.price * multiplier
            fee = float(args.fee) if args.fee is not None else notional * float(position["fee_rate"])
            realized = int(position["side"]) * quantity * multiplier * (args.price - float(position["average_price"])) - fee
            state["cash"] = _money(state["cash"] + realized)
            state["realized_pnl"] = _money(state["realized_pnl"] + realized)
            del state["positions"][variety]
        elif action.startswith("ENTER"):
            if position:
                raise LedgerError("position already exists; reconcile before filling")
            state["cash"] = _money(state["cash"] - fee)
            state["realized_pnl"] = _money(state["realized_pnl"] - fee)
            state["positions"][variety] = {
                "variety": variety, "name": order["name"], "sector": order["sector"],
                "contract": order["contract"], "side": int(order["side"]),
                "quantity": quantity, "average_price": args.price, "last_price": args.price,
                "multiplier": multiplier, "margin_rate": float(order["margin_rate"]), "fee_rate": fee_rate,
                "margin_source": order.get("margin_source"),
                "margin_source_url": order.get("margin_source_url"),
                "margin_as_of": order.get("margin_as_of"),
                "margin_official_direct": order.get("margin_official_direct"),
                "entry_date": args.date, "entry_atr": order.get("atr14"), "layers": 1,
                "layer_fills": [{"date": args.date, "price": args.price, "quantity": quantity, "fee": fee}],
                "model_reason": order.get("reason"),
                "strategy_name": order.get("strategy_name"),
                "strategy_type": order.get("strategy_type"),
                "strategy_source": order.get("strategy_source"),
                "strategy_rationale": order.get("strategy_rationale"),
                "strategy_entry_rule": order.get("strategy_entry_rule"),
                "strategy_exit_rule": order.get("strategy_exit_rule"),
                "backtest_summary": order.get("backtest_summary"),
                "quantity_reason": order.get("quantity_reason"),
            }
        else:
            if not position or int(position["side"]) != int(order["side"]):
                raise LedgerError("position changed after pyramid plan; reconcile before filling")
            old_qty = int(position["quantity"])
            new_qty = old_qty + quantity
            average = (old_qty * position["average_price"] + quantity * args.price) / new_qty
            state["cash"] = _money(state["cash"] - fee)
            state["realized_pnl"] = _money(state["realized_pnl"] - fee)
            position["quantity"] = new_qty
            position["average_price"] = average
            position["last_price"] = args.price
            position["layers"] = int(position.get("layers", 1)) + 1
            position["layer_fills"].append({"date": args.date, "price": args.price, "quantity": quantity, "fee": fee})
        state["total_fees"] = _money(state["total_fees"] + fee)
        _revalue(state)
        if action in ENTRY_ACTIONS:
            _assert_caps(state, variety)
        order.update({"status": "filled", "fill_date": args.date, "fill_price": args.price, "fee": fee})
        state["filled_order_ids"].append(order["order_id"])
        _atomic_json(path, state)
        event = {
            "event": "FILL", "timestamp": _now(), "order_id": order["order_id"],
            "date": args.date, "variety": variety, "contract": order["contract"],
            "action": action, "side": order["side"], "quantity": quantity,
            "price": args.price, "multiplier": multiplier, "notional": notional,
            "fee": fee, "realized_pnl": realized, "virtual": True,
            "strategy_name": order.get("strategy_name"),
            "strategy_type": order.get("strategy_type"),
            "strategy_source": order.get("strategy_source"),
            "strategy_rationale": order.get("strategy_rationale"),
            "strategy_entry_rule": order.get("strategy_entry_rule"),
            "strategy_exit_rule": order.get("strategy_exit_rule"),
            "backtest_summary": order.get("backtest_summary"),
            "quantity_reason": order.get("quantity_reason"),
        }
        if action in EXIT_ACTIONS and position:
            event["entry_strategy_name"] = position.get("strategy_name")
        _append_jsonl(args.state_dir / "trade_ledger.jsonl", event)
    return {"fill": event, "state": state}


def command_cancel(args: argparse.Namespace) -> dict[str, Any]:
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        state = _read_json(path)
        order = _find_order(state, args.order_id)
        order.update({"status": "cancelled", "cancelled_at": _now(), "cancel_reason": args.reason})
        _atomic_json(path, state)
        event = {"event": "ORDER_CANCELLED", "timestamp": _now(), "order_id": args.order_id, "reason": args.reason}
        _append_jsonl(args.state_dir / "trade_ledger.jsonl", event)
    return event


def command_roll(args: argparse.Namespace) -> dict[str, Any]:
    new_contract = _validate_contract(args.new_contract)
    if min(args.old_price, args.new_price) <= 0:
        raise LedgerError("roll prices must be positive")
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        state = _read_json(path)
        variety = args.variety.upper()
        position = state["positions"].get(variety)
        if not position:
            raise LedgerError(f"no position for {variety}")
        old_contract = position["contract"]
        if new_contract == old_contract:
            raise LedgerError("new contract equals held contract")
        qty, multiplier, side = int(position["quantity"]), float(position["multiplier"]), int(position["side"])
        old_notional = qty * args.old_price * multiplier
        new_notional = qty * args.new_price * multiplier
        fee = (old_notional + new_notional) * float(position["fee_rate"])
        realized = side * qty * multiplier * (args.old_price - float(position["average_price"])) - fee
        state["cash"] = _money(state["cash"] + realized)
        state["realized_pnl"] = _money(state["realized_pnl"] + realized)
        state["total_fees"] = _money(state["total_fees"] + fee)
        position.update({"contract": new_contract, "average_price": args.new_price, "last_price": args.new_price})
        position["roll_count"] = int(position.get("roll_count", 0)) + 1
        position.setdefault("rolls", []).append({
            "date": args.date, "from": old_contract, "to": new_contract,
            "old_price": args.old_price, "new_price": args.new_price, "fee": fee,
        })
        _revalue(state)
        _atomic_json(path, state)
        event = {
            "event": "ROLL", "timestamp": _now(), "date": args.date, "variety": variety,
            "from_contract": old_contract, "to_contract": new_contract, "quantity": qty,
            "old_price": args.old_price, "new_price": args.new_price, "fee": fee,
            "realized_pnl": realized, "virtual": True,
        }
        _append_jsonl(args.state_dir / "trade_ledger.jsonl", event)
    return {"roll": event, "state": state}


def command_mark(args: argparse.Namespace) -> dict[str, Any]:
    prices = _read_json(args.prices)
    mark_date, rows = str(prices.get("as_of", "")), prices.get("prices")
    if not mark_date or not isinstance(rows, list):
        raise LedgerError("mark file requires as_of and prices list")
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        state = _read_json(path)
        mapped = {str(row.get("variety", "")).upper(): row for row in rows}
        missing = []
        for variety, position in state["positions"].items():
            row = mapped.get(variety)
            if not row:
                missing.append(variety)
                continue
            contract = _validate_contract(row.get("contract", ""))
            if contract != position["contract"]:
                raise LedgerError(f"{variety} mark contract {contract} differs from held {position['contract']}")
            position.update({
                "last_price": _positive(row, "price"), "last_mark_date": mark_date,
                "mark_source": row.get("source", prices.get("source")),
            })
        if missing:
            raise LedgerError(f"missing marks for held varieties: {', '.join(sorted(missing))}")
        state["last_mark_date"] = mark_date
        _revalue(state)
        snapshot = _summary(state)
        _atomic_json(path, state)
        _append_jsonl(args.state_dir / "snapshots.jsonl", {"event": "DAILY_MARK", "timestamp": _now(), **snapshot})
    return snapshot


def command_update_margins(args: argparse.Namespace) -> dict[str, Any]:
    """Apply audited exact-contract exchange margin rates to live exposures."""
    payload = _read_json(args.rates)
    as_of, rows = str(payload.get("as_of", "")), payload.get("rates")
    if not as_of or not isinstance(rows, list):
        raise LedgerError("margin file requires as_of and rates list")
    by_contract: dict[str, dict[str, Any]] = {}
    for row in rows:
        contract = _validate_contract(row.get("contract", ""))
        rate = _positive(row, "margin_rate")
        if rate > 1:
            raise LedgerError(f"margin rate for {contract} must not exceed 1")
        by_contract[contract] = row
    with locked(args.state_dir):
        path = state_path(args.state_dir)
        state = _read_json(path)
        updated: list[str] = []
        for position in state["positions"].values():
            row = by_contract.get(position["contract"])
            if not row:
                continue
            position["margin_rate"] = float(row["margin_rate"])
            position["margin_source"] = row.get("source")
            position["margin_source_url"] = row.get("source_url")
            position["margin_as_of"] = row.get("source_updated_at") or as_of
            position["margin_official_direct"] = bool(row.get("official_direct"))
            updated.append(position["contract"])
        for order in state["pending_orders"]:
            if order.get("status") != "pending" or order.get("action") in EXIT_ACTIONS:
                continue
            row = by_contract.get(order["contract"])
            if not row:
                continue
            order["margin_rate"] = float(row["margin_rate"])
            order["margin_source"] = row.get("source")
            order["margin_source_url"] = row.get("source_url")
            order["margin_as_of"] = row.get("source_updated_at") or as_of
            order["margin_official_direct"] = bool(row.get("official_direct"))
            updated.append(order["contract"])
        _revalue(state)
        _atomic_json(path, state)
        _append_jsonl(args.state_dir / "trade_ledger.jsonl", {
            "event": "MARGIN_RATES_UPDATED", "timestamp": _now(), "as_of": as_of,
            "contracts": sorted(set(updated)), "source": payload.get("source"),
        })
    return state


def _summary(state: dict[str, Any]) -> dict[str, Any]:
    equity, initial = float(state["equity"]), float(state["initial_capital"])
    return {
        "fund_name": state["fund_name"], "model_version": state["model_version"],
        "date": state.get("last_mark_date"), "initial_capital": initial,
        "cash": state["cash"], "used_margin": state["used_margin"],
        "available_cash_after_margin": _money(state["cash"] - state["used_margin"]),
        "gross_notional": state["gross_notional"], "equity": equity,
        "realized_pnl": state["realized_pnl"], "unrealized_pnl": state["unrealized_pnl"],
        "total_fees": state["total_fees"], "cumulative_return": equity / initial - 1,
        "max_drawdown": state["max_drawdown"], "positions": list(state["positions"].values()),
        "pending_orders": [order for order in state["pending_orders"] if order["status"] == "pending"],
    }


def _ledger_events(state_dir: Path, target_date: str | None) -> list[dict[str, Any]]:
    if not target_date:
        return []
    path = state_dir / "trade_ledger.jsonl"
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        event_date = str(event.get("date") or event.get("as_of") or event.get("timestamp", "")[:10])
        if event_date == target_date and event.get("event") in {"FILL", "ROLL", "ORDER_CANCELLED"}:
            events.append(event)
    return events


def _performance_metrics(state_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    path = state_dir / "snapshots.jsonl"
    observations: dict[str, float] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("event") == "DAILY_MARK" and row.get("date"):
                observations[str(row["date"])] = float(row["equity"])
    ordered = sorted(observations.items())
    if len(ordered) < 30:
        return {"annualized_return": None, "sharpe": None, "performance_note": "少于30个有效日度权益快照，暂不年化"}
    elapsed = (date.fromisoformat(ordered[-1][0]) - date.fromisoformat(ordered[0][0])).days
    if elapsed < 90:
        return {"annualized_return": None, "sharpe": None, "performance_note": "权益历史少于90日，暂不年化"}
    returns = [ordered[index][1] / ordered[index - 1][1] - 1 for index in range(1, len(ordered))]
    volatility = statistics.stdev(returns) if len(returns) >= 2 else 0.0
    sharpe = statistics.mean(returns) / volatility * math.sqrt(242) if volatility > 0 else None
    annualized = (ordered[-1][1] / ordered[0][1]) ** (365.25 / elapsed) - 1
    return {
        "annualized_return": annualized, "sharpe": sharpe,
        "performance_note": f"基于{len(ordered)}个有效日度权益快照，未扣无风险利率",
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['fund_name']}日报", "",
        f"- 日期：{summary.get('date') or '尚未收盘盯市'}",
        f"- 模型版本：`{summary['model_version']}`",
        f"- 权益：¥{summary['equity']:,.2f}；累计收益：{summary['cumulative_return']:.2%}；最大回撤：{summary['max_drawdown']:.2%}",
        f"- 已实现盈亏：¥{summary['realized_pnl']:,.2f}；未实现盈亏：¥{summary['unrealized_pnl']:,.2f}；累计费用：¥{summary['total_fees']:,.2f}",
        f"- 现金：¥{summary['cash']:,.2f}；占用保证金：¥{summary['used_margin']:,.2f}；扣除保证金后可用：¥{summary['available_cash_after_margin']:,.2f}",
        f"- 年化与夏普：{'年化 ' + format(summary['annualized_return'], '.2%') + '；夏普 ' + format(summary['sharpe'], '.2f') if summary.get('annualized_return') is not None and summary.get('sharpe') is not None else '暂不输出'}（{summary['performance_note']}）",
        "", "## 今日账本事件", "",
    ]
    if not summary["today_events"]:
        lines.append("无已落账成交、换月或取消。")
    else:
        lines.extend(["| 类型 | 品种 | 合约/换月 | 动作 | 手数 | 价格 | 费用 | 已实现盈亏 |", "|---|---|---|---|---:|---:|---:|---:|"])
        for event in summary["today_events"]:
            contract = event.get("contract") or f"{event.get('from_contract')}→{event.get('to_contract')}"
            price = event.get("price") or event.get("new_price")
            lines.append(
                f"| {event['event']} | {event.get('variety', '')} | {contract} | {event.get('action', '')} | "
                f"{event.get('quantity', '')} | {price if price is not None else ''} | ¥{float(event.get('fee', 0)):,.2f} | ¥{float(event.get('realized_pnl', 0)):,.2f} |"
            )
    lines.extend(["", "## 当前持仓", ""])
    if not summary["positions"]:
        lines.append("空仓。")
    else:
        lines.extend(["| 品种 | 合约 | 方向 | 手数 | 层数 | 均价 | 最新价 | 名义金额 | 保证金 | 浮盈亏 |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
        for position in summary["positions"]:
            lines.append(
                f"| {position['name']} | {position['contract']} | {'多' if position['side'] == 1 else '空'} | "
                f"{position['quantity']} | {position.get('layers', 1)} | {position['average_price']:.4f} | "
                f"{position['last_price']:.4f} | ¥{position['notional']:,.2f} | ¥{position['used_margin']:,.2f} | ¥{position['unrealized_pnl']:,.2f} |"
            )
    lines.extend(["", "## 待执行订单", ""])
    if not summary["pending_orders"]:
        lines.append("无。")
    else:
        lines.extend(["| 订单 | 执行日 | 品种 | 合约 | 动作 | 手数 | 原因 |", "|---|---|---|---|---|---:|---|"])
        for order in summary["pending_orders"]:
            lines.append(f"| {order['order_id']} | {order.get('execution_date')} | {order['name']} | {order['contract']} | {order['action']} | {order['quantity']} | {order['reason']} |")
    lines.extend(["", "> AI 风险提示：本报告由 AI 基于所列真实合约数据、模型信号和虚拟基金账本生成，不代表任何数据源或机构的官方立场，不构成投资建议；虚拟成交不等于真实成交，请自行核验。"])
    return "\n".join(lines)


def command_report(args: argparse.Namespace) -> Any:
    with locked(args.state_dir):
        state = _read_json(state_path(args.state_dir))
        _revalue(state)
        summary = _summary(state)
        target_date = summary.get("date") or date.today().isoformat()
        summary["today_events"] = _ledger_events(args.state_dir, target_date)
        summary.update(_performance_metrics(args.state_dir, state))
    return _markdown(summary) if args.format == "markdown" else summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--initial-capital", type=float, default=INITIAL_CAPITAL)
    init.add_argument("--if-missing", action="store_true")
    sub.add_parser("status")
    sub.add_parser("verify")
    plan = sub.add_parser("plan")
    plan.add_argument("--signals", type=Path, required=True)
    fill = sub.add_parser("fill")
    fill.add_argument("--order-id", required=True)
    fill.add_argument("--date", required=True)
    fill.add_argument("--price", type=float, required=True)
    fill.add_argument("--fee", type=float)
    fill.add_argument("--allow-date-mismatch", action="store_true")
    cancel = sub.add_parser("cancel")
    cancel.add_argument("--order-id", required=True)
    cancel.add_argument("--reason", required=True)
    roll = sub.add_parser("roll")
    roll.add_argument("--variety", required=True)
    roll.add_argument("--new-contract", required=True)
    roll.add_argument("--date", required=True)
    roll.add_argument("--old-price", type=float, required=True)
    roll.add_argument("--new-price", type=float, required=True)
    mark = sub.add_parser("mark")
    mark.add_argument("--prices", type=Path, required=True)
    margins = sub.add_parser("update-margins")
    margins.add_argument("--rates", type=Path, required=True)
    report = sub.add_parser("report")
    report.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    commands = {
        "init": command_init, "status": command_status, "verify": command_verify,
        "plan": command_plan, "fill": command_fill, "cancel": command_cancel,
        "roll": command_roll, "mark": command_mark,
        "update-margins": command_update_margins, "report": command_report,
    }
    try:
        result = commands[args.command](args)
    except LedgerError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2) from exc
    print(result if isinstance(result, str) else json.dumps({"status": "ok", "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

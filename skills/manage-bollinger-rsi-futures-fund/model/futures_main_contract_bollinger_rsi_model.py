#!/usr/bin/env python3
"""布林中轨 + RSI 背离 + 非对称 MA6 止损的真实主力合约权益复利回测。

V2 更新：主力换月时，回看新主力合约在此前5个交易日中未消耗的
MA20 穿越入场信号；仅当T-1收盘仍与该信号同向时，T日开盘补发入场。

与主连代理回测的核心区别：
1. T 日交易 T-1 日成交量最大的交割月合约；
2. 每笔初始仓按入场时账户权益建立，盈利或亏损会改变下一笔仓位名义；
3. 换月时旧合约平仓、新合约开仓，计入双边成本；
4. 按新旧合约同日开盘价差平移入场参考价和高低水位，不重置
   entry ATR、浮盈 ATR、MA6 连续确认数、待加仓和方向锁定状态；
5. MA20/MA6/RSI/ATR/背离均在当时真实 PYYMM 合约自身的
   未复权日线历史上计算，不用跨合约价差拼接价格生成信号。

所有信号均为收盘确认、下一交易日开盘执行。
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import futures_real_contract_top20_backtest as data_source
import palm_oil_bollinger_rsi_ma6_strategy as signal_model


MODEL_NAME = "布林RSI模型"
MODEL_VERSION = "palm-oil-v2-real-contract-indicators-carry5-main-contract"
LEGACY_GAP_ADJUSTED_MODEL_VERSION = "palm-oil-v2-ma6-rsi-carry5-main-contract"
LEGACY_MODEL_VERSION = "bollinger-rsi-ma6-main-contract-roll-compound-v2"
FIXED_NOTIONAL_MODEL_VERSION = "bollinger-rsi-ma6-main-contract-roll-v1"
FUSION_MODEL_NAME = "布林RSI模型（均线融合研究变体）"
FUSION_MODEL_VERSION = "bollinger-rsi-ma6-ma5-ma20-fusion-research-v1"
COST = signal_model.COST
INITIAL_CAPITAL = 1.0
FIXED_NOTIONAL_PER_LAYER = 1.0
ENTRY_MODES = {"baseline", "ma_filter", "ma_cross", "union"}
EXIT_MODES = {"baseline", "combo", "regime", "spread_overlay", "spread_only"}


class RollDataError(ValueError):
    """换月日缺失旧合约开盘价，无法无偏地计算隔夜盈亏和价差。"""


def _prepare_indicator_series(frame: pd.DataFrame) -> pd.DataFrame:
    """在单一价格坐标上计算模型和研究模式所需的全部指标。"""
    prepared = signal_model.prepare(
        frame.sort_values("datetime").reset_index(drop=True), divergence_window=20
    )
    prepared["ma5"] = prepared.close.rolling(5, min_periods=5).mean()
    prepared["ma5_long_cross"] = (
        prepared.ma5.gt(prepared.ma20)
        & prepared.ma5.shift(1).le(prepared.ma20.shift(1))
    )
    prepared["ma5_short_cross"] = (
        prepared.ma5.lt(prepared.ma20)
        & prepared.ma5.shift(1).ge(prepared.ma20.shift(1))
    )
    prepared["ma5_ma20_spread_abs"] = (prepared.ma5 - prepared.ma20).abs()
    prepared["ma5_ma20_spread_max_5"] = prepared.ma5_ma20_spread_abs.rolling(
        5, min_periods=5
    ).max()
    prepared["ma5_ma20_spread_peak_5"] = (
        prepared.ma5_ma20_spread_abs.notna()
        & prepared.ma5_ma20_spread_max_5.notna()
        & prepared.ma5_ma20_spread_abs.ge(prepared.ma5_ma20_spread_max_5 - 1e-12)
    )
    up_move = prepared.high.diff()
    down_move = -prepared.low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    true_range = pd.concat([
        prepared.high - prepared.low,
        (prepared.high - prepared.close.shift()).abs(),
        (prepared.low - prepared.close.shift()).abs(),
    ], axis=1).max(axis=1)
    atr_adx = true_range.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean() / atr_adx
    minus_di = 100 * minus_dm.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean() / atr_adx
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    prepared["adx"] = dx.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    return prepared


def build_contract_indicators(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """对每个真实交割月合约独立计算指标。"""
    indicators: dict[str, pd.DataFrame] = {}
    for contract, group in raw.sort_values("date").groupby("contract"):
        contract_frame = group.rename(columns={"date": "datetime"}).copy()
        indicators[str(contract)] = _prepare_indicator_series(contract_frame).rename(
            columns={"datetime": "date"}
        )
    return indicators


def build_contract_signals(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """计算每个交割月自身序列的可观测入场信号，供换月回看使用。"""
    signals: dict[str, pd.DataFrame] = {}
    for contract, prepared in build_contract_indicators(raw).items():
        if len(prepared) < 21:
            continue
        signals[contract] = prepared[
            ["date", "long_signal", "short_signal", "atr", "close", "ma20"]
        ].copy()
    return signals


def _roll_carry_pending(
    contract_signals: dict[str, pd.DataFrame] | None,
    new_contract: str,
    roll_day: pd.Timestamp,
    lookback: int,
) -> tuple[int, float]:
    """返回换月日可执行的未消耗入场信号，严格只读取roll_day之前的K线。"""
    if not contract_signals or lookback <= 0:
        return 0, np.nan
    own = contract_signals.get(new_contract)
    if own is None or own.empty:
        return 0, np.nan
    before_roll = own.loc[own.date.lt(roll_day)].sort_values("date")
    if len(before_roll) < 2:
        return 0, np.nan
    window = before_roll.tail(lookback)
    long_hit = bool(window.long_signal.any())
    short_hit = bool(window.short_signal.any())
    if long_hit == short_hit:  # 无信号或双向信号同时存在，均不追入。
        return 0, np.nan
    last = before_roll.iloc[-1]
    direction = 1 if long_hit else -1
    if pd.isna(last.close) or pd.isna(last.ma20) or pd.isna(last.atr):
        return 0, np.nan
    trend_ok = last.close > last.ma20 if direction == 1 else last.close < last.ma20
    return (direction, float(last.atr)) if trend_ok else (0, np.nan)


def build_lagged_main_schedule(raw: pd.DataFrame) -> pd.DataFrame:
    """以 T-1 日可观测成交量选择 T 日主力合约。"""
    valid = raw.loc[raw["volume"].gt(0)].copy()
    winners = valid.loc[
        valid.groupby("date")["volume"].idxmax(), ["date", "contract", "volume"]
    ].sort_values("date")
    winners["active_contract"] = winners["contract"].shift(1)
    winners["selection_volume_t_minus_1"] = winners["volume"].shift(1)
    schedule = winners[["date", "active_contract", "selection_volume_t_minus_1"]].dropna()
    active = schedule.merge(
        raw,
        left_on=["date", "active_contract"],
        right_on=["date", "contract"],
        how="left",
        validate="one_to_one",
    ).sort_values("date").reset_index(drop=True)
    unavailable = active["contract"].isna()
    if unavailable.any():
        examples = active.loc[unavailable, ["date", "active_contract"]].head(5)
        detail = ", ".join(
            f"{row.date:%Y-%m-%d}:{row.active_contract}" for row in examples.itertuples(index=False)
        )
        raise RollDataError(f"selected main contract has no day-T bar: {detail}")
    return active.drop(columns=["active_contract"])


def prepare_gap_adjusted_main(active: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    """保留的修复前价差连续算法，仅供旧研究复现与对照。"""
    required = {"date", "contract", "open", "high", "low", "close", "volume"}
    missing = sorted(required.difference(active.columns) | required.difference(raw.columns))
    if missing:
        raise ValueError(f"missing columns: {missing}")
    active = active.sort_values("date").reset_index(drop=True).copy()
    if active.empty:
        raise ValueError("active main-contract schedule is empty")
    raw_lookup = raw.drop_duplicates(["date", "contract"], keep="last").set_index(["date", "contract"])
    adjustment = 0.0
    previous_contract = None
    adjusted_rows: list[dict] = []
    for row in active.itertuples(index=False):
        roll_gap = 0.0
        old_open = np.nan
        if previous_contract is not None and row.contract != previous_contract:
            key = (row.date, previous_contract)
            if key not in raw_lookup.index:
                raise RollDataError(
                    f"{row.date:%Y-%m-%d} {previous_contract}->{row.contract}: missing old-contract open"
                )
            old_open = float(raw_lookup.loc[key, "open"])
            roll_gap = float(row.open) - old_open
            adjustment -= roll_gap
        item = row._asdict()
        for column in ("open", "high", "low", "close"):
            item[f"raw_{column}"] = float(item[column])
            item[column] = float(item[column]) + adjustment
        item["price_adjustment"] = adjustment
        item["roll_gap"] = roll_gap
        item["old_contract_open"] = old_open
        item["rolled"] = previous_contract is not None and row.contract != previous_contract
        adjusted_rows.append(item)
        previous_contract = row.contract
    continuous = pd.DataFrame(adjusted_rows).rename(columns={"date": "datetime"})
    prepared = _prepare_indicator_series(continuous)
    output = prepared.rename(columns={"datetime": "date"})
    output.attrs["contract_signals"] = build_contract_signals(raw)
    output.attrs["roll_lookback"] = 5
    output.attrs["indicator_policy"] = "legacy opening-gap-adjusted stitched main series"
    return output


def prepare_contract_local_main(active: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    """用活跃交割月合约自身的未复权历史计算当日指标。"""
    required = {"date", "contract", "open", "high", "low", "close", "volume"}
    missing = sorted(required.difference(active.columns) | required.difference(raw.columns))
    if missing:
        raise ValueError(f"missing columns: {missing}")
    active = active.sort_values("date").reset_index(drop=True).copy()
    if active.empty:
        raise ValueError("active main-contract schedule is empty")
    raw_lookup = raw.drop_duplicates(["date", "contract"], keep="last").set_index(
        ["date", "contract"]
    )
    indicators = build_contract_indicators(raw)
    rows: list[dict] = []
    previous_contract: str | None = None
    for active_row in active.itertuples(index=False):
        contract = str(active_row.contract)
        own = indicators.get(contract)
        if own is None:
            raise ValueError(f"no indicator history for {contract}")
        match = own.loc[own.date.eq(active_row.date)]
        if len(match) != 1:
            raise ValueError(f"{active_row.date:%Y-%m-%d} {contract}: indicator row not unique")
        item = match.iloc[0].to_dict()
        if hasattr(active_row, "selection_volume_t_minus_1"):
            item["selection_volume_t_minus_1"] = active_row.selection_volume_t_minus_1
        for column in ("open", "high", "low", "close"):
            item[f"raw_{column}"] = float(item[column])
        rolled = previous_contract is not None and contract != previous_contract
        old_open = np.nan
        roll_gap = 0.0
        if rolled:
            key = (active_row.date, previous_contract)
            if key not in raw_lookup.index:
                raise RollDataError(
                    f"{active_row.date:%Y-%m-%d} {previous_contract}->{contract}: "
                    "missing old-contract open"
                )
            old_open = float(raw_lookup.loc[key, "open"])
            roll_gap = float(item["open"]) - old_open
        item["price_adjustment"] = 0.0
        item["roll_gap"] = roll_gap
        item["old_contract_open"] = old_open
        item["rolled"] = rolled
        rows.append(item)
        previous_contract = contract
    output = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    output.attrs["contract_signals"] = {
        contract: frame[["date", "long_signal", "short_signal", "atr", "close", "ma20"]].copy()
        for contract, frame in indicators.items()
        if len(frame) >= 21
    }
    output.attrs["roll_lookback"] = 5
    output.attrs["indicator_policy"] = "actual PYYMM contract own unadjusted history"
    return output


def _charge(cumulative_pnl: float, sides: int, layers: int, notional: float) -> tuple[float, float]:
    cost = sides * layers * notional * COST
    return cumulative_pnl - cost, cost


def run_backtest(
    prepared: pd.DataFrame,
    raw: pd.DataFrame,
    *,
    initial_capital: float = INITIAL_CAPITAL,
    fixed_notional_per_layer: float | None = None,
    entry_mode: str = "baseline",
    exit_mode: str = "baseline",
    adx_threshold: float = 25.0,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """默认按每笔入场权益复利；显式传入固定名义仅用于旧版精确对照。"""
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    if fixed_notional_per_layer is not None and fixed_notional_per_layer <= 0:
        raise ValueError("fixed_notional_per_layer must be positive when provided")
    if entry_mode not in ENTRY_MODES:
        raise ValueError(f"entry_mode must be one of {sorted(ENTRY_MODES)}")
    if exit_mode not in EXIT_MODES:
        raise ValueError(f"exit_mode must be one of {sorted(EXIT_MODES)}")
    contract_signals = prepared.attrs.get("contract_signals") if hasattr(prepared, "attrs") else None
    roll_lookback = int(prepared.attrs.get("roll_lookback", 5)) if hasattr(prepared, "attrs") else 5
    data = prepared.sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError("prepared data is empty")
    raw_lookup = raw.drop_duplicates(["date", "contract"], keep="last").set_index(["date", "contract"])

    compound_equity = fixed_notional_per_layer is None
    capital_policy = (
        "trade-level equity compounding; each layer uses equity at initial entry"
        if compound_equity else "fixed notional; no equity compounding"
    )
    benchmark_notional = (
        initial_capital if compound_equity else float(fixed_notional_per_layer)
    )
    cumulative_pnl = benchmark_pnl = 0.0
    benchmark_qty = 0.0
    active_notional_per_layer = benchmark_notional
    position = 0
    layers: list[dict] = []
    entry_reference = entry_atr = high_water = low_water = np.nan
    pending_exit_reason: str | None = None
    pending_entry = 0
    pending_entry_atr = np.nan
    pending_entry_reason = ""
    pending_pyramid = False
    pyramided = False
    stop_count = 0
    blocked_direction = 0
    trail_active = False
    trail_price = np.nan
    trade_exit_mode = ""
    roll_count = 0
    roll_cost = total_cost = 0.0
    trade_start_pnl = 0.0
    trade_entry_date = None
    trade_direction = 0
    previous = None
    events: list[dict] = []
    curve: list[dict] = []
    trades: list[dict] = []

    def add_cost(sides: int, layer_count: int) -> float:
        nonlocal cumulative_pnl, total_cost
        cumulative_pnl, amount = _charge(
            cumulative_pnl, sides, layer_count, active_notional_per_layer
        )
        total_cost += amount
        return amount

    def close_trade(date, price: float, contract: str, reason: str) -> None:
        nonlocal position, layers, pending_exit_reason, pending_pyramid, pyramided, stop_count
        nonlocal trail_active, trail_price, trade_exit_mode
        exit_layers = len(layers)
        add_cost(1, exit_layers)
        net_pnl = cumulative_pnl - trade_start_pnl
        trades.append({
            "entry_date": trade_entry_date, "exit_date": date,
            "direction": trade_direction, "exit_contract": contract,
            "exit_price": price, "exit_reason": reason, "layers": exit_layers,
            "notional_per_layer_at_entry": active_notional_per_layer,
            "net_pnl": net_pnl,
            "net_return_on_initial_capital": net_pnl / initial_capital,
            "net_return_on_entry_equity": net_pnl / active_notional_per_layer,
        })
        events.append({
            "date": date, "event": "exit", "contract": contract,
            "direction": position, "layers": exit_layers, "price": price,
            "reason": reason, "notional_per_layer": active_notional_per_layer,
        })
        position = 0
        layers = []
        pending_exit_reason = None
        pending_pyramid = False
        pyramided = False
        stop_count = 0
        trail_active = False
        trail_price = np.nan
        trade_exit_mode = ""

    for row in data.itertuples(index=False):
        day_start_pnl = cumulative_pnl
        contract_changed = previous is not None and row.contract != previous.contract
        old_open = np.nan

        # 先对旧合约从昨收盘盯市到今开盘。
        if previous is not None:
            if contract_changed:
                key = (row.date, previous.contract)
                if key not in raw_lookup.index:
                    raise RollDataError(
                        f"{row.date:%Y-%m-%d} {previous.contract}->{row.contract}: missing old-contract open"
                    )
                old_open = float(raw_lookup.loc[key, "open"])
                for layer in layers:
                    cumulative_pnl += position * layer["quantity"] * (old_open - previous.raw_close)
                benchmark_pnl += benchmark_qty * (old_open - previous.raw_close)
            else:
                for layer in layers:
                    cumulative_pnl += position * layer["quantity"] * (row.raw_open - previous.raw_close)
                benchmark_pnl += benchmark_qty * (row.raw_open - previous.raw_close)

        # 基准始终是一层固定名义多头，使用同一换月时点和成本。
        if previous is None:
            benchmark_qty = benchmark_notional / row.raw_open
            benchmark_pnl -= benchmark_notional * COST
        elif contract_changed:
            benchmark_pnl -= 2 * benchmark_notional * COST
            benchmark_qty = benchmark_notional / row.raw_open

        if position and pending_exit_reason:
            execution_price = old_open if contract_changed else row.raw_open
            execution_contract = previous.contract if contract_changed else row.contract
            close_trade(row.date, execution_price, execution_contract, pending_exit_reason)
        elif position and contract_changed:
            gap = float(row.raw_open - old_open)
            before_entry = entry_reference
            before_high = high_water
            before_low = low_water
            floating_before = position * (old_open - before_entry) / entry_atr
            cost = add_cost(2, len(layers))
            roll_cost += cost
            roll_count += 1
            entry_reference += gap
            high_water += gap
            low_water += gap
            if trail_active and pd.notna(trail_price):
                trail_price += gap
            for layer in layers:
                layer["state_entry_reference"] += gap
                layer["physical_entry"] = row.raw_open
                layer["quantity"] = active_notional_per_layer / row.raw_open
                layer["rolls"] += 1
            floating_after = position * (row.raw_open - entry_reference) / entry_atr
            events.append({
                "date": row.date, "event": "roll",
                "contract": f"{previous.contract}->{row.contract}",
                "direction": position, "layers": len(layers),
                "old_open": old_open, "new_open": row.raw_open, "price_gap": gap,
                "entry_reference_before": before_entry,
                "entry_reference_after": entry_reference,
                "high_water_before": before_high, "high_water_after": high_water,
                "low_water_before": before_low, "low_water_after": low_water,
                "entry_atr_before": entry_atr, "entry_atr_after": entry_atr,
                "floating_profit_atr_before": floating_before,
                "floating_profit_atr_after": floating_after,
                "stop_count_before": stop_count, "stop_count_after": stop_count,
                "pending_pyramid_inherited": pending_pyramid,
                "roll_cost": cost, "notional_per_layer": active_notional_per_layer,
                "reason": "T-1 volume leader changed; state shifted by open-price gap",
            })

        if position and pending_pyramid:
            add_cost(1, 1)
            layers.append({
                "name": "pyramid", "physical_entry": row.raw_open,
                "state_entry_reference": row.raw_open,
                "quantity": active_notional_per_layer / row.raw_open,
                "notional": active_notional_per_layer, "rolls": 0,
            })
            pending_pyramid = False
            pyramided = True
            events.append({
                "date": row.date, "event": "pyramid", "contract": row.contract,
                "direction": position, "layers": len(layers), "price": row.raw_open,
                "notional_per_layer": active_notional_per_layer,
                "reason": "prior close initial-layer profit >= 1 entry ATR",
            })

        # 新主力在成为T日主力前已出现的信号，连续主力序列看不到；
        # 只读取T-1及以前，且仅在连续序列本身没有待执行信号时补发。
        if contract_changed and not position and not pending_entry:
            carry_direction, carry_atr = _roll_carry_pending(
                contract_signals, str(row.contract), row.date, roll_lookback
            )
            if carry_direction and carry_direction != blocked_direction:
                pending_entry = carry_direction
                pending_entry_atr = carry_atr
                pending_entry_reason = "roll-lookback carry"

        if not position and pending_entry:
            if pending_entry != blocked_direction and pd.notna(pending_entry_atr):
                trade_start_pnl = cumulative_pnl
                active_notional_per_layer = (
                    initial_capital + cumulative_pnl
                    if compound_equity else float(fixed_notional_per_layer)
                )
                if active_notional_per_layer <= 0:
                    raise RuntimeError("strategy equity is non-positive; cannot open a new trade")
                position = pending_entry
                trade_direction = position
                trade_entry_date = row.date
                entry_reference = row.raw_open
                entry_atr = float(pending_entry_atr)
                high_water = low_water = row.raw_open
                stop_count = 0
                pyramided = False
                trail_active = False
                trail_price = np.nan
                if exit_mode == "regime":
                    trade_exit_mode = (
                        "combo" if pd.notna(row.adx) and row.adx >= adx_threshold else "baseline"
                    )
                else:
                    trade_exit_mode = exit_mode
                layers = [{
                    "name": "initial", "physical_entry": row.raw_open,
                    "state_entry_reference": row.raw_open,
                    "quantity": active_notional_per_layer / row.raw_open,
                    "notional": active_notional_per_layer, "rolls": 0,
                }]
                add_cost(1, 1)
                events.append({
                    "date": row.date, "event": "entry", "contract": row.contract,
                    "direction": position, "layers": 1, "price": row.raw_open,
                    "entry_atr": entry_atr,
                    "notional_per_layer": active_notional_per_layer,
                    "entry_equity": initial_capital + trade_start_pnl,
                    "reason": pending_entry_reason or "prior close MA20 cross",
                })
            pending_entry = 0
            pending_entry_reason = ""

        # 新主力合约从开盘盯市到收盘。
        for layer in layers:
            cumulative_pnl += position * layer["quantity"] * (row.raw_close - row.raw_open)
        benchmark_pnl += benchmark_qty * (row.raw_close - row.raw_open)

        exit_reason = None
        stop_active = False
        ma6_raw = row.ma6 - row.price_adjustment if pd.notna(row.ma6) else np.nan
        if position:
            high_water = max(high_water, row.raw_high)
            low_water = min(low_water, row.raw_low)
            profit_atr = position * (row.raw_close - entry_reference) / entry_atr
            effective_exit = trade_exit_mode if exit_mode == "regime" else exit_mode
            if effective_exit == "combo":
                divergence = (
                    (position == 1 and bool(row.bearish_divergence))
                    or (position == -1 and bool(row.bullish_divergence))
                )
                if profit_atr >= signal_model.ATR_TARGET:
                    exit_reason = "ATR target take profit"
                elif divergence:
                    exit_reason = "RSI divergence"
                elif profit_atr >= signal_model.TRAIL_TIER3_ATR:
                    stop_active = True
                    if position == 1:
                        trail_price = max(
                            trail_price if pd.notna(trail_price) else -np.inf,
                            high_water - signal_model.TRAIL_DIST_ATR * entry_atr,
                        )
                        if row.raw_close < trail_price:
                            exit_reason = "trailing stop"
                    else:
                        trail_price = min(
                            trail_price if pd.notna(trail_price) else np.inf,
                            low_water + signal_model.TRAIL_DIST_ATR * entry_atr,
                        )
                        if row.raw_close > trail_price:
                            exit_reason = "trailing stop"
                    trail_active = True
                elif profit_atr >= signal_model.TRAIL_TIER2_ATR:
                    stop_active = True
                    stop_count = stop_count + 1 if (
                        row.raw_close < ma6_raw if position == 1 else row.raw_close > ma6_raw
                    ) else 0
                    if stop_count >= 1:
                        exit_reason = "MA6 single-confirm stop"
                elif profit_atr >= signal_model.TRAIL_TIER1_ATR:
                    stop_active = True
                    stop_count = stop_count + 1 if (
                        row.raw_close < ma6_raw if position == 1 else row.raw_close > ma6_raw
                    ) else 0
                    required = 2 if position == 1 else 1
                    if stop_count >= required:
                        exit_reason = "MA6 double-confirm stop"
            elif effective_exit != "spread_only":
                divergence = (
                    (position == 1 and bool(row.bearish_divergence))
                    or (position == -1 and bool(row.bullish_divergence))
                )
                if divergence:
                    exit_reason = "RSI divergence"
                elif position == 1:
                    stop_active = (high_water - entry_reference) / entry_atr >= 0.75
                    stop_count = stop_count + 1 if stop_active and row.raw_close < ma6_raw else 0
                    if stop_count >= 2:
                        exit_reason = "asymmetric MA6 stop"
                else:
                    stop_active = True
                    stop_count = stop_count + 1 if row.raw_close > ma6_raw else 0
                    if stop_count >= 1:
                        exit_reason = "asymmetric MA6 stop"
            spread_peak = bool(getattr(row, "ma5_ma20_spread_peak_5", False))
            if effective_exit in {"spread_overlay", "spread_only"} and not exit_reason and spread_peak:
                exit_reason = "MA5-MA20 spread 5-day peak"
            if exit_reason:
                pending_exit_reason = exit_reason
                if "stop" in exit_reason:
                    blocked_direction = position
            if not pyramided and not pending_pyramid:
                if profit_atr >= signal_model.DEFAULT_PYRAMID_ATR:
                    pending_pyramid = True
        else:
            baseline_direction = (
                1 if bool(row.long_signal) else (-1 if bool(row.short_signal) else 0)
            )
            ma_direction = (
                1 if bool(getattr(row, "ma5_long_cross", False))
                else (-1 if bool(getattr(row, "ma5_short_cross", False)) else 0)
            )
            if entry_mode == "baseline":
                direction = baseline_direction
                entry_reason = "prior close MA20 cross"
            elif entry_mode == "ma_filter":
                aligned = (
                    (baseline_direction == 1 and row.ma5 > row.ma20)
                    or (baseline_direction == -1 and row.ma5 < row.ma20)
                )
                direction = baseline_direction if aligned else 0
                entry_reason = "prior close MA20 cross with MA5 alignment"
            elif entry_mode == "ma_cross":
                direction = ma_direction
                entry_reason = "prior close MA5-MA20 cross"
            else:
                direction = baseline_direction or ma_direction
                entry_reason = (
                    "prior close MA20 cross" if baseline_direction
                    else "prior close MA5-MA20 cross"
                )
            if blocked_direction and direction == -blocked_direction:
                blocked_direction = 0
            if direction and direction != blocked_direction:
                pending_entry = direction
                pending_entry_atr = row.atr
                pending_entry_reason = entry_reason

        equity = initial_capital + cumulative_pnl
        benchmark_equity = initial_capital + benchmark_pnl
        day_start_equity = initial_capital + day_start_pnl
        curve.append({
            "date": row.date, "contract": row.contract,
            "strategy_equity": equity, "benchmark_equity": benchmark_equity,
            "strategy_return_on_initial_capital": (cumulative_pnl - day_start_pnl) / initial_capital,
            "strategy_daily_return": equity / day_start_equity - 1 if day_start_equity > 0 else np.nan,
            "position": position, "layers": len(layers),
            "notional_per_layer": active_notional_per_layer if position else 0.0,
            "gross_notional": sum(layer["notional"] for layer in layers),
            "entry_reference": entry_reference if position else np.nan,
            "entry_atr": entry_atr if position else np.nan,
            "floating_profit_atr": (
                position * (row.raw_close - entry_reference) / entry_atr if position else np.nan
            ),
            "stop_active": stop_active, "stop_count": stop_count,
            "trail_active": trail_active if position else False,
            "pending_pyramid": pending_pyramid, "rolled": contract_changed,
        })
        previous = row

    if position:
        last = data.iloc[-1]
        terminal_layers = len(layers)
        close_trade(last.date, float(last.raw_close), str(last.contract), "period_end")
        curve[-1]["strategy_equity"] = initial_capital + cumulative_pnl
        previous_equity = initial_capital if len(curve) == 1 else curve[-2]["strategy_equity"]
        curve[-1]["strategy_return_on_initial_capital"] -= (
            terminal_layers * active_notional_per_layer * COST / initial_capital
        )
        curve[-1]["strategy_daily_return"] = (
            curve[-1]["strategy_equity"] / previous_equity - 1
            if previous_equity > 0 else np.nan
        )
    # 回测期末同样平掉基准仓位。
    benchmark_pnl -= benchmark_notional * COST
    curve[-1]["benchmark_equity"] = initial_capital + benchmark_pnl

    curve_df = pd.DataFrame(curve)
    trade_df = pd.DataFrame(trades)
    total_return = curve_df.strategy_equity.iloc[-1] / initial_capital - 1
    days = max((data.date.iloc[-1] - data.date.iloc[0]).days, 1)
    annual = (
        (1 + total_return) ** (365.25 / days) - 1 if total_return > -1 else -1.0
    )
    drawdown = (
        curve_df.strategy_equity / curve_df.strategy_equity.cummax() - 1
    ).min()
    daily = curve_df.strategy_daily_return
    sharpe = daily.mean() / daily.std(ddof=1) * math.sqrt(252) if daily.std(ddof=1) > 0 else np.nan
    benchmark_total_return = curve_df.benchmark_equity.iloc[-1] / initial_capital - 1
    wins = trade_df.loc[trade_df.net_pnl.gt(0), "net_pnl"] if len(trade_df) else pd.Series(dtype=float)
    losses = trade_df.loc[trade_df.net_pnl.lt(0), "net_pnl"] if len(trade_df) else pd.Series(dtype=float)
    profit_loss_ratio = (
        float((wins / trade_df.loc[wins.index, "notional_per_layer_at_entry"]).mean()
              / abs((losses / trade_df.loc[losses.index, "notional_per_layer_at_entry"]).mean()))
        if len(wins) and len(losses) else np.nan
    )
    metrics = {
        "model_name": (
            MODEL_NAME if entry_mode == "baseline" and compound_equity
            else FUSION_MODEL_NAME
        ),
        "model_version": (
            MODEL_VERSION if entry_mode == "baseline" and compound_equity
            else (FIXED_NOTIONAL_MODEL_VERSION if entry_mode == "baseline" else FUSION_MODEL_VERSION)
        ),
        "entry_mode": entry_mode, "exit_mode": exit_mode,
        "roll_lookback": roll_lookback,
        "start": data.date.iloc[0], "end": data.date.iloc[-1], "bars": len(data),
        "initial_capital": initial_capital,
        "fixed_notional_per_layer": fixed_notional_per_layer,
        "capital_policy": capital_policy,
        "total_return": total_return,
        "annual_return_cagr": annual,
        # 兼容既有批量/小时线调用者；复利模式下请优先读取 annual_return_cagr。
        "annual_return_cagr_on_fixed_capital": annual,
        "annual_return_simple": total_return * 365.25 / days,
        "benchmark_total_return": benchmark_total_return,
        "benchmark_annual_return_simple": benchmark_total_return * 365.25 / days,
        "max_drawdown": float(drawdown), "sharpe_rf0": sharpe,
        "completed_trades": len(trade_df),
        "win_rate": float(trade_df.net_pnl.gt(0).mean()) if len(trade_df) else 0.0,
        "profit_loss_ratio": profit_loss_ratio,
        "roll_count_while_held": roll_count, "roll_cost": roll_cost,
        "total_transaction_cost": total_cost,
        "max_gross_notional": float(curve_df.gross_notional.max()),
        "max_gross_fixed_notional": float(curve_df.gross_notional.max()),
    }
    return metrics, curve_df, pd.DataFrame(events), trade_df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variety", default="P", help="品种字母，例如 P/Y/M/RB")
    parser.add_argument("--name", default="棕榈油")
    parser.add_argument("--years", type=int, default=1)
    parser.add_argument("--end", default="2026-08-07")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--initial-capital", type=float, default=INITIAL_CAPITAL)
    parser.add_argument(
        "--fixed-notional", type=float, default=None,
        help="仅用于复现旧版固定名义口径；默认按每笔入场权益复利",
    )
    parser.add_argument("--exit-mode", choices=sorted(EXIT_MODES), default="baseline")
    parser.add_argument("--adx-threshold", type=float, default=25.0)
    parser.add_argument("--roll-lookback", type=int, default=5, choices=range(0, 21))
    parser.add_argument("--cache-dir", default="futures_real_contract_cache")
    parser.add_argument("--output-dir", default="futures_main_contract_bollinger_rsi_output")
    args = parser.parse_args()

    end = pd.Timestamp(args.end)
    start = end - pd.DateOffset(years=args.years)
    warmup_start = start - pd.DateOffset(years=1)
    cache = Path(args.cache_dir) / args.variety.upper()
    raw, errors = data_source.fetch_variety(
        args.variety.upper(), warmup_start.year, end.year, cache, args.workers
    )
    raw = raw[raw.date.between(warmup_start, end)].copy()
    active = build_lagged_main_schedule(raw)
    prepared_all = prepare_contract_local_main(active, raw)
    prepared = prepared_all[prepared_all.date.between(start, end)].reset_index(drop=True)
    prepared.attrs["roll_lookback"] = args.roll_lookback
    metrics, curve, events, trades = run_backtest(
        prepared, raw,
        initial_capital=args.initial_capital,
        fixed_notional_per_layer=args.fixed_notional,
        exit_mode=args.exit_mode,
        adx_threshold=args.adx_threshold,
    )

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{**{"variety": args.variety.upper(), "name": args.name}, **metrics}]).to_csv(
        output / "summary.csv", index=False, encoding="utf-8-sig"
    )
    prepared.to_csv(output / "main_contract_bars.csv", index=False, encoding="utf-8-sig")
    curve.to_csv(output / "equity_curve.csv", index=False, encoding="utf-8-sig")
    events.to_csv(output / "events.csv", index=False, encoding="utf-8-sig")
    trades.to_csv(output / "trades.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(errors).to_csv(output / "fetch_errors.csv", index=False, encoding="utf-8-sig")
    methodology = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION if args.fixed_notional is None else FIXED_NOTIONAL_MODEL_VERSION,
        "exit_strategy": args.exit_mode,
        "roll_lookback": args.roll_lookback,
        "main_contract": "day T uses the highest-volume delivery contract observed on T-1",
        "signal_timing": "completed close confirmation; next trading-day open execution",
        "indicator_series": (
            "each actual PYYMM delivery contract's own unadjusted daily history; "
            "no cross-contract price stitching for signals"
        ),
        "capital": (
            "each layer uses account equity at initial entry; next trade compounds realized P&L"
            if args.fixed_notional is None
            else "legacy comparison: each layer uses a fixed nominal amount"
        ),
        "roll": "close old/open new at same-day opens; shift state by new_open-old_open",
        "inherited_on_roll": [
            "entry_atr", "floating_profit_atr", "high_water", "low_water",
            "stop_count", "pending_pyramid", "pyramided", "blocked_direction",
            "trail_active", "trail_price",
        ],
        "cost": {"single_side_rate": COST, "roll_sides_per_layer": 2},
    }
    (output / "methodology.json").write_text(
        json.dumps(methodology, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(pd.DataFrame([metrics]).to_string(index=False), flush=True)
    print(f"output: {output.resolve()}", flush=True)


if __name__ == "__main__":
    main()

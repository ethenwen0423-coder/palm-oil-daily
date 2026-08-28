#!/usr/bin/env python3
"""Backtest the fixed Bollinger/RSI/MA6 model on actual monthly contracts.

The continuous-main symbols are used only to freeze the liquidity-ranked universe.
All backtest prices and indicators come from individual delivery-month contracts.
The contract traded on day T is the contract with the largest volume on T-1.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

import palm_oil_bollinger_rsi_ma6_strategy as model


COST = model.COST
MODEL_VERSION = model.LATEST_MODEL_VERSION
TOP20 = [
    ("FG", "玻璃"), ("MA", "甲醇"), ("M", "豆粕"), ("TA", "PTA"),
    ("SA", "纯碱"), ("V", "PVC"), ("RB", "螺纹钢"), ("FU", "燃料油"),
    ("PP", "PP"), ("AG", "白银"), ("JD", "鸡蛋"), ("RM", "菜粕"),
    ("EG", "乙二醇"), ("L", "塑料"), ("JM", "焦煤"), ("EB", "苯乙烯"),
    ("P", "棕榈油"), ("HC", "热卷"), ("BU", "沥青"), ("SH", "烧碱"),
]


def contract_symbols(variety: str, start_year: int, end_year: int) -> list[str]:
    return [f"{variety}{year % 100:02d}{month:02d}"
            for year in range(start_year - 1, end_year + 2)
            for month in range(1, 13)]


def fetch_one(symbol: str, cache_dir: Path, retries: int = 2) -> tuple[str, pd.DataFrame | None, str | None]:
    cache = cache_dir / f"{symbol}.csv"
    if cache.exists():
        try:
            data = pd.read_csv(cache)
            if not data.empty:
                data["date"] = pd.to_datetime(data["date"])
                return symbol, data, None
        except Exception:
            pass
    import akshare as ak
    error = None
    for attempt in range(retries + 1):
        try:
            data = ak.futures_zh_daily_sina(symbol=symbol)
            if data is None or data.empty:
                return symbol, None, "empty"
            data["date"] = pd.to_datetime(data["date"])
            for col in ["open", "high", "low", "close", "volume", "hold", "settle"]:
                data[col] = pd.to_numeric(data[col], errors="coerce")
            data = data.dropna(subset=["date", "open", "high", "low", "close", "volume"])
            data.to_csv(cache, index=False)
            return symbol, data, None
        except Exception as exc:
            if isinstance(exc, ValueError) and "Length mismatch" in str(exc):
                return symbol, None, "empty"
            error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.25 * (attempt + 1))
    return symbol, None, error


def fetch_variety(variety: str, start_year: int, end_year: int, cache_dir: Path,
                  workers: int) -> tuple[pd.DataFrame, list[dict]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    symbols = contract_symbols(variety, start_year, end_year)
    frames, errors = [], []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_one, s, cache_dir): s for s in symbols}
        for future in as_completed(futures):
            symbol, data, error = future.result()
            if data is not None:
                data = data.copy()
                data["contract"] = symbol
                data["variety"] = variety
                frames.append(data)
            elif error != "empty":
                errors.append({"variety": variety, "contract": symbol, "error": error})
    if not frames:
        raise RuntimeError(f"{variety}: no monthly contract data")
    raw = pd.concat(frames, ignore_index=True).sort_values(["date", "contract"])
    raw = raw.drop_duplicates(["date", "contract"], keep="last")
    return raw, errors


def add_contract_indicators(raw: pd.DataFrame) -> pd.DataFrame:
    pieces = []
    for contract, data in raw.groupby("contract", sort=False):
        x = data.rename(columns={"date": "datetime"}).sort_values("datetime").reset_index(drop=True)
        prepared = model.prepare(x, divergence_window=20).rename(columns={"datetime": "date"})
        pieces.append(prepared)
    return pd.concat(pieces, ignore_index=True).sort_values(["date", "contract"])


def build_active_schedule(prepared: pd.DataFrame, start: pd.Timestamp,
                          end: pd.Timestamp) -> pd.DataFrame:
    valid = prepared[(prepared.volume > 0) & prepared.date.le(end)].copy()
    daily_winner = valid.loc[valid.groupby("date").volume.idxmax(), ["date", "contract", "volume"]]
    daily_winner = daily_winner.sort_values("date")
    daily_winner["active_contract"] = daily_winner.contract.shift(1)
    daily_winner["selection_volume_t_minus_1"] = daily_winner.volume.shift(1)
    schedule = daily_winner[["date", "active_contract", "selection_volume_t_minus_1"]].dropna()
    schedule = schedule[schedule.date.between(start, end)].copy()
    active = prepared.merge(
        schedule, left_on=["date", "contract"], right_on=["date", "active_contract"], how="inner"
    ).sort_values("date").reset_index(drop=True)
    return active


def _safe_factor(equity: float, simple_return: float) -> float:
    return max(equity * max(1.0 + simple_return, 1e-9), 1e-12)


def run_backtest(active: pd.DataFrame, all_rows: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    lookup = all_rows.set_index(["date", "contract"])
    equity = benchmark = 1.0
    position = 0
    layers = 0
    entry = entry_atr = np.nan
    high_water = low_water = np.nan
    pending_exit = pending_entry = 0
    pending_entry_atr = np.nan
    pending_pyramid = False
    pyramided = False
    stop_count = 0
    blocked = 0
    prev_row = None
    roll_count = 0
    roll_cost = 0.0
    events, curve, trade_log = [], [], []
    trade_start_equity = 1.0
    trade_entry_date = None
    trade_direction = 0

    for row in active.itertuples(index=False):
        day_ret = 0.0
        bench_ret = 0.0
        contract_changed = prev_row is not None and row.contract != prev_row.contract
        old_open = np.nan
        if prev_row is not None:
            if contract_changed and (row.date, prev_row.contract) in lookup.index:
                old_open = float(lookup.loc[(row.date, prev_row.contract), "open"])
                overnight = old_open / prev_row.close - 1
            elif not contract_changed:
                overnight = row.open / prev_row.close - 1
            else:
                overnight = 0.0
            day_ret += position * layers * overnight
            bench_ret += overnight

        # Benchmark is always 1x long and rolls at the open.
        if prev_row is None:
            bench_ret -= COST
        elif contract_changed:
            bench_ret -= 2 * COST

        if position and pending_exit:
            day_ret -= layers * COST
            events.append({"date": row.date, "event": "exit", "contract": prev_row.contract if prev_row is not None else row.contract,
                           "direction": position, "layers": layers, "reason": "signal_at_prior_close"})
            trade_log.append({"entry_date": trade_entry_date, "exit_date": row.date,
                              "direction": trade_direction, "exit_reason": "signal_at_prior_close",
                              "net_return": equity * (1 + day_ret) / trade_start_equity - 1})
            position = layers = 0
            pending_exit = 0
            pending_pyramid = False
            pyramided = False
            stop_count = 0
        elif position and contract_changed:
            day_ret -= layers * 2 * COST
            roll_count += 1
            roll_cost += layers * 2 * COST
            events.append({"date": row.date, "event": "roll", "contract": f"{prev_row.contract}->{row.contract}",
                           "direction": position, "layers": layers, "reason": "T-1 volume leader changed"})
            entry = row.open
            prior_new_atr = (
                float(lookup.loc[(prev_row.date, row.contract), "atr"])
                if (prev_row.date, row.contract) in lookup.index else np.nan
            )
            entry_atr = prior_new_atr
            high_water = low_water = row.open
            stop_count = 0

        if position and pending_pyramid:
            layers = 2
            pyramided = True
            pending_pyramid = False
            day_ret -= COST
            events.append({"date": row.date, "event": "pyramid", "contract": row.contract,
                           "direction": position, "layers": layers, "reason": "prior close profit >= 1 ATR"})

        if not position and pending_entry:
            if pending_entry != blocked and pd.notna(pending_entry_atr):
                position = pending_entry
                layers = 1
                entry = row.open
                entry_atr = pending_entry_atr
                high_water = low_water = row.open
                stop_count = 0
                pyramided = False
                day_ret -= COST
                trade_start_equity = equity
                trade_entry_date = row.date
                trade_direction = position
                events.append({"date": row.date, "event": "entry", "contract": row.contract,
                               "direction": position, "layers": layers, "reason": "prior close MA20 cross"})
            pending_entry = 0

        # Current active contract open-to-close P&L.
        day_ret += position * layers * (row.close / row.open - 1)
        bench_ret += row.close / row.open - 1
        equity = _safe_factor(equity, day_ret)
        benchmark = _safe_factor(benchmark, bench_ret)

        # Signals are based only on this completed bar and contract-local indicators.
        exit_reason = None
        if position:
            high_water = max(high_water, row.high)
            low_water = min(low_water, row.low)
            divergence = (position == 1 and row.bearish_divergence) or (position == -1 and row.bullish_divergence)
            if divergence:
                exit_reason = "RSI divergence"
            else:
                if position == 1:
                    active_stop = pd.notna(entry_atr) and entry_atr > 0 and (high_water - entry) / entry_atr >= 0.75
                    stop_count = stop_count + 1 if active_stop and row.close < row.ma6 else 0
                    if stop_count >= 2:
                        exit_reason = "asymmetric MA6 stop"
                else:
                    stop_count = stop_count + 1 if row.close > row.ma6 else 0
                    if stop_count >= 1:
                        exit_reason = "asymmetric MA6 stop"
            if exit_reason:
                pending_exit = 1
                if "stop" in exit_reason:
                    blocked = position
            if not pyramided and not pending_pyramid and pd.notna(entry_atr) and entry_atr > 0:
                if position * (row.close - entry) / entry_atr >= 1.0:
                    pending_pyramid = True
        else:
            direction = 1 if bool(row.long_signal) else (-1 if bool(row.short_signal) else 0)
            if blocked and direction == -blocked:
                blocked = 0
            if direction and direction != blocked:
                pending_entry = direction
                pending_entry_atr = row.atr

        curve.append({"date": row.date, "contract": row.contract, "strategy_equity": equity,
                      "benchmark_equity": benchmark, "strategy_return": day_ret,
                      "benchmark_return": bench_ret, "position": position,
                      "gross_exposure": abs(position * layers), "rolled": contract_changed})
        prev_row = row

    if position:
        equity = _safe_factor(equity, -layers * COST)
        trade_log.append({"entry_date": trade_entry_date, "exit_date": active.date.iloc[-1],
                          "direction": trade_direction, "exit_reason": "period_end",
                          "net_return": equity / trade_start_equity - 1})
        curve[-1]["strategy_equity"] = equity
        curve[-1]["strategy_return"] -= layers * COST

    curve_df = pd.DataFrame(curve)
    returns = curve_df[["strategy_return", "benchmark_return"]].dropna()
    variance = returns.benchmark_return.var(ddof=1)
    beta = returns.strategy_return.cov(returns.benchmark_return) / variance if variance > 0 else np.nan
    daily_alpha = returns.strategy_return.mean() - beta * returns.benchmark_return.mean()
    alpha = (1 + daily_alpha) ** 252 - 1 if pd.notna(daily_alpha) and daily_alpha > -1 else np.nan
    days = max((active.date.iloc[-1] - active.date.iloc[0]).days, 1)
    annual = equity ** (365.25 / days) - 1
    bench_annual = benchmark ** (365.25 / days) - 1
    dd = (curve_df.strategy_equity / curve_df.strategy_equity.cummax() - 1).min()
    std = returns.strategy_return.std(ddof=1)
    sharpe = returns.strategy_return.mean() / std * math.sqrt(252) if std > 0 else np.nan
    metrics = {
        "start": active.date.iloc[0], "end": active.date.iloc[-1], "bars": len(active),
        "total_return": equity - 1, "annual_return": annual, "benchmark_annual": bench_annual,
        "alpha_annual": alpha, "beta": beta, "max_drawdown": dd, "sharpe_rf0": sharpe,
        "completed_trades": len(trade_log), "win_rate": float((pd.DataFrame(trade_log).net_return > 0).mean()) if trade_log else 0.0,
        "roll_count_while_held": roll_count, "roll_cost_return_units": roll_cost,
        "max_gross_exposure": float(curve_df.gross_exposure.max()),
    }
    return metrics, curve_df, pd.DataFrame(events), pd.DataFrame(trade_log)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--end", default="2026-08-07")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output-dir", default="futures_real_contract_top20_output")
    parser.add_argument("--cache-dir", default="futures_real_contract_cache")
    args = parser.parse_args()
    end = pd.Timestamp(args.end)
    start_5y = end - pd.DateOffset(years=5)
    raw_start = start_5y - pd.DateOffset(years=1)
    output = Path(args.output_dir)
    cache_root = Path(args.cache_dir)
    output.mkdir(parents=True, exist_ok=True)
    summaries, schedules, errors = [], [], []
    for rank, (variety, name) in enumerate(TOP20, 1):
        print(f"[{rank:02d}/20] {variety} {name}: fetching monthly contracts", flush=True)
        try:
            raw, fetch_errors = fetch_variety(variety, raw_start.year, end.year, cache_root / variety, args.workers)
            errors.extend(fetch_errors)
            raw = raw[raw.date.between(raw_start, end)].copy()
            prepared = add_contract_indicators(raw)
            for years in [1, 3, 5]:
                start = end - pd.DateOffset(years=years)
                active = build_active_schedule(prepared, start, end)
                if len(active) < 100:
                    raise ValueError(f"{years}y only {len(active)} active bars")
                metric, curve, events, trades = run_backtest(active, prepared)
                coverage_years = (metric["end"] - metric["start"]).days / 365.25
                summaries.append({"volume_rank": rank, "variety": variety, "name": name,
                                  "window_years": years, "coverage_years": coverage_years,
                                  "coverage_status": "complete" if coverage_years >= years - 0.05 else "insufficient_history",
                                  **metric})
                prefix = f"{rank:02d}_{variety}_{years}y"
                curve.to_csv(output / f"{prefix}_equity.csv", index=False, encoding="utf-8-sig")
                events.to_csv(output / f"{prefix}_events.csv", index=False, encoding="utf-8-sig")
                trades.to_csv(output / f"{prefix}_trades.csv", index=False, encoding="utf-8-sig")
                schedule = active[["date", "contract", "selection_volume_t_minus_1"]].copy()
                schedule.insert(0, "window_years", years)
                schedule.insert(0, "variety", variety)
                schedules.append(schedule)
        except Exception as exc:
            errors.append({"variety": variety, "contract": "*", "error": f"backtest: {type(exc).__name__}: {exc}"})
            print(f"  ERROR {exc}", flush=True)
    summary = pd.DataFrame(summaries)
    summary.to_csv(output / "summary_1_3_5y.csv", index=False, encoding="utf-8-sig")
    if schedules:
        pd.concat(schedules, ignore_index=True).to_csv(output / "active_contract_schedule.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(errors, columns=["variety", "contract", "error"]).to_csv(
        output / "fetch_errors.csv", index=False, encoding="utf-8-sig"
    )
    methodology = {
        "model_version": MODEL_VERSION, "single_side_cost": COST,
        "universe": "Top20 by 20-day median volume frozen at 2026-08-07; continuous symbols used for ranking only",
        "market_data": "Sina daily bars for individual delivery-month contracts via AkShare futures_zh_daily_sina",
        "main_contract": "day T trades the highest-volume contract observed on T-1",
        "roll": "at day-T open, close old and open new; charge 2 single-side costs per layer",
        "signals": "contract-local MA20/RSI14/ATR14/MA6; close confirmation and next-open execution",
        "alpha_beta_benchmark": "same-variety 1x long daily main contract, using identical lagged selection and roll costs",
        "alpha": "OLS daily intercept annualized as (1+alpha_daily)^252-1",
        "beta": "cov(strategy daily return, benchmark daily return)/var(benchmark daily return)",
        "sharpe": "sqrt(252)*mean(daily return)/std(daily return), risk-free rate 0",
    }
    (output / "methodology.json").write_text(json.dumps(methodology, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary.to_string(index=False), flush=True)
    print(f"output: {output.resolve()}", flush=True)


if __name__ == "__main__":
    main()

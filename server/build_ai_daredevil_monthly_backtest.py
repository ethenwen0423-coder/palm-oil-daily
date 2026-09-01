#!/usr/bin/env python3
"""Build the AI Daredevil five-year monthly return table.

The backtest uses actual PYYMM delivery-contract bars.  For each product, the
contract traded on T is selected from T-1 volume, signals are confirmed at the
close, and executions occur at the next open.  The public portfolio benchmark
is a static equal-weight basket of the current 40 product sleeves; it is not a
historical replay of the live fund's dynamic position allocator.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

import run_ai_daredevil as runtime


SHANGHAI = ZoneInfo("Asia/Shanghai")
SCHEMA_VERSION = 1
MONTH_COUNT = 60
WARMUP_MONTHS = 14
SINGLE_SIDE_COST = 0.0004


def previous_completed_month(value: date) -> pd.Period:
    return pd.Period(value, freq="M") - 1


def month_window(as_of: date) -> tuple[pd.Period, pd.Period, pd.Timestamp, pd.Timestamp]:
    end_period = previous_completed_month(as_of)
    start_period = end_period - (MONTH_COUNT - 1)
    start = start_period.start_time.normalize()
    end = end_period.end_time.normalize()
    return start_period, end_period, start, end


def contract_symbols(variety: str, start_year: int, end_year: int) -> list[str]:
    return [
        f"{variety}{year % 100:02d}{month:02d}"
        for year in range(start_year - 1, end_year + 2)
        for month in range(1, 13)
    ]


def normalize_bars(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    if "datetime" in data.columns and "date" not in data.columns:
        data = data.rename(columns={"datetime": "date"})
    required = ("date", "open", "high", "low", "close", "volume")
    if not set(required).issubset(data.columns):
        raise ValueError("daily bars are missing required columns")
    data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.tz_localize(None)
    for column in ("open", "high", "low", "close", "volume", "hold", "settle"):
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return (
        data.dropna(subset=list(required))
        .sort_values("date")
        .drop_duplicates("date", keep="last")
        .reset_index(drop=True)
    )


def _contract_period(symbol: str) -> pd.Period:
    suffix = symbol[-4:]
    year = 2000 + int(suffix[:2])
    return pd.Period(f"{year:04d}-{int(suffix[2:]):02d}", freq="M")


def fetch_contract(
    symbol: str,
    cache_dir: Path,
    end_period: pd.Period,
) -> tuple[str, pd.DataFrame | None, str | None]:
    cache = cache_dir / f"{symbol}.csv"
    empty_marker = cache_dir / f"{symbol}.empty"
    if cache.is_file():
        try:
            bars = normalize_bars(pd.read_csv(cache))
            if not bars.empty:
                return symbol, bars, None
        except (OSError, ValueError, pd.errors.ParserError):
            pass
    if empty_marker.is_file() and _contract_period(symbol) <= end_period:
        return symbol, None, "empty"
    try:
        bars = normalize_bars(runtime.fetch_daily(symbol))
        if bars.empty:
            raise runtime.RuntimeErrorSafe(f"{symbol}: empty daily bars")
        cache_dir.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=cache_dir,
                prefix=f".{symbol}.", suffix=".tmp", delete=False,
            ) as stream:
                temporary = Path(stream.name)
                bars.to_csv(stream, index=False)
            os.replace(temporary, cache)
            temporary = None
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
        empty_marker.unlink(missing_ok=True)
        return symbol, bars, None
    except Exception as exc:  # bounded network failures are retained in audit output
        detail = str(exc)
        if "empty daily bars" in detail or "invalid daily response" in detail:
            if _contract_period(symbol) <= end_period:
                cache_dir.mkdir(parents=True, exist_ok=True)
                empty_marker.write_text(end_period.strftime("%Y-%m"), encoding="utf-8")
            return symbol, None, "empty"
        return symbol, None, f"{type(exc).__name__}: {detail}"


def fetch_universe(
    varieties: list[str],
    cache_dir: Path,
    start_year: int,
    end_year: int,
    end_period: pd.Period,
    workers: int,
) -> tuple[dict[str, pd.DataFrame], list[dict[str, str]]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    requested = {
        symbol: variety
        for variety in varieties
        for symbol in contract_symbols(variety, start_year, end_year)
    }
    frames: dict[str, list[pd.DataFrame]] = {variety: [] for variety in varieties}
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(fetch_contract, symbol, cache_dir, end_period): (symbol, variety)
            for symbol, variety in requested.items()
        }
        for future in as_completed(futures):
            symbol, variety = futures[future]
            try:
                _, data, error = future.result()
            except Exception as exc:  # defensive: keep a failed worker auditable
                data, error = None, f"{type(exc).__name__}: {exc}"
            if data is not None and not data.empty:
                item = data.copy()
                item["contract"] = symbol
                item["variety"] = variety
                frames[variety].append(item)
            elif error and error != "empty":
                errors.append({"variety": variety, "contract": symbol, "error": error})
    output: dict[str, pd.DataFrame] = {}
    for variety, pieces in frames.items():
        if not pieces:
            continue
        output[variety] = (
            pd.concat(pieces, ignore_index=True)
            .sort_values(["date", "contract"])
            .drop_duplicates(["date", "contract"], keep="last")
            .reset_index(drop=True)
        )
    return output, sorted(errors, key=lambda item: (item["variety"], item["contract"]))


def _remove_untradeable_active_dates(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Remove sessions where the T-1 leader has no executable day-T bar.

    This is an explicit no-execution rule for suspended/missing active-contract
    sessions, not a synthetic zero-price fill.  The removed dates are exposed
    in the public audit payload.
    """
    source = raw.copy()
    removed: list[str] = []
    for _attempt in range(10):
        valid = source.loc[source.volume.gt(0)].copy()
        winners = valid.loc[
            valid.groupby("date")["volume"].idxmax(), ["date", "contract"]
        ].sort_values("date")
        winners["active_contract"] = winners.contract.shift(1)
        schedule = winners.dropna(subset=["active_contract"])
        available = pd.MultiIndex.from_frame(source[["date", "contract"]])
        expected = pd.MultiIndex.from_frame(
            schedule[["date", "active_contract"]].rename(columns={"active_contract": "contract"})
        )
        missing_mask = ~expected.isin(available)
        missing_dates = pd.DatetimeIndex(schedule.loc[missing_mask, "date"].unique())
        if missing_dates.empty:
            return source, sorted(set(removed))
        removed.extend(day.strftime("%Y-%m-%d") for day in missing_dates)
        source = source.loc[~source.date.isin(missing_dates)].copy()
    raise ValueError("untradeable active-contract sessions did not converge")


def run_sleeve(
    model: Any, raw: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp
) -> tuple[pd.Series, list[str]]:
    warmup_start = start - pd.DateOffset(months=WARMUP_MONTHS)
    source = raw.loc[raw.date.between(warmup_start, end)].copy()
    source, removed_dates = _remove_untradeable_active_dates(source)
    active = model.build_lagged_main_schedule(source)
    prepared_all = model.prepare_contract_local_main(active, source)
    prepared = prepared_all.loc[prepared_all.date.between(start, end)].copy()
    prepared.attrs.update(prepared_all.attrs)
    if prepared.empty:
        raise ValueError("no active main-contract rows in requested window")
    _metrics, curve, _events, _trades = model.run_backtest(
        prepared, source, initial_capital=1.0
    )
    series = curve.set_index(pd.to_datetime(curve["date"]))["strategy_equity"].astype(float)
    return series[~series.index.duplicated(keep="last")].sort_index(), removed_dates


def build_monthly_table(
    sleeves: dict[str, pd.Series],
    varieties: list[str],
    start_period: pd.Period,
    end_period: pd.Period,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], pd.Series]:
    periods = pd.period_range(start_period, end_period, freq="M")
    trading_dates = sorted({
        pd.Timestamp(day).normalize()
        for series in sleeves.values()
        for day in series.index
        if start_period.start_time <= pd.Timestamp(day) <= end_period.end_time
    })
    if not trading_dates:
        raise ValueError("no portfolio trading dates in requested window")
    index = pd.DatetimeIndex(trading_dates)
    aligned: list[pd.Series] = []
    for variety in varieties:
        series = sleeves.get(variety)
        if series is None or series.empty:
            aligned.append(pd.Series(1.0, index=index, name=variety))
            continue
        normalized = series.copy()
        normalized.index = pd.to_datetime(normalized.index).tz_localize(None).normalize()
        normalized = normalized[~normalized.index.duplicated(keep="last")].sort_index()
        aligned.append(normalized.reindex(index).ffill().fillna(1.0).rename(variety))
    portfolio = pd.concat(aligned, axis=1).mean(axis=1)

    month_ends: dict[pd.Period, float] = {}
    for period in periods:
        sample = portfolio.loc[portfolio.index.to_period("M") == period]
        if not sample.empty:
            month_ends[period] = float(sample.iloc[-1])
    monthly: list[dict[str, Any]] = []
    previous = 1.0
    for period in periods:
        equity = month_ends.get(period)
        if equity is None:
            value = None
        else:
            value = equity / previous - 1.0
            previous = equity
        monthly.append({
            "month": str(period),
            "return": round(value, 10) if value is not None else None,
            "equity": round(equity, 10) if equity is not None else None,
        })

    years: list[dict[str, Any]] = []
    for year in range(start_period.year, end_period.year + 1):
        row = [item for item in monthly if int(item["month"][:4]) == year]
        values = [item["return"] for item in row if item["return"] is not None]
        factor = math.prod(1.0 + value for value in values) if values else None
        months = {str(month): None for month in range(1, 13)}
        months.update({str(int(item["month"][5:])): item["return"] for item in row})
        years.append({
            "year": year,
            "months": months,
            "period_return": round(factor - 1.0, 10) if factor is not None else None,
            "available_months": len(values),
            "complete_year": len(values) == 12,
        })
    return monthly, years, portfolio


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    generated_at = datetime.now(SHANGHAI)
    as_of = date.fromisoformat(args.as_of) if args.as_of else generated_at.date()
    start_period, end_period, start, end = month_window(as_of)
    warmup_start = start - pd.DateOffset(months=WARMUP_MONTHS)
    site_root = Path(args.site_root).resolve()
    _ledger, model, _signal_model = runtime.load_components(site_root)
    if model.MODEL_VERSION != runtime.MODEL_VERSION:
        raise RuntimeError(f"unexpected model version: {model.MODEL_VERSION}")
    varieties = list(runtime.PRODUCTS)
    raw_by_variety, network_errors = fetch_universe(
        varieties, Path(args.cache_dir).resolve(), warmup_start.year, end.year,
        end_period, args.workers,
    )
    sleeves: dict[str, pd.Series] = {}
    untradeable_sessions: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for variety in varieties:
        raw = raw_by_variety.get(variety)
        if raw is None or raw.empty:
            failures.append({"variety": variety, "reason": "无真实交割月历史行情"})
            continue
        try:
            sleeve, removed_dates = run_sleeve(model, raw, start, end)
            sleeves[variety] = sleeve
            if removed_dates:
                untradeable_sessions.append({"variety": variety, "dates": removed_dates})
        except Exception as exc:
            failures.append({"variety": variety, "reason": f"{type(exc).__name__}: {exc}"})
    monthly, years, portfolio = build_monthly_table(
        sleeves, varieties, start_period, end_period
    )
    successful = len(sleeves)
    status = "ready" if successful == len(varieties) and not network_errors else "partial"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "status_label": "完整回测" if status == "ready" else "部分覆盖，需核验",
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "as_of": end.strftime("%Y-%m-%d"),
        "window_start": start.strftime("%Y-%m-%d"),
        "window_end": end.strftime("%Y-%m-%d"),
        "model": {
            "name": "布林RSI模型",
            "version": model.MODEL_VERSION,
            "single_side_cost": SINGLE_SIDE_COST,
        },
        "methodology": {
            "portfolio": "当前40品种各占2.5%初始资金的静态等权策略袖套组合；各袖套内部权益复利，上市前或无数据资金按现金零收益处理",
            "execution": "T日使用T-1成交量选出的真实PYYMM主力合约；日线收盘确认，下一开盘执行",
            "price_policy": "指标、成交与损益均使用真实交割月自身未复权行情；不使用P0、连续、加权或合成价格",
            "cost": "每次单边交易按名义本金0.04%计费，换月按双边成本计费",
            "historical_margin": "月度模型收益不使用历史逐日保证金率；交易所实际保证金仅约束实时虚拟基金的可开仓容量",
            "missing_open_policy": "T-1主力在T日无可成交开盘时，该品种当日不执行、不填造价格，恢复真实行情后继续",
            "not_live_replay": "不是实时基金动态前八仓位、手数和板块配置的历史回放",
            "limitations": [
                "使用当前品种池回溯，存在品种池存续偏差",
                "新上市品种在上市前按现金零收益处理",
                "历史回测不代表未来收益",
            ],
        },
        "coverage": {
            "universe_count": len(varieties),
            "successful_count": successful,
            "failed_count": len(failures),
            "failed_varieties": failures,
            "network_error_count": len(network_errors),
            "network_errors": network_errors[:100],
            "untradeable_active_sessions": untradeable_sessions,
            "expected_months": MONTH_COUNT,
            "populated_months": sum(item["return"] is not None for item in monthly),
        },
        "summary": {
            "total_return": round(float(portfolio.iloc[-1]) - 1.0, 10),
            "ending_equity_multiple": round(float(portfolio.iloc[-1]), 10),
        },
        "monthly_returns": monthly,
        "years": years,
        "source": {
            "name": "新浪期货真实交割月日线（通过AKShare兼容接口）",
            "url": "https://finance.sina.com.cn/futures/",
            "updated_at": generated_at.isoformat(timespec="seconds"),
        },
        "update_schedule": "每月1日03:20 Asia/Shanghai，更新至上一个完整自然月",
        "ai_notice": "AI基于所列真实交割月行情和既定模型规则生成回测表，不代表新浪、AKShare、交易所或任何来源方的官方立场，也不构成投资建议；历史收益不保证未来表现，请自行核验。",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--cache-dir", default="/srv/palm-oil-daily/state/ai-daredevil-backtest/cache")
    parser.add_argument("--output", default="/srv/palm-oil-daily/live-data/ai_daredevil_monthly_backtest.json")
    parser.add_argument("--as-of", help="YYYY-MM-DD; defaults to today in Asia/Shanghai")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    payload = build_payload(args)
    atomic_write_json(Path(args.output).resolve(), payload)
    print(json.dumps({
        "status": payload["status"],
        "output": str(Path(args.output).resolve()),
        "as_of": payload["as_of"],
        "coverage": payload["coverage"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""棕榈油V2：布林中轨突破入场 + RSI背离止盈 + 多空非对称MA6止损。

使用日线回测。所有信号均在当日收盘确认，并在下一交易日开盘执行；
单边交易成本固定为0.04%，不使用未来数据。止损均线默认MA6，可切换为MA20。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


COST = 0.0004
DEFAULT_PYRAMID_ATR = 1.0
LATEST_MODEL_NAME = "布林RSI模型"
# P0 单一连续代理没有真实合约换月；其固定入口仍保持原版本。
LATEST_MODEL_VERSION = "bollinger-rsi-ma6-pyramid-v1"

# 可选 combo 退出模式参数；正式默认仍是 MA6/RSI 基线退出。
TRAIL_TIER1_ATR = 0.75
TRAIL_TIER2_ATR = 1.5
TRAIL_TIER3_ATR = 2.5
TRAIL_DIST_ATR = 1.0
ATR_TARGET = 2.5


def fetch_daily() -> pd.DataFrame:
    import akshare as ak

    data = ak.futures_main_sina(symbol="P0").rename(columns={
        "日期": "datetime", "开盘价": "open", "最高价": "high",
        "最低价": "low", "收盘价": "close", "成交量": "volume",
        "持仓量": "hold",
    })
    return normalize(data)


def normalize(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    out["datetime"] = pd.to_datetime(out["datetime"])
    for column in ["open", "high", "low", "close", "volume", "hold"]:
        if column in out:
            out[column] = pd.to_numeric(out[column], errors="coerce")
    return (
        out.dropna(subset=["datetime", "open", "high", "low", "close"])
        .sort_values("datetime")
        .reset_index(drop=True)
    )


def prepare(data: pd.DataFrame, divergence_window: int = 20) -> pd.DataFrame:
    out = data.copy()
    out["ma20"] = out.close.rolling(20).mean()
    std = out.close.rolling(20).std(ddof=0)
    out["upper"] = out.ma20 + 2 * std
    out["lower"] = out.ma20 - 2 * std
    out["ma6"] = out.close.rolling(6).mean()

    delta = out.close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    average_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    average_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    out["rsi"] = 100 - 100 / (1 + average_gain / average_loss.replace(0, np.nan))
    out.loc[average_loss.eq(0) & average_gain.gt(0), "rsi"] = 100

    previous_close = out.close.shift()
    true_range = pd.concat([
        out.high - out.low,
        (out.high - previous_close).abs(),
        (out.low - previous_close).abs(),
    ], axis=1).max(axis=1)
    out["atr"] = true_range.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()

    # 布林中轨就是MA20；仅要求收盘价穿越中轨，不要求收口或RSI>50。
    out["long_signal"] = out.close.gt(out.ma20) & out.close.shift().le(out.ma20.shift())
    out["short_signal"] = out.close.lt(out.ma20) & out.close.shift().ge(out.ma20.shift())

    prior_highs, rsi_at_highs, prior_lows, rsi_at_lows = [], [], [], []
    for i in range(len(out)):
        if i < divergence_window:
            prior_highs.append(np.nan)
            rsi_at_highs.append(np.nan)
            prior_lows.append(np.nan)
            rsi_at_lows.append(np.nan)
            continue
        previous = out.iloc[i - divergence_window:i]
        high_index = previous.high.idxmax()
        low_index = previous.low.idxmin()
        prior_highs.append(previous.loc[high_index, "high"])
        rsi_at_highs.append(previous.loc[high_index, "rsi"])
        prior_lows.append(previous.loc[low_index, "low"])
        rsi_at_lows.append(previous.loc[low_index, "rsi"])

    out["prior_high_20"] = prior_highs
    out["rsi_at_prior_high"] = rsi_at_highs
    out["prior_low_20"] = prior_lows
    out["rsi_at_prior_low"] = rsi_at_lows
    out["bearish_divergence"] = (
        out.high.gt(out.prior_high_20) & out.rsi.le(out.rsi_at_prior_high)
    )
    out["bullish_divergence"] = (
        out.low.lt(out.prior_low_20) & out.rsi.ge(out.rsi_at_prior_low)
    )
    return out


def backtest(
    data: pd.DataFrame,
    stop_ma_period: int = 6,
    pyramiding: bool = True,
    pyramid_atr: float = DEFAULT_PYRAMID_ATR,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if stop_ma_period not in {6, 20}:
        raise ValueError("stop_ma_period must be 6 or 20")
    if pyramid_atr <= 0:
        raise ValueError("pyramid_atr must be positive")
    stop_label = f"MA{stop_ma_period}"
    equity, position, entry, entry_atr, entry_time = 1.0, 0, np.nan, np.nan, None
    trade_base, high_water, low_water = 1.0, np.nan, np.nan
    pending_stop = False
    pending_pyramid = False
    pyramided = False
    pyramid_time, pyramid_price, pyramid_profit_atr = None, np.nan, np.nan
    stop_confirm_count = 0
    blocked_direction = 0
    trades: list[dict] = []
    events: list[dict] = []
    curve: list[dict] = []

    def position_size() -> float:
        return 2.0 if pyramided else 1.0

    def weighted_entry() -> float:
        return (entry + pyramid_price) / 2 if pyramided else entry

    def close_position(time, price: float, reason: str, is_stop: bool) -> None:
        nonlocal equity, position, pending_stop, pending_pyramid, stop_confirm_count, blocked_direction
        old_position = position
        initial_return = old_position * (price / entry - 1) - 2 * COST
        pyramid_contribution = (
            old_position * (price / pyramid_price - 1) - 2 * COST if pyramided else 0.0
        )
        net_return = initial_return + pyramid_contribution
        total_entry_fee = COST * position_size()
        total_exit_fee = COST * position_size()
        equity = trade_base * (1 + net_return)
        direction = "做多" if old_position == 1 else "做空"
        trades.append({
            "入场时间": entry_time, "出场时间": time, "方向": direction,
            "入场价": entry, "初始入场价": entry, "初始仓位": 1.0,
            "追加时间": pyramid_time, "追加价": pyramid_price,
            "追加仓位": 1.0 if pyramided else 0.0,
            "加仓触发ATR": entry_atr if pyramided else np.nan,
            "加仓触发浮盈ATR": pyramid_profit_atr if pyramided else np.nan,
            "总敞口": position_size(), "加权平均入场价": weighted_entry(),
            "出场价": price, "出场原因": reason,
            "入场手续费": total_entry_fee, "出场手续费": total_exit_fee,
            "总手续费": total_entry_fee + total_exit_fee,
            "初始仓收益贡献": initial_return,
            "加仓后收益贡献": pyramid_contribution,
            "净收益率": net_return, "权益": equity,
        })
        events.append({
            "时间": time, "事件": "平仓", "方向": direction, "价格": price,
            "仓位层级": "全部", "成交仓位": position_size(), "总敞口": position_size(),
            "加权平均入场价": weighted_entry(), "原因": reason,
        })
        if is_stop:
            blocked_direction = old_position
        position = 0
        pending_stop = False
        pending_pyramid = False
        stop_confirm_count = 0

    for i, row in data.iterrows():
        previous = data.iloc[i - 1] if i else None

        # 上一根K线收盘确认止损，本根K线开盘退出。
        if position and pending_stop:
            close_position(row.datetime, row.open, f"非对称{stop_label}止损", True)

        # 上一根K线确认价格/RSI背离，本根K线开盘止盈。
        if position and previous is not None:
            divergence = (
                (position == 1 and previous.bearish_divergence)
                or (position == -1 and previous.bullish_divergence)
            )
            if divergence:
                reason = "价格新高但RSI未创新高" if position == 1 else "价格新低但RSI未创新低"
                close_position(row.datetime, row.open, reason, False)

        # 上一根K线收盘确认初始仓已获利至少1ATR，本根K线开盘只追加一次。
        if position and pending_pyramid:
            pyramid_time, pyramid_price = row.datetime, row.open
            pyramided = True
            pending_pyramid = False
            events.append({
                "时间": row.datetime, "事件": "加仓", "方向": "做多" if position == 1 else "做空",
                "价格": row.open, "仓位层级": "追加", "成交仓位": 1.0,
                "总敞口": 2.0, "加权平均入场价": weighted_entry(),
                "加仓触发ATR": entry_atr, "加仓触发浮盈ATR": pyramid_profit_atr,
                "原因": f"初始仓收盘浮盈达到{pyramid_atr:g}ATR",
            })

        # 空仓后按上一根K线的中轨交叉入场。止损方向需先出现反向交叉才解锁。
        if position == 0 and previous is not None and pd.notna(previous.atr):
            direction = 1 if previous.long_signal else (-1 if previous.short_signal else 0)
            if blocked_direction and direction == -blocked_direction:
                blocked_direction = 0
            if direction and direction != blocked_direction:
                position, entry, entry_atr, entry_time = direction, row.open, previous.atr, row.datetime
                trade_base = equity
                high_water, low_water = row.open, row.open
                stop_confirm_count = 0
                pending_pyramid = False
                pyramided = False
                pyramid_time, pyramid_price, pyramid_profit_atr = None, np.nan, np.nan
                events.append({
                    "时间": row.datetime, "事件": "开仓",
                    "方向": "做多" if direction == 1 else "做空",
                    "价格": entry, "仓位层级": "初始", "成交仓位": 1.0,
                    "总敞口": 1.0, "加权平均入场价": entry,
                    "原因": "向上突破MA20" if direction == 1 else "向下突破MA20",
                })

        stop_level = np.nan
        stop_active = False
        if position:
            high_water = max(high_water, row.high)
            low_water = min(low_water, row.low)
            stop_level = row.ma6 if stop_ma_period == 6 else row.ma20
            if position == 1:
                # 多单只有浮盈达到0.75ATR后才启动均线止损；连续两根收盘跌破才退出。
                stop_active = (high_water - entry) / entry_atr >= 0.75
                breached = row.close < stop_level
                stop_confirm_count = stop_confirm_count + 1 if stop_active and breached else 0
                pending_stop = stop_confirm_count >= 2
            else:
                # 空单均线止损立即有效；一根收盘突破即退出。
                stop_active = True
                breached = row.close > stop_level
                stop_confirm_count = stop_confirm_count + 1 if breached else 0
                pending_stop = stop_confirm_count >= 1

            # 仅以已完成K线的收盘价确认，不以盘中最高/最低价追触发。
            if pyramiding and not pyramided and not pending_pyramid:
                profit_atr = position * (row.close - entry) / entry_atr
                if profit_atr >= pyramid_atr:
                    pending_pyramid = True
                    pyramid_profit_atr = profit_atr

        marked_equity = (
            equity if position == 0
            else trade_base * (
                1 + position * (row.close / entry - 1) - COST
                + (position * (row.close / pyramid_price - 1) - COST if pyramided else 0.0)
            )
        )
        curve.append({
            "时间": row.datetime, "收盘价": row.close, "持仓方向": position,
            "MA6": row.ma6, "MA20": row.ma20,
            "止损均线": stop_label, "止损线": stop_level,
            "止损已激活": stop_active,
            "连续触发数": stop_confirm_count,
            "初始入场价": entry if position else np.nan,
            "追加价": pyramid_price if pyramided else np.nan,
            "加权平均入场价": weighted_entry() if position else np.nan,
            "已加仓": pyramided, "待加仓": pending_pyramid,
            "总敞口": position * position_size(), "权益": marked_equity,
        })

    if position:
        row = data.iloc[-1]
        close_position(row.datetime, row.close, "期末平仓", False)
        curve[-1]["权益"] = equity
    return pd.DataFrame(trades), pd.DataFrame(events), pd.DataFrame(curve)


def backtest_latest(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the fixed production model used by all dependent programs.

    Rules are intentionally not caller-configurable: MA20 crossing entry,
    RSI divergence exit, asymmetric MA6 exit, and one 1-ATR profit add from
    1x to 2x gross exposure.
    """
    return backtest(
        data,
        stop_ma_period=6,
        pyramiding=True,
        pyramid_atr=DEFAULT_PYRAMID_ATR,
    )


def metrics(
    data: pd.DataFrame,
    stop_ma_period: int = 6,
    pyramiding: bool = True,
    pyramid_atr: float = DEFAULT_PYRAMID_ATR,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return comparable strategy metrics without changing the input window."""
    trades, events, curve = backtest(
        data,
        stop_ma_period=stop_ma_period,
        pyramiding=pyramiding,
        pyramid_atr=pyramid_atr,
    )
    final_equity = float(curve.权益.iloc[-1]) if len(curve) else 1.0
    days = max((data.datetime.iloc[-1] - data.datetime.iloc[0]).days, 1)
    annual_return = final_equity ** (365.25 / days) - 1 if final_equity > 0 else -1.0
    max_drawdown = float((curve.权益 / curve.权益.cummax() - 1).min()) if len(curve) else 0.0
    win_rate = float((trades.净收益率 > 0).mean()) if len(trades) else 0.0
    pyramid_count = int((events.事件 == "加仓").sum()) if len(events) else 0
    pyramid_contribution = float(trades.加仓后收益贡献.sum()) if len(trades) else 0.0
    return {
        "实际开始": data.datetime.iloc[0], "实际结束": data.datetime.iloc[-1],
        "K线数": len(data), "完整交易次数": len(trades), "胜率": win_rate,
        "累计净收益": final_equity - 1, "年化收益": annual_return,
        "最大回撤": max_drawdown, "加仓次数": pyramid_count,
        "加仓后收益贡献": pyramid_contribution,
        "最大总敞口": float(curve.总敞口.abs().max()) if len(curve) else 0.0,
    }, trades, events, curve


def build_comparison(
    prepared: pd.DataFrame,
    end: pd.Timestamp,
    stop_ma_period: int,
    pyramid_atr: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare baseline and one-addition versions under identical windows."""
    def compare_window(label: str, window: pd.DataFrame) -> list[dict]:
        rows = []
        for name, enabled in [("基线_不加仓", False), (f"浮盈加仓_{pyramid_atr:g}ATR", True)]:
            result, _, _, _ = metrics(
                window, stop_ma_period=stop_ma_period,
                pyramiding=enabled, pyramid_atr=pyramid_atr,
            )
            rows.append({"窗口": label, "策略": name, **result})
        return rows

    recent_rows: list[dict] = []
    for years in [1, 3, 5]:
        window = prepared[prepared.datetime >= end - pd.DateOffset(years=years)].reset_index(drop=True)
        if len(window) >= 21:
            recent_rows.extend(compare_window(f"最近{years}年", window))

    rolling_rows: list[dict] = []
    for year in range(int(prepared.datetime.min().year) + 1, int(end.year) + 1):
        period_end = min(end, pd.Timestamp(year=year, month=12, day=31))
        period_start = period_end - pd.DateOffset(years=1)
        window = prepared[
            prepared.datetime.between(period_start, period_end, inclusive="both")
        ].reset_index(drop=True)
        if len(window) >= 100:
            rolling_rows.extend(compare_window(f"截至{period_end:%Y-%m-%d}的滚动1年", window))
    return pd.DataFrame(recent_rows), pd.DataFrame(rolling_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", choices=["daily"], default="daily", help="仅支持日线")
    parser.add_argument("--years", type=int, default=1, help="日线回测年数")
    parser.add_argument("--stop-ma", type=int, choices=[6, 20], default=6, help="止损均线周期")
    parser.add_argument("--disable-pyramiding", action="store_true", help="关闭浮盈加仓，复现原单层仓位基线")
    parser.add_argument("--pyramid-atr", type=float, default=DEFAULT_PYRAMID_ATR, help="首次加仓所需初始仓收盘浮盈ATR倍数")
    parser.add_argument("--output-dir", help="输出目录；默认按周期自动命名")
    args = parser.parse_args()

    raw = fetch_daily()
    end = raw.datetime.max()
    start = end - pd.DateOffset(years=args.years)
    # 全部可用历史只用于指标预热，回测收益从start开始计算。
    prepared = prepare(raw, divergence_window=20)
    window = prepared[prepared.datetime >= start].reset_index(drop=True)
    result, trades, events, curve = metrics(
        window,
        stop_ma_period=args.stop_ma,
        pyramiding=not args.disable_pyramiding,
        pyramid_atr=args.pyramid_atr,
    )
    divergence_exits = int(trades.出场原因.str.contains("RSI", na=False).sum()) if len(trades) else 0
    stop_label = f"MA{args.stop_ma}"
    stop_exits = int(trades.出场原因.str.contains(stop_label, na=False).sum()) if len(trades) else 0
    summary = pd.DataFrame([{
        "模型名称": LATEST_MODEL_NAME,
        "模型版本": LATEST_MODEL_VERSION if not args.disable_pyramiding and args.stop_ma == 6 and args.pyramid_atr == DEFAULT_PYRAMID_ATR else "研究参数变体",
        "周期": "日线", "数据范围": f"{window.datetime.min()} 至 {window.datetime.max()}",
        "K线数": result["K线数"], "完整交易次数": result["完整交易次数"],
        "RSI背离止盈次数": divergence_exits, f"{stop_label}止损次数": stop_exits,
        "胜率": result["胜率"], "累计净收益": result["累计净收益"],
        "年化收益": result["年化收益"], "最大回撤": result["最大回撤"],
        "入场": "收盘突破MA20，下一根K线开盘入场",
        "止盈": "20根K线价格新高/低但RSI未确认",
        "多单止损": f"浮盈>=0.75ATR后连续2根K线收盘跌破{stop_label}",
        "空单止损": f"1根K线收盘突破{stop_label}",
        "止损后再入场": "反向MA20交叉后解除原方向锁定",
        "浮盈加仓": "关闭" if args.disable_pyramiding else f"初始仓收盘浮盈>={args.pyramid_atr:g}ATR，下一根开盘追加1倍（最多一次）",
        "加仓次数": result["加仓次数"], "加仓后收益贡献": result["加仓后收益贡献"],
        "最大总敞口": result["最大总敞口"],
        "单边成本": COST,
    }])

    suffix = "" if args.stop_ma == 6 else "_ma20_stop"
    default_output = f"palm_oil_bollinger_rsi_ma6_daily{suffix}_output"
    output = Path(args.output_dir or default_output)
    output.mkdir(exist_ok=True)
    raw.to_csv(output / "raw.csv", index=False, encoding="utf-8-sig")
    window.to_csv(output / "backtest_window.csv", index=False, encoding="utf-8-sig")
    trades.to_csv(output / "trades.csv", index=False, encoding="utf-8-sig")
    events.to_csv(output / "events.csv", index=False, encoding="utf-8-sig")
    curve.to_csv(output / "equity_curve.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(output / "summary.csv", index=False, encoding="utf-8-sig")
    recent_comparison, rolling_comparison = build_comparison(
        prepared, end, args.stop_ma, args.pyramid_atr,
    )
    recent_comparison.to_csv(output / "comparison_recent_1_3_5y.csv", index=False, encoding="utf-8-sig")
    rolling_comparison.to_csv(output / "comparison_rolling_1y.csv", index=False, encoding="utf-8-sig")
    print(summary.to_string(index=False, formatters={
        "胜率": "{:.2%}".format, "累计净收益": "{:.2%}".format,
        "年化收益": "{:.2%}".format, "最大回撤": "{:.2%}".format,
        "加仓后收益贡献": "{:.2%}".format,
        "单边成本": "{:.4%}".format,
    }))
    print(f"输出目录: {output.resolve()}")


if __name__ == "__main__":
    main()

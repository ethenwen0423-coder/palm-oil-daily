window.QUANT_MODEL_SIGNALS = {
  "status": "ok",
  "schema_version": 2,
  "generated_at": "2026-07-27T11:43:01+08:00",
  "market_updated_at": "2026-07-27 11:37",
  "market_update_session": "midday",
  "market_timezone": "Asia/Shanghai",
  "default_model_id": "bollinger-rsi-ma6-v1",
  "models": [
    {
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
      "universe": [
        "P 棕榈油",
        "Y 豆油",
        "OI 菜油",
        "M 豆粕",
        "RM 菜粕"
      ],
      "summary": "以 MA20 穿越识别方向，以 RSI 价格背离锁定止盈，并使用多空非对称 MA6 规则控制回撤。",
      "tags": [
        "MA20 趋势",
        "RSI 背离",
        "MA6 风控",
        "次日开盘执行"
      ],
      "rules": {
        "entry": {
          "title": "趋势入场",
          "summary": "完整日线收盘穿越 MA20 后，于次交易日开盘执行。",
          "conditions": [
            "收盘价由下向上穿越 MA20：确认做多信号",
            "收盘价由上向下穿越 MA20：确认做空信号",
            "执行窗口已过时不追单，等待下一个确认信号"
          ]
        },
        "take_profit": {
          "title": "RSI 背离止盈",
          "summary": "用 20 日价格极值与 RSI 是否同步确认判断趋势衰竭。",
          "conditions": [
            "多单：价格创 20 日新高，RSI 未创对应新高，全部止盈",
            "空单：价格创 20 日新低，RSI 未创对应新低，全部止盈",
            "只使用已完成日线确认背离"
          ]
        },
        "stop": {
          "title": "多空非对称止损",
          "summary": "多单先等待浮盈激活保护，空单则用更快的 MA6 收盘规则。",
          "conditions": [
            "多单最大有利浮动达到 0.75 倍入场 ATR 后，激活 MA6 保护",
            "激活后连续两个完整收盘低于 MA6，多单全部止损",
            "一个完整收盘高于 MA6，空单全部止损"
          ]
        },
        "reentry": {
          "title": "再入场锁定",
          "summary": "止损后不立即重复开同方向仓位。",
          "conditions": [
            "止损方向保持锁定",
            "只有出现反向 MA20 穿越后，才解除原方向锁定"
          ]
        },
        "execution": {
          "title": "执行约束",
          "summary": "信号与下单时点分离，避免使用未完成日线或追逐过期信号。",
          "conditions": [
            "默认只使用最新完整日线",
            "确认信号在次交易日开盘执行",
            "过期入场信号降级为观望；过期离场信号应在下一可用机会处理"
          ]
        }
      },
      "cost_assumption_one_way": 0.0004,
      "risk_notice": "该模型是基于历史日线的确定性规则，不保证未来表现；同规则试算不等于已完成独立回测验证。"
    }
  ],
  "model_contracts": {
    "bollinger-rsi-ma6-v1": [
      {
        "symbol": "P2609",
        "product": "P",
        "product_name": "棕榈油",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "validated_mapping",
        "model_scope_label": "成熟模型映射",
        "market": {
          "close": 9570.0,
          "ma6": 9366.0,
          "ma20": 9298.55,
          "atr14": 152.54074116994798,
          "rsi14": 60.0389432035961,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9570.0,
              "ma6": 9366.0,
              "ma20": 9298.55,
              "atr14": 152.54074116994798,
              "rsi14": 60.0389432035961,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9570.0,
              "ma6": 9366.0,
              "ma20": 9298.55,
              "atr14": 152.54074116994798,
              "rsi14": 60.0389432035961,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 9570.0,
              "ma6": 9366.0,
              "ma20": 9298.55,
              "atr14": 152.54074116994798,
              "rsi14": 60.0389432035961,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 9366.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 9394.0,
          "change": "-1.84%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "P2701",
        "product": "P",
        "product_name": "棕榈油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "validated_mapping",
        "model_scope_label": "成熟模型映射",
        "market": {
          "close": 9843.0,
          "ma6": 9653.166666666666,
          "ma20": 9578.45,
          "atr14": 141.60915344440377,
          "rsi14": 61.16490752511858,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9843.0,
              "ma6": 9653.166666666666,
              "ma20": 9578.45,
              "atr14": 141.60915344440377,
              "rsi14": 61.16490752511858,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9843.0,
              "ma6": 9653.166666666666,
              "ma20": 9578.45,
              "atr14": 141.60915344440377,
              "rsi14": 61.16490752511858,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 9843.0,
              "ma6": 9653.166666666666,
              "ma20": 9578.45,
              "atr14": 141.60915344440377,
              "rsi14": 61.16490752511858,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 9653.166666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 9690.0,
          "change": "-1.55%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "Y2609",
        "product": "Y",
        "product_name": "豆油",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 8620.0,
          "ma6": 8547.166666666666,
          "ma20": 8533.5,
          "atr14": 86.96637995130277,
          "rsi14": 57.823232748710076,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "Y2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8620.0,
              "ma6": 8547.166666666666,
              "ma20": 8533.5,
              "atr14": 86.96637995130277,
              "rsi14": 57.823232748710076,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "Y2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8620.0,
              "ma6": 8547.166666666666,
              "ma20": 8533.5,
              "atr14": 86.96637995130277,
              "rsi14": 57.823232748710076,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "Y2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 8620.0,
              "ma6": 8547.166666666666,
              "ma20": 8533.5,
              "atr14": 86.96637995130277,
              "rsi14": 57.823232748710076,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 8547.166666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 8492.0,
          "change": "-1.48%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "Y2701",
        "product": "Y",
        "product_name": "豆油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 8633.0,
          "ma6": 8555.333333333334,
          "ma20": 8518.3,
          "atr14": 83.87009091940598,
          "rsi14": 60.59713016758963,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": true,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "Y2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8633.0,
              "ma6": 8555.333333333334,
              "ma20": 8518.3,
              "atr14": 83.87009091940598,
              "rsi14": 60.59713016758963,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": true,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "Y2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "price made a 20-day high while RSI failed to confirm",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8633.0,
              "ma6": 8555.333333333334,
              "ma20": 8518.3,
              "atr14": 83.87009091940598,
              "rsi14": 60.59713016758963,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": true,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "TAKE_PROFIT_EXIT_LONG",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "Y2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 8633.0,
              "ma6": 8555.333333333334,
              "ma20": 8518.3,
              "atr14": 83.87009091940598,
              "rsi14": 60.59713016758963,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": true,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 8555.333333333334
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 8520.0,
          "change": "-1.31%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "OI2609",
        "product": "OI",
        "product_name": "菜油",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 10281.0,
          "ma6": 10071.333333333334,
          "ma20": 9884.6,
          "atr14": 140.25278144588066,
          "rsi14": 66.90007953472426,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "OI2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10281.0,
              "ma6": 10071.333333333334,
              "ma20": 9884.6,
              "atr14": 140.25278144588066,
              "rsi14": 66.90007953472426,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "OI2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10281.0,
              "ma6": 10071.333333333334,
              "ma20": 9884.6,
              "atr14": 140.25278144588066,
              "rsi14": 66.90007953472426,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "OI2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 10281.0,
              "ma6": 10071.333333333334,
              "ma20": 9884.6,
              "atr14": 140.25278144588066,
              "rsi14": 66.90007953472426,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 10071.333333333334
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 10039.0,
          "change": "-2.35%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "OI2611",
        "product": "OI",
        "product_name": "菜油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 10276.0,
          "ma6": 10068.833333333334,
          "ma20": 9876.1,
          "atr14": 137.49826608167743,
          "rsi14": 67.39388020928129,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "OI2611",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10276.0,
              "ma6": 10068.833333333334,
              "ma20": 9876.1,
              "atr14": 137.49826608167743,
              "rsi14": 67.39388020928129,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "OI2611",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10276.0,
              "ma6": 10068.833333333334,
              "ma20": 9876.1,
              "atr14": 137.49826608167743,
              "rsi14": 67.39388020928129,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "OI2611",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 10276.0,
              "ma6": 10068.833333333334,
              "ma20": 9876.1,
              "atr14": 137.49826608167743,
              "rsi14": 67.39388020928129,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 10068.833333333334
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 10039.0,
          "change": "-2.31%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "M2609",
        "product": "M",
        "product_name": "豆粕",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 3225.0,
          "ma6": 3147.3333333333335,
          "ma20": 3057.65,
          "atr14": 39.86364280531316,
          "rsi14": 84.95486255809308,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "M2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3225.0,
              "ma6": 3147.3333333333335,
              "ma20": 3057.65,
              "atr14": 39.86364280531316,
              "rsi14": 84.95486255809308,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "M2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3225.0,
              "ma6": 3147.3333333333335,
              "ma20": 3057.65,
              "atr14": 39.86364280531316,
              "rsi14": 84.95486255809308,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "M2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 3225.0,
              "ma6": 3147.3333333333335,
              "ma20": 3057.65,
              "atr14": 39.86364280531316,
              "rsi14": 84.95486255809308,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 3147.3333333333335
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 3181.0,
          "change": "-1.36%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "M2701",
        "product": "M",
        "product_name": "豆粕",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 3270.0,
          "ma6": 3202.8333333333335,
          "ma20": 3117.2,
          "atr14": 34.970763900678776,
          "rsi14": 85.73157768794474,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "M2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3270.0,
              "ma6": 3202.8333333333335,
              "ma20": 3117.2,
              "atr14": 34.970763900678776,
              "rsi14": 85.73157768794474,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "M2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3270.0,
              "ma6": 3202.8333333333335,
              "ma20": 3117.2,
              "atr14": 34.970763900678776,
              "rsi14": 85.73157768794474,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "M2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 3270.0,
              "ma6": 3202.8333333333335,
              "ma20": 3117.2,
              "atr14": 34.970763900678776,
              "rsi14": 85.73157768794474,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 3202.8333333333335
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 3237.0,
          "change": "-1.01%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "RM2609",
        "product": "RM",
        "product_name": "菜粕",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 2467.0,
          "ma6": 2356.3333333333335,
          "ma20": 2314.85,
          "atr14": 42.54712899898587,
          "rsi14": 72.28233979699029,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "RM2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2467.0,
              "ma6": 2356.3333333333335,
              "ma20": 2314.85,
              "atr14": 42.54712899898587,
              "rsi14": 72.28233979699029,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "RM2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2467.0,
              "ma6": 2356.3333333333335,
              "ma20": 2314.85,
              "atr14": 42.54712899898587,
              "rsi14": 72.28233979699029,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "RM2609",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 2467.0,
              "ma6": 2356.3333333333335,
              "ma20": 2314.85,
              "atr14": 42.54712899898587,
              "rsi14": 72.28233979699029,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 2356.3333333333335
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 2399.0,
          "change": "-2.76%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "akshare:futures_zh_realtime",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "RM2701",
        "product": "RM",
        "product_name": "菜粕",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-24",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 2389.0,
          "ma6": 2298.1666666666665,
          "ma20": 2257.45,
          "atr14": 32.11385252129422,
          "rsi14": 75.62524209714222,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "RM2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2389.0,
              "ma6": 2298.1666666666665,
              "ma20": 2257.45,
              "atr14": 32.11385252129422,
              "rsi14": 75.62524209714222,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "RM2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2389.0,
              "ma6": 2298.1666666666665,
              "ma20": 2257.45,
              "atr14": 32.11385252129422,
              "rsi14": 75.62524209714222,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "evaluated": false,
              "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "short": {
            "status": "ok",
            "symbol": "RM2701",
            "period": "daily",
            "market_date": "2026-07-24",
            "position": "short",
            "action": "EXIT_SIGNAL_OVERDUE",
            "execution": "next_available_market_opportunity",
            "rationale": [
              "short stop triggered: completed close above MA6",
              "the strategy's next-open exit window has passed; risk-control exit is overdue"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 2389.0,
              "ma6": 2298.1666666666665,
              "ma20": 2257.45,
              "atr14": 32.11385252129422,
              "rsi14": 75.62524209714222,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 2298.1666666666665
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-27",
            "intended_execution_at": "2026-07-24T21:00+08:00",
            "original_confirmed_action": "STOP_EXIT_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 2351.0,
          "change": "-1.59%",
          "direction": "↓",
          "trade_date": "2026-07-27",
          "source": "akshare:futures_zh_realtime",
          "unit": "元/吨"
        }
      }
    ]
  },
  "model": {
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
    "universe": [
      "P 棕榈油",
      "Y 豆油",
      "OI 菜油",
      "M 豆粕",
      "RM 菜粕"
    ],
    "summary": "以 MA20 穿越识别方向，以 RSI 价格背离锁定止盈，并使用多空非对称 MA6 规则控制回撤。",
    "tags": [
      "MA20 趋势",
      "RSI 背离",
      "MA6 风控",
      "次日开盘执行"
    ],
    "rules": {
      "entry": {
        "title": "趋势入场",
        "summary": "完整日线收盘穿越 MA20 后，于次交易日开盘执行。",
        "conditions": [
          "收盘价由下向上穿越 MA20：确认做多信号",
          "收盘价由上向下穿越 MA20：确认做空信号",
          "执行窗口已过时不追单，等待下一个确认信号"
        ]
      },
      "take_profit": {
        "title": "RSI 背离止盈",
        "summary": "用 20 日价格极值与 RSI 是否同步确认判断趋势衰竭。",
        "conditions": [
          "多单：价格创 20 日新高，RSI 未创对应新高，全部止盈",
          "空单：价格创 20 日新低，RSI 未创对应新低，全部止盈",
          "只使用已完成日线确认背离"
        ]
      },
      "stop": {
        "title": "多空非对称止损",
        "summary": "多单先等待浮盈激活保护，空单则用更快的 MA6 收盘规则。",
        "conditions": [
          "多单最大有利浮动达到 0.75 倍入场 ATR 后，激活 MA6 保护",
          "激活后连续两个完整收盘低于 MA6，多单全部止损",
          "一个完整收盘高于 MA6，空单全部止损"
        ]
      },
      "reentry": {
        "title": "再入场锁定",
        "summary": "止损后不立即重复开同方向仓位。",
        "conditions": [
          "止损方向保持锁定",
          "只有出现反向 MA20 穿越后，才解除原方向锁定"
        ]
      },
      "execution": {
        "title": "执行约束",
        "summary": "信号与下单时点分离，避免使用未完成日线或追逐过期信号。",
        "conditions": [
          "默认只使用最新完整日线",
          "确认信号在次交易日开盘执行",
          "过期入场信号降级为观望；过期离场信号应在下一可用机会处理"
        ]
      }
    },
    "cost_assumption_one_way": 0.0004,
    "risk_notice": "该模型是基于历史日线的确定性规则，不保证未来表现；同规则试算不等于已完成独立回测验证。"
  },
  "contracts": [
    {
      "symbol": "P2609",
      "product": "P",
      "product_name": "棕榈油",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "validated_mapping",
      "model_scope_label": "成熟模型映射",
      "market": {
        "close": 9570.0,
        "ma6": 9366.0,
        "ma20": 9298.55,
        "atr14": 152.54074116994798,
        "rsi14": 60.0389432035961,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9570.0,
            "ma6": 9366.0,
            "ma20": 9298.55,
            "atr14": 152.54074116994798,
            "rsi14": 60.0389432035961,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9570.0,
            "ma6": 9366.0,
            "ma20": 9298.55,
            "atr14": 152.54074116994798,
            "rsi14": 60.0389432035961,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 9570.0,
            "ma6": 9366.0,
            "ma20": 9298.55,
            "atr14": 152.54074116994798,
            "rsi14": 60.0389432035961,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 9366.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 9394.0,
        "change": "-1.84%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "P2701",
      "product": "P",
      "product_name": "棕榈油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "validated_mapping",
      "model_scope_label": "成熟模型映射",
      "market": {
        "close": 9843.0,
        "ma6": 9653.166666666666,
        "ma20": 9578.45,
        "atr14": 141.60915344440377,
        "rsi14": 61.16490752511858,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9843.0,
            "ma6": 9653.166666666666,
            "ma20": 9578.45,
            "atr14": 141.60915344440377,
            "rsi14": 61.16490752511858,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9843.0,
            "ma6": 9653.166666666666,
            "ma20": 9578.45,
            "atr14": 141.60915344440377,
            "rsi14": 61.16490752511858,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 9843.0,
            "ma6": 9653.166666666666,
            "ma20": 9578.45,
            "atr14": 141.60915344440377,
            "rsi14": 61.16490752511858,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 9653.166666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 9690.0,
        "change": "-1.55%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "Y2609",
      "product": "Y",
      "product_name": "豆油",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 8620.0,
        "ma6": 8547.166666666666,
        "ma20": 8533.5,
        "atr14": 86.96637995130277,
        "rsi14": 57.823232748710076,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "Y2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8620.0,
            "ma6": 8547.166666666666,
            "ma20": 8533.5,
            "atr14": 86.96637995130277,
            "rsi14": 57.823232748710076,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "Y2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8620.0,
            "ma6": 8547.166666666666,
            "ma20": 8533.5,
            "atr14": 86.96637995130277,
            "rsi14": 57.823232748710076,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "Y2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 8620.0,
            "ma6": 8547.166666666666,
            "ma20": 8533.5,
            "atr14": 86.96637995130277,
            "rsi14": 57.823232748710076,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 8547.166666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 8492.0,
        "change": "-1.48%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "Y2701",
      "product": "Y",
      "product_name": "豆油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 8633.0,
        "ma6": 8555.333333333334,
        "ma20": 8518.3,
        "atr14": 83.87009091940598,
        "rsi14": 60.59713016758963,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": true,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "Y2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8633.0,
            "ma6": 8555.333333333334,
            "ma20": 8518.3,
            "atr14": 83.87009091940598,
            "rsi14": 60.59713016758963,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": true,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "Y2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "price made a 20-day high while RSI failed to confirm",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8633.0,
            "ma6": 8555.333333333334,
            "ma20": 8518.3,
            "atr14": 83.87009091940598,
            "rsi14": 60.59713016758963,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": true,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "TAKE_PROFIT_EXIT_LONG",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "Y2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 8633.0,
            "ma6": 8555.333333333334,
            "ma20": 8518.3,
            "atr14": 83.87009091940598,
            "rsi14": 60.59713016758963,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": true,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 8555.333333333334
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 8520.0,
        "change": "-1.31%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "OI2609",
      "product": "OI",
      "product_name": "菜油",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 10281.0,
        "ma6": 10071.333333333334,
        "ma20": 9884.6,
        "atr14": 140.25278144588066,
        "rsi14": 66.90007953472426,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "OI2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10281.0,
            "ma6": 10071.333333333334,
            "ma20": 9884.6,
            "atr14": 140.25278144588066,
            "rsi14": 66.90007953472426,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "OI2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10281.0,
            "ma6": 10071.333333333334,
            "ma20": 9884.6,
            "atr14": 140.25278144588066,
            "rsi14": 66.90007953472426,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "OI2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 10281.0,
            "ma6": 10071.333333333334,
            "ma20": 9884.6,
            "atr14": 140.25278144588066,
            "rsi14": 66.90007953472426,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 10071.333333333334
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 10039.0,
        "change": "-2.35%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "OI2611",
      "product": "OI",
      "product_name": "菜油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 10276.0,
        "ma6": 10068.833333333334,
        "ma20": 9876.1,
        "atr14": 137.49826608167743,
        "rsi14": 67.39388020928129,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "OI2611",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10276.0,
            "ma6": 10068.833333333334,
            "ma20": 9876.1,
            "atr14": 137.49826608167743,
            "rsi14": 67.39388020928129,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "OI2611",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10276.0,
            "ma6": 10068.833333333334,
            "ma20": 9876.1,
            "atr14": 137.49826608167743,
            "rsi14": 67.39388020928129,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "OI2611",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 10276.0,
            "ma6": 10068.833333333334,
            "ma20": 9876.1,
            "atr14": 137.49826608167743,
            "rsi14": 67.39388020928129,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 10068.833333333334
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 10039.0,
        "change": "-2.31%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "M2609",
      "product": "M",
      "product_name": "豆粕",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 3225.0,
        "ma6": 3147.3333333333335,
        "ma20": 3057.65,
        "atr14": 39.86364280531316,
        "rsi14": 84.95486255809308,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "M2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3225.0,
            "ma6": 3147.3333333333335,
            "ma20": 3057.65,
            "atr14": 39.86364280531316,
            "rsi14": 84.95486255809308,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "M2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3225.0,
            "ma6": 3147.3333333333335,
            "ma20": 3057.65,
            "atr14": 39.86364280531316,
            "rsi14": 84.95486255809308,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "M2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 3225.0,
            "ma6": 3147.3333333333335,
            "ma20": 3057.65,
            "atr14": 39.86364280531316,
            "rsi14": 84.95486255809308,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 3147.3333333333335
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 3181.0,
        "change": "-1.36%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "M2701",
      "product": "M",
      "product_name": "豆粕",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 3270.0,
        "ma6": 3202.8333333333335,
        "ma20": 3117.2,
        "atr14": 34.970763900678776,
        "rsi14": 85.73157768794474,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "M2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3270.0,
            "ma6": 3202.8333333333335,
            "ma20": 3117.2,
            "atr14": 34.970763900678776,
            "rsi14": 85.73157768794474,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "M2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3270.0,
            "ma6": 3202.8333333333335,
            "ma20": 3117.2,
            "atr14": 34.970763900678776,
            "rsi14": 85.73157768794474,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "M2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 3270.0,
            "ma6": 3202.8333333333335,
            "ma20": 3117.2,
            "atr14": 34.970763900678776,
            "rsi14": 85.73157768794474,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 3202.8333333333335
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 3237.0,
        "change": "-1.01%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "RM2609",
      "product": "RM",
      "product_name": "菜粕",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 2467.0,
        "ma6": 2356.3333333333335,
        "ma20": 2314.85,
        "atr14": 42.54712899898587,
        "rsi14": 72.28233979699029,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "RM2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2467.0,
            "ma6": 2356.3333333333335,
            "ma20": 2314.85,
            "atr14": 42.54712899898587,
            "rsi14": 72.28233979699029,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "RM2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2467.0,
            "ma6": 2356.3333333333335,
            "ma20": 2314.85,
            "atr14": 42.54712899898587,
            "rsi14": 72.28233979699029,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "RM2609",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 2467.0,
            "ma6": 2356.3333333333335,
            "ma20": 2314.85,
            "atr14": 42.54712899898587,
            "rsi14": 72.28233979699029,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 2356.3333333333335
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 2399.0,
        "change": "-2.76%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "akshare:futures_zh_realtime",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "RM2701",
      "product": "RM",
      "product_name": "菜粕",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-24",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 2389.0,
        "ma6": 2298.1666666666665,
        "ma20": 2257.45,
        "atr14": 32.11385252129422,
        "rsi14": 75.62524209714222,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "RM2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2389.0,
            "ma6": 2298.1666666666665,
            "ma20": 2257.45,
            "atr14": 32.11385252129422,
            "rsi14": 75.62524209714222,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "RM2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2389.0,
            "ma6": 2298.1666666666665,
            "ma20": 2257.45,
            "atr14": 32.11385252129422,
            "rsi14": 75.62524209714222,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "evaluated": false,
            "missing": "entry_date or entry_price, entry_atr, and highest_since_entry"
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "short": {
          "status": "ok",
          "symbol": "RM2701",
          "period": "daily",
          "market_date": "2026-07-24",
          "position": "short",
          "action": "EXIT_SIGNAL_OVERDUE",
          "execution": "next_available_market_opportunity",
          "rationale": [
            "short stop triggered: completed close above MA6",
            "the strategy's next-open exit window has passed; risk-control exit is overdue"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 2389.0,
            "ma6": 2298.1666666666665,
            "ma20": 2257.45,
            "atr14": 32.11385252129422,
            "rsi14": 75.62524209714222,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 2298.1666666666665
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-27",
          "intended_execution_at": "2026-07-24T21:00+08:00",
          "original_confirmed_action": "STOP_EXIT_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 2351.0,
        "change": "-1.59%",
        "direction": "↓",
        "trade_date": "2026-07-27",
        "source": "akshare:futures_zh_realtime",
        "unit": "元/吨"
      }
    }
  ]
};

window.QUANT_MODEL_SIGNALS = {
  "status": "ok",
  "schema_version": 2,
  "generated_at": "2026-07-21T08:34:45+08:00",
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
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "validated_mapping",
        "model_scope_label": "成熟模型映射",
        "market": {
          "close": 9389.0,
          "ma6": 9284.5,
          "ma20": 9275.7,
          "atr14": 146.82301434770218,
          "rsi14": 53.48393659991196,
          "long_signal": true,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "OPEN_LONG",
            "execution": "next_trading_day_open",
            "rationale": [
              "completed close crossed above MA20"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9389.0,
              "ma6": 9284.5,
              "ma20": 9275.7,
              "atr14": 146.82301434770218,
              "rsi14": 53.48393659991196,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9389.0,
              "ma6": 9284.5,
              "ma20": 9275.7,
              "atr14": 146.82301434770218,
              "rsi14": 53.48393659991196,
              "long_signal": true,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 9389.0,
              "ma6": 9284.5,
              "ma20": 9275.7,
              "atr14": 146.82301434770218,
              "rsi14": 53.48393659991196,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 9284.5
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "P2701",
        "product": "P",
        "product_name": "棕榈油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "validated_mapping",
        "model_scope_label": "成熟模型映射",
        "market": {
          "close": 9670.0,
          "ma6": 9576.666666666666,
          "ma20": 9552.5,
          "atr14": 136.65688311754542,
          "rsi14": 54.744804464093086,
          "long_signal": true,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "OPEN_LONG",
            "execution": "next_trading_day_open",
            "rationale": [
              "completed close crossed above MA20"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9670.0,
              "ma6": 9576.666666666666,
              "ma20": 9552.5,
              "atr14": 136.65688311754542,
              "rsi14": 54.744804464093086,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9670.0,
              "ma6": 9576.666666666666,
              "ma20": 9552.5,
              "atr14": 136.65688311754542,
              "rsi14": 54.744804464093086,
              "long_signal": true,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 9670.0,
              "ma6": 9576.666666666666,
              "ma20": 9552.5,
              "atr14": 136.65688311754542,
              "rsi14": 54.744804464093086,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 9576.666666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "Y2609",
        "product": "Y",
        "product_name": "豆油",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 8599.0,
          "ma6": 8579.666666666666,
          "ma20": 8502.95,
          "atr14": 81.24703099363632,
          "rsi14": 58.889926127440944,
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
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8599.0,
              "ma6": 8579.666666666666,
              "ma20": 8502.95,
              "atr14": 81.24703099363632,
              "rsi14": 58.889926127440944,
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
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8599.0,
              "ma6": 8579.666666666666,
              "ma20": 8502.95,
              "atr14": 81.24703099363632,
              "rsi14": 58.889926127440944,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 8599.0,
              "ma6": 8579.666666666666,
              "ma20": 8502.95,
              "atr14": 81.24703099363632,
              "rsi14": 58.889926127440944,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 8579.666666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "Y2701",
        "product": "Y",
        "product_name": "豆油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 8593.0,
          "ma6": 8572.0,
          "ma20": 8476.15,
          "atr14": 80.30777678512305,
          "rsi14": 61.027180267505905,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "Y2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8593.0,
              "ma6": 8572.0,
              "ma20": 8476.15,
              "atr14": 80.30777678512305,
              "rsi14": 61.027180267505905,
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
            "symbol": "Y2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8593.0,
              "ma6": 8572.0,
              "ma20": 8476.15,
              "atr14": 80.30777678512305,
              "rsi14": 61.027180267505905,
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
            "symbol": "Y2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 8593.0,
              "ma6": 8572.0,
              "ma20": 8476.15,
              "atr14": 80.30777678512305,
              "rsi14": 61.027180267505905,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 8572.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "OI2609",
        "product": "OI",
        "product_name": "菜油",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 10050.0,
          "ma6": 9963.0,
          "ma20": 9793.3,
          "atr14": 134.98788039721825,
          "rsi14": 60.75728160954093,
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
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10050.0,
              "ma6": 9963.0,
              "ma20": 9793.3,
              "atr14": 134.98788039721825,
              "rsi14": 60.75728160954093,
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
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10050.0,
              "ma6": 9963.0,
              "ma20": 9793.3,
              "atr14": 134.98788039721825,
              "rsi14": 60.75728160954093,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 10050.0,
              "ma6": 9963.0,
              "ma20": 9793.3,
              "atr14": 134.98788039721825,
              "rsi14": 60.75728160954093,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 9963.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "OI2611",
        "product": "OI",
        "product_name": "菜油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 10045.0,
          "ma6": 9954.666666666666,
          "ma20": 9784.8,
          "atr14": 132.71900107817368,
          "rsi14": 61.1464715320885,
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
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10045.0,
              "ma6": 9954.666666666666,
              "ma20": 9784.8,
              "atr14": 132.71900107817368,
              "rsi14": 61.1464715320885,
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
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 10045.0,
              "ma6": 9954.666666666666,
              "ma20": 9784.8,
              "atr14": 132.71900107817368,
              "rsi14": 61.1464715320885,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 10045.0,
              "ma6": 9954.666666666666,
              "ma20": 9784.8,
              "atr14": 132.71900107817368,
              "rsi14": 61.1464715320885,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 9954.666666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "M2609",
        "product": "M",
        "product_name": "豆粕",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 3129.0,
          "ma6": 3070.3333333333335,
          "ma20": 3014.5,
          "atr14": 36.38789615240749,
          "rsi14": 77.36015818981144,
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
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3129.0,
              "ma6": 3070.3333333333335,
              "ma20": 3014.5,
              "atr14": 36.38789615240749,
              "rsi14": 77.36015818981144,
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
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3129.0,
              "ma6": 3070.3333333333335,
              "ma20": 3014.5,
              "atr14": 36.38789615240749,
              "rsi14": 77.36015818981144,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 3129.0,
              "ma6": 3070.3333333333335,
              "ma20": 3014.5,
              "atr14": 36.38789615240749,
              "rsi14": 77.36015818981144,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 3070.3333333333335
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "M2701",
        "product": "M",
        "product_name": "豆粕",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 3184.0,
          "ma6": 3136.0,
          "ma20": 3074.25,
          "atr14": 32.888864745928906,
          "rsi14": 78.40378755689969,
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
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3184.0,
              "ma6": 3136.0,
              "ma20": 3074.25,
              "atr14": 32.888864745928906,
              "rsi14": 78.40378755689969,
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
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3184.0,
              "ma6": 3136.0,
              "ma20": 3074.25,
              "atr14": 32.888864745928906,
              "rsi14": 78.40378755689969,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 3184.0,
              "ma6": 3136.0,
              "ma20": 3074.25,
              "atr14": 32.888864745928906,
              "rsi14": 78.40378755689969,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 3136.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "RM2609",
        "product": "RM",
        "product_name": "菜粕",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 2333.0,
          "ma6": 2307.5,
          "ma20": 2298.4,
          "atr14": 37.298326656105914,
          "rsi14": 55.84732469856743,
          "long_signal": true,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "RM2609",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "OPEN_LONG",
            "execution": "next_trading_day_open",
            "rationale": [
              "completed close crossed above MA20"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2333.0,
              "ma6": 2307.5,
              "ma20": 2298.4,
              "atr14": 37.298326656105914,
              "rsi14": 55.84732469856743,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "RM2609",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2333.0,
              "ma6": 2307.5,
              "ma20": 2298.4,
              "atr14": 37.298326656105914,
              "rsi14": 55.84732469856743,
              "long_signal": true,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 2333.0,
              "ma6": 2307.5,
              "ma20": 2298.4,
              "atr14": 37.298326656105914,
              "rsi14": 55.84732469856743,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 2307.5
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        }
      },
      {
        "symbol": "RM2701",
        "product": "RM",
        "product_name": "菜粕",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-20",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 2271.0,
          "ma6": 2249.6666666666665,
          "ma20": 2240.65,
          "atr14": 26.98644159721434,
          "rsi14": 56.99818990721578,
          "long_signal": true,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "RM2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "flat",
            "action": "OPEN_LONG",
            "execution": "next_trading_day_open",
            "rationale": [
              "completed close crossed above MA20"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2271.0,
              "ma6": 2249.6666666666665,
              "ma20": 2240.65,
              "atr14": 26.98644159721434,
              "rsi14": 56.99818990721578,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "RM2701",
            "period": "daily",
            "market_date": "2026-07-20",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2271.0,
              "ma6": 2249.6666666666665,
              "ma20": 2240.65,
              "atr14": 26.98644159721434,
              "rsi14": 56.99818990721578,
              "long_signal": true,
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
            "market_date": "2026-07-20",
            "position": "short",
            "action": "STOP_EXIT_SHORT",
            "execution": "next_trading_day_open",
            "rationale": [
              "short stop triggered: completed close above MA6"
            ],
            "blocked_direction_after_action": "short",
            "market": {
              "close": 2271.0,
              "ma6": 2249.6666666666665,
              "ma20": 2240.65,
              "atr14": 26.98644159721434,
              "rsi14": 56.99818990721578,
              "long_signal": true,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": true,
              "ma6": 2249.6666666666665
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-07-21",
            "execution_window": "pending",
            "data_source": "akshare:futures_zh_daily_sina"
          }
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
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "validated_mapping",
      "model_scope_label": "成熟模型映射",
      "market": {
        "close": 9389.0,
        "ma6": 9284.5,
        "ma20": 9275.7,
        "atr14": 146.82301434770218,
        "rsi14": 53.48393659991196,
        "long_signal": true,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "OPEN_LONG",
          "execution": "next_trading_day_open",
          "rationale": [
            "completed close crossed above MA20"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9389.0,
            "ma6": 9284.5,
            "ma20": 9275.7,
            "atr14": 146.82301434770218,
            "rsi14": 53.48393659991196,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9389.0,
            "ma6": 9284.5,
            "ma20": 9275.7,
            "atr14": 146.82301434770218,
            "rsi14": 53.48393659991196,
            "long_signal": true,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 9389.0,
            "ma6": 9284.5,
            "ma20": 9275.7,
            "atr14": 146.82301434770218,
            "rsi14": 53.48393659991196,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 9284.5
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "P2701",
      "product": "P",
      "product_name": "棕榈油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "validated_mapping",
      "model_scope_label": "成熟模型映射",
      "market": {
        "close": 9670.0,
        "ma6": 9576.666666666666,
        "ma20": 9552.5,
        "atr14": 136.65688311754542,
        "rsi14": 54.744804464093086,
        "long_signal": true,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "OPEN_LONG",
          "execution": "next_trading_day_open",
          "rationale": [
            "completed close crossed above MA20"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9670.0,
            "ma6": 9576.666666666666,
            "ma20": 9552.5,
            "atr14": 136.65688311754542,
            "rsi14": 54.744804464093086,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9670.0,
            "ma6": 9576.666666666666,
            "ma20": 9552.5,
            "atr14": 136.65688311754542,
            "rsi14": 54.744804464093086,
            "long_signal": true,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 9670.0,
            "ma6": 9576.666666666666,
            "ma20": 9552.5,
            "atr14": 136.65688311754542,
            "rsi14": 54.744804464093086,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 9576.666666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "Y2609",
      "product": "Y",
      "product_name": "豆油",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 8599.0,
        "ma6": 8579.666666666666,
        "ma20": 8502.95,
        "atr14": 81.24703099363632,
        "rsi14": 58.889926127440944,
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
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8599.0,
            "ma6": 8579.666666666666,
            "ma20": 8502.95,
            "atr14": 81.24703099363632,
            "rsi14": 58.889926127440944,
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
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8599.0,
            "ma6": 8579.666666666666,
            "ma20": 8502.95,
            "atr14": 81.24703099363632,
            "rsi14": 58.889926127440944,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 8599.0,
            "ma6": 8579.666666666666,
            "ma20": 8502.95,
            "atr14": 81.24703099363632,
            "rsi14": 58.889926127440944,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 8579.666666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "Y2701",
      "product": "Y",
      "product_name": "豆油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 8593.0,
        "ma6": 8572.0,
        "ma20": 8476.15,
        "atr14": 80.30777678512305,
        "rsi14": 61.027180267505905,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "Y2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8593.0,
            "ma6": 8572.0,
            "ma20": 8476.15,
            "atr14": 80.30777678512305,
            "rsi14": 61.027180267505905,
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
          "symbol": "Y2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8593.0,
            "ma6": 8572.0,
            "ma20": 8476.15,
            "atr14": 80.30777678512305,
            "rsi14": 61.027180267505905,
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
          "symbol": "Y2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 8593.0,
            "ma6": 8572.0,
            "ma20": 8476.15,
            "atr14": 80.30777678512305,
            "rsi14": 61.027180267505905,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 8572.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "OI2609",
      "product": "OI",
      "product_name": "菜油",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 10050.0,
        "ma6": 9963.0,
        "ma20": 9793.3,
        "atr14": 134.98788039721825,
        "rsi14": 60.75728160954093,
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
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10050.0,
            "ma6": 9963.0,
            "ma20": 9793.3,
            "atr14": 134.98788039721825,
            "rsi14": 60.75728160954093,
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
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10050.0,
            "ma6": 9963.0,
            "ma20": 9793.3,
            "atr14": 134.98788039721825,
            "rsi14": 60.75728160954093,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 10050.0,
            "ma6": 9963.0,
            "ma20": 9793.3,
            "atr14": 134.98788039721825,
            "rsi14": 60.75728160954093,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 9963.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "OI2611",
      "product": "OI",
      "product_name": "菜油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 10045.0,
        "ma6": 9954.666666666666,
        "ma20": 9784.8,
        "atr14": 132.71900107817368,
        "rsi14": 61.1464715320885,
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
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10045.0,
            "ma6": 9954.666666666666,
            "ma20": 9784.8,
            "atr14": 132.71900107817368,
            "rsi14": 61.1464715320885,
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
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 10045.0,
            "ma6": 9954.666666666666,
            "ma20": 9784.8,
            "atr14": 132.71900107817368,
            "rsi14": 61.1464715320885,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 10045.0,
            "ma6": 9954.666666666666,
            "ma20": 9784.8,
            "atr14": 132.71900107817368,
            "rsi14": 61.1464715320885,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 9954.666666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "M2609",
      "product": "M",
      "product_name": "豆粕",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 3129.0,
        "ma6": 3070.3333333333335,
        "ma20": 3014.5,
        "atr14": 36.38789615240749,
        "rsi14": 77.36015818981144,
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
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3129.0,
            "ma6": 3070.3333333333335,
            "ma20": 3014.5,
            "atr14": 36.38789615240749,
            "rsi14": 77.36015818981144,
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
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3129.0,
            "ma6": 3070.3333333333335,
            "ma20": 3014.5,
            "atr14": 36.38789615240749,
            "rsi14": 77.36015818981144,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 3129.0,
            "ma6": 3070.3333333333335,
            "ma20": 3014.5,
            "atr14": 36.38789615240749,
            "rsi14": 77.36015818981144,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 3070.3333333333335
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "M2701",
      "product": "M",
      "product_name": "豆粕",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 3184.0,
        "ma6": 3136.0,
        "ma20": 3074.25,
        "atr14": 32.888864745928906,
        "rsi14": 78.40378755689969,
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
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3184.0,
            "ma6": 3136.0,
            "ma20": 3074.25,
            "atr14": 32.888864745928906,
            "rsi14": 78.40378755689969,
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
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3184.0,
            "ma6": 3136.0,
            "ma20": 3074.25,
            "atr14": 32.888864745928906,
            "rsi14": 78.40378755689969,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 3184.0,
            "ma6": 3136.0,
            "ma20": 3074.25,
            "atr14": 32.888864745928906,
            "rsi14": 78.40378755689969,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 3136.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "RM2609",
      "product": "RM",
      "product_name": "菜粕",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 2333.0,
        "ma6": 2307.5,
        "ma20": 2298.4,
        "atr14": 37.298326656105914,
        "rsi14": 55.84732469856743,
        "long_signal": true,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "RM2609",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "OPEN_LONG",
          "execution": "next_trading_day_open",
          "rationale": [
            "completed close crossed above MA20"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2333.0,
            "ma6": 2307.5,
            "ma20": 2298.4,
            "atr14": 37.298326656105914,
            "rsi14": 55.84732469856743,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "RM2609",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2333.0,
            "ma6": 2307.5,
            "ma20": 2298.4,
            "atr14": 37.298326656105914,
            "rsi14": 55.84732469856743,
            "long_signal": true,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 2333.0,
            "ma6": 2307.5,
            "ma20": 2298.4,
            "atr14": 37.298326656105914,
            "rsi14": 55.84732469856743,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 2307.5
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    },
    {
      "symbol": "RM2701",
      "product": "RM",
      "product_name": "菜粕",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-20",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 2271.0,
        "ma6": 2249.6666666666665,
        "ma20": 2240.65,
        "atr14": 26.98644159721434,
        "rsi14": 56.99818990721578,
        "long_signal": true,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "RM2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "flat",
          "action": "OPEN_LONG",
          "execution": "next_trading_day_open",
          "rationale": [
            "completed close crossed above MA20"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2271.0,
            "ma6": 2249.6666666666665,
            "ma20": 2240.65,
            "atr14": 26.98644159721434,
            "rsi14": 56.99818990721578,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "RM2701",
          "period": "daily",
          "market_date": "2026-07-20",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2271.0,
            "ma6": 2249.6666666666665,
            "ma20": 2240.65,
            "atr14": 26.98644159721434,
            "rsi14": 56.99818990721578,
            "long_signal": true,
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
          "market_date": "2026-07-20",
          "position": "short",
          "action": "STOP_EXIT_SHORT",
          "execution": "next_trading_day_open",
          "rationale": [
            "short stop triggered: completed close above MA6"
          ],
          "blocked_direction_after_action": "short",
          "market": {
            "close": 2271.0,
            "ma6": 2249.6666666666665,
            "ma20": 2240.65,
            "atr14": 26.98644159721434,
            "rsi14": 56.99818990721578,
            "long_signal": true,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": true,
            "ma6": 2249.6666666666665
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-07-21",
          "execution_window": "pending",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      }
    }
  ]
};

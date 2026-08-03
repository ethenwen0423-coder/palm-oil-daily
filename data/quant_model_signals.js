window.QUANT_MODEL_SIGNALS = {
  "status": "ok",
  "schema_version": 2,
  "generated_at": "2026-08-03T11:44:38+08:00",
  "market_updated_at": "2026-08-03 11:38",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "validated_mapping",
        "model_scope_label": "成熟模型映射",
        "market": {
          "close": 9281.0,
          "ma6": 9386.833333333334,
          "ma20": 9326.75,
          "atr14": 146.72693002025477,
          "rsi14": 47.23562698832731,
          "long_signal": false,
          "short_signal": true,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "MISSED_ENTRY_SIGNAL",
            "execution": "wait_for_next_confirmed_signal",
            "rationale": [
              "completed close crossed below MA20",
              "the strategy's next-open entry window has already passed; do not chase"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9281.0,
              "ma6": 9386.833333333334,
              "ma20": 9326.75,
              "atr14": 146.72693002025477,
              "rsi14": 47.23562698832731,
              "long_signal": false,
              "short_signal": true,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-08-03",
            "original_confirmed_action": "OPEN_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "P2609",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9281.0,
              "ma6": 9386.833333333334,
              "ma20": 9326.75,
              "atr14": 146.72693002025477,
              "rsi14": 47.23562698832731,
              "long_signal": false,
              "short_signal": true,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9281.0,
              "ma6": 9386.833333333334,
              "ma20": 9326.75,
              "atr14": 146.72693002025477,
              "rsi14": 47.23562698832731,
              "long_signal": false,
              "short_signal": true,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 9386.833333333334
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 9294.0,
          "change": "+0.14%",
          "direction": "↑",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "validated_mapping",
        "model_scope_label": "成熟模型映射",
        "market": {
          "close": 9567.0,
          "ma6": 9668.166666666666,
          "ma20": 9611.4,
          "atr14": 135.66506033541276,
          "rsi14": 47.55011242640676,
          "long_signal": false,
          "short_signal": true,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "MISSED_ENTRY_SIGNAL",
            "execution": "wait_for_next_confirmed_signal",
            "rationale": [
              "completed close crossed below MA20",
              "the strategy's next-open entry window has already passed; do not chase"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9567.0,
              "ma6": 9668.166666666666,
              "ma20": 9611.4,
              "atr14": 135.66506033541276,
              "rsi14": 47.55011242640676,
              "long_signal": false,
              "short_signal": true,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {},
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "intended_execution_date": "2026-08-03",
            "original_confirmed_action": "OPEN_SHORT",
            "execution_window": "missed",
            "data_source": "akshare:futures_zh_daily_sina"
          },
          "long": {
            "status": "ok",
            "symbol": "P2701",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9567.0,
              "ma6": 9668.166666666666,
              "ma20": 9611.4,
              "atr14": 135.66506033541276,
              "rsi14": 47.55011242640676,
              "long_signal": false,
              "short_signal": true,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9567.0,
              "ma6": 9668.166666666666,
              "ma20": 9611.4,
              "atr14": 135.66506033541276,
              "rsi14": 47.55011242640676,
              "long_signal": false,
              "short_signal": true,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 9668.166666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 9580.0,
          "change": "+0.14%",
          "direction": "↑",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 8389.0,
          "ma6": 8453.0,
          "ma20": 8529.55,
          "atr14": 84.5672694250518,
          "rsi14": 42.11525738701254,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8389.0,
              "ma6": 8453.0,
              "ma20": 8529.55,
              "atr14": 84.5672694250518,
              "rsi14": 42.11525738701254,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8389.0,
              "ma6": 8453.0,
              "ma20": 8529.55,
              "atr14": 84.5672694250518,
              "rsi14": 42.11525738701254,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8389.0,
              "ma6": 8453.0,
              "ma20": 8529.55,
              "atr14": 84.5672694250518,
              "rsi14": 42.11525738701254,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 8453.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 8390.0,
          "change": "+0.01%",
          "direction": "↑",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 8406.0,
          "ma6": 8477.666666666666,
          "ma20": 8531.15,
          "atr14": 81.2000016134256,
          "rsi14": 43.23275032138129,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8406.0,
              "ma6": 8477.666666666666,
              "ma20": 8531.15,
              "atr14": 81.2000016134256,
              "rsi14": 43.23275032138129,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8406.0,
              "ma6": 8477.666666666666,
              "ma20": 8531.15,
              "atr14": 81.2000016134256,
              "rsi14": 43.23275032138129,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 8406.0,
              "ma6": 8477.666666666666,
              "ma20": 8531.15,
              "atr14": 81.2000016134256,
              "rsi14": 43.23275032138129,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 8477.666666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 8392.0,
          "change": "-0.17%",
          "direction": "↓",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 9894.0,
          "ma6": 9978.833333333334,
          "ma20": 9953.25,
          "atr14": 139.32373226443107,
          "rsi14": 48.99221039666829,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9894.0,
              "ma6": 9978.833333333334,
              "ma20": 9953.25,
              "atr14": 139.32373226443107,
              "rsi14": 48.99221039666829,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9894.0,
              "ma6": 9978.833333333334,
              "ma20": 9953.25,
              "atr14": 139.32373226443107,
              "rsi14": 48.99221039666829,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9894.0,
              "ma6": 9978.833333333334,
              "ma20": 9953.25,
              "atr14": 139.32373226443107,
              "rsi14": 48.99221039666829,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 9978.833333333334
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 9898.0,
          "change": "+0.04%",
          "direction": "↑",
          "trade_date": "2026-08-03",
          "source": "AkShare + 同花顺问财行情skill",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "OI2701",
        "product": "OI",
        "product_name": "菜油",
        "rank": 2,
        "label": "次主力",
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 9779.0,
          "ma6": 9884.166666666666,
          "ma20": 9854.05,
          "atr14": 132.98851525656437,
          "rsi14": 47.46109550217037,
          "long_signal": false,
          "short_signal": false,
          "bearish_divergence": false,
          "bullish_divergence": false
        },
        "signals": {
          "flat": {
            "status": "ok",
            "symbol": "OI2701",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9779.0,
              "ma6": 9884.166666666666,
              "ma20": 9854.05,
              "atr14": 132.98851525656437,
              "rsi14": 47.46109550217037,
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
            "symbol": "OI2701",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9779.0,
              "ma6": 9884.166666666666,
              "ma20": 9854.05,
              "atr14": 132.98851525656437,
              "rsi14": 47.46109550217037,
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
            "symbol": "OI2701",
            "period": "daily",
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 9779.0,
              "ma6": 9884.166666666666,
              "ma20": 9854.05,
              "atr14": 132.98851525656437,
              "rsi14": 47.46109550217037,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 9884.166666666666
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 9746.0,
          "change": "-0.34%",
          "direction": "↓",
          "trade_date": "2026-08-03",
          "source": "akshare:futures_zh_realtime",
          "unit": "元/吨"
        }
      },
      {
        "symbol": "M2609",
        "product": "M",
        "product_name": "豆粕",
        "rank": 1,
        "label": "主力",
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 3071.0,
          "ma6": 3124.0,
          "ma20": 3092.9,
          "atr14": 41.538781326443484,
          "rsi14": 49.95132889831573,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3071.0,
              "ma6": 3124.0,
              "ma20": 3092.9,
              "atr14": 41.538781326443484,
              "rsi14": 49.95132889831573,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3071.0,
              "ma6": 3124.0,
              "ma20": 3092.9,
              "atr14": 41.538781326443484,
              "rsi14": 49.95132889831573,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3071.0,
              "ma6": 3124.0,
              "ma20": 3092.9,
              "atr14": 41.538781326443484,
              "rsi14": 49.95132889831573,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 3124.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 3075.0,
          "change": "+0.13%",
          "direction": "↑",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 3131.0,
          "ma6": 3181.0,
          "ma20": 3152.2,
          "atr14": 37.30672644020112,
          "rsi14": 50.07592574740127,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3131.0,
              "ma6": 3181.0,
              "ma20": 3152.2,
              "atr14": 37.30672644020112,
              "rsi14": 50.07592574740127,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3131.0,
              "ma6": 3181.0,
              "ma20": 3152.2,
              "atr14": 37.30672644020112,
              "rsi14": 50.07592574740127,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 3131.0,
              "ma6": 3181.0,
              "ma20": 3152.2,
              "atr14": 37.30672644020112,
              "rsi14": 50.07592574740127,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 3181.0
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 3131.0,
          "change": "0.00%",
          "direction": "→",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 2316.0,
          "ma6": 2355.1666666666665,
          "ma20": 2330.9,
          "atr14": 45.40133606425236,
          "rsi14": 48.896233607256185,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2316.0,
              "ma6": 2355.1666666666665,
              "ma20": 2330.9,
              "atr14": 45.40133606425236,
              "rsi14": 48.896233607256185,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2316.0,
              "ma6": 2355.1666666666665,
              "ma20": 2330.9,
              "atr14": 45.40133606425236,
              "rsi14": 48.896233607256185,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2316.0,
              "ma6": 2355.1666666666665,
              "ma20": 2330.9,
              "atr14": 45.40133606425236,
              "rsi14": 48.896233607256185,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 2355.1666666666665
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 2317.0,
          "change": "+0.04%",
          "direction": "↑",
          "trade_date": "2026-08-03",
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
        "market_date": "2026-07-31",
        "data_source": "akshare:futures_zh_daily_sina",
        "bar_completed": true,
        "bar_note": "latest source bar treated as completed",
        "model_scope": "rule_trial",
        "model_scope_label": "同规则试算",
        "market": {
          "close": 2248.0,
          "ma6": 2302.5,
          "ma20": 2274.15,
          "atr14": 34.42472564294062,
          "rsi14": 45.974765196221796,
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
            "market_date": "2026-07-31",
            "position": "flat",
            "action": "WAIT",
            "execution": "none",
            "rationale": [
              "no new MA20 crossover"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2248.0,
              "ma6": 2302.5,
              "ma20": 2274.15,
              "atr14": 34.42472564294062,
              "rsi14": 45.974765196221796,
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
            "market_date": "2026-07-31",
            "position": "long",
            "action": "HOLD_LONG_DATA_NEEDED",
            "execution": "none",
            "rationale": [
              "long ATR activation cannot be evaluated from the supplied position data"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2248.0,
              "ma6": 2302.5,
              "ma20": 2274.15,
              "atr14": 34.42472564294062,
              "rsi14": 45.974765196221796,
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
            "market_date": "2026-07-31",
            "position": "short",
            "action": "HOLD_SHORT",
            "execution": "none",
            "rationale": [
              "short stop and bullish divergence not triggered"
            ],
            "blocked_direction_after_action": "none",
            "market": {
              "close": 2248.0,
              "ma6": 2302.5,
              "ma20": 2274.15,
              "atr14": 34.42472564294062,
              "rsi14": 45.974765196221796,
              "long_signal": false,
              "short_signal": false,
              "bearish_divergence": false,
              "bullish_divergence": false
            },
            "stop_state": {
              "armed": true,
              "close_above_ma6": false,
              "ma6": 2302.5
            },
            "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
            "cost_assumption_one_way": 0.0004,
            "validation_scope": "same_rule_calculation",
            "data_source": "akshare:futures_zh_daily_sina"
          }
        },
        "current_quote": {
          "price": 2242.0,
          "change": "-0.27%",
          "direction": "↓",
          "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "validated_mapping",
      "model_scope_label": "成熟模型映射",
      "market": {
        "close": 9281.0,
        "ma6": 9386.833333333334,
        "ma20": 9326.75,
        "atr14": 146.72693002025477,
        "rsi14": 47.23562698832731,
        "long_signal": false,
        "short_signal": true,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "MISSED_ENTRY_SIGNAL",
          "execution": "wait_for_next_confirmed_signal",
          "rationale": [
            "completed close crossed below MA20",
            "the strategy's next-open entry window has already passed; do not chase"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9281.0,
            "ma6": 9386.833333333334,
            "ma20": 9326.75,
            "atr14": 146.72693002025477,
            "rsi14": 47.23562698832731,
            "long_signal": false,
            "short_signal": true,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-08-03",
          "original_confirmed_action": "OPEN_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "P2609",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9281.0,
            "ma6": 9386.833333333334,
            "ma20": 9326.75,
            "atr14": 146.72693002025477,
            "rsi14": 47.23562698832731,
            "long_signal": false,
            "short_signal": true,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9281.0,
            "ma6": 9386.833333333334,
            "ma20": 9326.75,
            "atr14": 146.72693002025477,
            "rsi14": 47.23562698832731,
            "long_signal": false,
            "short_signal": true,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 9386.833333333334
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 9294.0,
        "change": "+0.14%",
        "direction": "↑",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "validated_mapping",
      "model_scope_label": "成熟模型映射",
      "market": {
        "close": 9567.0,
        "ma6": 9668.166666666666,
        "ma20": 9611.4,
        "atr14": 135.66506033541276,
        "rsi14": 47.55011242640676,
        "long_signal": false,
        "short_signal": true,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "MISSED_ENTRY_SIGNAL",
          "execution": "wait_for_next_confirmed_signal",
          "rationale": [
            "completed close crossed below MA20",
            "the strategy's next-open entry window has already passed; do not chase"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9567.0,
            "ma6": 9668.166666666666,
            "ma20": 9611.4,
            "atr14": 135.66506033541276,
            "rsi14": 47.55011242640676,
            "long_signal": false,
            "short_signal": true,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {},
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "intended_execution_date": "2026-08-03",
          "original_confirmed_action": "OPEN_SHORT",
          "execution_window": "missed",
          "data_source": "akshare:futures_zh_daily_sina"
        },
        "long": {
          "status": "ok",
          "symbol": "P2701",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9567.0,
            "ma6": 9668.166666666666,
            "ma20": 9611.4,
            "atr14": 135.66506033541276,
            "rsi14": 47.55011242640676,
            "long_signal": false,
            "short_signal": true,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9567.0,
            "ma6": 9668.166666666666,
            "ma20": 9611.4,
            "atr14": 135.66506033541276,
            "rsi14": 47.55011242640676,
            "long_signal": false,
            "short_signal": true,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 9668.166666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 9580.0,
        "change": "+0.14%",
        "direction": "↑",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 8389.0,
        "ma6": 8453.0,
        "ma20": 8529.55,
        "atr14": 84.5672694250518,
        "rsi14": 42.11525738701254,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8389.0,
            "ma6": 8453.0,
            "ma20": 8529.55,
            "atr14": 84.5672694250518,
            "rsi14": 42.11525738701254,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8389.0,
            "ma6": 8453.0,
            "ma20": 8529.55,
            "atr14": 84.5672694250518,
            "rsi14": 42.11525738701254,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8389.0,
            "ma6": 8453.0,
            "ma20": 8529.55,
            "atr14": 84.5672694250518,
            "rsi14": 42.11525738701254,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 8453.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 8390.0,
        "change": "+0.01%",
        "direction": "↑",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 8406.0,
        "ma6": 8477.666666666666,
        "ma20": 8531.15,
        "atr14": 81.2000016134256,
        "rsi14": 43.23275032138129,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8406.0,
            "ma6": 8477.666666666666,
            "ma20": 8531.15,
            "atr14": 81.2000016134256,
            "rsi14": 43.23275032138129,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8406.0,
            "ma6": 8477.666666666666,
            "ma20": 8531.15,
            "atr14": 81.2000016134256,
            "rsi14": 43.23275032138129,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 8406.0,
            "ma6": 8477.666666666666,
            "ma20": 8531.15,
            "atr14": 81.2000016134256,
            "rsi14": 43.23275032138129,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 8477.666666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 8392.0,
        "change": "-0.17%",
        "direction": "↓",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 9894.0,
        "ma6": 9978.833333333334,
        "ma20": 9953.25,
        "atr14": 139.32373226443107,
        "rsi14": 48.99221039666829,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9894.0,
            "ma6": 9978.833333333334,
            "ma20": 9953.25,
            "atr14": 139.32373226443107,
            "rsi14": 48.99221039666829,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9894.0,
            "ma6": 9978.833333333334,
            "ma20": 9953.25,
            "atr14": 139.32373226443107,
            "rsi14": 48.99221039666829,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9894.0,
            "ma6": 9978.833333333334,
            "ma20": 9953.25,
            "atr14": 139.32373226443107,
            "rsi14": 48.99221039666829,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 9978.833333333334
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 9898.0,
        "change": "+0.04%",
        "direction": "↑",
        "trade_date": "2026-08-03",
        "source": "AkShare + 同花顺问财行情skill",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "OI2701",
      "product": "OI",
      "product_name": "菜油",
      "rank": 2,
      "label": "次主力",
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 9779.0,
        "ma6": 9884.166666666666,
        "ma20": 9854.05,
        "atr14": 132.98851525656437,
        "rsi14": 47.46109550217037,
        "long_signal": false,
        "short_signal": false,
        "bearish_divergence": false,
        "bullish_divergence": false
      },
      "signals": {
        "flat": {
          "status": "ok",
          "symbol": "OI2701",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9779.0,
            "ma6": 9884.166666666666,
            "ma20": 9854.05,
            "atr14": 132.98851525656437,
            "rsi14": 47.46109550217037,
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
          "symbol": "OI2701",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9779.0,
            "ma6": 9884.166666666666,
            "ma20": 9854.05,
            "atr14": 132.98851525656437,
            "rsi14": 47.46109550217037,
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
          "symbol": "OI2701",
          "period": "daily",
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 9779.0,
            "ma6": 9884.166666666666,
            "ma20": 9854.05,
            "atr14": 132.98851525656437,
            "rsi14": 47.46109550217037,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 9884.166666666666
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 9746.0,
        "change": "-0.34%",
        "direction": "↓",
        "trade_date": "2026-08-03",
        "source": "akshare:futures_zh_realtime",
        "unit": "元/吨"
      }
    },
    {
      "symbol": "M2609",
      "product": "M",
      "product_name": "豆粕",
      "rank": 1,
      "label": "主力",
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 3071.0,
        "ma6": 3124.0,
        "ma20": 3092.9,
        "atr14": 41.538781326443484,
        "rsi14": 49.95132889831573,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3071.0,
            "ma6": 3124.0,
            "ma20": 3092.9,
            "atr14": 41.538781326443484,
            "rsi14": 49.95132889831573,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3071.0,
            "ma6": 3124.0,
            "ma20": 3092.9,
            "atr14": 41.538781326443484,
            "rsi14": 49.95132889831573,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3071.0,
            "ma6": 3124.0,
            "ma20": 3092.9,
            "atr14": 41.538781326443484,
            "rsi14": 49.95132889831573,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 3124.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 3075.0,
        "change": "+0.13%",
        "direction": "↑",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 3131.0,
        "ma6": 3181.0,
        "ma20": 3152.2,
        "atr14": 37.30672644020112,
        "rsi14": 50.07592574740127,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3131.0,
            "ma6": 3181.0,
            "ma20": 3152.2,
            "atr14": 37.30672644020112,
            "rsi14": 50.07592574740127,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3131.0,
            "ma6": 3181.0,
            "ma20": 3152.2,
            "atr14": 37.30672644020112,
            "rsi14": 50.07592574740127,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 3131.0,
            "ma6": 3181.0,
            "ma20": 3152.2,
            "atr14": 37.30672644020112,
            "rsi14": 50.07592574740127,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 3181.0
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 3131.0,
        "change": "0.00%",
        "direction": "→",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 2316.0,
        "ma6": 2355.1666666666665,
        "ma20": 2330.9,
        "atr14": 45.40133606425236,
        "rsi14": 48.896233607256185,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2316.0,
            "ma6": 2355.1666666666665,
            "ma20": 2330.9,
            "atr14": 45.40133606425236,
            "rsi14": 48.896233607256185,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2316.0,
            "ma6": 2355.1666666666665,
            "ma20": 2330.9,
            "atr14": 45.40133606425236,
            "rsi14": 48.896233607256185,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2316.0,
            "ma6": 2355.1666666666665,
            "ma20": 2330.9,
            "atr14": 45.40133606425236,
            "rsi14": 48.896233607256185,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 2355.1666666666665
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 2317.0,
        "change": "+0.04%",
        "direction": "↑",
        "trade_date": "2026-08-03",
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
      "market_date": "2026-07-31",
      "data_source": "akshare:futures_zh_daily_sina",
      "bar_completed": true,
      "bar_note": "latest source bar treated as completed",
      "model_scope": "rule_trial",
      "model_scope_label": "同规则试算",
      "market": {
        "close": 2248.0,
        "ma6": 2302.5,
        "ma20": 2274.15,
        "atr14": 34.42472564294062,
        "rsi14": 45.974765196221796,
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
          "market_date": "2026-07-31",
          "position": "flat",
          "action": "WAIT",
          "execution": "none",
          "rationale": [
            "no new MA20 crossover"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2248.0,
            "ma6": 2302.5,
            "ma20": 2274.15,
            "atr14": 34.42472564294062,
            "rsi14": 45.974765196221796,
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
          "market_date": "2026-07-31",
          "position": "long",
          "action": "HOLD_LONG_DATA_NEEDED",
          "execution": "none",
          "rationale": [
            "long ATR activation cannot be evaluated from the supplied position data"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2248.0,
            "ma6": 2302.5,
            "ma20": 2274.15,
            "atr14": 34.42472564294062,
            "rsi14": 45.974765196221796,
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
          "market_date": "2026-07-31",
          "position": "short",
          "action": "HOLD_SHORT",
          "execution": "none",
          "rationale": [
            "short stop and bullish divergence not triggered"
          ],
          "blocked_direction_after_action": "none",
          "market": {
            "close": 2248.0,
            "ma6": 2302.5,
            "ma20": 2274.15,
            "atr14": 34.42472564294062,
            "rsi14": 45.974765196221796,
            "long_signal": false,
            "short_signal": false,
            "bearish_divergence": false,
            "bullish_divergence": false
          },
          "stop_state": {
            "armed": true,
            "close_above_ma6": false,
            "ma6": 2302.5
          },
          "take_profit": "long: 20-day price high without RSI confirmation; short: reverse",
          "cost_assumption_one_way": 0.0004,
          "validation_scope": "same_rule_calculation",
          "data_source": "akshare:futures_zh_daily_sina"
        }
      },
      "current_quote": {
        "price": 2242.0,
        "change": "-0.27%",
        "direction": "↓",
        "trade_date": "2026-08-03",
        "source": "akshare:futures_zh_realtime",
        "unit": "元/吨"
      }
    }
  ]
};

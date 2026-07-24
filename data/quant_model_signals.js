window.QUANT_MODEL_SIGNALS = {
  "status": "error",
  "schema_version": 2,
  "generated_at": "2026-07-24T16:47:39+08:00",
  "market_updated_at": "2026-07-24 08:29",
  "market_update_session": "morning",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for P2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=P2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 9534.0,
          "change": "+0.20%",
          "direction": "↑",
          "trade_date": "2026-07-24",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for P2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=P2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 9812.0,
          "change": "+0.17%",
          "direction": "↑",
          "trade_date": "2026-07-24",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for Y2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=Y2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 8582.0,
          "change": "+0.43%",
          "direction": "↑",
          "trade_date": "2026-07-24",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for Y2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=Y2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 8596.0,
          "change": "+0.40%",
          "direction": "↑",
          "trade_date": "2026-07-24",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for OI2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=OI2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 10170.0,
          "change": "-0.05%",
          "direction": "↓",
          "trade_date": "2026-07-23",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for OI2611: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=OI2611&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 10169.0,
          "change": "-0.04%",
          "direction": "↓",
          "trade_date": "2026-07-23",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for M2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=M2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 3172.0,
          "change": "-0.09%",
          "direction": "↓",
          "trade_date": "2026-07-24",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for M2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=M2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 3228.0,
          "change": "-0.15%",
          "direction": "↓",
          "trade_date": "2026-07-24",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for RM2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=RM2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 2375.0,
          "change": "+0.64%",
          "direction": "↑",
          "trade_date": "2026-07-23",
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
        "status": "error",
        "message": "market data request failed after 2 attempts for RM2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=RM2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
        "current_quote": {
          "price": 2333.0,
          "change": "+0.56%",
          "direction": "↑",
          "trade_date": "2026-07-23",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for P2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=P2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 9534.0,
        "change": "+0.20%",
        "direction": "↑",
        "trade_date": "2026-07-24",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for P2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=P2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 9812.0,
        "change": "+0.17%",
        "direction": "↑",
        "trade_date": "2026-07-24",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for Y2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=Y2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 8582.0,
        "change": "+0.43%",
        "direction": "↑",
        "trade_date": "2026-07-24",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for Y2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=Y2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 8596.0,
        "change": "+0.40%",
        "direction": "↑",
        "trade_date": "2026-07-24",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for OI2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=OI2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 10170.0,
        "change": "-0.05%",
        "direction": "↓",
        "trade_date": "2026-07-23",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for OI2611: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=OI2611&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 10169.0,
        "change": "-0.04%",
        "direction": "↓",
        "trade_date": "2026-07-23",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for M2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=M2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 3172.0,
        "change": "-0.09%",
        "direction": "↓",
        "trade_date": "2026-07-24",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for M2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=M2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 3228.0,
        "change": "-0.15%",
        "direction": "↓",
        "trade_date": "2026-07-24",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for RM2609: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=RM2609&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 2375.0,
        "change": "+0.64%",
        "direction": "↑",
        "trade_date": "2026-07-23",
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
      "status": "error",
      "message": "market data request failed after 2 attempts for RM2701: HTTPSConnectionPool(host='stock2.finance.sina.com.cn', port=443): Max retries exceeded with url: /futures/api/jsonp.php/var%20_V21052021_4_12=/InnerFuturesNewService.getDailyKLine?symbol=RM2701&type=2021_04_12 (Caused by NameResolutionError(\"HTTPSConnection(host='stock2.finance.sina.com.cn', port=443): Failed to resolve 'stock2.finance.sina.com.cn' ([Errno 8] nodename nor servname provided, or not known)\"))",
      "current_quote": {
        "price": 2333.0,
        "change": "+0.56%",
        "direction": "↑",
        "trade_date": "2026-07-23",
        "source": "akshare:futures_zh_realtime",
        "unit": "元/吨"
      }
    }
  ]
};

module.exports = {
  "updated_at": "2026-08-31 09:40",
  "update_session": "morning",
  "timezone": "Asia/Shanghai",
  "source": "futures-oil-daily 最新快照：source_runs/2026-08-31-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
  "fundamental_mode": "refresh",
  "fundamental_updated_at": "2026-08-31 09:40",
  "fundamental_update_session": "morning",
  "contract_selector_skill": "contract_selector_skill",
  "contract_discovery_skill": "contract_discovery_skill",
  "contract_discovery_month": "2026-08",
  "contract_discovery_warnings": [],
  "review_learning_warning": "",
  "review_learning_repeated_errors": {},
  "market_references": {
    "malaysia_fcpo": {
      "label": "马来 BMD FCPO",
      "location": "马来西亚",
      "price": "4890",
      "change": "+1.35%",
      "unit": "林吉特/吨",
      "updated_at": "2026-08-28T17:59:59",
      "source": "tradingview:MYX:FCPO1!"
    },
    "indonesia_cpotr": {
      "label": "印尼 ICDX CPOTR",
      "location": "雅加达",
      "price": "16550",
      "change": "-0.81%",
      "unit": "印尼盾/公斤",
      "updated_at": "2026-08-28",
      "source": "ICDX 官方历史价格接口"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1399.85",
      "change": "+0.18%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-08-28T15:19",
      "source": "ncdex:live-spot"
    }
  },
  "contracts": [
    {
      "symbol": "P2701",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2701",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "10171",
      "change": "+1.25%",
      "volume": "73.90 万手",
      "open_interest": "57.94 万手",
      "direction": "↑",
      "open": "10015",
      "high": "10225",
      "low": "9952",
      "preclose": "10045",
      "settle": "10089",
      "trade_date": "2026-08-28",
      "source": "akshare:futures_zh_daily_sina",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 63.1,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 65.8,
        "money_flow": 60.7,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前观点为偏多，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+1.25%；成交量较前快照+215.84%；持仓较前快照+1.86%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10171 先看与 MA20 9871.70、MA60 9684.97 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10292 和统计通道上轨 10280.01，下方关注20日区间下沿 9515 和统计通道下轨 9463.39。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 137.29，说明观察位需要给盘中噪音留出空间。综合评分 63.10 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+1.35%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 79.68，豆棕价差 -1206。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 10171；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10676.51",
        "stop_loss": "下方观察位 9800.12",
        "upper_watch": "10676.51",
        "lower_watch": "9800.12",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "P2705",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2705",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "10505",
      "change": "+1.60%",
      "volume": "14.45 万手",
      "open_interest": "20.43 万手",
      "direction": "↑",
      "open": "10303",
      "high": "10550",
      "low": "10249",
      "preclose": "10340",
      "settle": "10416",
      "trade_date": "2026-08-28",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 52.6,
        "technical": 50.0,
        "fundamental": 50.0,
        "driver": 65.8,
        "money_flow": 39.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示数据不足，按中性处理，主要信号为技术数据不足。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+1.60%；成交量较前快照-38.26%；持仓较前快照-64.08%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10505 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 50，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：技术数据不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 需进一步核验，说明观察位需要给盘中噪音留出空间。综合评分 52.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+1.35%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 79.68，豆棕价差 -1206。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 10505；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10733.17 / 下方观察位 10276.83",
        "stop_loss": "下方观察位 10276.83",
        "upper_watch": "10733.17",
        "lower_watch": "10276.83",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "Y2701",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2701",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "8965",
      "change": "+1.55%",
      "volume": "49.91 万手",
      "open_interest": "77.24 万手",
      "direction": "↑",
      "open": "8824",
      "high": "9017",
      "low": "8776",
      "preclose": "8828",
      "settle": "8908",
      "trade_date": "2026-08-28",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 66.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 66.2,
        "money_flow": 77.0,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前观点为偏多，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、突破20日区间上沿。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+1.55%；成交量较前快照+261.84%；持仓较前快照+6.49%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8965 先看与 MA20 8615.85、MA60 8498.53 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8899 和统计通道上轨 8977.53，下方关注20日区间下沿 8371 和统计通道下轨 8254.17。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 106.36，说明观察位需要给盘中噪音留出空间。综合评分 66.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+1.35%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 121.74 和豆棕价差 -1206。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 8965；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9342.85",
        "stop_loss": "下方观察位 8596.10",
        "upper_watch": "9342.85",
        "lower_watch": "8596.10",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "Y2705",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2705",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "8788",
      "change": "+1.96%",
      "volume": "10.66 万手",
      "open_interest": "24.75 万手",
      "direction": "↑",
      "open": "8632",
      "high": "8847",
      "low": "8572",
      "preclose": "8619",
      "settle": "8719",
      "trade_date": "2026-08-28",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 55.2,
        "technical": 50.0,
        "fundamental": 50.0,
        "driver": 66.2,
        "money_flow": 51.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示数据不足，按中性处理，主要信号为技术数据不足。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+1.96%；成交量较前快照-22.72%；持仓较前快照-65.87%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8788 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 50，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：技术数据不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 需进一步核验，说明观察位需要给盘中噪音留出空间。综合评分 55.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+1.35%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 121.74 和豆棕价差 -1206。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 8788；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8978.88 / 下方观察位 8597.12",
        "stop_loss": "下方观察位 8597.12",
        "upper_watch": "8978.88",
        "lower_watch": "8597.12",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "OI2611",
      "product": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2611",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "10333",
      "change": "+0.35%",
      "volume": "28.25 万手",
      "open_interest": "29.49 万手",
      "direction": "↑",
      "open": "10279",
      "high": "10398",
      "low": "10198",
      "preclose": "10297",
      "settle": "10301",
      "trade_date": "2026-08-28",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 58.2,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 50.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+0.35%；成交量较前快照+198.76%；持仓较前快照-3.77%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10333 先看与 MA20 10259.55、MA60 9991.80 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10723 和统计通道上轨 10669.96，下方关注20日区间下沿 9851 和统计通道下轨 9849.14。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 156.79，说明观察位需要给盘中噪音留出空间。综合评分 58.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+1.35%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 42.20，豆棕价差 -1206。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 10333；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10759.64 / 下方观察位 9761.32",
        "stop_loss": "下方观察位 9761.32",
        "upper_watch": "10759.64",
        "lower_watch": "9761.32",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "OI2701",
      "product": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "10201",
      "change": "+0.72%",
      "volume": "17.09 万手",
      "open_interest": "26.61 万手",
      "direction": "↑",
      "open": "10123",
      "high": "10271",
      "low": "10051",
      "preclose": "10128",
      "settle": "10167",
      "trade_date": "2026-08-28",
      "source": "akshare:futures_zh_daily_sina",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 57.8,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 47.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+0.72%；成交量较前快照+80.74%；持仓较前快照-13.15%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10201 先看与 MA20 10070.10、MA60 9881.35 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10474 和统计通道上轨 10419.34，下方关注20日区间下沿 9683 和统计通道下轨 9720.86。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 146.50，说明观察位需要给盘中噪音留出空间。综合评分 57.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+1.35%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 42.20，豆棕价差 -1206。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 10201；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10519.20 / 下方观察位 9637.06",
        "stop_loss": "下方观察位 9637.06",
        "upper_watch": "10519.20",
        "lower_watch": "9637.06",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "M2701",
      "product": "M",
      "name": "豆粕",
      "market": "DCE",
      "contract": "M2701",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "3340",
      "change": "-0.45%",
      "volume": "165.72 万手",
      "open_interest": "274.48 万手",
      "direction": "↓",
      "open": "3353",
      "high": "3370",
      "low": "3318",
      "preclose": "3355",
      "settle": "3344",
      "trade_date": "2026-08-28",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 60.4,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 48.2,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅-0.45%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3340 先看与 MA20 3202.30、MA60 3120.53 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3356 和统计通道上轨 3344.37，下方关注20日区间下沿 3106 和统计通道下轨 3060.23。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 43.71，说明观察位需要给盘中噪音留出空间。综合评分 60.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +1.35%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：基本面暂无强新增驱动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 3340；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3381.00 / 下方观察位 3081.00",
        "stop_loss": "下方观察位 3081.00",
        "upper_watch": "3381.00",
        "lower_watch": "3081.00",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "M2705",
      "product": "M",
      "name": "豆粕",
      "market": "DCE",
      "contract": "M2705",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "3018",
      "change": "-0.26%",
      "volume": "36.66 万手",
      "open_interest": "85.95 万手",
      "direction": "↓",
      "open": "3018",
      "high": "3044",
      "low": "2994",
      "preclose": "3026",
      "settle": "3021",
      "trade_date": "2026-08-28",
      "source": "akshare:futures_zh_daily_sina",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 54.2,
        "technical": 50.0,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 48.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示数据不足，按中性处理，主要信号为技术数据不足。基本面背景看基本面暂无强新增驱动；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅-0.26%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3018 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 50，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：技术数据不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 需进一步核验，说明观察位需要给盘中噪音留出空间。综合评分 54.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +1.35%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：基本面暂无强新增驱动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 3018；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3083.55 / 下方观察位 2952.45",
        "stop_loss": "下方观察位 2952.45",
        "upper_watch": "3083.55",
        "lower_watch": "2952.45",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "RM2611",
      "product": "RM",
      "name": "菜粕",
      "market": "CZCE",
      "contract": "RM2611",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "2339",
      "change": "-0.38%",
      "volume": "73.88 万手",
      "open_interest": "65.79 万手",
      "direction": "↓",
      "open": "2348",
      "high": "2355",
      "low": "2324",
      "preclose": "2348",
      "settle": "2341",
      "trade_date": "2026-08-28",
      "source": "akshare:futures_zh_daily_sina",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 60.4,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 48.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列。基本面背景看基本面暂无强新增驱动；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅-0.38%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2339 先看与 MA20 2227.40、MA60 2214.57 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2359 和统计通道上轨 2339.12，下方关注20日区间下沿 2163 和统计通道下轨 2115.68。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 37.71，说明观察位需要给盘中噪音留出空间。综合评分 60.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +1.35%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：基本面暂无强新增驱动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 2339；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2380.57 / 下方观察位 2141.43",
        "stop_loss": "下方观察位 2141.43",
        "upper_watch": "2380.57",
        "lower_watch": "2141.43",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "RM2701",
      "product": "RM",
      "name": "菜粕",
      "market": "CZCE",
      "contract": "RM2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "2366",
      "change": "-0.46%",
      "volume": "35.36 万手",
      "open_interest": "51.31 万手",
      "direction": "↓",
      "open": "2377",
      "high": "2386",
      "low": "2355",
      "preclose": "2377",
      "settle": "2372",
      "trade_date": "2026-08-28",
      "source": "akshare:futures_zh_daily_sina",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "非夜盘刷新发现未来交易日 2026-08-31；已锁定最近完整收盘 2026-08-28。",
      "score": {
        "total": 60.3,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 48.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、处于统计区间上沿外侧。基本面背景看基本面暂无强新增驱动；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅-0.46%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2366 先看与 MA20 2269.90、MA60 2254.50 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、处于统计区间上沿外侧。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2378 和统计通道上轨 2357.65，下方关注20日区间下沿 2217 和统计通道下轨 2182.15。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 31.07，说明观察位需要给盘中噪音留出空间。综合评分 60.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +1.35%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：基本面暂无强新增驱动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 2366；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2395.77 / 下方观察位 2199.23",
        "stop_loss": "下方观察位 2199.23",
        "upper_watch": "2395.77",
        "lower_watch": "2199.23",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "FCPO",
      "product": "FCPO",
      "name": "马棕油",
      "market": "BMD",
      "contract": "FCPOX2026",
      "price": "4890",
      "unit": "林吉特/吨",
      "change": "+1.35%",
      "change_basis": "intraday_vs_open",
      "volume": "3.53 万手",
      "open_interest": "9.94 万手",
      "direction": "↑",
      "open": "4825",
      "high": "4908",
      "low": "4799",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-08-28",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "海外产地价格使用交易所或公开行情源，仅作棕榈油跨市场参考。",
      "score": {
        "total": 57.0,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 55.4,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前观点为震荡偏强，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅+1.35%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 4890 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 109，说明观察位需要给盘中噪音留出空间。综合评分 57 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +1.35%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：外盘参考合约，国内基本面因子不直接套用。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 4890；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 5126.75",
        "stop_loss": "下方观察位 4639.30",
        "upper_watch": "5126.75",
        "lower_watch": "4639.30",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "CPOTR",
      "product": "CPOTR",
      "name": "印尼棕榈油",
      "market": "ICDX",
      "contract": "CPOTR SEP26",
      "price": "16550",
      "unit": "印尼盾/公斤",
      "change": "-0.81%",
      "change_basis": "vs_previous_settlement_ydsp",
      "volume": "100 手",
      "open_interest": "需进一步核验",
      "direction": "↓",
      "open": "16550",
      "high": "16550",
      "low": "16550",
      "preclose": "16685",
      "settle": "16550",
      "trade_date": "2026-08-28",
      "source": "ICDX 官方历史价格接口",
      "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
      "verification": "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。",
      "score": {
        "total": 52.3,
        "technical": 44,
        "fundamental": 50.0,
        "driver": 64.9,
        "money_flow": 46.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "印尼棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+1.35%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+0.53%（24小时新增）；资金看当日涨跌幅-0.81%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 16550 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 165.50，说明观察位需要给盘中噪音留出空间。综合评分 52.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +1.35%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性背景处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：外盘参考合约，国内基本面因子不直接套用。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 16550；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 16909.47 / 下方观察位 16190.53",
        "stop_loss": "下方观察位 16190.53",
        "upper_watch": "16909.47",
        "lower_watch": "16190.53",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    }
  ],
  "watchlist_options": [
    {
      "value": "P2701",
      "label": "P2701",
      "display": "棕榈油 P2701 主力",
      "name": "棕榈油",
      "contract": "P2701",
      "product": "P",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "P2705",
      "label": "P2705",
      "display": "棕榈油 P2705 次主力",
      "name": "棕榈油",
      "contract": "P2705",
      "product": "P",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "Y2701",
      "label": "Y2701",
      "display": "豆油 Y2701 主力",
      "name": "豆油",
      "contract": "Y2701",
      "product": "Y",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "Y2705",
      "label": "Y2705",
      "display": "豆油 Y2705 次主力",
      "name": "豆油",
      "contract": "Y2705",
      "product": "Y",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "OI2611",
      "label": "OI2611",
      "display": "菜油 OI2611 主力",
      "name": "菜油",
      "contract": "OI2611",
      "product": "OI",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "OI2701",
      "label": "OI2701",
      "display": "菜油 OI2701 次主力",
      "name": "菜油",
      "contract": "OI2701",
      "product": "OI",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "M2701",
      "label": "M2701",
      "display": "豆粕 M2701 主力",
      "name": "豆粕",
      "contract": "M2701",
      "product": "M",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "M2705",
      "label": "M2705",
      "display": "豆粕 M2705 次主力",
      "name": "豆粕",
      "contract": "M2705",
      "product": "M",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "RM2611",
      "label": "RM2611",
      "display": "菜粕 RM2611 主力",
      "name": "菜粕",
      "contract": "RM2611",
      "product": "RM",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "RM2701",
      "label": "RM2701",
      "display": "菜粕 RM2701 次主力",
      "name": "菜粕",
      "contract": "RM2701",
      "product": "RM",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "FCPO",
      "label": "FCPOX2026",
      "display": "马棕油 FCPOX2026",
      "name": "马棕油",
      "contract": "FCPOX2026",
      "product": "FCPO",
      "rank": null,
      "contract_label": null
    },
    {
      "value": "CPOTR",
      "label": "CPOTR SEP26",
      "display": "印尼棕榈油 CPOTR SEP26",
      "name": "印尼棕榈油",
      "contract": "CPOTR SEP26",
      "product": "CPOTR",
      "rank": null,
      "contract_label": null
    }
  ]
};

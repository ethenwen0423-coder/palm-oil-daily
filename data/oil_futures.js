window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-23 12:41",
  "update_session": "midday",
  "timezone": "Asia/Shanghai",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-23-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
  "contract_selector_skill": "contract_selector_skill",
  "contract_discovery_skill": "contract_discovery_skill",
  "contract_discovery_month": "2026-07",
  "contract_discovery_warnings": [],
  "review_learning_warning": "",
  "review_learning_repeated_errors": {},
  "market_references": {
    "malaysia_fcpo": {
      "label": "马来 BMD FCPO",
      "location": "马来西亚",
      "price": "4621",
      "change": "+0.28%",
      "unit": "林吉特/吨",
      "updated_at": "2026-07-22T17:57:50",
      "source": "tradingview:MYX:FCPO1!"
    },
    "indonesia_cpotr": {
      "label": "印尼 ICDX CPOTR",
      "location": "雅加达",
      "price": "16145",
      "change": "-0.95%",
      "unit": "印尼盾/公斤",
      "updated_at": "2026-07-22",
      "source": "ICDX 官方历史价格接口"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1368.10",
      "change": "+0.01%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-07-22T15:25",
      "source": "ncdex:live-spot"
    }
  },
  "contracts": [
    {
      "symbol": "P2609",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "9494",
      "change": "+2.64%",
      "volume": "67.17 万手",
      "open_interest": "44.79 万手",
      "direction": "↑",
      "open": "9260",
      "high": "9505",
      "low": "9260",
      "preclose": "9250",
      "settle": "9251",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9494 / 行情skill 9494",
      "score": {
        "total": 68.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 75.2,
        "money_flow": 73.2,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前观点为偏多，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+2.64%；成交量较前快照+390.00%；持仓较前快照-2.59%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9494 先看与 MA20 9280.25、MA60 9451.58 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9439 和统计通道上轨 9459.13，下方关注20日区间下沿 9028 和统计通道下轨 9101.37。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 149.21，说明观察位需要给盘中噪音留出空间。综合评分 68.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.28%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 80.24，豆棕价差 -887。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 9494；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9967.50",
        "stop_loss": "下方观察位 9167.02",
        "upper_watch": "9967.50",
        "lower_watch": "9167.02",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "P2701",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "9777",
      "change": "+2.45%",
      "volume": "19.15 万手",
      "open_interest": "24.78 万手",
      "direction": "↑",
      "open": "9563",
      "high": "9799",
      "low": "9556",
      "preclose": "9543",
      "settle": "9546",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9777 / 行情skill 9777",
      "score": {
        "total": 67.4,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 75.2,
        "money_flow": 67.8,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前观点为偏多，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+2.45%；成交量较前快照+39.69%；持仓较前快照-46.11%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9777 先看与 MA20 9558.30、MA60 9659.28 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9715 和统计通道上轨 9730.30，下方关注20日区间下沿 9313 和统计通道下轨 9386.30。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 137.64，说明观察位需要给盘中噪音留出空间。综合评分 67.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.28%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 80.24，豆棕价差 -887。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 9777；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10227.41",
        "stop_loss": "下方观察位 9460.94",
        "upper_watch": "10227.41",
        "lower_watch": "9460.94",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "Y2609",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "8542",
      "change": "+1.18%",
      "volume": "22.10 万手",
      "open_interest": "43.50 万手",
      "direction": "↑",
      "open": "8453",
      "high": "8552",
      "low": "8445",
      "preclose": "8442",
      "settle": "8481",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8542 / 行情skill 8542；涨跌幅口径不同：AkShare +1.18% / 行情skill +0.72%",
      "score": {
        "total": 60.3,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 74.1,
        "money_flow": 46.7,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.18%；成交量较前快照+111.94%；持仓较前快照-8.50%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8542 先看与 MA20 8519.85、MA60 8493.25 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8657 和统计通道上轨 8675.64，下方关注20日区间下沿 8302 和统计通道下轨 8364.06。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 83.50，说明观察位需要给盘中噪音留出空间。综合评分 60.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.28%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 138.88 和豆棕价差 -887。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 8542；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8723.36 / 下方观察位 8316.30",
        "stop_loss": "下方观察位 8316.30",
        "upper_watch": "8723.36",
        "lower_watch": "8316.30",
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
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "8560",
      "change": "+1.12%",
      "volume": "9.58 万手",
      "open_interest": "33.86 万手",
      "direction": "↑",
      "open": "8485",
      "high": "8564",
      "low": "8461",
      "preclose": "8465",
      "settle": "8488",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8560 / 行情skill 8560；涨跌幅口径不同：AkShare +1.12% / 行情skill +0.85%",
      "score": {
        "total": 57.7,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 74.1,
        "money_flow": 33.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.12%；成交量较前快照-8.12%；持仓较前快照-28.79%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8560 先看与 MA20 8498.90、MA60 8462.65 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8629 和统计通道上轨 8679.39，下方关注20日区间下沿 8264 和统计通道下轨 8318.41。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 80.93，说明观察位需要给盘中噪音留出空间。综合评分 57.70 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.28%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 138.88 和豆棕价差 -887。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8560；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8725.68 / 下方观察位 8272.12",
        "stop_loss": "下方观察位 8272.12",
        "upper_watch": "8725.68",
        "lower_watch": "8272.12",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "OI2609",
      "product": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "10118",
      "change": "+1.70%",
      "volume": "23.04 万手",
      "open_interest": "35.01 万手",
      "direction": "↑",
      "open": "9964",
      "high": "10128",
      "low": "9947",
      "preclose": "9949",
      "settle": "9976",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 10118 / 行情skill 10118；涨跌幅口径不同：AkShare +1.70% / 行情skill +1.42%",
      "score": {
        "total": 65.9,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 65.6,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前观点为偏多，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、突破20日区间上沿。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.70%；成交量较前快照+100.80%；持仓较前快照+2.04%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10118 先看与 MA20 9830.60、MA60 9821.38 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10109 和统计通道上轨 10170.18，下方关注20日区间下沿 9453 和统计通道下轨 9491.02。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 126.43，说明观察位需要给盘中噪音留出空间。综合评分 65.90 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.28%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 48.45，豆棕价差 -887。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 10118；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10572.71",
        "stop_loss": "下方观察位 9742.22",
        "upper_watch": "10572.71",
        "lower_watch": "9742.22",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
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
      "price": "10040",
      "change": "+1.70%",
      "volume": "4.79 万手",
      "open_interest": "10.04 万手",
      "direction": "↑",
      "open": "9885",
      "high": "10052",
      "low": "9872",
      "preclose": "9872",
      "settle": "9887",
      "trade_date": "2026-07-23",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 61.3,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 42.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.70%；成交量较前快照-58.29%；持仓较前快照-70.74%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10040 先看与 MA20 9743.30、MA60 9776.55 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9991 和统计通道上轨 10051.74，下方关注20日区间下沿 9420 和统计通道下轨 9434.86。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 119.50，说明观察位需要给盘中噪音留出空间。综合评分 61.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.28%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 48.45，豆棕价差 -887。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 10040；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10120.09 / 下方观察位 9366.51",
        "stop_loss": "下方观察位 9366.51",
        "upper_watch": "10120.09",
        "lower_watch": "9366.51",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "M2609",
      "product": "M",
      "name": "豆粕",
      "market": "DCE",
      "contract": "M2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "3179",
      "change": "+1.05%",
      "volume": "144.60 万手",
      "open_interest": "207.50 万手",
      "direction": "↑",
      "open": "3161",
      "high": "3209",
      "low": "3161",
      "preclose": "3146",
      "settle": "3144",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3179 / 行情skill 3179",
      "score": {
        "total": 63.6,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 54.2,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为偏多，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.05%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3179 先看与 MA20 3035.90、MA60 2996.95 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3153 和统计通道上轨 3164.48，下方关注20日区间下沿 2919 和统计通道下轨 2907.32。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 38.64，说明观察位需要给盘中噪音留出空间。综合评分 63.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.28%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 3179；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 3366.43",
        "stop_loss": "下方观察位 3033.27",
        "upper_watch": "3366.43",
        "lower_watch": "3033.27",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
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
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "3234",
      "change": "+1.06%",
      "volume": "45.77 万手",
      "open_interest": "146.58 万手",
      "direction": "↑",
      "open": "3215",
      "high": "3258",
      "low": "3215",
      "preclose": "3200",
      "settle": "3198",
      "trade_date": "2026-07-23",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3234 / 行情skill 3234",
      "score": {
        "total": 63.6,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 54.2,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为偏多，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.06%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3234 先看与 MA20 3095.50、MA60 3055.65 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3208 和统计通道上轨 3224.37，下方关注20日区间下沿 2982 和统计通道下轨 2966.63。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 35.71，说明观察位需要给盘中噪音留出空间。综合评分 63.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.28%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 3234；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 3412.41",
        "stop_loss": "下方观察位 3093.61",
        "upper_watch": "3412.41",
        "lower_watch": "3093.61",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查"
    },
    {
      "symbol": "RM2609",
      "product": "RM",
      "name": "菜粕",
      "market": "CZCE",
      "contract": "RM2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "2370",
      "change": "+0.85%",
      "volume": "75.36 万手",
      "open_interest": "64.27 万手",
      "direction": "↑",
      "open": "2360",
      "high": "2397",
      "low": "2360",
      "preclose": "2350",
      "settle": "2354",
      "trade_date": "2026-07-23",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 63.4,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 53.4,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为偏多，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+0.85%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2370 先看与 MA20 2303.05、MA60 2316.12 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2356 和统计通道上轨 2363.18，下方关注20日区间下沿 2232 和统计通道下轨 2242.92。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 36.93，说明观察位需要给盘中噪音留出空间。综合评分 63.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.28%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 2370；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 2498.14",
        "stop_loss": "下方观察位 2279.07",
        "upper_watch": "2498.14",
        "lower_watch": "2279.07",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
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
      "price": "2329",
      "change": "+1.61%",
      "volume": "20.07 万手",
      "open_interest": "34.01 万手",
      "direction": "↑",
      "open": "2301",
      "high": "2340",
      "low": "2301",
      "preclose": "2292",
      "settle": "2298",
      "trade_date": "2026-07-23",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 64.1,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 56.5,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为偏多，置信度高。核心原因是：驱动与资金对价格更友好；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+1.61%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2329 先看与 MA20 2247.05、MA60 2264.47 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2297 和统计通道上轨 2301.81，下方关注20日区间下沿 2191 和统计通道下轨 2192.29。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 29.29，说明观察位需要给盘中噪音留出空间。综合评分 64.10 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.28%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 2329；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 2438.95",
        "stop_loss": "下方观察位 2240.12",
        "upper_watch": "2438.95",
        "lower_watch": "2240.12",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
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
      "contract": "FCPOV2026",
      "price": "4621",
      "unit": "林吉特/吨",
      "change": "+0.28%",
      "change_basis": "intraday_vs_open",
      "volume": "4.39 万手",
      "open_interest": "9.75 万手",
      "direction": "↑",
      "open": "4608",
      "high": "4633",
      "low": "4592",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-22",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "海外产地价格使用交易所或公开行情源，仅作棕榈油跨市场参考。",
      "score": {
        "total": 58.2,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 51.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅+0.28%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 4621 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 41，说明观察位需要给盘中噪音留出空间。综合评分 58.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.28%，CBOT豆油 +0.51%。"
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
        "stance": "震荡",
        "entry": "现价 4621；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4710.05 / 下方观察位 4531.95",
        "stop_loss": "下方观察位 4531.95",
        "upper_watch": "4710.05",
        "lower_watch": "4531.95",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
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
      "contract": "CPOTR AUG26",
      "price": "16145",
      "unit": "印尼盾/公斤",
      "change": "-0.95%",
      "change_basis": "vs_previous_settlement_ydsp",
      "volume": "112 手",
      "open_interest": "需进一步核验",
      "direction": "↓",
      "open": "16145",
      "high": "16145",
      "low": "16145",
      "preclose": "16300",
      "settle": "16145",
      "trade_date": "2026-07-22",
      "source": "ICDX 官方历史价格接口",
      "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
      "verification": "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。",
      "score": {
        "total": 54.3,
        "technical": 44,
        "fundamental": 50.0,
        "driver": 71.7,
        "money_flow": 46.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "印尼棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.28%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.70%（24小时新增）；资金看当日涨跌幅-0.95%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 16145 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 161.45，说明观察位需要给盘中噪音留出空间。综合评分 54.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.28%，CBOT豆油 +0.51%。"
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
        "entry": "现价 16145；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 16495.67 / 下方观察位 15794.33",
        "stop_loss": "下方观察位 15794.33",
        "upper_watch": "16495.67",
        "lower_watch": "15794.33",
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
      "value": "P2609",
      "label": "P2609",
      "display": "棕榈油 P2609 主力",
      "name": "棕榈油",
      "contract": "P2609",
      "product": "P",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "P2701",
      "label": "P2701",
      "display": "棕榈油 P2701 次主力",
      "name": "棕榈油",
      "contract": "P2701",
      "product": "P",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "Y2609",
      "label": "Y2609",
      "display": "豆油 Y2609 主力",
      "name": "豆油",
      "contract": "Y2609",
      "product": "Y",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "Y2701",
      "label": "Y2701",
      "display": "豆油 Y2701 次主力",
      "name": "豆油",
      "contract": "Y2701",
      "product": "Y",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "OI2609",
      "label": "OI2609",
      "display": "菜油 OI2609 主力",
      "name": "菜油",
      "contract": "OI2609",
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
      "value": "M2609",
      "label": "M2609",
      "display": "豆粕 M2609 主力",
      "name": "豆粕",
      "contract": "M2609",
      "product": "M",
      "rank": 1,
      "contract_label": "主力"
    },
    {
      "value": "M2701",
      "label": "M2701",
      "display": "豆粕 M2701 次主力",
      "name": "豆粕",
      "contract": "M2701",
      "product": "M",
      "rank": 2,
      "contract_label": "次主力"
    },
    {
      "value": "RM2609",
      "label": "RM2609",
      "display": "菜粕 RM2609 主力",
      "name": "菜粕",
      "contract": "RM2609",
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
      "label": "FCPOV2026",
      "display": "马棕油 FCPOV2026",
      "name": "马棕油",
      "contract": "FCPOV2026",
      "product": "FCPO",
      "rank": null,
      "contract_label": null
    },
    {
      "value": "CPOTR",
      "label": "CPOTR AUG26",
      "display": "印尼棕榈油 CPOTR AUG26",
      "name": "印尼棕榈油",
      "contract": "CPOTR AUG26",
      "product": "CPOTR",
      "rank": null,
      "contract_label": null
    }
  ]
};

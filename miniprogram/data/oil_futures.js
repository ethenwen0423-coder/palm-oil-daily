module.exports = {
  "updated_at": "2026-07-14 09:58",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-14-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "4543",
      "change": "+0.22%",
      "unit": "林吉特/吨",
      "updated_at": "2026-07-13T22:59:59",
      "source": "tradingview:MYX:FCPO1!"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1357.35",
      "change": "+0.03%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-07-13T15:32",
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
      "price": "9262",
      "change": "+0.54%",
      "volume": "30.58 万手",
      "open_interest": "48.78 万手",
      "direction": "↑",
      "open": "9221",
      "high": "9304",
      "low": "9194",
      "preclose": "9212",
      "settle": "9263",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9262 / 行情skill 9264；涨跌幅口径不同：AkShare +0.54% / 行情skill +0.01%",
      "score": {
        "total": 50.1,
        "technical": 35.0,
        "fundamental": 47.0,
        "driver": 67.0,
        "money_flow": 47.5,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看棕榈油库存偏高但仅作背景压力；豆棕价差用于相对强弱背景；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.54%；成交量较前快照-11.35%；持仓较前快照+0.37%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9262 先看与 MA20 9283.70、MA60 9484 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9470 和统计通道上轨 9433.46，下方关注20日区间下沿 9028 和统计通道下轨 9133.94。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 151.29，说明观察位需要给盘中噪音留出空间。综合评分 50.10 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.22%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 75.86，豆棕价差 -681。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：棕榈油库存偏高但仅作背景压力；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9262；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9556.54 / 下方观察位 8941.46",
        "stop_loss": "下方观察位 8941.46",
        "upper_watch": "9556.54",
        "lower_watch": "8941.46",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
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
      "price": "9549",
      "change": "+0.42%",
      "volume": "5.83 万手",
      "open_interest": "22.11 万手",
      "direction": "↑",
      "open": "9538",
      "high": "9604",
      "low": "9501",
      "preclose": "9509",
      "settle": "9555",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9549 / 行情skill 9565；涨跌幅口径不同：AkShare +0.42% / 行情skill +0.10%",
      "score": {
        "total": 48.5,
        "technical": 35.0,
        "fundamental": 47.0,
        "driver": 67.0,
        "money_flow": 39.7,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看棕榈油库存偏高但仅作背景压力；豆棕价差用于相对强弱背景；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.42%；成交量较前快照-83.10%；持仓较前快照-54.50%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9549 先看与 MA20 9553.25、MA60 9645.92 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9738 和统计通道上轨 9691.28，下方关注20日区间下沿 9313 和统计通道下轨 9415.22。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 141，说明观察位需要给盘中噪音留出空间。综合评分 48.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.22%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 75.86，豆棕价差 -681。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：棕榈油库存偏高但仅作背景压力；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9549；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9818.65 / 下方观察位 9242.75",
        "stop_loss": "下方观察位 9242.75",
        "upper_watch": "9818.65",
        "lower_watch": "9242.75",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
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
      "price": "8580",
      "change": "+0.14%",
      "volume": "12.48 万手",
      "open_interest": "58.31 万手",
      "direction": "↑",
      "open": "8600",
      "high": "8614",
      "low": "8557",
      "preclose": "8568",
      "settle": "8574",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8580 / 行情skill 8588",
      "score": {
        "total": 55.4,
        "technical": 65.0,
        "fundamental": 47.0,
        "driver": 63.9,
        "money_flow": 40.9,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看豆油库存压力但仅作背景压力；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.14%；成交量较前快照-28.50%；持仓较前快照-0.76%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8580 先看与 MA20 8446.70、MA60 8487.60 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8657 和统计通道上轨 8633.23，下方关注20日区间下沿 8270 和统计通道下轨 8260.17。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 84.07，说明观察位需要给盘中噪音留出空间。综合评分 55.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.22%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 110.30 和豆棕价差 -681。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：豆油库存压力但仅作背景压力。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8580；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8705.09 / 下方观察位 8221.91",
        "stop_loss": "下方观察位 8221.91",
        "upper_watch": "8705.09",
        "lower_watch": "8221.91",
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
      "price": "8582",
      "change": "+0.25%",
      "volume": "4.04 万手",
      "open_interest": "33.06 万手",
      "direction": "↑",
      "open": "8592",
      "high": "8606",
      "low": "8551",
      "preclose": "8561",
      "settle": "8566",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8582 / 行情skill 8584",
      "score": {
        "total": 54.2,
        "technical": 65.0,
        "fundamental": 47.0,
        "driver": 63.9,
        "money_flow": 35.0,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看豆油库存压力但仅作背景压力；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.25%；成交量较前快照-76.86%；持仓较前快照-43.74%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8582 先看与 MA20 8412.55、MA60 8449.73 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8629 和统计通道上轨 8617.70，下方关注20日区间下沿 8237 和统计通道下轨 8207.40。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 84.71，说明观察位需要给盘中噪音留出空间。综合评分 54.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.22%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 110.30 和豆棕价差 -681。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：豆油库存压力但仅作背景压力。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8582；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8677.46 / 下方观察位 8188.54",
        "stop_loss": "下方观察位 8188.54",
        "upper_watch": "8677.46",
        "lower_watch": "8188.54",
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
      "price": "9933",
      "change": "+0.59%",
      "volume": "13.58 万手",
      "open_interest": "31.89 万手",
      "direction": "↑",
      "open": "9890",
      "high": "9967",
      "low": "9880",
      "preclose": "9875",
      "settle": "9910",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9933 / 行情skill 9934；涨跌幅口径不同：AkShare +0.59% / 行情skill +0.24%",
      "score": {
        "total": 56.2,
        "technical": 65.0,
        "fundamental": 47.0,
        "driver": 63.6,
        "money_flow": 45.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看菜油库存压力但仅作背景压力；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.59%；成交量较前快照-51.04%；持仓较前快照+0.19%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9933 先看与 MA20 9743.10、MA60 9766.08 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9960 和统计通道上轨 9974.33，下方关注20日区间下沿 9453 和统计通道下轨 9511.87。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 140.43，说明观察位需要给盘中噪音留出空间。综合评分 56.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.22%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.25，豆棕价差 -681。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：菜油库存压力但仅作背景压力；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 9933；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10054.66 / 下方观察位 9431.54",
        "stop_loss": "下方观察位 9431.54",
        "upper_watch": "10054.66",
        "lower_watch": "9431.54",
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
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "9912",
      "change": "+0.49%",
      "volume": "2.47 万手",
      "open_interest": "14.81 万手",
      "direction": "↑",
      "open": "9888",
      "high": "9957",
      "low": "9873",
      "preclose": "9864",
      "settle": "9896",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9912 / 行情skill 9927",
      "score": {
        "total": 54.7,
        "technical": 65.0,
        "fundamental": 47.0,
        "driver": 63.6,
        "money_flow": 37.9,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看菜油库存压力但仅作背景压力；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.49%；成交量较前快照-91.08%；持仓较前快照-53.45%。需要降级看待的地方：库存偏高但价格上涨，库存不能单独解释今日方向。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9912 先看与 MA20 9737.80、MA60 9758.22 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9966 和统计通道上轨 9969.07，下方关注20日区间下沿 9458 和统计通道下轨 9506.53。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 137.86，说明观察位需要给盘中噪音留出空间。综合评分 54.70 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.22%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.25，豆棕价差 -681。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：菜油库存压力但仅作背景压力；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9912；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10047.92 / 下方观察位 9427.68",
        "stop_loss": "下方观察位 9427.68",
        "upper_watch": "10047.92",
        "lower_watch": "9427.68",
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
      "price": "3056",
      "change": "+0.20%",
      "volume": "47.74 万手",
      "open_interest": "193.09 万手",
      "direction": "↑",
      "open": "3048",
      "high": "3068",
      "low": "3045",
      "preclose": "3050",
      "settle": "3063",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3056 / 行情skill 3058；涨跌幅口径不同：AkShare +0.20% / 行情skill -0.16%",
      "score": {
        "total": 58.0,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 63.6,
        "money_flow": 50.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.20%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3056 先看与 MA20 2982.15、MA60 2983.58 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3063 和统计通道上轨 3069.71，下方关注20日区间下沿 2919 和统计通道下轨 2894.59。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 34.43，说明观察位需要给盘中噪音留出空间。综合评分 58 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.22%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3056；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3089.40 / 下方观察位 2899.31",
        "stop_loss": "下方观察位 2899.31",
        "upper_watch": "3089.40",
        "lower_watch": "2899.31",
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
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "3123",
      "change": "+0.19%",
      "volume": "16.84 万手",
      "open_interest": "137.13 万手",
      "direction": "↑",
      "open": "3113",
      "high": "3132",
      "low": "3113",
      "preclose": "3117",
      "settle": "3124",
      "trade_date": "2026-07-14",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3123 / 行情skill 3123",
      "score": {
        "total": 60.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 63.6,
        "money_flow": 50.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.19%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3123 先看与 MA20 3040.95、MA60 3040.12 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3122 和统计通道上轨 3128.53，下方关注20日区间下沿 2982 和统计通道下轨 2953.37。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 30.64，说明观察位需要给盘中噪音留出空间。综合评分 60.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.22%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3123；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3146.06 / 下方观察位 2964.47",
        "stop_loss": "下方观察位 2964.47",
        "upper_watch": "3146.06",
        "lower_watch": "2964.47",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
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
      "price": "2320",
      "change": "+1.09%",
      "volume": "39.79 万手",
      "open_interest": "70.41 万手",
      "direction": "↑",
      "open": "2302",
      "high": "2328",
      "low": "2295",
      "preclose": "2295",
      "settle": "2320",
      "trade_date": "2026-07-14",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 55.2,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 63.6,
        "money_flow": 54.4,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+1.09%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2320 先看与 MA20 2291.10、MA60 2320.33 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2343 和统计通道上轨 2340.70，下方关注20日区间下沿 2232 和统计通道下轨 2241.50。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 39.93，说明观察位需要给盘中噪音留出空间。综合评分 55.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.22%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2320；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2365.84 / 下方观察位 2218.66",
        "stop_loss": "下方观察位 2218.66",
        "upper_watch": "2365.84",
        "lower_watch": "2218.66",
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
      "price": "2253",
      "change": "+0.67%",
      "volume": "6.70 万手",
      "open_interest": "34.35 万手",
      "direction": "↑",
      "open": "2243",
      "high": "2260",
      "low": "2239",
      "preclose": "2238",
      "settle": "2261",
      "trade_date": "2026-07-14",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 54.9,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 63.6,
        "money_flow": 52.7,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.67%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2253 先看与 MA20 2233.55、MA60 2271.40 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2273 和统计通道上轨 2269.52，下方关注20日区间下沿 2191 和统计通道下轨 2197.58。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 27.71，说明观察位需要给盘中噪音留出空间。综合评分 54.90 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.22%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2253；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2288.85 / 下方观察位 2181.73",
        "stop_loss": "下方观察位 2181.73",
        "upper_watch": "2288.85",
        "lower_watch": "2181.73",
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
      "contract": "FCPOU2026",
      "price": "4543",
      "change": "+0.22%",
      "change_basis": "intraday_vs_open",
      "volume": "5185 手",
      "open_interest": "7.74 万手",
      "direction": "↑",
      "open": "4533",
      "high": "4545",
      "low": "4518",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-13",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
      "score": {
        "total": 55.8,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 63.6,
        "money_flow": 50.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.22%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.42%（24小时新增）；资金看当日涨跌幅+0.22%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 4543 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 27，说明观察位需要给盘中噪音留出空间。综合评分 55.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.22%，CBOT豆油 +0.51%。"
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
        "entry": "现价 4543；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4601.64 / 下方观察位 4484.36",
        "stop_loss": "下方观察位 4484.36",
        "upper_watch": "4601.64",
        "lower_watch": "4484.36",
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
      "value": "OI2611",
      "label": "OI2611",
      "display": "菜油 OI2611 次主力",
      "name": "菜油",
      "contract": "OI2611",
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
      "label": "FCPOU2026",
      "display": "马棕油 FCPOU2026",
      "name": "马棕油",
      "contract": "FCPOU2026",
      "product": "FCPO",
      "rank": null,
      "contract_label": null
    }
  ]
};

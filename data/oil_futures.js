window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-30 06:13",
  "update_session": "morning",
  "timezone": "Asia/Shanghai",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-30-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
  "fundamental_mode": "refresh",
  "fundamental_updated_at": "2026-07-30 06:13",
  "fundamental_update_session": "morning",
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
      "price": "4653",
      "change": "+0.22%",
      "unit": "林吉特/吨",
      "updated_at": "2026-07-28T22:59:59",
      "source": "tradingview:MYX:FCPO1!"
    },
    "indonesia_cpotr": {
      "label": "印尼 ICDX CPOTR",
      "location": "雅加达",
      "price": "16300",
      "change": "-0.64%",
      "unit": "印尼盾/公斤",
      "updated_at": "2026-07-28",
      "source": "ICDX 官方历史价格接口"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1372.85",
      "change": "0.00%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-07-29T15:18",
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
      "price": "9370",
      "change": "-0.16%",
      "volume": "12.70 万手",
      "open_interest": "36.60 万手",
      "direction": "↓",
      "open": "9400",
      "high": "9416",
      "low": "9348",
      "preclose": "9385",
      "settle": "9349",
      "trade_date": "2026-07-30",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9370 / 行情skill 9370；涨跌幅口径不同：AkShare -0.16% / 行情skill +0.22%",
      "score": {
        "total": 57.3,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 65.1,
        "money_flow": 62.4,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为震荡偏强，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.16%；成交量较前快照+0.74%；持仓较前快照-5.04%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9370 先看与 MA20 9305.70、MA60 9417.92 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9600 和统计通道上轨 9522.36，下方关注20日区间下沿 9084 和统计通道下轨 9089.04。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 150.07，说明观察位需要给盘中噪音留出空间。综合评分 57.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.22%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 83.91，豆棕价差 -978。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9370；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9685.84",
        "stop_loss": "下方观察位 8983.99",
        "upper_watch": "9685.84",
        "lower_watch": "8983.99",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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
      "price": "9645",
      "change": "-0.20%",
      "volume": "3.58 万手",
      "open_interest": "26.68 万手",
      "direction": "↓",
      "open": "9665",
      "high": "9688",
      "low": "9625",
      "preclose": "9664",
      "settle": "9637",
      "trade_date": "2026-07-30",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未返回有效行情）；当前以 AkShare 为准。",
      "score": {
        "total": 56.2,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 65.1,
        "money_flow": 57.2,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为震荡偏强，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.20%；成交量较前快照-71.61%；持仓较前快照-30.76%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9645 先看与 MA20 9590.60、MA60 9648.28 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9876 和统计通道上轨 9799.80，下方关注20日区间下沿 9369 和统计通道下轨 9381.40。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 135.71，说明观察位需要给盘中噪音留出空间。综合评分 56.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.22%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 83.91，豆棕价差 -978。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9645；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9939.77",
        "stop_loss": "下方观察位 9286.40",
        "upper_watch": "9939.77",
        "lower_watch": "9286.40",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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
      "price": "8392",
      "change": "-0.24%",
      "volume": "7.10 万手",
      "open_interest": "38.44 万手",
      "direction": "↓",
      "open": "8430",
      "high": "8430",
      "low": "8388",
      "preclose": "8412",
      "settle": "8422",
      "trade_date": "2026-07-30",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8392 / 行情skill 8392",
      "score": {
        "total": 48.4,
        "technical": 29.0,
        "fundamental": 47.0,
        "driver": 61.0,
        "money_flow": 55.7,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。"
      },
      "view": "豆油当前观点为震荡偏强，置信度低。核心原因是：驱动与资金对价格更友好；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱。基本面背景看豆油库存压力但仅作背景压力；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.24%；成交量较前快照+21.45%；持仓较前快照-2.94%。需要降级看待的地方：技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8392 先看与 MA20 8530.30、MA60 8485.75 的相对位置，技术评分 29，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8657 和统计通道上轨 8681.04，下方关注20日区间下沿 8362 和统计通道下轨 8379.56。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 90.43，说明观察位需要给盘中噪音留出空间。综合评分 48.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.22%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 138.88 和豆棕价差 -978。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：豆油库存压力但仅作背景压力。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 8392；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 8708.73",
        "stop_loss": "下方观察位 8298.70",
        "upper_watch": "8708.73",
        "lower_watch": "8298.70",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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
      "price": "8428",
      "change": "-0.25%",
      "volume": "4.06 万手",
      "open_interest": "38.12 万手",
      "direction": "↓",
      "open": "8455",
      "high": "8465",
      "low": "8424",
      "preclose": "8449",
      "settle": "8454",
      "trade_date": "2026-07-30",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8428 / 行情skill 8428",
      "score": {
        "total": 45.8,
        "technical": 29.0,
        "fundamental": 47.0,
        "driver": 61.0,
        "money_flow": 42.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱。基本面背景看豆油库存压力但仅作背景压力；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.25%；成交量较前快照-30.54%；持仓较前快照-3.76%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8428 先看与 MA20 8526.25、MA60 8461.07 的相对位置，技术评分 29，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8658 和统计通道上轨 8669.70，下方关注20日区间下沿 8315 和统计通道下轨 8382.80。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 82.21，说明观察位需要给盘中噪音留出空间。综合评分 45.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.22%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 138.88 和豆棕价差 -978。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47，读数为中性。本轮可核验依据是：豆油库存压力但仅作背景压力。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8428；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8705.03 / 下方观察位 8267.97",
        "stop_loss": "下方观察位 8267.97",
        "upper_watch": "8705.03",
        "lower_watch": "8267.97",
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
      "price": "9893",
      "change": "-0.29%",
      "volume": "8.05 万手",
      "open_interest": "27.30 万手",
      "direction": "↓",
      "open": "9928",
      "high": "9959",
      "low": "9891",
      "preclose": "9922",
      "settle": "9900",
      "trade_date": "2026-07-29",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9893 / 行情skill 9893",
      "score": {
        "total": 54.6,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 56.3,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为震荡偏强，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.29%；成交量较前快照+32.62%；持仓较前快照-6.05%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9893 先看与 MA20 9923.20、MA60 9839.02 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10292 和统计通道上轨 10236.26，下方关注20日区间下沿 9518 和统计通道下轨 9610.14。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 143.86，说明观察位需要给盘中噪音留出空间。综合评分 54.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.22%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 48.45，豆棕价差 -978。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9893；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10318.55",
        "stop_loss": "下方观察位 9509.44",
        "upper_watch": "10318.55",
        "lower_watch": "9509.44",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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
      "price": "9779",
      "change": "-0.49%",
      "volume": "2.03 万手",
      "open_interest": "11.24 万手",
      "direction": "↓",
      "open": "9836",
      "high": "9847",
      "low": "9778",
      "preclose": "9827",
      "settle": "9814",
      "trade_date": "2026-07-29",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 48.4,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 43.0,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.49%；成交量较前快照-66.58%；持仓较前快照-61.31%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9779 先看与 MA20 9826.95、MA60 9788.25 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10208 和统计通道上轨 10137.32，下方关注20日区间下沿 9456 和统计通道下轨 9516.58。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 136.29，说明观察位需要给盘中噪音留出空间。综合评分 48.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.22%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 48.45，豆棕价差 -978。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9779；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10215.27 / 下方观察位 9438.63",
        "stop_loss": "下方观察位 9438.63",
        "upper_watch": "10215.27",
        "lower_watch": "9438.63",
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
      "price": "3092",
      "change": "-0.55%",
      "volume": "42.91 万手",
      "open_interest": "171.72 万手",
      "direction": "↓",
      "open": "3095",
      "high": "3102",
      "low": "3080",
      "preclose": "3109",
      "settle": "3109",
      "trade_date": "2026-07-30",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3092 / 行情skill 3092",
      "score": {
        "total": 56.9,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 47.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.55%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3092 先看与 MA20 3081.75、MA60 3008.62 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3230 和统计通道上轨 3210.48，下方关注20日区间下沿 2921 和统计通道下轨 2953.02。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 46.14，说明观察位需要给盘中噪音留出空间。综合评分 56.90 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 3092；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3236.87 / 下方观察位 2926.63",
        "stop_loss": "下方观察位 2926.63",
        "upper_watch": "3236.87",
        "lower_watch": "2926.63",
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
      "price": "3150",
      "change": "-0.72%",
      "volume": "20.51 万手",
      "open_interest": "151.08 万手",
      "direction": "↓",
      "open": "3151",
      "high": "3166",
      "low": "3142",
      "preclose": "3173",
      "settle": "3171",
      "trade_date": "2026-07-30",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3150 / 行情skill 3150",
      "score": {
        "total": 56.8,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 47.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.72%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3150 先看与 MA20 3141.10、MA60 3068.30 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3273 和统计通道上轨 3261.54，下方关注20日区间下沿 2982 和统计通道下轨 3020.66。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 40.71，说明观察位需要给盘中噪音留出空间。综合评分 56.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 3150；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3284.82 / 下方观察位 2997.38",
        "stop_loss": "下方观察位 2997.38",
        "upper_watch": "3284.82",
        "lower_watch": "2997.38",
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
      "price": "2313",
      "change": "-1.03%",
      "volume": "24.39 万手",
      "open_interest": "47.47 万手",
      "direction": "↓",
      "open": "2324",
      "high": "2334",
      "low": "2312",
      "preclose": "2337",
      "settle": "2340",
      "trade_date": "2026-07-29",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 49.0,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 45.9,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-1.03%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2313 先看与 MA20 2326.05、MA60 2313.77 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2472 和统计通道上轨 2412.90，下方关注20日区间下沿 2232 和统计通道下轨 2239.20。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 48.29，说明观察位需要给盘中噪音留出空间。综合评分 49 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "stance": "分歧震荡",
        "entry": "现价 2313；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2440.52 / 下方观察位 2208.12",
        "stop_loss": "下方观察位 2208.12",
        "upper_watch": "2440.52",
        "lower_watch": "2208.12",
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
      "price": "2271",
      "change": "-1.13%",
      "volume": "7.46 万手",
      "open_interest": "32.50 万手",
      "direction": "↓",
      "open": "2288",
      "high": "2292",
      "low": "2269",
      "preclose": "2297",
      "settle": "2298",
      "trade_date": "2026-07-29",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 56.4,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 45.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-1.13%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2271 先看与 MA20 2269.70、MA60 2262.37 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2394 和统计通道上轨 2351.80，下方关注20日区间下沿 2191 和统计通道下轨 2187.60。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 37.71，说明观察位需要给盘中噪音留出空间。综合评分 56.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 2271；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2373.38 / 下方观察位 2169.43",
        "stop_loss": "下方观察位 2169.43",
        "upper_watch": "2373.38",
        "lower_watch": "2169.43",
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
      "contract": "FCPOV2026",
      "price": "4653",
      "unit": "林吉特/吨",
      "change": "+0.22%",
      "change_basis": "intraday_vs_open",
      "volume": "6007 手",
      "open_interest": "7.46 万手",
      "direction": "↑",
      "open": "4643",
      "high": "4658",
      "low": "4633",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-28",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "海外产地价格使用交易所或公开行情源，仅作棕榈油跨市场参考。",
      "score": {
        "total": 55.3,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 50.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅+0.22%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 4653 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 25，说明观察位需要给盘中噪音留出空间。综合评分 55.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 4653；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4707.30 / 下方观察位 4598.70",
        "stop_loss": "下方观察位 4598.70",
        "upper_watch": "4707.30",
        "lower_watch": "4598.70",
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
      "price": "16300",
      "unit": "印尼盾/公斤",
      "change": "-0.64%",
      "change_basis": "vs_previous_settlement_ydsp",
      "volume": "112 手",
      "open_interest": "需进一步核验",
      "direction": "↓",
      "open": "16300",
      "high": "16300",
      "low": "16300",
      "preclose": "16405",
      "settle": "16300",
      "trade_date": "2026-07-28",
      "source": "ICDX 官方历史价格接口",
      "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
      "verification": "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。",
      "score": {
        "total": 51.6,
        "technical": 44,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 47.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "印尼棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.64%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 16300 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 163，说明观察位需要给盘中噪音留出空间。综合评分 51.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "stance": "分歧震荡",
        "entry": "现价 16300；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 16654.04 / 下方观察位 15945.96",
        "stop_loss": "下方观察位 15945.96",
        "upper_watch": "16654.04",
        "lower_watch": "15945.96",
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

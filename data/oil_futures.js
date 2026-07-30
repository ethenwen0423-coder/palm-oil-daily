window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-31 00:25",
  "update_session": "overnight",
  "timezone": "Asia/Shanghai",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-30-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证；基本面沿用最近交易日晨报发布后冻结的快照，盘中、夜盘与凌晨尾盘仅刷新行情、技术面、驱动和资金",
  "fundamental_mode": "carry",
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
      "change": "0.00%",
      "unit": "印尼盾/公斤",
      "updated_at": "2026-07-29",
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
      "change": "-0.24%",
      "volume": "11.74 万手",
      "open_interest": "35.18 万手",
      "direction": "↓",
      "open": "9388",
      "high": "9396",
      "low": "9360",
      "preclose": "9393",
      "settle": "9360",
      "trade_date": "2026-07-31",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9370 / 行情skill 9370；涨跌幅口径不同：AkShare -0.24% / 行情skill +0.11%",
      "score": {
        "total": 56.6,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 65.1,
        "money_flow": 59.2,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为震荡偏强，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.24%；成交量较前快照-6.89%；持仓较前快照-8.73%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9370 先看与 MA20 9316.75、MA60 9409.93 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9600 和统计通道上轨 9525.78，下方关注20日区间下沿 9084 和统计通道下轨 9107.72。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 146.86，说明观察位需要给盘中噪音留出空间。综合评分 56.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "take_profit": "上方观察位 9684.00",
        "stop_loss": "下方观察位 9004.92",
        "upper_watch": "9684.00",
        "lower_watch": "9004.92",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "P2701",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "9644",
      "change": "-0.17%",
      "volume": "3.10 万手",
      "open_interest": "28.00 万手",
      "direction": "↓",
      "open": "9648",
      "high": "9664",
      "low": "9633",
      "preclose": "9660",
      "settle": "9628",
      "trade_date": "2026-07-31",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9644 / 行情skill 9644；涨跌幅口径不同：AkShare -0.17% / 行情skill +0.17%",
      "score": {
        "total": 56.2,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 65.1,
        "money_flow": 57.3,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为震荡偏强，置信度中。核心原因是：驱动与资金对价格更友好；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.17%；成交量较前快照-75.41%；持仓较前快照-27.34%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9644 先看与 MA20 9601.60、MA60 9644.15 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9876 和统计通道上轨 9801.55，下方关注20日区间下沿 9369 和统计通道下轨 9401.65。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 134.21，说明观察位需要给盘中噪音留出空间。综合评分 56.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 9644；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9935.51",
        "stop_loss": "下方观察位 9307.70",
        "upper_watch": "9935.51",
        "lower_watch": "9307.70",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "Y2609",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "8400",
      "change": "-0.08%",
      "volume": "6.37 万手",
      "open_interest": "35.72 万手",
      "direction": "↓",
      "open": "8410",
      "high": "8415",
      "low": "8394",
      "preclose": "8407",
      "settle": "8394",
      "trade_date": "2026-07-31",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8400 / 行情skill 8400",
      "score": {
        "total": 49.3,
        "technical": 29.0,
        "fundamental": 47.0,
        "driver": 61.0,
        "money_flow": 59.9,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。"
      },
      "view": "豆油当前观点为震荡偏强，置信度低。核心原因是：驱动与资金对价格更友好；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱。基本面背景看豆油库存压力但仅作背景压力；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.08%；成交量较前快照+8.97%；持仓较前快照-9.82%。需要降级看待的地方：技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8400 先看与 MA20 8530.05、MA60 8481.68 的相对位置，技术评分 29，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8657 和统计通道上轨 8681.29，下方关注20日区间下沿 8393 和统计通道下轨 8378.81。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 87.71，说明观察位需要给盘中噪音留出空间。综合评分 49.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 8400；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 8707.17",
        "stop_loss": "下方观察位 8317.41",
        "upper_watch": "8707.17",
        "lower_watch": "8317.41",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "Y2701",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "8420",
      "change": "-0.19%",
      "volume": "3.32 万手",
      "open_interest": "39.29 万手",
      "direction": "↓",
      "open": "8425",
      "high": "8441",
      "low": "8418",
      "preclose": "8436",
      "settle": "8424",
      "trade_date": "2026-07-31",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未返回有效行情）；当前以 AkShare 为准。",
      "score": {
        "total": 45.3,
        "technical": 29.0,
        "fundamental": 47.0,
        "driver": 61.0,
        "money_flow": 39.9,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱。基本面背景看豆油库存压力但仅作背景压力；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.19%；成交量较前快照-43.27%；持仓较前快照-0.78%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8420 先看与 MA20 8528.85、MA60 8457.78 的相对位置，技术评分 29，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8658 和统计通道上轨 8664.15，下方关注20日区间下沿 8364 和统计通道下轨 8393.55。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 80.64，说明观察位需要给盘中噪音留出空间。综合评分 45.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 8420；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8704.13 / 下方观察位 8317.87",
        "stop_loss": "下方观察位 8317.87",
        "upper_watch": "8704.13",
        "lower_watch": "8317.87",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "OI2609",
      "product": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "9879",
      "change": "-0.14%",
      "volume": "4.80 万手",
      "open_interest": "25.57 万手",
      "direction": "↓",
      "open": "9899",
      "high": "9913",
      "low": "9866",
      "preclose": "9893",
      "settle": "9896",
      "trade_date": "2026-07-30",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9879 / 行情skill 9879",
      "score": {
        "total": 52.2,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 44.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.14%；成交量较前快照-20.91%；持仓较前快照-12.00%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9879 先看与 MA20 9940.05、MA60 9838.57 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10292 和统计通道上轨 10208.88，下方关注20日区间下沿 9550 和统计通道下轨 9671.22。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 144.43，说明观察位需要给盘中噪音留出空间。综合评分 52.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 9879；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10291.50 / 下方观察位 9565.30",
        "stop_loss": "下方观察位 9565.30",
        "upper_watch": "10291.50",
        "lower_watch": "9565.30",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "OI2701",
      "product": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "9776",
      "change": "-0.03%",
      "volume": "9882 手",
      "open_interest": "11.36 万手",
      "direction": "↓",
      "open": "9780",
      "high": "9799",
      "low": "9757",
      "preclose": "9779",
      "settle": "9784",
      "trade_date": "2026-07-30",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未返回有效行情）；当前以 AkShare 为准。",
      "score": {
        "total": 48.8,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 44.9,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.03%；成交量较前快照-83.71%；持仓较前快照-60.91%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9776 先看与 MA20 9842.85、MA60 9786.72 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10208 和统计通道上轨 10116.30，下方关注20日区间下沿 9479 和统计通道下轨 9569.40。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 137.64，说明观察位需要给盘中噪音留出空间。综合评分 48.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 9776；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10195.03 / 下方观察位 9477.04",
        "stop_loss": "下方观察位 9477.04",
        "upper_watch": "10195.03",
        "lower_watch": "9477.04",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "M2609",
      "product": "M",
      "name": "豆粕",
      "market": "DCE",
      "contract": "M2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "3075",
      "change": "+0.03%",
      "volume": "26.70 万手",
      "open_interest": "158.97 万手",
      "direction": "↑",
      "open": "3076",
      "high": "3086",
      "low": "3072",
      "preclose": "3074",
      "settle": "3080",
      "trade_date": "2026-07-31",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3075 / 行情skill 3075",
      "score": {
        "total": 53.4,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 50.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅+0.03%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3075 先看与 MA20 3087.50、MA60 3010.03 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3230 和统计通道上轨 3207.42，下方关注20日区间下沿 2957 和统计通道下轨 2967.58。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 48.21，说明观察位需要给盘中噪音留出空间。综合评分 53.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 3075；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3235.00 / 下方观察位 2940.00",
        "stop_loss": "下方观察位 2940.00",
        "upper_watch": "3235.00",
        "lower_watch": "2940.00",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "M2701",
      "product": "M",
      "name": "豆粕",
      "market": "DCE",
      "contract": "M2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "3136",
      "change": "-0.03%",
      "volume": "9.61 万手",
      "open_interest": "151.86 万手",
      "direction": "↓",
      "open": "3142",
      "high": "3146",
      "low": "3134",
      "preclose": "3137",
      "settle": "3141",
      "trade_date": "2026-07-31",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3136 / 行情skill 3136",
      "score": {
        "total": 53.3,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 49.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.03%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3136 先看与 MA20 3147.15、MA60 3070.12 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3273 和统计通道上轨 3258.62，下方关注20日区间下沿 3024 和统计通道下轨 3035.68。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 42.86，说明观察位需要给盘中噪音留出空间。综合评分 53.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 3136；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3283.13 / 下方观察位 3011.17",
        "stop_loss": "下方观察位 3011.17",
        "upper_watch": "3283.13",
        "lower_watch": "3011.17",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "RM2609",
      "product": "RM",
      "name": "菜粕",
      "market": "CZCE",
      "contract": "RM2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "2299",
      "change": "+0.44%",
      "volume": "16.42 万手",
      "open_interest": "47.28 万手",
      "direction": "↑",
      "open": "2289",
      "high": "2300",
      "low": "2287",
      "preclose": "2289",
      "settle": "2298",
      "trade_date": "2026-07-30",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 50.2,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 51.7,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅+0.44%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2299 先看与 MA20 2328.45、MA60 2312.60 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2472 和统计通道上轨 2412.92，下方关注20日区间下沿 2254 和统计通道下轨 2243.98。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 50，说明观察位需要给盘中噪音留出空间。综合评分 50.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 2299；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2441.52 / 下方观察位 2215.38",
        "stop_loss": "下方观察位 2215.38",
        "upper_watch": "2441.52",
        "lower_watch": "2215.38",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "RM2701",
      "product": "RM",
      "name": "菜粕",
      "market": "CZCE",
      "contract": "RM2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "2242",
      "change": "-0.13%",
      "volume": "6.44 万手",
      "open_interest": "35.33 万手",
      "direction": "↓",
      "open": "2245",
      "high": "2248",
      "low": "2236",
      "preclose": "2245",
      "settle": "2256",
      "trade_date": "2026-07-30",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 49.7,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 49.5,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅-0.13%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2242 先看与 MA20 2272.15、MA60 2261.08 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2394 和统计通道上轨 2352.80，下方关注20日区间下沿 2209 和统计通道下轨 2191.50。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 39.71，说明观察位需要给盘中噪音留出空间。综合评分 49.70 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
        "entry": "现价 2242；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2375.52 / 下方观察位 2168.78",
        "stop_loss": "下方观察位 2168.78",
        "upper_watch": "2375.52",
        "lower_watch": "2168.78",
        "invalidation": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 4 组候选点位，不输出明确交易指令。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
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
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
    },
    {
      "symbol": "CPOTR",
      "product": "CPOTR",
      "name": "印尼棕榈油",
      "market": "ICDX",
      "contract": "CPOTR AUG26",
      "price": "16300",
      "unit": "印尼盾/公斤",
      "change": "0.00%",
      "change_basis": "vs_previous_settlement_ydsp",
      "volume": "112 手",
      "open_interest": "需进一步核验",
      "direction": "→",
      "open": "16300",
      "high": "16300",
      "low": "16300",
      "preclose": "16300",
      "settle": "16300",
      "trade_date": "2026-07-29",
      "source": "ICDX 官方历史价格接口",
      "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
      "verification": "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。",
      "score": {
        "total": 53.6,
        "technical": 50,
        "fundamental": 50.0,
        "driver": 62.0,
        "money_flow": 50.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "印尼棕榈油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.22%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-1.69%（24小时新增）；资金看当日涨跌幅0.00%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 16300 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 163，说明观察位需要给盘中噪音留出空间。综合评分 53.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
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
      "quality_note": "动态驱动评分、观点置信度、冲突提示与观察位已通过skill质量检查",
      "fundamental_snapshot_note": "基本面沿用当日晨报发布后冻结的快照，午盘与收盘不重新计算。"
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

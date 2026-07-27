module.exports = {
  "updated_at": "2026-07-27 11:37",
  "update_session": "midday",
  "timezone": "Asia/Shanghai",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-27-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "4723",
      "change": "+0.04%",
      "unit": "林吉特/吨",
      "updated_at": "2026-07-24T17:59:59",
      "source": "tradingview:MYX:FCPO1!"
    },
    "indonesia_cpotr": {
      "label": "印尼 ICDX CPOTR",
      "location": "雅加达",
      "price": "16355",
      "change": "+1.43%",
      "unit": "印尼盾/公斤",
      "updated_at": "2026-07-24",
      "source": "ICDX 官方历史价格接口"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1382.95",
      "change": "0.00%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-07-24T15:48",
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
      "price": "9394",
      "change": "-1.84%",
      "volume": "42.85 万手",
      "open_interest": "38.96 万手",
      "direction": "↓",
      "open": "9518",
      "high": "9532",
      "low": "9363",
      "preclose": "9570",
      "settle": "9538",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9394 / 行情skill 9394；涨跌幅口径不同：AkShare -1.84% / 行情skill -1.51%",
      "score": {
        "total": 50.2,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 54.6,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.84%；成交量较前快照+170.23%；持仓较前快照-5.56%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9394 先看与 MA20 9289.75、MA60 9436.62 的相对位置，技术评分 51，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9515 和统计通道上轨 9471.85，下方关注20日区间下沿 9084 和统计通道下轨 9107.65。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 147.43，说明观察位需要给盘中噪音留出空间。综合评分 50.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.04%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 80.24，豆棕价差 -906。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 9394；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9599.33 / 下方观察位 9023.33",
        "stop_loss": "下方观察位 9023.33",
        "upper_watch": "9599.33",
        "lower_watch": "9023.33",
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
      "price": "9690",
      "change": "-1.55%",
      "volume": "11.71 万手",
      "open_interest": "24.90 万手",
      "direction": "↓",
      "open": "9776",
      "high": "9801",
      "low": "9659",
      "preclose": "9843",
      "settle": "9817",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9690 / 行情skill 9690；涨跌幅口径不同：AkShare -1.55% / 行情skill -1.29%",
      "score": {
        "total": 51.5,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 43.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.55%；成交量较前快照-26.18%；持仓较前快照-39.64%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9690 先看与 MA20 9570.80、MA60 9654.10 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9799 和统计通道上轨 9747.19，下方关注20日区间下沿 9369 和统计通道下轨 9394.41。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 135.43，说明观察位需要给盘中噪音留出空间。综合评分 51.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（+0.04%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 80.24，豆棕价差 -906。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9690；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9876.47 / 下方观察位 9316.94",
        "stop_loss": "下方观察位 9316.94",
        "upper_watch": "9876.47",
        "lower_watch": "9316.94",
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
      "price": "8492",
      "change": "-1.48%",
      "volume": "22.35 万手",
      "open_interest": "40.99 万手",
      "direction": "↓",
      "open": "8589",
      "high": "8610",
      "low": "8486",
      "preclose": "8620",
      "settle": "8593",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8492 / 行情skill 8492；涨跌幅口径不同：AkShare -1.48% / 行情skill -1.18%",
      "score": {
        "total": 49.3,
        "technical": 43.0,
        "fundamental": 50.0,
        "driver": 47.2,
        "money_flow": 59.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示震荡，主要信号为价格在20日均线下方、短均线转弱。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.48%；成交量较前快照+184.31%；持仓较前快照-3.71%。需要降级看待的地方：技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8492 先看与 MA20 8527.10、MA60 8491.20 的相对位置，技术评分 43，读数为中性略弱。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8657 和统计通道上轨 8663.15，下方关注20日区间下沿 8334 和统计通道下轨 8391.05。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 89.21，说明观察位需要给盘中噪音留出空间。综合评分 49.30 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.04%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 139 和豆棕价差 -906。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8492；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8708.03 / 下方观察位 8298.23",
        "stop_loss": "下方观察位 8298.23",
        "upper_watch": "8708.03",
        "lower_watch": "8298.23",
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
      "price": "8520",
      "change": "-1.31%",
      "volume": "11.22 万手",
      "open_interest": "35.18 万手",
      "direction": "↓",
      "open": "8600",
      "high": "8631",
      "low": "8514",
      "preclose": "8633",
      "settle": "8610",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8520 / 行情skill 8520；涨跌幅口径不同：AkShare -1.31% / 行情skill -1.05%",
      "score": {
        "total": 55.7,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 47.2,
        "money_flow": 63.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.31%；成交量较前快照+42.68%；持仓较前快照-17.36%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8520 先看与 MA20 8512.65、MA60 8463.25 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8629 和统计通道上轨 8665.76，下方关注20日区间下沿 8303 和统计通道下轨 8359.54。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 84.50，说明观察位需要给盘中噪音留出空间。综合评分 55.70 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（+0.04%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 139 和豆棕价差 -906。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 8520；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8703.53 / 下方观察位 8311.20",
        "stop_loss": "下方观察位 8311.20",
        "upper_watch": "8703.53",
        "lower_watch": "8311.20",
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
      "price": "10039",
      "change": "-2.35%",
      "volume": "25.72 万手",
      "open_interest": "34.11 万手",
      "direction": "↓",
      "open": "10240",
      "high": "10240",
      "low": "10017",
      "preclose": "10281",
      "settle": "10206",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 10039 / 行情skill 10039；涨跌幅口径不同：AkShare -2.35% / 行情skill -1.64%",
      "score": {
        "total": 52.1,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 46.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-2.35%；成交量较前快照+99.82%；持仓较前快照-4.82%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10039 先看与 MA20 9872.50、MA60 9831.93 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10186 和统计通道上轨 10196.66，下方关注20日区间下沿 9516 和统计通道下轨 9548.34。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 137.93，说明观察位需要给盘中噪音留出空间。综合评分 52.10 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.04%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 48.45，豆棕价差 -906。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 10039；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10275.56 / 下方观察位 9469.44",
        "stop_loss": "下方观察位 9469.44",
        "upper_watch": "10275.56",
        "lower_watch": "9469.44",
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
      "price": "10039",
      "change": "-2.31%",
      "volume": "5.66 万手",
      "open_interest": "14.65 万手",
      "direction": "↓",
      "open": "10240",
      "high": "10240",
      "low": "10019",
      "preclose": "10276",
      "settle": "10202",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 10039 / 行情skill 10039；涨跌幅口径不同：AkShare -2.31% / 行情skill -1.60%",
      "score": {
        "total": 49.9,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 35.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-2.31%；成交量较前快照-56.00%；持仓较前快照-59.13%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 10039 先看与 MA20 9864.25、MA60 9825.15 的相对位置，技术评分 65，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10184 和统计通道上轨 10195.88，下方关注20日区间下沿 9505 和统计通道下轨 9532.62。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 135.43，说明观察位需要给盘中噪音留出空间。综合评分 49.90 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（+0.04%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 48.45，豆棕价差 -906。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 10039；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10273.35 / 下方观察位 9455.15",
        "stop_loss": "下方观察位 9455.15",
        "upper_watch": "10273.35",
        "lower_watch": "9455.15",
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
      "price": "3181",
      "change": "-1.36%",
      "volume": "148.95 万手",
      "open_interest": "201.75 万手",
      "direction": "↓",
      "open": "3203",
      "high": "3209",
      "low": "3155",
      "preclose": "3225",
      "settle": "3189",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3181 / 行情skill 3181；涨跌幅口径不同：AkShare -1.36% / 行情skill -0.25%",
      "score": {
        "total": 54.1,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 44.5,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.36%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3181 先看与 MA20 3055.45、MA60 3002.72 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3209 和统计通道上轨 3194.85，下方关注20日区间下沿 2921 和统计通道下轨 2916.05。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 40，说明观察位需要给盘中噪音留出空间。综合评分 54.10 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3181；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3231.88 / 下方观察位 2898.12",
        "stop_loss": "下方观察位 2898.12",
        "upper_watch": "3231.88",
        "lower_watch": "2898.12",
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
      "price": "3237",
      "change": "-1.01%",
      "volume": "45.96 万手",
      "open_interest": "150.49 万手",
      "direction": "↓",
      "open": "3246",
      "high": "3260",
      "low": "3213",
      "preclose": "3270",
      "settle": "3246",
      "trade_date": "2026-07-27",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3237 / 行情skill 3237；涨跌幅口径不同：AkShare -1.01% / 行情skill -0.28%",
      "score": {
        "total": 54.4,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 46.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.01%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3237 先看与 MA20 3115.55、MA60 3061.95 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线多头排列、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3258 和统计通道上轨 3252.23，下方关注20日区间下沿 2982 和统计通道下轨 2978.87。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 36.36，说明观察位需要给盘中噪音留出空间。综合评分 54.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3237；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3278.80 / 下方观察位 2961.20",
        "stop_loss": "下方观察位 2961.20",
        "upper_watch": "3278.80",
        "lower_watch": "2961.20",
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
      "price": "2399",
      "change": "-2.76%",
      "volume": "111.45 万手",
      "open_interest": "57.46 万手",
      "direction": "↓",
      "open": "2441",
      "high": "2446",
      "low": "2378",
      "preclose": "2467",
      "settle": "2406",
      "trade_date": "2026-07-27",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 53.0,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 39.0,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-2.76%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2399 先看与 MA20 2311.45、MA60 2315.93 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2397 和统计通道上轨 2382.81，下方关注20日区间下沿 2232 和统计通道下轨 2240.09。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 42.14，说明观察位需要给盘中噪音留出空间。综合评分 53 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2399；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2451.79 / 下方观察位 2280.96",
        "stop_loss": "下方观察位 2280.96",
        "upper_watch": "2451.79",
        "lower_watch": "2280.96",
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
      "price": "2351",
      "change": "-1.59%",
      "volume": "22.27 万手",
      "open_interest": "33.44 万手",
      "direction": "↓",
      "open": "2360",
      "high": "2371",
      "low": "2332",
      "preclose": "2389",
      "settle": "2356",
      "trade_date": "2026-07-27",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 54.0,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 43.6,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏多，主要信号为价格在20日均线上方、均线结构震荡、突破20日区间上沿。基本面背景看基本面暂无强新增驱动；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅-1.59%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2351 先看与 MA20 2255.55、MA60 2264.20 的相对位置，技术评分 75，读数为偏强。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2340 和统计通道上轨 2325.24，下方关注20日区间下沿 2191 和统计通道下轨 2185.86。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 32.86，说明观察位需要给盘中噪音留出空间。综合评分 54 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2351；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2382.71 / 下方观察位 2232.44",
        "stop_loss": "下方观察位 2232.44",
        "upper_watch": "2382.71",
        "lower_watch": "2232.44",
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
      "price": "4723",
      "unit": "林吉特/吨",
      "change": "+0.04%",
      "change_basis": "intraday_vs_open",
      "volume": "4.05 万手",
      "open_interest": "10.54 万手",
      "direction": "↑",
      "open": "4721",
      "high": "4786",
      "low": "4712",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-24",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "海外产地价格使用交易所或公开行情源，仅作棕榈油跨市场参考。",
      "score": {
        "total": 50.5,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 50.2,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅+0.04%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 4723 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 74，说明观察位需要给盘中噪音留出空间。综合评分 50.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
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
        "entry": "现价 4723；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4883.73 / 下方观察位 4562.27",
        "stop_loss": "下方观察位 4562.27",
        "upper_watch": "4883.73",
        "lower_watch": "4562.27",
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
      "price": "16355",
      "unit": "印尼盾/公斤",
      "change": "+1.43%",
      "change_basis": "vs_previous_settlement_ydsp",
      "volume": "112 手",
      "open_interest": "需进一步核验",
      "direction": "↑",
      "open": "16355",
      "high": "16355",
      "low": "16355",
      "preclose": "16125",
      "settle": "16355",
      "trade_date": "2026-07-24",
      "source": "ICDX 官方历史价格接口",
      "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
      "verification": "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。",
      "score": {
        "total": 51.6,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 46.6,
        "money_flow": 55.7,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "印尼棕榈油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏多，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO+0.04%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆-0.18%（24小时新增）；资金看当日涨跌幅+1.43%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 16355 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格相对均线和区间位置偏强，但仍需要外盘驱动和资金配合确认延续性；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 163.55，说明观察位需要给盘中噪音留出空间。综合评分 51.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
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
        "entry": "现价 16355；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 16710.23 / 下方观察位 15999.77",
        "stop_loss": "下方观察位 15999.77",
        "upper_watch": "16710.23",
        "lower_watch": "15999.77",
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

module.exports = {
  "updated_at": "2026-08-03 15:09",
  "update_session": "close",
  "timezone": "Asia/Shanghai",
  "source": "futures-oil-daily 最新快照：source_runs/2026-08-03-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，海外产地盘展示马来 BMD FCPO 与印尼 ICDX CPOTR；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证；基本面沿用最近交易日晨报发布后冻结的快照，盘中、夜盘与凌晨尾盘仅刷新行情、技术面、驱动和资金",
  "fundamental_mode": "carry",
  "fundamental_updated_at": "2026-08-03 06:17",
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
      "price": "4642",
      "change": "-0.68%",
      "unit": "林吉特/吨",
      "updated_at": "2026-07-31T17:59:57",
      "source": "tradingview:MYX:FCPO1!"
    },
    "indonesia_cpotr": {
      "label": "印尼 ICDX CPOTR",
      "location": "雅加达",
      "price": "待更新",
      "change": "需进一步核验",
      "unit": "",
      "updated_at": "2026-08-03T15:05:11+08:00",
      "source": "ICDX 官方历史价格接口"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1372.95",
      "change": "-0.11%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-07-31T15:50",
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
      "price": "9253",
      "change": "-0.30%",
      "volume": "31.63 万手",
      "open_interest": "34.67 万手",
      "direction": "↓",
      "open": "9310",
      "high": "9322",
      "low": "9228",
      "preclose": "9281",
      "settle": "9335",
      "trade_date": "2026-08-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9253 / 行情skill 9253；涨跌幅口径不同：AkShare -0.30% / 行情skill -0.88%",
      "score": {
        "total": 47.2,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 52.2,
        "money_flow": 51.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.30%；成交量较前快照+196.17%；持仓较前快照-0.61%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9253 先看与 MA20 9325.35、MA60 9402 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9600 和统计通道上轨 9514.44，下方关注20日区间下沿 9084 和统计通道下轨 9136.26。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 147.29，说明观察位需要给盘中噪音留出空间。综合评分 47.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（-0.68%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 79.92，豆棕价差 -891。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 9253；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9598.69 / 下方观察位 8999.75",
        "stop_loss": "下方观察位 8999.75",
        "upper_watch": "9598.69",
        "lower_watch": "8999.75",
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
      "symbol": "P2701",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "9542",
      "change": "-0.26%",
      "volume": "11.98 万手",
      "open_interest": "28.69 万手",
      "direction": "↓",
      "open": "9602",
      "high": "9605",
      "low": "9515",
      "preclose": "9567",
      "settle": "9608",
      "trade_date": "2026-08-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9542 / 行情skill 9542；涨跌幅口径不同：AkShare -0.26% / 行情skill -0.69%",
      "score": {
        "total": 48.5,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 52.2,
        "money_flow": 58.0,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。"
      },
      "view": "棕榈油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.26%；成交量较前快照+12.19%；持仓较前快照-17.74%。需要降级看待的地方：技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9542 先看与 MA20 9610.15、MA60 9640.03 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 9876 和统计通道上轨 9787.66，下方关注20日区间下沿 9369 和统计通道下轨 9432.64。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 133.86，说明观察位需要给盘中噪音留出空间。综合评分 48.50 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "P的外盘弹性主要来自FCPO（-0.68%），CBOT豆油（+0.51%）决定油脂板块共振强度。两者同向时，内盘更容易形成顺畅传导；若背离，盘面通常更偏震荡。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看两点：棕榈油库存 79.92，豆棕价差 -891。库存偏高会限制单边上行弹性，价差变化则决定P相对Y/OI是继续强，还是转为板块跟随。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9542；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9864.22 / 下方观察位 9292.43",
        "stop_loss": "下方观察位 9292.43",
        "upper_watch": "9864.22",
        "lower_watch": "9292.43",
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
      "symbol": "Y2609",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "8385",
      "change": "-0.05%",
      "volume": "16.06 万手",
      "open_interest": "29.72 万手",
      "direction": "↓",
      "open": "8406",
      "high": "8412",
      "low": "8369",
      "preclose": "8389",
      "settle": "8394",
      "trade_date": "2026-08-03",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill返回非 JSON）；当前以 AkShare 为准。",
      "score": {
        "total": 48.8,
        "technical": 29.0,
        "fundamental": 50.0,
        "driver": 54.7,
        "money_flow": 63.1,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。"
      },
      "view": "豆油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.05%；成交量较前快照+201.36%；持仓较前快照-6.95%。需要降级看待的地方：技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8385 先看与 MA20 8529.35、MA60 8478.53 的相对位置，技术评分 29，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8657 和统计通道上轨 8683.13，下方关注20日区间下沿 8368 和统计通道下轨 8375.57。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 84.57，说明观察位需要给盘中噪音留出空间。综合评分 48.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（-0.68%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 141.64 和豆棕价差 -891。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8385；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8705.37 / 下方观察位 8319.63",
        "stop_loss": "下方观察位 8319.63",
        "upper_watch": "8705.37",
        "lower_watch": "8319.63",
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
      "symbol": "Y2701",
      "product": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2701",
      "contract_rank": 2,
      "contract_label": "次主力",
      "price": "8388",
      "change": "-0.21%",
      "volume": "13.04 万手",
      "open_interest": "43.06 万手",
      "direction": "↓",
      "open": "8428",
      "high": "8430",
      "low": "8380",
      "preclose": "8406",
      "settle": "8412",
      "trade_date": "2026-08-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8388 / 行情skill 8388",
      "score": {
        "total": 45.2,
        "technical": 26.0,
        "fundamental": 50.0,
        "driver": 54.7,
        "money_flow": 49.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱、处于统计区间下沿外侧。基本面背景看豆油库存压力，非24小时新增，只作背景；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.21%；成交量较前快照+144.67%；持仓较前快照+34.81%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 8388 先看与 MA20 8530.25、MA60 8455.28 的相对位置，技术评分 26，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱、处于统计区间下沿外侧。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 8658 和统计通道上轨 8660.43，下方关注20日区间下沿 8368 和统计通道下轨 8400.07。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 78.36，说明观察位需要给盘中噪音留出空间。综合评分 45.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "Y首先锚定CBOT豆油（+0.51%），同时受FCPO（-0.68%）影响油脂整体风险偏好。如果CBOT强而FCPO弱，Y可能强于P，但板块趋势会更不顺。"
        },
        {
          "title": "库存与价差",
          "text": "国内背景看豆油库存 141.64 和豆棕价差 -891。库存偏高时，Y独立上攻需要更强外盘或资金配合；价差变化会影响它对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：豆油库存压力，非24小时新增，只作背景。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 8388；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8702.82 / 下方观察位 8323.18",
        "stop_loss": "下方观察位 8323.18",
        "upper_watch": "8702.82",
        "lower_watch": "8323.18",
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
      "price": "9891",
      "change": "-0.03%",
      "volume": "17.63 万手",
      "open_interest": "23.07 万手",
      "direction": "↓",
      "open": "9923",
      "high": "9942",
      "low": "9840",
      "preclose": "9894",
      "settle": "9869",
      "trade_date": "2026-08-03",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未返回有效行情）；当前以 AkShare 为准。",
      "score": {
        "total": 52.2,
        "technical": 43.0,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 66.1,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。"
      },
      "view": "菜油当前观点为分歧震荡，置信度低。核心原因是：各类信号并不一致，暂按分歧震荡处理；技术面显示震荡，主要信号为价格在20日均线下方、短均线转弱。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.03%；成交量较前快照+132.08%；持仓较前快照-4.65%。需要降级看待的地方：技术面偏空，但资金与盘面偏多，当前不宜仅按技术面给出偏空结论。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9891 先看与 MA20 9953.10、MA60 9838.95 的相对位置，技术评分 43，读数为中性略弱。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10292 和统计通道上轨 10185.99，下方关注20日区间下沿 9550 和统计通道下轨 9720.21。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 138.29，说明观察位需要给盘中噪音留出空间。综合评分 52.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（-0.68%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 40.34，豆棕价差 -891。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9891；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10265.09 / 下方观察位 9590.64",
        "stop_loss": "下方观察位 9590.64",
        "upper_watch": "10265.09",
        "lower_watch": "9590.64",
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
      "price": "9732",
      "change": "-0.48%",
      "volume": "5.36 万手",
      "open_interest": "11.82 万手",
      "direction": "↓",
      "open": "9810",
      "high": "9814",
      "low": "9683",
      "preclose": "9779",
      "settle": "9761",
      "trade_date": "2026-08-03",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 46.2,
        "technical": 29.0,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 53.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏空，主要信号为价格在20日均线下方、短均线转弱。基本面背景看菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.48%；成交量较前快照-29.41%；持仓较前快照-51.16%。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 9732 先看与 MA20 9851.70、MA60 9784.60 的相对位置，技术评分 29，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 10208 和统计通道上轨 10097.89，下方关注20日区间下沿 9479 和统计通道下轨 9605.51。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 131.64，说明观察位需要给盘中噪音留出空间。综合评分 46.20 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "OI没有单一外盘锚，更多看CBOT豆油（+0.51%）和FCPO（-0.68%）共同带来的板块方向。外盘共振越强，菜油相对强弱切换越容易被资金放大。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 40.34，豆棕价差 -891。OI更容易体现油脂内部轮动，若库存压力没有缓解，单独走强的持续性需要打折。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50，读数为中性。本轮可核验依据是：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。库存、基差、进口利润、压榨利润只作为背景压力；除非24小时内有新增更新，否则不作为今日主驱动。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 9732；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10173.19 / 下方观察位 9446.07",
        "stop_loss": "下方观察位 9446.07",
        "upper_watch": "10173.19",
        "lower_watch": "9446.07",
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
      "price": "3067",
      "change": "-0.13%",
      "volume": "87.20 万手",
      "open_interest": "146.07 万手",
      "direction": "↓",
      "open": "3071",
      "high": "3086",
      "low": "3045",
      "preclose": "3071",
      "settle": "3075",
      "trade_date": "2026-08-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3067 / 行情skill 3067",
      "score": {
        "total": 50.4,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 49.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.13%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3067 先看与 MA20 3092.70、MA60 3011.33 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3230 和统计通道上轨 3198.59，下方关注20日区间下沿 2957 和统计通道下轨 2986.81。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 45.86，说明观察位需要给盘中噪音留出空间。综合评分 50.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO -0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3067；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3224.82 / 下方观察位 2960.58",
        "stop_loss": "下方观察位 2960.58",
        "upper_watch": "3224.82",
        "lower_watch": "2960.58",
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
      "price": "3126",
      "change": "-0.16%",
      "volume": "41.67 万手",
      "open_interest": "159.86 万手",
      "direction": "↓",
      "open": "3131",
      "high": "3148",
      "low": "3106",
      "preclose": "3131",
      "settle": "3135",
      "trade_date": "2026-08-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3126 / 行情skill 3126",
      "score": {
        "total": 50.4,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 49.4,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。基本面背景看基本面暂无强新增驱动；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.16%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 3126 先看与 MA20 3151.95、MA60 3071.70 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 3273 和统计通道上轨 3250.54，下方关注20日区间下沿 3024 和统计通道下轨 3053.36。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 40.93，说明观察位需要给盘中噪音留出空间。综合评分 50.40 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO -0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3126；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3273.95 / 下方观察位 3029.95",
        "stop_loss": "下方观察位 3029.95",
        "upper_watch": "3273.95",
        "lower_watch": "3029.95",
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
      "price": "2319",
      "change": "+0.13%",
      "volume": "54.23 万手",
      "open_interest": "47.33 万手",
      "direction": "↑",
      "open": "2316",
      "high": "2322",
      "low": "2294",
      "preclose": "2316",
      "settle": "2301",
      "trade_date": "2026-08-03",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 50.6,
        "technical": 49.0,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 50.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅+0.13%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2319 先看与 MA20 2331.05、MA60 2311.60 的相对位置，技术评分 49，读数为中性。价格仍在区间内反复，技术面更多说明节奏而不是方向结论；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2472 和统计通道上轨 2410.06，下方关注20日区间下沿 2254 和统计通道下轨 2252.04。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 47.93，说明观察位需要给盘中噪音留出空间。综合评分 50.60 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO -0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2319；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2437.48 / 下方观察位 2224.62",
        "stop_loss": "下方观察位 2224.62",
        "upper_watch": "2437.48",
        "lower_watch": "2224.62",
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
      "price": "2241",
      "change": "-0.31%",
      "volume": "17.67 万手",
      "open_interest": "37.58 万手",
      "direction": "↓",
      "open": "2247",
      "high": "2257",
      "low": "2229",
      "preclose": "2248",
      "settle": "2244",
      "trade_date": "2026-08-03",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 46.8,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 48.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏空，主要信号为价格在20日均线下方、均线结构震荡。基本面背景看基本面暂无强新增驱动；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.31%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 2241 先看与 MA20 2273.80、MA60 2259.72 的相对位置，技术评分 35，读数为偏弱。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 2394 和统计通道上轨 2350.65，下方关注20日区间下沿 2209 和统计通道下轨 2196.95。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 37.36，说明观察位需要给盘中噪音留出空间。综合评分 46.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO -0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2241；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2372.02 / 下方观察位 2175.58",
        "stop_loss": "下方观察位 2175.58",
        "upper_watch": "2372.02",
        "lower_watch": "2175.58",
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
      "price": "4642",
      "unit": "林吉特/吨",
      "change": "-0.68%",
      "change_basis": "intraday_vs_open",
      "volume": "2.73 万手",
      "open_interest": "9.37 万手",
      "direction": "↓",
      "open": "4674",
      "high": "4686",
      "low": "4627",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-31",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "海外产地价格使用交易所或公开行情源，仅作棕榈油跨市场参考。",
      "score": {
        "total": 48.7,
        "technical": 44,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 47.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示偏空，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅-0.68%；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "现价 4642 先看与 MA20 需进一步核验、MA60 需进一步核验 的相对位置，技术评分 需进一步核验，读数为数据需进一步核验。价格对均线支撑的依赖减弱，下方区间有效性需要继续观察；主要信号是：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 59，说明观察位需要给盘中噪音留出空间。综合评分 48.70 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO -0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 4642；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4770.15 / 下方观察位 4513.85",
        "stop_loss": "下方观察位 4513.85",
        "upper_watch": "4770.15",
        "lower_watch": "4513.85",
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
      "contract": "CPOTR",
      "price": "需进一步核验",
      "unit": "",
      "change": "需进一步核验",
      "change_basis": "需进一步核验",
      "volume": "需进一步核验",
      "open_interest": "需进一步核验",
      "direction": "→",
      "open": "需进一步核验",
      "high": "需进一步核验",
      "low": "需进一步核验",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-08-03",
      "source": "ICDX 官方历史价格接口",
      "note": "CPOTR 是印尼 ICDX 原棕榈油期货，以印尼盾/公斤报价，用于对照印尼产地价格发现。",
      "verification": "ICDX CPOTR价格来自交易所官方历史价格接口；涨跌幅相对前结算价YDSP计算。",
      "score": {
        "total": 50.8,
        "technical": 50,
        "fundamental": 50.0,
        "driver": 52.6,
        "money_flow": 50.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "印尼棕榈油当前观点为震荡，置信度中。核心原因是：当前行情缺少单边确认，仍需要等待新增驱动；技术面显示震荡，主要信号为外盘参考合约，技术历史样本不足。基本面背景看外盘参考合约，国内基本面因子不直接套用；驱动看FCPO-0.68%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+1.32%（24小时新增）；资金看当日涨跌幅需进一步核验；成交量变化需进一步核验；持仓变化需进一步核验。需要降级看待的地方：暂未看到需要明显降级的冲突信号。",
      "technical_detail": [
        {
          "title": "价格位置",
          "text": "最新价缺失，无法判断价格相对均线和区间的位置，技术结构需进一步核验。"
        },
        {
          "title": "关键区间",
          "text": "上方先观察20日区间上沿 需进一步核验 和统计通道上轨 需进一步核验，下方关注20日区间下沿 需进一步核验 和统计通道下轨 需进一步核验。这些位置用于判断突破或回落是否有效，不直接等同于开平仓点位。"
        },
        {
          "title": "波动节奏",
          "text": "14日平均波动幅度约 0.01，说明观察位需要给盘中噪音留出空间。综合评分 50.80 来自技术、基本面、驱动和资金共同作用，技术面只负责描述位置和节奏，不能单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅主要用于观察情绪传导：FCPO -0.68%，CBOT豆油 +0.51%。"
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
        "entry": "需进一步核验",
        "take_profit": "上方观察位需进一步核验",
        "stop_loss": "下方观察位需进一步核验",
        "upper_watch": "需进一步核验",
        "lower_watch": "需进一步核验",
        "invalidation": "行情价格或关键位不足，观点失效条件需进一步核验。",
        "risk_tip": "不输出明确开平仓指令。",
        "basis": "行情价格或关键位不足，暂不输出具体观察位。"
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
      "label": "CPOTR",
      "display": "印尼棕榈油 CPOTR",
      "name": "印尼棕榈油",
      "contract": "CPOTR",
      "product": "CPOTR",
      "rank": null,
      "contract_label": null
    }
  ]
};

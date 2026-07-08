window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-07 11:10",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-07-daily/raw/futures_market_data.json；国内合约名单由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
  "contract_discovery_skill": "contract_discovery_skill",
  "contract_discovery_month": "2026-07",
  "contract_discovery_warnings": [],
  "review_learning_warning": "",
  "review_learning_repeated_errors": {},
  "contracts": [
    {
      "symbol": "P2609",
      "product": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2609",
      "contract_rank": 1,
      "contract_label": "主力",
      "price": "9339",
      "change": "+1.02%",
      "volume": "37.12 万手",
      "open_interest": "49.35 万手",
      "direction": "↑",
      "open": "9251",
      "high": "9356",
      "low": "9237",
      "preclose": "9245",
      "settle": "9199",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9339 / 行情skill 9340；涨跌幅口径不同：AkShare +1.02% / 行情skill +1.53%",
      "score": {
        "total": 56.4,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 64.5,
        "money_flow": 58.9,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前驱动与资金偏强，总观点为震荡偏强，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+1.02%；成交量较前快照+2.70%；持仓较前快照-0.01%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9339 对照 MA20 9298.40、MA60 9507.22，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9588、下沿 9028；统计通道上轨 9458.48、下轨 9138.32。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 173.21，用于衡量波动区间和观察位有效性。综合评分 56.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +0.04% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -747。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9339；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9687.08",
        "stop_loss": "下方观察位 8940.61",
        "upper_watch": "9687.08",
        "lower_watch": "8940.61",
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
      "price": "9604",
      "change": "+0.90%",
      "volume": "7.14 万手",
      "open_interest": "21.45 万手",
      "direction": "↑",
      "open": "9558",
      "high": "9629",
      "low": "9515",
      "preclose": "9518",
      "settle": "9486",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9604 / 行情skill 9606；涨跌幅口径不同：AkShare +0.90% / 行情skill +1.27%",
      "score": {
        "total": 53.1,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 64.5,
        "money_flow": 42.6,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.90%；成交量较前快照-80.23%；持仓较前快照-56.54%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9604 对照 MA20 9567.70、MA60 9630.67，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9881、下沿 9313；统计通道上轨 9722.41、下轨 9412.99。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 159.86，用于衡量波动区间和观察位有效性。综合评分 53.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +0.04% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -747。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9604；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9951.21 / 下方观察位 9256.79",
        "stop_loss": "下方观察位 9256.79",
        "upper_watch": "9951.21",
        "lower_watch": "9256.79",
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
      "price": "8586",
      "change": "+0.89%",
      "volume": "20.73 万手",
      "open_interest": "57.94 万手",
      "direction": "↑",
      "open": "8532",
      "high": "8595",
      "low": "8518",
      "preclose": "8510",
      "settle": "8476",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8586 / 行情skill 8586；涨跌幅口径不同：AkShare +0.89% / 行情skill +1.30%",
      "score": {
        "total": 58.9,
        "technical": 75.0,
        "fundamental": 47.0,
        "driver": 62.4,
        "money_flow": 48.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力但仅作背景压力。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.89%；成交量较前快照+3.86%；持仓较前快照+0.27%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8586 对照 MA20 8390.30、MA60 8480.05，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8505、下沿 8270；统计通道上轨 8514.15、下轨 8266.45。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 88.14，用于衡量波动区间和观察位有效性。综合评分 58.90 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +0.04% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 125.83，豆棕价差 -747。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47。本轮纳入的可核验因子为：豆油库存压力但仅作背景压力；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 8586；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8628.74 / 下方观察位 8325.33",
        "stop_loss": "下方观察位 8325.33",
        "upper_watch": "8628.74",
        "lower_watch": "8325.33",
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
      "price": "8558",
      "change": "+0.99%",
      "volume": "6.43 万手",
      "open_interest": "32.37 万手",
      "direction": "↑",
      "open": "8498",
      "high": "8568",
      "low": "8492",
      "preclose": "8474",
      "settle": "8445",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8558 / 行情skill 8559；涨跌幅口径不同：AkShare +0.99% / 行情skill +1.35%",
      "score": {
        "total": 55.6,
        "technical": 75.0,
        "fundamental": 47.0,
        "driver": 62.4,
        "money_flow": 32.0,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力但仅作背景压力。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.99%；成交量较前快照-67.77%；持仓较前快照-43.99%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8558 对照 MA20 8355.40、MA60 8437.77，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8499、下沿 8237；统计通道上轨 8476.68、下轨 8234.12。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 87.79，用于衡量波动区间和观察位有效性。综合评分 55.60 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +0.04% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 125.83，豆棕价差 -747。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47。本轮纳入的可核验因子为：豆油库存压力但仅作背景压力；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8558；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8613.12 / 下方观察位 8298.86",
        "stop_loss": "下方观察位 8298.86",
        "upper_watch": "8613.12",
        "lower_watch": "8298.86",
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
      "price": "9870",
      "change": "+1.32%",
      "volume": "20.59 万手",
      "open_interest": "26.99 万手",
      "direction": "↑",
      "open": "9755",
      "high": "9883",
      "low": "9736",
      "preclose": "9741",
      "settle": "9692",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9870 / 行情skill 9872；涨跌幅口径不同：AkShare +1.32% / 行情skill +1.86%",
      "score": {
        "total": 59.8,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 63.1,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+1.32%；成交量较前快照+3.53%；持仓较前快照+0.38%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9870 对照 MA20 9759.10、MA60 9729.20，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10352、下沿 9453；统计通道上轨 10023.28、下轨 9494.92。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 150.43，用于衡量波动区间和观察位有效性。综合评分 59.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +0.04% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -747。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9870；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10196.73",
        "stop_loss": "下方观察位 9389.62",
        "upper_watch": "10196.73",
        "lower_watch": "9389.62",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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
      "price": "9856",
      "change": "+1.33%",
      "volume": "4.81 万手",
      "open_interest": "15.77 万手",
      "direction": "↑",
      "open": "9734",
      "high": "9869",
      "low": "9725",
      "preclose": "9727",
      "settle": "9672",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9856 / 行情skill 9856；涨跌幅口径不同：AkShare +1.33% / 行情skill +1.90%",
      "score": {
        "total": 56.4,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 46.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+1.33%；成交量较前快照-75.83%；持仓较前快照-41.35%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9856 对照 MA20 9758.20、MA60 9722.23，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10364、下沿 9458；统计通道上轨 10031.98、下轨 9484.42。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 148.71，用于衡量波动区间和观察位有效性。综合评分 56.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +0.04% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -747。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 9856；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10179.01 / 下方观察位 9399.36",
        "stop_loss": "下方观察位 9399.36",
        "upper_watch": "10179.01",
        "lower_watch": "9399.36",
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
      "price": "3036",
      "change": "+0.33%",
      "volume": "76.99 万手",
      "open_interest": "188.34 万手",
      "direction": "↑",
      "open": "3039",
      "high": "3045",
      "low": "3030",
      "preclose": "3026",
      "settle": "3005",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3036 / 行情skill 3038；涨跌幅口径不同：AkShare +0.33% / 行情skill +1.10%",
      "score": {
        "total": 59.9,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 51.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.33%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3036 对照 MA20 2949.90、MA60 2977.32，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2989、下沿 2887；统计通道上轨 3006.88、下轨 2892.92。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 33.36，用于衡量波动区间和观察位有效性。综合评分 59.90 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 3036；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3050.25 / 下方观察位 2921.60",
        "stop_loss": "下方观察位 2921.60",
        "upper_watch": "3050.25",
        "lower_watch": "2921.60",
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
      "price": "3095",
      "change": "+0.45%",
      "volume": "33.02 万手",
      "open_interest": "137.41 万手",
      "direction": "↑",
      "open": "3091",
      "high": "3104",
      "low": "3085",
      "preclose": "3081",
      "settle": "3064",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3095 / 行情skill 3097；涨跌幅口径不同：AkShare +0.45% / 行情skill +1.08%",
      "score": {
        "total": 60.0,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 51.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.45%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3095 对照 MA20 3012.20、MA60 3033.12，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3047、下沿 2966；统计通道上轨 3060.70、下轨 2963.70。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 28.93，用于衡量波动区间和观察位有效性。综合评分 60 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 3095；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3098.31 / 下方观察位 2989.39",
        "stop_loss": "下方观察位 2989.39",
        "upper_watch": "3098.31",
        "lower_watch": "2989.39",
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
      "price": "2316",
      "change": "+0.52%",
      "volume": "55.01 万手",
      "open_interest": "78.16 万手",
      "direction": "↑",
      "open": "2312",
      "high": "2326",
      "low": "2301",
      "preclose": "2304",
      "settle": "2287",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 54.1,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 52.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.52%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2316 对照 MA20 2272.35、MA60 2322.35，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2321、下沿 2214；统计通道上轨 2321.91、下轨 2222.79。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 39.21，用于衡量波动区间和观察位有效性。综合评分 54.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 2316；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2344.34 / 下方观察位 2200.36",
        "stop_loss": "下方观察位 2200.36",
        "upper_watch": "2344.34",
        "lower_watch": "2200.36",
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
      "price": "2258",
      "change": "+0.62%",
      "volume": "13.45 万手",
      "open_interest": "32.46 万手",
      "direction": "↑",
      "open": "2248",
      "high": "2270",
      "low": "2243",
      "preclose": "2244",
      "settle": "2230",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 57.4,
        "technical": 64.0,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 52.5,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.62%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2258 对照 MA20 2221.60、MA60 2276.80，当前技术评分为 64，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2252、下沿 2188；统计通道上轨 2252.90、下轨 2190.30。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 27.50，用于衡量波动区间和观察位有效性。综合评分 57.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 2258；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2288.65 / 下方观察位 2202.69",
        "stop_loss": "下方观察位 2202.69",
        "upper_watch": "2288.65",
        "lower_watch": "2202.69",
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
      "name": "马棕油",
      "market": "BMD",
      "contract": "FCPOU2026",
      "price": "4531",
      "change": "+0.04%",
      "volume": "1.47 万手",
      "open_interest": "8.57 万手",
      "direction": "↑",
      "open": "4529",
      "high": "4550",
      "low": "4525",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-06",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
      "score": {
        "total": 55.0,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 61.4,
        "money_flow": 50.2,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（外盘参考合约，技术历史样本不足）。基本面背景：外盘参考合约，国内基本面因子不直接套用。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.15%（24小时新增）；WTI/Brent原油+0.79%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.04%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -1；rapeseed_soybean_spread变化 -4。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 4531 对照 MA20 需进一步核验、MA60 需进一步核验，当前技术评分为 需进一步核验，趋势标签为偏多。核心信号为：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 需进一步核验、下沿 需进一步核验；统计通道上轨 需进一步核验、下轨 需进一步核验。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 25，用于衡量波动区间和观察位有效性。综合评分 55 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.04%，CBOT豆油 +0.51%。"
        },
        {
          "title": "库存与价差",
          "text": "外盘参考合约暂缺国内库存、基差与价差的可比口径，基本面评分按中性处理。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：外盘参考合约，国内基本面因子不直接套用；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 4531；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4585.30 / 下方观察位 4476.70",
        "stop_loss": "下方观察位 4476.70",
        "upper_watch": "4585.30",
        "lower_watch": "4476.70",
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

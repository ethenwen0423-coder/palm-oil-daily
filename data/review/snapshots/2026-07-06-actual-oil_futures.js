window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-06 23:05",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-06-daily/raw/futures_market_data.json；国内合约名单由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "9296",
      "change": "+0.55%",
      "volume": "17.96 万手",
      "open_interest": "49.53 万手",
      "direction": "↑",
      "open": "9251",
      "high": "9305",
      "low": "9237",
      "preclose": "9245",
      "settle": "9199",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 50.0,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 63.0,
        "money_flow": 49.3,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏空（价格在20日均线下方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.55%；成交量较前快照-16.62%；持仓较前快照-4.32%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9296 对照 MA20 9296.25、MA60 9506.50，当前技术评分为 35，趋势标签为偏空。核心信号为：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9588、下沿 9028；统计通道上轨 9455.24、下轨 9137.26。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 170.14，用于衡量波动区间和观察位有效性。综合评分 50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 -0.73% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -741。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9296；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9665.55 / 下方观察位 8930.68",
        "stop_loss": "下方观察位 8930.68",
        "upper_watch": "9665.55",
        "lower_watch": "8930.68",
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
      "price": "9557",
      "change": "+0.41%",
      "volume": "3.09 万手",
      "open_interest": "21.17 万手",
      "direction": "↑",
      "open": "9558",
      "high": "9570",
      "low": "9515",
      "preclose": "9518",
      "settle": "9486",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 49.3,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 63.0,
        "money_flow": 45.6,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏空（价格在20日均线下方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.41%；成交量较前快照-85.67%；持仓较前快照-59.10%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9557 对照 MA20 9565.35、MA60 9629.88，当前技术评分为 35，趋势标签为偏空。核心信号为：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9881、下沿 9313；统计通道上轨 9719.21、下轨 9411.49。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 156.50，用于衡量波动区间和观察位有效性。综合评分 49.30 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 -0.73% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -741。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9557；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9896.92 / 下方观察位 9223.48",
        "stop_loss": "下方观察位 9223.48",
        "upper_watch": "9896.92",
        "lower_watch": "9223.48",
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
      "price": "8555",
      "change": "+0.53%",
      "volume": "10.54 万手",
      "open_interest": "56.45 万手",
      "direction": "↑",
      "open": "8532",
      "high": "8563",
      "low": "8518",
      "preclose": "8510",
      "settle": "8476",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 62.2,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 63.8,
        "money_flow": 59.2,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前驱动与资金偏强，总观点为偏多，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力，非24小时新增，只作背景。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.53%；成交量较前快照+18.98%；持仓较前快照+3.47%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8555 对照 MA20 8388.75、MA60 8479.53，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8505、下沿 8270；统计通道上轨 8503.19、下轨 8274.31。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 85.93，用于衡量波动区间和观察位有效性。综合评分 62.20 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO -0.73% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 120.98，豆棕价差 -741。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：豆油库存压力，非24小时新增，只作背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 8555；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 8830.88",
        "stop_loss": "下方观察位 8349.52",
        "upper_watch": "8830.88",
        "lower_watch": "8349.52",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
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
      "price": "8525",
      "change": "+0.60%",
      "volume": "3.65 万手",
      "open_interest": "32.21 万手",
      "direction": "↑",
      "open": "8498",
      "high": "8532",
      "low": "8492",
      "preclose": "8474",
      "settle": "8445",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 57.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 63.8,
        "money_flow": 35.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力，非24小时新增，只作背景。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.60%；成交量较前快照-58.78%；持仓较前快照-40.97%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8525 对照 MA20 8353.75、MA60 8437.22，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8499、下沿 8237；统计通道上轨 8464.39、下轨 8243.11。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 85.43，用于衡量波动区间和观察位有效性。综合评分 57.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO -0.73% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 120.98，豆棕价差 -741。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：豆油库存压力，非24小时新增，只作背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8525；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8610.06 / 下方观察位 8303.65",
        "stop_loss": "下方观察位 8303.65",
        "upper_watch": "8610.06",
        "lower_watch": "8303.65",
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
      "price": "9769",
      "change": "+0.29%",
      "volume": "8.75 万手",
      "open_interest": "25.24 万手",
      "direction": "↑",
      "open": "9755",
      "high": "9798",
      "low": "9736",
      "preclose": "9741",
      "settle": "9692",
      "trade_date": "2026-07-06",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 57.3,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 52.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.29%；成交量较前快照-1.69%；持仓较前快照+7.77%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9769 对照 MA20 9754.05、MA60 9727.52，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10352、下沿 9453；统计通道上轨 10013.37、下轨 9494.73。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 143.21，用于衡量波动区间和观察位有效性。综合评分 57.30 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO -0.73% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 47.15，豆棕价差 -741。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 9769；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10095.29 / 下方观察位 9412.81",
        "stop_loss": "下方观察位 9412.81",
        "upper_watch": "10095.29",
        "lower_watch": "9412.81",
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
      "price": "9755",
      "change": "+0.29%",
      "volume": "1.86 万手",
      "open_interest": "15.72 万手",
      "direction": "↑",
      "open": "9734",
      "high": "9781",
      "low": "9725",
      "preclose": "9727",
      "settle": "9672",
      "trade_date": "2026-07-06",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 53.3,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 32.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.29%；成交量较前快照-79.13%；持仓较前快照-32.89%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9755 对照 MA20 9753.15、MA60 9720.55，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10364、下沿 9458；统计通道上轨 10023.23、下轨 9483.07。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 141.50，用于衡量波动区间和观察位有效性。综合评分 53.30 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO -0.73% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 47.15，豆棕价差 -741。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9755；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10104.17 / 下方观察位 9402.13",
        "stop_loss": "下方观察位 9402.13",
        "upper_watch": "10104.17",
        "lower_watch": "9402.13",
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
      "price": "3044",
      "change": "+0.59%",
      "volume": "41.34 万手",
      "open_interest": "188.72 万手",
      "direction": "↑",
      "open": "3039",
      "high": "3045",
      "low": "3030",
      "preclose": "3026",
      "settle": "3005",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 59.9,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 52.4,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.59%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3044 对照 MA20 2950.30、MA60 2977.45，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2989、下沿 2887；统计通道上轨 3009.75、下轨 2890.85。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 33.93，用于衡量波动区间和观察位有效性。综合评分 59.90 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.73%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3044；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3053.86 / 下方观察位 2921.09",
        "stop_loss": "下方观察位 2921.09",
        "upper_watch": "3053.86",
        "lower_watch": "2921.09",
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
      "price": "3098",
      "change": "+0.55%",
      "volume": "17.03 万手",
      "open_interest": "138.08 万手",
      "direction": "↑",
      "open": "3091",
      "high": "3099",
      "low": "3085",
      "preclose": "3081",
      "settle": "3064",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 59.8,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 52.2,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.55%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3098 对照 MA20 3012.35、MA60 3033.17，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3047、下沿 2966；统计通道上轨 3061.88、下轨 2962.82。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 29.14，用于衡量波动区间和观察位有效性。综合评分 59.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.73%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3098；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3099.77 / 下方观察位 2989.73",
        "stop_loss": "下方观察位 2989.73",
        "upper_watch": "3099.77",
        "lower_watch": "2989.73",
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
      "price": "2319",
      "change": "+0.65%",
      "volume": "27.34 万手",
      "open_interest": "78.78 万手",
      "direction": "↑",
      "open": "2312",
      "high": "2319",
      "low": "2301",
      "preclose": "2304",
      "settle": "2287",
      "trade_date": "2026-07-06",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 53.9,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 52.6,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.65%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2319 对照 MA20 2272.50、MA60 2322.40，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2321、下沿 2214；统计通道上轨 2322.60、下轨 2222.40。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 39.43，用于衡量波动区间和观察位有效性。综合评分 53.90 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.73%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2319；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2345.15 / 下方观察位 2199.85",
        "stop_loss": "下方观察位 2199.85",
        "upper_watch": "2345.15",
        "lower_watch": "2199.85",
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
      "price": "2257",
      "change": "+0.58%",
      "volume": "5.35 万手",
      "open_interest": "31.92 万手",
      "direction": "↑",
      "open": "2248",
      "high": "2258",
      "low": "2243",
      "preclose": "2244",
      "settle": "2230",
      "trade_date": "2026-07-06",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 57.1,
        "technical": 64.0,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 52.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.58%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2257 对照 MA20 2221.55、MA60 2276.78，当前技术评分为 64，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2252、下沿 2188；统计通道上轨 2252.62、下轨 2190.48。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 27.43，用于衡量波动区间和观察位有效性。综合评分 57.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.73%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2257；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2288.28 / 下方观察位 2202.73",
        "stop_loss": "下方观察位 2202.73",
        "upper_watch": "2288.28",
        "lower_watch": "2202.73",
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
      "price": "4483",
      "change": "-0.73%",
      "volume": "2.60 万手",
      "open_interest": "9.50 万手",
      "direction": "↓",
      "open": "4516",
      "high": "4520",
      "low": "4460",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-03",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
      "score": {
        "total": 51.1,
        "technical": 44,
        "fundamental": 50.0,
        "driver": 60.5,
        "money_flow": 47.1,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏空（外盘参考合约，技术历史样本不足）。基本面背景：外盘参考合约，国内基本面因子不直接套用。驱动：FCPO-0.73%（非24小时新增，降权）；CBOT豆油+0.51%（24小时新增）；美豆+2.56%（24小时新增）；WTI/Brent原油-0.20%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.73%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 -6；rapeseed_soybean_spread变化 55。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 4483 对照 MA20 需进一步核验、MA60 需进一步核验，当前技术评分为 需进一步核验，趋势标签为偏空。核心信号为：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 需进一步核验、下沿 需进一步核验；统计通道上轨 需进一步核验、下轨 需进一步核验。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 60，用于衡量波动区间和观察位有效性。综合评分 51.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.73%，CBOT豆油 +0.51%。"
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
        "stance": "分歧震荡",
        "entry": "现价 4483；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4613.32 / 下方观察位 4352.68",
        "stop_loss": "下方观察位 4352.68",
        "upper_watch": "4613.32",
        "lower_watch": "4352.68",
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

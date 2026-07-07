window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-06 22:01",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-01-daily/raw/futures_market_data.json；国内合约名单由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "9288",
      "change": "+0.47%",
      "volume": "11.92 万手",
      "open_interest": "49.88 万手",
      "direction": "↑",
      "open": "9251",
      "high": "9295",
      "low": "9237",
      "preclose": "9245",
      "settle": "9199",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9288 / 行情skill 9287；涨跌幅口径不同：AkShare +0.47% / 行情skill +0.96%",
      "score": {
        "total": 48.4,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 57.8,
        "money_flow": 48.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏空（价格在20日均线下方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.47%；成交量较前快照-11.53%；持仓较前快照+2.21%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9288 对照 MA20 9295.85、MA60 9506.37，当前技术评分为 35，趋势标签为偏空。核心信号为：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9588、下沿 9028；统计通道上轨 9454.88、下轨 9136.82。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 169.57，用于衡量波动区间和观察位有效性。综合评分 48.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 -0.83% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 66.91，豆棕价差 -823。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9288；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9656.31 / 下方观察位 8931.01",
        "stop_loss": "下方观察位 8931.01",
        "upper_watch": "9656.31",
        "lower_watch": "8931.01",
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
      "price": "9555",
      "change": "+0.39%",
      "volume": "2.13 万手",
      "open_interest": "21.15 万手",
      "direction": "↑",
      "open": "9558",
      "high": "9565",
      "low": "9515",
      "preclose": "9518",
      "settle": "9486",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9555 / 行情skill 9556；涨跌幅口径不同：AkShare +0.39% / 行情skill +0.74%",
      "score": {
        "total": 46.5,
        "technical": 35.0,
        "fundamental": 50.0,
        "driver": 57.8,
        "money_flow": 39.6,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏空（价格在20日均线下方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.39%；成交量较前快照-84.16%；持仓较前快照-56.67%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：FCPO偏弱但内盘P走强，需核验内盘资金、价差或政策驱动。；库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9555 对照 MA20 9565.25、MA60 9629.85，当前技术评分为 35，趋势标签为偏空。核心信号为：价格在20日均线下方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9881、下沿 9313；统计通道上轨 9719.13、下轨 9411.37。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 156.36，用于衡量波动区间和观察位有效性。综合评分 46.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 -0.83% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 66.91，豆棕价差 -823。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9555；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9894.61 / 下方观察位 9223.56",
        "stop_loss": "下方观察位 9223.56",
        "upper_watch": "9894.61",
        "lower_watch": "9223.56",
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
      "price": "8549",
      "change": "+0.46%",
      "volume": "7.62 万手",
      "open_interest": "56.44 万手",
      "direction": "↑",
      "open": "8532",
      "high": "8558",
      "low": "8518",
      "preclose": "8510",
      "settle": "8476",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8549 / 行情skill 8548；涨跌幅口径不同：AkShare +0.46% / 行情skill +0.85%",
      "score": {
        "total": 61.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 60.1,
        "money_flow": 61.0,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力，非24小时新增，只作背景。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.46%；成交量较前快照+7.86%；持仓较前快照+0.73%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8549 对照 MA20 8388.45、MA60 8479.43，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8505、下沿 8270；统计通道上轨 8501.16、下轨 8275.74。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 85.50，用于衡量波动区间和观察位有效性。综合评分 61.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO -0.83% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 120.30，豆棕价差 -823。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：豆油库存压力，非24小时新增，只作背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 8549；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 8616.15",
        "stop_loss": "下方观察位 8215.89",
        "upper_watch": "8616.15",
        "lower_watch": "8215.89",
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
      "price": "8520",
      "change": "+0.54%",
      "volume": "2.72 万手",
      "open_interest": "32.02 万手",
      "direction": "↑",
      "open": "8498",
      "high": "8531",
      "low": "8492",
      "preclose": "8474",
      "settle": "8445",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8520 / 行情skill 8520；涨跌幅口径不同：AkShare +0.54% / 行情skill +0.89%",
      "score": {
        "total": 57.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 60.1,
        "money_flow": 41.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力，非24小时新增，只作背景。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.54%；成交量较前快照-61.44%；持仓较前快照-42.85%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8520 对照 MA20 8353.50、MA60 8437.13，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8499、下沿 8237；统计通道上轨 8462.60、下轨 8244.40。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 85.07，用于衡量波动区间和观察位有效性。综合评分 57.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO -0.83% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 120.30，豆棕价差 -823。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：豆油库存压力，非24小时新增，只作背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8520；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8609.59 / 下方观察位 8304.60",
        "stop_loss": "下方观察位 8304.60",
        "upper_watch": "8609.59",
        "lower_watch": "8304.60",
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
      "price": "9771",
      "change": "+0.31%",
      "volume": "6.52 万手",
      "open_interest": "25.44 万手",
      "direction": "↑",
      "open": "9755",
      "high": "9798",
      "low": "9736",
      "preclose": "9741",
      "settle": "9692",
      "trade_date": "2026-07-06",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9771 / 行情skill 9770；涨跌幅口径不同：AkShare +0.31% / 行情skill +0.80%",
      "score": {
        "total": 54.1,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 42.3,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认）。基本面背景：菜油基本面更多看油脂内部轮动。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.31%；成交量较前快照-17.62%；持仓较前快照+3.38%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9771 对照 MA20 9754.15、MA60 9727.55，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10352、下沿 9453；统计通道上轨 10013.50、下轨 9494.80。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 143.36，用于衡量波动区间和观察位有效性。综合评分 54.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO -0.83% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 3.53，豆棕价差 -823。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9771；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10095.50 / 下方观察位 9412.80",
        "stop_loss": "下方观察位 9412.80",
        "upper_watch": "10095.50",
        "lower_watch": "9412.80",
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
      "price": "9757",
      "change": "+0.31%",
      "volume": "1.24 万手",
      "open_interest": "15.67 万手",
      "direction": "↑",
      "open": "9734",
      "high": "9781",
      "low": "9725",
      "preclose": "9727",
      "settle": "9672",
      "trade_date": "2026-07-06",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9757 / 行情skill 9757；涨跌幅口径不同：AkShare +0.31% / 行情skill +0.88%",
      "score": {
        "total": 52.1,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 32.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认）。基本面背景：菜油基本面更多看油脂内部轮动。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.31%；成交量较前快照-84.31%；持仓较前快照-36.32%；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9757 对照 MA20 9753.25、MA60 9720.58，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、区间波动收敛，等待方向确认。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10364、下沿 9458；统计通道上轨 10023.33、下轨 9483.17。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 141.64，用于衡量波动区间和观察位有效性。综合评分 52.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO -0.83% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 3.53，豆棕价差 -823。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9757；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10104.35 / 下方观察位 9402.15",
        "stop_loss": "下方观察位 9402.15",
        "upper_watch": "10104.35",
        "lower_watch": "9402.15",
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
      "price": "3038",
      "change": "+0.40%",
      "volume": "30.45 万手",
      "open_interest": "188.74 万手",
      "direction": "↑",
      "open": "3039",
      "high": "3043",
      "low": "3030",
      "preclose": "3026",
      "settle": "3005",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3038 / 行情skill 3039；涨跌幅口径不同：AkShare +0.40% / 行情skill +1.13%",
      "score": {
        "total": 58.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 51.6,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.40%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3038 对照 MA20 2950、MA60 2977.35，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2989、下沿 2887；统计通道上轨 3007.59、下轨 2892.41。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 33.50，用于衡量波动区间和观察位有效性。综合评分 58.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.83%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3038；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3051.14 / 下方观察位 2921.47",
        "stop_loss": "下方观察位 2921.47",
        "upper_watch": "3051.14",
        "lower_watch": "2921.47",
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
      "price": "3093",
      "change": "+0.39%",
      "volume": "13.01 万手",
      "open_interest": "138.73 万手",
      "direction": "↑",
      "open": "3091",
      "high": "3098",
      "low": "3085",
      "preclose": "3081",
      "settle": "3064",
      "trade_date": "2026-07-07",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3093 / 行情skill 3093；涨跌幅口径不同：AkShare +0.39% / 行情skill +0.95%",
      "score": {
        "total": 58.5,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 51.6,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.39%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3093 对照 MA20 3012.10、MA60 3033.08，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3047、下沿 2966；统计通道上轨 3059.92、下轨 2964.28。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 28.79，用于衡量波动区间和观察位有效性。综合评分 58.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.83%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3093；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3097.35 / 下方观察位 2989.16",
        "stop_loss": "下方观察位 2989.16",
        "upper_watch": "3097.35",
        "lower_watch": "2989.16",
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
      "price": "2310",
      "change": "+0.26%",
      "volume": "18.29 万手",
      "open_interest": "79.40 万手",
      "direction": "↑",
      "open": "2312",
      "high": "2316",
      "low": "2301",
      "preclose": "2304",
      "settle": "2287",
      "trade_date": "2026-07-06",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 52.4,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 51.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.26%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2310 对照 MA20 2272.05、MA60 2322.25，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2321、下沿 2214；统计通道上轨 2320.61、下轨 2223.49。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 38.79，用于衡量波动区间和观察位有效性。综合评分 52.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.83%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2310；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2343.19 / 下方观察位 2201.31",
        "stop_loss": "下方观察位 2201.31",
        "upper_watch": "2343.19",
        "lower_watch": "2201.31",
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
      "price": "2249",
      "change": "+0.22%",
      "volume": "3.73 万手",
      "open_interest": "31.72 万手",
      "direction": "↑",
      "open": "2248",
      "high": "2254",
      "low": "2243",
      "preclose": "2244",
      "settle": "2230",
      "trade_date": "2026-07-06",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 52.4,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 50.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.22%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2249 对照 MA20 2221.15、MA60 2276.65，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2252、下沿 2188；统计通道上轨 2250.55、下轨 2191.75。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 26.86，用于衡量波动区间和观察位有效性。综合评分 52.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.83%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2249；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2267.36 / 下方观察位 2176.39",
        "stop_loss": "下方观察位 2176.39",
        "upper_watch": "2267.36",
        "lower_watch": "2176.39",
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
      "price": "4554",
      "change": "-0.83%",
      "volume": "1.13 万手",
      "open_interest": "8.41 万手",
      "direction": "↓",
      "open": "4592",
      "high": "4598",
      "low": "4539",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-06-30",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
      "score": {
        "total": 49.8,
        "technical": 44,
        "fundamental": 50.0,
        "driver": 56.4,
        "money_flow": 46.7,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏空（外盘参考合约，技术历史样本不足）。基本面背景：外盘参考合约，国内基本面因子不直接套用。驱动：FCPO-0.83%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+2.89%（24小时新增）；WTI/Brent原油-1.12%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.83%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 palm_oil > soybean_oil > rapeseed_oil；soybean_palm_spread变化 74；rapeseed_soybean_spread变化 -97。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 4554 对照 MA20 需进一步核验、MA60 需进一步核验，当前技术评分为 需进一步核验，趋势标签为偏空。核心信号为：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 需进一步核验、下沿 需进一步核验；统计通道上轨 需进一步核验、下轨 需进一步核验。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 59，用于衡量波动区间和观察位有效性。综合评分 49.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO -0.83%，CBOT豆油 +0.51%。"
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
        "entry": "现价 4554；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4682.15 / 下方观察位 4425.85",
        "stop_loss": "下方观察位 4425.85",
        "upper_watch": "4682.15",
        "lower_watch": "4425.85",
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

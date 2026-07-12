module.exports = {
  "updated_at": "2026-07-08 21:28",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-07-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
  "contract_selector_skill": "contract_selector_skill",
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
      "price": "9393",
      "change": "+0.56%",
      "volume": "7.78 万手",
      "open_interest": "48.62 万手",
      "direction": "↑",
      "open": "9384",
      "high": "9403",
      "low": "9372",
      "preclose": "9341",
      "settle": "9344",
      "trade_date": "2026-07-09",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9393 / 行情skill 9394",
      "score": {
        "total": 52.9,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 64.7,
        "money_flow": 41.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.56%；成交量较前快照-55.23%；持仓较前快照-8.40%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9393 对照 MA20 9295.90、MA60 9497.57，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9470、下沿 9028；统计通道上轨 9452.74、下轨 9139.06。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 159.93，用于衡量波动区间和观察位有效性。综合评分 52.90 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +0.04% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -751。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9393；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9561.48 / 下方观察位 9045.64",
        "stop_loss": "下方观察位 9045.64",
        "upper_watch": "9561.48",
        "lower_watch": "9045.64",
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
      "price": "9675",
      "change": "+0.63%",
      "volume": "1.76 万手",
      "open_interest": "21.83 万手",
      "direction": "↑",
      "open": "9656",
      "high": "9682",
      "low": "9643",
      "preclose": "9614",
      "settle": "9616",
      "trade_date": "2026-07-09",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9675 / 行情skill 9675",
      "score": {
        "total": 56.5,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 64.7,
        "money_flow": 41.5,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.63%；成交量较前快照-89.86%；持仓较前快照-58.88%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9675 对照 MA20 9564.05、MA60 9637.33，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9738、下沿 9313；统计通道上轨 9714.45、下轨 9413.65。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 149.86，用于衡量波动区间和观察位有效性。综合评分 56.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +0.04% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -751。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9675；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9823.72 / 下方观察位 9327.93",
        "stop_loss": "下方观察位 9327.93",
        "upper_watch": "9823.72",
        "lower_watch": "9327.93",
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
      "price": "8637",
      "change": "+0.24%",
      "volume": "3.92 万手",
      "open_interest": "61.14 万手",
      "direction": "↑",
      "open": "8642",
      "high": "8654",
      "low": "8630",
      "preclose": "8616",
      "settle": "8611",
      "trade_date": "2026-07-09",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8637 / 行情skill 8637",
      "score": {
        "total": 57.9,
        "technical": 75.0,
        "fundamental": 47.0,
        "driver": 62.6,
        "money_flow": 43.0,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力但仅作背景压力。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.24%；成交量较前快照-36.48%；持仓较前快照+12.74%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8637 对照 MA20 8413、MA60 8483.25，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8598、下沿 8270；统计通道上轨 8578.25、下轨 8247.75。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 84，用于衡量波动区间和观察位有效性。综合评分 57.90 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +0.04% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 125.83，豆棕价差 -751。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47。本轮纳入的可核验因子为：豆油库存压力但仅作背景压力；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8637；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8707.20 / 下方观察位 8356.94",
        "stop_loss": "下方观察位 8356.94",
        "upper_watch": "8707.20",
        "lower_watch": "8356.94",
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
      "price": "8614",
      "change": "+0.17%",
      "volume": "1.18 万手",
      "open_interest": "33.01 万手",
      "direction": "↑",
      "open": "8617",
      "high": "8629",
      "low": "8609",
      "preclose": "8599",
      "settle": "8582",
      "trade_date": "2026-07-09",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8614 / 行情skill 8613",
      "score": {
        "total": 55.0,
        "technical": 75.0,
        "fundamental": 47.0,
        "driver": 62.6,
        "money_flow": 28.7,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：豆油库存压力但仅作背景压力。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.17%；成交量较前快照-80.83%；持仓较前快照-39.13%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8614 对照 MA20 8377、MA60 8442.22，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8570、下沿 8237；统计通道上轨 8545.01、下轨 8208.99。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 84.36，用于衡量波动区间和观察位有效性。综合评分 55 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +0.04% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 125.83，豆棕价差 -751。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47。本轮纳入的可核验因子为：豆油库存压力但仅作背景压力；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8614；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8679.66 / 下方观察位 8325.61",
        "stop_loss": "下方观察位 8325.61",
        "upper_watch": "8679.66",
        "lower_watch": "8325.61",
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
      "price": "9882",
      "change": "+0.39%",
      "volume": "2.80 万手",
      "open_interest": "28.90 万手",
      "direction": "↑",
      "open": "9855",
      "high": "9890",
      "low": "9855",
      "preclose": "9844",
      "settle": "9881",
      "trade_date": "2026-07-08",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9882 / 行情skill 9883；涨跌幅口径不同：AkShare +0.39% / 行情skill +0.02%",
      "score": {
        "total": 58.5,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.6,
        "money_flow": 56.5,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.39%；成交量较前快照-61.79%；持仓较前快照+20.45%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9882 对照 MA20 9743.60、MA60 9742.15，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10037、下沿 9453；统计通道上轨 9976.34、下轨 9510.86。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 142.50，用于衡量波动区间和观察位有效性。综合评分 58.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +0.04% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -751。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9882；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10118.51",
        "stop_loss": "下方观察位 9411.11",
        "upper_watch": "10118.51",
        "lower_watch": "9411.11",
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
      "price": "9875",
      "change": "+0.37%",
      "volume": "3217 手",
      "open_interest": "15.83 万手",
      "direction": "↑",
      "open": "9859",
      "high": "9884",
      "low": "9854",
      "preclose": "9839",
      "settle": "9870",
      "trade_date": "2026-07-08",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9875 / 行情skill 9876；涨跌幅口径不同：AkShare +0.37% / 行情skill +0.06%",
      "score": {
        "total": 55.7,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.6,
        "money_flow": 42.5,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.37%；成交量较前快照-95.61%；持仓较前快照-34.01%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9875 对照 MA20 9741、MA60 9735.03，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10041、下沿 9458；统计通道上轨 9981.42、下轨 9500.58。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 140.64，用于衡量波动区间和观察位有效性。综合评分 55.70 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +0.04% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -751。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9875；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10121.45 / 下方观察位 9420.13",
        "stop_loss": "下方观察位 9420.13",
        "upper_watch": "10121.45",
        "lower_watch": "9420.13",
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
      "price": "3051",
      "change": "0.00%",
      "volume": "14.69 万手",
      "open_interest": "192.06 万手",
      "direction": "→",
      "open": "3058",
      "high": "3061",
      "low": "3049",
      "preclose": "3051",
      "settle": "3045",
      "trade_date": "2026-07-09",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3051 / 行情skill 3051",
      "score": {
        "total": 59.7,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 61.6,
        "money_flow": 50.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅0.00%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3051 对照 MA20 2964.20、MA60 2979.87，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3046、下沿 2887；统计通道上轨 3034.57、下轨 2893.83。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 32.93，用于衡量波动区间和观察位有效性。综合评分 59.70 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 3051；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3088.81 / 下方观察位 2936.38",
        "stop_loss": "下方观察位 2936.38",
        "upper_watch": "3088.81",
        "lower_watch": "2936.38",
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
      "price": "3111",
      "change": "0.00%",
      "volume": "5.02 万手",
      "open_interest": "138.36 万手",
      "direction": "→",
      "open": "3118",
      "high": "3119",
      "low": "3107",
      "preclose": "3111",
      "settle": "3106",
      "trade_date": "2026-07-09",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "价格一致：AkShare 3111 / 行情skill 3111",
      "score": {
        "total": 59.7,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 61.6,
        "money_flow": 50.0,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅0.00%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3111 对照 MA20 3024.35、MA60 3035.80，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3104、下沿 2966；统计通道上轨 3090.48、下轨 2958.22。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 28.79，用于衡量波动区间和观察位有效性。综合评分 59.70 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 3111；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3141.42 / 下方观察位 3004.98",
        "stop_loss": "下方观察位 3004.98",
        "upper_watch": "3141.42",
        "lower_watch": "3004.98",
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
      "price": "2324",
      "change": "+0.82%",
      "volume": "18.38 万手",
      "open_interest": "78.03 万手",
      "direction": "↑",
      "open": "2311",
      "high": "2336",
      "low": "2308",
      "preclose": "2305",
      "settle": "2315",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 57.9,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.6,
        "money_flow": 53.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.82%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2324 对照 MA20 2280.30、MA60 2321.60，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2326、下沿 2214；统计通道上轨 2329.51、下轨 2231.09。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 39.64，用于衡量波动区间和观察位有效性。综合评分 57.90 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 2324；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2352.18 / 下方观察位 2208.42",
        "stop_loss": "下方观察位 2208.42",
        "upper_watch": "2352.18",
        "lower_watch": "2208.42",
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
      "price": "2259",
      "change": "+0.53%",
      "volume": "2.86 万手",
      "open_interest": "33.33 万手",
      "direction": "↑",
      "open": "2253",
      "high": "2268",
      "low": "2250",
      "preclose": "2247",
      "settle": "2256",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill返回空数据）；当前以 AkShare 为准。",
      "score": {
        "total": 54.9,
        "technical": 54.0,
        "fundamental": 50.0,
        "driver": 61.6,
        "money_flow": 52.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.53%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2259 对照 MA20 2226.45、MA60 2274.62，当前技术评分为 54，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2270、下沿 2188；统计通道上轨 2258.35、下轨 2194.55。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 27.43，用于衡量波动区间和观察位有效性。综合评分 54.90 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 2259；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2285.69 / 下方观察位 2178.86",
        "stop_loss": "下方观察位 2178.86",
        "upper_watch": "2285.69",
        "lower_watch": "2178.86",
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
        "driver": 61.6,
        "money_flow": 50.2,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（外盘参考合约，技术历史样本不足）。基本面背景：外盘参考合约，国内基本面因子不直接套用。驱动：FCPO+0.04%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+0.25%（24小时新增）；WTI/Brent原油+0.80%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.04%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -10；rapeseed_soybean_spread变化 86。冲突提示：暂无明显冲突信号。",
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

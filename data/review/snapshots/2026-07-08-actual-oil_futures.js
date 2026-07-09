window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-08 23:14",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-08-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "9422",
      "change": "+0.87%",
      "volume": "22.21 万手",
      "open_interest": "47.76 万手",
      "direction": "↑",
      "open": "9384",
      "high": "9439",
      "low": "9360",
      "preclose": "9341",
      "settle": "9344",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 55.5,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 76.9,
        "money_flow": 35.7,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.87%；成交量较前快照-39.35%；持仓较前快照-3.13%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9422 对照 MA20 9297.35、MA60 9498.05，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9470、下沿 9028；统计通道上轨 9458.24、下轨 9136.46。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 161.93，用于衡量波动区间和观察位有效性。综合评分 55.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +0.68% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -730。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9422；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9562.62 / 下方观察位 9043.84",
        "stop_loss": "下方观察位 9043.84",
        "upper_watch": "9562.62",
        "lower_watch": "9043.84",
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
      "price": "9696",
      "change": "+0.85%",
      "volume": "4.70 万手",
      "open_interest": "22.04 万手",
      "direction": "↑",
      "open": "9656",
      "high": "9715",
      "low": "9640",
      "preclose": "9614",
      "settle": "9616",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 58.1,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 76.9,
        "money_flow": 31.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.85%；成交量较前快照-87.17%；持仓较前快照-55.30%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9696 对照 MA20 9565.10、MA60 9637.68，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9738、下沿 9313；统计通道上轨 9718.84、下轨 9411.36。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 151.36，用于衡量波动区间和观察位有效性。综合评分 58.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +0.68% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -730。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9696；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9824.58 / 下方观察位 9324.78",
        "stop_loss": "下方观察位 9324.78",
        "upper_watch": "9824.58",
        "lower_watch": "9324.78",
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
      "price": "8648",
      "change": "+0.37%",
      "volume": "9.92 万手",
      "open_interest": "61.24 万手",
      "direction": "↑",
      "open": "8642",
      "high": "8657",
      "low": "8616",
      "preclose": "8616",
      "settle": "8611",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 64.2,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 74.7,
        "money_flow": 52.6,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前驱动与资金偏强，总观点为偏多，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.37%；成交量较前快照-51.45%；持仓较前快照+5.72%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8648 对照 MA20 8413.55、MA60 8483.43，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8598、下沿 8270；统计通道上轨 8581.83、下轨 8245.27。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 84，用于衡量波动区间和观察位有效性。综合评分 64.20 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +0.68% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 108，豆棕价差 -730。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏多",
        "entry": "现价 8648；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 8965.87",
        "stop_loss": "下方观察位 8403.90",
        "upper_watch": "8965.87",
        "lower_watch": "8403.90",
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
      "price": "8623",
      "change": "+0.28%",
      "volume": "3.82 万手",
      "open_interest": "33.02 万手",
      "direction": "↑",
      "open": "8617",
      "high": "8629",
      "low": "8585",
      "preclose": "8599",
      "settle": "8582",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 61.7,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 74.7,
        "money_flow": 40.1,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.28%；成交量较前快照-81.33%；持仓较前快照-42.99%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8623 对照 MA20 8377.45、MA60 8442.37，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8570、下沿 8237；统计通道上轨 8548.03、下轨 8206.87。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 84.36，用于衡量波动区间和观察位有效性。综合评分 61.70 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +0.68% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 108，豆棕价差 -730。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8623；区间内等待驱动与资金确认",
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
      "price": "9902",
      "change": "+0.59%",
      "volume": "7.46 万手",
      "open_interest": "28.82 万手",
      "direction": "↑",
      "open": "9855",
      "high": "9918",
      "low": "9855",
      "preclose": "9844",
      "settle": "9881",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 61.8,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 56.6,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.59%；成交量较前快照-63.25%；持仓较前快照+6.99%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9902 对照 MA20 9744.60、MA60 9742.48，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10037、下沿 9453；统计通道上轨 9979.87、下轨 9509.33。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 142.50，用于衡量波动区间和观察位有效性。综合评分 61.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +0.68% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -730。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9902；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10118.51",
        "stop_loss": "下方观察位 9409.58",
        "upper_watch": "10118.51",
        "lower_watch": "9409.58",
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
      "price": "9894",
      "change": "+0.56%",
      "volume": "1.90 万手",
      "open_interest": "15.68 万手",
      "direction": "↑",
      "open": "9859",
      "high": "9910",
      "low": "9854",
      "preclose": "9839",
      "settle": "9870",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 59.1,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 43.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.56%；成交量较前快照-90.62%；持仓较前快照-41.80%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9894 对照 MA20 9741.95、MA60 9735.35，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10041、下沿 9458；统计通道上轨 9984.62、下轨 9499.28。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 140.64，用于衡量波动区间和观察位有效性。综合评分 59.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +0.68% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -730。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9894；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10121.45 / 下方观察位 9418.83",
        "stop_loss": "下方观察位 9418.83",
        "upper_watch": "10121.45",
        "lower_watch": "9418.83",
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
      "price": "3057",
      "change": "+0.20%",
      "volume": "33.81 万手",
      "open_interest": "192.76 万手",
      "direction": "↑",
      "open": "3058",
      "high": "3063",
      "low": "3046",
      "preclose": "3051",
      "settle": "3045",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 63.2,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 50.8,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前驱动与资金偏强，总观点为偏多，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.20%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3057 对照 MA20 2964.50、MA60 2979.97，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3046、下沿 2887；统计通道上轨 3036.38、下轨 2892.62。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 32.93，用于衡量波动区间和观察位有效性。综合评分 63.20 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.68%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 3057；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 3194.56",
        "stop_loss": "下方观察位 2957.67",
        "upper_watch": "3194.56",
        "lower_watch": "2957.67",
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
      "price": "3113",
      "change": "+0.06%",
      "volume": "14.14 万手",
      "open_interest": "136.32 万手",
      "direction": "↑",
      "open": "3118",
      "high": "3120",
      "low": "3103",
      "preclose": "3111",
      "settle": "3106",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 63.1,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 50.3,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前驱动与资金偏强，总观点为偏多，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.06%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3113 对照 MA20 3024.45、MA60 3035.83，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3104、下沿 2966；统计通道上轨 3091.11、下轨 2957.79。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 28.79，用于衡量波动区间和观察位有效性。综合评分 63.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.68%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 3113；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 3232.63",
        "stop_loss": "下方观察位 3024.55",
        "upper_watch": "3232.63",
        "lower_watch": "3024.55",
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
      "price": "2334",
      "change": "+1.26%",
      "volume": "39.98 万手",
      "open_interest": "78.52 万手",
      "direction": "↑",
      "open": "2311",
      "high": "2340",
      "low": "2308",
      "preclose": "2305",
      "settle": "2315",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 64.0,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 55.0,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前驱动与资金偏强，总观点为偏多，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+1.26%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2334 对照 MA20 2280.80、MA60 2321.77，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2326、下沿 2214；统计通道上轨 2331.94、下轨 2229.66。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 39.71，用于衡量波动区间和观察位有效性。综合评分 64 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.68%，CBOT豆油 +0.51%。"
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
        "stance": "偏多",
        "entry": "现价 2334；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 2459.84",
        "stop_loss": "下方观察位 2249.27",
        "upper_watch": "2459.84",
        "lower_watch": "2249.27",
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
      "price": "2263",
      "change": "+0.71%",
      "volume": "7.29 万手",
      "open_interest": "33.78 万手",
      "direction": "↑",
      "open": "2253",
      "high": "2268",
      "low": "2250",
      "preclose": "2247",
      "settle": "2256",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 58.3,
        "technical": 54.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 52.8,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.71%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2263 对照 MA20 2226.65、MA60 2274.68，当前技术评分为 54，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2270、下沿 2188；统计通道上轨 2259.40、下轨 2193.90。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 27.43，用于衡量波动区间和观察位有效性。综合评分 58.30 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2263；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2285.69 / 下方观察位 2178.21",
        "stop_loss": "下方观察位 2178.21",
        "upper_watch": "2285.69",
        "lower_watch": "2178.21",
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
      "price": "4583",
      "change": "+0.68%",
      "volume": "1.95 万手",
      "open_interest": "8.90 万手",
      "direction": "↑",
      "open": "4552",
      "high": "4595",
      "low": "4547",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-07",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
      "score": {
        "total": 58.8,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 52.7,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（外盘参考合约，技术历史样本不足）。基本面背景：外盘参考合约，国内基本面因子不直接套用。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.68%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 4583 对照 MA20 需进一步核验、MA60 需进一步核验，当前技术评分为 需进一步核验，趋势标签为偏多。核心信号为：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 需进一步核验、下沿 需进一步核验；统计通道上轨 需进一步核验、下轨 需进一步核验。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 48，用于衡量波动区间和观察位有效性。综合评分 58.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +0.68%，CBOT豆油 +0.51%。"
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
        "entry": "现价 4583；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 4687.26 / 下方观察位 4478.74",
        "stop_loss": "下方观察位 4478.74",
        "upper_watch": "4687.26",
        "lower_watch": "4478.74",
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

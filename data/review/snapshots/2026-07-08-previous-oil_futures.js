window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-08 08:40",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-08-daily/raw/futures_market_data.json；国内合约名单由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "9302",
      "change": "-0.41%",
      "volume": "17.36 万手",
      "open_interest": "48.90 万手",
      "direction": "↓",
      "open": "9320",
      "high": "9338",
      "low": "9286",
      "preclose": "9340",
      "settle": "9306",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 55.1,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 76.9,
        "money_flow": 34.1,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.41%；成交量较前快照-52.60%；持仓较前快照-0.83%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9302 对照 MA20 9287.60、MA60 9501.22，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9470、下沿 9028；统计通道上轨 9436.75、下轨 9138.45。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 160.71，用于衡量波动区间和观察位有效性。综合评分 55.10 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 9302；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9561.93 / 下方观察位 8952.93",
        "stop_loss": "下方观察位 8952.93",
        "upper_watch": "9561.93",
        "lower_watch": "8952.93",
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
      "price": "9571",
      "change": "-0.35%",
      "volume": "3.23 万手",
      "open_interest": "21.33 万手",
      "direction": "↓",
      "open": "9572",
      "high": "9604",
      "low": "9548",
      "preclose": "9605",
      "settle": "9580",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 56.4,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 76.9,
        "money_flow": 40.6,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.35%；成交量较前快照-91.17%；持仓较前快照-56.74%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9571 对照 MA20 9556.45、MA60 9632.95，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9743、下沿 9313；统计通道上轨 9696.49、下轨 9416.41。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 148.57，用于衡量波动区间和观察位有效性。综合评分 56.40 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 9571；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9827.98 / 下方观察位 9248.30",
        "stop_loss": "下方观察位 9248.30",
        "upper_watch": "9827.98",
        "lower_watch": "9248.30",
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
      "price": "8572",
      "change": "-0.17%",
      "volume": "9.52 万手",
      "open_interest": "59.53 万手",
      "direction": "↓",
      "open": "8637",
      "high": "8637",
      "low": "8562",
      "preclose": "8587",
      "settle": "8564",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 62.2,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 74.7,
        "money_flow": 42.8,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.17%；成交量较前快照-53.44%；持仓较前快照+2.77%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8572 对照 MA20 8396.30、MA60 8480.65，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8523、下沿 8270；统计通道上轨 8526.54、下轨 8266.06。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 83.93，用于衡量波动区间和观察位有效性。综合评分 62.20 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 8572；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8635.65 / 下方观察位 8331.32",
        "stop_loss": "下方观察位 8331.32",
        "upper_watch": "8635.65",
        "lower_watch": "8331.32",
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
      "price": "8539",
      "change": "-0.23%",
      "volume": "2.44 万手",
      "open_interest": "32.77 万手",
      "direction": "↓",
      "open": "8549",
      "high": "8581",
      "low": "8531",
      "preclose": "8559",
      "settle": "8535",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 64.1,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 74.7,
        "money_flow": 52.1,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前驱动与资金偏强，总观点为偏多，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.23%；成交量较前快照-88.07%；持仓较前快照-43.41%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8539 对照 MA20 8359.80、MA60 8438.78，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8492、下沿 8237；统计通道上轨 8486.09、下轨 8233.51。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 83.93，用于衡量波动区间和观察位有效性。综合评分 64.10 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 8539；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 8820.48",
        "stop_loss": "下方观察位 8328.34",
        "upper_watch": "8820.48",
        "lower_watch": "8328.34",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
        "risk_tip": "仅给观察位和失效条件，不构成开平仓指令。",
        "basis": "综合波动、突破、均线和区间测算观察位；共纳入 5 组候选点位，不输出明确交易指令。"
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
      "price": "9868",
      "change": "+0.10%",
      "volume": "8.32 万手",
      "open_interest": "27.88 万手",
      "direction": "↑",
      "open": "9856",
      "high": "9881",
      "low": "9824",
      "preclose": "9858",
      "settle": "9821",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 60.8,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 51.6,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.10%；成交量较前快照-58.99%；持仓较前快照+3.52%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9868 对照 MA20 9745.50、MA60 9734.70，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10148、下沿 9453；统计通道上轨 9982.86、下轨 9508.14。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 144，用于衡量波动区间和观察位有效性。综合评分 60.80 只作多因子结果，技术面不得单独决定总观点。"
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
        "stance": "震荡",
        "entry": "现价 9868；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10180.77 / 下方观察位 9425.78",
        "stop_loss": "下方观察位 9425.78",
        "upper_watch": "10180.77",
        "lower_watch": "9425.78",
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
      "price": "9854",
      "change": "+0.11%",
      "volume": "1.64 万手",
      "open_interest": "15.82 万手",
      "direction": "↑",
      "open": "9846",
      "high": "9867",
      "low": "9811",
      "preclose": "9843",
      "settle": "9806",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 58.8,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 41.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.11%；成交量较前快照-91.94%；持仓较前快照-41.26%；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9854 对照 MA20 9743.55、MA60 9727.67，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10147、下沿 9458；统计通道上轨 9989.95、下轨 9497.15。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 142.07，用于衡量波动区间和观察位有效性。综合评分 58.80 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 9854；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10162.58 / 下方观察位 9415.88",
        "stop_loss": "下方观察位 9415.88",
        "upper_watch": "10162.58",
        "lower_watch": "9415.88",
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
      "price": "3032",
      "change": "-0.43%",
      "volume": "44.64 万手",
      "open_interest": "190.53 万手",
      "direction": "↓",
      "open": "3045",
      "high": "3054",
      "low": "3027",
      "preclose": "3045",
      "settle": "3038",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 62.7,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 48.3,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前驱动与资金偏强，总观点为偏多，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.43%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3032 对照 MA20 2955.75、MA60 2978.32，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3026、下沿 2887；统计通道上轨 3016.83、下轨 2894.67。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 32.64，用于衡量波动区间和观察位有效性。综合评分 62.70 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 3032；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 3158.21",
        "stop_loss": "下方观察位 2943.93",
        "upper_watch": "3158.21",
        "lower_watch": "2943.93",
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
      "price": "3092",
      "change": "-0.29%",
      "volume": "12.37 万手",
      "open_interest": "138.70 万手",
      "direction": "↓",
      "open": "3100",
      "high": "3109",
      "low": "3085",
      "preclose": "3101",
      "settle": "3093",
      "trade_date": "2026-07-08",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 62.8,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 48.8,
        "stance": "偏多",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前驱动与资金偏强，总观点为偏多，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.29%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3092 对照 MA20 3016.95、MA60 3034.17，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3085、下沿 2966；统计通道上轨 3071.18、下轨 2962.72。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 28.50，用于衡量波动区间和观察位有效性。综合评分 62.80 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 3092；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 3201.43",
        "stop_loss": "下方观察位 3013.15",
        "upper_watch": "3201.43",
        "lower_watch": "3013.15",
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
      "price": "2308",
      "change": "-0.43%",
      "volume": "27.43 万手",
      "open_interest": "78.25 万手",
      "direction": "↓",
      "open": "2322",
      "high": "2333",
      "low": "2306",
      "preclose": "2318",
      "settle": "2315",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 56.7,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 48.3,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.43%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2308 对照 MA20 2275.15、MA60 2321.70，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2321、下沿 2214；统计通道上轨 2322.99、下轨 2227.31。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 38.43，用于衡量波动区间和观察位有效性。综合评分 56.70 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 2308；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2344.97 / 下方观察位 2205.33",
        "stop_loss": "下方观察位 2205.33",
        "upper_watch": "2344.97",
        "lower_watch": "2205.33",
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
      "price": "2248",
      "change": "-0.22%",
      "volume": "4.57 万手",
      "open_interest": "32.62 万手",
      "direction": "↓",
      "open": "2262",
      "high": "2268",
      "low": "2245",
      "preclose": "2253",
      "settle": "2256",
      "trade_date": "2026-07-07",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 56.8,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 72.5,
        "money_flow": 49.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+0.68%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆+1.42%（24小时新增）；WTI/Brent原油+5.70%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.22%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > soybean_oil > palm_oil；soybean_palm_spread变化 17；rapeseed_soybean_spread变化 17。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2248 对照 MA20 2223.15、MA60 2275.50，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2252、下沿 2188；统计通道上轨 2252.74、下轨 2193.56。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 27.50，用于衡量波动区间和观察位有效性。综合评分 56.80 只作多因子结果，技术面不得单独决定总观点。"
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
        "entry": "现价 2248；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2268.47 / 下方观察位 2177.83",
        "stop_loss": "下方观察位 2177.83",
        "upper_watch": "2268.47",
        "lower_watch": "2177.83",
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

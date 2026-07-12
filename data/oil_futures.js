window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-09 16:36",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-09-daily/raw/futures_market_data.json；国内合约名单先由 contract_selector_skill 选择，再由 contract_discovery_skill 按当月实时成交量、持仓量、成交额排序生成，外盘仅展示与棕榈油最相关的 FCPO；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
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
      "price": "4607",
      "change": "+1.25%",
      "unit": "林吉特/吨",
      "updated_at": "2026-07-08",
      "source": "tradingview:MYX:FCPO1!"
    },
    "india_cpo_spot": {
      "label": "印度 NCDEX CPO 现货",
      "location": "Kandla",
      "price": "1354.10",
      "change": "-0.18%",
      "unit": "印度卢比/10公斤",
      "updated_at": "2026-07-10 15:24",
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
      "price": "9354",
      "change": "+0.14%",
      "volume": "48.88 万手",
      "open_interest": "46.74 万手",
      "direction": "↑",
      "open": "9384",
      "high": "9439",
      "low": "9331",
      "preclose": "9341",
      "settle": "9344",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 56.8,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 67.4,
        "money_flow": 56.6,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前驱动与资金偏强，总观点为震荡偏强，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.14%；成交量较前快照+181.52%；持仓较前快照-4.41%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9354 对照 MA20 9293.95、MA60 9496.92，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9470、下沿 9028；统计通道上轨 9446.83、下轨 9141.07。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 159.93，用于衡量波动区间和观察位有效性。综合评分 56.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +1.25% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -763。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9354；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 9561.48",
        "stop_loss": "下方观察位 8986.16",
        "upper_watch": "9561.48",
        "lower_watch": "8986.16",
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
      "price": "9630",
      "change": "+0.17%",
      "volume": "11.38 万手",
      "open_interest": "21.71 万手",
      "direction": "↑",
      "open": "9656",
      "high": "9715",
      "low": "9606",
      "preclose": "9614",
      "settle": "9662",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 53.4,
        "technical": 51.0,
        "fundamental": 50.0,
        "driver": 67.4,
        "money_flow": 39.7,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "棕榈油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示震荡（价格在20日均线上方、均线结构震荡）。基本面背景：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.17%；成交量较前快照-34.48%；持仓较前快照-55.60%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9630 对照 MA20 9561.80、MA60 9636.58，当前技术评分为 51，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9738、下沿 9313；统计通道上轨 9706.74、下轨 9416.86。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 148.93，用于衡量波动区间和观察位有效性。综合评分 53.40 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 +1.25% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -763。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：棕榈油库存偏高，非24小时新增，只作背景；豆棕价差用于相对强弱背景；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9630；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 9823.19 / 下方观察位 9306.53",
        "stop_loss": "下方观察位 9306.53",
        "upper_watch": "9823.19",
        "lower_watch": "9306.53",
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
      "price": "8610",
      "change": "-0.07%",
      "volume": "23.60 万手",
      "open_interest": "60.85 万手",
      "direction": "↓",
      "open": "8642",
      "high": "8657",
      "low": "8580",
      "preclose": "8616",
      "settle": "8623",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 57.5,
        "technical": 68.0,
        "fundamental": 50.0,
        "driver": 62.3,
        "money_flow": 46.7,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.07%；成交量较前快照+147.94%；持仓较前快照+2.22%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8610 对照 MA20 8426.45、MA60 8484.63，当前技术评分为 68，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8650、下沿 8270；统计通道上轨 8602.02、下轨 8250.88。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 82.79，用于衡量波动区间和观察位有效性。综合评分 57.50 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +1.25% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 102.17，豆棕价差 -763。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价 8610；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 8697.35 / 下方观察位 8222.65",
        "stop_loss": "下方观察位 8222.65",
        "upper_watch": "8697.35",
        "lower_watch": "8222.65",
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
      "price": "8587",
      "change": "-0.14%",
      "volume": "8.23 万手",
      "open_interest": "33.28 万手",
      "direction": "↓",
      "open": "8617",
      "high": "8629",
      "low": "8543",
      "preclose": "8599",
      "settle": "8596",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 58.2,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 62.3,
        "money_flow": 41.4,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.14%；成交量较前快照-13.49%；持仓较前快照-44.09%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8587 对照 MA20 8375.65、MA60 8441.77，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8570、下沿 8237；统计通道上轨 8536.30、下轨 8215.00。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 84.36，用于衡量波动区间和观察位有效性。综合评分 58.20 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO +1.25% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 102.17，豆棕价差 -763。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：基本面暂无强新增驱动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 8587；区间内等待驱动与资金确认",
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
      "volume": "22.36 万手",
      "open_interest": "29.17 万手",
      "direction": "↑",
      "open": "9855",
      "high": "9929",
      "low": "9855",
      "preclose": "9844",
      "settle": "9897",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 61.0,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 68.5,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.59%；成交量较前快照+168.67%；持仓较前快照+4.62%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9902 对照 MA20 9742.65、MA60 9749.22，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9996、下沿 9453；统计通道上轨 9973.91、下轨 9511.39。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 136.36，用于衡量波动区间和观察位有效性。综合评分 61 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +1.25% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -763。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡偏强",
        "entry": "现价 9902；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 10074.00",
        "stop_loss": "下方观察位 9415.94",
        "upper_watch": "10074.00",
        "lower_watch": "9415.94",
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
      "price": "9892",
      "change": "+0.54%",
      "volume": "6.29 万手",
      "open_interest": "15.63 万手",
      "direction": "↑",
      "open": "9859",
      "high": "9922",
      "low": "9854",
      "preclose": "9839",
      "settle": "9889",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 56.0,
        "technical": 65.0,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 43.2,
        "stance": "分歧震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "低",
        "contradiction_warning": "库存偏高但价格上涨，库存不能单独解释今日方向。"
      },
      "view": "菜油当前信号分歧，按震荡处理，总观点为分歧震荡，置信度低；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面背景：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.54%；成交量较前快照-24.36%；持仓较前快照-43.96%；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：库存偏高但价格上涨，库存不能单独解释今日方向。。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9892 对照 MA20 9739.40、MA60 9741.78，当前技术评分为 65，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10000、下沿 9458；统计通道上轨 9976.81、下轨 9501.99。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 134.21，用于衡量波动区间和观察位有效性。综合评分 56 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO +1.25% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 33.65，豆棕价差 -763。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 50。本轮纳入的可核验因子为：菜油库存压力，非24小时新增，只作背景；菜油基本面更多看油脂内部轮动；库存、基差、进口利润、压榨利润只作背景压力，非24小时信息不得作为今日主线加减分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "分歧震荡",
        "entry": "现价 9892；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 10076.77 / 下方观察位 9425.22",
        "stop_loss": "下方观察位 9425.22",
        "upper_watch": "10076.77",
        "lower_watch": "9425.22",
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
      "price": "3052",
      "change": "+0.03%",
      "volume": "93.20 万手",
      "open_interest": "190.85 万手",
      "direction": "↑",
      "open": "3058",
      "high": "3063",
      "low": "3034",
      "preclose": "3051",
      "settle": "3045",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 59.8,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 50.1,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.03%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3052 对照 MA20 2964.25、MA60 2979.88，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3046、下沿 2887；统计通道上轨 3034.87、下轨 2893.63。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 32.93，用于衡量波动区间和观察位有效性。综合评分 59.80 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +1.25%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3052；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3088.81 / 下方观察位 2936.26",
        "stop_loss": "下方观察位 2936.26",
        "upper_watch": "3088.81",
        "lower_watch": "2936.26",
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
      "price": "3110",
      "change": "-0.03%",
      "volume": "33.36 万手",
      "open_interest": "136.61 万手",
      "direction": "↓",
      "open": "3118",
      "high": "3120",
      "low": "3091",
      "preclose": "3111",
      "settle": "3107",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "M 用于观察豆系蛋白粕与油脂之间的资金和压榨链条联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 58.0,
        "technical": 68.0,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 49.9,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "豆粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示偏多（价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅-0.03%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 3110 对照 MA20 3030.10、MA60 3037.22，当前技术评分为 68，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 3122、下沿 2966；统计通道上轨 3104.50、下轨 2955.70。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 29.07，用于衡量波动区间和观察位有效性。综合评分 58 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +1.25%，CBOT豆油 +0.51%。"
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
        "entry": "现价 3110；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 3138.63 / 下方观察位 2949.37",
        "stop_loss": "下方观察位 2949.37",
        "upper_watch": "3138.63",
        "lower_watch": "2949.37",
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
      "price": "2338",
      "change": "+1.43%",
      "volume": "90.47 万手",
      "open_interest": "77.74 万手",
      "direction": "↑",
      "open": "2311",
      "high": "2340",
      "low": "2308",
      "preclose": "2305",
      "settle": "2329",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 61.0,
        "technical": 75.0,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 55.7,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（价格在20日均线上方、均线结构震荡、突破20日区间上沿）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+1.43%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2338 对照 MA20 2284.30、MA60 2321.20，当前技术评分为 75，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡、突破20日区间上沿。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2333、下沿 2214；统计通道上轨 2333.51、下轨 2235.09。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 40.57，用于衡量波动区间和观察位有效性。综合评分 61 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +1.25%，CBOT豆油 +0.51%。"
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
        "stance": "震荡偏强",
        "entry": "现价 2338；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 2386.26",
        "stop_loss": "下方观察位 2206.69",
        "upper_watch": "2386.26",
        "lower_watch": "2206.69",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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
      "price": "2267",
      "change": "+0.89%",
      "volume": "15.71 万手",
      "open_interest": "33.51 万手",
      "direction": "↑",
      "open": "2253",
      "high": "2272",
      "low": "2250",
      "preclose": "2247",
      "settle": "2261",
      "trade_date": "2026-07-09",
      "source": "akshare:futures_zh_realtime",
      "note": "RM 用于观察菜系供需、资金迁移与菜油联动。",
      "verification": "行情skill核验：未完成（行情skill未配置 IWENCAI_API_KEY）；当前以 AkShare 为准。",
      "score": {
        "total": 55.3,
        "technical": 54.0,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 53.6,
        "stance": "震荡",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "中",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "菜粕当前行情偏震荡，等待驱动确认，总观点为震荡，置信度中；技术面显示震荡（价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧）。基本面背景：基本面暂无强新增驱动。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+0.89%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 2267 对照 MA20 2228.90、MA60 2273.45，当前技术评分为 54，趋势标签为震荡。核心信号为：价格在20日均线上方、均线结构震荡、处于统计区间上沿外侧。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 2270、下沿 2188；统计通道上轨 2262.23、下轨 2195.57。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 28，用于衡量波动区间和观察位有效性。综合评分 55.30 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +1.25%，CBOT豆油 +0.51%。"
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
        "entry": "现价 2267；区间内等待驱动与资金确认",
        "take_profit": "上方观察位 2286.02 / 下方观察位 2179.55",
        "stop_loss": "下方观察位 2179.55",
        "upper_watch": "2286.02",
        "lower_watch": "2179.55",
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
      "price": "4607",
      "change": "+1.25%",
      "volume": "2.91 万手",
      "open_interest": "9.48 万手",
      "direction": "↑",
      "open": "4550",
      "high": "4618",
      "low": "4528",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-08",
      "source": "tradingview:MYX:FCPO1!",
      "note": "FCPO 是棕榈油最直接的外盘参考，只用于观察产地盘面对 P 的传导。",
      "verification": "外盘只展示与棕榈油最相关的 FCPO；暂不使用同花顺问财核验，以公开外盘数据源为准。",
      "score": {
        "total": 56.1,
        "technical": 56,
        "fundamental": 50.0,
        "driver": 61.9,
        "money_flow": 55.0,
        "stance": "震荡偏强",
        "weights": "技术面25% / 基本面25% / 驱动30% / 资金20%",
        "view_confidence": "高",
        "contradiction_warning": "暂无明显冲突信号"
      },
      "view": "马棕油当前驱动与资金偏强，总观点为震荡偏强，置信度高；技术面显示偏多（外盘参考合约，技术历史样本不足）。基本面背景：外盘参考合约，国内基本面因子不直接套用。驱动：FCPO+1.25%（24小时新增）；CBOT豆油+0.51%（24小时新增）；美豆-0.31%（24小时新增）；WTI/Brent原油-0.10%（24小时新增）；天气出现24小时内可核验扰动；当日新增政策/新闻纳入驱动；周度库存不作为今日主驱动。资金：当日涨跌幅+1.25%；成交量变化需进一步核验；持仓变化需进一步核验；板块强弱排序 rapeseed_oil > palm_oil > soybean_oil；soybean_palm_spread变化 -33；rapeseed_soybean_spread变化 13。冲突提示：暂无明显冲突信号。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 4607 对照 MA20 需进一步核验、MA60 需进一步核验，当前技术评分为 需进一步核验，趋势标签为偏多。核心信号为：外盘参考合约，技术历史样本不足。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 需进一步核验、下沿 需进一步核验；统计通道上轨 需进一步核验、下轨 需进一步核验。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 90，用于衡量波动区间和观察位有效性。综合评分 56.10 只作多因子结果，技术面不得单独决定总观点。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "外盘涨跌幅用于观察情绪传导：FCPO +1.25%，CBOT豆油 +0.51%。"
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
        "stance": "震荡偏强",
        "entry": "现价 4607；观察回撤后能否守住下方关键位",
        "take_profit": "上方观察位 4802.48",
        "stop_loss": "下方观察位 4400",
        "upper_watch": "4802.48",
        "lower_watch": "4400",
        "invalidation": "若驱动评分与资金评分同步转弱，当前偏强判断失效。",
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

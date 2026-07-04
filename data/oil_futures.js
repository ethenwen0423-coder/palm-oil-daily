window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-04 10:29",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-03-daily/raw/futures_market_data.json；主卡片展示国内油脂主力合约，内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证；外盘仅作为联动因子纳入评分",
  "contracts": [
    {
      "symbol": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2609",
      "price": "9169",
      "change": "+0.71%",
      "volume": "17.38 万手",
      "open_interest": "53.08 万手",
      "direction": "↑",
      "open": "9090",
      "high": "9175",
      "low": "9084",
      "preclose": "9104",
      "settle": "9148",
      "trade_date": "2026-07-06",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格一致：AkShare 9169 / 行情skill 9169；涨跌幅口径不同：AkShare +0.71% / 行情skill +0.23%",
      "score": {
        "total": 28.3,
        "technical": 20.0,
        "fundamental": 47.6,
        "stance": "偏空",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "棕榈油当前行情偏弱，反弹压力优先；技术面显示偏空（价格在20日均线下方、均线空头排列）。基本面：FCPO联动；棕榈油库存偏高；豆棕价差仍支撑P相对强弱。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9169 对照 MA20 9303.80、MA60 9519.12，当前技术评分为 20，趋势标签为偏空。核心信号为：价格在20日均线下方、均线空头排列。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 9825、下沿 9028；统计通道上轨 9453.35、下轨 9154.25。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 166.29，用于衡量止损宽度和止盈弹性。综合评分 28.30 低于强势阈值时，不宜把反弹直接视为趋势反转。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "FCPO涨跌幅 -0.09% 是P的外盘弹性来源，CBOT豆油 +0.51% 影响油脂板块共振。"
        },
        {
          "title": "库存与价差",
          "text": "棕榈油库存 67.54，豆棕价差 -735。库存偏高会压制单边上行，价差偏低则仍支撑P相对强弱。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47.60。本轮纳入的可核验因子为：FCPO联动；棕榈油库存偏高；豆棕价差仍支撑P相对强弱；未能核验的政策、天气、基差和进口利润不直接上调评分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏空",
        "entry": "现价附近 9169；反弹不过压力时偏空处理",
        "take_profit": "8634.47",
        "stop_loss": "9488.65",
        "basis": "综合波动、突破、均线、区间和风险回报测算后取加权中枢；共纳入 5 组候选点位。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "评分、观点与策略已通过skill质量检查"
    },
    {
      "symbol": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2609",
      "price": "8428",
      "change": "+0.26%",
      "volume": "6.18 万手",
      "open_interest": "54.23 万手",
      "direction": "↑",
      "open": "8403",
      "high": "8430",
      "low": "8393",
      "preclose": "8406",
      "settle": "8423",
      "trade_date": "2026-07-06",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8428 / 行情skill 8428",
      "score": {
        "total": 61.6,
        "technical": 69.0,
        "fundamental": 44.5,
        "stance": "震荡",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "豆油当前行情偏震荡，等待突破确认；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面：CBOT豆油联动；豆油库存压力。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 8428 对照 MA20 8384.10、MA60 8483.12，当前技术评分为 69，趋势标签为偏多。核心信号为：价格在20日均线上方、均线结构震荡。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 8630、下沿 8270；统计通道上轨 8474.96、下轨 8293.24。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 79，用于衡量止损宽度和止盈弹性。综合评分 61.60 低于强势阈值时，不宜把反弹直接视为趋势反转。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油涨跌幅 +0.51% 是Y的主要外盘锚，FCPO -0.09% 影响油脂整体风险偏好。"
        },
        {
          "title": "库存与价差",
          "text": "豆油库存 120.98，豆棕价差 -735。库存高位会限制豆油独立上攻，价差变化决定对P的拖累或托底。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 44.50。本轮纳入的可核验因子为：CBOT豆油联动；豆油库存压力；未能核验的政策、天气、基差和进口利润不直接上调评分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "震荡",
        "entry": "现价附近 8428；区间内等待突破确认",
        "take_profit": "上沿 8599.59 / 下沿 8248.05",
        "stop_loss": "8425.66",
        "basis": "综合波动、突破、均线、区间和风险回报测算后取加权中枢；共纳入 4 组候选点位。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "评分、观点与策略已通过skill质量检查"
    },
    {
      "symbol": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2609",
      "price": "9625",
      "change": "-0.20%",
      "volume": "7.33 万手",
      "open_interest": "23.99 万手",
      "direction": "↓",
      "open": "9644",
      "high": "9669",
      "low": "9605",
      "preclose": "9644",
      "settle": "9604",
      "trade_date": "2026-07-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9625 / 行情skill 9625；涨跌幅口径不同：AkShare -0.20% / 行情skill +0.22%",
      "score": {
        "total": 28.1,
        "technical": 20.0,
        "fundamental": 47.0,
        "stance": "偏空",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "菜油当前行情偏弱，反弹压力优先；技术面显示偏空（价格在20日均线下方、短均线转弱）。基本面：菜油库存压力；油脂板块共振。",
      "technical_detail": [
        {
          "title": "趋势结构",
          "text": "现价 9625 对照 MA20 9764.15、MA60 9726.20，当前技术评分为 20，趋势标签为偏空。核心信号为：价格在20日均线下方、短均线转弱。"
        },
        {
          "title": "支撑压力",
          "text": "20日价格区间上沿 10416、下沿 9453；统计通道上轨 10044.93、下轨 9483.37。这些位置决定突破确认和反抽压力。"
        },
        {
          "title": "波动与执行",
          "text": "14日平均波动幅度约 139.86，用于衡量止损宽度和止盈弹性。综合评分 28.10 低于强势阈值时，不宜把反弹直接视为趋势反转。"
        }
      ],
      "fundamental_detail": [
        {
          "title": "外盘联动",
          "text": "CBOT豆油 +0.51% 和FCPO -0.09% 共同决定油脂共振强度，OI当前更多看相对强弱切换。"
        },
        {
          "title": "库存与价差",
          "text": "菜油库存 37.40，豆棕价差 -735。菜油更偏油脂内部轮动，若库存压力不缓解，追涨持续性受限。"
        },
        {
          "title": "评分解释",
          "text": "基本面评分 47。本轮纳入的可核验因子为：菜油库存压力；油脂板块共振；未能核验的政策、天气、基差和进口利润不直接上调评分。"
        }
      ],
      "strategy_recommendation": {
        "stance": "偏空",
        "entry": "现价附近 9625；反弹不过压力时偏空处理",
        "take_profit": "9044.71",
        "stop_loss": "9962.48",
        "basis": "综合波动、突破、均线、区间和风险回报测算后取加权中枢；共纳入 5 组候选点位。"
      },
      "analysis_skill": "master_analytic_skill",
      "child_skill": "technical_basic_analysis_skill",
      "quality_note": "评分、观点与策略已通过skill质量检查"
    }
  ]
};

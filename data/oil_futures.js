window.OIL_FUTURES_CONTRACTS = {
  "updated_at": "2026-07-03 14:40",
  "source": "futures-oil-daily 最新快照：source_runs/2026-07-03-daily/raw/futures_market_data.json；内盘具体合约与日线缺口由 AkShare 补充，并用同花顺问财行情skill交叉验证",
  "contracts": [
    {
      "symbol": "P",
      "name": "棕榈油",
      "market": "DCE",
      "contract": "P2609",
      "price": "9106",
      "change": "-0.63%",
      "volume": "53.69 万手",
      "open_interest": "53.65 万手",
      "direction": "↓",
      "open": "9171",
      "high": "9211",
      "low": "9106",
      "preclose": "9164",
      "settle": "9236",
      "trade_date": "2026-07-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "P 是棕榈油报告主线，重点看持仓与豆油、菜油共振。",
      "verification": "价格不一致：AkShare 9106 / 行情skill 9112；涨跌幅口径不同：AkShare -0.63% / 行情skill -1.34%",
      "score": {
        "total": 28.3,
        "technical": 20.0,
        "fundamental": 47.6,
        "stance": "偏空",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "棕榈油当前行情偏弱，反弹压力优先；技术面显示偏空（价格在20日均线下方、均线空头排列、跌破布林下轨）。基本面：FCPO联动；棕榈油库存偏高；豆棕价差仍支撑P相对强弱。",
      "strategies": [
        {
          "name": "ATR趋势",
          "entry": "现价附近 9106",
          "take_profit": "8599",
          "stop_loss": "9444"
        },
        {
          "name": "海龟20日突破",
          "entry": "9028",
          "take_profit": "8690",
          "stop_loss": "9366"
        }
      ]
    },
    {
      "symbol": "Y",
      "name": "豆油",
      "market": "DCE",
      "contract": "Y2609",
      "price": "8412",
      "change": "-0.15%",
      "volume": "18.76 万手",
      "open_interest": "54.53 万手",
      "direction": "↓",
      "open": "8435",
      "high": "8455",
      "low": "8405",
      "preclose": "8425",
      "settle": "8442",
      "trade_date": "2026-07-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "Y 用于观察豆系对棕榈油的共振或拖累。",
      "verification": "价格一致：AkShare 8412 / 行情skill 8410",
      "score": {
        "total": 61.6,
        "technical": 69.0,
        "fundamental": 44.5,
        "stance": "震荡",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "豆油当前行情偏震荡，等待突破确认；技术面显示偏多（价格在20日均线上方、均线结构震荡）。基本面：CBOT豆油联动；豆油库存压力。",
      "strategies": [
        {
          "name": "ATR区间",
          "entry": "8270 - 8630",
          "take_profit": "上沿 8630 / 下沿 8270",
          "stop_loss": "上破 8709.43 或下破 8190.57"
        },
        {
          "name": "海龟20日突破",
          "entry": "上破 8630 或下破 8270",
          "take_profit": "顺势 2ATR：8570.86 / 8253.14",
          "stop_loss": "反向 1ATR：8332.57 / 8491.43"
        }
      ]
    },
    {
      "symbol": "OI",
      "name": "菜油",
      "market": "CZCE",
      "contract": "OI2609",
      "price": "9640",
      "change": "+0.72%",
      "volume": "21.42 万手",
      "open_interest": "24.05 万手",
      "direction": "↑",
      "open": "9593",
      "high": "9656",
      "low": "9550",
      "preclose": "9571",
      "settle": "9601",
      "trade_date": "2026-07-03",
      "source": "AkShare + 同花顺问财行情skill",
      "note": "OI 用于观察油脂内部轮动和相对强弱切换。",
      "verification": "价格一致：AkShare 9640 / 行情skill 9638；涨跌幅口径不同：AkShare +0.72% / 行情skill +0.39%",
      "score": {
        "total": 28.1,
        "technical": 20.0,
        "fundamental": 47.0,
        "stance": "偏空",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "菜油当前行情偏弱，反弹压力优先；技术面显示偏空（价格在20日均线下方、短均线转弱）。基本面：菜油库存压力；油脂板块共振。",
      "strategies": [
        {
          "name": "ATR趋势",
          "entry": "现价附近 9640",
          "take_profit": "9213.14",
          "stop_loss": "9924.57"
        },
        {
          "name": "海龟20日突破",
          "entry": "9453",
          "take_profit": "9168.43",
          "stop_loss": "9737.57"
        }
      ]
    },
    {
      "symbol": "FCPO",
      "name": "马棕油",
      "market": "BMD",
      "contract": "FCPOU2026",
      "price": "4547",
      "change": "-0.09%",
      "volume": "1.17 万手",
      "open_interest": "8.01 万手",
      "direction": "↓",
      "open": "4551",
      "high": "4570",
      "low": "4536",
      "preclose": "需进一步核验",
      "settle": "需进一步核验",
      "trade_date": "2026-07-02",
      "source": "tradingview:MYX:FCPO1!",
      "note": "产地盘面决定 P 的外盘弹性。",
      "verification": "外盘合约暂不使用同花顺问财核验；以公开外盘数据源为准。",
      "score": {
        "total": 44.4,
        "technical": 42,
        "fundamental": 50,
        "stance": "震荡",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "马棕油作为外盘参考，当前按震荡处理；主要用于判断内盘油脂情绪传导，不单独作为交易指令。",
      "strategies": [
        {
          "name": "ATR区间",
          "entry": "4496 - 4598",
          "take_profit": "上沿 4598 / 下沿 4496",
          "stop_loss": "上破 4632 或下破 4462"
        },
        {
          "name": "海龟20日突破",
          "entry": "上破 4598 或下破 4496",
          "take_profit": "顺势 2ATR：4615 / 4479",
          "stop_loss": "反向 1ATR：4513 / 4581"
        }
      ]
    },
    {
      "symbol": "CBOT BO",
      "name": "CBOT 豆油",
      "market": "CME",
      "contract": "BO=F",
      "price": "31.68",
      "change": "+0.51%",
      "volume": "3.97 万手",
      "open_interest": "需进一步核验",
      "direction": "↑",
      "open": "需进一步核验",
      "high": "31.71",
      "low": "31.34",
      "preclose": "31.52",
      "settle": "需进一步核验",
      "trade_date": "2026-07-03",
      "source": "yahoo:BO=F",
      "note": "美豆油用于观察全球油脂链条共振。",
      "verification": "外盘合约暂不使用同花顺问财核验；以公开外盘数据源为准。",
      "score": {
        "total": 55.6,
        "technical": 58,
        "fundamental": 50,
        "stance": "震荡",
        "weights": "技术面70% / 基本面30%"
      },
      "view": "CBOT 豆油作为外盘参考，当前按震荡处理；主要用于判断内盘油脂情绪传导，不单独作为交易指令。",
      "strategies": [
        {
          "name": "ATR区间",
          "entry": "31.12 - 32.23",
          "take_profit": "上沿 32.23 / 下沿 31.12",
          "stop_loss": "上破 32.61 或下破 30.75"
        },
        {
          "name": "海龟20日突破",
          "entry": "上破 32.23 或下破 31.12",
          "take_profit": "顺势 2ATR：32.42 / 30.94",
          "stop_loss": "反向 1ATR：31.31 / 32.05"
        }
      ]
    }
  ]
};

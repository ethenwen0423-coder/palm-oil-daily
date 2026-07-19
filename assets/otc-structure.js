(function () {
  const dataset = window.OIL_FUTURES_CONTRACTS || {};
  const contracts = Array.isArray(dataset.contracts) ? dataset.contracts : [];
  const form = document.querySelector("#otc-form");
  const contractSelect = document.querySelector("#otc-contract");
  const formError = document.querySelector("#otc-form-error");
  const result = document.querySelector("#otc-result");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function number(value) {
    const parsed = Number(String(value ?? "").replaceAll(",", ""));
    return Number.isFinite(parsed) ? parsed : null;
  }

  function format(value, digits = 0) {
    const parsed = number(value);
    if (parsed === null) return "需进一步核验";
    return parsed.toLocaleString("zh-CN", { maximumFractionDigits: digits });
  }

  function technicalText(contract, index) {
    return String(contract.technical_detail?.[index]?.text || "");
  }

  function capture(text, pattern) {
    const match = String(text).match(pattern);
    return match ? number(match[1]) : null;
  }

  function marketSnapshot(contract) {
    const price = number(contract.price);
    const trend = technicalText(contract, 0);
    const volatility = technicalText(contract, 2);
    const ma20 = capture(trend, /MA20\s*([\d,.]+)/i);
    const ma60 = capture(trend, /MA60\s*([\d,.]+)/i);
    const atr = capture(volatility, /波动幅度约\s*([\d,.]+)/);
    const stance = String(contract.score?.stance || "方向不明");
    const confidence = String(contract.score?.view_confidence || "需进一步核验");
    const aboveBoth = price !== null && ma20 !== null && ma60 !== null && price > ma20 && price > ma60;
    const belowBoth = price !== null && ma20 !== null && ma60 !== null && price < ma20 && price < ma60;
    let direction = "neutral";

    if (aboveBoth) direction = "bullish";
    else if (belowBoth) direction = "bearish";
    else if (/偏强|偏多|看多|多头/.test(stance)) direction = "bullish";
    else if (/偏弱|偏空|看空|空头/.test(stance)) direction = "bearish";

    return {
      price,
      ma20,
      ma60,
      atr,
      atrPct: price && atr ? atr / price * 100 : null,
      stance,
      confidence,
      direction,
      marketLabel: direction === "bullish" ? "震荡偏强" : direction === "bearish" ? "震荡偏弱" : "方向不明",
    };
  }

  function recommend(contract) {
    const market = marketSnapshot(contract);
    const confirmed = market.confidence !== "低";
    const lowVolatility = market.atrPct !== null && market.atrPct < 1;
    const maSummary = market.ma20 !== null && market.ma60 !== null
      ? `最新价 ${format(market.price)}，MA20 为 ${format(market.ma20, 2)}，MA60 为 ${format(market.ma60, 2)}`
      : `最新价 ${format(market.price)}，均线数据需进一步核验`;

    if (market.direction === "bullish") {
      if (confirmed && lowVolatility) {
        return {
          market,
          structure: "正向气囊宝1.0（虚值行权 + 收益封顶）",
          reason: `${maSummary}，价格位于两条均线上方，方向偏强；ATR占价格约 ${market.atrPct.toFixed(2)}%，波动偏低，适合用虚值行权与收益封顶提高上涨参与效率，同时保留回撤安全垫。`,
        };
      }
      return {
        market,
        structure: "正向气囊宝1.0（标准型）",
        reason: `${maSummary}，技术方向偏强；但当前${market.confidence === "低" ? "观点置信度偏低" : "波动不低"}，采用标准型参与上涨并保留安全垫，暂不叠加参与率增强。`,
      };
    }

    if (market.direction === "bearish") {
      if (confirmed && lowVolatility) {
        return {
          market,
          structure: "反向气囊宝1.0（虚值行权 + 收益封顶）",
          reason: `${maSummary}，价格位于两条均线下方，方向偏弱；ATR占价格约 ${market.atrPct.toFixed(2)}%，波动偏低，适合用虚值行权与收益封顶提高下跌参与效率，同时保留反弹安全垫。`,
        };
      }
      return {
        market,
        structure: "反向气囊宝1.0（标准型）",
        reason: `${maSummary}，技术方向偏弱；但当前${market.confidence === "低" ? "观点置信度偏低" : "波动不低"}，采用标准型参与下跌并保留安全垫，暂不叠加参与率增强。`,
      };
    }

    return {
      market,
      structure: "暂不配置场外结构",
      reason: `${maSummary}，价格尚未形成一致的均线方向，综合观点也缺少明确确认。此时强行配置会增加路径与结算风险，建议等待方向突破后再选择正向或反向结构。`,
    };
  }

  function render(contract) {
    const advice = recommend(contract);
    result.innerHTML = `
      <article class="otc-result-card otc-simple-result">
        <header class="otc-result-header">
          <div>
            <span>${escapeHtml(contract.name)} ${escapeHtml(contract.contract)} · ${escapeHtml(contract.trade_date || dataset.updated_at || "日期需进一步核验")}</span>
            <h2>${escapeHtml(advice.structure)}</h2>
            <p>${escapeHtml(advice.reason)}</p>
          </div>
        </header>
      </article>`;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function selectedContract() {
    return contracts.find((contract) => contract.contract === contractSelect.value);
  }

  if (!contracts.length) {
    formError.textContent = "当前无法生成建议，需进一步核验行情数据。";
    return;
  }

  contractSelect.innerHTML = contracts.map((contract) =>
    `<option value="${escapeHtml(contract.contract)}">${escapeHtml(contract.name)} ${escapeHtml(contract.contract)}</option>`
  ).join("");
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const contract = selectedContract();
    if (!contract) {
      formError.textContent = "请选择需要研判的合约。";
      return;
    }
    formError.textContent = "";
    render(contract);
  });
})();

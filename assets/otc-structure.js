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

  function relativeTo(price, baseline) {
    if (!Number.isFinite(price) || !Number.isFinite(baseline) || baseline === 0) return "需核验";
    const change = (price / baseline - 1) * 100;
    return `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`;
  }

  function volatilityLabel(atrPct) {
    if (!Number.isFinite(atrPct)) return "需核验";
    if (atrPct < 1) return "偏低";
    if (atrPct < 1.5) return "适中";
    return "偏高";
  }

  function trendReason(market) {
    if (market.direction === "bullish") {
      return {
        title: "价格站上双均线",
        detail: `最新价高于 MA20 和 MA60，短中期技术方向一致偏强。`,
      };
    }
    if (market.direction === "bearish") {
      return {
        title: "价格跌破双均线",
        detail: `最新价低于 MA20 和 MA60，短中期技术方向一致偏弱。`,
      };
    }
    return {
      title: "均线方向尚未统一",
      detail: "价格没有同时站上或跌破 MA20、MA60，暂未形成可确认方向。",
    };
  }

  function recommend(contract) {
    const market = marketSnapshot(contract);
    const confirmed = market.confidence !== "低";
    const lowVolatility = market.atrPct !== null && market.atrPct < 1;
    const trend = trendReason(market);
    const volatility = volatilityLabel(market.atrPct);
    const marketReason = {
      title: `波动${volatility} · ${market.confidence}置信`,
      detail: Number.isFinite(market.atrPct)
        ? `ATR 占价格 ${market.atrPct.toFixed(2)}%，综合观点为“${market.stance}”，置信度为${market.confidence}。`
        : `ATR 数据需进一步核验，综合观点为“${market.stance}”，置信度为${market.confidence}。`,
    };
    const metrics = [
      { label: "最新价", value: format(market.price) },
      { label: "相对 MA20", value: relativeTo(market.price, market.ma20) },
      { label: "相对 MA60", value: relativeTo(market.price, market.ma60) },
      { label: "ATR / 价格", value: Number.isFinite(market.atrPct) ? `${market.atrPct.toFixed(2)}% · ${volatility}` : "需核验" },
    ];

    function build(structure, summary, structureReason, reviewCondition) {
      return {
        market,
        structure,
        summary,
        reasons: [trend, marketReason, structureReason],
        metrics,
        reviewCondition,
      };
    }

    if (market.direction === "bullish") {
      if (confirmed && lowVolatility) {
        return build(
          "正向气囊宝1.0",
          "虚值行权 + 收益封顶",
          {
            title: "用封顶换取更高参与效率",
            detail: "偏强方向已经确认且波动偏低，采用虚值行权与收益封顶增强上涨参与，同时保留下方安全垫。",
          },
          "若价格重新跌回 MA20 与 MA60 下方，正向逻辑失效，应重新研判结构方向。"
        );
      }
      return build(
        "正向气囊宝1.0",
        "标准型",
        {
          title: "先参与方向，不放大结构",
          detail: `${market.confidence === "低" ? "方向虽偏强，但观点置信度仍低" : "方向偏强，但当前波动不低"}，标准型保留上涨参与和回撤安全垫，暂不使用增强版本。`,
        },
        "待观点置信度提升且 ATR 回落后，再评估虚值行权与收益封顶版本；跌回双均线下方则取消正向判断。"
      );
    }

    if (market.direction === "bearish") {
      if (confirmed && lowVolatility) {
        return build(
          "反向气囊宝1.0",
          "虚值行权 + 收益封顶",
          {
            title: "用封顶换取更高参与效率",
            detail: "偏弱方向已经确认且波动偏低，采用虚值行权与收益封顶增强下跌参与，同时保留上方安全垫。",
          },
          "若价格重新站上 MA20 与 MA60，反向逻辑失效，应重新研判结构方向。"
        );
      }
      return build(
        "反向气囊宝1.0",
        "标准型",
        {
          title: "先参与方向，不放大结构",
          detail: `${market.confidence === "低" ? "方向虽偏弱，但观点置信度仍低" : "方向偏弱，但当前波动不低"}，标准型保留下跌参与和反弹安全垫，暂不使用增强版本。`,
        },
        "待观点置信度提升且 ATR 回落后，再评估虚值行权与收益封顶版本；站上双均线则取消反向判断。"
      );
    }

    return build(
      "暂不配置场外结构",
      "等待方向确认",
      {
        title: "不为震荡强行构造方向",
        detail: "均线信号不一致时配置方向结构，会增加不必要的路径与结算风险，等待确认优于勉强入场。",
      },
      "价格同时站上 MA20、MA60 时评估正向结构；同时跌破两条均线时评估反向结构。"
    );
  }

  function render(contract) {
    const advice = recommend(contract);
    const reasons = advice.reasons.map((item, index) => `
      <li>
        <span>${String(index + 1).padStart(2, "0")}</span>
        <div><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.detail)}</p></div>
      </li>`).join("");
    const metrics = advice.metrics.map((item) => `
      <div><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong></div>`).join("");
    result.innerHTML = `
      <article class="otc-result-card otc-analysis-result">
        <header class="otc-result-header">
          <div>
            <span>${escapeHtml(contract.name)} ${escapeHtml(contract.contract)} · ${escapeHtml(contract.trade_date || dataset.updated_at || "日期需进一步核验")}</span>
            <h2>${escapeHtml(advice.structure)}</h2>
            <p>${escapeHtml(advice.summary)}</p>
          </div>
          <div class="otc-result-date">
            <span>行情结论</span>
            <strong>${escapeHtml(advice.market.marketLabel)}</strong>
            <small>${escapeHtml(advice.market.confidence)}置信</small>
          </div>
        </header>

        <div class="otc-market-grid otc-market-grid--compact">${metrics}</div>

        <section class="otc-rationale">
          <header><span>Why this structure</span><h3>为什么推荐</h3></header>
          <ol>${reasons}</ol>
        </section>

        <div class="otc-review-condition">
          <span>何时重新评估</span>
          <p>${escapeHtml(advice.reviewCondition)}</p>
        </div>
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

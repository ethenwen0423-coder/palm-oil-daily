(function () {
  const dataset = window.OIL_FUTURES_CONTRACTS || {};
  const contracts = Array.isArray(dataset.contracts) ? dataset.contracts : [];
  const form = document.querySelector("#otc-form");
  const contractSelect = document.querySelector("#otc-contract");
  const contractNote = document.querySelector("#otc-contract-note");
  const dataDate = document.querySelector("#otc-data-date");
  const dataSource = document.querySelector("#otc-data-source");
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

  function textOf(contract, sectionIndex) {
    return String(contract.technical_detail?.[sectionIndex]?.text || "");
  }

  function capture(text, pattern) {
    const match = String(text).match(pattern);
    return match ? number(match[1]) : null;
  }

  function tradingIncrement(contract) {
    return ["M", "RM"].includes(String(contract.product || "").toUpperCase()) ? 5 : 10;
  }

  function roundStrike(value, contract) {
    if (!Number.isFinite(value)) return null;
    const increment = tradingIncrement(contract);
    return Math.round(value / increment) * increment;
  }

  function unique(values) {
    return [...new Set(values.filter(Number.isFinite))];
  }

  function technicalSnapshot(contract) {
    const price = number(contract.price);
    const trend = textOf(contract, 0);
    const levels = textOf(contract, 1);
    const volatility = textOf(contract, 2);
    const ma20 = capture(trend, /MA20\s*([\d,.]+)/i);
    const ma60 = capture(trend, /MA60\s*([\d,.]+)/i);
    const rangeHigh = capture(levels, /区间上沿\s*([\d,.]+)/);
    const rangeLow = capture(levels, /下沿\s*([\d,.]+)/);
    const channelHigh = capture(levels, /通道上轨\s*([\d,.]+)/);
    const channelLow = capture(levels, /通道下轨\s*([\d,.]+)/);
    const atr = capture(volatility, /波动幅度约\s*([\d,.]+)/) || (price ? price * 0.02 : null);
    const upperWatch = number(contract.strategy_recommendation?.upper_watch);
    const lowerWatch = number(contract.strategy_recommendation?.lower_watch);
    const candidates = unique([ma20, ma60, rangeHigh, rangeLow, channelHigh, channelLow, upperWatch, lowerWatch]);
    const below = candidates.filter((item) => item < price).sort((a, b) => b - a);
    const above = candidates.filter((item) => item > price).sort((a, b) => a - b);
    let support1 = below[0] || price - atr;
    let support2 = below.find((item) => item < support1 - atr * 0.35) || lowerWatch || price - atr * 2;
    let resistance1 = above[0] || price + atr;
    let resistance2 = above.find((item) => item > resistance1 + atr * 0.35) || upperWatch || price + atr * 2;
    support1 = roundStrike(support1, contract);
    support2 = roundStrike(Math.min(support2, support1 - tradingIncrement(contract)), contract);
    resistance1 = roundStrike(resistance1, contract);
    resistance2 = roundStrike(Math.max(resistance2, resistance1 + tradingIncrement(contract)), contract);
    return { price, atm: roundStrike(price, contract), ma20, ma60, atr, support1, support2, resistance1, resistance2 };
  }

  function directionOf(contract) {
    const stance = String(contract.score?.stance || "");
    if (/偏强|偏多|看多|多头/.test(stance)) return "bullish";
    if (/偏弱|偏空|看空|空头/.test(stance)) return "bearish";
    return "neutral";
  }

  function ageInDays(dateText) {
    const match = String(dateText || "").match(/(\d{4})-(\d{2})-(\d{2})/);
    if (!match) return null;
    const marketDate = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    return Math.floor((today - marketDate) / 86400000);
  }

  function selected(name) {
    return form.querySelector(`input[name="${name}"]:checked`)?.value || "";
  }

  function leg(action, option, strike, note) {
    return { action, option, strike, note };
  }

  function recommendation(contract, objective, cost, technical) {
    const direction = directionOf(contract);
    const stance = contract.score?.stance || "需进一步核验";
    const confidence = contract.score?.view_confidence || "需进一步核验";
    const lowConfidence = confidence === "低" || /分歧/.test(stance);
    const p = technical;
    let name = "";
    let summary = "";
    let tradeoff = "";
    let legs = [];

    if (objective === "procurement") {
      if (cost === "protection") {
        name = "买入香草看涨期权";
        const strike = direction === "bullish" ? p.atm : p.resistance1;
        legs = [leg("买入", "看涨期权", strike, "建立采购成本上限；下跌时仍可按更低现货价格采购")];
        summary = "纯买方保护，适合把最大损失限定为已付权利金。";
        tradeoff = "保护不封顶，但初始权利金通常高于价差结构。";
      } else if (cost === "low_cost") {
        name = "采购领口（买涨 + 卖跌）";
        legs = [
          leg("买入", "看涨期权", p.resistance1, "限制价格向上突破后的采购成本"),
          leg("卖出", "看跌期权", p.support1, "用权利金补贴买涨成本；跌破后可能承担采购义务"),
        ];
        summary = "用下方采购承诺换取较低的上行保护成本。";
        tradeoff = "价格跌破卖出看跌执行价时，可能必须按约定价采购。";
      } else {
        name = "看涨价差";
        const buyStrike = direction === "bullish" ? p.atm : p.resistance1;
        legs = [
          leg("买入", "较低执行价看涨", buyStrike, "从该点位开始获得上涨保护"),
          leg("卖出", "较高执行价看涨", p.resistance2, "降低权利金，同时封顶更高价格区间的保护"),
        ];
        summary = "适合预期温和上涨或希望用可控成本防范采购价上行。";
        tradeoff = "超过高执行价后的新增上涨不再获得额外补偿。";
      }
    } else if (objective === "inventory") {
      if (cost === "protection") {
        name = "买入香草看跌期权";
        const strike = direction === "bearish" ? p.atm : p.support1;
        legs = [leg("买入", "看跌期权", strike, "建立库存价值下限，同时保留上涨收益")];
        summary = "纯买方保护，适合明确限制库存跌价风险。";
        tradeoff = "保护不封底，但需承担确定的权利金成本。";
      } else if (cost === "low_cost") {
        name = "库存领口（买跌 + 卖涨）";
        legs = [
          leg("买入", "看跌期权", p.support1, "跌破支撑后保护库存价值"),
          leg("卖出", "看涨期权", p.resistance1, "用权利金补贴保护成本，但限制上涨收益"),
        ];
        summary = "用部分上涨空间换取较低的库存保护成本。";
        tradeoff = "超过卖出看涨执行价后的库存增值收益会受限。";
      } else {
        name = "看跌价差";
        const buyStrike = direction === "bearish" ? p.atm : p.support1;
        legs = [
          leg("买入", "较高执行价看跌", buyStrike, "从该点位开始获得下跌保护"),
          leg("卖出", "较低执行价看跌", p.support2, "降低权利金，同时封顶深跌区间的保护"),
        ];
        summary = "适合预期温和下跌或希望用可控成本保护库存价值。";
        tradeoff = "低执行价以下的新增跌幅不再获得额外补偿。";
      }
    } else if (cost === "protection") {
      name = "买入宽跨式";
      legs = [
        leg("买入", "看跌期权", p.support1, "价格向下突破时提供保护"),
        leg("买入", "看涨期权", p.resistance1, "价格向上突破时提供保护"),
      ];
      summary = "适合事件前担心大幅波动、但方向尚不确定的情形。";
      tradeoff = "需要支付两腿权利金；行情停留区间内时可能损失全部权利金。";
    } else if (cost === "balanced") {
      name = "双向价差组合";
      legs = [
        leg("买入", "看跌期权", p.support1, "建立下方第一层保护"),
        leg("卖出", "更低执行价看跌", p.support2, "降低下方保护成本"),
        leg("买入", "看涨期权", p.resistance1, "建立上方第一层保护"),
        leg("卖出", "更高执行价看涨", p.resistance2, "降低上方保护成本"),
      ];
      summary = "用四腿结构控制双向尾部风险，并限制总权利金。";
      tradeoff = "两端保护均有封顶，需确认每一腿期限与名义本金完全一致。";
    } else {
      name = "暂缓低成本卖权结构";
      legs = [leg("等待", "补充正式询价", null, "先获取隐含波动率、期限、权利金和最大损失，再决定是否引入卖方腿")];
      summary = "双边风险下，低成本通常意味着卖出期权或路径依赖，不适合仅凭方向数据自动下结论。";
      tradeoff = "当前不给出累计、敲入或裸卖结构点位；需进一步核验。";
    }

    if (lowConfidence) {
      summary += " 当前观点置信度偏低，建议把点位仅用于多家交易对手询价比较。";
    }
    return { name, summary, tradeoff, legs, direction, stance, confidence, lowConfidence };
  }

  function directionLabel(value) {
    return { bullish: "偏强", bearish: "偏弱", neutral: "震荡/方向不明" }[value] || "需进一步核验";
  }

  function render(contract, objective, cost) {
    const technical = technicalSnapshot(contract);
    const advice = recommendation(contract, objective, cost, technical);
    const age = ageInDays(contract.trade_date || dataset.updated_at);
    const warnings = [];
    if (age === null || age > 3) warnings.push("行情时间超过 3 个自然日，所有点位需进一步核验后再询价。");
    if (/未完成|未配置|待核验/.test(String(contract.verification || ""))) warnings.push("行情交叉核验未完成，当前以页面记录的主数据源为准。");
    if (advice.lowConfidence) warnings.push("综合观点为分歧或低置信，不建议使用敲入放大、累计或裸卖期权结构。");
    const updated = dataset.updated_at || contract.trade_date || "需进一步核验";
    const legs = advice.legs.map((item, index) => `
      <article class="otc-leg-card">
        <span>${String(index + 1).padStart(2, "0")} · ${escapeHtml(item.action)}</span>
        <h3>${escapeHtml(item.option)}</h3>
        <strong>${item.strike === null ? "需进一步核验" : format(item.strike)}</strong>
        <p>${escapeHtml(item.note)}</p>
      </article>`).join("");
    const warningHtml = warnings.length
      ? `<div class="otc-warning"><strong>数据与风险提示</strong><ul>${warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`
      : `<div class="otc-ready">行情时效通过页面规则检查；执行价仍需结合正式场外报价确认。</div>`;
    result.innerHTML = `
      <article class="otc-result-card">
        <header class="otc-result-header">
          <div>
            <span>${escapeHtml(contract.name)} ${escapeHtml(contract.symbol)} · ${escapeHtml(contract.contract_label || "外盘参考")}</span>
            <h2>${escapeHtml(advice.name)}</h2>
            <p>${escapeHtml(advice.summary)}</p>
          </div>
          <div class="otc-result-date"><span>行情日期</span><strong>${escapeHtml(contract.trade_date || updated)}</strong><small>${escapeHtml(advice.stance)} · 置信度${escapeHtml(advice.confidence)}</small></div>
        </header>

        ${warningHtml}

        <div class="otc-market-grid">
          <div><span>当前价</span><strong>${format(technical.price)}</strong></div>
          <div><span>MA20</span><strong>${format(technical.ma20, 2)}</strong></div>
          <div><span>MA60</span><strong>${format(technical.ma60, 2)}</strong></div>
          <div><span>近端支撑</span><strong>${format(technical.support1)}</strong></div>
          <div><span>近端压力</span><strong>${format(technical.resistance1)}</strong></div>
          <div><span>行情方向</span><strong>${escapeHtml(directionLabel(advice.direction))}</strong></div>
        </div>

        <section class="otc-legs">
          <header><span>询价参考点位</span><p>场外执行价可定制；页面按技术位取整，不代表可成交报价。</p></header>
          <div class="otc-leg-grid">${legs}</div>
        </section>

        <div class="otc-decision-grid">
          <section><span>为什么是这个结构</span><p>${escapeHtml(advice.summary)}</p></section>
          <section><span>核心取舍</span><p>${escapeHtml(advice.tradeoff)}</p></section>
          <section><span>观点失效条件</span><p>${escapeHtml(contract.strategy_recommendation?.invalidation || "需进一步核验")}</p></section>
          <section><span>询价必须补齐</span><p>期限、名义本金、结算标的、执行方式、隐含波动率、权利金、保证金/授信、最大损失与提前终止条款。</p></section>
        </div>

        <footer class="otc-result-footer">
          <p>技术依据：${escapeHtml(contract.child_skill || contract.analysis_skill || "technical-analysis-helper")} · ATR/波动幅度 ${format(technical.atr, 2)}</p>
          <p>数据更新时间：${escapeHtml(updated)} · ${escapeHtml(contract.source || dataset.source || "来源需进一步核验")}</p>
        </footer>
      </article>`;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function populate() {
    if (!contracts.length) {
      contractSelect.innerHTML = '<option value="">暂无可用行情</option>';
      contractSelect.disabled = true;
      formError.textContent = "行情数据未加载，暂时无法生成结构建议。";
      dataDate.textContent = "数据不可用";
      return;
    }
    contractSelect.innerHTML = '<option value="">请选择合约</option>' + contracts.map((contract) => {
      const label = `${contract.name} ${contract.symbol}${contract.contract_label ? ` · ${contract.contract_label}` : ""} · ${contract.trade_date || "日期待核验"}`;
      return `<option value="${escapeHtml(contract.symbol)}">${escapeHtml(label)}</option>`;
    }).join("");
    const newest = contracts.map((item) => item.trade_date).filter(Boolean).sort().at(-1);
    dataDate.textContent = newest ? `最新交易日 ${newest}` : dataset.updated_at || "需进一步核验";
    dataSource.textContent = `数据集更新 ${dataset.updated_at || "需进一步核验"} · 技术分析随行情自动重算`;
  }

  contractSelect.addEventListener("change", () => {
    const contract = contracts.find((item) => item.symbol === contractSelect.value);
    contractNote.textContent = contract
      ? `${contract.score?.stance || "观点待核验"} · 置信度${contract.score?.view_confidence || "待核验"} · 最新价 ${format(contract.price)}`
      : "主力与次主力合约";
    formError.textContent = "";
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const contract = contracts.find((item) => item.symbol === contractSelect.value);
    if (!contract) {
      formError.textContent = "请先选择标的合约。";
      contractSelect.focus();
      return;
    }
    formError.textContent = "";
    render(contract, selected("objective"), selected("cost"));
  });

  populate();
})();

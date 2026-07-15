(() => {
  const data = window.EXCHANGE_FUTURES_DATA || {};
  const contracts = Array.isArray(data.contracts) ? data.contracts : [];
  const exchangeFilter = document.querySelector("#exchange-filter");
  const contractSelect = document.querySelector("#contract-select");
  const confirm = document.querySelector("#contract-confirm");
  const result = document.querySelector("#contract-analysis-result");
  const source = document.querySelector("#futures-data-source");
  const pickerNote = document.querySelector("#contract-picker-note");
  const exchangeNames = { DCE: "大商所", CZCE: "郑商所", SHFE: "上期所", GFEX: "广期所", CFFEX: "中金所" };

  const escapeHtml = (value) => String(value ?? "需进一步核验").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
  const formatNumber = (value) => typeof value === "number" ? value.toLocaleString("zh-CN", { maximumFractionDigits: 2 }) : "需进一步核验";
  const formatChange = (value) => typeof value === "number" ? `${value > 0 ? "+" : ""}${value.toFixed(2)}%` : "需进一步核验";

  function populateContracts() {
    const exchange = exchangeFilter.value;
    const options = contracts.filter((item) => exchange === "all" || item.exchange === exchange);
    const groups = options.reduce((result, item) => {
      (result[item.exchange] ||= []).push(item);
      return result;
    }, {});
    const groupedOptions = Object.entries(groups).map(([exchangeCode, items]) => `
      <optgroup label="${escapeHtml(exchangeNames[exchangeCode] || exchangeCode)} · ${items.length} 个品种">
        ${items.map((item) => `<option value="${escapeHtml(item.symbol)}">${escapeHtml(item.product)} ${escapeHtml(item.symbol)}</option>`).join("")}
      </optgroup>
    `).join("");
    contractSelect.innerHTML = `<option value="">选择具体主力合约</option>${groupedOptions}`;
    if (pickerNote) {
      const scope = exchange === "all" ? "五大交易所" : (exchangeNames[exchange] || exchange);
      pickerNote.textContent = `${scope}当前收录 ${options.length} 个品种主力合约；按实时成交量、持仓量排序选取。`;
    }
  }

  function renderNews(items) {
    if (!items.length) return '<p class="analysis-muted">未匹配到该品种的近期直接热点；新闻维度不参与方向判断。</p>';
    return `<ul class="hotspot-list">${items.map((item) => `<li><span>${escapeHtml(item.date)} · ${escapeHtml(item.source)}</span>${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title)}</a>` : `<strong>${escapeHtml(item.title)}</strong>`}</li>`).join("")}</ul>`;
  }

  function renderDetailList(items, className) {
    return `<div class="${className}">${items.map((item) => `<section><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.text)}</span></section>`).join("")}</div>`;
  }

  function renderAnalysis(contract) {
    const technical = contract.technical || {};
    const indicators = technical.indicators || {};
    const levels = technical.levels || {};
    const direction = contract.change_pct > 0 ? "up" : contract.change_pct < 0 ? "down" : "flat";
    result.innerHTML = `
      <article class="analysis-head">
        <div><p>${escapeHtml(contract.exchange)} · ${escapeHtml(contract.category)}</p><h2>${escapeHtml(contract.product)} <span>${escapeHtml(contract.symbol)}</span></h2><small>主力合约，交易日 ${escapeHtml(contract.trade_date || "需进一步核验")}</small></div>
        <div class="analysis-price ${direction}"><strong>${formatNumber(contract.price)}</strong><span>${formatChange(contract.change_pct)}</span></div>
      </article>
      <div class="analysis-columns">
        <section class="analysis-panel">
          <header><p>技术面</p><h3>${escapeHtml(technical.trend || "需进一步核验")}</h3></header>
          <p>${escapeHtml(technical.summary)}</p>
          <dl class="indicator-grid">${Object.entries(indicators).map(([name, value]) => `<div><dt>${escapeHtml(name)}</dt><dd>${formatNumber(value)}</dd></div>`).join("")}</dl>
          <div class="analysis-levels">${Object.entries(levels).map(([name, value]) => `<span>${escapeHtml(name)}：<b>${formatNumber(value)}</b></span>`).join("")}</div>
          ${renderDetailList(technical.details || [], "technical-detail-list")}
        </section>
        <section class="analysis-panel">
          <header><p>基本面</p><h3>${escapeHtml(contract.fundamental?.category || contract.category)}</h3></header>
          <p>${escapeHtml(contract.fundamental?.summary)}</p>
          ${renderDetailList(contract.fundamental?.factors || [], "fundamental-detail-list")}
          <div class="hotspot-section"><strong>新闻热点</strong>${renderNews(contract.news_hotspots || [])}</div>
        </section>
      </div>
      <p class="analysis-quality">${escapeHtml(contract.data_quality)}</p>
    `;
  }

  exchangeFilter.addEventListener("change", populateContracts);
  confirm.addEventListener("click", () => {
    const contract = contracts.find((item) => item.symbol === contractSelect.value);
    result.innerHTML = contract ? "" : '<div class="analysis-empty">请选择有效的具体合约后确认。</div>';
    if (contract) renderAnalysis(contract);
  });
  if (source) source.textContent = data.source ? `${data.source} 更新 ${data.updated_at || "需进一步核验"}` : "数据集等待生成";
  populateContracts();
})();

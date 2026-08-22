(function () {
  "use strict";

  const sources = {
    reports: ["/api/reports", "data/reports.json"],
    oil: ["/api/oil-futures", "data/oil_futures.json"],
    exchange: ["/api/exchange-futures", "data/exchange_futures.json"],
    supply: ["/api/supply-demand", "data/supply-demand.json"],
    brief: ["/api/assistant/brief", "data/market_assistant_brief.json"],
    status: ["/api/status"]
  };

  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value == null ? "" : value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
  const array = (value) => Array.isArray(value) ? value : [];
  const first = (value, fallback = "--") => value == null || value === "" ? fallback : value;
  const staticFallbacks = {
    reports: () => window.PALM_OIL_REPORTS,
    oil: () => window.OIL_FUTURES_CONTRACTS,
    exchange: () => window.EXCHANGE_FUTURES_DATA
  };

  async function fetchFirst(urls) {
    let lastError;
    for (const url of urls) {
      try {
        const response = await fetch(url, { cache: "no-store" });
        if (!response.ok) throw new Error(`${response.status} ${url}`);
        return await response.json();
      } catch (error) { lastError = error; }
    }
    throw lastError || new Error("数据不可用");
  }

  function fmtTime(value, includeDate) {
    if (!value) return "时间待核验";
    const dateOnly = String(value).match(/^(\d{4})-(\d{2})-(\d{2})(?:-|$)/);
    if (dateOnly && !String(value).includes("T") && !String(value).includes(":")) return `${dateOnly[2]}/${dateOnly[3]}`;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return new Intl.DateTimeFormat("zh-CN", { month: includeDate ? "2-digit" : undefined, day: includeDate ? "2-digit" : undefined, hour: "2-digit", minute: "2-digit", hour12: false }).format(date);
  }

  function number(value, digits = 0) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed.toLocaleString("zh-CN", { maximumFractionDigits: digits, minimumFractionDigits: digits }) : "--";
  }

  function numberOrText(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed.toLocaleString("zh-CN") : first(value, "--");
  }

  function pct(value) {
    const parsed = Number(String(value == null ? "" : value).replace("%", ""));
    if (!Number.isFinite(parsed)) return "--";
    return `${parsed > 0 ? "+" : ""}${parsed.toFixed(2)}%`;
  }

  function direction(value) {
    const parsed = Number(String(value == null ? "" : value).replace("%", ""));
    return parsed > 0 ? "up" : parsed < 0 ? "down" : "flat";
  }

  function renderBrief(payload) {
    $("market-state").textContent = first(payload.market_state, "待判断");
    $("decision-title").textContent = first(payload.headline, "等待 AI 研究结论");
    $("confidence-value").textContent = first(payload.confidence, "--");
    $("decision-summary").textContent = first(payload.summary, "暂无可发布摘要。");
    $("brief-generated").textContent = `生成 ${fmtTime(payload.generated_at || payload.updated_at, true)}`;

    const moves = array(payload.key_moves).slice(0, 4);
    $("decision-evidence").innerHTML = moves.length ? moves.map((item) => `<span>${esc(first(item.label, "证据"))} · ${esc(first(item.value, "待核验"))}</span>`).join("") : "<span>证据待补充</span>";

    const watch = array(payload.watchlist).slice().sort((a, b) => Number(a.priority || 99) - Number(b.priority || 99)).slice(0, 3);
    $("priority-list").innerHTML = watch.length ? watch.map((item) => `<li><div><strong>${esc(first(item.item, "关注项"))}</strong><span>${esc(first(item.trigger, item.why || "等待触发条件"))}</span></div></li>`).join("") : "<li><div><strong>暂无新触发</strong><span>继续按自动任务周期检查</span></div></li>";
    $("trigger-list").innerHTML = watch.length ? watch.map((item) => `<li><strong>${esc(first(item.item, "关注项"))}</strong><span>${esc(first(item.trigger, "等待下一次自动检查"))}</span></li>`).join("") : "<li><strong>暂无等待触发</strong><span>系统仍会持续检查</span></li>";
  }

  function renderPulse(payload) {
    const desiredProducts = ["P", "Y", "OI", "M", "RM"];
    const allContracts = array(payload.contracts);
    const contracts = desiredProducts.map((product) => allContracts.find((item) => item.product === product && Number(item.contract_rank) === 1) || allContracts.find((item) => item.product === product)).filter(Boolean);
    $("pulse-updated").textContent = `行情快照 ${fmtTime(payload.updated_at, true)}`;
    $("market-pulse").innerHTML = contracts.length ? contracts.map((item) => {
      const change = item.change_pct != null ? item.change_pct : item.change;
      return `<article class="pulse-card"><header><strong>${esc(first(item.name, item.symbol))}</strong><span>${esc(first(item.symbol, "--"))}</span></header><div class="pulse-price"><strong>${number(item.price)}</strong><b class="${direction(change)}">${pct(change)}</b></div><div class="pulse-meta"><span>成交 ${esc(numberOrText(item.volume))}</span><span>持仓 ${esc(numberOrText(item.open_interest))}</span></div></article>`;
    }).join("") : "<article class='pulse-card'>暂无可用行情</article>";
  }

  function eventTime(item) { return item.observed_at || item.generated_at || item.updated_at || item.date; }

  function buildTimeline(data) {
    const events = [];
    array(data.brief.key_moves).forEach((item) => events.push({ type: "move", title: first(item.label, "行情证据"), summary: first(item.value, "数值待核验"), detail: first(item.interpretation, "暂无补充解释"), source: first(item.source, "已发布数据"), time: eventTime(item) }));
    array(data.brief.actions).forEach((item) => events.push({ type: "agent", title: first(item.task, "Agent 任务"), summary: first(item.result, item.status || "已处理"), detail: first(item.next_check, "等待下一次自动检查"), source: "AI Agent", time: eventTime(item) || data.brief.generated_at }));
    const report = array(data.reports.reports || data.reports).slice(0, 1)[0];
    if (report) events.push({ type: "report", title: first(report.headline || report.title, "最新研究报告"), summary: first(report.summary || report.subtitle, "研究报告已发布"), detail: "点击 AI 报告导航可查看完整正文与来源。", source: first(report.source, "Vinson Research"), time: eventTime(report) });
    if (data.supply && Object.keys(data.supply).length) {
      const countries = Object.values(data.supply.countries || {});
      const summary = countries.length ? countries.map((item) => `${first(item.name, "来源")} ${first(item.latest_period, "待更新")}`).join(" · ") : "供需资料已检查";
      const detail = countries.length ? countries.map((item) => `${first(item.name, "来源")}：${first(item.status_message, item.status || "已检查")}`).join("；") : `数据更新：${first(data.supply.generated_at, "待核验")}`;
      events.push({ type: "supply", title: "官方供需资料检查", summary, detail, source: "MPOB · GAPKI · USDA", time: data.supply.generated_at || data.supply.checked_at || data.supply.updated_at });
    }
    return events.sort((a, b) => new Date(eventTime(b) || 0) - new Date(eventTime(a) || 0));
  }

  function renderTimeline(events, filter = "all") {
    const visible = filter === "all" ? events : events.filter((item) => item.type === filter);
    const labels = { move: "行情", report: "研究", supply: "供需", agent: "AGENT" };
    $("intelligence-timeline").innerHTML = visible.length ? visible.map((item, index) => `<article class="timeline-item" data-type="${esc(item.type)}"><time class="timeline-time">${esc(fmtTime(item.time, true))}</time><span class="timeline-marker ${item.type === "report" ? "is-degraded" : "is-ready"}">${esc(labels[item.type] || item.type)}</span><div class="timeline-content"><button type="button" aria-expanded="false" aria-controls="timeline-detail-${index}"><span class="timeline-copy"><h3>${esc(item.title)}</h3><p>${esc(item.summary)}</p><span class="timeline-meta"><span>${esc(item.source)}</span></span></span><span class="timeline-toggle" aria-hidden="true">＋</span></button><div id="timeline-detail-${index}" class="timeline-detail">${esc(item.detail)}</div></div></article>`).join("") : "<p class='empty-state'>当前筛选下没有事件。</p>";
    document.querySelectorAll(".timeline-content button").forEach((button) => button.addEventListener("click", () => {
      const detail = document.getElementById(button.getAttribute("aria-controls"));
      const open = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!open));
      detail.classList.toggle("is-open", !open);
    }));
  }

  function renderOilDesk(payload) {
    const oilProducts = new Set(["P", "Y", "OI", "FCPO", "CPOTR"]);
    const contracts = array(payload.contracts).filter((item) => oilProducts.has(item.product));
    $("oil-desk-updated").textContent = `行情 ${fmtTime(payload.updated_at, true)}`;
    $("oil-desk-source").textContent = first(payload.source, "行情数据源待核验");
    $("oil-desk-grid").innerHTML = contracts.length ? contracts.map((item) => {
      const change = item.change_pct != null ? item.change_pct : item.change;
      const rank = item.contract_rank ? `流动性 #${item.contract_rank}` : first(item.market, "海外参照");
      return `<article class="data-card oil-contract-card"><header><div><span>${esc(first(item.market, "--"))}</span><h3>${esc(first(item.name, item.product))}</h3></div><b>${esc(rank)}</b></header><div class="contract-quote"><strong>${esc(numberOrText(item.price))}</strong><span class="${direction(change)}">${esc(pct(change))}</span></div><dl><div><dt>合约</dt><dd>${esc(first(item.symbol, "--"))}</dd></div><div><dt>成交</dt><dd>${esc(numberOrText(item.volume))}</dd></div><div><dt>持仓</dt><dd>${esc(numberOrText(item.open_interest))}</dd></div></dl></article>`;
    }).join("") : "<article class='data-card'><p class='empty-state'>暂无可用油脂主力数据。</p></article>";
  }

  function latestMetric(metric) {
    const series = array(metric && metric.series);
    const latest = series[series.length - 1];
    const previous = series[series.length - 2];
    if (!latest) return { value: "--", period: "待更新", change: "--" };
    const raw = Number(latest.value);
    const prior = Number(previous && previous.value);
    const useWan = metric.display_unit === "万吨" && Number.isFinite(raw);
    const value = Number.isFinite(raw) ? number(useWan ? raw / 10000 : raw, useWan ? 1 : 0) : first(latest.value, "--");
    const change = Number.isFinite(raw) && Number.isFinite(prior) && prior !== 0 ? pct((raw / prior - 1) * 100) : "--";
    return { value, period: first(latest.period, "待更新"), change, unit: first(metric.display_unit, metric.unit || "") };
  }

  function renderSupplyDesk(payload) {
    const countries = Object.values(payload.countries || {});
    $("supply-desk-updated").textContent = `检查 ${fmtTime(payload.checked_at || payload.generated_at, true)}`;
    $("supply-desk-note").textContent = first(payload.update_message, "官方来源状态待核验");
    $("supply-desk-grid").innerHTML = countries.length ? countries.map((country) => {
      const metrics = Object.values(country.metrics || {}).slice(0, 4);
      return `<article class="data-card supply-country-card"><header><div><span>${esc(first(country.latest_period, "待更新"))}</span><h3>${esc(first(country.name, "产地"))}</h3></div><b class="${country.status === "ok" ? "is-ready" : "is-degraded"}">${esc(country.status === "ok" ? "官方已更新" : first(country.status, "待核验"))}</b></header><div class="supply-metrics">${metrics.map((metric) => { const latest = latestMetric(metric); return `<div><span>${esc(first(metric.label, "指标"))}</span><strong>${esc(latest.value)} <small>${esc(latest.unit)}</small></strong><em class="${direction(latest.change)}">环比 ${esc(latest.change)}</em></div>`; }).join("")}</div><p>${esc(first(country.status_message, "官方数据状态待核验"))}</p>${country.source && country.source.url ? `<a href="${esc(country.source.url)}" target="_blank" rel="noopener noreferrer">${esc(first(country.source.name, "查看官方来源"))} ↗</a>` : ""}</article>`;
    }).join("") : "<article class='data-card'><p class='empty-state'>暂无结构化供需数据。</p></article>";
  }

  function renderContractDesk(payload) {
    const contracts = array(payload.contracts);
    const exchangeFilter = $("assistant-exchange-filter");
    const contractSelect = $("assistant-contract-select");
    const result = $("assistant-contract-result");
    const exchangeNames = { DCE: "大商所", CZCE: "郑商所", SHFE: "上期所", GFEX: "广期所", CFFEX: "中金所" };
    $("all-contracts-updated").textContent = `行情 ${fmtTime(payload.updated_at, true)}`;

    function populate() {
      const exchange = exchangeFilter.value;
      const options = contracts.filter((item) => exchange === "all" || item.exchange === exchange);
      const groups = options.reduce((acc, item) => { (acc[item.exchange] ||= []).push(item); return acc; }, {});
      contractSelect.innerHTML = `<option value="">选择具体主力合约</option>${Object.entries(groups).map(([code, items]) => `<optgroup label="${esc(exchangeNames[code] || code)} · ${items.length} 个品种">${items.map((item) => `<option value="${esc(item.symbol)}">${esc(item.product)} ${esc(item.symbol)}</option>`).join("")}</optgroup>`).join("")}`;
      $("assistant-contract-note").textContent = `${exchange === "all" ? "五大交易所" : (exchangeNames[exchange] || exchange)}当前收录 ${options.length} 个主力合约。`;
    }

    function detailList(items) {
      return array(items).map((item) => `<div><strong>${esc(first(item.title, "要点"))}</strong><span>${esc(first(item.text, "需进一步核验"))}</span></div>`).join("");
    }

    function render(contract) {
      const technical = contract.technical || {};
      const fundamental = contract.fundamental || {};
      const indicators = technical.indicators || {};
      const levels = technical.levels || {};
      const news = array(contract.news_hotspots).slice(0, 4);
      result.innerHTML = `<article class="contract-result-head"><div><span>${esc(first(contract.exchange, "--"))} · ${esc(first(contract.category, "--"))}</span><h3>${esc(first(contract.product, "品种"))} <small>${esc(first(contract.symbol, "--"))}</small></h3><p>交易日 ${esc(first(contract.trade_date, "需进一步核验"))}</p></div><div class="contract-result-price ${direction(contract.change_pct)}"><strong>${esc(numberOrText(contract.price))}</strong><span>${esc(pct(contract.change_pct))}</span></div></article><div class="contract-analysis-grid"><section><header><span>技术面</span><h4>${esc(first(technical.trend, "需进一步核验"))}</h4></header><p>${esc(first(technical.summary, "暂无结构化技术结论。"))}</p><dl class="contract-indicators">${Object.entries(indicators).slice(0, 6).map(([name, value]) => `<div><dt>${esc(name)}</dt><dd>${esc(numberOrText(value))}</dd></div>`).join("")}</dl><div class="contract-levels">${Object.entries(levels).map(([name, value]) => `<span>${esc(name)} <b>${esc(numberOrText(value))}</b></span>`).join("")}</div><div class="contract-detail-list">${detailList(technical.details)}</div></section><section><header><span>基本面与新闻</span><h4>${esc(first(fundamental.category, contract.category || "需进一步核验"))}</h4></header><p>${esc(first(fundamental.summary, "暂无结构化基本面结论。"))}</p><div class="contract-detail-list">${detailList(fundamental.factors)}</div><div class="contract-news">${news.length ? news.map((item) => `<div><span>${esc(first(item.date, "--"))} · ${esc(first(item.source, "来源待核验"))}</span>${item.url ? `<a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">${esc(first(item.title, "新闻"))}</a>` : `<strong>${esc(first(item.title, "新闻"))}</strong>`}</div>`).join("") : "<p>暂无直接新闻证据。</p>"}</div></section></div><p class="contract-quality">${esc(first(contract.data_quality, "数据质量说明待补充"))}</p>`;
    }

    exchangeFilter.onchange = populate;
    $("assistant-contract-confirm").onclick = () => {
      const contract = contracts.find((item) => item.symbol === contractSelect.value);
      result.innerHTML = contract ? "" : "<p class='empty-state'>请选择有效的具体合约。</p>";
      if (contract) render(contract);
    };
    populate();
  }

  function renderStatus(payload) {
    const state = first(payload.status, "degraded");
    const klass = state === "ready" ? "is-ready" : state === "error" ? "is-error" : "is-degraded";
    $("overall-state").className = klass;
    $("overall-state").textContent = state === "ready" ? "数据链正常" : state === "degraded" ? "部分数据延迟" : "数据链异常";
    $("system-label").textContent = $("overall-state").textContent;
    $("system-label").className = klass;
    const datasets = Object.values(payload.datasets || {});
    const counts = { ready: 0, stale: 0, invalid: 0 };
    datasets.forEach((item) => { const key = item.state === "ready" ? "ready" : item.state === "invalid" || item.state === "missing" ? "invalid" : "stale"; counts[key] += 1; });
    $("health-summary").innerHTML = `<div class="health-stat"><strong class="is-ready">${counts.ready}</strong><span>正常</span></div><div class="health-stat"><strong class="is-degraded">${counts.stale}</strong><span>延迟</span></div><div class="health-stat"><strong class="is-error">${counts.invalid}</strong><span>缺失</span></div>`;
    const datasetOrder = ["/api/assistant/brief", "/api/reports", "/api/supply-demand", "/api/oil-futures", "/api/exchange-futures", "/api/forecast/metrics/latest"];
    const orderedDatasets = datasetOrder.map((route) => payload.datasets && payload.datasets[route]).filter(Boolean);
    $("dataset-status-list").innerHTML = orderedDatasets.length ? orderedDatasets.map((item) => {
      const itemClass = item.state === "ready" ? "is-ready" : item.state === "invalid" || item.state === "missing" ? "is-error" : "is-degraded";
      const stateLabel = item.state === "ready" ? "正常" : item.state === "stale" ? "延迟" : item.state === "missing" ? "缺失" : first(item.state, "待查");
      return `<div class="dataset-row"><span><strong>${esc(first(item.label, item.route))}</strong><small>${esc(fmtTime(item.observed_at || item.updated_at, true))}</small></span><b class="${itemClass}">${esc(stateLabel)}</b></div>`;
    }).join("") : "<p class='empty-state'>暂无分项数据状态</p>";
    const automation = Object.entries(payload.automation || {});
    $("agent-summary").innerHTML = automation.length ? automation.slice(0, 6).map(([name, item]) => {
      const itemState = typeof item === "string" ? item : item.state || item.status;
      const itemClass = itemState === "ready" || itemState === "active" ? "is-ready" : "is-degraded";
      const label = typeof item === "string" ? name : first(item.label, name);
      const checked = typeof item === "string" ? "" : fmtTime(item.last_success_at, true);
      return `<div class="status-row"><span><strong>${esc(label)}</strong><small>${esc(checked)}</small></span><b class="${itemClass}">${esc(itemState === "ready" ? "已运行" : first(itemState, "待检查"))}</b></div>`;
    }).join("") : "<p class='empty-state'>暂无任务状态</p>";
  }

  function renderMonitorMode(data) {
    const shanghaiWeekday = new Intl.DateTimeFormat("en-US", { weekday: "short", timeZone: "Asia/Shanghai" }).format(new Date());
    const researchSession = data.status && data.status.automation && data.status.automation.research && data.status.automation.research.session;
    const nonTrading = shanghaiWeekday === "Sat" || shanghaiWeekday === "Sun" || researchSession === "weekend" || researchSession === "holiday";
    $("monitor-mode-label").className = nonTrading ? "is-degraded" : "is-ready";
    $("monitor-mode-label").textContent = nonTrading ? "休市监控" : "连续监控";
    $("monitor-mode-title").textContent = nonTrading ? "价格冻结，研究链继续运行" : "行情与研究分轨更新";
    const snapshotAt = data.oil && data.oil.updated_at;
    $("monitor-mode-detail").textContent = nonTrading
      ? `行情保持最近交易时段快照（${fmtTime(snapshotAt, true)}）；研究、供需、AI 判断、触发条件和数据健康继续更新。`
      : `行情按真实交易时段刷新；研究、供需、AI 判断、触发条件和数据健康独立持续更新。`;
    const automation = Object.values((data.status && data.status.automation) || {}).filter((item) => item && typeof item === "object" && item.last_success_at);
    const latest = automation.sort((a, b) => new Date(b.last_success_at) - new Date(a.last_success_at))[0];
    $("background-checked").textContent = latest ? `最近后台完成：${first(latest.label, "自动任务")} · ${fmtTime(latest.last_success_at, true)}` : "后台任务时间待核验";
  }

  function bindFilters(events) {
    document.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => {
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("is-active", item === button));
      renderTimeline(events, button.dataset.filter);
    }));
  }

  async function load() {
    const entries = await Promise.all(Object.entries(sources).map(async ([key, urls]) => {
      try { return [key, await fetchFirst(urls)]; } catch (error) {
        const fallback = staticFallbacks[key] && staticFallbacks[key]();
        return [key, fallback || { _error: error.message }];
      }
    }));
    const data = Object.fromEntries(entries);
    renderBrief(data.brief || {});
    renderPulse(data.oil || {});
    renderOilDesk(data.oil || {});
    renderSupplyDesk(data.supply || {});
    renderContractDesk(data.exchange || {});
    renderStatus(data.status || { status: "degraded" });
    renderMonitorMode(data);
    const events = buildTimeline(data);
    renderTimeline(events);
    bindFilters(events);
    $("refresh-note").textContent = `最近检查 ${fmtTime(new Date().toISOString(), false)} · 每 60 秒刷新`;
  }

  function clock() { $("live-clock").textContent = new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).format(new Date()); }
  clock(); setInterval(clock, 1000);
  load(); setInterval(load, 60000);
})();

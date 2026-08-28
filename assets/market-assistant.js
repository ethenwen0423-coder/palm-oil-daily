(function () {
  "use strict";

  const sources = {
    reports: ["/api/reports", "data/reports.json"],
    oil: ["/api/oil-futures", "data/oil_futures.json"],
    exchange: ["/api/exchange-futures", "data/exchange_futures.json"],
    supply: ["/api/supply-demand", "data/supply-demand.json"],
    brief: ["/api/assistant/brief", "data/market_assistant_brief.json"],
    watch: ["/api/assistant/watch", "data/market_watch.json"],
    researchWatch: ["/api/assistant/research-watch", "data/research_watch.json"],
    status: ["/api/status"]
  };

  const $ = (id) => document.getElementById(id);
  const publicText = (value) => String(value == null ? "" : value)
    .replace(/https?:\/\/(?:www\.)?htfc\.com\/?/gi, "")
    .replace(/htfc[-_ ]news/gi, "institutional-news")
    .replace(/htfc[-_ ]kline/gi, "institutional-kline")
    .replace(/HTFC\s*Tianji/gi, "机构资讯数据")
    .replace(/htfc[-_ ]tianji/gi, "institutional-feed")
    .replace(/华泰天玑/g, "机构资讯")
    .replace(/华泰期货/g, "机构研究")
    .replace(/天玑/gi, "机构资讯")
    .replace(/HTFC/gi, "机构资讯");
  const esc = (value) => publicText(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
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

  function watchDimension(item) {
    const evidence = array(item.evidence_ids).join(" ").toLowerCase();
    const trigger = `${first(item.trigger, "")} ${first(item.item, "")}`;
    if (evidence.includes("quant:") || /突破|观察位|均线|趋势|量化|波动/.test(trigger)) {
      return { key: "technical", label: "技术面", evidenceLabel: "价格与趋势证据" };
    }
    if (evidence.includes("supply:") || /供需|库存|出口|产量|官方|外盘/.test(trigger)) {
      return { key: "fundamental", label: "基本面", evidenceLabel: "供需与外盘证据" };
    }
    return { key: "technical", label: "技术面", evidenceLabel: "行情结构证据" };
  }

  function displayEvidenceValue(item) {
    const value = first(item && item.value, "待核验");
    return item && item.source === "reports" && /^\d{4}-\d{2}-\d{2}/.test(String(value)) ? `${fmtTime(value, true)} 周报` : value;
  }

  function contractVariety(item) {
    const matched = String(item && item.symbol || "").toUpperCase().match(/^[A-Z]+/);
    return matched ? matched[0] : "";
  }

  function structuredWatch(data) {
    const core = array(data.exchange && data.exchange.contracts).filter((item) => ["P", "Y", "OI"].includes(contractVariety(item)));
    const technical = core.filter((item) => item.technical && item.technical.status === "ok").slice(0, 3);
    const technicalDates = technical.map((item) => item.technical.snapshot_date || item.trade_date).filter(Boolean).sort();
    const technicalWhy = technical.map((item) => {
      const indicators = item.technical.indicators || {};
      const rsi = Number(indicators.RSI12);
      return `${first(item.product, item.symbol)} ${first(item.technical.trend, "待判断")}${Number.isFinite(rsi) ? ` · RSI ${rsi.toFixed(1)}` : ""}`;
    }).join("；");

    const factors = core.flatMap((item) => array(item.fundamental && item.fundamental.factors)
      .filter((factor) => !/跟踪框架/.test(first(factor.title, "")))
      .slice(0, 2)
      .map((factor) => ({ item, factor }))
    ).slice(0, 4);
    const fundamentalWhy = factors.map(({ item, factor }) => `${first(item.product, item.symbol)}：${first(factor.text, factor.title)}`).join("；");

    const countries = Object.values((data.supply && data.supply.countries) || {});
    const supplyWhy = countries.map((country) => {
      const metrics = Object.values(country.metrics || {}).slice(0, 3).map((metric) => {
        const latest = latestMetric(metric);
        return `${first(metric.label, "指标")} ${latest.value}${latest.unit}`;
      }).join("、");
      return `${first(country.name, "产地")} ${first(country.latest_period, "最近一期")}：${metrics || "沿用最近成功值"}`;
    }).join("；");

    const result = [];
    if (technical.length) result.push({
      _dimension: "technical", priority: "高", item: "油脂最近收盘技术结构",
      trigger: monitoringMode(data) === "closed" ? "休市锁定最近收盘" : "随有效交易日更新",
      why: technicalWhy,
      evidence_ids: technical.map((item) => `technical:${item.symbol}:${item.technical.snapshot_date || item.trade_date}`),
      _date: technicalDates.at(-1) || ""
    });
    if (factors.length) result.push({
      _dimension: "fundamental", priority: "高", item: "仓单、基差与现货证据",
      trigger: "基本面持续检查",
      why: fundamentalWhy,
      evidence_ids: factors.map(({ item, factor }) => `fundamental:${item.symbol}:${first(factor.title, "evidence")}`)
    });
    if (countries.length) result.push({
      _dimension: "fundamental", priority: "中", item: "产地供需持续更新",
      trigger: "官方数据更新",
      why: supplyWhy,
      evidence_ids: countries.map((country) => `supply:${first(country.name, "official")}:${first(country.latest_period, "latest")}`)
    });
    return result;
  }

  function renderBrief(payload, data) {
    $("market-state").textContent = first(payload.market_state, "待判断");
    $("decision-title").textContent = first(payload.headline, "等待 AI 研究结论");
    $("confidence-value").textContent = first(payload.confidence, "--");
    $("decision-summary").textContent = first(payload.summary, "暂无可发布摘要。");
    $("brief-generated").textContent = `生成 ${fmtTime(payload.generated_at || payload.updated_at, true)}`;

    const priorityRank = { "高": 1, "中": 2, "低": 3 };
    const structured = structuredWatch(data);
    const watch = structured.length
      ? structured.slice(0, 3)
      : array(payload.watchlist).slice().sort((a, b) => (priorityRank[a.priority] || 99) - (priorityRank[b.priority] || 99)).slice(0, 3);
    const dimensions = watch.map((item) => item._dimension === "fundamental"
      ? { key: "fundamental", label: "基本面", evidenceLabel: "官方供需与现货证据" }
      : item._dimension === "technical"
        ? { key: "technical", label: "技术面", evidenceLabel: "最近收盘指标" }
        : watchDimension(item));
    const fundamentalCount = dimensions.filter((item) => item.key === "fundamental").length;
    const technicalCount = dimensions.filter((item) => item.key === "technical").length;
    const fundamentalWatch = watch.find((item, index) => dimensions[index].key === "fundamental");
    const technicalWatch = watch.find((item, index) => dimensions[index].key === "technical");
    const confidence = first(payload.confidence, "待核验");
    const risks = array(payload.risks);
    const boundary = confidence === "低" ? "暂不扩大方向判断" : confidence === "中" ? "等待更多同向证据" : "按已确认方向跟踪";
    const closed = monitoringMode(data) === "closed";
    $("decision-thesis").innerHTML = `<section class="thesis-card is-fundamental"><span>基本面</span><strong>${esc(fundamentalWatch ? "证据持续更新" : "等待新增资料")}</strong><p>${esc(first(fundamentalWatch && fundamentalWatch.why, "尚无足够供需证据支持单边判断。"))}</p></section><section class="thesis-card is-technical"><span>技术面</span><strong>${esc(technicalWatch ? (closed ? "锁定最近交易日收盘" : first(technicalWatch.trigger, "随有效交易日更新")) : "等待趋势确认")}</strong><p>${esc(first(technicalWatch && technicalWatch.why, "技术与量化状态等待下一次有效突破。"))}</p></section><section class="thesis-card is-boundary"><span>执行边界</span><strong>${esc(`${confidence}置信度 · ${boundary}`)}</strong><p>${esc(closed ? "休市不生成伪行情；技术面沿用最近收盘，基本面与官方供需继续检查。" : first(risks[0], "缺少可核验的新证据时，维持当前观察结论。"))}</p></section>`;

    const moves = array(payload.key_moves).slice(0, 3);
    $("decision-evidence").innerHTML = moves.length ? moves.map((item) => `<article><span>${esc(first(item.label, "证据"))}</span><strong>${esc(displayEvidenceValue(item))}</strong><p>${esc(first(item.interpretation, "等待进一步解释。"))}</p></article>`).join("") : "<p class='empty-state'>暂无新增关键证据，继续按任务周期检查。</p>";
    const actions = array(payload.actions).slice(0, 2);
    const actionLabels = { completed: "已完成", monitoring: "监控中", blocked: "待补数据" };
    $("decision-action-list").innerHTML = actions.length ? actions.map((item) => `<article><span>${esc(actionLabels[item.status] || first(item.status, "待检查"))}</span><strong>${esc(first(item.task, "检查任务"))}</strong><p>${esc(first(item.next_check, item.result || "等待下一轮检查"))}</p></article>`).join("") : "<p class='empty-state'>暂无可发布任务；系统仍会持续检查。</p>";

    $("priority-mode-summary").textContent = watch.length ? `基本面 ${fundamentalCount} · 技术面 ${technicalCount}` : "等待新增证据";
    $("priority-list").innerHTML = watch.length ? watch.map((item, index) => {
      const dimension = dimensions[index];
      const evidenceCount = array(item.evidence_ids).length;
      const priorityLabel = first(item.priority, "观察");
      return `<li class="priority-item is-${dimension.key}"><div class="priority-topline"><span class="priority-kind">${esc(dimension.label)}</span><span class="priority-level">${esc(priorityLabel)}优先</span></div><strong>${esc(first(item.item, "关注项"))}</strong><p>${esc(first(item.why, "等待更多证据确认。"))}</p><footer><span><b>触发</b>${esc(first(item.trigger, "等待下一次检查"))}</span><span><b>依据</b>${esc(dimension.evidenceLabel)}${evidenceCount ? ` · ${evidenceCount}项` : ""}</span></footer></li>`;
    }).join("") : "<li class='priority-item is-empty'><strong>暂无新触发</strong><p>继续按自动任务周期检查基本面与技术面证据。</p></li>";
    $("trigger-list").innerHTML = watch.length ? watch.map((item) => `<li><strong>${esc(first(item.item, "关注项"))}</strong><span>${esc(first(item.trigger, "等待下一次自动检查"))}</span></li>`).join("") : "<li><strong>暂无等待触发</strong><span>系统仍会持续检查</span></li>";
  }

  const sectorGroups = {
    "油脂油料": ["油脂油料"],
    "黑色建材": ["黑色建材", "黑色金属"],
    "能源化工": ["能化材料", "能源化工"],
    "有色新能源": ["有色金属", "新能源材料"],
    "贵金属": ["贵金属"],
    "金融期货": ["利率期货", "股指期货"],
    "农产品": ["谷物饲料", "软商品"],
    "航运浆纸": ["造纸航运"]
  };

  function sectorFallback(exchange) {
    const contracts = array(exchange && exchange.contracts).filter((item) => Number.isFinite(Number(item.change_pct)));
    return Object.entries(sectorGroups).map(([sector, categories]) => {
      const members = contracts.filter((item) => categories.includes(item.category));
      if (!members.length) return null;
      const ranked = members.slice().sort((a, b) => Number(b.change_pct) - Number(a.change_pct));
      const average = members.reduce((total, item) => total + Number(item.change_pct), 0) / members.length;
      const state = average > .5 ? "偏强" : average < -.5 ? "偏弱" : "分化";
      return {
        sector,
        state,
        summary: "AI 板块简报待生成；当前先展示可追溯的主力合约强弱结构。",
        evidence: [{ value: `平均涨跌 ${average >= 0 ? "+" : ""}${average.toFixed(2)}%；领涨 ${first(ranked[0].product, ranked[0].symbol)}；领跌 ${first(ranked.at(-1).product, ranked.at(-1).symbol)}` }]
      };
    }).filter(Boolean);
  }

  const expandedSectors = new Set();

  function sectorEvidenceDetails(evidence) {
    const items = array(evidence);
    if (!items.length) {
      return "<section class='sector-evidence-item is-empty'><strong>暂无可追溯证据</strong><p>等待下一轮行情与事件采集。</p></section>";
    }
    return items.map((item) => {
      const source = first(item.source, "来源待核验");
      const observedAt = item.observed_at ? fmtTime(item.observed_at, true) : "时间待核验";
      return `<section class="sector-evidence-item"><header><strong>${esc(first(item.label, "行情证据"))}</strong><span>${esc(source)} · ${esc(observedAt)}</span></header><p>${esc(first(item.value, "数值待核验"))}</p>${item.detail ? `<small>${esc(item.detail)}</small>` : ""}</section>`;
    }).join("");
  }

  function bindSectorViewToggles() {
    const grid = $("sector-view-grid");
    grid.onclick = (event) => {
      const button = event.target.closest(".sector-view-toggle");
      if (!button || !grid.contains(button)) return;
      const sector = button.dataset.sector;
      const details = $(button.getAttribute("aria-controls"));
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      button.querySelector(".sector-view-affordance").textContent = expanded ? "展开证据链" : "收起证据链";
      button.closest(".sector-view-card").classList.toggle("is-expanded", !expanded);
      details.hidden = expanded;
      if (expanded) expandedSectors.delete(sector);
      else expandedSectors.add(sector);
    };
  }

  function renderSectorViews(payload, data) {
    const generated = array(payload.sector_views);
    const views = generated.length ? generated : sectorFallback(data.exchange || {});
    $("sector-intelligence-updated").textContent = generated.length
      ? `AI 生成 ${fmtTime(payload.generated_at || payload.updated_at, true)}`
      : `行情结构 ${fmtTime((data.exchange || {}).updated_at, true)}`;
    $("sector-view-grid").innerHTML = views.length ? views.map((item, index) => {
      const sector = first(item.sector, "未分类板块");
      const expanded = expandedSectors.has(sector);
      const detailsId = `sector-evidence-${index}`;
      const state = first(item.state, "数据不足");
      const stateClass = state === "偏强" ? "is-strong" : state === "偏弱" ? "is-weak" : state === "分化" ? "is-split" : "is-neutral";
      return `<article class="sector-view-card ${stateClass}${expanded ? " is-expanded" : ""}"><button class="sector-view-toggle" type="button" data-sector="${esc(sector)}" aria-expanded="${expanded}" aria-controls="${detailsId}"><header><strong>${esc(sector)}</strong><span>${esc(state)}</span></header><p class="sector-summary">${esc(first(item.summary, "等待板块研判。"))}</p><span class="sector-view-affordance">${expanded ? "收起证据链" : "展开证据链"}</span></button><div class="sector-evidence-list" id="${detailsId}"${expanded ? "" : " hidden"}>${sectorEvidenceDetails(item.evidence)}</div></article>`;
    }).join("") : "<article class='sector-view-card is-empty'><strong>暂无板块数据</strong><p>等待下一轮全市场行情刷新。</p></article>";
    bindSectorViewToggles();
  }

  function compactLots(value) {
    const numeric = Number(value);
    return Number.isFinite(numeric) && Math.abs(numeric) >= 10000 ? `${(numeric / 10000).toFixed(2)} 万手` : numberOrText(value);
  }

  function renderPulse(payload, watch) {
    const desiredProducts = ["P", "Y", "OI", "M", "RM"];
    const allContracts = array(payload.contracts);
    const liveQuotes = array(watch && watch.quotes);
    const contracts = desiredProducts.map((product) => liveQuotes.find((item) => item.product === product) || allContracts.find((item) => item.product === product && Number(item.contract_rank) === 1) || allContracts.find((item) => item.product === product)).filter(Boolean);
    const live = liveQuotes.length > 0;
    $("pulse-updated").textContent = `${live ? "盘中行情" : "行情快照"} ${fmtTime(live ? watch.generated_at : payload.updated_at, true)}`;
    $("market-pulse").innerHTML = contracts.length ? contracts.map((item) => {
      const change = item.change_pct != null ? item.change_pct : item.change;
      return `<article class="pulse-card"><header><strong>${esc(first(item.name, item.symbol))}</strong><span>${esc(first(item.symbol, "--"))}</span></header><div class="pulse-price"><strong>${number(item.price)}</strong><b class="${direction(change)}">${pct(change)}</b></div><div class="pulse-meta"><span>成交 ${esc(compactLots(item.volume))}</span><span>持仓 ${esc(compactLots(item.open_interest))}</span></div></article>`;
    }).join("") : "<article class='pulse-card'>暂无可用行情</article>";
  }

  function eventTime(item) { return item.time || item.observed_at || item.generated_at || item.updated_at || item.date; }

  function monitoringMode(data) {
    const weekday = new Intl.DateTimeFormat("en-US", { weekday: "short", timeZone: "Asia/Shanghai" }).format(new Date());
    const researchSession = data.status && data.status.automation && data.status.automation.research && data.status.automation.research.session;
    return weekday === "Sat" || weekday === "Sun" || researchSession === "weekend" || researchSession === "holiday" ? "closed" : "continuous";
  }

  function timestamp(value) {
    const text = String(value == null ? "" : value);
    const dateOnly = text.match(/^(\d{4})-(\d{2})-(\d{2})(?:-|$)/);
    const parsed = dateOnly && !text.includes("T") && !text.includes(":") ? new Date(`${dateOnly[1]}-${dateOnly[2]}-${dateOnly[3]}T00:00:00+08:00`) : new Date(value);
    return parsed.getTime();
  }

  function relativeAge(value) {
    const text = String(value == null ? "" : value);
    if (/^\d{4}-\d{2}-\d{2}(?:-|$)/.test(text) && !text.includes("T") && !text.includes(":")) return "当日发布";
    const time = timestamp(value);
    if (!Number.isFinite(time)) return "时间待核验";
    const minutes = Math.max(0, Math.floor((Date.now() - time) / 60000));
    if (minutes < 1) return "刚刚";
    if (minutes < 60) return `${minutes} 分钟前`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} 小时前`;
    return `${Math.floor(hours / 24)} 天前`;
  }

  function eventScope(item, fallback) {
    const ids = array(item && (item.evidence_ids || item.evidence_id)).map((id) => String(id).split(":").pop().toUpperCase()).filter(Boolean);
    return ids.length ? ids.slice(0, 3).join(" · ") : fallback;
  }

  function eventEvidence(item) {
    const readable = array(item && item.evidence);
    return readable.length ? readable : array(item && (item.evidence_ids || item.evidence_id));
  }

  function completeTimelineSummary(title, value) {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    const sentences = text.match(/[^。！？!?；;]+[。！？!?；;]/g) || [];
    let result = "";
    for (const sentence of sentences) {
      if (result && result.length + sentence.length > 180) break;
      if (!result && sentence.length > 180) continue;
      result += sentence.trim();
      if (result.length >= 90) break;
    }
    if (result) return result;
    const cleanTitle = String(title || "来源内容待核验").replace(/^[【\[]|[】\]]$/g, "").trim();
    return /[。！？!?；;]$/.test(cleanTitle) ? cleanTitle : `${cleanTitle}。`;
  }

  function moveImpact(value) {
    const matched = String(value == null ? "" : value).match(/[-+]?\d+(?:\.\d+)?%/g) || [];
    const largest = matched.reduce((max, item) => Math.max(max, Math.abs(Number(item.replace("%", "")))), 0);
    return largest >= 3 ? "高" : largest >= 1 ? "中" : "低";
  }

  function eventTimelineType(item) {
    const text = `${first(item.category, "")} ${first(item.title, "")} ${first(item.summary, "")}`.toLowerCase();
    if (/天气|气象|降雨|降水|干旱|洪水|高温|低温|霜冻|厄尔尼诺|拉尼娜|weather|rain|drought|flood|temperature/.test(text)) return "weather";
    if (/政策|关税|禁令|法案|补贴|配额|监管|制裁|生物柴油|b\d{2,3}/.test(text)) return "policy";
    if (/美联储|利率|汇率|美元|通胀|就业|央行|宏观|地缘|战争/.test(text)) return "macro";
    return "industry";
  }

  function researchPoints(value) {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    if (!text) return [];
    const matcher = /(?:^|\s)(?:\d{1,2}[.、)]|[（(]\d{1,2}[）)])\s*/g;
    const markers = [];
    let match;
    while ((match = matcher.exec(text)) !== null) markers.push({ start: match.index, end: matcher.lastIndex });
    if (markers.length) return markers.map((marker, index) => text.slice(marker.end, markers[index + 1] ? markers[index + 1].start : text.length).trim()).filter(Boolean);
    return (text.match(/.+?(?:[。！？；]|[!?;](?=\s|$)|$)/g) || [text]).map((part) => part.trim()).filter(Boolean);
  }

  function fallbackResearchReading(summary) {
    const text = String(summary || "").replace(/\s+/g, " ").trim();
    const sections = { core: [], strategy: [], risk: [] };
    const matcher = /(核心观点|核心结论|主要观点|观点摘要|关键结论|结论|策略建议|投资建议|操作建议|交易建议|后市展望|风险提示|风险因素|主要风险)\s*[:：]?\s*/g;
    const markers = [];
    let match;
    while ((match = matcher.exec(text)) !== null) {
      const label = match[1];
      const key = /风险/.test(label) ? "risk" : /建议|展望/.test(label) ? "strategy" : "core";
      markers.push({ start: match.index, end: matcher.lastIndex, key });
    }
    if (markers.length) markers.forEach((marker, index) => {
      sections[marker.key].push(...researchPoints(text.slice(marker.end, markers[index + 1] ? markers[index + 1].start : text.length)));
    });
    else sections.core = researchPoints(text);
    const clause = (points) => researchPoints(points[0] || "")[0] || "";
    const driverTerms = /库存|供需|产量|出口|进口|需求|价格|成本|政策|利率|汇率|地缘|PMI|天气/;
    const driver = sections.core.slice(1).find((point) => driverTerms.test(point));
    const riskCandidate = [...sections.risk, ...sections.core, ...sections.strategy].find((point) => /风险|警惕|不确定|冲突|下行/.test(point));
    return {
      quick_points: [
        { label: "核心结论", text: clause(sections.core) || clause(sections.strategy) || "来源摘要未提供可独立提取的核心结论。" },
        { label: "主要驱动", text: clause(driver ? [driver] : sections.core.slice(1)) || "来源摘要未提供可独立提取的主要驱动。" },
        { label: "关键风险", text: clause(sections.risk) || clause(riskCandidate ? [riskCandidate] : []) || "来源摘要未单列风险，需进一步核验。" }
      ],
      sections,
      reading_notice: "以下分类与选择由AI基于所列来源摘要生成，所列文字来自来源摘要；不代表任何来源方官方立场，也不构成投资建议，请自行核验。"
    };
  }

  function researchReading(item) {
    const view = item && item.reading_view;
    if (view && array(view.quick_points).length && view.sections) return view;
    return fallbackResearchReading(item && item.summary);
  }

  function researchQuickHtml(item) {
    return `<div class="research-quick-points">${array(item.quickPoints).map((point) => `<span><b>${esc(first(point.label, "阅读要点"))}</b><em>${esc(first(point.text, "需进一步核验。"))}</em></span>`).join("")}</div>${item.readingNotice ? `<small class="timeline-ai-label">${esc(item.readingNotice)}</small>` : ""}`;
  }

  function researchSectionHtml(label, points, emptyText) {
    const values = array(points).filter(Boolean);
    return `<article><span>${esc(label)}</span>${values.length ? `<ul>${values.map((point) => `<li>${esc(point)}</li>`).join("")}</ul>` : `<p>${esc(emptyText)}</p>`}</article>`;
  }

  function researchDetailHtml(item) {
    const sections = item.researchSections || {};
    const sourceControl = item.url ? `<a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">查看原始研报</a>` : item.sourceSummaryAvailable ? '<small class="timeline-source-note">来源未提供可直接打开的原始研报链接；可在下方核验未按字数截断的完整来源摘要。</small>' : '<small class="timeline-source-note">来源未提供可直接打开的原始研报链接或可核验摘要，本站不补写内容性结论。</small>';
    const fullSummary = item.sourceSummaryAvailable ? `<details class="research-source-summary"><summary>查看完整来源摘要</summary><p>${esc(item.sourceSummary)}</p>${item.summaryNotice ? `<small class="timeline-source-note">${esc(item.summaryNotice)}</small>` : ""}</details>` : "";
    return `<section class="research-reading-detail"><div class="research-section-grid">${researchSectionHtml("核心观点", sections.core, "来源摘要未提供可独立提取的核心观点。")}${researchSectionHtml("策略建议", sections.strategy, "来源摘要未单列策略建议。")}${researchSectionHtml("风险提示", sections.risk, "来源摘要未单列风险，需进一步核验。")}</div><small class="timeline-ai-notice">${esc(item.readingNotice)}</small></section><section class="research-recommendation"><span>推荐与来源</span><p>${esc(item.detail)}</p><div class="research-evidence">${array(item.evidence).filter(Boolean).map((entry) => `<b>${esc(entry)}</b>`).join("")}</div>${sourceControl}</section>${fullSummary}`;
  }

  function weatherDetailHtml(item) {
    const analysis = item.weatherAnalysis || {};
    const mechanism = analysis.mechanism_source || {};
    return `<section class="timeline-detail-summary weather-facts"><span>直接天气事实</span><p>${esc(first(analysis.direct_facts, item.detailSummary))}</p><p><b>当前物候</b> ${esc(first(analysis.stage, "物候阶段待核验"))}</p>${item.url ? `<a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">查看直接预报</a>` : ""}</section><section><span>产量因果链</span><p>${esc(first(analysis.production_chain, item.detail))}</p></section><section><span>行情传导</span><p>${esc(first(analysis.market_chain, "尚无足够证据判断行情方向。"))}</p></section><section><span>判断边界</span><p>${esc(first(analysis.boundary, "单一地点和单周预报不能直接确认减产。"))}</p>${mechanism.url ? `<a href="${esc(mechanism.url)}" target="_blank" rel="noopener noreferrer">${esc(first(mechanism.name, "查看农业机制依据"))}</a>` : ""}<small class="timeline-ai-notice">${esc(item.aiNotice)}</small></section>`;
  }

  function buildTimeline(data) {
    const events = [];
    array(data.watch && data.watch.events).forEach((item) => events.push({
      type: item.kind === "event" ? eventTimelineType(item) : "move",
      category: first(item.category, "市场扫描"), title: first(item.title, "市场事件"),
      summary: item.kind === "event" ? completeTimelineSummary(item.title, item.summary) : first(item.summary, "来源内容待核验"),
      detailSummary: item.kind === "event" ? first(item.detail_summary, completeTimelineSummary(item.title, item.summary)) : "",
      detail: first(item.interpretation, "暂无影响研判"), aiNotice: item.kind === "event" ? first(item.ai_notice, "AI 基于来源返回内容整理，非来源方原话，不代表来源方官方立场，不构成投资建议；请自行核验。") : "",
      evidence: eventEvidence(item), source: first(item.source, "市场扫描"), time: eventTime(item),
      scope: first(item.scope, "相关合约"), impact: first(item.impact, "低"), nextCheck: "下一轮5分钟扫描",
      url: item.url, directSourceAvailable: Boolean(item.url), weatherAnalysis: item.weather_analysis
    }));
    array(data.brief.key_moves).forEach((item) => events.push({
      type: "move", category: "市场异动", title: first(item.label, "行情证据"), summary: first(item.value, "数值待核验"),
      detail: first(item.interpretation, "暂无补充解释"), evidence: eventEvidence(item), source: first(item.source, "已发布数据"),
      time: eventTime(item), scope: eventScope(item, "相关合约"), impact: moveImpact(item.value), nextCheck: "下一轮行情检查"
    }));
    const report = array(data.reports.reports || data.reports).slice(0, 1)[0];
    if (report) events.push({
      type: "report", category: "研究报告", title: first(report.headline || report.title, "最新研究报告"),
      summary: first(report.summary || report.subtitle, "研究报告已发布"), detail: "完整论证、数据出处与风险说明保留在 AI 报告正文中。",
      aiNotice: "该报告摘要由AI基于报告正文生成，不代表任何来源方官方立场，也不构成投资建议；请自行核验。",
      evidence: [first(report.id || report.slug, "最新报告")], source: first(report.source, "Vinson Research"), time: eventTime(report),
      scope: "油脂研究", impact: "中", nextCheck: "下一次研究任务"
    });
    if (data.researchWatch && data.researchWatch.status === "ready") {
      array(data.researchWatch.items).forEach((item) => {
        const reading = researchReading(item);
        events.push({
          type: "report", category: first(item.sector, "公开研报"), title: first(item.title, "公开研报"),
          summary: first(item.summary, "机构公开晨报已更新"), sourceSummary: first(item.summary, ""), summaryNotice: first(item.summary_notice, ""),
          quickPoints: array(reading.quick_points), researchSections: reading.sections || {}, readingNotice: first(reading.reading_notice, item.ai_notice),
          detail: `推荐依据：${first(item.recommendation_reason, "与市场研究相关")}。${first(item.ai_notice, "推荐分、筛选和推荐依据由AI基于所列来源字段生成，不代表任何来源方官方立场，也不构成投资建议；请自行核验。")}`,
          evidence: [first(item.organization, "机构研究"), `推荐分 ${first(item.recommendation_score, "--")}`, ...array(item.topics)],
          source: first(item.source, "公开研报搜索"), time: item.published_at || data.researchWatch.generated_at,
          scope: array(item.topics).join(" · ") || first(item.sector, "跨板块"), impact: "中", nextCheck: "下一轮5分钟研报扫描", url: item.url,
          isPublicResearch: true, sourceSummaryAvailable: item.summary_type !== "missing_source_content"
        });
      });
    }
    if (data.supply && !data.supply._error && Object.keys(data.supply).length) {
      const countries = Object.values(data.supply.countries || {});
      const summary = countries.length ? countries.map((item) => `${first(item.name, "来源")} ${first(item.latest_period, "待更新")}`).join(" · ") : "供需资料已检查";
      const detail = countries.length ? countries.map((item) => `${first(item.name, "来源")}：${first(item.status_message, item.status || "已检查")}`).join("；") : `数据更新：${first(data.supply.generated_at, "待核验")}`;
      events.push({ type: "supply", category: "供需更新", title: "官方供需资料检查", summary, detail,
        evidence: countries.map((item) => first(item.name, "官方来源")), source: "MPOB · GAPKI · USDA",
        time: data.supply.generated_at || data.supply.checked_at || data.supply.updated_at, scope: "P · Y · OI", impact: "中", nextCheck: "按官方发布周期复查" });
    }
    return events.sort((a, b) => (timestamp(eventTime(b)) || 0) - (timestamp(eventTime(a)) || 0));
  }

  function renderTimeline(events, filter = "all") {
    const visible = filter === "all" ? events : events.filter((item) => item.type === filter);
    const labels = { move: "行情", weather: "天气", policy: "政策", industry: "产业", macro: "宏观", report: "研究", supply: "供需" };
    document.querySelectorAll("[data-filter]").forEach((button) => {
      const type = button.dataset.filter;
      const count = type === "all" ? events.length : events.filter((item) => item.type === type).length;
      button.innerHTML = `<span>${esc(button.dataset.label || labels[type] || type)}</span><b>${count}</b>`;
    });
    $("intelligence-timeline").innerHTML = visible.length ? visible.map((item, index) => {
      const detailId = `timeline-detail-${filter}-${index}`;
      const evidence = array(item.evidence).filter(Boolean);
      return `<article class="timeline-item" data-type="${esc(item.type)}">
        <time class="timeline-time" datetime="${esc(item.time)}"><strong>${esc(fmtTime(item.time, false))}</strong><small>${esc(relativeAge(item.time))}</small></time>
        <div class="timeline-content">
          <button type="button" aria-expanded="false" aria-controls="${detailId}">
            <span class="timeline-copy"><span class="timeline-title-row"><b class="timeline-category">${esc(item.category || labels[item.type] || item.type)}</b><h3>${esc(item.title)}</h3></span>${item.isPublicResearch ? researchQuickHtml(item) : `<p>${esc(item.summary)}</p>${item.aiNotice ? `<small class="timeline-ai-label">${esc(item.aiNotice)}</small>` : ""}`}</span>
            <span class="timeline-context"><span><small>影响合约</small><b>${esc(first(item.scope, "待核验"))}</b></span><span><small>来源</small><b>${esc(item.source)}</b></span><span><small>影响级别</small><b class="impact-${esc(item.impact || "低")}">${esc(first(item.impact, "低"))}</b></span></span>
            <span class="timeline-toggle" aria-hidden="true">展开</span>
          </button>
          <div id="${detailId}" class="timeline-detail">
            ${item.isPublicResearch ? researchDetailHtml(item) : item.type === "weather" && item.weatherAnalysis ? weatherDetailHtml(item) : `${item.detailSummary ? `<section class="timeline-detail-summary"><span>事件详情</span><p>${esc(item.detailSummary)}</p><small class="timeline-ai-notice">${esc(item.aiNotice)}</small></section>` : ""}<section><span>影响研判</span><p>${esc(item.detail)}</p>${item.aiNotice ? `<small class="timeline-ai-notice">${esc(item.aiNotice)}</small>` : ""}</section><section><span>关键证据</span>${evidence.length ? `<ul>${evidence.map((entry) => `<li>${esc(entry)}</li>`).join("")}</ul>` : "<p>本轮没有新增可核验证据。</p>"}</section><section><span>下一步检查</span><p>${esc(first(item.nextCheck, "等待下一轮自动检查"))}</p>${item.url ? `<a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">${item.type === "report" ? "查看原始研报" : "查看直接来源"}</a>` : ["weather", "policy", "industry", "macro"].includes(item.type) ? '<small class="timeline-source-note">未提供可直接打开的原文链接；本页仅展示已获取内容的整理摘要。</small>' : ""}</section>`}
          </div>
        </div>
      </article>`;
    }).join("") : "<p class='empty-state'>当前分类没有新增可发布的行情、天气、政策、产业、宏观、研究或供需证据。</p>";
    document.querySelectorAll(".timeline-content button").forEach((button) => button.addEventListener("click", () => {
      const detail = document.getElementById(button.getAttribute("aria-controls"));
      const open = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!open));
      detail.classList.toggle("is-open", !open);
      button.querySelector(".timeline-toggle").textContent = open ? "展开" : "收起";
    }));
  }

  function renderOilDesk(payload) {
    const oilProducts = new Set(["P", "Y", "OI", "FCPO", "CPOTR"]);
    const contracts = array(payload.contracts).filter((item) => oilProducts.has(item.product) && (Number(item.contract_rank) === 2 || !item.contract_rank));
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

    function render(contract, response = {}) {
      const technical = contract.technical || {};
      const fundamental = contract.fundamental || {};
      const judgement = contract.judgement || {};
      const indicators = technical.indicators || {};
      const levels = technical.levels || {};
      const news = array(contract.news_hotspots).slice(0, 4);
      const sources = array(response.sources);
      const sourceState = (status) => status === "ready" ? "已更新" : status === "not_applicable" ? "不适用" : status === "insufficient" ? "样本不足" : "已降级";
      const evidence = array(judgement.key_evidence);
      result.innerHTML = `<article class="contract-result-head"><div><span>${esc(first(contract.exchange, "--"))} · ${esc(first(contract.category, "--"))}</span><h3>${esc(first(contract.product, "品种"))} <small>${esc(first(contract.symbol, "--"))}</small></h3><p>交易日 ${esc(first(contract.trade_date, "需进一步核验"))} · 生成 ${esc(fmtTime(response.generated_at, true))}</p></div><div class="contract-result-price ${direction(contract.change_pct)}"><strong>${esc(numberOrText(contract.price))}</strong><span>${esc(pct(contract.change_pct))}</span></div></article>${judgement.stance ? `<article class="contract-judgement"><div><span>后台综合判断</span><h4>${esc(judgement.stance)} <small>置信度 ${esc(first(judgement.confidence, "低"))}</small></h4><p>${esc(first(judgement.summary, "等待结构化判断。"))}</p></div><ul>${evidence.map((item) => `<li>${esc(item)}</li>`).join("")}</ul><p class="contract-risk">${esc(first(judgement.risk, "该判断不构成交易指令。"))}</p></article>` : ""}<div class="contract-analysis-grid"><section><header><span>技术面 · 即时重算</span><h4>${esc(first(technical.trend, "需进一步核验"))}</h4></header><p>${esc(first(technical.summary, "暂无结构化技术结论。"))}</p><dl class="contract-indicators">${Object.entries(indicators).slice(0, 6).map(([name, value]) => `<div><dt>${esc(name)}</dt><dd>${esc(numberOrText(value))}</dd></div>`).join("")}</dl><div class="contract-levels">${Object.entries(levels).map(([name, value]) => `<span>${esc(name)} <b>${esc(numberOrText(value))}</b></span>`).join("")}</div><div class="contract-detail-list">${detailList(technical.details)}</div></section><section><header><span>基本面与新闻 · 按品种检查</span><h4>${esc(first(fundamental.category, contract.category || "需进一步核验"))}</h4></header><p>${esc(first(fundamental.summary, "暂无结构化基本面结论。"))}</p><div class="contract-detail-list">${detailList(fundamental.factors)}</div><div class="contract-news">${news.length ? news.map((item) => `<div><span>${esc(first(item.date, "--"))} · ${esc(first(item.source, "来源待核验"))}</span>${item.url ? `<a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">${esc(first(item.title, "新闻"))}</a>` : `<strong>${esc(first(item.title, "新闻"))}</strong>`}</div>`).join("") : "<p>暂无直接新闻证据。</p>"}</div></section></div>${sources.length ? `<div class="contract-sources"><strong>本次来源状态</strong>${sources.map((item) => `<span class="${item.status === "ready" ? "is-ready" : item.status === "not_applicable" ? "" : "is-degraded"}"><b>${esc(first(item.name, "数据源"))}</b>${esc(sourceState(item.status))} · ${esc(item.observed_at ? fmtTime(item.observed_at, true) : first(item.detail, "时间待核验"))}</span>`).join("")}</div>` : ""}<p class="contract-quality">${esc(first(contract.data_quality, "数据质量说明待补充"))}</p>`;
    }

    exchangeFilter.onchange = populate;
    $("assistant-contract-confirm").onclick = async () => {
      const button = $("assistant-contract-confirm");
      const symbol = contractSelect.value;
      const snapshot = contracts.find((item) => item.symbol === symbol);
      if (!snapshot) {
        result.innerHTML = "<p class='empty-state'>请选择有效的具体合约。</p>";
        return;
      }
      button.disabled = true;
      button.textContent = "正在分析…";
      result.innerHTML = `<div class="contract-loading"><span></span><strong>正在按 ${esc(symbol)} 请求后台</strong><p>依次检查最新行情、日线技术结构与该品种相关基本面源。</p></div>`;
      try {
        const response = await fetch(`/api/assistant/contract-analysis?symbol=${encodeURIComponent(symbol)}`, { cache: "no-store" });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || !payload.contract) throw new Error(first(payload.message, `后台返回 ${response.status}`));
        render(payload.contract, payload);
      } catch (error) {
        result.innerHTML = `<div class="contract-request-error"><strong>${esc(symbol)} 即时分析未完成</strong><p>${esc(first(error && error.message, "后台数据源暂不可用"))}</p><span>为避免误判，本次不自动展示旧的静态结论。你可以稍后重试。</span></div>`;
      } finally {
        button.disabled = false;
        button.textContent = "查看分析";
      }
    };
    populate();
  }

  function renderStatus(payload) {
    const state = first(payload.status, "degraded");
    const klass = state === "ready" || state === "ok" ? "is-ready" : state === "error" ? "is-error" : "is-degraded";
    $("overall-state").className = klass;
    $("overall-state").classList.add("data-chain-trigger");
    $("overall-state").textContent = state === "ready" || state === "ok" ? "数据链正常" : state === "degraded" ? "部分数据延迟" : "数据链异常";
    $("system-label").textContent = $("overall-state").textContent;
    $("system-label").className = klass;
    const datasets = Object.values(payload.datasets || {});
    const counts = { ready: 0, stale: 0, invalid: 0 };
    datasets.forEach((item) => { const key = item.state === "ready" ? "ready" : item.state === "invalid" || item.state === "missing" ? "invalid" : "stale"; counts[key] += 1; });
    $("health-summary").innerHTML = `<div class="health-stat"><strong class="is-ready">${counts.ready}</strong><span>正常</span></div><div class="health-stat"><strong class="is-degraded">${counts.stale}</strong><span>延迟</span></div><div class="health-stat"><strong class="is-error">${counts.invalid}</strong><span>缺失</span></div>`;
    const abnormalDatasets = datasets.filter((item) => item.state !== "ready");
    $("data-chain-details-title").textContent = abnormalDatasets.length ? `${abnormalDatasets.length} 条数据链需要关注` : "全部数据链正常";
    $("data-chain-details-list").innerHTML = abnormalDatasets.length ? abnormalDatasets.map((item) => {
      const itemClass = item.state === "invalid" || item.state === "missing" ? "is-error" : "is-degraded";
      const stateLabel = item.state === "stale" ? "延迟" : item.state === "missing" ? "缺失" : item.state === "invalid" ? "异常" : first(item.state, "待查");
      const detail = item.state === "stale"
        ? `最近有效数据 ${fmtTime(item.observed_at || item.updated_at, true)}，已超过刷新时限。`
        : item.state === "missing" ? "尚未发现可发布的数据文件。"
          : item.state === "invalid" ? "数据内容未通过格式校验。" : "该数据链需要进一步检查。";
      return `<article class="data-chain-issue"><div><strong>${esc(first(item.label, item.route))}</strong><b class="${itemClass}">${esc(stateLabel)}</b></div><code>${esc(first(item.route, "数据路径待核验"))}</code><p>${esc(detail)}</p></article>`;
    }).join("") : "<p class='data-chain-ok'>当前所有数据链均在允许的新鲜度范围内。</p>";
    $("data-chain-details-note").textContent = `状态检查 ${fmtTime(payload.served_at, true)} · 系统将继续自动复查`;
    $("overall-state").title = abnormalDatasets.length ? `点击查看 ${abnormalDatasets.length} 条异常数据链` : "点击查看数据链状态";
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

  function bindDataChainDetails() {
    const trigger = $("overall-state");
    const panel = $("data-chain-details");
    const close = $("data-chain-details-close");
    const setOpen = (open) => {
      panel.hidden = !open;
      trigger.setAttribute("aria-expanded", String(open));
    };
    trigger.onclick = () => setOpen(panel.hidden);
    close.onclick = () => { setOpen(false); trigger.focus(); };
    document.addEventListener("click", (event) => {
      if (!panel.hidden && !panel.contains(event.target) && event.target !== trigger) setOpen(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !panel.hidden) { setOpen(false); trigger.focus(); }
    });
  }

  function renderMonitorMode(data) {
    const nonTrading = monitoringMode(data) === "closed";
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

  let activeTimelineFilter = "all";

  function bindFilters(events) {
    document.querySelectorAll("[data-filter]").forEach((button) => button.onclick = () => {
      activeTimelineFilter = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("is-active", item === button));
      renderTimeline(events, activeTimelineFilter);
    });
  }

  function bindSectionNavigation() {
    const links = Array.from(document.querySelectorAll('.command-nav > nav a[href^="#"]'));
    const items = links.map((link) => ({
      link,
      section: document.querySelector(link.getAttribute("href"))
    })).filter((item) => item.section);
    if (!items.length) return;

    const setCurrent = (current) => {
      items.forEach(({ link }) => {
        if (link === current) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    };

    const updateCurrent = () => {
      const headerOffset = 116;
      const positions = items.map((item) => ({ ...item, top: item.section.getBoundingClientRect().top }));
      const reachedBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4;
      if (reachedBottom) {
        const lastSection = items.slice().sort((a, b) => a.section.offsetTop - b.section.offsetTop).at(-1);
        setCurrent(lastSection.link);
        return;
      }
      const passed = positions.filter((item) => item.top <= headerOffset).sort((a, b) => b.top - a.top);
      const upcoming = positions.filter((item) => item.top > headerOffset).sort((a, b) => a.top - b.top);
      setCurrent((passed[0] || upcoming[0] || positions[0]).link);
    };

    items.forEach(({ link }) => link.addEventListener("click", () => setCurrent(link)));
    let scheduled = false;
    window.addEventListener("scroll", () => {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(() => {
        updateCurrent();
        scheduled = false;
      });
    }, { passive: true });
    window.addEventListener("hashchange", updateCurrent);
    updateCurrent();
  }

  async function load() {
    const entries = await Promise.all(Object.entries(sources).map(async ([key, urls]) => {
      try { return [key, await fetchFirst(urls)]; } catch (error) {
        const fallback = staticFallbacks[key] && staticFallbacks[key]();
        return [key, fallback || { _error: error.message }];
      }
    }));
    const data = Object.fromEntries(entries);
    renderBrief(data.brief || {}, data);
    renderSectorViews(data.brief || {}, data);
    renderPulse(data.oil || {}, data.watch || {});
    renderOilDesk(data.oil || {});
    renderSupplyDesk(data.supply || {});
    renderContractDesk(data.exchange || {});
    renderStatus(data.status || { status: "degraded" });
    renderMonitorMode(data);
    const events = buildTimeline(data);
    renderTimeline(events, activeTimelineFilter);
    bindFilters(events);
    const checkedAt = new Date().toISOString();
    $("refresh-note").textContent = `页面刷新 ${fmtTime(checkedAt, false)} · 不把系统检查写入时间线`;
    const scanAt = data.watch && (data.watch.events_updated_at || data.watch.generated_at);
    $("timeline-refresh-state").textContent = scanAt ? `5分钟全量扫描 · 最近 ${fmtTime(scanAt, false)} · 仅显示可追溯证据` : "等待首轮5分钟市场扫描";
  }

  function clock() { $("live-clock").textContent = new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).format(new Date()); }
  bindSectionNavigation();
  bindDataChainDetails();
  clock(); setInterval(clock, 1000);
  load(); setInterval(load, 60000);
})();

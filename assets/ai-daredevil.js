(function () {
  "use strict";

  const STRATEGIES = {
    bollinger: {
      label: "布林带模型", api: "/api/ai-daredevil", fallback: "data/ai_daredevil.json",
      kicker: "Bollinger RSI · Real Contract Fund",
      lead: "独立100万元虚拟基金，按布林带、RSI与MA6既定规则扫描跨板块机会。只使用真实交割月主力合约，收盘确认，下一开盘成交。",
      auditTitle: "布林带模型跨板块全量扫描",
      disciplines: [["真实交割月", "拒绝 P0、连续、加权和合成价格"], ["收盘确认", "布林、RSI与MA6日线信号不被盘中波动改写"], ["下一开盘", "只有取得可核验开盘价才记录虚拟成交"], ["跨板块复利", "按信号强度、品种上限和板块上限配置资金"]],
      notice: "本模式由 AI 基于所列真实合约行情、布林RSI模型信号和虚拟基金账本生成说明，不代表任何来源方的官方立场，也不构成投资建议。虚拟成交不等于真实成交，请自行核验。",
    },
    "pure-ai": {
      label: "纯AI决策", api: "/api/ai-daredevil/pure-ai", fallback: "data/ai_daredevil_pure_ai.json",
      kicker: "Source-grounded AI · Independent Fund",
      lead: "独立100万元虚拟基金。AI自行汇总技术指标、公开研报与基本面证据，决定开仓、平仓或等待；外部风控以约10%最大回撤为目标约束组合。",
      auditTitle: "纯AI技术与基本面全量研判",
      disciplines: [["证据约束", "只允许引用列明来源、时间和真实合约的数据"], ["独立研判", "AI自行选择指标权重并决定开仓、平仓或等待"], ["下一开盘", "收盘决定经校验后，仅在可核验的下一开盘执行"], ["回撤目标", "8%进入降风险区，目标约10%；跳空可能使实际回撤超出目标"]],
      notice: "本模式的观点、开平仓决定与文字解释由 AI 基于页面列明的技术指标、基本面材料和虚拟账本生成，不代表任何来源方官方立场，也不构成投资建议。约10%回撤是风控目标而非保证，请自行核验。",
    },
  };
  const money = new Intl.NumberFormat("zh-CN", { style: "currency", currency: "CNY", maximumFractionDigits: 2 });
  const number = new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 });
  let selected = "bollinger";
  let requestToken = 0;

  function el(id) { return document.getElementById(id); }
  function percent(value) { return Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(2)}%` : "--"; }
  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
  }
  function colorize(node, value) {
    node.classList.remove("is-positive", "is-negative");
    if (Number(value) > 0) node.classList.add("is-positive");
    if (Number(value) < 0) node.classList.add("is-negative");
  }
  function formatTime(value) {
    if (!value) return "--";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toLocaleString("zh-CN", { hour12: false });
  }
  function actionLabel(value) {
    return ({ WAIT: "等待", ENTER_LONG: "开多", ENTER_SHORT: "开空", EXIT_LONG: "平多", EXIT_SHORT: "平空", ADD_LONG: "加多", ADD_SHORT: "加空", ROLL: "换月" })[value] || value || "待核验";
  }

  async function fetchPayload(url) {
    const response = await fetch(`${url}?_=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
  async function load(strategy) {
    const config = STRATEGIES[strategy];
    try { return { payload: await fetchPayload(config.api), transport: "实时 API" }; }
    catch (error) { return { payload: await fetchPayload(config.fallback), transport: "静态备份" }; }
  }

  function applyStrategyCopy(strategy) {
    const config = STRATEGIES[strategy];
    el("strategy-kicker").textContent = config.kicker;
    el("fund-lead").textContent = config.lead;
    el("scan-audit-title").textContent = config.auditTitle;
    el("chart-legend-label").textContent = `${config.label}净值`;
    el("equity-chart-title").textContent = `${config.label}历史净值曲线`;
    el("risk-notice-copy").textContent = config.notice;
    el("inline-ai-notice").textContent = `AI 生成说明：${config.notice}`;
    config.disciplines.forEach((row, index) => {
      el(`discipline-${index + 1}-title`).textContent = row[0];
      el(`discipline-${index + 1}-copy`).textContent = row[1];
    });
  }

  function renderMetrics(data) {
    const summary = data.summary || {};
    el("equity").textContent = money.format(Number(summary.equity || 0));
    el("net-value").textContent = `净值 ${Number(summary.net_value || 1).toFixed(4)}`;
    el("cumulative-return").textContent = percent(summary.cumulative_return); colorize(el("cumulative-return"), summary.cumulative_return);
    el("annualized-return").textContent = summary.annualized_return == null ? "年化：样本不足" : `年化 ${percent(summary.annualized_return)}`;
    el("daily-pnl").textContent = money.format(Number(summary.daily_pnl || 0)); colorize(el("daily-pnl"), summary.daily_pnl);
    el("realized-pnl").textContent = `已实现 ${money.format(Number(summary.realized_pnl || 0))}`;
    el("max-drawdown").textContent = percent(summary.max_drawdown || 0); colorize(el("max-drawdown"), summary.max_drawdown);
    el("sharpe").textContent = summary.sharpe == null ? "夏普：样本不足" : `夏普 ${Number(summary.sharpe).toFixed(2)}`;
    el("margin-use").textContent = percent(summary.margin_usage || 0);
    el("used-margin").textContent = money.format(Number(summary.used_margin || 0));
    el("available-cash").textContent = money.format(Number(summary.available_cash || 0));
    el("gross-exposure").textContent = `总敞口 ${percent(summary.gross_exposure_multiple || 0)}权益`;
  }

  function renderChart(points) {
    const svg = el("equity-chart"); const empty = el("chart-empty");
    svg.replaceChildren(svg.querySelector("title"), svg.querySelector("desc"));
    const valid = Array.isArray(points) ? points.filter((point) => Number.isFinite(Number(point.net_value))) : [];
    if (valid.length < 2) { empty.hidden = false; return; }
    empty.hidden = true;
    const values = valid.map((point) => Number(point.net_value));
    const min = Math.min(...values, 0.995); const max = Math.max(...values, 1.005);
    const pad = { left: 54, right: 22, top: 20, bottom: 34 }; const width = 920 - pad.left - pad.right; const height = 320 - pad.top - pad.bottom;
    const x = (index) => pad.left + width * index / Math.max(1, valid.length - 1);
    const y = (value) => pad.top + height * (max - value) / Math.max(.0001, max - min);
    for (let index = 0; index <= 4; index += 1) {
      const value = min + (max - min) * index / 4;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", pad.left); line.setAttribute("x2", 920 - pad.right); line.setAttribute("y1", y(value)); line.setAttribute("y2", y(value)); line.setAttribute("stroke", "rgba(177,211,193,.12)"); svg.appendChild(line);
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", 4); label.setAttribute("y", y(value) + 4); label.setAttribute("fill", "#91a99d"); label.setAttribute("font-size", "11"); label.textContent = value.toFixed(3); svg.appendChild(label);
    }
    const path = valid.map((point, index) => `${index ? "L" : "M"}${x(index)},${y(Number(point.net_value))}`).join(" ");
    const area = document.createElementNS("http://www.w3.org/2000/svg", "path"); area.setAttribute("d", `${path} L${x(valid.length - 1)},${pad.top + height} L${x(0)},${pad.top + height} Z`); area.setAttribute("fill", "rgba(94,224,163,.08)"); svg.appendChild(area);
    const curve = document.createElementNS("http://www.w3.org/2000/svg", "path"); curve.setAttribute("d", path); curve.setAttribute("fill", "none"); curve.setAttribute("stroke", "#5ee0a3"); curve.setAttribute("stroke-width", "3"); curve.setAttribute("vector-effect", "non-scaling-stroke"); svg.appendChild(curve);
    [0, valid.length - 1].forEach((index) => {
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text"); label.setAttribute("x", x(index)); label.setAttribute("y", 312); label.setAttribute("text-anchor", index ? "end" : "start"); label.setAttribute("fill", "#91a99d"); label.setAttribute("font-size", "11"); label.textContent = valid[index].date; svg.appendChild(label);
    });
  }

  function renderPositions(data) {
    const positions = Array.isArray(data.positions) ? data.positions : [];
    el("position-count").textContent = `${positions.length} 个品种`; el("positions-empty").hidden = positions.length > 0;
    el("positions-body").innerHTML = positions.map((position) => {
      const pnl = Number(position.unrealized_pnl || 0);
      return `<tr><td><strong>${escapeHtml(position.name || position.variety)}</strong><span>${escapeHtml(position.contract)}</span></td><td>${escapeHtml(position.entry_date || "--")}</td><td class="reason-cell">${escapeHtml(position.model_reason || "开仓依据待核验")}</td><td><em class="side-badge ${Number(position.side) === 1 ? "side-long" : "side-short"}">${Number(position.side) === 1 ? "多" : "空"}</em></td><td>${escapeHtml(position.quantity)} / ${escapeHtml(position.layers || 1)}</td><td>${number.format(position.average_price)}</td><td>${number.format(position.last_price)}</td><td>${money.format(position.notional || 0)}</td><td class="${pnl >= 0 ? "is-positive" : "is-negative"}">${money.format(pnl)}</td><td>${percent(position.weight || 0)}</td><td><strong>${escapeHtml(position.price_source || "待核验")}</strong><span>${escapeHtml(formatTime(position.price_time))}</span></td><td class="instruction-cell">${escapeHtml(position.next_instruction || "等待下一次完整日线确认")}</td></tr>`;
    }).join("");
  }

  function renderScanAudit(data) {
    const scan = data.scan_audit || {}; const universe = Number(scan.universe_count || 0); const discovered = Number(scan.discovered_count || 0); const evaluated = Number(scan.evaluated_count || 0); const candidates = Number(scan.candidate_count || 0); const orders = Number(scan.order_count || 0);
    el("scan-universe").textContent = universe ? `${universe} 个` : "--"; el("scan-discovered").textContent = universe ? `${discovered} / ${universe}` : "--"; el("scan-evaluated").textContent = universe ? `${evaluated} / ${universe}` : "--"; el("scan-candidates").textContent = scan.generated_at ? `${candidates} 个` : "--"; el("scan-orders").textContent = scan.generated_at ? `${orders} 条` : "--";
    const complete = scan.coverage_status === "complete"; el("scan-status").textContent = scan.generated_at ? `${complete ? "完整" : "部分"} · ${scan.as_of || "日期待核验"}` : "尚未扫描";
    if (!scan.generated_at) { el("scan-detail").textContent = "等待完整日线扫描记录；未扫描不等于没有信号。"; return; }
    const missing = Array.isArray(scan.missing_varieties) ? scan.missing_varieties : []; const prefix = scan.decision_summary ? `${scan.decision_summary}；` : ""; const coverage = complete ? "全部策略品种完成指标计算" : `${Math.max(0, universe - evaluated)} 个品种未完成${missing.length ? `（${missing.join("、")}）` : ""}`;
    el("scan-detail").textContent = `${prefix}${coverage}；候选决定 ${candidates} 个，待执行订单 ${orders} 条。扫描时间 ${formatTime(scan.generated_at)}。`;
  }

  function renderActivity(containerId, emptyId, items, kind) {
    const list = Array.isArray(items) ? items : []; el(emptyId).hidden = list.length > 0;
    el(containerId).innerHTML = list.map((item) => {
      const action = actionLabel(item.action); const detail = kind === "skipped" ? (item.reason || item.next_instruction || item.open_reason || action || "--") : (item.next_instruction || item.reason || item.open_reason || action || "--");
      const tail = kind === "trade" ? money.format(Number(item.pnl ?? item.realized_pnl ?? 0)) : (item.confidence != null ? `置信 ${percent(item.confidence)}` : `${item.quantity || 0} 手`);
      return `<article class="activity-item"><span>${escapeHtml(item.time || item.execution_date || item.signal_date || "--")}</span><div><strong>${escapeHtml(item.name || item.variety || "--")} · ${escapeHtml(item.contract || action)}</strong><small>${escapeHtml(detail)}</small></div><b class="${Number(item.pnl ?? item.realized_pnl ?? 0) >= 0 ? "is-positive" : "is-negative"}">${escapeHtml(tail)}</b></article>`;
    }).join("");
  }

  function renderSources(data) {
    const schedule = Array.isArray(data.refresh_schedule) ? data.refresh_schedule : [];
    el("refresh-timeline").innerHTML = schedule.map((item) => `<div class="refresh-slot"><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.time)}</strong><small>${escapeHtml(item.purpose)}</small></div>`).join("");
    const sources = Array.isArray(data.sources) ? data.sources : [];
    el("source-grid").innerHTML = sources.map((source) => `<article class="source-item ${escapeHtml(source.state || "failed")}"><span>${escapeHtml(source.priority || "--")}</span><strong>${escapeHtml(source.name)}</strong><small>${escapeHtml(source.note || source.state_label || "--")}</small></article>`).join("");
    el("next-refresh").textContent = data.next_refresh ? `下次 ${formatTime(data.next_refresh)}` : "等待调度";
  }

  function render(data, transport) {
    el("updated-at").textContent = formatTime(data.generated_at); el("refresh-session").textContent = `${data.refresh_reason || "定时刷新"} · ${data.market_date || "交易日待核验"}`; el("primary-source").textContent = data.price_source || "--"; el("source-state").textContent = transport; el("data-state").textContent = data.status_label || "状态待核验"; el("data-state").className = `data-state is-${data.status || "degraded"}`;
    renderMetrics(data); renderScanAudit(data); renderChart(data.equity_curve); renderPositions(data);
    const trades = Array.isArray(data.today_trades) ? data.today_trades : []; const pending = Array.isArray(data.pending_orders) ? data.pending_orders : []; const decisions = Array.isArray(data.latest_decisions) ? data.latest_decisions : []; const instructions = pending.length ? pending : decisions;
    el("trade-count").textContent = `${trades.length} 条`; el("pending-count").textContent = `${instructions.length} 条`; renderActivity("trades-list", "trades-empty", trades, "trade"); renderActivity("pending-list", "pending-empty", instructions, "instruction");
    const skipped = Array.isArray(data.skipped_signals) ? data.skipped_signals : []; el("skipped-count").textContent = `${skipped.length} 条`; renderActivity("skipped-list", "skipped-empty", skipped, "skipped"); renderSources(data);
  }

  async function boot() {
    const token = ++requestToken; applyStrategyCopy(selected); el("data-state").textContent = `正在载入${STRATEGIES[selected].label}`;
    try { const result = await load(selected); if (token === requestToken) render(result.payload, result.transport); }
    catch (error) { if (token === requestToken) { el("data-state").textContent = `${STRATEGIES[selected].label}数据不可用`; el("data-state").className = "data-state is-degraded"; } }
  }
  function initialStrategy() {
    const query = new URLSearchParams(window.location.search).get("strategy"); if (STRATEGIES[query]) return query;
    try { const saved = window.localStorage.getItem("ai-daredevil-strategy"); if (STRATEGIES[saved]) return saved; } catch (error) { /* optional */ }
    return "bollinger";
  }

  selected = initialStrategy(); el("strategy-select").value = selected;
  el("strategy-select").addEventListener("change", (event) => {
    selected = STRATEGIES[event.target.value] ? event.target.value : "bollinger";
    try { window.localStorage.setItem("ai-daredevil-strategy", selected); } catch (error) { /* optional */ }
    const url = new URL(window.location.href); if (selected === "bollinger") url.searchParams.delete("strategy"); else url.searchParams.set("strategy", selected); window.history.replaceState({}, "", url); boot();
  });
  boot(); window.setInterval(boot, 60 * 1000);
}());

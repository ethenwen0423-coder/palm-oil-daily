(function () {
  "use strict";

  const STRATEGIES = {
    bollinger: {
      label: "布林带模型", api: "/api/ai-daredevil", fallback: "data/ai_daredevil.json",
      backtestApi: "/api/ai-daredevil/monthly-backtest", backtestFallback: "data/ai_daredevil_monthly_backtest.json",
      kicker: "Bollinger RSI · Real Contract Fund",
      lead: "独立100万元虚拟基金，按布林带、RSI与MA6既定规则扫描跨板块机会。只使用真实交割月主力合约，收盘确认，下一开盘成交。",
      auditTitle: "布林带模型跨板块全量扫描",
      disciplines: [["真实交割月", "拒绝 P0、连续、加权和合成价格"], ["收盘确认", "布林、RSI与MA6日线信号不被盘中波动改写"], ["下一开盘", "只有取得可核验开盘价才记录虚拟成交"], ["跨板块复利", "按信号强度、品种上限和板块上限配置资金"]],
      notice: "本模式由 AI 基于所列真实合约行情、布林RSI模型信号和虚拟基金账本生成说明，不代表任何来源方的官方立场，也不构成投资建议。虚拟成交不等于真实成交，请自行核验。",
    },
    "pure-ai": {
      label: "纯AI决策", api: "/api/ai-daredevil/pure-ai", fallback: "data/ai_daredevil_pure_ai.json",
      kicker: "Source-grounded AI · Independent Fund",
      lead: "独立100万元虚拟基金。AI可为不同品种选择不同策略与有限整数手数，结合本地Python回测、技术指标、公开研报与基本面证据决定开平仓；不设置仓位、回撤、品种数量或板块上限，唯一目标是追求最高收益率。",
      auditTitle: "纯AI技术与基本面全量研判",
      disciplines: [["逐品种选策略", "每个品种可使用不同的AI自主、公开研究或本地回测策略"], ["本地Python回测", "真实交割月、收盘确认、下一开盘并计入成本，按净收益排序"], ["下一开盘", "AI决定经合约与时序校验后，仅在可核验的下一开盘执行"], ["收益率优先", "不设仓位、回撤、品种数量和板块上限；AI自行给出有限整数手数"]],
      notice: "本模式的策略选择、开平仓决定、手数与文字解释由 AI 基于页面列明的技术指标、基本面材料、本地回测和虚拟账本生成，不代表任何来源方官方立场，也不构成投资建议。无仓位与回撤上限可能导致负现金、权益归零或亏损超过本金，请自行核验。",
    },
  };
  const money = new Intl.NumberFormat("zh-CN", { style: "currency", currency: "CNY", maximumFractionDigits: 2 });
  const number = new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 });
  let selected = "bollinger";
  let requestToken = 0;
  let monthlyBacktestCache = null;
  let monthlyBacktestLoadedAt = 0;

  function el(id) { return document.getElementById(id); }
  function percent(value) { return Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(2)}%` : "--"; }
  function signedMoney(value) {
    const amount = Number(value);
    if (!Number.isFinite(amount)) return "--";
    if (amount > 0) return `+${money.format(amount)}`;
    if (amount < 0) return `-${money.format(Math.abs(amount))}`;
    return money.format(0);
  }
  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
  }
  function colorize(node, value) {
    node.classList.remove("is-positive", "is-negative");
    if (Number(value) > 0) node.classList.add("is-positive");
    if (Number(value) < 0) node.classList.add("is-negative");
  }
  function formatPositionPnl(value) {
    const amount = Number(value);
    if (!Number.isFinite(amount)) return { className: "position-pnl-zero", text: "--" };
    if (amount < 0) return { className: "position-pnl-negative", text: `（${money.format(Math.abs(amount))}）` };
    return { className: amount > 0 ? "position-pnl-positive" : "position-pnl-zero", text: money.format(amount) };
  }
  function formatTradePnl(value) {
    const amount = Number(value);
    if (!Number.isFinite(amount)) return { className: "position-pnl-zero", text: "--" };
    if (amount < 0) return { className: "is-negative", text: `（${money.format(Math.abs(amount))}）` };
    if (amount > 0) return { className: "is-positive", text: `+${money.format(amount)}` };
    return { className: "position-pnl-zero", text: money.format(0) };
  }
  function formatTime(value) {
    if (!value) return "--";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toLocaleString("zh-CN", { hour12: false });
  }
  function actionLabel(value) {
    return ({ WAIT: "等待", ENTER_LONG: "开多", ENTER_SHORT: "开空", EXIT_LONG: "平多", EXIT_SHORT: "平空", ADD_LONG: "加多", ADD_SHORT: "加空", ROLL: "换月" })[value] || value || "待核验";
  }
  function tradeTime(item) {
    const value = item.timestamp || item.time || item.execution_date || item.signal_date || item.date;
    if (!value && item.backtest_summary && item.backtest_summary.sample_end) return `依据 ${item.backtest_summary.sample_end} 收盘`;
    if (!value) return "时间待核验";
    return /^\d{4}-\d{2}-\d{2}$/.test(String(value)) ? String(value) : formatTime(value);
  }
  function positionActionClass(action) {
    if (String(action).endsWith("LONG")) return "position-action-long";
    if (String(action).endsWith("SHORT")) return "position-action-short";
    return "position-action-neutral";
  }
  function todayTradesForPosition(position, trades) {
    return trades.filter((trade) => String(trade.variety || "").toUpperCase() === String(position.variety || "").toUpperCase()
      && String(trade.contract || "").toUpperCase() === String(position.contract || "").toUpperCase());
  }
  function todayActionMarkup(position, trades) {
    const matched = todayTradesForPosition(position, trades);
    if (!matched.length) return '<span class="position-action-none">今日无开平仓</span>';
    return matched.map((trade) => {
      const price = Number(trade.price);
      const detail = [Number.isFinite(price) ? `成交 ${number.format(price)}` : "成交价待核验", tradeTime(trade)].join(" · ");
      return `<span class="position-action-record"><strong class="${positionActionClass(trade.action)}">${escapeHtml(actionLabel(trade.action))} ${escapeHtml(trade.quantity || 0)} 手</strong><span>${escapeHtml(detail)}</span></span>`;
    }).join("");
  }
  function strategyName(item) {
    return item.strategy_name || (selected === "bollinger" ? "布林带 + RSI + MA6" : "AI策略待记录");
  }
  function friendlyStrategyText(value) {
    return String(value == null ? "" : value)
      .replace(/INPUT\.local_strategy_backtests\[([^\]]+)\]\./g, "本地Python回测（$1） · ")
      .replace(/INPUT\.local_strategy_backtests\./g, "本地Python回测 · ")
      .replace(/INPUT\.local_strategy_backtests/g, "本地Python回测")
      .replace(/channel20_breakout/g, "20日通道突破")
      .replace(/bollinger_reversion/g, "布林带均值回归")
      .replace(/rsi_reversion/g, "RSI均值回归")
      .replace(/macd_momentum/g, "MACD动量")
      .replace(/ma20_60_trend/g, "MA20\/MA60趋势")
      .replace(/trend_vs_ma60/g, "相对MA60趋势")
      .replace(/current_bias/g, "当前方向")
      .replace(/target_quantity/g, "目标手数")
      .replace(/\bENTER_LONG\b/g, "开多")
      .replace(/\bENTER_SHORT\b/g, "开空")
      .replace(/\bEXIT_LONG\b/g, "平多")
      .replace(/\bEXIT_SHORT\b/g, "平空")
      .replace(/\bLOCAL_BACKTEST\b/g, "本地回测")
      .replace(/\bLONG\b/g, "多头")
      .replace(/\bSHORT\b/g, "空头")
      .replace(/\bFLAT\b/g, "空仓");
  }
  function strategyMeta(item) {
    const summary = item.backtest_summary && typeof item.backtest_summary === "object" ? item.backtest_summary : null;
    const strategy = friendlyStrategyText(strategyName(item));
    const source = friendlyStrategyText(item.strategy_source || item.strategy_type).replace(`本地Python回测 · ${strategy}`, "本地Python回测");
    const parts = [source];
    if (summary && summary.total_return != null) parts.push(`回测收益 ${percent(summary.total_return)}`);
    if (summary && summary.sample_start && summary.sample_end) parts.push(`${summary.sample_start} 至 ${summary.sample_end}`);
    return parts.filter(Boolean).join(" · ") || "策略来源待核验";
  }
  function strategyRules(item) {
    const parts = [];
    if (item.strategy_rationale) parts.push(`选择依据：${friendlyStrategyText(item.strategy_rationale)}`);
    if (item.strategy_entry_rule) parts.push(`开仓：${friendlyStrategyText(item.strategy_entry_rule)}`);
    if (item.strategy_exit_rule) parts.push(`平仓：${friendlyStrategyText(item.strategy_exit_rule)}`);
    if (item.quantity_reason) parts.push(`手数：${friendlyStrategyText(item.quantity_reason)}`);
    return parts.join("；") || "策略规则待核验";
  }
  function marginMeta(item) {
    if (item.margin_rate == null) return "";
    const applied = item.margin_applied_side === "long" ? "多头" : (item.margin_applied_side === "short" ? "空头" : "较高侧");
    const parts = [`${applied}实际保证金 ${percent(item.margin_rate)}`];
    if (item.margin_source) parts.push(item.margin_source);
    if (item.margin_as_of) parts.push(`截至 ${item.margin_as_of}`);
    return parts.join(" · ");
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
  async function loadMonthlyBacktest() {
    if (monthlyBacktestCache && Date.now() - monthlyBacktestLoadedAt < 60 * 60 * 1000) return monthlyBacktestCache;
    const config = STRATEGIES.bollinger;
    let result;
    try { result = { payload: await fetchPayload(config.backtestApi), transport: "实时 API" }; }
    catch (error) { result = { payload: await fetchPayload(config.backtestFallback), transport: "静态备份" }; }
    monthlyBacktestCache = result;
    monthlyBacktestLoadedAt = Date.now();
    return result;
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
    el("monthly-backtest-panel").hidden = strategy !== "bollinger";
    config.disciplines.forEach((row, index) => {
      el(`discipline-${index + 1}-title`).textContent = row[0];
      el(`discipline-${index + 1}-copy`).textContent = row[1];
    });
  }

  function monthlyReturn(value) {
    if (value == null || value === "") return { className: "monthly-na", text: "—" };
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return { className: "monthly-na", text: "—" };
    if (parsed > 0) return { className: "is-positive", text: `+${(parsed * 100).toFixed(2)}%` };
    if (parsed < 0) return { className: "is-negative", text: `（${(parsed * 100).toFixed(2)}%）` };
    return { className: "monthly-zero", text: "0.00%" };
  }

  function renderMonthlyBacktest(data, transport) {
    const years = Array.isArray(data.years) ? data.years : [];
    const coverage = data.coverage || {};
    const model = data.model || {};
    const methodology = data.methodology || {};
    el("monthly-backtest-status").textContent = `${data.status_label || "状态待核验"} · ${transport}`;
    el("monthly-return-body").innerHTML = years.length ? years.map((row) => {
      const cells = Array.from({ length: 12 }, (_, index) => monthlyReturn((row.months || {})[String(index + 1)]));
      const period = monthlyReturn(row.period_return);
      const label = row.complete_year ? String(row.year) : `${row.year}*`;
      return `<tr><th scope="row">${escapeHtml(label)}</th>${cells.map((item) => `<td class="${item.className}">${escapeHtml(item.text)}</td>`).join("")}<td class="monthly-period ${period.className}">${escapeHtml(period.text)}</td></tr>`;
    }).join("") : '<tr><td colspan="14" class="monthly-loading">没有可展示的完整自然月回测数据。</td></tr>';
    el("monthly-backtest-range").textContent = `区间 ${data.window_start || "--"} 至 ${data.window_end || data.as_of || "--"}（* 为非完整年度）`;
    el("monthly-backtest-coverage").textContent = `品种覆盖 ${coverage.successful_count ?? "--"} / ${coverage.universe_count ?? "--"} · 月份 ${coverage.populated_months ?? "--"} / ${coverage.expected_months ?? "--"}`;
    el("monthly-backtest-model").textContent = `${model.name || "布林RSI模型"} · ${model.version || "版本待核验"} · 单边成本 ${model.single_side_cost == null ? "--" : percent(model.single_side_cost)}`;
    el("monthly-backtest-source").textContent = `${(data.source || {}).name || "来源待核验"} · 截至 ${data.as_of || "--"} · ${data.update_schedule || "每月更新"}`;
    const limits = Array.isArray(methodology.limitations) ? methodology.limitations.join("；") : "限制待核验";
    el("monthly-backtest-limit").textContent = `${methodology.not_live_replay || "不是实时基金动态仓位历史回放"}；${methodology.historical_margin || "历史保证金口径待核验"}；${limits}。`;
    el("monthly-backtest-ai-notice").textContent = `AI 风险提示：${data.ai_notice || "本表由 AI 基于所列行情和既定规则生成，不代表任何来源方官方立场，也不构成投资建议，请自行核验。"}`;
  }

  function renderMetrics(data) {
    const summary = data.summary || {};
    el("equity").textContent = money.format(Number(summary.equity || 0));
    el("net-value").textContent = `净值 ${Number(summary.net_value || 1).toFixed(4)}`;
    el("cumulative-return").textContent = percent(summary.cumulative_return); colorize(el("cumulative-return"), summary.cumulative_return);
    el("annualized-return").textContent = summary.annualized_return == null ? "年化：样本不足" : `年化 ${percent(summary.annualized_return)}`;
    el("daily-pnl").textContent = signedMoney(summary.daily_pnl); colorize(el("daily-pnl"), summary.daily_pnl);
    el("daily-pnl").title = "今日盈亏 = 当前权益 − 上一交易日权益";
    el("realized-pnl").textContent = `累计已实现（非今日） ${signedMoney(summary.realized_pnl)}`;
    el("realized-pnl").title = "累计已实现包含历次开平仓损益与费用，不是今日盈亏";
    colorize(el("realized-pnl"), summary.realized_pnl);
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
    const trades = Array.isArray(data.today_trades) ? data.today_trades : [];
    const positionKeys = new Set(positions.map((position) => `${String(position.variety || "").toUpperCase()}|${String(position.contract || "").toUpperCase()}`));
    const exited = trades.filter((trade) => String(trade.action || "").startsWith("EXIT")
      && !positionKeys.has(`${String(trade.variety || "").toUpperCase()}|${String(trade.contract || "").toUpperCase()}`));
    const exitedNames = [...new Set(exited.map((trade) => trade.name || trade.variety).filter(Boolean))];
    el("position-count").textContent = `${positions.length} 个品种`; el("positions-empty").hidden = positions.length > 0;
    el("position-trade-note").textContent = exited.length
      ? `当前持仓只显示未平仓合约；今日已平仓 ${exitedNames.length} 个品种（${exitedNames.join("、")}）已移至下方“今日动作”。表内“今日动作”列显示仍在持有的今日成交。`
      : (trades.length ? "表内“今日动作”列显示今日开仓或加仓；平仓完成后该品种会从当前持仓移除并保留在下方“今日动作”。" : "今日尚无已落账开平仓；当前持仓继续按最新价盯市。");
    el("positions-body").innerHTML = positions.map((position) => {
      const pnl = formatPositionPnl(position.unrealized_pnl || 0);
      return `<tr><td><strong>${escapeHtml(position.name || position.variety)}</strong><span>${escapeHtml(position.contract)}</span></td><td>${escapeHtml(position.entry_date || "--")}</td><td class="strategy-cell"><strong>${escapeHtml(strategyName(position))}</strong><span>${escapeHtml(strategyMeta(position))}</span><span>${escapeHtml(strategyRules(position))}</span></td><td class="reason-cell">${escapeHtml(friendlyStrategyText(position.model_reason || "开仓依据待核验"))}</td><td><em class="side-badge ${Number(position.side) === 1 ? "side-long" : "side-short"}">${Number(position.side) === 1 ? "多" : "空"}</em></td><td>${escapeHtml(position.quantity)} / ${escapeHtml(position.layers || 1)}</td><td>${number.format(position.average_price)}</td><td>${number.format(position.last_price)}</td><td title="${escapeHtml(position.margin_source || "保证金来源待核验")}"><strong>${money.format(position.notional || 0)}</strong><span>${escapeHtml(marginMeta(position) || "保证金待核验")} · ${money.format(position.used_margin || 0)}</span></td><td class="${pnl.className}">${escapeHtml(pnl.text)}</td><td>${percent(position.weight || 0)}</td><td><strong>${escapeHtml(position.price_source || "待核验")}</strong><span>${escapeHtml(formatTime(position.price_time))}</span></td><td class="today-action-cell">${todayActionMarkup(position, trades)}</td><td class="instruction-cell">${escapeHtml(friendlyStrategyText(position.next_instruction || "等待下一次完整日线确认"))}</td></tr>`;
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
      const actionDetail = detail && detail !== action ? `${action} · ${detail}` : action;
      const pnl = Number(item.pnl ?? item.realized_pnl ?? 0);
      const pnlClass = kind === "trade" ? (pnl > 0 ? "is-positive" : (pnl < 0 ? "is-negative" : "")) : "";
      const quantity = Number(item.requested_quantity ?? item.target_quantity ?? item.quantity ?? 0);
      const tail = kind === "trade" ? `已实现 ${signedMoney(pnl)}` : (kind === "skipped" ? "未执行" : (item.confidence != null ? `置信度 ${percent(item.confidence)}` : (quantity > 0 ? `计划 ${quantity} 手` : "等待")));
      const margin = marginMeta(item);
      return `<article class="activity-item"><div class="activity-item-meta"><span>${escapeHtml(tradeTime(item))}</span><b class="${pnlClass}">${escapeHtml(tail)}</b></div><div class="activity-item-copy"><strong>${escapeHtml(item.name || item.variety || "--")} · ${escapeHtml(item.contract || action)}</strong><small class="strategy-line">策略：${escapeHtml(strategyName(item))} · ${escapeHtml(strategyMeta(item))}</small><small>${escapeHtml(strategyRules(item))}</small>${margin ? `<small>保证金：${escapeHtml(margin)}</small>` : ""}<small>${escapeHtml(friendlyStrategyText(actionDetail || "--"))}</small></div></article>`;
    }).join("");
  }

  function renderTrades(items) {
    const trades = Array.isArray(items) ? items : [];
    el("trades-empty").hidden = trades.length > 0;
    el("trades-list").innerHTML = trades.map((item) => {
      const action = actionLabel(item.action);
      const isExit = item.action === "EXIT_LONG" || item.action === "EXIT_SHORT";
      const actionClass = String(item.action || "").endsWith("_LONG") ? "trade-action-long" : (String(item.action || "").endsWith("_SHORT") ? "trade-action-short" : "trade-action-neutral");
      const pnl = formatTradePnl(item.pnl ?? item.realized_pnl);
      const price = Number(item.price ?? item.fill_price);
      const priceText = Number.isFinite(price) ? number.format(price) : "--";
      const pnlCell = isExit ? `<div class="trade-stat trade-pnl"><span>平仓收益（含费）</span><strong class="${pnl.className}">${escapeHtml(pnl.text)}</strong></div>` : "";
      return `<article class="trade-card ${isExit ? "is-exit" : "is-entry"}"><header><div><span class="trade-variety">${escapeHtml(item.name || item.variety || "--")}</span><strong>${escapeHtml(item.contract || "合约待核验")}</strong></div><em class="trade-action-badge ${actionClass}">${escapeHtml(action)}</em></header><div class="trade-card-stats"><div class="trade-stat"><span>开平仓方向</span><strong>${escapeHtml(action)}</strong></div><div class="trade-stat"><span>成交手数</span><strong>${escapeHtml(item.quantity ?? "--")} 手</strong></div><div class="trade-stat"><span>成交价格</span><strong>${escapeHtml(priceText)}</strong></div>${pnlCell}</div><details class="trade-card-strategy"><summary>使用策略：${escapeHtml(strategyName(item))}</summary><span>${escapeHtml(strategyMeta(item))}</span><p>${escapeHtml(strategyRules(item))}</p></details><footer><span>虚拟成交</span><time datetime="${escapeHtml(item.timestamp || item.date || "")}">${escapeHtml(tradeTime(item))}</time></footer></article>`;
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
    el("trade-count").textContent = `${trades.length} 条`; el("pending-count").textContent = `${instructions.length} 条`; renderTrades(trades); renderActivity("pending-list", "pending-empty", instructions, "instruction");
    const skipped = Array.isArray(data.skipped_signals) ? data.skipped_signals : []; el("skipped-count").textContent = `${skipped.length} 条`; renderActivity("skipped-list", "skipped-empty", skipped, "skipped"); renderSources(data);
  }

  async function boot() {
    const token = ++requestToken; applyStrategyCopy(selected); el("data-state").textContent = `正在载入${STRATEGIES[selected].label}`;
    try {
      const result = await load(selected);
      if (token === requestToken) render(result.payload, result.transport);
      if (selected === "bollinger") {
        const backtest = await loadMonthlyBacktest();
        if (token === requestToken) renderMonthlyBacktest(backtest.payload, backtest.transport);
      }
    }
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

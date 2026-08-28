(function () {
  "use strict";

  const API = "/api/ai-daredevil";
  const FALLBACK = "data/ai_daredevil.json";
  const money = new Intl.NumberFormat("zh-CN", { style: "currency", currency: "CNY", maximumFractionDigits: 2 });
  const number = new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 });

  function el(id) { return document.getElementById(id); }
  function percent(value) { return Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(2)}%` : "--"; }
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

  async function load() {
    try {
      const response = await fetch(`${API}?_=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return { payload: await response.json(), transport: "实时 API" };
    } catch (error) {
      const response = await fetch(`${FALLBACK}?_=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) throw error;
      return { payload: await response.json(), transport: "静态备份" };
    }
  }

  function renderMetrics(data) {
    const summary = data.summary || {};
    const equity = Number(summary.equity || 0);
    el("equity").textContent = money.format(equity);
    el("net-value").textContent = `净值 ${Number(summary.net_value || 1).toFixed(4)}`;
    el("cumulative-return").textContent = percent(summary.cumulative_return);
    colorize(el("cumulative-return"), summary.cumulative_return);
    el("annualized-return").textContent = summary.annualized_return == null ? "年化：样本不足" : `年化 ${percent(summary.annualized_return)}`;
    el("daily-pnl").textContent = money.format(Number(summary.daily_pnl || 0));
    colorize(el("daily-pnl"), summary.daily_pnl);
    el("realized-pnl").textContent = `已实现 ${money.format(Number(summary.realized_pnl || 0))}`;
    el("max-drawdown").textContent = percent(summary.max_drawdown || 0);
    colorize(el("max-drawdown"), summary.max_drawdown);
    el("sharpe").textContent = summary.sharpe == null ? "夏普：样本不足" : `夏普 ${Number(summary.sharpe).toFixed(2)}`;
    el("margin-use").textContent = percent(summary.margin_usage || 0);
    el("used-margin").textContent = money.format(Number(summary.used_margin || 0));
    el("available-cash").textContent = money.format(Number(summary.available_cash || 0));
    el("gross-exposure").textContent = `总敞口 ${percent(summary.gross_exposure_multiple || 0)}权益`;
  }

  function renderChart(points) {
    const svg = el("equity-chart");
    const empty = el("chart-empty");
    svg.replaceChildren(svg.querySelector("title"), svg.querySelector("desc"));
    if (!Array.isArray(points) || points.length < 2) { empty.hidden = false; return; }
    empty.hidden = true;
    const values = points.map((point) => Number(point.net_value)).filter(Number.isFinite);
    const min = Math.min(...values, 0.995);
    const max = Math.max(...values, 1.005);
    const pad = { left: 54, right: 22, top: 20, bottom: 34 };
    const width = 920 - pad.left - pad.right;
    const height = 320 - pad.top - pad.bottom;
    const x = (index) => pad.left + width * index / Math.max(1, points.length - 1);
    const y = (value) => pad.top + height * (max - value) / Math.max(.0001, max - min);
    for (let index = 0; index <= 4; index += 1) {
      const value = min + (max - min) * index / 4;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", pad.left); line.setAttribute("x2", 920 - pad.right);
      line.setAttribute("y1", y(value)); line.setAttribute("y2", y(value));
      line.setAttribute("stroke", "rgba(177,211,193,.12)");
      svg.appendChild(line);
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", 4); label.setAttribute("y", y(value) + 4);
      label.setAttribute("fill", "#91a99d"); label.setAttribute("font-size", "11");
      label.textContent = value.toFixed(3); svg.appendChild(label);
    }
    const path = points.map((point, index) => `${index ? "L" : "M"}${x(index)},${y(Number(point.net_value))}`).join(" ");
    const area = document.createElementNS("http://www.w3.org/2000/svg", "path");
    area.setAttribute("d", `${path} L${x(points.length - 1)},${pad.top + height} L${x(0)},${pad.top + height} Z`);
    area.setAttribute("fill", "rgba(94,224,163,.08)"); svg.appendChild(area);
    const curve = document.createElementNS("http://www.w3.org/2000/svg", "path");
    curve.setAttribute("d", path); curve.setAttribute("fill", "none"); curve.setAttribute("stroke", "#5ee0a3"); curve.setAttribute("stroke-width", "3"); curve.setAttribute("vector-effect", "non-scaling-stroke"); svg.appendChild(curve);
    [0, points.length - 1].forEach((index) => {
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", x(index)); label.setAttribute("y", 312); label.setAttribute("text-anchor", index ? "end" : "start");
      label.setAttribute("fill", "#91a99d"); label.setAttribute("font-size", "11"); label.textContent = points[index].date; svg.appendChild(label);
    });
  }

  function renderPositions(data) {
    const positions = Array.isArray(data.positions) ? data.positions : [];
    el("position-count").textContent = `${positions.length} 个品种`;
    el("positions-empty").hidden = positions.length > 0;
    el("positions-body").innerHTML = positions.map((position) => {
      const pnl = Number(position.unrealized_pnl || 0);
      return `<tr>
        <td><strong>${position.name || position.variety}</strong><span>${position.contract}</span></td>
        <td><em class="side-badge ${Number(position.side) === 1 ? "side-long" : "side-short"}">${Number(position.side) === 1 ? "多" : "空"}</em></td>
        <td>${position.quantity} / ${position.layers || 1}</td><td>${number.format(position.average_price)}</td><td>${number.format(position.last_price)}</td>
        <td>${money.format(position.notional || 0)}</td><td class="${pnl >= 0 ? "is-positive" : "is-negative"}">${money.format(pnl)}</td>
        <td>${percent(position.weight || 0)}</td><td><strong>${position.price_source || "待核验"}</strong><span>${formatTime(position.price_time)}</span></td>
      </tr>`;
    }).join("");
  }

  function renderActivity(containerId, emptyId, items, kind) {
    const list = Array.isArray(items) ? items : [];
    el(emptyId).hidden = list.length > 0;
    el(containerId).innerHTML = list.map((item) => `<article class="activity-item">
      <span>${item.time || item.execution_date || "--"}</span>
      <div><strong>${item.name || item.variety || "--"} · ${item.contract || "--"}</strong><small>${item.reason || item.action || "--"}</small></div>
      <b class="${Number(item.pnl ?? item.realized_pnl ?? 0) >= 0 ? "is-positive" : "is-negative"}">${kind === "trade" ? money.format(Number(item.pnl ?? item.realized_pnl ?? 0)) : `${item.quantity || 0} 手`}</b>
    </article>`).join("");
  }

  function renderSources(data) {
    const schedule = data.refresh_schedule || [];
    el("refresh-timeline").innerHTML = schedule.map((item) => `<div class="refresh-slot"><span>${item.label}</span><strong>${item.time}</strong><small>${item.purpose}</small></div>`).join("");
    const sources = data.sources || [];
    el("source-grid").innerHTML = sources.map((source) => `<article class="source-item ${source.state || "failed"}"><span>${source.priority || "--"}</span><strong>${source.name}</strong><small>${source.note || source.state_label || "--"}</small></article>`).join("");
    el("next-refresh").textContent = data.next_refresh ? `下次 ${formatTime(data.next_refresh)}` : "等待调度";
  }

  function render(data, transport) {
    el("updated-at").textContent = formatTime(data.generated_at);
    el("refresh-session").textContent = `${data.refresh_reason || "定时刷新"} · ${data.market_date || "交易日待核验"}`;
    el("primary-source").textContent = data.price_source || "--";
    el("source-state").textContent = transport;
    el("data-state").textContent = data.status_label || "状态待核验";
    el("data-state").className = `data-state is-${data.status || "degraded"}`;
    renderMetrics(data); renderChart(data.equity_curve); renderPositions(data);
    const trades = data.today_trades || []; const pending = data.pending_orders || [];
    el("trade-count").textContent = `${trades.length} 条`; el("pending-count").textContent = `${pending.length} 条`;
    renderActivity("trades-list", "trades-empty", trades, "trade");
    renderActivity("pending-list", "pending-empty", pending, "pending");
    const skipped = data.skipped_signals || [];
    el("skipped-count").textContent = `${skipped.length} 条`;
    renderActivity("skipped-list", "skipped-empty", skipped, "pending");
    renderSources(data);
  }

  async function boot() {
    try { const result = await load(); render(result.payload, result.transport); }
    catch (error) { el("data-state").textContent = "基金数据不可用"; el("data-state").className = "data-state is-degraded"; }
  }
  boot();
  window.setInterval(boot, 60 * 1000);
}());

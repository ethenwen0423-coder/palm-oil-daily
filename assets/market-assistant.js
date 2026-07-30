(() => {
  "use strict";

  const POLL_INTERVAL_MS = 60000;
  const DATASETS = {
    reports: ["/api/reports", "data/reports.json"],
    oil: ["/api/oil-futures", "data/oil_futures.json"],
    exchange: ["/api/exchange-futures", "data/exchange_futures.json"],
    supply: ["/api/supply-demand", "data/supply-demand.json"],
    forecast: ["/api/forecast/metrics/latest", "data/forecast/metrics/latest.json"],
  };
  const STATUS_LABELS = {
    ready: "正常",
    stale: "延迟",
    missing: "缺失",
    invalid: "异常",
  };
  const SESSION_LABELS = {
    morning: "早盘",
    midday: "午盘",
    close: "收盘",
    manual: "手动",
  };

  const element = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  async function fetchJson(url) {
    const response = await fetch(url, {
      cache: "no-store",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error(`${url} HTTP ${response.status}`);
    return response.json();
  }

  async function fetchWithFallback([api, fallback]) {
    try {
      return { payload: await fetchJson(api), source: "api" };
    } catch (apiError) {
      return {
        payload: await fetchJson(fallback),
        source: "static",
        error: String(apiError.message || apiError),
      };
    }
  }

  function formatDateTime(value) {
    if (!value) return "需进一步核验";
    const normalized = String(value).includes("T")
      ? String(value)
      : `${String(value).replace(" ", "T")}:00+08:00`;
    const parsed = new Date(normalized);
    if (!Number.isFinite(parsed.getTime())) return String(value);
    return parsed.toLocaleString("zh-CN", {
      timeZone: "Asia/Shanghai",
      hour12: false,
    });
  }

  function formatAge(seconds) {
    if (!Number.isFinite(Number(seconds))) return "观测时间需进一步核验";
    const minutes = Math.floor(Number(seconds) / 60);
    if (minutes < 60) return `${Math.max(minutes, 0)} 分钟前`;
    const hours = Math.floor(minutes / 60);
    if (hours < 48) return `${hours} 小时前`;
    return `${Math.floor(hours / 24)} 天前`;
  }

  function number(value) {
    const parsed = Number(String(value ?? "").replaceAll(",", "").replace("%", ""));
    return Number.isFinite(parsed) ? parsed : null;
  }

  function changeClass(value) {
    const parsed = number(value);
    return parsed > 0 ? "is-up" : parsed < 0 ? "is-down" : "is-flat";
  }

  function formatChange(value) {
    const parsed = number(value);
    if (parsed === null) return "需核验";
    return `${parsed > 0 ? "+" : ""}${parsed.toFixed(2)}%`;
  }

  function syntheticStatus(results) {
    const labels = {
      reports: "研究报告",
      oil: "油脂行情",
      exchange: "全品种行情",
      supply: "供需资料",
      forecast: "预测评估",
    };
    const datasets = {};
    Object.entries(results).forEach(([key, result]) => {
      datasets[`local:${key}`] = {
        label: labels[key],
        state: result ? "ready" : "missing",
        observed_at: null,
        age_seconds: null,
        source: result?.source || "missing",
      };
    });
    return {
      status: Object.values(datasets).every((item) => item.state === "ready") ? "ok" : "degraded",
      datasets,
    };
  }

  function renderHealth(status, results) {
    const datasets = status?.datasets || {};
    const cards = Object.values(datasets).map((item) => {
      const state = item.state || "missing";
      return `
        <article class="health-card is-${escapeHtml(state)}">
          <header>
            <strong>${escapeHtml(item.label || item.route || "数据集")}</strong>
            <span>${escapeHtml(STATUS_LABELS[state] || state)}</span>
          </header>
          <p>${escapeHtml(item.observed_at ? `${formatAge(item.age_seconds)} · ${formatDateTime(item.observed_at)}` : "观测时间需进一步核验")}</p>
        </article>
      `;
    });
    element("monitor-data-health").innerHTML = cards.join("");

    const fallbackUsed = Object.values(results).some((item) => item?.source === "static");
    const degraded = status?.status !== "ok" || fallbackUsed;
    const badge = element("monitor-overall-state");
    badge.className = `monitor-state ${degraded ? "is-degraded" : "is-ready"}`;
    badge.textContent = degraded ? "部分数据延迟或回退" : "数据链运行正常";
  }

  function renderReport(result) {
    const reports = Array.isArray(result?.payload) ? result.payload : [];
    const latest = reports[0] || {};
    element("monitor-report-date").textContent = latest.date
      ? `${latest.date} · ${latest.kind === "weekend" ? "周报" : "日报"}`
      : "等待报告";
    element("monitor-report-headline").textContent = latest.headline || latest.title || "暂无最新研究结论";
    element("monitor-report-summary").textContent = latest.summary || "报告摘要需进一步核验。";
    element("monitor-report-link").href = latest.date
      ? `report.html?id=${encodeURIComponent(latest.date)}`
      : "reports.html";
  }

  function renderOil(result) {
    const payload = result?.payload || {};
    const contracts = Array.isArray(payload.contracts) ? payload.contracts : [];
    const main = contracts
      .filter((item) => item.contract_rank === 1 || ["FCPO", "CPOTR"].includes(String(item.symbol || "").toUpperCase()))
      .slice(0, 8);
    element("monitor-oil-updated").textContent = payload.updated_at
      ? `${formatDateTime(payload.updated_at)} · ${SESSION_LABELS[payload.update_session] || "行情"}`
      : "行情更新时间需进一步核验";
    element("monitor-oil-list").innerHTML = main.length
      ? main.map((item) => `
          <div class="quote-row">
            <div><strong>${escapeHtml(item.name || item.product || item.symbol)}</strong><small>${escapeHtml(item.contract || item.symbol || "")}</small></div>
            <b>${escapeHtml(item.price || "--")}</b>
            <span class="${changeClass(item.change)}">${escapeHtml(item.change || "--")}</span>
          </div>
        `).join("")
      : '<p class="monitor-meta">暂无可用油脂合约，需进一步核验。</p>';
  }

  function renderMovers(result) {
    const payload = result?.payload || {};
    const contracts = (Array.isArray(payload.contracts) ? payload.contracts : [])
      .filter((item) => number(item.change_pct) !== null);
    const gainers = [...contracts].sort((a, b) => number(b.change_pct) - number(a.change_pct)).slice(0, 5);
    const losers = [...contracts].sort((a, b) => number(a.change_pct) - number(b.change_pct)).slice(0, 5);
    element("monitor-exchange-updated").textContent = payload.updated_at
      ? `${formatDateTime(payload.updated_at)} · ${SESSION_LABELS[payload.update_session] || "行情"}`
      : "行情更新时间需进一步核验";
    const render = (items) => items.map((item) => `
      <div class="mover-row">
        <span>${escapeHtml(item.product || item.symbol)}</span>
        <b class="${changeClass(item.change_pct)}">${formatChange(item.change_pct)}</b>
      </div>
    `).join("");
    element("monitor-gainers").innerHTML = render(gainers);
    element("monitor-losers").innerHTML = render(losers);
  }

  function renderSupply(result) {
    const payload = result?.payload || {};
    element("monitor-supply-message").textContent = payload.update_message || "官方资料检查状态需进一步核验。";
    element("monitor-supply-checked").textContent = formatDateTime(payload.checked_at || payload.generated_at);
    element("monitor-supply-updated").textContent = formatDateTime(payload.data_updated_at);
  }

  function renderForecast(result) {
    const payload = result?.payload || {};
    element("monitor-forecast-date").textContent = payload.as_of || "需进一步核验";
    if (payload.public_display_allowed) {
      element("monitor-forecast-status").textContent = "评估样本达到公开展示门槛，可查看模型证据。";
      element("monitor-forecast-public").textContent = "可公开";
    } else {
      element("monitor-forecast-status").textContent = "当前评估样本不足，不将历史命中率包装成可靠预测能力。";
      element("monitor-forecast-public").textContent = "样本不足";
    }
  }

  function renderTasks(status, results) {
    const tasks = [];
    const degraded = Object.values(status?.datasets || {})
      .filter((item) => item.state !== "ready")
      .map((item) => item.label || item.route);
    if (degraded.length) tasks.push(`优先补采或核验：${degraded.slice(0, 4).join("、")}`);

    const exchange = results.exchange?.payload?.contracts || [];
    const movers = exchange
      .filter((item) => number(item.change_pct) !== null)
      .sort((a, b) => Math.abs(number(b.change_pct)) - Math.abs(number(a.change_pct)))
      .slice(0, 3)
      .map((item) => `${item.product || item.symbol} ${formatChange(item.change_pct)}`);
    if (movers.length) tasks.push(`关注全品种绝对波动：${movers.join("；")}`);

    const report = Array.isArray(results.reports?.payload) ? results.reports.payload[0] : null;
    if (report?.summary) tasks.push(`沿用最新报告触发器：${report.summary}`);
    if (!tasks.length) tasks.push("数据链无明显异常，继续等待下一次行情或官方资料更新。");
    element("monitor-task-list").innerHTML = tasks.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }

  let lastFingerprint = "";
  let loading = false;

  async function refresh() {
    if (loading) return;
    loading = true;
    try {
      const entries = await Promise.all(
        Object.entries(DATASETS).map(async ([key, config]) => {
          try {
            return [key, await fetchWithFallback(config)];
          } catch (_error) {
            return [key, null];
          }
        }),
      );
      const results = Object.fromEntries(entries);
      let status;
      try {
        status = await fetchJson("/api/status");
      } catch (_error) {
        status = syntheticStatus(results);
      }

      const nextFingerprint = JSON.stringify({ status, results });
      if (nextFingerprint === lastFingerprint) return;
      lastFingerprint = nextFingerprint;
      renderHealth(status, results);
      renderReport(results.reports);
      renderOil(results.oil);
      renderMovers(results.exchange);
      renderSupply(results.supply);
      renderForecast(results.forecast);
      renderTasks(status, results);
      element("monitor-refresh-note").textContent = `最近检查：${new Date().toLocaleTimeString("zh-CN", { hour12: false })} · 每 60 秒自动检查`;
    } catch (error) {
      const badge = element("monitor-overall-state");
      badge.className = "monitor-state is-error";
      badge.textContent = "数据链读取失败";
      element("monitor-refresh-note").textContent = String(error.message || error);
    } finally {
      loading = false;
    }
  }

  function updateClock() {
    element("monitor-clock").textContent = new Date().toLocaleTimeString("zh-CN", {
      timeZone: "Asia/Shanghai",
      hour12: false,
    });
  }

  updateClock();
  window.setInterval(updateClock, 1000);
  refresh();
  window.setInterval(() => {
    if (document.visibilityState !== "hidden") refresh();
  }, POLL_INTERVAL_MS);
})();

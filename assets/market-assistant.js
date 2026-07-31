(() => {
  "use strict";

  const POLL_INTERVAL_MS = 60000;
  const DATASETS = {
    reports: ["/api/reports", "data/reports.json"],
    oil: ["/api/oil-futures", "data/oil_futures.json"],
    exchange: ["/api/exchange-futures", "data/exchange_futures.json"],
    quant: ["/api/quant-model-signals", "data/quant_model_signals.json"],
    contracts: ["/api/contracts/current", "data/contracts/current_contracts.json"],
    supply: ["/api/supply-demand", "data/supply-demand.json"],
    forecast: ["/api/forecast/metrics/latest", "data/forecast/metrics/latest.json"],
    brief: ["/api/assistant/brief", "data/market_assistant_brief.json"],
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
    night_open: "夜盘开盘",
    night_close: "夜盘收盘",
    overnight: "凌晨尾盘",
    manual: "手动",
  };
  const OWNER_LABELS = {
    "server-market-collector": "服务器行情任务",
    "server-supply-collector": "服务器官方资料任务",
    "server-ai-brief": "服务器 AI 任务",
    "upstream-sync": "自动发布同步",
    "server-api": "服务器 API",
    "static-fallback": "静态回退",
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
      quant: "动态量化信号",
      contracts: "主力合约",
      supply: "供需资料",
      forecast: "预测评估",
      brief: "AI 盯盘简报",
    };
    const datasets = {};
    Object.entries(results).forEach(([key, result]) => {
      datasets[`local:${key}`] = {
        label: labels[key],
        state: result ? "ready" : "missing",
        observed_at: null,
        age_seconds: null,
        source: result?.source || "missing",
        owner: result?.source === "api" ? "server-api" : "static-fallback",
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
          <p>${escapeHtml([
            OWNER_LABELS[item.owner] || item.owner || "来源需进一步核验",
            item.observed_at ? `${formatAge(item.age_seconds)} · ${formatDateTime(item.observed_at)}` : "观测时间需进一步核验",
          ].join(" · "))}</p>
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

  function renderQuant(result) {
    const payload = result?.payload || {};
    const modelId = payload.default_model_id || "";
    const grouped = payload.model_contracts || {};
    const contracts = Array.isArray(grouped[modelId]) ? grouped[modelId] : [];
    const signals = contracts.filter((item) => item?.rank === 1).slice(0, 5);
    element("monitor-quant-updated").textContent = payload.market_updated_at
      ? `${formatDateTime(payload.market_updated_at)} · ${SESSION_LABELS[payload.market_update_session] || "模型输出"}`
      : "动态信号更新时间需进一步核验";
    element("monitor-quant-list").innerHTML = signals.length
      ? signals.map((item) => {
          const flat = item?.signals?.flat || {};
          return `
            <div class="quote-row">
              <div>
                <strong>${escapeHtml(item.product_name || item.product || item.symbol)}</strong>
                <small>${escapeHtml(item.symbol || "")} · ${escapeHtml(item.model_scope_label || "规则试算")}</small>
              </div>
              <b>${escapeHtml(flat.action || "需核验")}</b>
              <span>${escapeHtml(flat.execution || "none")}</span>
            </div>
          `;
        }).join("")
      : '<p class="monitor-meta">暂无可验证的动态量化输出；模型规则本身仍保持固定。</p>';
  }

  function renderContracts(result) {
    const payload = result?.payload || {};
    const products = payload.products && typeof payload.products === "object"
      ? payload.products
      : {};
    const entries = Object.entries(products).slice(0, 8);
    element("monitor-contracts-updated").textContent = payload.generated_at
      ? `${formatDateTime(payload.generated_at)} · ${escapeHtml(payload.source || "来源需核验")}`
      : "合约识别时间需进一步核验";
    element("monitor-contracts-list").innerHTML = entries.length
      ? entries.map(([product, items]) => {
          const ranked = Array.isArray(items)
            ? items.filter((item) => item?.rank === 1 || item?.rank === 2).slice(0, 2)
            : [];
          const symbols = ranked.map((item) => `${item.label || `第${item.rank}位`} ${item.symbol || "--"}`);
          return `
            <div class="mover-row">
              <span>${escapeHtml(ranked[0]?.product_name || product)}</span>
              <b>${escapeHtml(symbols.join(" · ") || "需核验")}</b>
            </div>
          `;
        }).join("")
      : '<p class="monitor-meta">暂无主力与次主力合约识别结果。</p>';
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

  function renderFallbackTasks(status, results) {
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
    element("monitor-ai-status").textContent = "AI 简报暂不可用，当前展示规则化回退队列";
  }

  function renderBrief(result, status, results) {
    const payload = result?.payload;
    if (!payload || payload.status !== "ready") {
      element("monitor-ai-headline").textContent = "AI 简报暂不可用";
      element("monitor-ai-summary").textContent = "继续展示最近有效数据，并等待下一次自动生成。";
      element("monitor-ai-generated").textContent = "生成时间需进一步核验";
      element("monitor-ai-state").textContent = "数据不足";
      element("monitor-ai-confidence").textContent = "低";
      element("monitor-key-moves").innerHTML = "";
      element("monitor-watch-list").innerHTML = "";
      element("monitor-risk-list").innerHTML = "<li>AI 结果缺失，不将规则回退包装成模型结论。</li>";
      renderFallbackTasks(status, results);
      return;
    }

    element("monitor-ai-headline").textContent = payload.headline || "AI 盯盘简报";
    element("monitor-ai-summary").textContent = payload.summary || "摘要需进一步核验。";
    element("monitor-ai-generated").textContent = payload.generated_at
      ? `${formatDateTime(payload.generated_at)} · ${SESSION_LABELS[payload.update_session] || "自动"}`
      : "生成时间需进一步核验";
    element("monitor-ai-state").textContent = payload.market_state || "需核验";
    element("monitor-ai-confidence").textContent = payload.confidence || "需核验";
    element("monitor-ai-status").textContent = "只读证据约束生成 · 数值由数据源回填";

    const keyMoves = Array.isArray(payload.key_moves) ? payload.key_moves : [];
    element("monitor-key-moves").innerHTML = keyMoves.map((item) => `
      <li>
        <strong>${escapeHtml(item.label || item.evidence_id)}</strong>
        <b>${escapeHtml(item.value || "需核验")}</b>
        <span>${escapeHtml(item.interpretation || "")}</span>
        <small>${escapeHtml(item.source || "")} · ${escapeHtml(formatDateTime(item.observed_at))}</small>
      </li>
    `).join("");

    const watchlist = Array.isArray(payload.watchlist) ? payload.watchlist : [];
    element("monitor-watch-list").innerHTML = watchlist.map((item) => `
      <li>
        <strong>${escapeHtml(item.priority || "中")} · ${escapeHtml(item.item || "")}</strong>
        <span>${escapeHtml(item.trigger || "")}：${escapeHtml(item.why || "")}</span>
      </li>
    `).join("");

    const actions = Array.isArray(payload.actions) ? payload.actions : [];
    element("monitor-task-list").innerHTML = actions.map((item) => `
      <li>
        <strong>${escapeHtml(item.task || "")}</strong>
        <span>${escapeHtml(item.result || "")}</span>
        <small>${escapeHtml(item.status || "")} · ${escapeHtml(item.next_check || "")}</small>
      </li>
    `).join("");

    const risks = Array.isArray(payload.risks) ? payload.risks : [];
    element("monitor-risk-list").innerHTML = risks.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
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
      renderQuant(results.quant);
      renderContracts(results.contracts);
      renderSupply(results.supply);
      renderForecast(results.forecast);
      renderBrief(results.brief, status, results);
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

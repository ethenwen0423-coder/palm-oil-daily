(() => {
  "use strict";

  const DATA_URL = "data/supply-demand.json";
  const METRIC_ORDER = ["production", "exports", "stocks"];
  const STATUS_LABELS = {
    ok: "数据正常",
    partial: "部分缺失",
    stale: "更新滞后",
    source_unreachable: "来源暂不可达",
    parse_error: "来源解析异常",
  };
  const UPDATE_STATUS_LABELS = {
    updated: "发现新数据",
    no_change: "官网暂未更新",
    source_error: "来源检查异常",
  };

  const root = document.getElementById("supply-demand-root");
  const generated = document.getElementById("supply-demand-generated");
  const charts = [];

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function monthShift(period, delta) {
    const [year, month] = period.split("-").map(Number);
    const shifted = new Date(Date.UTC(year, month - 1 + delta, 1));
    return `${shifted.getUTCFullYear()}-${String(shifted.getUTCMonth() + 1).padStart(2, "0")}`;
  }

  function monthRange(end, count) {
    return Array.from({ length: count }, (_, index) => monthShift(end, index - count + 1));
  }

  function latestPoint(series) {
    return series.length ? series[series.length - 1] : null;
  }

  function displayValue(value) {
    if (!Number.isFinite(value)) return "需进一步核验";
    return (value / 10000).toLocaleString("zh-CN", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    });
  }

  function comparison(series, latest, delta) {
    if (!latest) return { text: "需进一步核验", className: "is-missing" };
    const priorPeriod = monthShift(latest.period, delta);
    const prior = series.find((item) => item.period === priorPeriod);
    if (!prior || !Number.isFinite(prior.value) || prior.value === 0) {
      return { text: "需进一步核验", className: "is-missing" };
    }
    const change = ((latest.value / prior.value) - 1) * 100;
    const sign = change > 0 ? "+" : "";
    return {
      text: `${sign}${change.toFixed(1)}%`,
      className: change > 0 ? "is-up" : change < 0 ? "is-down" : "is-flat",
    };
  }

  function formatPublished(value) {
    if (!value) return "需进一步核验";
    return value.replaceAll("-", ".");
  }

  function ratio(numerator, denominator) {
    if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator === 0) {
      return "需进一步核验";
    }
    return `${((numerator / denominator) * 100).toFixed(1)}%`;
  }

  function annualChange(series, field) {
    if (!Array.isArray(series) || series.length < 2) return "需进一步核验";
    const latest = series.at(-1);
    const previous = series.at(-2);
    const latestYear = Number(String(latest.market_year).slice(0, 4));
    const previousYear = Number(String(previous.market_year).slice(0, 4));
    if (latestYear - previousYear !== 1 || !previous[field]) return "需进一步核验";
    const change = ((latest[field] / previous[field]) - 1) * 100;
    return `${change > 0 ? "+" : ""}${change.toFixed(1)}%`;
  }

  function metricCard(countryKey, metricKey, metric, rangeEnd, displayMonths) {
    const series = Array.isArray(metric.series) ? metric.series : [];
    const latest = latestPoint(series);
    const mom = comparison(series, latest, -1);
    const yoy = comparison(series, latest, -12);
    const sourceUrl = latest?.source_url || "#";
    const chartId = `chart-${countryKey}-${metricKey}`;

    return `
      <article class="supply-metric-card">
        <header class="supply-metric-heading">
          <div>
            <span>${escapeHtml(metric.label)}</span>
            <strong>${latest ? displayValue(latest.value) : "需进一步核验"}${latest ? "<small>万吨</small>" : ""}</strong>
          </div>
          <time datetime="${escapeHtml(latest?.period || "")}">${escapeHtml(latest?.period || "暂无统计期")}</time>
        </header>
        <div class="supply-comparisons" aria-label="环比与同比">
          <span>环比 <b class="${mom.className}">${mom.text}</b></span>
          <span>同比 <b class="${yoy.className}">${yoy.text}</b></span>
        </div>
        <div class="supply-chart-wrap">
          <canvas id="${chartId}" width="640" height="260" aria-label="${escapeHtml(metric.label)}最近24个月趋势图"></canvas>
        </div>
        <dl class="supply-metric-meta">
          <div><dt>统计期</dt><dd>${escapeHtml(latest?.period || "需进一步核验")}</dd></div>
          <div><dt>单位</dt><dd>万吨</dd></div>
          <div><dt>发布日期</dt><dd>${escapeHtml(formatPublished(latest?.published_at))}</dd></div>
          <div><dt>来源</dt><dd><a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">查看官方原文 ↗</a></dd></div>
        </dl>
        <p class="supply-definition">${escapeHtml(metric.definition)}</p>
      </article>
    `;
  }

  function countrySection(key, country, displayMonths) {
    const metrics = country.metrics || {};
    const ends = METRIC_ORDER
      .flatMap((metricKey) => (metrics[metricKey]?.series || []).map((item) => item.period))
      .sort();
    const rangeEnd = ends.at(-1) || country.latest_period;
    const cards = METRIC_ORDER
      .map((metricKey) => metricCard(key, metricKey, metrics[metricKey] || {}, rangeEnd, displayMonths))
      .join("");
    const status = country.status || "parse_error";

    return `
      <section class="supply-country" aria-labelledby="country-${escapeHtml(key)}">
        <header class="supply-country-heading">
          <div>
            <p>${key === "malaysia" ? "Malaysia · MPOB" : "Indonesia · GAPKI"}</p>
            <h2 id="country-${escapeHtml(key)}">${escapeHtml(country.name)}</h2>
          </div>
          <div class="supply-country-status">
            <span class="supply-status supply-status-${escapeHtml(status)}">${escapeHtml(STATUS_LABELS[status] || status)}</span>
            <small>${escapeHtml(country.status_message)}</small>
          </div>
        </header>
        <div class="supply-metric-grid">${cards}</div>
      </section>
    `;
  }

  function renderGlobalBalance(section) {
    const rows = [...(section.series || [])]
      .slice(-10)
      .reverse()
      .map((item) => `
        <tr>
          <th scope="row">${escapeHtml(item.market_year)}</th>
          <td>${displayValue(item.production)}</td>
          <td>${displayValue(item.domestic_consumption)}</td>
          <td>${displayValue(item.ending_stocks)}</td>
          <td>${ratio(item.ending_stocks, item.domestic_consumption)}</td>
        </tr>
      `)
      .join("");
    return `
      <article class="supply-table-card supply-table-card-wide">
        <header>
          <div><span>Global Balance</span><h3>${escapeHtml(section.title)}</h3></div>
          <small>${escapeHtml(section.definition)}</small>
        </header>
        <div class="supply-table-scroll">
          <table class="supply-data-table">
            <thead><tr><th>市场年度</th><th>产量</th><th>消费量</th><th>期末库存</th><th>库存消费比</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </article>
    `;
  }

  function renderImportDemand(section) {
    const rows = (section.markets || [])
      .map((market) => {
        const latest = market.series?.at(-1);
        if (!latest) return "";
        return `
          <tr>
            <th scope="row">${escapeHtml(market.name)}</th>
            <td>${escapeHtml(latest.market_year)}</td>
            <td>${displayValue(latest.imports)}</td>
            <td>${escapeHtml(annualChange(market.series, "imports"))}</td>
            <td>${displayValue(latest.domestic_consumption)}</td>
            <td>${displayValue(latest.ending_stocks)}</td>
          </tr>
        `;
      })
      .join("");
    return `
      <article class="supply-table-card">
        <header>
          <div><span>Import Demand</span><h3>${escapeHtml(section.title)}</h3></div>
          <small>${escapeHtml(section.definition)}</small>
        </header>
        <div class="supply-table-scroll">
          <table class="supply-data-table">
            <thead><tr><th>市场</th><th>市场年度</th><th>进口量</th><th>同比</th><th>消费量</th><th>期末库存</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </article>
    `;
  }

  function renderVegetableOils(section) {
    const rows = (section.oils || [])
      .map((oil) => {
        const latest = oil.series?.at(-1);
        if (!latest) return "";
        return `
          <tr>
            <th scope="row">${escapeHtml(oil.name)}</th>
            <td>${escapeHtml(latest.market_year)}</td>
            <td>${displayValue(latest.production)}</td>
            <td>${escapeHtml(annualChange(oil.series, "production"))}</td>
            <td>${displayValue(latest.domestic_consumption)}</td>
            <td>${displayValue(latest.ending_stocks)}</td>
            <td>${ratio(latest.ending_stocks, latest.domestic_consumption)}</td>
          </tr>
        `;
      })
      .join("");
    return `
      <article class="supply-table-card">
        <header>
          <div><span>Substitute Oils</span><h3>${escapeHtml(section.title)}</h3></div>
          <small>${escapeHtml(section.definition)}</small>
        </header>
        <div class="supply-table-scroll">
          <table class="supply-data-table">
            <thead><tr><th>油种</th><th>市场年度</th><th>产量</th><th>产量同比</th><th>消费量</th><th>期末库存</th><th>库存消费比</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </article>
    `;
  }

  function renderSupplemental(section) {
    if (!section) return "";
    const status = section.status || "parse_error";
    return `
      <section class="supply-supplemental" aria-labelledby="supplemental-title">
        <header class="supply-country-heading supply-supplemental-heading">
          <div>
            <p>Global Balance · Import Demand · Substitute Oils</p>
            <h2 id="supplemental-title">全球与消费端供需</h2>
          </div>
          <div class="supply-country-status">
            <span class="supply-status supply-status-${escapeHtml(status)}">${escapeHtml(STATUS_LABELS[status] || status)}</span>
            <small>${escapeHtml(section.status_message)}</small>
          </div>
        </header>
        <div class="supply-psd-meta">
          <span>USDA PSD ${escapeHtml(section.release_period)}版</span>
          <span>单位：万吨</span>
          <a href="${escapeHtml(section.source?.url || "#")}" target="_blank" rel="noopener noreferrer">查看官方数据库 ↗</a>
        </div>
        <div class="supply-table-stack">
          ${renderGlobalBalance(section.global_balance || {})}
          ${renderImportDemand(section.import_demand || {})}
          ${renderVegetableOils(section.vegetable_oils || {})}
        </div>
      </section>
    `;
  }

  function renderUpdateNotice(payload) {
    const status = payload.update_status || "source_error";
    const checkedAt = payload.checked_at || payload.generated_at;
    const checkedText = checkedAt
      ? new Date(checkedAt).toLocaleString("zh-CN", {
          timeZone: payload.timezone || "Asia/Shanghai",
          hour12: false,
        })
      : "需进一步核验";
    return `
      <section class="supply-update-notice supply-update-${escapeHtml(status)}" aria-label="官方数据检查状态">
        <div>
          <span>${escapeHtml(UPDATE_STATUS_LABELS[status] || "检查状态")}</span>
          <strong>${escapeHtml(payload.update_message || "官方来源检查状态需进一步核验。")}</strong>
        </div>
        <dl>
          <div><dt>跟随日报</dt><dd>${escapeHtml(payload.checked_for_report_date || "需进一步核验")}</dd></div>
          <div><dt>检查时间</dt><dd>${escapeHtml(checkedText)}</dd></div>
        </dl>
      </section>
    `;
  }

  function drawChart(canvas, series, rangeEnd, displayMonths) {
    if (!canvas || !rangeEnd) return;
    const rect = canvas.getBoundingClientRect();
    if (!rect.width) return;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const height = 220;
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(height * ratio);
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);

    const width = rect.width;
    const padding = { top: 18, right: 14, bottom: 34, left: 46 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;
    const periods = monthRange(rangeEnd, displayMonths);
    const valuesByPeriod = new Map(series.map((item) => [item.period, item.value / 10000]));
    const values = periods.map((period) => valuesByPeriod.get(period));
    const available = values.filter(Number.isFinite);

    context.clearRect(0, 0, width, height);
    if (!available.length) {
      context.fillStyle = "rgba(244, 248, 242, .52)";
      context.font = "12px system-ui";
      context.fillText("暂无可核验数据", padding.left, padding.top + 30);
      return;
    }

    let minimum = Math.min(...available);
    let maximum = Math.max(...available);
    const spread = maximum - minimum || Math.max(maximum * 0.1, 1);
    minimum = Math.max(0, minimum - spread * 0.16);
    maximum += spread * 0.16;

    context.lineWidth = 1;
    context.font = "10px system-ui";
    context.textAlign = "right";
    context.textBaseline = "middle";
    for (let index = 0; index <= 3; index += 1) {
      const y = padding.top + (plotHeight * index) / 3;
      const label = maximum - ((maximum - minimum) * index) / 3;
      context.strokeStyle = "rgba(220, 240, 213, .11)";
      context.beginPath();
      context.moveTo(padding.left, y);
      context.lineTo(width - padding.right, y);
      context.stroke();
      context.fillStyle = "rgba(244, 248, 242, .46)";
      context.fillText(label.toFixed(0), padding.left - 8, y);
    }

    const xFor = (index) => padding.left + (plotWidth * index) / Math.max(periods.length - 1, 1);
    const yFor = (value) => padding.top + ((maximum - value) / (maximum - minimum)) * plotHeight;
    context.strokeStyle = "#7bc790";
    context.lineWidth = 2;
    context.lineJoin = "round";
    context.lineCap = "round";
    context.beginPath();
    let drawing = false;
    values.forEach((value, index) => {
      if (!Number.isFinite(value)) {
        drawing = false;
        return;
      }
      const x = xFor(index);
      const y = yFor(value);
      if (!drawing) context.moveTo(x, y);
      else context.lineTo(x, y);
      drawing = true;
    });
    context.stroke();

    values.forEach((value, index) => {
      if (!Number.isFinite(value)) return;
      context.beginPath();
      context.fillStyle = "#d7b06c";
      context.arc(xFor(index), yFor(value), index === values.length - 1 ? 3.5 : 2, 0, Math.PI * 2);
      context.fill();
    });

    context.fillStyle = "rgba(244, 248, 242, .46)";
    context.font = "10px system-ui";
    context.textAlign = "center";
    context.textBaseline = "top";
    [0, 6, 12, 18, periods.length - 1]
      .filter((value, index, list) => value >= 0 && value < periods.length && list.indexOf(value) === index)
      .forEach((index) => {
        context.fillText(periods[index].replace("-", "."), xFor(index), height - padding.bottom + 10);
      });
  }

  function initializeCharts(payload) {
    charts.length = 0;
    const displayMonths = Number(payload.display_months) || 24;
    Object.entries(payload.countries).forEach(([countryKey, country]) => {
      const allPeriods = METRIC_ORDER
        .flatMap((metricKey) => (country.metrics?.[metricKey]?.series || []).map((item) => item.period))
        .sort();
      const rangeEnd = allPeriods.at(-1) || country.latest_period;
      METRIC_ORDER.forEach((metricKey) => {
        const canvas = document.getElementById(`chart-${countryKey}-${metricKey}`);
        const series = country.metrics?.[metricKey]?.series || [];
        charts.push({ canvas, series, rangeEnd, displayMonths });
        drawChart(canvas, series, rangeEnd, displayMonths);
      });
    });
  }

  function render(payload) {
    const displayMonths = Number(payload.display_months) || 24;
    const countries = Object.entries(payload.countries)
      .map(([key, country]) => countrySection(key, country, displayMonths))
      .join("");
    root.innerHTML = `${renderUpdateNotice(payload)}${countries}${renderSupplemental(payload.supplemental)}`;
    const checkedAt = payload.checked_at || payload.generated_at;
    generated.textContent = `官方来源检查：${new Date(checkedAt).toLocaleString("zh-CN", {
      timeZone: payload.timezone || "Asia/Shanghai",
      hour12: false,
    })}`;
    requestAnimationFrame(() => initializeCharts(payload));
  }

  function renderError() {
    root.innerHTML = `
      <div class="supply-demand-error" role="alert">
        <strong>供需数据暂时无法读取</strong>
        <span>已停止展示可能不完整的结果，请稍后重试；需进一步核验。</span>
      </div>
    `;
    generated.textContent = "数据更新时间读取失败";
  }

  let resizeTimer;
  window.addEventListener("resize", () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      charts.forEach(({ canvas, series, rangeEnd, displayMonths }) => {
        drawChart(canvas, series, rangeEnd, displayMonths);
      });
    }, 120);
  });

  fetch(DATA_URL, { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(render)
    .catch(renderError);
})();

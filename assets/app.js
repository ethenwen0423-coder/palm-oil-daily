(function () {
  const reports = Array.isArray(window.PALM_OIL_REPORTS) ? window.PALM_OIL_REPORTS : [];
  const latestDate = document.querySelector("#latest-date");
  const latestUpdated = document.querySelector("#latest-updated");
  const recentList = document.querySelector("#recent-list");
  const dailyList = document.querySelector("#daily-list");
  const weeklyList = document.querySelector("#weekly-list");
  const dailyReportLink = document.querySelector("#daily-report-link");
  const weeklyReportLink = document.querySelector("#weekly-report-link");
  const tabTriggers = Array.from(document.querySelectorAll("[data-tab-target]"));
  const homeTabs = Array.from(document.querySelectorAll(".home-tab"));
  const tabPanels = Array.from(document.querySelectorAll(".tab-panel"));
  const oilFuturesList = document.querySelector("#oil-futures-list");
  const oilFuturesUpdated = document.querySelector("#oil-futures-updated");
  const oilFuturesSource = document.querySelector("#oil-futures-source");
  const overviewDate = document.querySelector("#overview-date");
  const overviewDailyTitle = document.querySelector("#overview-daily-title");
  const overviewDailyLink = document.querySelector("#overview-daily-link");
  const overviewWeeklyTitle = document.querySelector("#overview-weekly-title");
  const overviewWeeklyLink = document.querySelector("#overview-weekly-link");
  const overviewFuturesTitle = document.querySelector("#overview-futures-title");
  const overviewFuturesStrip = document.querySelector("#overview-futures-strip");
  const overviewMarketReferences = document.querySelector("#overview-market-references");
  const sourcesReports = document.querySelector("#sources-reports");
  const sourcesFutures = document.querySelector("#sources-futures");
  const heroCall = document.querySelector("#hero-call");
  const heroPoints = document.querySelector("#hero-points");
  const detailTitle = document.querySelector("#detail-title");
  const detailMeta = document.querySelector("#detail-meta");
  const detailKind = document.querySelector("#detail-kind");
  const detailContent = document.querySelector("#report-content");
  const downloadLink = document.querySelector("#download-link");

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function renderInline(value) {
    return escapeHtml(value).replace(/https?:\/\/[^\s<]+/g, (url) => {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });
  }

  function renderMarkdown(markdown) {
    const lines = markdown.split(/\r?\n/);
    const html = [];
    let listOpen = false;
    let tableRows = [];

    function closeList() {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
    }

    function closeTable() {
      if (!tableRows.length) return;
      const rows = tableRows.map((row, index) => {
        const cells = row
          .split("|")
          .slice(1, -1)
          .map((cell) => escapeHtml(cell.trim()));
        const tag = index === 0 ? "th" : "td";
        return `<tr>${cells.map((cell) => `<${tag}>${cell}</${tag}>`).join("")}</tr>`;
      });
      html.push(`<table>${rows.join("")}</table>`);
      tableRows = [];
    }

    lines.forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed) {
        closeList();
        closeTable();
        return;
      }
      if (/^\|.+\|$/.test(trimmed) && !/^\|\s*-+/.test(trimmed)) {
        closeList();
        tableRows.push(trimmed);
        return;
      }
      if (/^\|\s*:?-+/.test(trimmed)) {
        return;
      }
      closeTable();
      if (trimmed.startsWith("### ")) {
        closeList();
        html.push(`<h3>${escapeHtml(trimmed.slice(4))}</h3>`);
      } else if (trimmed.startsWith("## ")) {
        closeList();
        html.push(`<h2>${escapeHtml(trimmed.slice(3))}</h2>`);
      } else if (trimmed.startsWith("# ")) {
        closeList();
        html.push(`<h1>${escapeHtml(trimmed.slice(2))}</h1>`);
      } else if (/^- /.test(trimmed)) {
        if (!listOpen) {
          html.push("<ul>");
          listOpen = true;
        }
        html.push(`<li>${escapeHtml(trimmed.slice(2))}</li>`);
      } else {
        closeList();
        if (/^【结论】/.test(trimmed)) {
          html.push(`<p class="research-conclusion">${escapeHtml(trimmed.replace(/^【结论】\s*/, ""))}</p>`);
        } else {
          html.push(`<p>${escapeHtml(trimmed)}</p>`);
        }
      }
    });
    closeList();
    closeTable();
    return html.join("");
  }

  function normalizeHeading(value) {
    return String(value || "")
      .replace(/^#+\s*/, "")
      .replace(/[【】\[\]]/g, "")
      .trim();
  }

  function parseMarkdownSections(markdown) {
    const sections = [];
    let current = null;

    String(markdown || "")
      .split(/\r?\n/)
      .forEach((line) => {
        if (line.startsWith("# ")) return;
        if (line.startsWith("## ")) {
          current = { title: normalizeHeading(line), lines: [] };
          sections.push(current);
          return;
        }
        if (!current) {
          current = { title: "摘要", lines: [] };
          sections.push(current);
        }
        current.lines.push(line);
      });

    return sections
      .map((section) => ({
        ...section,
        body: section.lines.join("\n").trim(),
      }))
      .filter((section) => section.body);
  }

  function sectionMatches(section, module) {
    if (module.match) return module.match(section.title);
    return module.keywords.some((keyword) => section.title.includes(keyword));
  }

  function renderSectionBody(markdown) {
    const lines = String(markdown || "").split(/\r?\n/);
    const html = [];
    let listOpen = false;
    let tableRows = [];

    function closeList() {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
    }

    function closeTable() {
      if (!tableRows.length) return;
      const rows = tableRows.map((row, index) => {
        const cells = row
          .split("|")
          .slice(1, -1)
          .map((cell) => renderInline(cell.trim()));
        const tag = index === 0 ? "th" : "td";
        return `<tr>${cells.map((cell) => `<${tag}>${cell}</${tag}>`).join("")}</tr>`;
      });
      html.push(`<div class="research-table-wrap"><table>${rows.join("")}</table></div>`);
      tableRows = [];
    }

    lines.forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed) {
        closeList();
        closeTable();
        return;
      }
      if (/^\|.+\|$/.test(trimmed) && !/^\|\s*-+/.test(trimmed)) {
        closeList();
        tableRows.push(trimmed);
        return;
      }
      if (/^\|\s*:?-+/.test(trimmed)) {
        return;
      }
      closeTable();
      if (trimmed.startsWith("### ")) {
        closeList();
        html.push(`<h3>${escapeHtml(normalizeHeading(trimmed))}</h3>`);
      } else if (/^[-*] /.test(trimmed)) {
        if (!listOpen) {
          html.push("<ul>");
          listOpen = true;
        }
        html.push(`<li>${renderInline(trimmed.slice(2))}</li>`);
      } else if (/^\d+\.\s+/.test(trimmed)) {
        if (!listOpen) {
          html.push("<ul>");
          listOpen = true;
        }
        html.push(`<li>${renderInline(trimmed.replace(/^\d+\.\s+/, ""))}</li>`);
      } else {
        closeList();
        if (/^【结论】/.test(trimmed)) {
          html.push(`<p class="research-conclusion">${renderInline(trimmed.replace(/^【结论】\s*/, ""))}</p>`);
        } else {
          html.push(`<p>${renderInline(trimmed)}</p>`);
        }
      }
    });

    closeList();
    closeTable();
    return html.join("");
  }

  function renderResearchModules(report) {
    const sections = parseMarkdownSections(report.content || "");
    const used = new Set();
    const modules = [
      {
        title: "今日观点",
        label: "观点",
        keywords: ["今日观点", "一句话核心观点"],
        fallback: report.headline || report.summary || "",
      },
      {
        title: "交易信号",
        label: "信号",
        keywords: ["今日交易信号", "交易信号", "市场一致预期"],
      },
      {
        title: "核心逻辑",
        label: "逻辑",
        keywords: ["今日交易重点", "昨夜发生了什么", "市场复盘", "本周三大变化", "核心逻辑"],
      },
      {
        title: "关键数据",
        label: "数据",
        keywords: ["今日关键数据", "关键价格", "观察指标", "核心数据变化", "下周重要事件"],
      },
      {
        title: "交易计划",
        label: "计划",
        keywords: ["开盘推演", "交易计划", "周一开盘推演"],
      },
      {
        title: "风险提示",
        label: "风控",
        keywords: ["风险提示"],
        match: (title) => title === "风险提示",
      },
      {
        title: "消息来源链接",
        label: "来源",
        keywords: ["消息来源链接"],
        match: (title) => title === "消息来源链接",
      },
      {
        title: "AI观点风险提示",
        label: "声明",
        keywords: ["AI观点风险提示"],
        match: (title) => title === "AI观点风险提示",
      },
      {
        title: "信息来源与核验说明",
        label: "核验",
        keywords: ["信息来源与核验说明"],
        match: (title) => title === "信息来源与核验说明",
      },
    ];

    const cards = modules
      .map((module) => {
        const matched = [];
        sections.forEach((section, index) => {
          if (!used.has(index) && sectionMatches(section, module)) {
            matched.push(section);
            used.add(index);
          }
        });
        const body = matched.map((section) => section.body).join("\n\n");
        const content = body || module.fallback;
        if (!content) return "";
        return `
          <section class="research-card" aria-labelledby="module-${escapeHtml(module.title)}">
            <div class="research-card-heading">
              <span>${escapeHtml(module.label)}</span>
              <h2 id="module-${escapeHtml(module.title)}">${escapeHtml(module.title)}</h2>
            </div>
            <div class="research-card-body">
              ${renderSectionBody(content)}
            </div>
          </section>
        `;
      })
      .filter(Boolean);

    return cards.join("");
  }

  function getKind(report) {
    return report.kind === "weekend" || /-weekend$/.test(report.date) ? "weekly" : "daily";
  }

  function baseDate(report) {
    return String(report.date || "").replace(/-weekend$/, "");
  }

  function formatDate(date) {
    const parts = String(date).split("-");
    if (parts.length !== 3) return date;
    return `${parts[0]}年${parts[1]}月${parts[2]}日`;
  }

  function formatShortDate(date) {
    const parts = String(date).split("-");
    if (parts.length !== 3) return date;
    return `${parts[1]}月${parts[2]}日`;
  }

  function cleanReportTitle(report) {
    const raw = report.title || "";
    return raw
      .replace(/^\d{4}-\d{2}-\d{2}\s*/, "")
      .replace(/^棕榈油/, "")
      .replace(/^行情/, "")
      .trim();
  }

  function displayHeadline(report) {
    const raw = report.headline || "";
    return raw
      .replace(/^预计/, "")
      .replace(/^周一开盘/, "")
      .replace(/^[:：，, ]+/, "")
      .trim();
  }

  function getHeroView(report) {
    const headline = displayHeadline(report) || cleanReportTitle(report) || "等待今日观点";
    const parts = headline
      .split(/[；;。]/)
      .map((part) => part.trim())
      .filter(Boolean);
    const main = (parts[0] || headline)
      .replace(/\s+/g, " ")
      .replace(/^P\s*主力/, "P主力")
      .trim();
    const secondary = parts.slice(1);
    if (!secondary.length && /，/.test(main)) {
      const commaParts = main.split(/，/).map((part) => part.trim()).filter(Boolean);
      return {
        call: commaParts[0] || main,
        points: commaParts.slice(1, 3),
      };
    }
    return {
      call: main,
      points: secondary.slice(0, 2),
    };
  }

  function compactTopic(value, maxLength) {
    return String(value || "")
      .replace(/[，。；：、,.!！?？“”"']/g, "")
      .replace(/^本周(棕榈油|油脂)?(维持|延续)?/, "")
      .replace(/^今日(棕榈油|油脂)?(维持|延续)?/, "")
      .replace(/^是/, "")
      .replace(/^P\s*主力/, "P")
      .replace(/^棕榈油/, "")
      .replace(/(.+)P\s*主力.*$/, "$1")
      .replace(/\s+/g, "")
      .slice(0, Math.max(0, maxLength));
  }

  function listTitle(report) {
    const kind = getKind(report) === "weekly" ? "周报" : "晨报";
    const dateText = formatShortDate(baseDate(report));
    const maxTopicLength = 15;
    let topic = displayHeadline(report) || cleanReportTitle(report);
    if (kind === "晨报" && (!topic || /^日报/.test(topic))) {
      topic = report.summary || "发生了什么事";
    }
    if (!topic) {
      topic = kind === "周报" ? "油脂强弱" : "盘前策略";
    }
    const compact = compactTopic(topic, maxTopicLength);
    return `${dateText}${kind}${compact ? ` ${compact}` : ""}`;
  }

  function detailPageTitle(report) {
    const dateText = formatShortDate(baseDate(report));
    const kind = getKind(report) === "weekly" ? "周报" : "晨报";
    const title = cleanReportTitle(report);
    const prefix = title && /^(晨报|周报)$/.test(title) ? `${dateText}${kind}` : title || `${dateText}${kind}`;
    const headline = displayHeadline(report);
    return headline ? `${prefix} ${headline}` : prefix;
  }

  function overviewReportTitle(report) {
    const title = String(report.title || "").trim() || `${formatShortDate(baseDate(report))}${getKind(report) === "weekly" ? "周报" : "晨报"}`;
    const headline = displayHeadline(report);
    return headline ? `${title} ${headline}` : title;
  }

  function reportHref(report) {
    return `report.html?id=${encodeURIComponent(report.date)}`;
  }

  function reportTime(report) {
    const timestamp = Date.parse(`${baseDate(report)}T00:00:00`);
    return Number.isNaN(timestamp) ? 0 : timestamp;
  }

  function renderDirection(value) {
    const direction = String(value || "→");
    const className = direction === "↑" ? "up" : direction === "↓" ? "down" : "flat";
    return `<span class="futures-direction ${className}">${escapeHtml(direction)}</span>`;
  }

  function renderStrategyRecommendation(recommendation) {
    const strategy = recommendation || {};
    if (!strategy.take_profit || !strategy.stop_loss) {
      return '<p class="futures-view">综合止盈止损需进一步核验。</p>';
    }
    return `
      <div class="futures-strategy-recommendation">
        <h4>综合策略建议</h4>
        <dl>
          <div>
            <dt>参考触发</dt>
            <dd>${escapeHtml(strategy.entry || "需进一步核验")}</dd>
          </div>
          <div>
            <dt>综合止盈</dt>
            <dd>${escapeHtml(strategy.take_profit || "需进一步核验")}</dd>
          </div>
          <div>
            <dt>综合止损</dt>
            <dd>${escapeHtml(strategy.stop_loss || "需进一步核验")}</dd>
          </div>
        </dl>
        <p>${escapeHtml(strategy.basis || "综合多组策略测算后给出当前最合适点位。")}</p>
      </div>
    `;
  }

  function renderAnalysisDetails(contract) {
    const groups = [
      ["技术面详解", contract.technical_detail],
      ["基本面详解", contract.fundamental_detail],
    ];
    return `
      <div class="futures-analysis-details">
        ${groups
          .map(([title, items]) => {
            const detailItems = Array.isArray(items) ? items : [];
            return `
              <section>
                <h4>${escapeHtml(title)}</h4>
                ${
                  detailItems.length
                    ? `<ul>${detailItems
                        .map(
                          (item) => `
                            <li>
                              <strong>${escapeHtml(item.title || "要点")}</strong>
                              <span>${escapeHtml(item.text || "需进一步核验")}</span>
                            </li>
                          `,
                        )
                        .join("")}</ul>`
                    : '<p>需进一步核验。</p>'
                }
              </section>
            `;
          })
          .join("")}
      </div>
    `;
  }

  function renderContractBody(contract) {
    const score = contract.score || {};
    const totalScore = score.total ?? contract.total_score ?? "需进一步核验";
    const technicalScore = score.technical ?? contract.technical_score ?? "需进一步核验";
    const fundamentalScore = score.fundamental ?? contract.basic_score ?? "需进一步核验";
    const stance = score.stance || contract.strategy || "需进一步核验";
    return `
      <div class="futures-card-top">
        <div>
          <span class="futures-market">${escapeHtml(contract.market || "")}</span>
          <h3>${escapeHtml(contract.name || "")} <span>${escapeHtml(contract.contract || "主力")}</span></h3>
        </div>
        ${renderDirection(contract.direction)}
      </div>
      <div class="futures-price-row">
        <strong>${escapeHtml(contract.price || "需进一步核验")}</strong>
        <span>${escapeHtml(contract.change || "需进一步核验")}</span>
      </div>
      <dl class="futures-score">
        <div>
          <dt>综合评分</dt>
          <dd>${escapeHtml(totalScore)}</dd>
        </div>
        <div>
          <dt>行情观点</dt>
          <dd>${escapeHtml(stance)}</dd>
        </div>
        <div>
          <dt>技术面</dt>
          <dd>${escapeHtml(technicalScore)}</dd>
        </div>
        <div>
          <dt>基本面</dt>
          <dd>${escapeHtml(fundamentalScore)}</dd>
        </div>
      </dl>
      <p class="futures-view">${escapeHtml(contract.view || contract.note || "走势观点需进一步核验。")}</p>
      ${renderAnalysisDetails(contract)}
      ${renderStrategyRecommendation(contract.strategy_recommendation)}
      <p class="futures-verification">${escapeHtml(contract.verification || contract.quality_note || "")}</p>
    `;
  }

  function renderContractCard(contract) {
    return `<article class="futures-card">${renderContractBody(contract)}</article>`;
  }

  function renderWatchlistCard(contracts, options) {
    const optionItems = (Array.isArray(options) && options.length ? options : contracts.map((contract) => ({
      value: contract.symbol,
      label: contract.symbol,
      name: contract.name,
      contract: contract.contract,
    }))).filter((item) => item.value);
    return `
      <article class="futures-card futures-watch-card">
        <div class="futures-card-top">
          <div>
            <span class="futures-market">WATCH</span>
            <h3>自选合约 <span>关注</span></h3>
          </div>
        </div>
        <div class="futures-watch-controls">
          <select id="futures-watch-select" aria-label="合约简称">
            <option value="">选择合约</option>
            ${optionItems
              .map((item) => {
                const display = item.display || `${item.name || ""} ${item.contract || item.label || ""} ${item.contract_label || ""}`.trim();
                return `<option value="${escapeHtml(item.value)}">${escapeHtml(display || item.label || item.value)}</option>`;
              })
              .join("")}
          </select>
          <button id="futures-watch-confirm" type="button">确认</button>
        </div>
        <div id="futures-watch-result" class="futures-watch-result"></div>
      </article>
    `;
  }

  function bindFuturesWatchlist(contracts) {
    const select = document.querySelector("#futures-watch-select");
    const confirm = document.querySelector("#futures-watch-confirm");
    const result = document.querySelector("#futures-watch-result");
    if (!select || !confirm || !result) return;
    confirm.addEventListener("click", () => {
      const contract = contracts.find((item) => item.symbol === select.value);
      result.innerHTML = contract ? renderContractBody(contract) : '<p class="futures-view">需进一步核验。</p>';
    });
  }

  function renderOilFutures() {
    if (!oilFuturesList) return;
    const data = window.OIL_FUTURES_CONTRACTS || {};
    const contracts = Array.isArray(data.contracts) ? data.contracts : [];
    if (oilFuturesUpdated) {
      oilFuturesUpdated.textContent = data.updated_at ? `更新 ${data.updated_at}` : "等待行情数据";
    }
    if (overviewFuturesTitle) {
      overviewFuturesTitle.textContent = data.updated_at ? `更新 ${data.updated_at}` : "等待行情数据";
    }
    if (oilFuturesSource) {
      oilFuturesSource.textContent = data.source || "数据源等待加载";
    }
    if (sourcesFutures) {
      sourcesFutures.textContent = data.source || "油脂主力合约行情等待加载。";
    }
    if (!contracts.length) {
      oilFuturesList.innerHTML = '<p class="empty">暂无油脂期货主力合约数据。</p>';
      if (overviewFuturesStrip) overviewFuturesStrip.innerHTML = '<p class="empty">暂无油脂油料合约数据。</p>';
      return;
    }

    const overviewContracts = contracts.filter((contract) => {
      const product = String(contract.product || "").toUpperCase();
      return product === "FCPO" || String(contract.symbol || "").toUpperCase() === "FCPO" || (["P", "Y", "OI"].includes(product) && Number(contract.contract_rank) === 1);
    });
    if (overviewFuturesStrip) {
      overviewFuturesStrip.innerHTML = overviewContracts
        .map((contract) => {
          const change = Number.parseFloat(String(contract.change || "").replace("%", ""));
          const state = change > 0 ? "up" : change < 0 ? "down" : "flat";
          return `
            <article class="market-strip-item ${state}">
              <div>
                <strong>${escapeHtml(contract.name || contract.product || "合约")}</strong>
                <span>${escapeHtml(contract.contract || contract.symbol || "")}</span>
              </div>
              <b>${escapeHtml(contract.price || "--")}</b>
              <small>${escapeHtml(contract.change || "--")}</small>
            </article>
          `;
        })
        .join("");
    }
    if (overviewMarketReferences) {
      const references = data.market_references || {};
      const items = [references.malaysia_fcpo, references.india_cpo_spot].filter(Boolean);
      overviewMarketReferences.innerHTML = items.length
        ? items
            .map(
              (reference) => `
                <article class="market-reference-item">
                  <div>
                    <span>${escapeHtml(reference.label || "海外市场")}</span>
                    <small>${escapeHtml(reference.location || "")}</small>
                  </div>
                  <strong>${escapeHtml(reference.price || "待更新")}</strong>
                  <p>
                    <b>${escapeHtml(reference.unit || "")}</b>
                    <em>${escapeHtml(reference.change || "需进一步核验")}</em>
                  </p>
                  <small class="market-reference-time">${escapeHtml(reference.updated_at || "待更新")}</small>
                </article>
              `,
            )
            .join("")
        : '<p class="empty">海外价格参照待更新。</p>';
    }
    oilFuturesList.innerHTML = `${contracts.map(renderContractCard).join("")}${renderWatchlistCard(contracts, data.watchlist_options)}`;
    bindFuturesWatchlist(contracts);
  }

  function activateTab(targetId) {
    homeTabs.forEach((tab) => {
      const active = tab.dataset.tabTarget === targetId;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    tabPanels.forEach((panel) => {
      panel.classList.toggle("active", panel.id === targetId);
    });
  }

  function bindHomeTabs() {
    if (!tabTriggers.length) return;
    homeTabs.forEach((tab) => {
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-selected", tab.classList.contains("active") ? "true" : "false");
    });
    tabTriggers.forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        const targetId = trigger.dataset.tabTarget;
        if (!targetId) return;
        activateTab(targetId);
        if (trigger.tagName !== "A") return;
        event.preventDefault();
        window.history.replaceState(null, "", `#${targetId}`);
        document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    const hashTarget = window.location.hash.replace(/^#/, "");
    if (hashTarget && tabPanels.some((panel) => panel.id === hashTarget)) {
      activateTab(hashTarget);
    }
  }

  function recentReports() {
    const datedReports = reports.filter((report) => reportTime(report));
    if (!datedReports.length) return [];
    const newest = Math.max(...datedReports.map(reportTime));
    const weekMs = 7 * 24 * 60 * 60 * 1000;
    return datedReports
      .filter((report) => newest - reportTime(report) < weekMs)
      .sort((left, right) => reportTime(right) - reportTime(left));
  }

  function renderIndex() {
    if (!dailyList || !weeklyList) return;
    const latest = reports[0];
    const groups = {
      daily: reports.filter((report) => getKind(report) === "daily").sort((left, right) => reportTime(right) - reportTime(left)),
      weekly: reports.filter((report) => getKind(report) === "weekly").sort((left, right) => reportTime(right) - reportTime(left)),
    };
    const latestDaily = groups.daily[0] || latest;
    const latestWeekly = groups.weekly[0];
    if (latestDate) latestDate.textContent = latestDaily ? baseDate(latestDaily) : "等待生成";
    if (overviewDate) overviewDate.textContent = latestDaily ? `更新 ${baseDate(latestDaily)}` : "等待更新";
    if (latestUpdated) {
      const updated = latestDaily?.updated_at || "";
      const time = updated.split(/\s+/)[1];
      latestUpdated.textContent = time ? `${time} 北京时间` : "自动发布准备中";
    }
    if (sourcesReports) {
      sourcesReports.textContent = latestDaily?.updated_at
        ? `最新日报整理于 ${latestDaily.updated_at}；报告归档按发布日期倒序排列。`
        : "日报与周报由本地发布流程同步生成。";
    }
    if (latestDaily) {
      const view = getHeroView(latestDaily);
      if (heroCall) heroCall.textContent = view.call || "等待今日观点";
      if (heroPoints) {
        const points = view.points.length ? view.points : ["等待盘面确认", "控制追高风险"];
        heroPoints.innerHTML = points
          .slice(0, 2)
          .map((point) => `<li>${escapeHtml(point)}</li>`)
          .join("");
      }
      if (overviewDailyTitle) overviewDailyTitle.textContent = overviewReportTitle(latestDaily);
      if (overviewDailyLink) overviewDailyLink.href = reportHref(latestDaily);
    }
    if (latestWeekly) {
      if (overviewWeeklyTitle) overviewWeeklyTitle.textContent = overviewReportTitle(latestWeekly);
      if (overviewWeeklyLink) overviewWeeklyLink.href = reportHref(latestWeekly);
    }
    if (dailyReportLink && latestDaily) dailyReportLink.href = reportHref(latestDaily);
    if (weeklyReportLink && latestWeekly) weeklyReportLink.href = reportHref(latestWeekly);

    function renderGroup(target, items, emptyText, className = "report-link") {
      if (!items.length) {
        target.innerHTML = `<p class="empty">${escapeHtml(emptyText)}</p>`;
        return;
      }
      target.innerHTML = items
        .map(
          (report) => `
            <a class="${className}" href="${reportHref(report)}">
              <span>${escapeHtml(listTitle(report))}</span>
            </a>
          `,
        )
        .join("");
    }

    if (recentList) {
      renderGroup(recentList, recentReports(), "暂无最近一周报告。", "report-link recent-link");
    }
    renderGroup(dailyList, groups.daily, "暂无日报。");
    renderGroup(weeklyList, groups.weekly, "暂无周报。");
  }

  function renderDetail() {
    if (!detailTitle || !detailContent) return;
    const id = new URLSearchParams(window.location.search).get("id");
    const report = reports.find((item) => item.date === id) || reports[0];
    if (!report) {
      detailTitle.textContent = "未找到报告";
      detailContent.innerHTML = "<p>暂无可展示的报告。</p>";
      return;
    }

    const kindLabel = getKind(report) === "weekly" ? "周报" : "日报";
    const fullTitle = detailPageTitle(report);
    document.title = `${fullTitle} | vinsontesla.com`;
    detailKind.textContent = kindLabel;
    detailTitle.textContent = fullTitle;
    detailMeta.textContent = report.updated_at ? `最后整理：${report.updated_at}` : "";
    if (downloadLink) {
      downloadLink.href = report.download || `reports/${report.date}.md`;
      downloadLink.setAttribute("download", `${report.date}.md`);
    }
    detailContent.innerHTML = renderResearchModules(report);
  }

  if (!reports.length && dailyList && weeklyList) {
    if (recentList) recentList.innerHTML = '<p class="empty">暂无最近一周报告。</p>';
    dailyList.innerHTML = '<p class="empty">暂无日报。</p>';
    weeklyList.innerHTML = '<p class="empty">暂无周报。</p>';
    return;
  }

  renderIndex();
  renderOilFutures();
  bindHomeTabs();
  renderDetail();
})();

(function () {
  const reports = Array.isArray(window.PALM_OIL_REPORTS) ? window.PALM_OIL_REPORTS : [];
  const latestDate = document.querySelector("#latest-date");
  const latestUpdated = document.querySelector("#latest-updated");
  const recentList = document.querySelector("#recent-list");
  const dailyList = document.querySelector("#daily-list");
  const weeklyList = document.querySelector("#weekly-list");
  const dailyReportLink = document.querySelector("#daily-report-link");
  const weeklyReportLink = document.querySelector("#weekly-report-link");
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

  function sectionMatches(section, keywords) {
    return keywords.some((keyword) => section.title.includes(keyword));
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
          .map((cell) => escapeHtml(cell.trim()));
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
        html.push(`<li>${escapeHtml(trimmed.slice(2))}</li>`);
      } else if (/^\d+\.\s+/.test(trimmed)) {
        if (!listOpen) {
          html.push("<ul>");
          listOpen = true;
        }
        html.push(`<li>${escapeHtml(trimmed.replace(/^\d+\.\s+/, ""))}</li>`);
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
      },
    ];

    const cards = modules
      .map((module) => {
        const matched = sections.filter((section, index) => !used.has(index) && sectionMatches(section, module.keywords));
        matched.forEach((section) => used.add(sections.indexOf(section)));
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

  function reportHref(report) {
    return `report.html?id=${encodeURIComponent(report.date)}`;
  }

  function reportTime(report) {
    const timestamp = Date.parse(`${baseDate(report)}T00:00:00`);
    return Number.isNaN(timestamp) ? 0 : timestamp;
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
    if (latestUpdated) {
      const updated = latestDaily?.updated_at || "";
      const time = updated.split(/\s+/)[1];
      latestUpdated.textContent = time ? `${time} 北京时间` : "自动发布准备中";
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
    document.title = `${listTitle(report)} | vinsontesla.com`;
    detailKind.textContent = kindLabel;
    detailTitle.textContent = listTitle(report);
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
  renderDetail();
})();

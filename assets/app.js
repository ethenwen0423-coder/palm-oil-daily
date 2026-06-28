(function () {
  const reports = Array.isArray(window.PALM_OIL_REPORTS) ? window.PALM_OIL_REPORTS : [];
  const latestDate = document.querySelector("#latest-date");
  const latestUpdated = document.querySelector("#latest-updated");
  const recentList = document.querySelector("#recent-list");
  const dailyList = document.querySelector("#daily-list");
  const weeklyList = document.querySelector("#weekly-list");
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
        html.push(`<p>${escapeHtml(trimmed)}</p>`);
      }
    });
    closeList();
    closeTable();
    return html.join("");
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
      .replace(/\s+/g, "")
      .slice(0, Math.max(0, maxLength));
  }

  function listTitle(report) {
    const kind = getKind(report) === "weekly" ? "周报" : "晨报";
    const dateText = formatShortDate(baseDate(report));
    const maxTopicLength = 15 - dateText.length - kind.length - 1;
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
    return datedReports.filter((report) => newest - reportTime(report) < weekMs);
  }

  function renderIndex() {
    if (!dailyList || !weeklyList) return;
    const latest = reports[0];
    if (latestDate) latestDate.textContent = latest ? baseDate(latest) : "等待生成";
    if (latestUpdated) latestUpdated.textContent = latest?.updated_at ? `最后整理：${latest.updated_at}` : "自动发布准备中";

    const groups = {
      daily: reports.filter((report) => getKind(report) === "daily"),
      weekly: reports.filter((report) => getKind(report) === "weekly"),
    };

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
    detailContent.innerHTML = renderMarkdown(report.content || "");
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

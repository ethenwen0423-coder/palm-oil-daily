(function () {
  const reports = Array.isArray(window.PALM_OIL_REPORTS) ? window.PALM_OIL_REPORTS : [];
  const latestDate = document.querySelector("#latest-date");
  const latestUpdated = document.querySelector("#latest-updated");
  const title = document.querySelector("#report-title");
  const content = document.querySelector("#report-content");
  const select = document.querySelector("#report-select");
  const archive = document.querySelector("#archive-list");

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

  function setActive(date) {
    const report = reports.find((item) => item.date === date) || reports[0];
    if (!report) return;
    latestDate.textContent = reports[0].date;
    latestUpdated.textContent = reports[0].updated_at
      ? `最后整理：${reports[0].updated_at}`
      : "已生成";
    title.textContent = report.title || `${report.date} 棕榈油行情日报`;
    content.innerHTML = renderMarkdown(report.content || "");
    select.value = report.date;
    document.querySelectorAll(".archive-item").forEach((button) => {
      button.classList.toggle("active", button.dataset.date === report.date);
    });
  }

  if (!reports.length) {
    select.hidden = true;
    archive.innerHTML = '<p class="empty">暂无历史日报。</p>';
    return;
  }

  reports.forEach((report) => {
    const option = document.createElement("option");
    option.value = report.date;
    option.textContent = report.date;
    select.appendChild(option);

    const button = document.createElement("button");
    button.type = "button";
    button.className = "archive-item";
    button.dataset.date = report.date;
    button.innerHTML = `<strong>${escapeHtml(report.date)}</strong><span>${escapeHtml(
      report.summary || report.title || "棕榈油行情日报",
    )}</span>`;
    button.addEventListener("click", () => setActive(report.date));
    archive.appendChild(button);
  });

  select.addEventListener("change", () => setActive(select.value));
  setActive(reports[0].date);
})();

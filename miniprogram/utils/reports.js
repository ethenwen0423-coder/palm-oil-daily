function baseDate(report) {
  return String(report.date || "").replace(/-weekend$/, "");
}

function kind(report) {
  return report.kind === "weekend" || /-weekend$/.test(report.date || "") ? "weekly" : "daily";
}

function shortDate(value) {
  const parts = String(value || "").split("-");
  return parts.length === 3 ? `${parts[1]}月${parts[2]}日` : value;
}

function headline(report) {
  return String(report.headline || report.title || report.summary || "等待观点")
    .replace(/^预计/, "")
    .replace(/^周一开盘/, "")
    .replace(/^[:：，, ]+/, "")
    .trim();
}

function decorate(report) {
  const reportKind = kind(report);
  return Object.assign({}, report, {
    kindLabel: reportKind === "weekly" ? "周报" : "晨报",
    dateLabel: shortDate(baseDate(report)),
    displayTitle: `${shortDate(baseDate(report))}${reportKind === "weekly" ? "周报" : "晨报"}`,
    displayHeadline: headline(report),
  });
}

function splitReports(reports) {
  const decorated = (Array.isArray(reports) ? reports : []).map(decorate);
  return {
    all: decorated,
    daily: decorated.filter((item) => kind(item) === "daily"),
    weekly: decorated.filter((item) => kind(item) === "weekly"),
  };
}

function recentReports(reports) {
  if (!reports.length) return [];
  const newest = Date.parse(`${baseDate(reports[0])}T00:00:00`);
  const week = 7 * 24 * 60 * 60 * 1000;
  return reports.filter((item) => newest - Date.parse(`${baseDate(item)}T00:00:00`) < week);
}

module.exports = { baseDate, decorate, headline, kind, recentReports, splitReports };

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function inline(value) {
  return escapeHtml(value).replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a style="color:#0e6b5c;text-decoration:underline" href="$1">$1</a>',
  );
}

function renderMarkdown(markdown) {
  const output = [];
  let list = [];
  let table = [];

  function closeList() {
    if (!list.length) return;
    output.push(`<ul style="padding-left:20px;margin:10px 0">${list.map((item) => `<li style="margin:6px 0">${inline(item)}</li>`).join("")}</ul>`);
    list = [];
  }

  function closeTable() {
    if (!table.length) return;
    const rows = table.map((row, index) => {
      const tag = index === 0 ? "th" : "td";
      const cells = row.split("|").slice(1, -1);
      return `<tr>${cells.map((cell) => `<${tag} style="border:1px solid #d7d0c0;padding:7px;text-align:left">${inline(cell.trim())}</${tag}>`).join("")}</tr>`;
    });
    output.push(`<div style="overflow-x:auto;margin:12px 0"><table style="border-collapse:collapse;font-size:13px;min-width:100%">${rows.join("")}</table></div>`);
    table = [];
  }

  String(markdown || "").split(/\r?\n/).forEach((raw) => {
    const line = raw.trim();
    if (!line) { closeList(); closeTable(); return; }
    if (/^\|.+\|$/.test(line) && !/^\|\s*:?-+/.test(line)) { closeList(); table.push(line); return; }
    if (/^\|\s*:?-+/.test(line)) return;
    closeTable();
    if (/^###\s+/.test(line)) { closeList(); output.push(`<h3 style="font-size:17px;margin:18px 0 8px">${inline(line.replace(/^###\s+/, ""))}</h3>`); }
    else if (/^##\s+/.test(line)) { closeList(); output.push(`<h2 style="font-size:20px;color:#0b554b;border-left:4px solid #c79d41;padding-left:9px;margin:24px 0 10px">${inline(line.replace(/^##\s+/, ""))}</h2>`); }
    else if (/^#\s+/.test(line)) { closeList(); output.push(`<h1 style="font-size:23px;margin:8px 0 18px">${inline(line.replace(/^#\s+/, ""))}</h1>`); }
    else if (/^[-*]\s+/.test(line)) list.push(line.replace(/^[-*]\s+/, ""));
    else if (/^\d+\.\s+/.test(line)) list.push(line.replace(/^\d+\.\s+/, ""));
    else if (/^【结论】/.test(line)) { closeList(); output.push(`<p style="background:#eef5f1;border-radius:8px;padding:11px;margin:10px 0;font-weight:600">${inline(line)}</p>`); }
    else { closeList(); output.push(`<p style="line-height:1.8;margin:9px 0">${inline(line)}</p>`); }
  });
  closeList();
  closeTable();
  return output.join("");
}

module.exports = { renderMarkdown };

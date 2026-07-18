(function () {
  const dataset = window.QUANT_MODEL_SIGNALS || {};
  const models = Array.isArray(dataset.models) && dataset.models.length
    ? dataset.models.filter((item) => item.status === "active")
    : dataset.model ? [dataset.model] : [];
  const params = new URLSearchParams(window.location.search);
  const requestedId = params.get("model") || dataset.default_model_id || models[0]?.id || "";
  const select = document.querySelector("#detail-model-select");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function modelById(id) {
    return models.find((item) => item.id === id) || models[0];
  }

  function renderRule(rule, index) {
    if (!rule) return "";
    const conditions = Array.isArray(rule.conditions) ? rule.conditions : [];
    return `
      <article class="quant-rule-card">
        <span>${String(index + 1).padStart(2, "0")}</span>
        <h3>${escapeHtml(rule.title || "策略规则")}</h3>
        <p>${escapeHtml(rule.summary || "")}</p>
        <ul>${conditions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </article>`;
  }

  function render(model) {
    if (!model) {
      document.querySelector("#detail-model-name").textContent = "暂无可用模型";
      document.querySelector("#detail-model-summary").textContent = "模型注册数据不足。";
      select.disabled = true;
      return;
    }
    document.title = `${model.name || "模型策略详情"} | Vinson Research`;
    select.value = model.id;
    document.querySelector("#detail-model-status").textContent = `${model.status_label || "已启用"} · v${model.version || "1.0"}`;
    document.querySelector("#detail-model-name").textContent = model.name || model.id;
    document.querySelector("#detail-model-summary").textContent = model.summary || "策略摘要待补充。";
    document.querySelector("#detail-timeframe").textContent = model.timeframe || "待核验";
    document.querySelector("#detail-validated-instrument").textContent = model.validated_instrument || "待核验";
    document.querySelector("#detail-cost").textContent = Number.isFinite(Number(model.cost_assumption_one_way))
      ? `${(Number(model.cost_assumption_one_way) * 100).toFixed(2)}% / 单边`
      : "待核验";
    document.querySelector("#detail-skill").textContent = model.skill || "待核验";
    document.querySelector("#detail-validation-note").textContent = model.validation_note || "";
    document.querySelector("#detail-risk-notice").textContent = model.risk_notice || "不保证未来表现。";
    document.querySelector("#detail-use-link").href = `quant-model.html?model=${encodeURIComponent(model.id)}`;
    document.querySelector("#detail-universe").innerHTML = (model.universe || [])
      .map((item) => `<span>${escapeHtml(item)}</span>`)
      .join("");
    const ruleOrder = ["entry", "take_profit", "stop", "reentry", "execution"];
    document.querySelector("#detail-rules").innerHTML = ruleOrder
      .map((key, index) => renderRule(model.rules?.[key], index))
      .join("");
  }

  select.innerHTML = models.length
    ? models.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name || item.id)}</option>`).join("")
    : '<option value="">暂无可用模型</option>';
  select.addEventListener("change", () => {
    const model = modelById(select.value);
    if (!model) return;
    window.history.replaceState(null, "", `?model=${encodeURIComponent(model.id)}`);
    render(model);
  });
  render(modelById(requestedId));
})();

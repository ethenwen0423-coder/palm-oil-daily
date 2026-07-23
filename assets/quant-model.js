(function () {
  const dataset = window.QUANT_MODEL_SIGNALS || {};
  const models = Array.isArray(dataset.models) && dataset.models.length
    ? dataset.models.filter((item) => item.status === "active")
    : dataset.model ? [dataset.model] : [];
  const requestedModelId = new URLSearchParams(window.location.search).get("model");
  let activeModelId = requestedModelId || dataset.default_model_id || models[0]?.id || "";
  let contracts = [];
  const form = document.querySelector("#quant-form");
  const modelSelect = document.querySelector("#model-select");
  const modelStatus = document.querySelector("#model-status");
  const modelDetailLink = document.querySelector("#model-detail-link");
  const activeModelName = document.querySelector("#active-model-name");
  const activeModelSummary = document.querySelector("#active-model-summary");
  const activeModelDetailLink = document.querySelector("#active-model-detail-link");
  const contractSelect = document.querySelector("#contract-select");
  const contractScope = document.querySelector("#contract-scope");
  const entryPrice = document.querySelector("#entry-price");
  const entryRequired = document.querySelector("#entry-required");
  const formError = document.querySelector("#form-error");
  const resultSection = document.querySelector("#quant-result-section");
  const marketUpdated = document.querySelector("#quant-market-updated");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatNumber(value, digits = 2) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "--";
    return number.toLocaleString("zh-CN", { maximumFractionDigits: digits });
  }

  function formatDateTime(value) {
    if (!value) return "待更新";
    const normalized = String(value).includes("T") ? String(value) : String(value).replace(" ", "T") + ":00+08:00";
    const date = new Date(normalized);
    if (!Number.isFinite(date.getTime())) return String(value);
    return date.toLocaleString("zh-CN", { hour12: false });
  }

  function marketSessionLabel(session) {
    return {
      morning: "早盘",
      midday: "午盘",
      close: "收盘",
    }[session] || "行情";
  }

  function quoteChangeClass(change) {
    const value = Number.parseFloat(String(change || "").replace("%", ""));
    if (!Number.isFinite(value) || value === 0) return "";
    return value > 0 ? "positive" : "negative";
  }

  function selectedPosition() {
    return form.querySelector('input[name="position"]:checked')?.value || "flat";
  }

  function currentModel() {
    return models.find((item) => item.id === activeModelId) || models[0] || dataset.model || {};
  }

  function contractsForModel(modelId) {
    const grouped = dataset.model_contracts || {};
    const selected = grouped[modelId];
    return Array.isArray(selected)
      ? selected
      : modelId === (dataset.model?.id || activeModelId) && Array.isArray(dataset.contracts)
        ? dataset.contracts
        : [];
  }

  function actionText(action) {
    const labels = {
      OPEN_LONG: "做多",
      OPEN_SHORT: "做空",
      HOLD_LONG: "持有多单",
      HOLD_LONG_DATA_NEEDED: "持有多单",
      HOLD_SHORT: "持有空单",
      TAKE_PROFIT_EXIT_LONG: "全部止盈多单",
      TAKE_PROFIT_EXIT_SHORT: "全部止盈空单",
      STOP_EXIT_LONG: "全部止损多单",
      STOP_EXIT_SHORT: "全部止损空单",
      MISSED_ENTRY_SIGNAL: "观望，不追单",
      EXIT_SIGNAL_OVERDUE: "离场信号已过执行窗口",
      WAIT: "观望",
    };
    return labels[action] || "数据不足";
  }

  function actionTone(action) {
    if (/EXIT|STOP|OVERDUE/.test(action)) return "risk";
    if (/OPEN|HOLD/.test(action)) return "active";
    return "neutral";
  }

  function rationaleText(signal) {
    const map = {
      "completed close crossed above MA20": "最新完整日线收盘上穿 MA20",
      "completed close crossed below MA20": "最新完整日线收盘下穿 MA20",
      "no new MA20 crossover": "最新完整日线未出现新的 MA20 穿越",
      "price made a 20-day high while RSI failed to confirm": "价格创 20 日新高，RSI 未同步确认",
      "price made a 20-day low while RSI failed to confirm": "价格创 20 日新低，RSI 未同步确认",
      "short stop triggered: completed close above MA6": "空单止损触发：完整日线收于 MA6 上方",
      "short stop and bullish divergence not triggered": "空单 MA6 止损与 RSI 看涨背离均未触发",
      "long ATR activation cannot be evaluated from the supplied position data": "仅凭入场价无法还原多单 0.75 ATR 激活过程，但 RSI 背离止盈仍已独立检查",
      "the strategy's next-open entry window has already passed; do not chase": "该信号的次日开盘执行窗口已过，不追单",
      "the strategy's next-open exit window has passed; risk-control exit is overdue": "模型离场窗口已过，应在下一可用机会处理风险",
    };
    return (signal.rationale || []).map((item) => map[item] || item).join("；") || "需进一步核验";
  }

  function executionText(signal) {
    const labels = {
      next_trading_day_open: "次交易日开盘",
      wait_for_next_confirmed_signal: "等待下一个确认信号",
      next_available_market_opportunity: "下一可用交易时点",
      none: "无新增执行动作",
    };
    return labels[signal.execution] || "需进一步核验";
  }

  function stopText(signal, position) {
    const state = signal.stop_state || {};
    if (position === "flat") return "未持仓，当前无止损计算。";
    if (position === "short") {
      return state.close_above_ma6
        ? `已触发：收盘价上破 MA6 ${formatNumber(state.ma6)}。`
        : `未触发：收盘价仍未上破 MA6 ${formatNumber(state.ma6)}。`;
    }
    if (state.evaluated === false) {
      return `待完整核验：多单止损需入场日期以确认 0.75 ATR 是否激活；本页已完成可独立判定的 RSI 止盈检查。`;
    }
    return state.armed
      ? `已激活：当前连续 ${state.consecutive_closes_below_ma6 || 0} 日收于 MA6 下。`
      : "0.75 ATR 保护尚未激活。";
  }

  function takeProfitText(signal, position) {
    if (position === "flat") return "开仓后按 20 日价格/RSI 背离全部止盈。";
    if (/TAKE_PROFIT/.test(signal.action)) return "背离已触发，模型指令为全部止盈。";
    return position === "long"
      ? "未触发看跌背离：等待价格创 20 日新高但 RSI 不确认。"
      : "未触发看涨背离：等待价格创 20 日新低但 RSI 不确认。";
  }

  function positionPerformance(close, price, position) {
    if (position === "flat") return null;
    const direction = position === "long" ? 1 : -1;
    const points = (close - price) * direction;
    const percent = price ? (points / price) * 100 : 0;
    return { points, percent };
  }

  function renderResult(contract, position, price) {
    const signal = contract.signals?.[position];
    if (!signal || signal.status !== "ok") {
      resultSection.innerHTML = `<div class="quant-result-error"><strong>数据不足</strong><p>${escapeHtml(signal?.message || contract.message || "所选合约暂无可用模型结果。")}</p></div>`;
      return;
    }

    const market = signal.market || contract.market || {};
    const quote = contract.current_quote || {};
    const quotePrice = Number(quote.price);
    const performancePrice = Number.isFinite(quotePrice) ? quotePrice : Number(market.close);
    const performance = positionPerformance(performancePrice, price, position);
    const generated = formatDateTime(dataset.generated_at);
    const quoteUpdated = formatDateTime(dataset.market_updated_at);
    const overdue = signal.execution_window === "missed";
    const model = currentModel();
    resultSection.innerHTML = `
      <article class="quant-result-card ${actionTone(signal.action)}">
        <header class="quant-result-header">
          <div>
            <span class="quant-scope ${contract.model_scope === "rule_trial" ? "trial" : ""}">${escapeHtml(contract.model_scope_label)}</span>
            <p>${escapeHtml(contract.product_name)} ${escapeHtml(contract.symbol)} · ${escapeHtml(contract.label)}</p>
            <h2>${escapeHtml(actionText(signal.action))}</h2>
          </div>
          <div class="quant-result-date">
            <span>模型行情日</span>
            <strong>${escapeHtml(contract.market_date || "待更新")}</strong>
            <small>${contract.bar_completed ? "完整日线" : "当日线未完成"}</small>
          </div>
        </header>

        ${overdue ? '<div class="quant-alert">该模型信号的标准执行窗口已过，请严格遵守不追单/及时风控规则。</div>' : ""}
        ${contract.model_scope === "rule_trial" ? '<div class="quant-alert scope">所选品种沿用相同模型规则试算；成熟回测范围为 P0 棕榈油主力连续合约。</div>' : ""}

        <div class="quant-live-quote">
          <div>
            <span>当前行情</span>
            <strong>${formatNumber(quote.price)}</strong>
            <em class="${quoteChangeClass(quote.change)}">${escapeHtml(quote.change || "--")}</em>
          </div>
          <p>${escapeHtml(quote.trade_date || "交易日待更新")} · ${escapeHtml(marketSessionLabel(dataset.market_update_session))}更新于 ${escapeHtml(quoteUpdated)}</p>
          <small>模型指令仍按 ${escapeHtml(contract.market_date || "最近交易日")} 完整日线计算，不使用盘中价格重算信号。</small>
        </div>

        <div class="quant-metrics">
          <div><span>模型收盘</span><strong>${formatNumber(market.close)}</strong></div>
          <div><span>MA20</span><strong>${formatNumber(market.ma20)}</strong></div>
          <div><span>MA6</span><strong>${formatNumber(market.ma6)}</strong></div>
          <div><span>RSI14</span><strong>${formatNumber(market.rsi14, 1)}</strong></div>
          <div><span>ATR14</span><strong>${formatNumber(market.atr14)}</strong></div>
          ${performance ? `<div class="${performance.points >= 0 ? "positive" : "negative"}"><span>${Number.isFinite(quotePrice) ? "盘中持仓浮动" : "持仓浮动"}</span><strong>${performance.points >= 0 ? "+" : ""}${formatNumber(performance.points)} <small>(${performance.percent >= 0 ? "+" : ""}${formatNumber(performance.percent)}%)</small></strong></div>` : ""}
        </div>

        <div class="quant-decision-grid">
          <section><span>执行时间</span><strong>${escapeHtml(executionText(signal))}</strong><p>${signal.intended_execution_date ? `模型执行日：${escapeHtml(signal.intended_execution_date)}` : "无新增交易动作时继续观察。"}</p></section>
          <section><span>模型依据</span><strong>${escapeHtml(rationaleText(signal))}</strong><p>收盘 ${formatNumber(market.close)} · MA20 ${formatNumber(market.ma20)} · RSI14 ${formatNumber(market.rsi14, 1)}</p></section>
          <section><span>止盈条件</span><strong>${escapeHtml(takeProfitText(signal, position))}</strong><p>背离信号只使用完整日线确认。</p></section>
          <section><span>止损状态</span><strong>${escapeHtml(stopText(signal, position))}</strong><p>止损后锁定原方向，直到出现反向 MA20 穿越。</p></section>
        </div>

        <footer class="quant-result-footer">
          <p><strong>模型</strong> ${escapeHtml(model.name || "待核验")} · <a href="quant-model-detail.html?model=${encodeURIComponent(model.id || "")}">查看策略详情</a></p>
          <p><strong>数据来源</strong> ${escapeHtml(contract.data_source || signal.data_source || "AkShare 国内期货日线")} · 标的：${escapeHtml(contract.symbol)} · 模型 skill：${escapeHtml(model.skill || "generate-oilseed-trade-signal")}</p>
          <p><strong>行情更新</strong> ${escapeHtml(quoteUpdated)} · <strong>模型生成</strong> ${escapeHtml(generated)} · 回测单边成本假设 0.04%</p>
          <p>本结果为策略信号，不保证未来表现，不构成个人化投资建议。</p>
        </footer>
      </article>`;
    resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function populateContracts() {
    const available = contracts.filter((item) => item.signals);
    if (!available.length) {
      contractSelect.innerHTML = '<option value="">暂无可用合约</option>';
      contractSelect.disabled = true;
      return;
    }
    contractSelect.innerHTML = '<option value="">请选择合约</option>' + available
      .map((item) => `<option value="${escapeHtml(item.symbol)}">${escapeHtml(item.product_name)} ${escapeHtml(item.symbol)}（${escapeHtml(item.label)}）</option>`)
      .join("");
  }

  function emptyResult() {
    resultSection.innerHTML = `
      <div class="quant-result-empty">
        <span>02</span>
        <strong>等待生成量化建议</strong>
        <p>完成上方输入后，这里将展示所选模型的当前指令、执行时间、止盈止损与模型依据。</p>
      </div>`;
  }

  function activateModel(modelId, resetResult = true) {
    const model = models.find((item) => item.id === modelId) || models[0];
    if (!model) return;
    activeModelId = model.id;
    contracts = contractsForModel(activeModelId);
    modelSelect.value = activeModelId;
    activeModelName.textContent = model.short_name || model.name || "未命名模型";
    activeModelSummary.textContent = model.summary || "策略说明待补充";
    modelStatus.textContent = `${model.status_label || "已启用"} · ${model.timeframe || "周期待核验"} · v${model.version || "1.0"}`;
    const detailHref = `quant-model-detail.html?model=${encodeURIComponent(activeModelId)}`;
    modelDetailLink.href = detailHref;
    activeModelDetailLink.href = detailHref;
    populateContracts();
    contractScope.textContent = "主力与次主力合约";
    if (resetResult) emptyResult();
  }

  function populateModels() {
    if (!models.length) {
      modelSelect.innerHTML = '<option value="">暂无已启用模型</option>';
      modelSelect.disabled = true;
      contractSelect.disabled = true;
      formError.textContent = "量化模型数据不足。";
      return;
    }
    modelSelect.innerHTML = models
      .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name || item.id)}</option>`)
      .join("");
    activateModel(activeModelId, false);
  }

  function updatePositionInput() {
    const position = selectedPosition();
    const needsEntry = position !== "flat";
    entryPrice.disabled = !needsEntry;
    entryPrice.required = needsEntry;
    entryRequired.textContent = needsEntry ? "必填" : "未开仓时无需填写";
    if (!needsEntry) entryPrice.value = "";
  }

  form.addEventListener("change", (event) => {
    if (event.target === modelSelect) activateModel(modelSelect.value);
    if (event.target.name === "position") updatePositionInput();
    if (event.target === contractSelect) {
      const contract = contracts.find((item) => item.symbol === contractSelect.value);
      contractScope.textContent = contract
        ? `${contract.model_scope_label}：${contract.product_name} ${contract.label}`
        : "主力与次主力合约";
    }
    formError.textContent = "";
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const contract = contracts.find((item) => item.symbol === contractSelect.value);
    const position = selectedPosition();
    const price = Number(entryPrice.value);
    if (!contract) {
      formError.textContent = "请先选择合约。";
      return;
    }
    if (position !== "flat" && (!Number.isFinite(price) || price <= 0)) {
      formError.textContent = "请输入有效的入场点位。";
      entryPrice.focus();
      return;
    }
    formError.textContent = "";
    renderResult(contract, position, price);
  });

  populateModels();
  updatePositionInput();
  if (marketUpdated) {
    marketUpdated.textContent = dataset.market_updated_at
      ? `${marketSessionLabel(dataset.market_update_session)}行情更新：${formatDateTime(dataset.market_updated_at)}`
      : "当前行情待更新";
  }
})();

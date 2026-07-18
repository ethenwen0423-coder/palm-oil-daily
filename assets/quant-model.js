(function () {
  const dataset = window.QUANT_MODEL_SIGNALS || {};
  const contracts = Array.isArray(dataset.contracts) ? dataset.contracts : [];
  const form = document.querySelector("#quant-form");
  const contractSelect = document.querySelector("#contract-select");
  const contractScope = document.querySelector("#contract-scope");
  const entryPrice = document.querySelector("#entry-price");
  const entryRequired = document.querySelector("#entry-required");
  const formError = document.querySelector("#form-error");
  const resultSection = document.querySelector("#quant-result-section");

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

  function selectedPosition() {
    return form.querySelector('input[name="position"]:checked')?.value || "flat";
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
    const performance = positionPerformance(Number(market.close), price, position);
    const generated = dataset.generated_at ? new Date(dataset.generated_at).toLocaleString("zh-CN", { hour12: false }) : "待更新";
    const overdue = signal.execution_window === "missed";
    resultSection.innerHTML = `
      <article class="quant-result-card ${actionTone(signal.action)}">
        <header class="quant-result-header">
          <div>
            <span class="quant-scope ${contract.model_scope === "rule_trial" ? "trial" : ""}">${escapeHtml(contract.model_scope_label)}</span>
            <p>${escapeHtml(contract.product_name)} ${escapeHtml(contract.symbol)} · ${escapeHtml(contract.label)}</p>
            <h2>${escapeHtml(actionText(signal.action))}</h2>
          </div>
          <div class="quant-result-date">
            <span>行情日期</span>
            <strong>${escapeHtml(contract.market_date || "待更新")}</strong>
            <small>${contract.bar_completed ? "完整日线" : "当日线未完成"}</small>
          </div>
        </header>

        ${overdue ? '<div class="quant-alert">该模型信号的标准执行窗口已过，请严格遵守不追单/及时风控规则。</div>' : ""}
        ${contract.model_scope === "rule_trial" ? '<div class="quant-alert scope">所选品种沿用相同模型规则试算；成熟回测范围为 P0 棕榈油主力连续合约。</div>' : ""}

        <div class="quant-metrics">
          <div><span>最新收盘</span><strong>${formatNumber(market.close)}</strong></div>
          <div><span>MA20</span><strong>${formatNumber(market.ma20)}</strong></div>
          <div><span>MA6</span><strong>${formatNumber(market.ma6)}</strong></div>
          <div><span>RSI14</span><strong>${formatNumber(market.rsi14, 1)}</strong></div>
          <div><span>ATR14</span><strong>${formatNumber(market.atr14)}</strong></div>
          ${performance ? `<div class="${performance.points >= 0 ? "positive" : "negative"}"><span>持仓浮动</span><strong>${performance.points >= 0 ? "+" : ""}${formatNumber(performance.points)} <small>(${performance.percent >= 0 ? "+" : ""}${formatNumber(performance.percent)}%)</small></strong></div>` : ""}
        </div>

        <div class="quant-decision-grid">
          <section><span>执行时间</span><strong>${escapeHtml(executionText(signal))}</strong><p>${signal.intended_execution_date ? `模型执行日：${escapeHtml(signal.intended_execution_date)}` : "无新增交易动作时继续观察。"}</p></section>
          <section><span>模型依据</span><strong>${escapeHtml(rationaleText(signal))}</strong><p>收盘 ${formatNumber(market.close)} · MA20 ${formatNumber(market.ma20)} · RSI14 ${formatNumber(market.rsi14, 1)}</p></section>
          <section><span>止盈条件</span><strong>${escapeHtml(takeProfitText(signal, position))}</strong><p>背离信号只使用完整日线确认。</p></section>
          <section><span>止损状态</span><strong>${escapeHtml(stopText(signal, position))}</strong><p>止损后锁定原方向，直到出现反向 MA20 穿越。</p></section>
        </div>

        <footer class="quant-result-footer">
          <p><strong>数据来源</strong> ${escapeHtml(contract.data_source || signal.data_source || "AkShare 国内期货日线")} · 标的：${escapeHtml(contract.symbol)} · 模型 skill：${escapeHtml(dataset.model?.skill || "generate-oilseed-trade-signal")}</p>
          <p><strong>更新时间</strong> ${escapeHtml(generated)} · 回测单边成本假设 0.04%</p>
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

  function updatePositionInput() {
    const position = selectedPosition();
    const needsEntry = position !== "flat";
    entryPrice.disabled = !needsEntry;
    entryPrice.required = needsEntry;
    entryRequired.textContent = needsEntry ? "必填" : "未开仓时无需填写";
    if (!needsEntry) entryPrice.value = "";
  }

  form.addEventListener("change", (event) => {
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

  populateContracts();
  updatePositionInput();
})();

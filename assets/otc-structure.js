(function () {
  const dataset = window.OIL_FUTURES_CONTRACTS || {};
  const contracts = Array.isArray(dataset.contracts) ? dataset.contracts : [];
  const form = document.querySelector("#otc-form");
  const contractSelect = document.querySelector("#otc-contract");
  const cadenceSelect = document.querySelector("#otc-cadence");
  const familySelect = document.querySelector("#otc-family");
  const phoenixSuitability = document.querySelector("#otc-phoenix-suitability");
  const r5Confirm = document.querySelector("#otc-r5-confirm");
  const contractNote = document.querySelector("#otc-contract-note");
  const dataDate = document.querySelector("#otc-data-date");
  const dataSource = document.querySelector("#otc-data-source");
  const formError = document.querySelector("#otc-form-error");
  const result = document.querySelector("#otc-result");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function number(value) {
    const parsed = Number(String(value ?? "").replaceAll(",", ""));
    return Number.isFinite(parsed) ? parsed : null;
  }

  function format(value, digits = 0) {
    const parsed = number(value);
    if (parsed === null) return "需进一步核验";
    return parsed.toLocaleString("zh-CN", { maximumFractionDigits: digits });
  }

  function textOf(contract, sectionIndex) {
    return String(contract.technical_detail?.[sectionIndex]?.text || "");
  }

  function capture(text, pattern) {
    const match = String(text).match(pattern);
    return match ? number(match[1]) : null;
  }

  function tradingIncrement(contract) {
    return ["M", "RM"].includes(String(contract.product || "").toUpperCase()) ? 5 : 10;
  }

  function roundStrike(value, contract) {
    if (!Number.isFinite(value)) return null;
    const increment = tradingIncrement(contract);
    return Math.round(value / increment) * increment;
  }

  function unique(values) {
    return [...new Set(values.filter(Number.isFinite))];
  }

  function technicalSnapshot(contract) {
    const price = number(contract.price);
    const trend = textOf(contract, 0);
    const levels = textOf(contract, 1);
    const volatility = textOf(contract, 2);
    const ma20 = capture(trend, /MA20\s*([\d,.]+)/i);
    const ma60 = capture(trend, /MA60\s*([\d,.]+)/i);
    const rangeHigh = capture(levels, /区间上沿\s*([\d,.]+)/);
    const rangeLow = capture(levels, /下沿\s*([\d,.]+)/);
    const channelHigh = capture(levels, /通道上轨\s*([\d,.]+)/);
    const channelLow = capture(levels, /通道下轨\s*([\d,.]+)/);
    const atr = capture(volatility, /波动幅度约\s*([\d,.]+)/) || (price ? price * 0.02 : null);
    const upperWatch = number(contract.strategy_recommendation?.upper_watch);
    const lowerWatch = number(contract.strategy_recommendation?.lower_watch);
    const candidates = unique([ma20, ma60, rangeHigh, rangeLow, channelHigh, channelLow, upperWatch, lowerWatch]);
    const below = candidates.filter((item) => item < price).sort((a, b) => b - a);
    const above = candidates.filter((item) => item > price).sort((a, b) => a - b);
    let support1 = below[0] || price - atr;
    let support2 = below.find((item) => item < support1 - atr * 0.35) || lowerWatch || price - atr * 2;
    let resistance1 = above[0] || price + atr;
    let resistance2 = above.find((item) => item > resistance1 + atr * 0.35) || upperWatch || price + atr * 2;
    support1 = roundStrike(support1, contract);
    support2 = roundStrike(Math.min(support2, support1 - tradingIncrement(contract)), contract);
    resistance1 = roundStrike(resistance1, contract);
    resistance2 = roundStrike(Math.max(resistance2, resistance1 + tradingIncrement(contract)), contract);
    return { price, atm: roundStrike(price, contract), ma20, ma60, atr, support1, support2, resistance1, resistance2 };
  }

  function directionOf(contract) {
    const stance = String(contract.score?.stance || "");
    if (/偏强|偏多|看多|多头/.test(stance)) return "bullish";
    if (/偏弱|偏空|看空|空头/.test(stance)) return "bearish";
    return "neutral";
  }

  function ageInDays(dateText) {
    const match = String(dateText || "").match(/(\d{4})-(\d{2})-(\d{2})/);
    if (!match) return null;
    const marketDate = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    return Math.floor((today - marketDate) / 86400000);
  }

  function selected(name) {
    return form.querySelector(`input[name="${name}"]:checked`)?.value || "";
  }

  function parameter(label, name, value, note) {
    return { label, name, value, note };
  }

  function resetResult(message) {
    result.innerHTML = `
      <div class="otc-result-empty">
        <span>02</span>
        <strong>当前条件未生成建议</strong>
        <p>${escapeHtml(message)}</p>
      </div>`;
  }

  function recommendation(contract, objective, cost, cadence, family, technical) {
    const direction = directionOf(contract);
    const stance = contract.score?.stance || "需进一步核验";
    const confidence = contract.score?.view_confidence || "需进一步核验";
    const lowConfidence = confidence === "低" || /分歧/.test(stance);
    const phoenix = family === "phoenix";
    const downgraded = lowConfidence && (cost === "leveraged" || (phoenix && cost !== "one_x"));
    const appliedCost = downgraded ? "one_x" : cost;
    const catalogueAdjusted = !phoenix && objective === "inventory" && cadence === "daily" && appliedCost === "leveraged";
    const p = technical;
    let name = "";
    let structureType = "";
    let sourcePage = "";
    let settlement = "";
    let summary = "";
    let tradeoff = "";
    let risk = "";
    let parameters = [];
    let blocked = false;

    if (phoenix) {
      const isBuy = objective === "procurement";
      const phoenixDirection = isBuy ? "累购" : "累沽";
      const knockIn = isBuy ? p.support1 : p.resistance1;
      const knockOut = isBuy ? p.resistance1 : p.support1;
      const isEnhanced = appliedCost === "leveraged";
      const variant = appliedCost === "one_x" ? "1.0" : appliedCost === "bounded" ? "2.0" : (direction === "neutral" ? "4.0" : "3.0");
      const allQuantity = variant === "2.0";
      const leverage = isEnhanced ? "2 倍" : "1 倍";
      const quantity = allQuantity ? "全部观察期数量" : "敲入时剩余数量";
      const knockOutPayoff = variant === "3.0" ? "线性增强收益" : variant === "4.0" ? "固定增强收益" : "无额外收益";
      name = `凤凰${phoenixDirection}${variant}`;
      structureType = `${leverage}凤凰累计 · 敲入价建仓 · ${quantity}`;
      sourcePage = "凤凰累计结构定义（2025-02-27）";
      settlement = "每日观察；敲入或敲出后产品立即终止";
      summary = isBuy
        ? `用于真实逐日采购：区间内累计票息，下方敲入后一次性形成${quantity}的远期多头，上方敲出后终止。`
        : `用于真实逐日销售或库存管理：区间内累计票息，上方敲入后一次性形成${quantity}的远期空头，下方敲出后终止。`;
      tradeoff = variant === "1.0"
        ? "选择剩余数量、1 倍参与和敲入价建仓，属于凤凰系列中相对较低风险组合；代价是区间票息通常较低。"
        : variant === "2.0"
          ? "1 倍参与但敲入覆盖全部观察期数量，区间票息可能更高；敲入时的集中远期头寸也更大。"
          : `${leverage}参与并在敲出端提供${knockOutPayoff}；只采用剩余数量和敲入价建仓，不自动使用风险更高的 5.0/6.0。`;
      risk = `该结构为 R5 高风险产品，可能承担无限风险敞口；敲入会集中形成${quantity}的${isBuy ? "多头" : "空头"}远期头寸，需准备保证金并以现货流量承接。`;
      parameters = [
        parameter("01", "入场参考", p.atm, "按当前价取整，仅作为询价锚点"),
        parameter("02", "敲入障碍", knockIn, `${isBuy ? "下方" : "上方"}技术位；触发后结构终止并形成远期头寸`),
        parameter("03", "敲出障碍", knockOut, `${isBuy ? "上方" : "下方"}技术位；触发后结构终止`),
        parameter("04", "敲入建仓", `${leverage} · 敲入价`, `${quantity}；不采用等间隔建仓`),
        parameter("05", "敲出收益", knockOutPayoff, "票息、增强参与率和保证金均需重新询价"),
        parameter("06", "建议观察", "30 个交易日 · 每日", "每日名义数量必须匹配真实采购或销售计划"),
      ];
    } else if (cadence === "spread") {
      name = "价差宝 / 月差宝（待补数据）";
      structureType = "跨品种或跨期价差期权";
      sourcePage = "19-22";
      settlement = "到期结算";
      summary = "附件要求先定义价差配比、方向与执行价；当前页面只有单合约行情，不能可靠推导价差点位。";
      tradeoff = "补齐两腿历史序列、相关性、期限匹配和流动性后，才可判断卖看涨或卖看跌。";
      risk = "价差方向错误时可能产生线性亏损，跨品种价差还存在相关性和流动性突变。";
      blocked = true;
      parameters = [
        parameter("01", "价差标的", "需进一步核验", "例如 OI-Y、近月-远月；必须先确定吨数配比"),
        parameter("02", "当前价差", "需进一步核验", "不能用两个单腿技术位直接相减代替"),
        parameter("03", "方向", "需进一步核验", "加工费保值、建仓或移仓对应的方向不同"),
        parameter("04", "期限", "20-30 个交易日", "附件示例期限，当前仍需重新询价"),
      ];
    } else if (objective === "procurement" && cadence === "daily") {
      if (appliedCost === "one_x") {
        name = direction === "bullish" ? "累进宝4.0 Plus" : "累进宝3.0";
        structureType = direction === "bullish" ? "线性熔断累计 Plus" : "线性累计";
        sourcePage = direction === "bullish" ? "10" : "3";
        settlement = "每日观察、逐日结算";
        summary = direction === "bullish"
          ? "适合每日采购且希望大涨时获得线性补贴并提前结束；下方仅按 1 倍承接采购。"
          : "适合每日有真实采购计划、希望震荡区间内线性降低成本，并在支撑位按 1 倍采购。";
        tradeoff = direction === "bullish" ? "熔断后产品提前结束；最后一日下破下方价可能形成全部剩余数量多单。" : "涨破上沿后当日无收益，无法提供足额大涨保护。";
        risk = "跌破下方价会产生期权亏损或按下方价建立多单，必须由真实采购流量承接。";
      } else if (appliedCost === "bounded") {
        name = "累进宝1.0";
        structureType = "固定赔付累计（带敲出）";
        sourcePage = "1";
        settlement = "每日观察、逐日结算";
        summary = "适合宽幅震荡中的每日采购：区间内拿固定补贴，下方按 1 倍低位采购，上方当日无损益。";
        tradeoff = "固定补贴需正式询价；大涨超过上沿时没有进一步采购保护。";
        risk = "跌破下方价会产生现金亏损或形成多单，并可能触发保证金追加。";
      } else {
        name = direction === "bullish" ? "累进宝3.0 Plus" : "累进宝1.0 Plus";
        structureType = direction === "bullish" ? "增强线性累计" : "增强固定赔付累计";
        sourcePage = direction === "bullish" ? "9" : "7";
        settlement = "每日观察、逐日结算";
        summary = "区间内获得补贴，大涨获得线性补贴；下破下方价时按附件示例形成 2 倍多单。";
        tradeoff = "上行保护更强，但以下方 2 倍采购义务交换，不能脱离现货采购能力使用。";
        risk = "大跌时产生 2 倍亏损或 2 倍多单，并可能显著追保。";
      }
      parameters = [
        parameter("01", "入场参考", p.price, "当前期货价，仅作为结构锚点"),
        parameter("02", "下方价", p.support1, "近端技术支撑；下破后可能产生多单或亏损"),
        parameter("03", "上方价", p.resistance2, "远端压力位；决定补贴封顶或熔断位置"),
        parameter("04", "建议观察", "20 个交易日 · 每日", "沿用附件示例期限，正式期限需结合采购计划"),
      ];
    } else if (objective === "procurement") {
      if (appliedCost === "one_x") {
        name = "采省易1.0";
        structureType = "领式看涨";
        sourcePage = "14";
        settlement = "到期结算";
        summary = "适合担心大涨、但愿意在支撑位采购的企业；上涨超过上方价获得完整保护，下方按 1 倍低价采购。";
        tradeoff = "零权利金来自让渡下方继续下跌后的低价采购收益。";
        risk = "跌破下方价会产生现金亏损或形成 1 倍多单，并可能追保。";
      } else if (appliedCost === "bounded") {
        name = "采省易3.0";
        structureType = "海鸥看涨";
        sourcePage = "16";
        settlement = "到期结算";
        summary = "适合震荡向上、希望低成本保护一段上涨区间并在下方 1 倍采购。";
        tradeoff = "上涨保护有最大额度；超过上方保护区间后不再增加补偿。";
        risk = "跌破下方价会让渡更低现货采购收益，大涨时保护程度有限。";
      } else {
        name = "采省易2.0";
        structureType = "比例领式看涨";
        sourcePage = "15";
        settlement = "到期结算";
        summary = "上涨从入场价开始完整保护，下跌有安全垫；跌破下方价按附件示例形成 2 倍多单。";
        tradeoff = "以 2 倍低位采购义务交换零权利金和完整上涨保护。";
        risk = "低于下方价时产生 2 倍亏损或 2 倍多单，仅适合有足量采购能力的用户。";
      }
      parameters = [
        parameter("01", "入场参考", p.price, "当前期货价，仅作为结构锚点"),
        parameter("02", "下方履约价", p.support1, "技术支撑；对应低位采购或现金结算"),
        parameter("03", appliedCost === "leveraged" ? "上涨保护起点" : "上方保护价", appliedCost === "leveraged" ? p.atm : p.resistance2, appliedCost === "bounded" ? "海鸥结构的保护上限需结合报价确定" : "上破后开始获得采购保护"),
        parameter("04", "建议期限", "20 个交易日", "沿用附件示例，需匹配实际采购日期"),
      ];
    } else if (objective === "inventory" && cadence === "daily") {
      if (appliedCost === "one_x") {
        name = "惠鑫保1.0";
        structureType = "香草累计（客户买入累沽）";
        sourcePage = "23";
        settlement = "每日观察、期初支付权利金";
        summary = "适合持续销售并希望每日完整获得执行价以下跌幅保护，同时保留现货上涨收益。";
        tradeoff = "需要期初支付总权利金；高于执行价时每日损失对应权利金。";
        risk = "不追保、最大期权损失为已付权利金，但提前平仓会损耗剩余权利金。";
        parameters = [
          parameter("01", "执行价参考", p.atm, "接近当前价；正式权利金需询价"),
          parameter("02", "盈亏平衡", "需询权利金", "执行价减去单日权利金"),
          parameter("03", "每日数量", "匹配销售计划", "每日数量之和不得超过可销售现货"),
          parameter("04", "建议观察", "15-20 个交易日 · 每日", "按实际销售日历设置"),
        ];
      } else {
        name = "惠鑫保2.0";
        structureType = "鲨鱼鳍累计（客户买入累沽）";
        sourcePage = "24-25";
        settlement = "每日观察、期初支付权利金";
        summary = "适合震荡偏弱中的短周期库存套保：区间内获得下跌保护，跌破障碍后提前结束并退还未观察权利金。";
        tradeoff = "权利金较低，但真正大跌跌破障碍后，剩余库存将失去保护。";
        risk = "障碍触发后的后续现货跌幅完全暴露，必须预先准备替代套保方案。";
        parameters = [
          parameter("01", "执行价参考", p.atm, "接近当前价，区间内逐日保护"),
          parameter("02", "障碍价参考", p.support2, "远端支撑；跌破后产品提前终止"),
          parameter("03", "权利金", "需正式询价", "附件历史示例不得沿用"),
          parameter("04", "建议观察", "15 个交易日 · 每日", "短周期使用，需准备障碍触发后的替代策略"),
        ];
      }
    } else if (objective === "inventory") {
      if (appliedCost === "one_x") {
        name = "期现易1.0";
        structureType = "领式看跌";
        sourcePage = "11";
        settlement = "到期结算";
        summary = "适合担心库存大跌、同时愿意在压力位高价销售或开 1 倍空单的企业。";
        tradeoff = "下方特定点位以下完整保护，但上涨超过上方价后让渡现货收益。";
        risk = "持续大涨会形成亏损或空单，并可能追加保证金。";
      } else if (appliedCost === "bounded") {
        name = "期现易3.0";
        structureType = "海鸥看跌";
        sourcePage = "13";
        settlement = "到期结算";
        summary = "适合震荡向下、希望零成本保护一段跌幅并在上方 1 倍高位销售。";
        tradeoff = "下跌保护有最大额度；深跌时套保效果减弱。";
        risk = "涨破上方价会让渡现货上涨收益；深跌超过保护区间后重新暴露。";
      } else {
        name = "期现易2.0";
        structureType = "比例领式看跌";
        sourcePage = "12";
        settlement = "到期结算";
        summary = "下跌从入场价开始完整保护，上涨至上方价后按附件示例形成 2 倍空单。";
        tradeoff = "以 2 倍高位销售义务交换零权利金和完整下跌保护。";
        risk = "大涨时产生 2 倍亏损或 2 倍空单，仅适合有足量现货可销售的用户。";
      }
      parameters = [
        parameter("01", "入场参考", p.price, "当前期货价，仅作为结构锚点"),
        parameter("02", appliedCost === "leveraged" ? "下跌保护起点" : "下方保护价", appliedCost === "leveraged" ? p.atm : p.support1, appliedCost === "bounded" ? "海鸥结构最大保护额需结合报价确定" : "下破后开始保护库存价值"),
        parameter("03", "上方履约价", p.resistance2, "远端压力；对应销售或空单点位"),
        parameter("04", "建议期限", "20 个交易日", "沿用附件示例，需匹配实际销售日期"),
      ];
    } else {
      const useAirbag = direction === "bullish" && !lowConfidence && appliedCost !== "one_x";
      name = useAirbag ? "气囊宝" : "惠增收";
      structureType = useAirbag ? "安全气囊（正向）" : "反比例领式看涨";
      sourcePage = useAirbag ? "18" : "17";
      settlement = useAirbag ? "到期结算、观察障碍" : "每日观察、逐日结算";
      summary = useAirbag
        ? "适合筑底偏强阶段，希望参与上涨但在障碍未触发时保留下跌安全垫。"
        : "适合已有现货库存、预期震荡或小幅反弹：下跌期权端不亏，小涨增强，大涨在更高价套保。";
      tradeoff = useAirbag ? "一旦观察期内触碰下方障碍，产品转为 100% 期货多头损益。" : "不是完整库存套保；下跌风险仍由现货承担，大涨超过盈亏平衡点后产生期权亏损。";
      risk = useAirbag ? "障碍具有路径依赖，触碰后安全垫失效，并可能追保。" : "必须匹配现货多头；无现货时该结构可能变成方向性风险敞口。";
      parameters = useAirbag ? [
        parameter("01", "入场参考", p.price, "当前期货价"),
        parameter("02", "下方障碍", p.support2, "远端支撑；触碰后转为 100% 多头参与"),
        parameter("03", "未触碰参与率", "需正式询价", "附件示例参与率不可直接沿用"),
        parameter("04", "建议期限", "20 个交易日", "障碍观察方式需写入确认书"),
      ] : [
        parameter("01", "入场参考", p.price, "必须有对应现货库存"),
        parameter("02", "上方价", p.resistance1, "小涨收益开始回落的位置"),
        parameter("03", "盈亏平衡参考", p.resistance2, "大涨后可能形成高位空单"),
        parameter("04", "建议观察", "20 个交易日 · 每日", "每日数量需匹配库存销售节奏"),
      ];
    }

    if (lowConfidence) {
      summary += " 当前观点置信度偏低，点位仅用于多家交易对手询价比较。";
    }
    return { name, structureType, sourcePage, settlement, summary, tradeoff, risk, parameters, direction, stance, confidence, lowConfidence, downgraded, catalogueAdjusted, blocked, phoenix };
  }

  function directionLabel(value) {
    return { bullish: "偏强", bearish: "偏弱", neutral: "震荡/方向不明" }[value] || "需进一步核验";
  }

  function render(contract, objective, cost, cadence, family) {
    const technical = technicalSnapshot(contract);
    const advice = recommendation(contract, objective, cost, cadence, family, technical);
    const age = ageInDays(contract.trade_date || dataset.updated_at);
    const warnings = [];
    warnings.push(advice.phoenix
      ? "凤凰累计只抽象使用结构定义；内部资料的历史报价、权利金和保证金不会在页面展示或用于当前交易。"
      : "产品结构依据附件 2024-10-09 版本；附件历史报价、权利金和保证金不得直接用于当前交易。");
    if (age === null || age > 3) warnings.push("行情时间超过 3 个自然日，所有点位需进一步核验后再询价。");
    if (/未完成|未配置|待核验/.test(String(contract.verification || ""))) warnings.push("行情交叉核验未完成，当前以页面记录的主数据源为准。");
    if (advice.lowConfidence) warnings.push("综合观点为分歧或低置信：累计结构仅限真实产业流量，禁止脱离现货做方向性放大。");
    if (advice.downgraded && !advice.phoenix) warnings.push("因行情低置信，已将“增强型”自动降级为 1 倍产品，不输出 2 倍比例领式或 Plus 累计。");
    if (advice.phoenix) warnings.push("已按 R5 产品处理：必须完成交易对手适当性、压力测试和保证金评估；敲入或敲出后头寸均结束。");
    if (advice.phoenix && advice.downgraded) warnings.push("凤凰结构已降至 1.0；当前低置信行情不自动输出覆盖全部数量的 2.0 或 2 倍的 3.0-6.0。");
    if (advice.catalogueAdjusted) warnings.push("附件未提供 2 倍每日累沽产品；模型按产品库边界改用惠鑫保2.0的障碍降本方案，不虚构杠杆版本。");
    if (advice.blocked) warnings.push("当前缺少价差序列与配比数据，候选产品不等于可执行建议，点位需进一步核验。");
    const updated = dataset.updated_at || contract.trade_date || "需进一步核验";
    const parameters = advice.parameters.map((item) => `
      <article class="otc-leg-card">
        <span>${escapeHtml(item.label)} · 结构参数</span>
        <h3>${escapeHtml(item.name)}</h3>
        <strong>${typeof item.value === "number" ? format(item.value) : escapeHtml(item.value)}</strong>
        <p>${escapeHtml(item.note)}</p>
      </article>`).join("");
    const warningHtml = `<div class="otc-warning"><strong>模型与数据提示</strong><ul>${warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`;
    result.innerHTML = `
      <article class="otc-result-card">
        <header class="otc-result-header">
          <div>
            <span>${escapeHtml(contract.name)} ${escapeHtml(contract.symbol)} · ${advice.phoenix ? escapeHtml(advice.sourcePage) : `附件第 ${escapeHtml(advice.sourcePage)} 页`}</span>
            <h2>${escapeHtml(advice.name)}</h2>
            <p>${escapeHtml(advice.structureType)} · ${escapeHtml(advice.summary)}</p>
          </div>
          <div class="otc-result-date"><span>行情日期</span><strong>${escapeHtml(contract.trade_date || updated)}</strong><small>${escapeHtml(advice.stance)} · 置信度${escapeHtml(advice.confidence)}</small></div>
        </header>

        ${warningHtml}

        <div class="otc-market-grid">
          <div><span>当前价</span><strong>${format(technical.price)}</strong></div>
          <div><span>MA20</span><strong>${format(technical.ma20, 2)}</strong></div>
          <div><span>MA60</span><strong>${format(technical.ma60, 2)}</strong></div>
          <div><span>近端支撑</span><strong>${format(technical.support1)}</strong></div>
          <div><span>近端压力</span><strong>${format(technical.resistance1)}</strong></div>
          <div><span>行情方向</span><strong>${escapeHtml(directionLabel(advice.direction))}</strong></div>
        </div>

        <section class="otc-legs">
          <header><span>产品参数与询价参考</span><p>点位按技术位取整；权利金、赔付额、保证金与参与率必须重新询价。</p></header>
          <div class="otc-leg-grid">${parameters}</div>
        </section>

        <div class="otc-decision-grid">
          <section><span>为什么是这个产品</span><p>${escapeHtml(advice.summary)}</p></section>
          <section><span>核心取舍</span><p>${escapeHtml(advice.tradeoff)}</p></section>
          <section><span>产品特有风险</span><p>${escapeHtml(advice.risk)}</p></section>
          <section><span>结算与询价</span><p>${escapeHtml(advice.settlement)}；必须补齐名义数量、权利金/固定赔付、保证金、观察方式、敲入敲出、现金或建仓结算和提前终止条款。</p></section>
        </div>

        <footer class="otc-result-footer">
          <p>产品依据：${advice.phoenix ? "凤凰累计结构定义（2025-02-27；未公开内部报价）" : `《商品类产品化宣传单页-20241009》附件第 ${escapeHtml(advice.sourcePage)} 页`} · 技术依据：${escapeHtml(contract.child_skill || contract.analysis_skill || "technical-analysis-helper")} · ATR ${format(technical.atr, 2)}</p>
          <p>数据更新时间：${escapeHtml(updated)} · ${escapeHtml(contract.source || dataset.source || "来源需进一步核验")}</p>
        </footer>
      </article>`;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function populate() {
    if (!contracts.length) {
      contractSelect.innerHTML = '<option value="">暂无可用行情</option>';
      contractSelect.disabled = true;
      formError.textContent = "行情数据未加载，暂时无法生成结构建议。";
      dataDate.textContent = "数据不可用";
      return;
    }
    contractSelect.innerHTML = '<option value="">请选择合约</option>' + contracts.map((contract) => {
      const label = `${contract.name} ${contract.symbol}${contract.contract_label ? ` · ${contract.contract_label}` : ""} · ${contract.trade_date || "日期待核验"}`;
      return `<option value="${escapeHtml(contract.symbol)}">${escapeHtml(label)}</option>`;
    }).join("");
    const newest = contracts.map((item) => item.trade_date).filter(Boolean).sort().at(-1);
    dataDate.textContent = newest ? `最新交易日 ${newest}` : dataset.updated_at || "需进一步核验";
    dataSource.textContent = `数据集更新 ${dataset.updated_at || "需进一步核验"} · 技术分析随行情自动重算`;
  }

  contractSelect.addEventListener("change", () => {
    const contract = contracts.find((item) => item.symbol === contractSelect.value);
    contractNote.textContent = contract
      ? `${contract.score?.stance || "观点待核验"} · 置信度${contract.score?.view_confidence || "待核验"} · 最新价 ${format(contract.price)}`
      : "主力与次主力合约";
    formError.textContent = "";
  });

  function syncFamilyFields() {
    const phoenixSelected = familySelect.value === "phoenix";
    phoenixSuitability.hidden = !phoenixSelected;
    if (phoenixSelected && cadenceSelect.value !== "daily") cadenceSelect.value = "daily";
    if (!phoenixSelected) r5Confirm.checked = false;
    formError.textContent = "";
  }

  familySelect.addEventListener("change", syncFamilyFields);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const contract = contracts.find((item) => item.symbol === contractSelect.value);
    if (!contract) {
      formError.textContent = "请先选择标的合约。";
      contractSelect.focus();
      return;
    }
    const family = familySelect.value;
    const objective = selected("objective");
    if (family === "phoenix" && cadenceSelect.value !== "daily") {
      formError.textContent = "凤凰累计必须选择“每日采购或销售 / 逐日结算”。";
      resetResult(formError.textContent);
      cadenceSelect.focus();
      return;
    }
    if (family === "phoenix" && objective === "enhancement") {
      formError.textContent = "凤凰累计需要明确真实采购或库存/销售方向，不能按无方向的“库存增收”输出。";
      resetResult(formError.textContent);
      form.querySelector('input[name="objective"][value="procurement"]').focus();
      return;
    }
    if (family === "phoenix" && !r5Confirm.checked) {
      formError.textContent = "请先确认交易主体已完成 R5 适当性核验。";
      resetResult(formError.textContent);
      r5Confirm.focus();
      return;
    }
    formError.textContent = "";
    render(contract, objective, selected("cost"), cadenceSelect.value, family);
  });

  populate();
  syncFamilyFields();
})();

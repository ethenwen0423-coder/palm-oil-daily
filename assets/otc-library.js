(function () {
  const groups = [
    {
      id: "daily-buy",
      name: "每日采购累计",
      description: "面向连续采购流量，通过每日观察在区间内获得补贴，并在下方形成低位采购头寸。",
      items: [
        {
          name: "累进宝1.0",
          type: "固定赔付累计（带敲出）",
          badge: "路径型",
          bestFor: "连续采购、希望区间内降低采购成本，并愿意在下方接多单。",
          mechanism: "价格位于约定区间时按日获得固定补贴；触及上方敲出条件时产品提前结束。",
          trigger: "跌破下方条件后，按条款形成剩余或约定数量的多头采购头寸。",
          tradeoff: "补贴与低位采购机会来自路径和建仓义务；快速下跌时可能集中形成多头并产生追保。",
        },
        {
          name: "累进宝2.0",
          type: "固定赔付累计（无敲出）",
          badge: "每日结算",
          bestFor: "逢低随采，希望保留完整观察期并持续获得固定补贴。",
          mechanism: "没有上方敲出，按每日收盘结果结算固定补贴；下方区域用于优化采购建仓。",
          trigger: "低于下方条件时，产生约定杠杆的下跌损益或多头建仓义务。",
          tradeoff: "获利情景比带敲出版本更宽，但观察期持续存在，数量与下方敞口更难提前结束。",
        },
        {
          name: "累进宝3.0",
          type: "线性累计",
          badge: "线性收益",
          bestFor: "希望折价采购，并接受收益随价格位置线性变化。",
          mechanism: "区间内收益不再是固定值，而是随标的价格线性变化；每日观察并累计。",
          trigger: "跌至下方区域时，按约定价格和数量形成采购多头。",
          tradeoff: "对行情位置更敏感，区间收益弹性更大，但价格快速越过区间时损益变化也更快。",
        },
        {
          name: "累进宝4.0",
          type: "线性熔断累计",
          badge: "敲出终止",
          bestFor: "希望每日采购套保，同时在上涨触发后及时结束结构、保持仓位灵活。",
          mechanism: "区间内按线性方式累计；触及上方敲出时获得约定敲出收益并提前终止。",
          trigger: "下方触发后按条款形成多头采购头寸；上方敲出后不再继续观察。",
          tradeoff: "熔断减少后续路径暴露，但敲出后若行情继续上涨，结构不再提供后续补贴。",
        },
        {
          name: "累进宝5.0",
          type: "固定赔付熔断累计",
          badge: "固定补贴",
          bestFor: "重视区间固定补贴，并希望上涨触发时提前结束结构。",
          mechanism: "区间内每日取得固定赔付；触及上方敲出后产品终止并按约定处理敲出收益。",
          trigger: "下方观察通常对应 1+1 或杠杆建仓安排，具体数量需在确认书中明确。",
          tradeoff: "固定补贴更直观，但敲入数量和到期额外观察可能放大下跌时的采购义务。",
        },
        {
          name: "累进宝1.0 Plus",
          type: "增强固定赔付累计（带敲出）",
          badge: "上涨增强",
          bestFor: "希望保留1.0的区间补贴，同时增加大涨时的线性补贴。",
          mechanism: "区间内获得固定补贴；上涨越过增强区后增加线性收益，敲出后提前结束。",
          trigger: "下方仍可能形成低位多头采购头寸。",
          tradeoff: "上涨保护更强，但通常需要牺牲部分区间补贴或承担更严格的下方建仓条件。",
        },
        {
          name: "累进宝2.0 Plus",
          type: "增强固定赔付累计（无敲出）",
          badge: "全程观察",
          bestFor: "希望完整覆盖观察期，并同时获取固定补贴和大涨线性收益。",
          mechanism: "区间内固定赔付，大涨时在固定赔付基础上叠加线性补贴；没有敲出提前终止。",
          trigger: "下方条件触发时按条款产生多头采购义务。",
          tradeoff: "获利情景更宽，但观察期不能靠敲出结束，路径、数量和保证金占用更长。",
        },
        {
          name: "累进宝3.0 Plus",
          type: "增强线性累计",
          badge: "上下沿采购",
          bestFor: "希望震荡或下跌时低位采购，大涨时也能获得采购补贴。",
          mechanism: "区间内按价格线性累计；下行侧对应区间下沿采购，上行侧增加增强收益。",
          trigger: "越过上下边界后，按条款分别处理低位建仓或上方增强结算。",
          tradeoff: "同时管理两端价格，但损益和建仓逻辑比固定补贴结构更复杂。",
        },
        {
          name: "累进宝4.0 Plus",
          type: "线性熔断累计 Plus",
          badge: "浮动敲出收益",
          bestFor: "希望保留熔断机制，并让上方敲出收益随行情变化。",
          mechanism: "区间内线性累计，触及上方敲出时取得浮动增强收益并结束产品。",
          trigger: "下方仍可能形成约定多头；上方敲出后剩余观察全部取消。",
          tradeoff: "敲出端收益更有弹性，但定价、提前平仓和路径依赖也更复杂。",
        },
      ],
    },
    {
      id: "buy-hedge",
      name: "阶段采购防涨",
      description: "面向一次性或阶段性采购，以领式、比例领式和海鸥结构管理上涨成本。",
      items: [
        {
          name: "采省易1.0",
          type: "领式看涨",
          badge: "1倍",
          bestFor: "担心价格上涨，同时愿意在较低价格采购现货或建立多头套保。",
          mechanism: "小幅下跌通常无期权损益，上涨越过上方价格后获得保护。",
          trigger: "大跌至下方价格时，按约定以较低价格形成多头或承担相应现金损益。",
          tradeoff: "用下方采购义务换取低成本上涨保护；持续大跌会让渡部分低价采购收益。",
        },
        {
          name: "采省易2.0",
          type: "比例领式看涨",
          badge: "2倍",
          bestFor: "对上涨方向判断较明确，并有能力在大跌后承接双倍采购数量。",
          mechanism: "上涨从入场价开始获得完整保护，小跌处于安全垫内无损益。",
          trigger: "跌破下方价格后，默认承担 2 倍下跌损益或形成双倍多头。",
          tradeoff: "看对时保护完整，但双倍敞口要求真实采购能力、保证金和严格数量控制。",
        },
        {
          name: "采省易3.0",
          type: "海鸥看涨",
          badge: "1倍封顶",
          bestFor: "希望无杠杆地保护一定上涨区间，并愿意在更低价格锁定采购。",
          mechanism: "上涨在约定区间内按涨幅补贴，达到上方价格后收益封顶；小跌无损益。",
          trigger: "跌破下方价格后，按 1:1 形成多头或承担下方损益。",
          tradeoff: "没有双倍杠杆，但大涨保护有限；用收益封顶换取较低采购建仓价。",
        },
      ],
    },
    {
      id: "sell-hedge",
      name: "销售与库存管理",
      description: "用于库存防跌、持续销售和库存增收，重点管理下跌保护与上方销售义务。",
      items: [
        {
          name: "期现易1.0",
          type: "领式看跌",
          badge: "1倍",
          bestFor: "担心价格下跌，并愿意在较高价格出售现货或建立空头套保。",
          mechanism: "小幅上涨通常无期权损益，下跌越过保护价格后获得补偿。",
          trigger: "大涨至上方条件时，按约定形成空头或锁定较高销售价格。",
          tradeoff: "用上方销售义务换取低成本下跌保护；持续大涨会让渡部分现货上涨收益。",
        },
        {
          name: "期现易2.0",
          type: "比例领式看跌",
          badge: "2倍",
          bestFor: "希望下跌得到完整保护，并有足够库存承接上方双倍销售。",
          mechanism: "价格下跌时从入场价开始获得保护，小涨在安全垫内无损益。",
          trigger: "上涨越过上方价格后，产生 2 倍空头损益或双倍销售义务。",
          tradeoff: "防跌完整，但上方双倍数量可能超过现货库存，必须严格匹配真实销售计划。",
        },
        {
          name: "期现易3.0",
          type: "海鸥看跌",
          badge: "1倍封顶",
          bestFor: "希望无杠杆保护下跌区间，并愿意在更高价格锁定销售。",
          mechanism: "下跌在约定区间内获得补偿，达到下方边界后保护封顶；小涨无损益。",
          trigger: "上涨越过上方价格后，按 1:1 形成空头或锁定销售价。",
          tradeoff: "便于匹配现货数量，但极端下跌保护有限，极端上涨也会让渡部分利润。",
        },
        {
          name: "惠增收",
          type: "反比例领式看涨",
          badge: "库存增强",
          bestFor: "已有现货库存，预期震荡或小幅反弹，希望提高库存持有收益。",
          mechanism: "下跌时期权端通常不亏；小涨区间增强收益，继续上涨后增强收益逐步回吐。",
          trigger: "上涨超过盈亏平衡点后产生期权亏损，或按约定形成高位空头。",
          tradeoff: "必须与现货多头合并使用；它不是完整防跌工具，无现货时会变成方向性风险。",
        },
        {
          name: "惠鑫保1.0",
          type: "香草累计",
          badge: "每日销售",
          bestFor: "有持续销售计划，希望低成本保护销售均价下跌。",
          mechanism: "按日观察与结算，下跌时对每日销售数量提供保护，上涨时保留现货收益。",
          trigger: "每日损益按收盘价格和约定数量累计，观察期内持续形成销售保护。",
          tradeoff: "数量随观察日累计，期限越长总名义越大；需与真实每日销售流量匹配。",
        },
        {
          name: "惠鑫保2.0",
          type: "鲨鱼鳍累计",
          badge: "障碍终止",
          bestFor: "预期震荡偏弱，希望低成本博取区间收益，并限制看错后的持续损失。",
          mechanism: "区间内按日获得下跌收益；跌破约定障碍后产品提前终止。",
          trigger: "触及下方终止条件时停止后续观察，并按条款退还或处理剩余权利金。",
          tradeoff: "成本较低且看错后可终止，但极端下跌时保护会提前失效，不适合要求完整防跌的库存。",
        },
      ],
    },
    {
      id: "relative-value",
      name: "价差与月差",
      description: "围绕加工费、跨品种关系和跨期价差进行保值或建仓优化，需要独立价差数据和流动性评估。",
      items: [
        {
          name: "价差宝·加工费保值",
          type: "跨品种价差卖出看涨",
          badge: "加工费",
          bestFor: "生产企业是加工费天然多头，认为高位加工费可能回落。",
          mechanism: "对按配比构造的加工费价差卖出看涨；价差未突破执行价时取得权利金收益。",
          trigger: "价差升破执行价后产生亏损，与企业实际加工费改善相互对冲。",
          tradeoff: "配比、基差和两腿流动性都会影响效果；无产业敞口时属于裸卖价差期权。",
        },
        {
          name: "价差宝·跨品种套利",
          type: "跨品种价差卖出看跌",
          badge: "建仓优化",
          bestFor: "计划建立跨品种多头价差，希望在更低价差水平入场。",
          mechanism: "对按配比构造的跨品种价差卖出看跌，未跌破执行价时获得权利金。",
          trigger: "价差跌破执行价后承担下跌损益或按约定建立价差多头。",
          tradeoff: "两腿价格和配比会共同变化，可能出现相关性失效、滑点和保证金放大。",
        },
        {
          name: "月差宝·移仓增收",
          type: "跨期价差卖出看跌",
          badge: "期现移仓",
          bestFor: "现货或期货头寸需要移仓，希望优化近远月换月价差。",
          mechanism: "以近远月价差为标的卖出看跌，未跌破执行价时获得权利金以增厚移仓收益。",
          trigger: "月差跌破执行价后承担下跌损益或形成约定的跨期头寸。",
          tradeoff: "交割、仓储、期限结构和流动性变化会使月差偏离历史区间。",
        },
        {
          name: "月差宝·月间套利",
          type: "跨期价差卖出看跌",
          badge: "套利建仓",
          bestFor: "计划建立月间价差多头，希望在更低价差水平建仓。",
          mechanism: "卖出月差看跌，未触发时获得权利金，触发后按约定承接跨期价差。",
          trigger: "价差跌破执行价后形成跨期建仓义务或现金亏损。",
          tradeoff: "不是无风险套利；期限结构反转、移仓成本和单腿流动性都可能扩大亏损。",
        },
      ],
    },
    {
      id: "airbag",
      name: "气囊宝1.0",
      description: "到期结算、每日收盘观察障碍；未敲入时看对方向获得折扣收益，看错但仍在安全垫内到期不亏。",
      items: [
        {
          name: "正向气囊宝1.0",
          type: "正向安全气囊",
          badge: "1倍多头",
          bestFor: "希望参与上涨，又担心抄底后先出现回撤。",
          mechanism: "未触及下方障碍时，到期按约定参与率分享上涨；到期仍处于安全垫内则无损益。",
          trigger: "任一观察日收盘触及下方障碍，气囊立即终止并转为约定建仓价的 1 倍多头远期。",
          tradeoff: "看对收益按参与率打折；安全垫内提前平仓仍可能亏损，不利波动也可能立即追保。",
        },
        {
          name: "反向气囊宝1.0",
          type: "反向安全气囊",
          badge: "1倍空头",
          bestFor: "希望参与下跌，又担心摸顶后先出现反弹。",
          mechanism: "未触及上方障碍时，到期按约定参与率分享下跌；到期仍处于安全垫内则无损益。",
          trigger: "任一观察日收盘触及上方障碍，气囊立即终止并转为约定建仓价的 1 倍空头远期。",
          tradeoff: "看对收益按参与率打折；保护区内提前平仓可能亏损，上涨过程也可能产生追保。",
        },
        {
          name: "气囊1.0·收益封顶",
          type: "增加封顶价格",
          badge: "参与率增强",
          bestFor: "愿意放弃极端行情收益，以换取更高参与率或更宽安全垫。",
          mechanism: "有利方向收益达到封顶价后不再增加，节省的期权成本用于改善参与率或障碍距离。",
          trigger: "障碍触发逻辑不变；未敲入时的到期收益受到封顶限制。",
          tradeoff: "大行情收益被限制，且越早在收益区间内平仓，折损通常越明显。",
        },
        {
          name: "气囊1.0·虚值行权",
          type: "调整收益起算价",
          badge: "参与率增强",
          bestFor: "接受行情先走一段才开始获利，以换取更高参与率或安全垫。",
          mechanism: "把收益行权价从平值移至虚值，收益从新的行权价开始计算。",
          trigger: "敲入障碍和转远期逻辑仍然存在，可与收益封顶组合使用。",
          tradeoff: "初段有利行情没有收益；与封顶组合时虽然参与率可超过100%，但实际收益区间更窄。",
        },
        {
          name: "气囊1.0·敲入建仓价优化",
          type: "调整敲入执行价格",
          badge: "降低浮亏",
          bestFor: "更重视敲入后的建仓成本，希望降低转远期时的初始浮亏。",
          mechanism: "把敲入后的远期建仓价从默认入场价调整到更接近障碍的位置。",
          trigger: "任一观察日收盘触及障碍后，仍立即终止并按新的建仓价转远期。",
          tradeoff: "敲入风险下降，但参与率或安全垫通常会相应变差。",
        },
      ],
    },
    {
      id: "phoenix",
      name: "凤凰累计",
      description: "每日观察并在区间内累计固定收益；敲入或敲出都会立即结束，风险等级高，必须匹配真实现货流量。",
      items: [
        {
          name: "凤凰累计1.0",
          type: "1倍·敲入剩余数量",
          badge: "R5",
          bestFor: "有库存或采购流量、震荡看待行情，并愿意在敲入价一次性建仓。",
          mechanism: "区间内每日获得固定凤凰收益；敲出后终止且无额外敲出收益。",
          trigger: "敲入后终止，并按敲入建仓价形成剩余观察数量的 1 倍远期。",
          tradeoff: "是凤凰系列相对基础的模型，但仍可能形成集中远期头寸并承担无限风险敞口。",
        },
        {
          name: "凤凰累计2.0",
          type: "1倍·敲入全部数量",
          badge: "R5",
          bestFor: "希望提高区间收益，并能承接全部观察期数量的一次性建仓。",
          mechanism: "区间内每日固定收益，敲出无额外收益。",
          trigger: "敲入后终止，并形成全部观察数量的 1 倍远期。",
          tradeoff: "与1.0相比，敲入数量从剩余数量扩大到全部数量，集中风险明显更高。",
        },
        {
          name: "凤凰累计3.0",
          type: "2倍·敲出线性增强",
          badge: "R5·2倍",
          bestFor: "愿意承担 2 倍敲入风险，以换取敲出端的线性增强收益。",
          mechanism: "区间内每日固定收益；敲出时剩余数量获得敲出价格外的线性增强收益。",
          trigger: "敲入后终止，并形成剩余数量乘以 2 倍参与率的远期。",
          tradeoff: "增强收益来自 2 倍敲入风险；行情反向时头寸会快速放大。",
        },
        {
          name: "凤凰累计4.0",
          type: "2倍·敲出固定增强",
          badge: "R5·2倍",
          bestFor: "希望敲出时取得明确固定收益，并能承接 2 倍剩余数量。",
          mechanism: "区间内每日固定收益；敲出时对剩余数量支付固定增强收益。",
          trigger: "敲入后终止，并形成剩余数量乘以 2 倍参与率的远期。",
          tradeoff: "敲出收益更容易理解，但敲入端仍是 2 倍集中远期风险。",
        },
        {
          name: "凤凰累计5.0",
          type: "2倍·全部数量·线性增强",
          badge: "R5·高风险",
          bestFor: "能承接全部观察期 2 倍数量，并追求敲出线性增强收益。",
          mechanism: "区间内每日固定收益；敲出时获得下沿价格相关的线性增强收益。",
          trigger: "敲入后终止，并形成全部观察数量乘以 2 倍参与率的远期。",
          tradeoff: "在3.0基础上把敲入从剩余数量扩大到全部数量，属于高集中度版本。",
        },
        {
          name: "凤凰累计6.0",
          type: "2倍·全部数量·固定增强",
          badge: "R5·高风险",
          bestFor: "能承接全部观察期 2 倍数量，并偏好固定敲出收益。",
          mechanism: "区间内每日固定收益；敲出时对剩余数量支付固定增强收益。",
          trigger: "敲入后终止，并形成全部观察数量乘以 2 倍参与率的远期。",
          tradeoff: "在4.0基础上扩大为全部数量，风险高于累进宝5.0和凤凰4.0。",
        },
      ],
    },
  ];

  const content = document.querySelector("#library-content");
  const filters = document.querySelector("#library-filters");
  const search = document.querySelector("#library-search");
  let activeGroup = "all";

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function searchable(group, item) {
    return [group.name, group.description, item.name, item.type, item.badge, item.bestFor, item.mechanism, item.trigger, item.tradeoff]
      .join(" ").toLowerCase();
  }

  function renderFilters() {
    const buttons = [{ id: "all", name: "全部" }, ...groups.map(({ id, name }) => ({ id, name }))];
    filters.innerHTML = buttons.map((button) => `
      <button type="button" data-group="${escapeHtml(button.id)}" aria-pressed="${button.id === activeGroup}">${escapeHtml(button.name)}</button>`).join("");
  }

  function render() {
    const keyword = search.value.trim().toLowerCase();
    const sections = groups.map((group) => {
      if (activeGroup !== "all" && activeGroup !== group.id) return "";
      const items = group.items.filter((item) => !keyword || searchable(group, item).includes(keyword));
      if (!items.length) return "";
      const cards = items.map((item) => `
        <details class="library-card">
          <summary>
            <div>
              <span>${escapeHtml(item.type)}</span>
              <h3>${escapeHtml(item.name)}</h3>
              <p>${escapeHtml(item.bestFor)}</p>
            </div>
            <strong>${escapeHtml(item.badge)}</strong>
            <i aria-hidden="true">+</i>
          </summary>
          <div class="library-card-body">
            <section><span>怎么运作</span><p>${escapeHtml(item.mechanism)}</p></section>
            <section><span>触发后发生什么</span><p>${escapeHtml(item.trigger)}</p></section>
            <section><span>核心取舍与风险</span><p>${escapeHtml(item.tradeoff)}</p></section>
          </div>
        </details>`).join("");
      return `
        <section class="library-group" id="${escapeHtml(group.id)}">
          <header><div><span>${String(groups.indexOf(group) + 1).padStart(2, "0")}</span><h2>${escapeHtml(group.name)}</h2></div><p>${escapeHtml(group.description)}</p></header>
          <div class="library-card-list">${cards}</div>
        </section>`;
    }).join("");

    content.innerHTML = sections || `
      <div class="library-empty"><strong>没有找到匹配结构</strong><p>请更换关键词或切换到“全部”。</p></div>`;
  }

  filters.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-group]");
    if (!button) return;
    activeGroup = button.dataset.group;
    renderFilters();
    render();
  });

  search.addEventListener("input", render);
  renderFilters();
  render();
})();

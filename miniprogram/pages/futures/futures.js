const api = require("../../utils/api");

function decorate(contract, index) {
  const score = contract.score || {};
  return Object.assign({}, contract, {
    index,
    scoreTotal: score.total === undefined ? "需进一步核验" : score.total,
    technicalScore: score.technical === undefined ? "需进一步核验" : score.technical,
    fundamentalScore: score.fundamental === undefined ? "需进一步核验" : score.fundamental,
    stance: score.stance || contract.strategy || "需进一步核验",
    changeClass: contract.direction === "↑" ? "up" : contract.direction === "↓" ? "down" : "flat",
    expanded: index === 0,
  });
}

Page({
  data: {
    updatedAt: "",
    source: "",
    contracts: [],
    pickerOptions: [],
    selectedIndex: 0,
    watchContract: null,
    offline: false,
  },
  onLoad() { this.loadData(); },
  onPullDownRefresh() { this.loadData(true); },

  async loadData(fromPullDown) {
    const result = await api.getFutures();
    const payload = result.data || {};
    const contracts = (Array.isArray(payload.contracts) ? payload.contracts : []).map(decorate);
    this.setData({
      updatedAt: payload.updated_at || "等待行情数据",
      source: payload.source || "数据源等待加载",
      contracts,
      pickerOptions: contracts.map((item) => `${item.name} ${item.contract} ${item.contract_label || ""}`),
      watchContract: contracts[0] || null,
      offline: result.offline,
    });
    if (fromPullDown) wx.stopPullDownRefresh();
  },

  toggleContract(event) {
    const index = Number(event.currentTarget.dataset.index);
    this.setData({ [`contracts[${index}].expanded`]: !this.data.contracts[index].expanded });
  },
  selectWatch(event) { this.setData({ selectedIndex: Number(event.detail.value) }); },
  confirmWatch() { this.setData({ watchContract: this.data.contracts[this.data.selectedIndex] || null }); },
});

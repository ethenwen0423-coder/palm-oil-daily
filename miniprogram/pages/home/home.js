const api = require("../../utils/api");
const reportUtils = require("../../utils/reports");

Page({
  data: {
    loading: true,
    offline: false,
    latest: null,
    recent: [],
    heroPoints: [],
  },

  onLoad() { this.loadData(); },
  onPullDownRefresh() { this.loadData(true); },

  async loadData(fromPullDown) {
    const result = await api.getReports();
    const groups = reportUtils.splitReports(result.data);
    const latest = groups.daily[0] || groups.all[0] || null;
    const parts = latest ? latest.displayHeadline.split(/[；;。]/).filter(Boolean) : [];
    this.setData({
      loading: false,
      offline: result.offline,
      latest,
      recent: reportUtils.recentReports(groups.all),
      heroPoints: parts.slice(1, 3).length ? parts.slice(1, 3) : ["等待盘面确认", "控制追高风险"],
    });
    if (fromPullDown) wx.stopPullDownRefresh();
  },

  openReport(event) {
    wx.navigateTo({ url: `/pages/report-detail/report-detail?id=${encodeURIComponent(event.currentTarget.dataset.id)}` });
  },
  openReports() { wx.switchTab({ url: "/pages/reports/reports" }); },
  openFutures() { wx.switchTab({ url: "/pages/futures/futures" }); },
});

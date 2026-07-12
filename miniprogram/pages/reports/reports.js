const api = require("../../utils/api");
const { splitReports } = require("../../utils/reports");

Page({
  data: { active: "recent", reports: [], all: [], daily: [], weekly: [], offline: false },
  onLoad() { this.loadData(); },
  onPullDownRefresh() { this.loadData(true); },
  async loadData(fromPullDown) {
    const result = await api.getReports();
    const groups = splitReports(result.data);
    this.setData(Object.assign({ offline: result.offline }, groups));
    this.applyFilter(this.data.active, groups);
    if (fromPullDown) wx.stopPullDownRefresh();
  },
  changeTab(event) { this.applyFilter(event.currentTarget.dataset.tab); },
  applyFilter(active, source) {
    const groups = source || this.data;
    const reports = active === "daily" ? groups.daily : active === "weekly" ? groups.weekly : groups.all;
    this.setData({ active, reports });
  },
  openReport(event) {
    wx.navigateTo({ url: `/pages/report-detail/report-detail?id=${encodeURIComponent(event.currentTarget.dataset.id)}` });
  },
});

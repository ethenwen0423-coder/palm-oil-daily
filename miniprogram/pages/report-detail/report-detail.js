const api = require("../../utils/api");
const config = require("../../config");
const { decorate } = require("../../utils/reports");
const { renderMarkdown } = require("../../utils/markdown");

Page({
  data: { report: null, contentHtml: "", offline: false },
  reportId: "",

  onLoad(options) {
    this.reportId = decodeURIComponent(options.id || "");
    this.loadData();
  },

  async loadData() {
    const result = await api.getReports();
    const reports = Array.isArray(result.data) ? result.data : [];
    const raw = reports.find((item) => item.date === this.reportId) || reports[0];
    if (!raw) return;
    const report = decorate(raw);
    this.setData({ report, contentHtml: renderMarkdown(report.content), offline: result.offline });
    wx.setNavigationBarTitle({ title: report.displayTitle });
  },

  copySource() {
    const path = this.data.report.download || `reports/${this.data.report.date}.md`;
    wx.setClipboardData({ data: `${config.siteBase}/${path}` });
  },

  downloadSource() {
    const report = this.data.report;
    if (!report) return;
    const path = report.download || `reports/${report.date}.md`;
    wx.showLoading({ title: "下载中" });
    wx.downloadFile({
      url: `${config.siteBase}/${path}`,
      success(response) {
        if (response.statusCode !== 200) { wx.showToast({ title: "下载失败", icon: "none" }); return; }
        wx.saveFile({
          tempFilePath: response.tempFilePath,
          success() { wx.showModal({ title: "下载完成", content: "原文已保存到小程序文件，可通过右上角菜单转发或继续使用。", showCancel: false }); },
          fail() { wx.showToast({ title: "保存失败，请复制链接", icon: "none" }); },
        });
      },
      fail() { wx.showToast({ title: "下载失败，请复制链接", icon: "none" }); },
      complete() { wx.hideLoading(); },
    });
  },

  onShareAppMessage() {
    const report = this.data.report || {};
    return { title: report.displayHeadline || report.displayTitle || "棕榈油研究报告", path: `/pages/report-detail/report-detail?id=${encodeURIComponent(report.date || "")}` };
  },
});

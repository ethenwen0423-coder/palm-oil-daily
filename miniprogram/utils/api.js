const config = require("../config");
const fallbackReports = require("../data/reports");
const fallbackFutures = require("../data/oil_futures");

function requestJson(path, fallback, cacheKey) {
  return new Promise((resolve) => {
    wx.request({
      url: `${config.apiBase}/${path}`,
      timeout: 10000,
      success(response) {
        const data = normalizeJson(response.data);
        if (response.statusCode >= 200 && response.statusCode < 300 && data) {
          wx.setStorage({ key: cacheKey, data });
          resolve({ data, offline: false });
          return;
        }
        resolveCached();
      },
      fail: resolveCached,
    });

    function resolveCached() {
      const cached = wx.getStorageSync(cacheKey);
      resolve({ data: cached || fallback, offline: true });
    }
  });
}

function normalizeJson(value) {
  if (typeof value !== "string") return value;
  try { return JSON.parse(value); } catch (error) { return null; }
}

function getReports() {
  return requestJson("reports.json", fallbackReports, "palm-oil-reports");
}

function getFutures() {
  return requestJson("oil_futures.json", fallbackFutures, "oil-futures-contracts");
}

module.exports = { getReports, getFutures };

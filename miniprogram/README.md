# Vinson Research 微信小程序

原生微信小程序版本，与 `palm-oil-daily` 网站共用报告与油脂合约数据。

## 已对齐的网站功能

- 首页今日观点、更新时间、最近一周报告和快捷入口。
- 日报/周报归档筛选。
- 报告详情、Markdown 表格/列表渲染、原文下载和链接复制。
- 油脂合约价格、涨跌幅、评分、技术面/基本面详解、策略观察位和自选合约。
- 下拉刷新、在线数据优先、缓存及随包数据兜底。

## 本地预览

1. 打开微信开发者工具，导入本目录。
2. 预览阶段可使用 `project.config.json` 的测试 AppID。
3. 发布前把 `appid` 替换为正式小程序 AppID。
4. 在微信公众平台配置合法域名：
   - `request`：`https://ethenwen0423-coder.github.io`
   - `downloadFile`：`https://ethenwen0423-coder.github.io`

当前真实静态数据地址是 `https://ethenwen0423-coder.github.io/palm-oil-daily/`。`vinsontesla.com` 目前由另一套 Vercel 页面响应，不能作为本小程序的数据域名；如果以后恢复自定义域名，需要同步修改 `config.js` 并重新配置微信合法域名。

## 数据同步

网站发布脚本会同时维护：

- 网站数据：`data/reports.js`、`data/oil_futures.js`
- 小程序在线接口：`data/reports.json`、`data/oil_futures.json`
- 小程序离线兜底：`miniprogram/data/reports.js`、`miniprogram/data/oil_futures.js`

手动同步现有网站数据：

```bash
python3 scripts/sync_miniprogram_data.py
```

日报/周报继续运行 `scripts/deploy_report.sh`，油脂合约独立刷新继续运行 `scripts/deploy_oil_futures_tab.sh`，两条链路都会一并更新小程序数据。

# 棕榈油期货日报与周报网站

这是 `vinsontesla.com` 的棕榈油研究网站仓库，用于展示棕榈油期货日报、周报、今日观点和油脂主力合约跟踪。

网站面向油脂期货研究和交易跟踪场景：每天自动整理棕榈油市场核心变化，把报告、观点、价格、持仓、评分和策略区间集中展示在一个可访问的静态网站里。

## 网站功能

### 首页观点看板

首页顶部展示最新报告中的核心观点，包括：

- 最新报告日期和更新时间。
- 今日观点摘要。
- 最近报告的关键判断。
- 日报、周报和油脂主力合约的快速入口。

### 报告归档

网站按时间归档所有研究报告：

- 最近一周报告：集中展示最新日报和周报。
- 日报列表：跟踪工作日棕榈油行情、库存、外盘、价差和交易信号。
- 周报列表：复盘棕榈油、豆油、菜油及原油、天气、政策等外部变量。
- 单篇报告页：把 Markdown 报告渲染为网页，并支持下载原文。

### 油脂主力合约跟踪

首页提供“油脂主力合约”tab，展示国内油脂期货和相关外盘合约：

- 棕榈油、豆油、菜油主力合约价格。
- 涨跌幅、成交量、持仓量、开高低收等行情字段。
- 技术面和基本面评分。
- 趋势立场、支撑压力、止盈止损和策略区间。
- 数据来源与交叉验证说明。

### 自动生成与发布

网站背后是一套本机自动化报告工作流：

- 工作日日报：每个交易日早间生成棕榈油期货日报，并在同一调度内刷新首页“油脂主力合约”tab。
- 周末周报：每周日生成棕榈油、豆油、菜油及外部变量的周度复盘。
- 自动补检：macOS `launchd` 在固定时间检查报告是否已发布，缺失或不合格时自动补跑。
- 网站发布：报告 Markdown 会同步写入 `reports/`、`downloads/` 和 `data/reports.js`，供前端页面读取。
- 来源约束：报告生成会调用金融数据脚本，并读取自动化 prompt、微信/产业来源池和 Vinson Research Writing Standard。

## 前端页面

- 首页：`index.html`
  - 展示今日观点、最近报告、日报归档、周报归档和油脂主力合约 tab。
- 详情页：`report.html`
  - 展示单篇报告正文，自动解析标题、表格、列表、风险提示和来源链接。
- 场外结构建议页：`otc-structure.html`
  - 选择合约后，根据最新行情、MA20/MA60、ATR、综合观点与置信度，输出行情结论、推荐结构、简短运作说明、核心依据和重新评估条件；不展示询价点位或附件示例数据。
- 场外结构详解库：`otc-structure-library.html`
  - 可搜索、筛选并展开查看 6 个结构家族、33 个结构与变种的适用场景、运作方式、触发结果及核心风险；不展示附件历史报价。
- 静态资源：`assets/`
  - 包含页面样式、交互逻辑和视觉资源。
- 数据文件：`data/`
  - `reports.js` 提供报告列表和正文。
  - `oil_futures.js` 提供油脂主力合约行情、评分和策略数据。
  - `version.js` 用于控制前端缓存刷新。

## 微信小程序

仓库内的 `miniprogram/` 是与网站功能对齐的原生微信小程序工程，包含今日观点、报告归档、报告详情与原文下载、油脂主力合约和自选合约功能。

小程序通过当前 GitHub Pages 站点在线读取 `data/reports.json` 和 `data/oil_futures.json`，网站每次自动发布时会同步更新这两个接口；随包数据和本地缓存用于断网兜底。导入、正式 AppID 和合法域名配置见 `miniprogram/README.md`。

## 目录说明

- `index.html`：报告列表首页。
- `report.html`：单篇报告阅读页。
- `otc-structure.html`：基于行情和技术位生成场外结构研究建议。
- `assets/`：网站样式、脚本和图片资源。
- `reports/`：正式报告 Markdown 原文。
- `downloads/`：供网站下载的 Markdown 副本。
- `data/reports.js`：网站读取的报告索引和正文数据。
- `references/`：日报、周报自动化 prompt 和来源参考。
- `scripts/run_financial_skills.py`：抓取和整理外盘、内盘、库存、价差、持仓等数据。
- `scripts/publish_report.py`：把 `reports/` 汇总成网站数据。
- `scripts/deploy_report.sh`：发布报告数据并推送到 GitHub。
- `scripts/update_oil_futures_data.py`：更新首页“油脂主力合约”tab 数据。
- `scripts/deploy_oil_futures_tab.sh`：发布首页“油脂主力合约”tab 数据，由工作日日报调度调用。
- `scripts/install_daily_watchdog_launchd.sh`：安装工作日日报补检任务。
- `scripts/install_weekly_watchdog_launchd.sh`：安装周末周报补检任务。
- `scripts/install_oil_futures_tab_launchd.sh`：卸载旧的独立 tab 刷新任务；tab 更新已并入工作日日报调度。

## 自动化调度

生产环境运行在本机 macOS `launchd`，默认运行目录是：

```bash
~/Sites/palm-oil-daily
```

当前调度包括：

- `com.vinsontesla.palm-oil-daily-watchdog`
  - 周一至周五 08:20 主动检查并生成日报
  - 周一至周五 08:40 再次补检
  - 日报合格后在同一调度内刷新首页“油脂主力合约”tab
- `com.vinsontesla.palm-oil-weekly-watchdog`
  - 周日 21:15 主动检查并生成周报
  - 周日 21:40 再次补检
  - 只更新周报，不刷新首页“油脂主力合约”tab

安装或刷新调度：

```bash
bash scripts/install_daily_watchdog_launchd.sh
bash scripts/install_weekly_watchdog_launchd.sh
bash scripts/install_oil_futures_tab_launchd.sh
```

## 手动发布流程

如果已经手动新增或修改了 `reports/` 下的报告，可以运行：

```bash
bash scripts/deploy_report.sh
```

脚本会执行以下操作：

1. 读取 `reports/*.md`。
2. 生成或更新 `downloads/*.md`。
3. 生成或更新 `data/reports.js`、`data/version.js` 和 `data/oil_futures.js`。
4. 提交报告相关变更。
5. 推送到 GitHub，触发 GitHub Pages 更新。

## 报告命名

- 日报：`reports/YYYY-MM-DD.md`
- 周报：`reports/YYYY-MM-DD-weekend.md`

例如：

```text
reports/2026-06-30.md
reports/2026-06-28-weekend.md
```

## 网站发布

本仓库通过 GitHub Pages 发布，域名为：

```text
vinsontesla.com
```

DNS 需要指向 GitHub Pages：

- `A` 记录，主机名 `@`，指向 `185.199.108.153`
- `A` 记录，主机名 `@`，指向 `185.199.109.153`
- `A` 记录，主机名 `@`，指向 `185.199.110.153`
- `A` 记录，主机名 `@`，指向 `185.199.111.153`
- `CNAME` 记录，主机名 `www`，指向 `ethenwen0423-coder.github.io`

## 重要约束

- 报告必须基于已调用的数据源和公开信息生成。
- 不能发布测试报告、排版调试稿或含有“未实际调用”“当前环境未暴露调用入口”等占位内容的报告。
- 每篇报告结尾需要包含消息来源链接和 AI 观点风险提示。
- 生成逻辑以交易所、官方机构、金融数据脚本和研报为核心，微信/产业来源池只作为补充参考。

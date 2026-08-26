# 油脂板块日报、周报与 24h 研究网站

这是以油脂板块为核心的研究与 24h 行情助手网站仓库，覆盖棕榈油、豆油、菜油及相关外盘，用于展示日报、周报、今日观点、跨市场行情和可追溯 AI 盯盘简报。

网站面向油脂期货研究和交易跟踪场景：自动整理市场核心变化，把报告、观点、价格、持仓、评分、供需状态和 AI 工作队列集中展示。前端优先读取只读动态 API。备案期间 GitHub Pages 与域名解析保持关闭，服务器仅在内部更新数据，不提供公网网站或 API。

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
- 日报列表：跟踪工作日油脂板块行情、库存、外盘、价差和交易信号。
- 周报列表：复盘棕榈油、豆油、菜油及原油、天气、政策等外部变量。
- 单篇报告页：把 Markdown 报告渲染为网页，并支持下载原文。

### 油脂主力合约跟踪

首页提供“油脂主力合约”tab，展示国内油脂期货和相关外盘合约：

- 棕榈油、豆油、菜油主力合约价格。
- 涨跌幅、成交量、持仓量、开高低收等行情字段。
- 技术面和基本面评分。
- 趋势立场、支撑压力、止盈止损和策略区间。
- 数据来源与交叉验证说明。

### 24h 行情助手

`assistant.html` 汇总油脂和跨市场期货行情、报告、供需检查、预测评估及主力合约状态。页面优先从 `/api/*` 读取最新数据，接口不可用时自动回退到仓库内 JSON。

AI 简报只分析已经发布的数据，并返回所引用的证据编号、观察清单、下一步工作和风险门槛。数值由程序从证据记录注入，AI 不能自行编造数值，也不能修改场外结构库或量化模型规则。

### 自动生成与发布

网站背后的正式目标是一套腾讯云 24h 自动化报告与行情工作流，运行不依赖个人电脑：

- 工作日日报：每个交易日早间生成油脂板块期货日报，并冻结当日基本面快照。
- 行情刷新：午间、收盘、夜盘开盘、夜盘收盘和凌晨盘后更新行情；盘中只沿用最近一个有效晨间基本面快照。
- AI 盯盘：每 15 分钟检查已发布数据；源数据发生变化后生成新的可追溯简报，未变化时幂等跳过。
- 周末周报：每周日生成棕榈油、豆油、菜油及外部变量的周度复盘。
- 自动补检：服务器 `systemd` 定时器持续重试，缺失或不合格时不写成功标记。
- 内部发布：备案期间报告和数据只写入服务器内部只读 API 数据卷，不推送到公网。
- 来源约束：报告生成会调用金融数据脚本，并读取自动化 prompt、微信/产业来源池和 Vinson Research Writing Standard。

## 前端页面

- 首页：`index.html`
  - 展示今日观点、最近报告、日报归档、周报归档和油脂主力合约 tab。
- 详情页：`report.html`
  - 展示单篇报告正文，自动解析标题、表格、列表、风险提示和来源链接。
- 场外结构建议页：`otc-structure.html`
  - 选择合约后，根据最新行情、MA20/MA60、ATR、综合观点与置信度，输出行情结论、推荐结构、简短运作说明、核心依据和重新评估条件；不展示询价点位或附件示例数据。
- 24h 行情助手：`assistant.html`
  - 通过 API 汇总行情、来源状态和 AI 简报；API 不可用时使用同源静态 JSON 兜底。
- 场外结构详解库：`otc-structure-library.html`
  - 可搜索、筛选并展开查看 6 个结构家族、38 个结构与变种的适用场景、运作方式、触发结果及核心风险；不展示附件历史报价。
- 静态资源：`assets/`
  - 包含页面样式、交互逻辑和视觉资源。
- 数据文件：`data/`
  - `reports.js` 提供报告列表和正文。
  - `oil_futures.js` 提供油脂主力合约行情、评分和策略数据。
  - `exchange_futures.json` 提供跨市场期货行情。
  - `market_assistant_brief.json` 提供带证据引用的 AI 盯盘简报。
  - `version.js` 用于控制前端缓存刷新。

## 微信小程序

仓库内的 `miniprogram/` 是与网站功能对齐的原生微信小程序工程，包含今日观点、报告归档、报告详情与原文下载、油脂主力合约和自选合约功能。

小程序的在线接口在备案期间停用，只保留随包数据和本地缓存。备案通过并完成合法域名配置后，才可切换到腾讯云只读 API；配置说明见 `miniprogram/README.md`。

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
- `scripts/deploy_oil_futures_tab.sh`：刷新并发布油脂与跨市场行情数据。
- `scripts/update_market_assistant_brief.py`：基于已发布数据生成带证据引用的只读 AI 简报。
- `scripts/deploy_market_assistant_brief.sh`：幂等生成并发布 AI 简报。
- `scripts/prediction_review_watchdog.py`：发现并补评所有已到期但尚未评估的预测，网络恢复后自动补推送。
- `scripts/install_daily_watchdog_launchd.sh`：安装工作日日报补检任务。
- `scripts/install_weekly_watchdog_launchd.sh`：安装周末周报补检任务。
- `scripts/install_oil_futures_tab_launchd.sh`：安装午间、收盘、夜盘和凌晨行情刷新任务。
- `scripts/install_market_assistant_launchd.sh`：安装每 15 分钟运行的 AI 盯盘任务。
- `scripts/install_prediction_review_launchd.sh`：安装每 15 分钟自恢复的收盘预测评估任务。

## 服务器自动化调度

腾讯云服务器使用独立运行目录、共享锁和 `systemd` 定时器；个人电脑上的旧 `launchd` 仅作为迁移期工具，不是 24h 生产依赖。服务器安装与验收见 `server/README.md`。

当前调度包括：

- 行情采集：每 10 分钟检查交易时段并幂等刷新。
- 官方供需：每日检查 MPOB、GAPKI、USDA 等官方来源。
- 日报/周报：每 20 分钟检查是否到期；工作日 06:00 后生成日报，周日 21:15 后生成周报。
- AI 简报：每 10 分钟检查已验证数据，只在真实模型凭据验收后启用。
- 预测复盘：每 15 分钟检查；当日 15:20 后使用服务器收盘快照评估。
- 所有任务共享锁、失败不写成功标记，并由下一个周期重试。

安装或刷新服务器调度：

```bash
sudo PALM_OIL_PUBLIC_ACCESS_MODE=private bash server/install_automation.sh --apply
sudo bash server/enable_ai_automation.sh --enable
sudo python3 server/audit_runtime.py --network --access-mode private
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
4. 默认提交报告相关变更；服务器内部运行时使用 `PALM_OIL_PUBLISH_MODE=files`，不提交或推送。

## 报告命名

- 日报：`reports/YYYY-MM-DD.md`
- 周报：`reports/YYYY-MM-DD-weekend.md`

例如：

```text
reports/2026-06-30.md
reports/2026-06-28-weekend.md
```

## 网站发布

备案完成前不启用 GitHub Pages、域名解析、服务器 Web 服务或公网 API。备案通过后必须另行完成 DNS、HTTPS 与公网访问验收，修改代码本身不会创建解析记录。

## 重要约束

- 报告必须基于已调用的数据源和公开信息生成。
- 不能发布测试报告、排版调试稿或含有“未实际调用”“当前环境未暴露调用入口”等占位内容的报告。
- 每篇报告结尾需要包含消息来源链接和 AI 观点风险提示。
- 生成逻辑以交易所、官方机构、金融数据脚本和研报为核心，微信/产业来源池只作为补充参考。
- AI 简报只能引用已发布证据；不能修改场外结构库、量化模型规则或输出自动交易指令。

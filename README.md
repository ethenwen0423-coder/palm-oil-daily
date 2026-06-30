# 棕榈油期货日报与周报网站

这是 `vinsontesla.com` 的棕榈油研究报告发布仓库，用于生成、归档并发布棕榈油期货日报和周报。

项目现在不是单纯的静态页面模板，而是一套本机自动化报告工作流：定时调用 Codex 生成研究报告，整理为网站数据，并通过 GitHub Pages 发布到公网。

## 当前功能

- 工作日日报：每个交易日早间生成棕榈油期货日报。
- 周末周报：每周日生成棕榈油、豆油、菜油及外部变量的周度复盘。
- 自动补检：macOS `launchd` 在固定时间检查报告是否已发布，缺失或不合格时自动补跑。
- 网站发布：报告 Markdown 会同步写入 `reports/`、`downloads/` 和 `data/reports.js`，供前端页面读取。
- 来源约束：报告生成会调用金融数据脚本，并读取自动化 prompt、微信/产业来源池和 Vinson Research Writing Standard。

## 目录说明

- `index.html`：报告列表首页。
- `report.html`：单篇报告阅读页。
- `assets/`：网站样式、脚本和图片资源。
- `reports/`：正式报告 Markdown 原文。
- `downloads/`：供网站下载的 Markdown 副本。
- `data/reports.js`：网站读取的报告索引和正文数据。
- `references/`：日报、周报自动化 prompt 和来源参考。
- `scripts/run_financial_skills.py`：抓取和整理外盘、内盘、库存、价差、持仓等数据。
- `scripts/publish_report.py`：把 `reports/` 汇总成网站数据。
- `scripts/deploy_report.sh`：发布报告数据并推送到 GitHub。
- `scripts/install_daily_watchdog_launchd.sh`：安装工作日日报补检任务。
- `scripts/install_weekly_watchdog_launchd.sh`：安装周末周报补检任务。

## 自动化调度

生产环境运行在本机 macOS `launchd`，默认运行目录是：

```bash
~/Sites/palm-oil-daily
```

当前调度包括：

- `com.vinsontesla.palm-oil-daily-watchdog`
  - 周一至周五 08:20 主动检查并生成日报
  - 周一至周五 08:40 再次补检
- `com.vinsontesla.palm-oil-weekly-watchdog`
  - 周日 21:15 主动检查并生成周报
  - 周日 21:40 再次补检

安装或刷新调度：

```bash
bash scripts/install_daily_watchdog_launchd.sh
bash scripts/install_weekly_watchdog_launchd.sh
```

## 手动发布流程

如果已经手动新增或修改了 `reports/` 下的报告，可以运行：

```bash
bash scripts/deploy_report.sh
```

脚本会执行以下操作：

1. 读取 `reports/*.md`。
2. 生成或更新 `downloads/*.md`。
3. 生成或更新 `data/reports.js` 和 `data/version.js`。
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

# Palm Oil Data API

## ICP 备案期间的隔离模式

备案完成前，服务器自动化默认使用 `private` 模式：行情、供需和 AI
任务可以继续写入服务器内部数据目录，但 `web` 服务会被明确停止，验收也只从
API 容器内部访问 `127.0.0.1`。修改代码、拉取仓库或刷新数据都不会创建 DNS
记录，也不会自动恢复公网访问。

```bash
cd /srv/palm-oil-daily/site
sudo PALM_OIL_PUBLIC_ACCESS_MODE=private \
  bash server/install_automation.sh --apply
sudo python3 server/audit_runtime.py --network --access-mode private
```

只有备案通过、DNS 和证书准备完成后，才应显式使用
`PALM_OIL_PUBLIC_ACCESS_MODE=public` 恢复 `web` 服务。恢复公网访问不是默认行为。

The API service mounts the repository `data/` directory at `/site/data` and runs
`server/api.py` in a small Python container. All dynamic endpoints are
read-only and return `Cache-Control: no-store`.

Dynamic datasets:

- `/api/reports`
- `/api/oil-futures`
- `/api/exchange-futures`
- `/api/quant-model-signals`
- `/api/supply-demand`
- `/api/contracts/current`
- `/api/forecast/metrics/latest`
- `/api/forecast/metrics/20d`
- `/api/forecast/metrics/60d`
- `/api/forecast/feedback/latest`
- `/api/review/latest`
- `/api/assistant/brief`

Operational endpoints:

- `/api/health` checks file availability.
- `/api/status` reports availability, observation time, age and stale state.

The server-side Git sync remains responsible for refreshing the mounted site
checkout. The server also checks official supply-demand sources daily. The AI
brief is generated from the published datasets, cites the evidence records it
used, and never mutates research data, OTC structure definitions or quant-model
rules.

## 24-hour automation readiness audit

Before moving market collection or AI generation from macOS to the server, run
the read-only audit from the synchronized checkout:

```bash
cd /srv/palm-oil-daily/site
sudo python3 server/audit_runtime.py --network
```

The audit reports Docker/API mounts, systemd timers, Python modules, repository
dependencies and unattended AI capabilities. Credential values are never
printed; only capability booleans are returned. A blocked result is expected
until the Python market-data dependencies, live-data mount and one unattended AI
backend have been configured.

After reviewing the audit, preview and apply the reproducible server install:

```bash
cd /srv/palm-oil-daily/site
sudo bash server/install_automation.sh --dry-run
sudo bash server/install_automation.sh --apply
```

服务器尚无 Codex CLI 时，先按
[OpenAI Codex CLI 官方说明](https://help.openai.com/en/articles/11096431)
安装 npm 包；该步骤只安装程序，不复制个人电脑凭据：

```bash
sudo bash server/install_codex_cli.sh --dry-run
sudo bash server/install_codex_cli.sh --apply
```

The installer creates a pinned Python virtual environment, bootstraps the
live-data directory, replaces only the API container's `/site/data` mount,
installs hardened market, official-data, report, prediction-review and AI
systemd units. Market data retries every ten minutes, the official-source check
retries hourly until its daily success marker exists, report generation every
twenty minutes, and prediction review every fifteen minutes. The AI and report
timers are installed but deliberately left disabled until a real unattended
backend generation and a structured report-draft acceptance both pass.

服务器 AI 使用独立凭证目录，不读取或复制个人电脑上的登录文件。先在腾讯云终端
完成一次设备登录，再通过真实简报生成验收后启用定时器：

```bash
cd /srv/palm-oil-daily/site
sudo bash server/enable_ai_automation.sh --login
sudo bash server/enable_ai_automation.sh --enable
sudo bash server/enable_ai_automation.sh --status
```

如果设备登录不可用，也可以通过标准输入提供 API key；密钥不会写入仓库、页面或
命令行参数：

```bash
sudo bash server/enable_ai_automation.sh --login-api-key
sudo bash server/enable_ai_automation.sh --enable
```

`--enable` 会先保持 AI 与报告定时器关闭，检查专用账号登录状态，运行一次真实
简报生成和一次真实结构化报告草稿验收，全部成功后才启用无人值守定时器。任何
一步失败都不会把测试响应或不完整报告写入正式数据目录。

## Server-owned live market data

The API should mount `/srv/palm-oil-daily/live-data` at `/site/data:ro`.
Repository synchronization only bootstraps reports and forecast metrics. Once
`.server-supply-ready.json` exists, the daily server collector owns
supply-demand checks. Once `.server-market-ready.json` exists, the server owns
market quotes, exchange quotes, dynamic quant-model outputs and current
contracts; a later Git update will not overwrite them. The AI brief remains
upstream-owned until a successful server AI generation writes
`.server-ai-ready.json`, so moving market collection alone cannot freeze newer
AI briefs produced by the existing automation.

服务器首次生成合格报告后写入 `.server-research-ready.json`，此后 Git 同步不能用
旧报告覆盖服务器报告。收盘复盘成功后写入 `.server-review-ready.json`，并同步
latest/20d/60d 指标、生成反馈和最新复盘。晨报同时保存晨间判断快照；15:20 后
复盘使用服务器收盘快照，预测评分与量化模型规则不被修改。

Preview the collector's session selection without changing files:

```bash
cd /srv/palm-oil-daily/site
python3 server/run_market_collector.py --dry-run
python3 server/run_ai_brief.py --dry-run
python3 server/run_research_agent.py --dry-run
python3 server/run_prediction_review.py --dry-run
```

Production calls the collector from a systemd timer every ten minutes. Each
ten-minute window has its own idempotency marker, while the latest session
marker remains available for acceptance checks. A failed window writes no
marker, so the next timer interval retries it. Repeated morning updates refresh
quotes, technicals and dynamic model output while carrying the first verified
morning fundamental snapshot. AI generation runs two minutes after the market
schedule and uses the same collection lock. Its first server-owned publish is
forced through the real structured-output backend before the AI ownership marker
is written. It must not be enabled until the Codex CLI backend and its
unattended credentials pass the readiness audit and a real generation succeeds.

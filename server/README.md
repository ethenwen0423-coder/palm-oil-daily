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

The installer creates a pinned Python virtual environment, bootstraps the
live-data directory, replaces only the API container's `/site/data` mount,
installs hardened market, official-data and AI systemd units, enables the
ten-minute market timer and the daily official-data timer. The AI timer is
installed but deliberately left disabled until a real unattended backend
generation passes its acceptance gate.

## Server-owned live market data

The API should mount `/srv/palm-oil-daily/live-data` at `/site/data:ro`.
Repository synchronization owns reports and forecast metrics. Once
`.server-supply-ready.json` exists, the daily server collector owns
supply-demand checks. Once `.server-market-ready.json` exists, the server owns
market quotes, exchange quotes, dynamic quant-model outputs and current
contracts; a later Git update will not overwrite them. The AI brief remains
upstream-owned until a successful server AI generation writes
`.server-ai-ready.json`, so moving market collection alone cannot freeze newer
AI briefs produced by the existing automation.

Preview the collector's session selection without changing files:

```bash
cd /srv/palm-oil-daily/site
python3 server/run_market_collector.py --dry-run
python3 server/run_ai_brief.py --dry-run
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

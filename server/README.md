# Palm Oil Data API

The public server mounts the repository `data/` directory at `/site/data` and runs
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
checkout. The AI brief is generated from the published datasets, cites the
evidence records it used, and never mutates research data, OTC structure
definitions or quant-model rules.

## 24-hour automation readiness audit

Before moving market collection or AI generation from macOS to the server, run
the read-only audit from the synchronized checkout:

```bash
cd /srv/palm-oil-daily/site
python3 server/audit_runtime.py --network
```

The audit reports Docker/API mounts, systemd timers, Python modules, repository
dependencies and unattended AI capabilities. Credential values are never
printed; only capability booleans are returned. A blocked result is expected
until the Python market-data dependencies, live-data mount and one unattended AI
backend have been configured.

## Server-owned live market data

The API should mount `/srv/palm-oil-daily/live-data` at `/site/data:ro`.
Repository synchronization owns reports, supply-demand data and forecast
metrics. Once `.server-market-ready.json` exists, the server collector owns
market quotes, exchange quotes, dynamic quant-model outputs and current
contracts; a later Git update will not overwrite them. The AI brief remains
upstream-owned until a successful server AI generation writes
`.server-ai-ready.json`, so moving market collection alone cannot freeze newer
AI briefs produced by the existing automation.

Preview the collector's session selection without changing files:

```bash
cd /srv/palm-oil-daily/site
python3 server/run_market_collector.py --dry-run
```

Production is designed to call the collector from a systemd timer every ten
minutes. A successful session writes an idempotency marker. A failed session
writes no marker, so the next timer interval retries it. AI generation remains
a separate unattended capability and must not be enabled until its backend and
credentials pass the readiness audit.

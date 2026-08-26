#!/usr/bin/env bash
set -euo pipefail

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
DEPLOY_ROOT="${PALM_OIL_DEPLOY_ROOT:-/srv/palm-oil-daily/deploy}"
LIVE_DATA_ROOT="${PALM_OIL_LIVE_DATA_ROOT:-/srv/palm-oil-daily/live-data}"
STATE_ROOT="${PALM_OIL_SERVER_STATE_ROOT:-/srv/palm-oil-daily/state}"
MARKET_RUNTIME_ROOT="${PALM_OIL_MARKET_RUNTIME_ROOT:-/srv/palm-oil-daily/market-runtime}"
AI_RUNTIME_ROOT="${PALM_OIL_AI_RUNTIME_ROOT:-/srv/palm-oil-daily/ai-runtime}"
RESEARCH_RUNTIME_ROOT="${PALM_OIL_RESEARCH_RUNTIME_ROOT:-/srv/palm-oil-daily/research-runtime}"
VENV_ROOT="${PALM_OIL_VENV_ROOT:-/srv/palm-oil-daily/venv}"
AI_ENV_FILE="${PALM_OIL_AI_ENV_FILE:-${PALM_OIL_OPENAI_ENV_FILE:-/etc/palm-oil-ai.env}}"
UNIT_ROOT="${PALM_OIL_SYSTEMD_UNIT_ROOT:-/etc/systemd/system}"
COMPOSE_FILE="${PALM_OIL_COMPOSE_FILE:-$DEPLOY_ROOT/compose.yaml}"
COMPOSE_OVERRIDE="${PALM_OIL_COMPOSE_OVERRIDE:-$DEPLOY_ROOT/compose.automation.yaml}"
PUBLIC_ACCESS_MODE="${PALM_OIL_PUBLIC_ACCESS_MODE:-private}"
REQUIREMENTS="$SITE_ROOT/server/requirements-market.txt"
MODE="${1:---dry-run}"

case "$MODE" in
  --dry-run|--apply) ;;
  *)
    echo "usage: sudo bash server/install_automation.sh [--dry-run|--apply]" >&2
    exit 2
    ;;
esac

case "$PUBLIC_ACCESS_MODE" in
  private|public) ;;
  *)
    echo "PALM_OIL_PUBLIC_ACCESS_MODE must be private or public" >&2
    exit 2
    ;;
esac

for command in python3 docker systemctl systemd-analyze flock install; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "required command is unavailable: $command" >&2
    exit 2
  }
done
docker compose version >/dev/null

for required in \
  "$SITE_ROOT/.git" \
  "$SITE_ROOT/server/enable_ai_automation.sh" \
  "$SITE_ROOT/server/run_market_watch.py" \
  "$SITE_ROOT/server/run_event_watch.py" \
  "$SITE_ROOT/server/run_supply_demand.py" \
  "$SITE_ROOT/server/run_ai_brief.py" \
  "$SITE_ROOT/server/run_research_agent.py" \
  "$SITE_ROOT/server/run_prediction_review.py" \
  "$SITE_ROOT/server/build_report_inputs.py" \
  "$SITE_ROOT/server/freeze_prepared_forecast.py" \
  "$SITE_ROOT/server/sync_live_data.py" \
  "$SITE_ROOT/server/Caddyfile" \
  "$SITE_ROOT/scripts/deploy_report.sh" \
  "$REQUIREMENTS" \
  "$COMPOSE_FILE"
do
  [[ -e "$required" ]] || {
    echo "required deployment input is missing: $required" >&2
    exit 2
  }
done

branch="$(git -c safe.directory="$SITE_ROOT" -C "$SITE_ROOT" branch --show-current)"
dirty="$(git -c safe.directory="$SITE_ROOT" -C "$SITE_ROOT" status --porcelain --untracked-files=all)"
[[ "$branch" == "main" && -z "$dirty" ]] || {
  echo "server site checkout must be a clean main branch" >&2
  exit 2
}

if [[ "$MODE" == "--dry-run" ]]; then
  python3 - "$SITE_ROOT" "$LIVE_DATA_ROOT" "$STATE_ROOT" "$MARKET_RUNTIME_ROOT" \
    "$AI_RUNTIME_ROOT" "$VENV_ROOT" "$COMPOSE_FILE" "$COMPOSE_OVERRIDE" \
    "$RESEARCH_RUNTIME_ROOT" "$PUBLIC_ACCESS_MODE" <<'PY'
import json
import sys

keys = (
    "site_root",
    "live_data_root",
    "state_root",
    "market_runtime_root",
    "ai_runtime_root",
    "venv_root",
    "compose_file",
    "compose_override",
    "research_runtime_root",
    "public_access_mode",
)
print(json.dumps(
    {
        "status": "planned",
        "mode": "dry-run",
        **dict(zip(keys, sys.argv[1:])),
        "market_timer": "every 5 minutes during exchange sessions",
        "event_timer": "every 5 minutes around the clock",
        "supply_timer": "daily official-source check",
        "ai_timer": "installed disabled until backend acceptance",
        "research_timer": "installed disabled until backend acceptance",
        "prediction_review_timer": "every 15 minutes with after-close gate",
        "web_service": "stopped" if sys.argv[-1] == "private" else "running",
    },
    sort_keys=True,
))
PY
  exit 0
fi

[[ "$(id -u)" -eq 0 ]] || {
  echo "--apply must run as root" >&2
  exit 2
}
for target in \
  "$SITE_ROOT" "$DEPLOY_ROOT" "$LIVE_DATA_ROOT" "$STATE_ROOT" \
  "$MARKET_RUNTIME_ROOT" "$AI_RUNTIME_ROOT" "$VENV_ROOT" \
  "$RESEARCH_RUNTIME_ROOT"
do
  case "$target" in
    /srv/palm-oil-daily|/srv/palm-oil-daily/*) ;;
    *)
      echo "refusing unsafe deployment path: $target" >&2
      exit 2
      ;;
  esac
done

install -d -m 0755 \
  "$LIVE_DATA_ROOT" \
  "$STATE_ROOT" \
  "$STATE_ROOT/home" \
  "$STATE_ROOT/cache"
install -d -m 0700 "$STATE_ROOT/home/.codex"
install -m 0644 "$SITE_ROOT/server/Caddyfile" "$DEPLOY_ROOT/Caddyfile"

for runtime_root in "$MARKET_RUNTIME_ROOT" "$AI_RUNTIME_ROOT" "$RESEARCH_RUNTIME_ROOT"; do
  if [[ -e "$runtime_root" && ! -d "$runtime_root/.git" ]]; then
    if [[ -d "$runtime_root" && -z "$(find "$runtime_root" -mindepth 1 -print -quit)" ]]; then
      rmdir "$runtime_root"
    else
      echo "runtime path exists but is not an empty or valid Git checkout: $runtime_root" >&2
      exit 2
    fi
  fi
  if [[ ! -d "$runtime_root/.git" ]]; then
    git clone \
      --branch main \
      --single-branch \
      --no-hardlinks \
      "$SITE_ROOT" \
      "$runtime_root"
  fi
done

if [[ ! -x "$VENV_ROOT/bin/python" ]] || \
  ! "$VENV_ROOT/bin/python" -m pip --version >/dev/null 2>&1
then
  python3 -m venv --clear "$VENV_ROOT"
fi
"$VENV_ROOT/bin/python" -m pip install \
  --disable-pip-version-check \
  --no-cache-dir \
  --requirement "$REQUIREMENTS"

python3 "$SITE_ROOT/server/sync_live_data.py" \
  --mode upstream \
  --source "$SITE_ROOT/data" \
  --target "$LIVE_DATA_ROOT"

temporary_root="$(mktemp -d /tmp/palm-oil-automation.XXXXXX)"
cleanup() {
  rm -rf "$temporary_root"
}
trap cleanup EXIT

cat >"$temporary_root/compose.automation.yaml" <<EOF
services:
  api:
    volumes:
      - $LIVE_DATA_ROOT:/site/data:ro
EOF
docker compose \
  -f "$COMPOSE_FILE" \
  -f "$temporary_root/compose.automation.yaml" \
  config >/dev/null

write_service() {
  local target="$1"
  local description="$2"
  local command="$3"
  cat >"$target" <<EOF
[Unit]
Description=$description
After=network-online.target palm-oil-site-update.service
Wants=network-online.target

[Service]
Type=oneshot
User=root
Group=root
WorkingDirectory=$SITE_ROOT
Environment=HOME=$STATE_ROOT/home
Environment=XDG_CACHE_HOME=$STATE_ROOT/cache
EnvironmentFile=-$AI_ENV_FILE
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PATH=$VENV_ROOT/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=GIT_CONFIG_COUNT=1
Environment=GIT_CONFIG_KEY_0=safe.directory
Environment=GIT_CONFIG_VALUE_0=$SITE_ROOT
ExecStart=$VENV_ROOT/bin/python $SITE_ROOT/server/$command
TimeoutStartSec=45min
UMask=0027
Nice=10
NoNewPrivileges=true
PrivateDevices=true
PrivateTmp=true
ProtectHome=read-only
ProtectSystem=strict
ReadOnlyPaths=$SITE_ROOT $VENV_ROOT
ReadWritePaths=$LIVE_DATA_ROOT $STATE_ROOT $MARKET_RUNTIME_ROOT $AI_RUNTIME_ROOT $RESEARCH_RUNTIME_ROOT
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
LockPersonality=true
EOF
}

write_timer() {
  local target="$1"
  local description="$2"
  local service="$3"
  local schedule="$4"
  local randomized_delay="$5"
  cat >"$target" <<EOF
[Unit]
Description=$description

[Timer]
OnCalendar=$schedule
AccuracySec=30s
RandomizedDelaySec=$randomized_delay
Persistent=true
Unit=$service

[Install]
WantedBy=timers.target
EOF
}

write_service \
  "$temporary_root/palm-oil-market-collector.service" \
  "Refresh palm oil market datasets into the live API mount" \
  "run_market_watch.py"
write_timer \
  "$temporary_root/palm-oil-market-collector.timer" \
  "Scan full palm oil market and events every five minutes" \
  "palm-oil-market-collector.service" \
  "*-*-* *:0/5:00" \
  "20s"
write_service \
  "$temporary_root/palm-oil-event-watch.service" \
  "Refresh cross-source oil market news and research" \
  "run_event_watch.py"
write_timer \
  "$temporary_root/palm-oil-event-watch.timer" \
  "Search cross-source oil market news and research every five minutes" \
  "palm-oil-event-watch.service" \
  "*-*-* *:2/5:00" \
  "15s"
write_service \
  "$temporary_root/palm-oil-research-agent.service" \
  "Generate governed palm oil research reports on the server" \
  "run_research_agent.py"
write_timer \
  "$temporary_root/palm-oil-research-agent.timer" \
  "Retry governed palm oil report generation every twenty minutes" \
  "palm-oil-research-agent.service" \
  "*-*-* *:07/20:00" \
  "30s"
write_service \
  "$temporary_root/palm-oil-prediction-review.service" \
  "Evaluate due palm oil forecasts from server close data" \
  "run_prediction_review.py"
write_timer \
  "$temporary_root/palm-oil-prediction-review.timer" \
  "Retry palm oil prediction review every fifteen minutes" \
  "palm-oil-prediction-review.service" \
  "*-*-* *:10/15:00" \
  "45s"
write_service \
  "$temporary_root/palm-oil-supply-demand.service" \
  "Check official palm oil supply-demand sources" \
  "run_supply_demand.py"
write_timer \
  "$temporary_root/palm-oil-supply-demand.timer" \
  "Check official palm oil supply-demand sources every day" \
  "palm-oil-supply-demand.service" \
  "*-*-* 09..23:17:00 Asia/Shanghai" \
  "30s"
write_service \
  "$temporary_root/palm-oil-ai-brief.service" \
  "Generate a source-grounded palm oil AI market brief" \
  "run_ai_brief.py"
write_timer \
  "$temporary_root/palm-oil-ai-brief.timer" \
  "Retry palm oil AI brief generation every ten minutes" \
  "palm-oil-ai-brief.service" \
  "*-*-* *:02/10:00" \
  "30s"

systemd-analyze verify \
  "$temporary_root/palm-oil-market-collector.service" \
  "$temporary_root/palm-oil-market-collector.timer" \
  "$temporary_root/palm-oil-event-watch.service" \
  "$temporary_root/palm-oil-event-watch.timer" \
  "$temporary_root/palm-oil-supply-demand.service" \
  "$temporary_root/palm-oil-supply-demand.timer" \
  "$temporary_root/palm-oil-ai-brief.service" \
  "$temporary_root/palm-oil-ai-brief.timer" \
  "$temporary_root/palm-oil-research-agent.service" \
  "$temporary_root/palm-oil-research-agent.timer" \
  "$temporary_root/palm-oil-prediction-review.service" \
  "$temporary_root/palm-oil-prediction-review.timer"

install -m 0644 "$temporary_root/compose.automation.yaml" "$COMPOSE_OVERRIDE"
for unit in \
  palm-oil-market-collector.service \
  palm-oil-market-collector.timer \
  palm-oil-event-watch.service \
  palm-oil-event-watch.timer \
  palm-oil-supply-demand.service \
  palm-oil-supply-demand.timer \
  palm-oil-ai-brief.service \
  palm-oil-ai-brief.timer \
  palm-oil-research-agent.service \
  palm-oil-research-agent.timer \
  palm-oil-prediction-review.service \
  palm-oil-prediction-review.timer
do
  install -m 0644 "$temporary_root/$unit" "$UNIT_ROOT/$unit"
done

systemctl daemon-reload
if [[ "$PUBLIC_ACCESS_MODE" == "private" ]]; then
  docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" stop web || true
  docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" up -d --no-deps api
  docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" stop web || true
else
  docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" up -d api web
fi
systemctl enable --now palm-oil-market-collector.timer
systemctl enable --now palm-oil-event-watch.timer
systemctl enable --now palm-oil-supply-demand.timer
systemctl enable --now palm-oil-prediction-review.timer
systemctl start palm-oil-market-collector.service
systemctl start palm-oil-event-watch.service
systemctl start palm-oil-supply-demand.service
systemctl start palm-oil-prediction-review.service

systemctl --no-pager --full status palm-oil-market-collector.service || true
systemctl --no-pager list-timers palm-oil-market-collector.timer
systemctl --no-pager list-timers palm-oil-event-watch.timer
systemctl --no-pager list-timers palm-oil-supply-demand.timer
systemctl --no-pager list-timers palm-oil-prediction-review.timer
docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" ps
set +e
python3 "$SITE_ROOT/server/audit_runtime.py" --access-mode "$PUBLIC_ACCESS_MODE"
audit_status=$?
set -e
if [[ "$audit_status" -ne 0 && "$audit_status" -ne 2 ]]; then
  exit "$audit_status"
fi

echo "AI and research service units installed but their timers intentionally remain disabled until authenticated backend acceptance."
if [[ "$PUBLIC_ACCESS_MODE" == "private" ]]; then
  echo "Public web service is stopped; internal API and collectors remain active."
fi

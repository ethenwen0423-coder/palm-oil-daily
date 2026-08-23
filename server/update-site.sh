#!/bin/sh
set -eu

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
DEPLOY_ROOT="${PALM_OIL_DEPLOY_ROOT:-/srv/palm-oil-daily/deploy}"
RUNNER_PATH="${PALM_OIL_UPDATE_RUNNER:-/srv/palm-oil-daily/update-site.sh}"
RUNNER_CANDIDATE="${RUNNER_PATH}.new"
LIVE_DATA_ROOT="${PALM_OIL_LIVE_DATA_ROOT:-/srv/palm-oil-daily/live-data}"
STATE_ROOT="${PALM_OIL_SERVER_STATE_ROOT:-/srv/palm-oil-daily/state}"
COMPOSE_FILE="${PALM_OIL_COMPOSE_FILE:-$DEPLOY_ROOT/compose.yaml}"
COMPOSE_OVERRIDE="${PALM_OIL_COMPOSE_OVERRIDE:-$DEPLOY_ROOT/compose.automation.yaml}"
GIT_FETCH_TIMEOUT_SECONDS="${PALM_OIL_GIT_FETCH_TIMEOUT_SECONDS:-75}"
PUBLIC_ACCESS_MODE="${PALM_OIL_PUBLIC_ACCESS_MODE:-private}"

case "$PUBLIC_ACCESS_MODE" in
  private|public) ;;
  *)
    echo "PALM_OIL_PUBLIC_ACCESS_MODE must be private or public" >&2
    exit 2
    ;;
esac

mkdir -p "$STATE_ROOT"
exec 9>"$STATE_ROOT/automation.lock"
if ! flock -n 9; then
  echo '{"status":"busy","reason":"server automation lock is held","retry":true}'
  exit 0
fi

cd "$SITE_ROOT"
timeout "${GIT_FETCH_TIMEOUT_SECONDS}s" git fetch --depth 1 origin main
git reset --hard FETCH_HEAD

for payload in \
  data/reports.json \
  data/oil_futures.json \
  data/exchange_futures.json \
  data/quant_model_signals.json \
  data/supply-demand.json \
  data/contracts/current_contracts.json \
  data/forecast/metrics/latest.json \
  data/forecast/metrics/20d.json \
  data/forecast/metrics/60d.json \
  data/forecast/feedback/latest.json \
  data/review/latest_review.json \
  data/market_assistant_brief.json
do
  python3 -m json.tool "$payload" >/dev/null
done

python3 server/sync_live_data.py \
  --mode upstream \
  --source data \
  --target "$LIVE_DATA_ROOT"

api_changed=false
for api_source in server/api.py server/contract_analysis.py
do
  api_name="$(basename "$api_source")"
  if ! cmp -s "$api_source" "$DEPLOY_ROOT/$api_name"; then
    cp "$api_source" "$DEPLOY_ROOT/$api_name"
    api_changed=true
  fi
done

web_changed=false
if ! cmp -s server/Caddyfile "$DEPLOY_ROOT/Caddyfile"; then
  cp server/Caddyfile "$DEPLOY_ROOT/Caddyfile"
  web_changed=true
fi

if ! cmp -s server/update-site.sh "$RUNNER_PATH"; then
  cp server/update-site.sh "$RUNNER_CANDIDATE"
  chmod 755 "$RUNNER_CANDIDATE"
  mv -f "$RUNNER_CANDIDATE" "$RUNNER_PATH"
fi

compose() {
  if [ -f "$COMPOSE_OVERRIDE" ]; then
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" "$@"
  else
    docker compose -f "$COMPOSE_FILE" "$@"
  fi
}

if [ "$PUBLIC_ACCESS_MODE" = private ]; then
  compose stop web || true
  compose up -d --no-deps api
  if [ "$api_changed" = true ]; then
    compose restart api
  fi
  compose stop web || true
else
  compose up -d api web
  if [ "$api_changed" = true ]; then
    compose restart api
  fi
  if [ "$web_changed" = true ]; then
    compose restart web
  fi
fi

check_endpoint() {
  endpoint="$1"
  attempt=1
  while [ "$attempt" -le 10 ]; do
    if [ "$PUBLIC_ACCESS_MODE" = private ]; then
      if compose exec -T api python3 -c \
        'import os,sys,urllib.request; port=os.environ.get("PALM_OIL_API_PORT", "8000"); urllib.request.urlopen(f"http://127.0.0.1:{port}{sys.argv[1]}", timeout=5).read()' \
        "$endpoint" >/dev/null
      then
        return 0
      fi
    elif curl -fsS --resolve palm.vinsontesla.com:443:127.0.0.1 \
      "https://palm.vinsontesla.com$endpoint" >/dev/null
    then
      return 0
    fi
    sleep 2
    attempt=$((attempt + 1))
  done
  return 1
}

check_endpoint /healthz
check_endpoint /api/status

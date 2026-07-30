#!/bin/sh
set -eu

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
DEPLOY_ROOT="${PALM_OIL_DEPLOY_ROOT:-/srv/palm-oil-daily/deploy}"
RUNNER_PATH="${PALM_OIL_UPDATE_RUNNER:-/srv/palm-oil-daily/update-site.sh}"

cd "$SITE_ROOT"
git fetch --depth 1 origin main
git reset --hard FETCH_HEAD

for payload in \
  data/reports.json \
  data/oil_futures.json \
  data/exchange_futures.json \
  data/quant_model_signals.json \
  data/supply-demand.json
do
  python3 -m json.tool "$payload" >/dev/null
done

api_changed=false
if ! cmp -s server/api.py "$DEPLOY_ROOT/api.py"; then
  cp server/api.py "$DEPLOY_ROOT/api.py"
  api_changed=true
fi

if ! cmp -s server/update-site.sh "$RUNNER_PATH"; then
  cp server/update-site.sh "$RUNNER_PATH"
  chmod 755 "$RUNNER_PATH"
fi

if [ "$api_changed" = true ]; then
  docker compose -f "$DEPLOY_ROOT/compose.yaml" restart api
fi

check_endpoint() {
  endpoint="$1"
  attempt=1
  while [ "$attempt" -le 10 ]; do
    if curl -fsS --resolve palm.vinsontesla.com:443:127.0.0.1 \
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

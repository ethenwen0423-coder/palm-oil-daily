#!/usr/bin/env bash
set -euo pipefail

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
LIVE_DATA_ROOT="${PALM_OIL_LIVE_DATA_ROOT:-/srv/palm-oil-daily/live-data}"
STATE_ROOT="${PALM_OIL_SERVER_STATE_ROOT:-/srv/palm-oil-daily/state}"
VENV_ROOT="${PALM_OIL_VENV_ROOT:-/srv/palm-oil-daily/venv}"
MODE="${1:---status}"
CODEX_HOME_ROOT="$STATE_ROOT/home/.codex"

case "$MODE" in
  --status|--login|--enable|--disable) ;;
  *)
    echo "usage: sudo bash server/enable_ai_automation.sh [--status|--login|--enable|--disable]" >&2
    exit 2
    ;;
esac

resolve_codex_bin() {
  if [[ -n "${CODEX_BIN:-}" && -x "${CODEX_BIN}" ]]; then
    printf '%s\n' "$CODEX_BIN"
    return 0
  fi
  command -v codex 2>/dev/null || true
}

codex_bin="$(resolve_codex_bin)"
[[ -n "$codex_bin" ]] || {
  echo "Codex CLI is unavailable on the server" >&2
  exit 2
}

codex_env=(
  env
  "HOME=$STATE_ROOT/home"
  "CODEX_HOME=$CODEX_HOME_ROOT"
  "XDG_CACHE_HOME=$STATE_ROOT/cache"
  "CODEX_BIN=$codex_bin"
)

login_status() {
  "${codex_env[@]}" "$codex_bin" login status >/dev/null 2>&1
}

if [[ "$MODE" == "--status" ]]; then
  authenticated=false
  timer_enabled=false
  timer_active=false
  login_status && authenticated=true
  systemctl is-enabled --quiet palm-oil-ai-brief.timer && timer_enabled=true
  systemctl is-active --quiet palm-oil-ai-brief.timer && timer_active=true
  python3 - "$authenticated" "$timer_enabled" "$timer_active" <<'PY'
import json
import sys

print(json.dumps(
    {
        "authenticated": sys.argv[1] == "true",
        "timer_enabled": sys.argv[2] == "true",
        "timer_active": sys.argv[3] == "true",
    },
    sort_keys=True,
))
PY
  exit 0
fi

[[ "$(id -u)" -eq 0 ]] || {
  echo "$MODE must run as root" >&2
  exit 2
}

install -d -m 0755 "$STATE_ROOT/home" "$STATE_ROOT/cache"
install -d -m 0700 "$CODEX_HOME_ROOT"

if [[ "$MODE" == "--login" ]]; then
  exec "${codex_env[@]}" "$codex_bin" login --device-auth
fi

if [[ "$MODE" == "--disable" ]]; then
  systemctl disable --now palm-oil-ai-brief.timer
  echo '{"status":"disabled","timer":"palm-oil-ai-brief.timer"}'
  exit 0
fi

systemctl disable --now palm-oil-ai-brief.timer >/dev/null 2>&1 || true
login_status || {
  echo "Codex CLI is not authenticated in the server automation credential directory" >&2
  exit 2
}
[[ -x "$VENV_ROOT/bin/python" ]] || {
  echo "server Python runtime is unavailable: $VENV_ROOT/bin/python" >&2
  exit 2
}

"${codex_env[@]}" "$VENV_ROOT/bin/python" \
  "$SITE_ROOT/server/run_ai_brief.py" \
  --site-root "$SITE_ROOT" \
  --live-data-root "$LIVE_DATA_ROOT" \
  --state-root "$STATE_ROOT"

[[ -s "$LIVE_DATA_ROOT/.server-ai-ready.json" ]] || {
  echo "real AI generation did not publish the server ownership marker" >&2
  exit 2
}

systemctl enable --now palm-oil-ai-brief.timer
systemctl --no-pager --full status palm-oil-ai-brief.timer
echo '{"status":"enabled","timer":"palm-oil-ai-brief.timer","acceptance":"real_generation_passed"}'

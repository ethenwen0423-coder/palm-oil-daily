#!/usr/bin/env bash
set -euo pipefail

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
LIVE_DATA_ROOT="${PALM_OIL_LIVE_DATA_ROOT:-/srv/palm-oil-daily/live-data}"
STATE_ROOT="${PALM_OIL_SERVER_STATE_ROOT:-/srv/palm-oil-daily/state}"
VENV_ROOT="${PALM_OIL_VENV_ROOT:-/srv/palm-oil-daily/venv}"
MODE="${1:---status}"
CODEX_HOME_ROOT="$STATE_ROOT/home/.codex"

case "$MODE" in
  --status|--login|--login-api-key|--enable|--disable) ;;
  *)
    echo "usage: sudo bash server/enable_ai_automation.sh [--status|--login|--login-api-key|--enable|--disable]" >&2
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

codex_env=(
  env
  "HOME=$STATE_ROOT/home"
  "CODEX_HOME=$CODEX_HOME_ROOT"
  "XDG_CACHE_HOME=$STATE_ROOT/cache"
  "CODEX_BIN=$codex_bin"
)

login_status() {
  [[ -n "$codex_bin" ]] && \
    "${codex_env[@]}" "$codex_bin" login status >/dev/null 2>&1
}

if [[ "$MODE" == "--status" ]]; then
  authenticated=false
  timer_enabled=false
  timer_active=false
  research_timer_enabled=false
  research_timer_active=false
  login_status && authenticated=true
  systemctl is-enabled --quiet palm-oil-ai-brief.timer && timer_enabled=true
  systemctl is-active --quiet palm-oil-ai-brief.timer && timer_active=true
  systemctl is-enabled --quiet palm-oil-research-agent.timer && research_timer_enabled=true
  systemctl is-active --quiet palm-oil-research-agent.timer && research_timer_active=true
  cli_present=false
  [[ -n "$codex_bin" ]] && cli_present=true
  python3 - "$cli_present" "$authenticated" "$timer_enabled" "$timer_active" \
    "$research_timer_enabled" "$research_timer_active" <<'PY'
import json
import sys

print(json.dumps(
    {
        "cli_present": sys.argv[1] == "true",
        "authenticated": sys.argv[2] == "true",
        "timer_enabled": sys.argv[3] == "true",
        "timer_active": sys.argv[4] == "true",
        "research_timer_enabled": sys.argv[5] == "true",
        "research_timer_active": sys.argv[6] == "true",
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

if [[ "$MODE" == "--login-api-key" ]]; then
  api_key="${OPENAI_API_KEY:-}"
  if [[ -z "$api_key" && ! -t 0 ]]; then
    IFS= read -r api_key || true
  fi
  if [[ -z "$api_key" ]]; then
    read -r -s -p "OpenAI API key: " api_key
    printf '\n' >&2
  fi
  [[ -n "$api_key" ]] || {
    echo "OpenAI API key was not provided" >&2
    exit 2
  }
  printf '%s' "$api_key" | "${codex_env[@]}" "$codex_bin" login --with-api-key
  unset api_key
  exit 0
fi

if [[ "$MODE" == "--disable" ]]; then
  systemctl disable --now palm-oil-ai-brief.timer
  systemctl disable --now palm-oil-research-agent.timer
  echo '{"status":"disabled","timers":["palm-oil-ai-brief.timer","palm-oil-research-agent.timer"]}'
  exit 0
fi

[[ -n "$codex_bin" ]] || {
  echo "Codex CLI is unavailable on the server" >&2
  exit 2
}

systemctl disable --now palm-oil-ai-brief.timer >/dev/null 2>&1 || true
systemctl disable --now palm-oil-research-agent.timer >/dev/null 2>&1 || true
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

"${codex_env[@]}" "$VENV_ROOT/bin/python" \
  "$SITE_ROOT/server/run_research_agent.py" \
  --site-root "$SITE_ROOT" \
  --live-data-root "$LIVE_DATA_ROOT" \
  --state-root "$STATE_ROOT" \
  --force-kind weekend \
  --acceptance-only \
  --attempts 1

[[ -s "$STATE_ROOT/research-backend.accepted.json" ]] || {
  echo "real research model acceptance did not publish its state marker" >&2
  exit 2
}

systemctl enable --now palm-oil-ai-brief.timer
systemctl enable --now palm-oil-research-agent.timer
systemctl --no-pager --full status palm-oil-ai-brief.timer palm-oil-research-agent.timer
echo '{"status":"enabled","timers":["palm-oil-ai-brief.timer","palm-oil-research-agent.timer"],"acceptance":"real_generation_and_report_draft_passed"}'

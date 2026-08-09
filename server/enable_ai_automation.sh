#!/usr/bin/env bash
set -euo pipefail

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
LIVE_DATA_ROOT="${PALM_OIL_LIVE_DATA_ROOT:-/srv/palm-oil-daily/live-data}"
STATE_ROOT="${PALM_OIL_SERVER_STATE_ROOT:-/srv/palm-oil-daily/state}"
VENV_ROOT="${PALM_OIL_VENV_ROOT:-/srv/palm-oil-daily/venv}"
OPENAI_ENV_FILE="${PALM_OIL_OPENAI_ENV_FILE:-/etc/palm-oil-ai.env}"
MODE="${1:---status}"

case "$MODE" in
  --status|--set-api-key|--enable|--disable) ;;
  *)
    echo "usage: sudo bash server/enable_ai_automation.sh [--status|--set-api-key|--enable|--disable]" >&2
    exit 2
    ;;
esac

api_key_configured() {
  [[ -f "$OPENAI_ENV_FILE" ]] &&
    [[ "$(stat -c '%U:%a' "$OPENAI_ENV_FILE" 2>/dev/null || true)" == "root:600" ]] &&
    grep -q '^OPENAI_API_KEY=.' "$OPENAI_ENV_FILE"
}

load_api_key() {
  api_key="$(sed -n 's/^OPENAI_API_KEY=//p' "$OPENAI_ENV_FILE" | head -n 1)"
  [[ -n "$api_key" ]]
}

if [[ "$MODE" == "--status" ]]; then
  api_key_present=false
  timer_enabled=false
  timer_active=false
  research_timer_enabled=false
  research_timer_active=false
  api_key_configured && api_key_present=true
  systemctl is-enabled --quiet palm-oil-ai-brief.timer && timer_enabled=true
  systemctl is-active --quiet palm-oil-ai-brief.timer && timer_active=true
  systemctl is-enabled --quiet palm-oil-research-agent.timer && research_timer_enabled=true
  systemctl is-active --quiet palm-oil-research-agent.timer && research_timer_active=true
  python3 - "$api_key_present" "$timer_enabled" "$timer_active" \
    "$research_timer_enabled" "$research_timer_active" <<'PY'
import json
import sys

print(json.dumps(
    {
        "openai_api_key_configured": sys.argv[1] == "true",
        "timer_enabled": sys.argv[2] == "true",
        "timer_active": sys.argv[3] == "true",
        "research_timer_enabled": sys.argv[4] == "true",
        "research_timer_active": sys.argv[5] == "true",
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

if [[ "$MODE" == "--set-api-key" ]]; then
  [[ -t 0 && -t 1 ]] || {
    echo "--set-api-key must be run in an interactive terminal" >&2
    exit 2
  }
  systemctl disable --now palm-oil-ai-brief.timer >/dev/null 2>&1 || true
  systemctl disable --now palm-oil-research-agent.timer >/dev/null 2>&1 || true
  read -r -s -p "OpenAI API key: " api_key
  printf '\n'
  [[ "$api_key" == sk-* ]] || {
    unset api_key
    echo "API key format is invalid" >&2
    exit 2
  }
  temporary="$(mktemp "${OPENAI_ENV_FILE}.tmp.XXXXXX")"
  trap 'rm -f "$temporary"' EXIT
  umask 077
  printf 'OPENAI_API_KEY=%s\n' "$api_key" >"$temporary"
  printf 'PALM_OIL_AI_MODEL=%s\n' "${PALM_OIL_AI_MODEL:-gpt-5.2}" >>"$temporary"
  unset api_key
  install -o root -g root -m 0600 "$temporary" "$OPENAI_ENV_FILE"
  rm -f "$temporary"
  trap - EXIT
  echo '{"status":"configured","credential":"openai-api-key","timers":"disabled"}'
  exit 0
fi

if [[ "$MODE" == "--disable" ]]; then
  systemctl disable --now palm-oil-ai-brief.timer
  systemctl disable --now palm-oil-research-agent.timer
  echo '{"status":"disabled","timers":["palm-oil-ai-brief.timer","palm-oil-research-agent.timer"]}'
  exit 0
fi

systemctl disable --now palm-oil-ai-brief.timer >/dev/null 2>&1 || true
systemctl disable --now palm-oil-research-agent.timer >/dev/null 2>&1 || true
api_key_configured && load_api_key || {
  echo "OpenAI API key is not configured in the protected server environment file" >&2
  exit 2
}
[[ -x "$VENV_ROOT/bin/python" ]] || {
  unset api_key
  echo "server Python runtime is unavailable: $VENV_ROOT/bin/python" >&2
  exit 2
}

env "OPENAI_API_KEY=$api_key" "$VENV_ROOT/bin/python" \
  "$SITE_ROOT/server/run_ai_brief.py" \
  --site-root "$SITE_ROOT" \
  --live-data-root "$LIVE_DATA_ROOT" \
  --state-root "$STATE_ROOT"

[[ -s "$LIVE_DATA_ROOT/.server-ai-ready.json" ]] || {
  unset api_key
  echo "real AI generation did not publish the server ownership marker" >&2
  exit 2
}

env "OPENAI_API_KEY=$api_key" "$VENV_ROOT/bin/python" \
  "$SITE_ROOT/server/run_research_agent.py" \
  --site-root "$SITE_ROOT" \
  --live-data-root "$LIVE_DATA_ROOT" \
  --state-root "$STATE_ROOT" \
  --force-kind weekend \
  --acceptance-only \
  --attempts 1
unset api_key

[[ -s "$STATE_ROOT/research-backend.accepted.json" ]] || {
  echo "real research model acceptance did not publish its state marker" >&2
  exit 2
}

systemctl enable --now palm-oil-ai-brief.timer
systemctl enable --now palm-oil-research-agent.timer
systemctl --no-pager --full status palm-oil-ai-brief.timer palm-oil-research-agent.timer
echo '{"status":"enabled","timers":["palm-oil-ai-brief.timer","palm-oil-research-agent.timer"],"acceptance":"real_generation_and_report_draft_passed"}'

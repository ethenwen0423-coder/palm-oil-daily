#!/usr/bin/env bash
set -euo pipefail

SITE_ROOT="${PALM_OIL_SITE_ROOT:-/srv/palm-oil-daily/site}"
LIVE_DATA_ROOT="${PALM_OIL_LIVE_DATA_ROOT:-/srv/palm-oil-daily/live-data}"
STATE_ROOT="${PALM_OIL_SERVER_STATE_ROOT:-/srv/palm-oil-daily/state}"
VENV_ROOT="${PALM_OIL_VENV_ROOT:-/srv/palm-oil-daily/venv}"
AI_ENV_FILE="${PALM_OIL_AI_ENV_FILE:-${PALM_OIL_OPENAI_ENV_FILE:-/etc/palm-oil-ai.env}}"
MODE="${1:---status}"

case "$MODE" in
  --status|--set-api-key|--set-deepseek-api-key|--enable|--disable) ;;
  *)
    echo "usage: sudo bash server/enable_ai_automation.sh [--status|--set-api-key|--set-deepseek-api-key|--enable|--disable]" >&2
    exit 2
    ;;
esac

model_credential_configured() {
  [[ -f "$AI_ENV_FILE" ]] &&
    [[ "$(stat -c '%U:%a' "$AI_ENV_FILE" 2>/dev/null || true)" == "root:600" ]] &&
    grep -Eq '^(PALM_OIL_AI_API_KEY|OPENAI_API_KEY|DEEPSEEK_API_KEY)=.' "$AI_ENV_FILE"
}

load_api_environment() {
  while IFS='=' read -r name value; do
    case "$name" in
      PALM_OIL_AI_PROVIDER|PALM_OIL_AI_API_STYLE|PALM_OIL_AI_ENDPOINT|\
      PALM_OIL_AI_MODEL|PALM_OIL_RESEARCH_AI_MODEL|PALM_OIL_AI_MAX_TOKENS|\
      PALM_OIL_AI_API_KEY|OPENAI_API_KEY|DEEPSEEK_API_KEY)
        export "$name=$value"
        ;;
    esac
  done <"$AI_ENV_FILE"
}

if [[ "$MODE" == "--status" ]]; then
  api_key_present=false
  provider="missing"
  timer_enabled=false
  timer_active=false
  research_timer_enabled=false
  research_timer_active=false
  if model_credential_configured; then
    api_key_present=true
    provider="$(sed -n 's/^PALM_OIL_AI_PROVIDER=//p' "$AI_ENV_FILE" | head -n 1)"
    [[ -n "$provider" ]] || provider="openai"
  fi
  systemctl is-enabled --quiet palm-oil-ai-brief.timer && timer_enabled=true
  systemctl is-active --quiet palm-oil-ai-brief.timer && timer_active=true
  systemctl is-enabled --quiet palm-oil-research-agent.timer && research_timer_enabled=true
  systemctl is-active --quiet palm-oil-research-agent.timer && research_timer_active=true
  python3 - "$api_key_present" "$provider" "$timer_enabled" "$timer_active" \
    "$research_timer_enabled" "$research_timer_active" <<'PY'
import json
import sys

print(json.dumps(
    {
        "model_api_key_configured": sys.argv[1] == "true",
        "model_provider": sys.argv[2],
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

if [[ "$MODE" == "--set-api-key" || "$MODE" == "--set-deepseek-api-key" ]]; then
  [[ -t 0 && -t 1 ]] || {
    echo "--set-api-key must be run in an interactive terminal" >&2
    exit 2
  }
  systemctl disable --now palm-oil-ai-brief.timer >/dev/null 2>&1 || true
  systemctl disable --now palm-oil-research-agent.timer >/dev/null 2>&1 || true
  provider="openai"
  prompt="OpenAI API key: "
  model="${PALM_OIL_AI_MODEL:-gpt-5.2}"
  endpoint="https://api.openai.com/v1/responses"
  style="responses"
  if [[ "$MODE" == "--set-deepseek-api-key" ]]; then
    provider="deepseek"
    prompt="DeepSeek API key: "
    model="${PALM_OIL_AI_MODEL:-deepseek-v4-pro}"
    endpoint="https://api.deepseek.com/chat/completions"
    style="chat-completions"
  fi
  read -r -s -p "$prompt" api_key
  printf '\n'
  [[ "$api_key" == sk-* ]] || {
    unset api_key
    echo "API key format is invalid" >&2
    exit 2
  }
  temporary="$(mktemp "${AI_ENV_FILE}.tmp.XXXXXX")"
  trap 'rm -f "$temporary"' EXIT
  umask 077
  printf 'PALM_OIL_AI_PROVIDER=%s\n' "$provider" >"$temporary"
  printf 'PALM_OIL_AI_API_STYLE=%s\n' "$style" >>"$temporary"
  printf 'PALM_OIL_AI_ENDPOINT=%s\n' "$endpoint" >>"$temporary"
  printf 'PALM_OIL_AI_MODEL=%s\n' "$model" >>"$temporary"
  printf 'PALM_OIL_AI_API_KEY=%s\n' "$api_key" >>"$temporary"
  unset api_key
  install -o root -g root -m 0600 "$temporary" "$AI_ENV_FILE"
  rm -f "$temporary"
  trap - EXIT
  python3 - "$provider" <<'PY'
import json
import sys
print(json.dumps({"status": "configured", "credential": "model-api-key", "provider": sys.argv[1], "timers": "disabled"}, sort_keys=True))
PY
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
model_credential_configured && load_api_environment || {
  echo "model API key is not configured in the protected server environment file" >&2
  exit 2
}
[[ -x "$VENV_ROOT/bin/python" ]] || {
  echo "server Python runtime is unavailable: $VENV_ROOT/bin/python" >&2
  exit 2
}

"$VENV_ROOT/bin/python" \
  "$SITE_ROOT/server/run_ai_brief.py" \
  --site-root "$SITE_ROOT" \
  --live-data-root "$LIVE_DATA_ROOT" \
  --state-root "$STATE_ROOT"

[[ -s "$LIVE_DATA_ROOT/.server-ai-ready.json" ]] || {
  echo "real AI generation did not publish the server ownership marker" >&2
  exit 2
}

"$VENV_ROOT/bin/python" \
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

#!/usr/bin/env bash
set -euo pipefail

LABEL="com.vinsontesla.palm-oil-prediction-review"
RUNTIME_ROOT="${PALM_OIL_PREDICTION_RUNTIME_ROOT:-$HOME/Sites/palm-oil-daily-runtime}"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Application Support/VinsonTesla/palm-oil-prediction-review"
RUNNER="$LOG_DIR/run-prediction-review.sh"
TIMEZONE="Asia/Shanghai"
DRY_RUN=false
PERSISTENCE_CONFIRMED=false

usage() {
  echo "usage: $0 [--dry-run] [--confirm-persistence-reviewed]" >&2
}

while (($#)); do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    --confirm-persistence-reviewed)
      PERSISTENCE_CONFIRMED=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 64
      ;;
  esac
  shift
done

DEPENDENCIES=(
  "scripts/prediction_review_watchdog.py"
  "scripts/review_prediction.py"
  "skills/forecast_tracking_skill/scripts/evaluate_forecast.py"
  "skills/forecast_tracking_skill/scripts/build_metrics.py"
  "skills/forecast_tracking_skill/scripts/build_generation_feedback.py"
  "skills/forecast_tracking_skill/scripts/validate_forecast.py"
  "skills/forecast_tracking_skill/scripts/prune_forecast_artifacts.py"
  "scripts/publish_prediction_review.sh"
  "data/forecast/daily"
  "data/forecast/evaluated"
  "data/forecast/metrics"
  "data/forecast/feedback"
  "data/review/daily"
)
PERSISTENT_OUTPUTS=(
  "data/forecast/evaluated/YYYY-MM-DD.json"
  "data/forecast/metrics/latest.json"
  "data/forecast/metrics/20d.json"
  "data/forecast/metrics/60d.json"
  "data/forecast/feedback/latest.json"
  "data/review/daily/YYYY-MM-DD.json"
  "data/review/latest_review.json"
)

MISSING=()
for relative_path in "${DEPENDENCIES[@]}"; do
  if [[ ! -e "$RUNTIME_ROOT/$relative_path" ]]; then
    MISSING+=("$relative_path")
  fi
done

DIRTY_WORKTREE=true
if [[ -d "$RUNTIME_ROOT/.git" ]] && [[ -z "$(git -C "$RUNTIME_ROOT" status --porcelain=v1 2>/dev/null)" ]]; then
  DIRTY_WORKTREE=false
fi

emit_summary() {
  local status="$1"
  local next_action="$2"
  local files_written="$3"
  local launchctl_called="$4"
  local missing_text persistent_text
  missing_text="$(printf '%s\n' "${MISSING[@]-}")"
  persistent_text="$(printf '%s\n' "${PERSISTENT_OUTPUTS[@]}")"
  STATUS="$status" \
  NEXT_ACTION="$next_action" \
  FILES_WRITTEN="$files_written" \
  LAUNCHCTL_CALLED="$launchctl_called" \
  MISSING_TEXT="$missing_text" \
  PERSISTENT_TEXT="$persistent_text" \
  DRY_RUN_VALUE="$DRY_RUN" \
  DIRTY_VALUE="$DIRTY_WORKTREE" \
  PERSISTENCE_VALUE="$PERSISTENCE_CONFIRMED" \
  LABEL_VALUE="$LABEL" \
  PLIST_VALUE="$PLIST" \
  ROOT_VALUE="$RUNTIME_ROOT" \
  LOG_DIR_VALUE="$LOG_DIR" \
  RUNNER_VALUE="$RUNNER" \
  TIMEZONE_VALUE="$TIMEZONE" \
  python3 - <<'PY'
import json
import os

def boolean(name: str) -> bool:
    return os.environ[name].lower() == "true"

missing = [item for item in os.environ["MISSING_TEXT"].splitlines() if item]
persistent = [item for item in os.environ["PERSISTENT_TEXT"].splitlines() if item]
payload = {
    "status": os.environ["STATUS"],
    "dry_run": boolean("DRY_RUN_VALUE"),
    "installation_blocked_by_dirty_worktree": boolean("DIRTY_VALUE"),
    "persistence_confirmation_required": True,
    "persistence_confirmed": boolean("PERSISTENCE_VALUE"),
    "launch_agent_label": os.environ["LABEL_VALUE"],
    "plist_path": os.environ["PLIST_VALUE"],
    "schedule": ["RunAtLoad", "every 15 minutes", "same-day reviews become due after 15:20"],
    "timezone": os.environ["TIMEZONE_VALUE"],
    "working_directory": os.environ["ROOT_VALUE"],
    "log_directory": os.environ["LOG_DIR_VALUE"],
    "runner_path": os.environ["RUNNER_VALUE"],
    "command": "python3 scripts/prediction_review_watchdog.py",
    "publish_command": "bash scripts/publish_prediction_review.sh --publish --confirm-persistence-reviewed --date <Asia/Shanghai current date>",
    "missing_dependencies": missing,
    "persistent_outputs_requiring_manual_confirmation": persistent,
    "files_written": boolean("FILES_WRITTEN"),
    "launchctl_called": boolean("LAUNCHCTL_CALLED"),
    "next_action": os.environ["NEXT_ACTION"],
}
print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
PY
}

if ((${#MISSING[@]} > 0)); then
  emit_summary "blocked" "补齐缺失依赖后重新执行dry-run" false false
  exit 2
fi

if [[ "$DIRTY_WORKTREE" == true ]]; then
  emit_summary "blocked" "先人工审查并提交当前改动，再执行非dry-run安装" false false
  exit 2
fi

if [[ "$DRY_RUN" == true ]]; then
  emit_summary "ok" "工作区干净；人工确认产物持久化方式后，使用--confirm-persistence-reviewed执行正式安装" false false
  exit 0
fi

if [[ "$PERSISTENCE_CONFIRMED" != true ]]; then
  emit_summary "blocked" "先人工确认评估、指标、复盘和快照文件的持久化发布方式，再传入--confirm-persistence-reviewed" false false
  exit 2
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

cat > "$RUNNER" <<'RUNNER'
#!/usr/bin/env bash
set -euo pipefail

ROOT="__RUNTIME_ROOT__"
export PALM_OIL_PREDICTION_RUNTIME_ROOT="$ROOT"
exec python3 "$ROOT/scripts/prediction_review_watchdog.py"
RUNNER
python3 - "$RUNNER" "$RUNTIME_ROOT" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(
    path.read_text(encoding="utf-8").replace("__RUNTIME_ROOT__", sys.argv[2]),
    encoding="utf-8",
)
PY
chmod 755 "$RUNNER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNNER</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$RUNTIME_ROOT</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>900</integer>
  <key>ThrottleInterval</key>
  <integer>60</integer>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/stderr.log</string>
</dict>
</plist>
PLIST
chmod 644 "$PLIST"
plutil -lint "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl enable "gui/$(id -u)/$LABEL"
launchctl bootstrap "gui/$(id -u)" "$PLIST"

emit_summary "installed" "验证LaunchAgent状态、RunAtLoad恢复和最新metrics日期" true true

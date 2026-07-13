#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.palm-oil-daily-review.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/palm-oil-daily-review.sh"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$SUPPORT_DIR"

if [[ "$ROOT" != "$RUNTIME_ROOT" ]]; then
  mkdir -p "$(dirname "$RUNTIME_ROOT")"
  if [[ ! -d "$RUNTIME_ROOT/.git" ]]; then
    git clone "$(git -C "$ROOT" remote get-url origin)" "$RUNTIME_ROOT"
  else
    git -C "$RUNTIME_ROOT" pull --ff-only
  fi
fi

cat > "$RUNNER" <<RUNNER
#!/usr/bin/env bash
set -euo pipefail

PRIVATE_ENV="$SUPPORT_DIR/private.env"
if [[ -f "\$PRIVATE_ENV" ]]; then
  set -a
  source "\$PRIVATE_ENV"
  set +a
fi

ROOT="$RUNTIME_ROOT"
REPORT_DATE="\$(TZ=Asia/Shanghai date +%F)"
WEEKDAY="\$(TZ=Asia/Shanghai date +%u)"
LOG="$SUPPORT_DIR/palm-oil-daily-review.check.log"

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] review \$REPORT_DATE" >> "\$LOG"

if (( WEEKDAY < 1 || WEEKDAY > 5 )); then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] not weekday, skip daily review" >> "\$LOG"
  exit 0
fi

cd "\$ROOT"
git pull --ff-only >> "\$LOG" 2>&1
python3 scripts/review_prediction.py --date "\$REPORT_DATE" >> "\$LOG" 2>&1
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] review complete" >> "\$LOG"
RUNNER
chmod +x "$RUNNER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.vinsontesla.palm-oil-daily-review</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>5</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>$SUPPORT_DIR/palm-oil-daily-review.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$SUPPORT_DIR/palm-oil-daily-review.stderr.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.vinsontesla.palm-oil-daily-review"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/com.vinsontesla.palm-oil-daily-review" | sed -n '1,80p'

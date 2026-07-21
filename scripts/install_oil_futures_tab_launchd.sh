#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.oil-futures-tab.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/oil-futures-tab.sh"

mkdir -p "$HOME/Library/LaunchAgents" "$SUPPORT_DIR"

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

ROOT="$RUNTIME_ROOT"
SUPPORT_DIR="$SUPPORT_DIR"
STATE_DIR="\$SUPPORT_DIR/market-refresh-state"
LOG="\$SUPPORT_DIR/oil-futures-tab.check.log"
TODAY="\$(TZ=Asia/Shanghai date +%F)"
WEEKDAY="\$(TZ=Asia/Shanghai date +%u)"
HOUR="\$(TZ=Asia/Shanghai date +%H)"
MINUTE="\$(TZ=Asia/Shanghai date +%M)"
MINUTES=\$((10#\$HOUR * 60 + 10#\$MINUTE))

mkdir -p "\$STATE_DIR"
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check intraday market refresh" >> "\$LOG"

if (( WEEKDAY < 1 || WEEKDAY > 5 )); then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] not weekday, skip" >> "\$LOG"
  exit 0
fi

if (( MINUTES >= 690 && MINUTES < 900 )); then
  SESSION="midday"
elif (( MINUTES >= 900 )); then
  SESSION="close"
else
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] outside midday/close window, skip" >> "\$LOG"
  exit 0
fi

STATE="\$STATE_DIR/\$TODAY-\$SESSION.ok"
if [[ -f "\$STATE" ]]; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] \$SESSION already published, skip retry" >> "\$LOG"
  exit 0
fi

cd "\$ROOT"
git pull --ff-only >> "\$LOG" 2>&1
bash scripts/deploy_oil_futures_tab.sh "\$SESSION" >> "\$LOG" 2>&1
touch "\$STATE"
find "\$STATE_DIR" -type f -name '*.ok' -mtime +14 -delete
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] \$SESSION market refresh published" >> "\$LOG"
RUNNER
chmod +x "$RUNNER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.vinsontesla.oil-futures-tab</string>
  <key>ProgramArguments</key>
  <array><string>$RUNNER</string></array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>50</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>50</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>50</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>50</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>50</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>5</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
  </array>
  <key>StandardOutPath</key><string>$SUPPORT_DIR/oil-futures-tab.stdout.log</string>
  <key>StandardErrorPath</key><string>$SUPPORT_DIR/oil-futures-tab.stderr.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST"
launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl enable "gui/$(id -u)/com.vinsontesla.oil-futures-tab"
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/com.vinsontesla.oil-futures-tab" | sed -n '1,100p'

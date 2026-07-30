#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily-runtime}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.oil-futures-tab.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/oil-futures-tab.sh"

mkdir -p "$HOME/Library/LaunchAgents" "$SUPPORT_DIR"

if [[ "$ROOT" != "$RUNTIME_ROOT" ]]; then
  mkdir -p "$(dirname "$RUNTIME_ROOT")"
  if [[ ! -d "$RUNTIME_ROOT/.git" ]]; then
    git clone --branch main --single-branch "$(git -C "$ROOT" remote get-url origin)" "$RUNTIME_ROOT"
  fi
fi

if [[ "$(git -C "$RUNTIME_ROOT" branch --show-current)" != "main" ]] \
  || [[ -n "$(git -C "$RUNTIME_ROOT" status --porcelain --untracked-files=all)" ]]; then
  echo "oil-futures runtime must be a clean main checkout: $RUNTIME_ROOT" >&2
  exit 2
fi
git -C "$RUNTIME_ROOT" pull --ff-only origin main

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
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check scheduled market refresh" >> "\$LOG"

FUNDAMENTAL_DATE="\$TODAY"
if (( WEEKDAY >= 2 && WEEKDAY <= 6 && MINUTES < 210 )); then
  SESSION="overnight"
  FUNDAMENTAL_DATE="\$(TZ=Asia/Shanghai date -v-1d +%F)"
elif (( WEEKDAY >= 1 && WEEKDAY <= 5 && MINUTES >= 690 && MINUTES < 900 )); then
  SESSION="midday"
elif (( WEEKDAY >= 1 && WEEKDAY <= 5 && MINUTES >= 900 && MINUTES < 1260 )); then
  SESSION="close"
elif (( WEEKDAY >= 1 && WEEKDAY <= 5 && MINUTES >= 1260 && MINUTES < 1380 )); then
  SESSION="night_open"
elif (( WEEKDAY >= 1 && WEEKDAY <= 5 && MINUTES >= 1380 )); then
  SESSION="night_close"
else
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] outside scheduled market windows, skip" >> "\$LOG"
  exit 0
fi

STATE="\$STATE_DIR/\$FUNDAMENTAL_DATE-\$SESSION.ok"
if [[ -f "\$STATE" ]]; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] \$SESSION already published, skip retry" >> "\$LOG"
  exit 0
fi

MORNING_STATE="\$STATE_DIR/\$FUNDAMENTAL_DATE-morning.ok"
if [[ ! -f "\$MORNING_STATE" ]]; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] \$FUNDAMENTAL_DATE morning report/fundamental snapshot not published, skip \$SESSION technical refresh" >> "\$LOG"
  exit 0
fi

cd "\$ROOT"
pull_with_retry() {
  local attempt
  for attempt in 1 2 3; do
    if GIT_TERMINAL_PROMPT=0 git pull --ff-only >> "\$LOG" 2>&1; then
      return 0
    fi
    echo "[\$(TZ=Asia/Shanghai date '+%F %T')] git pull failed (attempt \$attempt/3)" >> "\$LOG"
    if (( attempt < 3 )); then
      sleep \$((attempt * 10))
    fi
  done
  return 1
}

if ! pull_with_retry; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] source sync unavailable after retries; keep state open for next recovery" >> "\$LOG"
  exit 1
fi
bash scripts/deploy_oil_futures_tab.sh "\$SESSION" "\$FUNDAMENTAL_DATE" >> "\$LOG" 2>&1
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
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>23</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>2</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>2</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>2</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>2</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>6</integer><key>Hour</key><integer>2</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>6</integer><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
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

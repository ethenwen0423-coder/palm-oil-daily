#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.contract-discovery.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/contract-discovery.sh"

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

ROOT="$RUNTIME_ROOT"
LOG="$SUPPORT_DIR/contract-discovery.log"

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] start contract discovery" >> "\$LOG"
cd "\$ROOT"
git pull --ff-only >> "\$LOG" 2>&1 || true
python3 skills/contract_discovery_skill/scripts/select_contracts.py >> "\$LOG" 2>&1
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] finish contract discovery" >> "\$LOG"
RUNNER
chmod +x "$RUNNER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.vinsontesla.contract-discovery</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Day</key><integer>1</integer>
    <key>Hour</key><integer>0</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$SUPPORT_DIR/contract-discovery.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$SUPPORT_DIR/contract-discovery.stderr.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.vinsontesla.contract-discovery"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/com.vinsontesla.contract-discovery" | sed -n '1,80p'

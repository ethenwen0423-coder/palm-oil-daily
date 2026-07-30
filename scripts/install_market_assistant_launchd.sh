#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_ASSISTANT_RUNTIME_ROOT:-$HOME/Sites/palm-oil-daily-runtime}"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.market-assistant-ai.plist"
RUNNER="$SUPPORT_DIR/market-assistant-ai.sh"
LOG="$SUPPORT_DIR/market-assistant-ai.log"
LABEL="com.vinsontesla.market-assistant-ai"

mkdir -p "$HOME/Library/LaunchAgents" "$SUPPORT_DIR"

if [[ "$ROOT" != "$RUNTIME_ROOT" ]]; then
  if [[ ! -d "$RUNTIME_ROOT/.git" ]]; then
    git clone --branch main --single-branch "$(git -C "$ROOT" remote get-url origin)" "$RUNTIME_ROOT"
  fi
fi

if [[ "$(git -C "$RUNTIME_ROOT" branch --show-current)" != "main" ]] \
  || [[ -n "$(git -C "$RUNTIME_ROOT" status --porcelain --untracked-files=all)" ]]; then
  echo "market-assistant runtime must be a clean main checkout: $RUNTIME_ROOT" >&2
  exit 2
fi
git -C "$RUNTIME_ROOT" pull --ff-only origin main

cat > "$RUNNER" <<RUNNER
#!/usr/bin/env bash
set -euo pipefail

ROOT="$RUNTIME_ROOT"
LOG="$LOG"
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check AI brief source fingerprint" >> "\$LOG"
cd "\$ROOT"
set +e
bash scripts/deploy_market_assistant_brief.sh >> "\$LOG" 2>&1
result=\$?
set -e
if [[ "\$result" -eq 75 ]]; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] market refresh busy; retry AI brief on next interval" >> "\$LOG"
  exit 0
fi
if [[ "\$result" -ne 0 ]]; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] AI brief update failed with exit \$result; previous valid brief remains" >> "\$LOG"
  exit "\$result"
fi
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] AI brief check complete" >> "\$LOG"
RUNNER
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
  <array><string>$RUNNER</string></array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>900</integer>
  <key>ThrottleInterval</key>
  <integer>60</integer>
  <key>StandardOutPath</key>
  <string>$SUPPORT_DIR/market-assistant-ai.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$SUPPORT_DIR/market-assistant-ai.stderr.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST"
plutil -lint "$PLIST"
launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl enable "gui/$(id -u)/$LABEL"
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/$LABEL" | sed -n '1,100p'

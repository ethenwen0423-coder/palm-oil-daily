#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
LABEL="com.vinsontesla.palm-oil-supply-demand"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/palm-oil-supply-demand.sh"
LOG="$SUPPORT_DIR/palm-oil-supply-demand.log"

fail() {
  echo "supply-demand automation not installed: $*" >&2
  exit 2
}

[[ -d "$RUNTIME_ROOT/.git" ]] || fail "runtime is not a git checkout: $RUNTIME_ROOT"
[[ "$(git -C "$RUNTIME_ROOT" branch --show-current)" == "main" ]] ||
  fail "runtime must be on main: $RUNTIME_ROOT"
[[ -z "$(git -C "$RUNTIME_ROOT" status --porcelain --untracked-files=all)" ]] ||
  fail "runtime has uncommitted changes: $RUNTIME_ROOT"

git -C "$RUNTIME_ROOT" fetch origin main
git -C "$RUNTIME_ROOT" merge-base --is-ancestor HEAD origin/main ||
  fail "runtime cannot be safely fast-forwarded to origin/main"
git -C "$RUNTIME_ROOT" pull --ff-only origin main

[[ -x "$RUNTIME_ROOT/scripts/deploy_supply_demand_data.sh" ]] ||
  fail "published deploy script is unavailable in runtime"
[[ -f "$RUNTIME_ROOT/data/supply-demand.json" ]] ||
  fail "published data file is unavailable in runtime"

mkdir -p "$HOME/Library/LaunchAgents" "$SUPPORT_DIR"

cat > "$RUNNER" <<RUNNER
#!/usr/bin/env bash
set -euo pipefail

ROOT="$RUNTIME_ROOT"
LOG="$LOG"

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] start supply-demand update" >> "\$LOG"
cd "\$ROOT"
git pull --ff-only origin main >> "\$LOG" 2>&1
scripts/deploy_supply_demand_data.sh >> "\$LOG" 2>&1
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] finish supply-demand update" >> "\$LOG"
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
  <array>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>13</integer>
    <key>Minute</key><integer>15</integer>
  </dict>
  <key>ProcessType</key>
  <string>Background</string>
  <key>StandardOutPath</key>
  <string>$SUPPORT_DIR/palm-oil-supply-demand.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$SUPPORT_DIR/palm-oil-supply-demand.stderr.log</string>
</dict>
</plist>
PLIST
chmod 644 "$PLIST"
plutil -lint "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/$LABEL"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/$LABEL" | sed -n '1,80p'

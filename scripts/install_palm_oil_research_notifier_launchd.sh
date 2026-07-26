#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
SUPPORT_ROOT="$HOME/Library/Application Support/VinsonTesla"
RESEARCH_DIR="$SUPPORT_ROOT/palm-oil-research"
PRIVATE_ENV="$SUPPORT_ROOT/palm-oil-signal.env"
RUNNER="$SUPPORT_ROOT/palm-oil-research-notifier.sh"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.palm-oil-research-notifier.plist"
LABEL="com.vinsontesla.palm-oil-research-notifier"
PYTHON_BIN="${PALM_OIL_PYTHON_BIN:-$(command -v python3 || true)}"

if [[ "$ROOT" != "$RUNTIME_ROOT" ]]; then
  echo "请从生产目录 $RUNTIME_ROOT 运行安装器" >&2
  exit 2
fi
if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  echo "找不到可用的 python3" >&2
  exit 127
fi
if [[ ! -f "$PRIVATE_ENV" ]]; then
  echo "缺少现有 Messages 私有配置：$PRIVATE_ENV" >&2
  exit 2
fi

chmod 600 "$PRIVATE_ENV"
set -a
source "$PRIVATE_ENV"
set +a
if [[ -z "${PALM_OIL_MESSAGE_RECIPIENT:-}" ]]; then
  echo "PALM_OIL_MESSAGE_RECIPIENT 未配置，拒绝启用任务" >&2
  exit 2
fi
case "${PALM_OIL_MESSAGE_RECEIPT_CONFIRMED:-0}" in
  1|true|TRUE|yes|YES) ;;
  *) echo "Messages 接收端尚未确认，拒绝启用任务" >&2; exit 2 ;;
esac

mkdir -p "$HOME/Library/LaunchAgents" "$RESEARCH_DIR"
chmod 700 "$RESEARCH_DIR"

cat > "$RUNNER" <<RUNNER
#!/usr/bin/env bash
set -euo pipefail
set -a
source "$PRIVATE_ENV"
set +a
EDITION="\${1:-auto}"
cd "$RUNTIME_ROOT"
exec "$PYTHON_BIN" scripts/palm_oil_research_notifier.py --edition "\$EDITION"
RUNNER
chmod 700 "$RUNNER"

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
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>35</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>45</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>$RESEARCH_DIR/launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$RESEARCH_DIR/launchd.stderr.log</string>
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
echo "state $RESEARCH_DIR/state.json"
launchctl print "gui/$(id -u)/$LABEL" | sed -n '1,120p'

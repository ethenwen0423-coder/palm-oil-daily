#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.palm-oil-daily-watchdog.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/palm-oil-daily-watchdog.sh"
CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex"

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
REPORT_DATE="\$(TZ=Asia/Shanghai date +%F)"
REPORT="\$ROOT/reports/\$REPORT_DATE.md"
DOWNLOAD="\$ROOT/downloads/\$REPORT_DATE.md"
DATA="\$ROOT/data/reports.js"
LOG="$SUPPORT_DIR/palm-oil-daily-watchdog.check.log"
FORBIDDEN='未实际调用|当前环境未暴露调用入口|这是测试报告|排版调试样稿'

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check \$REPORT_DATE" >> "\$LOG"

if [[ -s "\$REPORT" && -s "\$DOWNLOAD" && -s "\$DATA" ]] \\
  && grep -q "\"date\": \"\$REPORT_DATE\"" "\$DATA" \\
  && ! grep -Eq "\$FORBIDDEN" "\$REPORT"; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] published, skip backfill" >> "\$LOG"
  exit 0
fi

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] missing or invalid, start codex backfill" >> "\$LOG"

PROMPT='这是棕榈油每日晨报的系统级兜底检查。现在是工作日 08:40 后的补检窗口。请先检查 '"$RUNTIME_ROOT"'/reports/当前上海日期.md、data/reports.js、downloads/当前上海日期.md 是否都存在，且正文不含“未实际调用”“当前环境未暴露调用入口”“这是测试报告”“排版调试样稿”。如果已经合格，立即结束，不要改文件。如果缺失或不合格，请使用当前上海日期补跑日报：先 git pull --ff-only，然后运行 python3 scripts/run_financial_skills.py --date 当前上海日期 --kind daily --timeout 90，读取 source_runs/当前日期-daily/manifest.json 和 raw 文件，按既定日报规范生成 reports/当前日期.md，运行 bash scripts/deploy_report.sh 发布。若当天不是中国期货市场交易日，停止发布并说明原因。最终简要说明是否补跑、是否已发布。'

printf '%s\n' "\$PROMPT" | "$CODEX_BIN" exec \\
  --cd "$ROOT" \\
  --model gpt-5.5 \\
  --sandbox danger-full-access \\
  --dangerously-bypass-approvals-and-sandbox \\
  -
RUNNER
chmod +x "$RUNNER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.vinsontesla.palm-oil-daily-watchdog</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>40</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>40</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>$SUPPORT_DIR/palm-oil-daily-watchdog.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$SUPPORT_DIR/palm-oil-daily-watchdog.stderr.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.vinsontesla.palm-oil-daily-watchdog"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/com.vinsontesla.palm-oil-daily-watchdog" | sed -n '1,80p'

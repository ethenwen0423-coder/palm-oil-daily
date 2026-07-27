#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.palm-oil-daily-watchdog.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/palm-oil-daily-watchdog.sh"

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

CODEX_BIN="\${CODEX_BIN:-}"
if [[ -z "\$CODEX_BIN" ]]; then
  for candidate in \
    "/Applications/ChatGPT.app/Contents/Resources/codex" \
    "/Applications/Codex.app/Contents/Resources/codex"; do
    if [[ -x "\$candidate" ]]; then
      CODEX_BIN="\$candidate"
      break
    fi
  done
fi
if [[ -z "\$CODEX_BIN" ]]; then
  CODEX_BIN="\$(command -v codex || true)"
fi
if [[ -z "\$CODEX_BIN" || ! -x "\$CODEX_BIN" ]]; then
  echo "Codex executable not found" >&2
  exit 127
fi

ROOT="$RUNTIME_ROOT"
REPORT_DATE="\$(TZ=Asia/Shanghai date +%F)"
WEEKDAY="\$(TZ=Asia/Shanghai date +%u)"
REPORT="\$ROOT/reports/\$REPORT_DATE.md"
DOWNLOAD="\$ROOT/downloads/\$REPORT_DATE.md"
DATA="\$ROOT/data/reports.js"
LOG="$SUPPORT_DIR/palm-oil-daily-watchdog.check.log"
STATE_DIR="$SUPPORT_DIR/market-refresh-state"
MORNING_STATE="\$STATE_DIR/\$REPORT_DATE-morning.ok"
RESEARCH_RUNNER="$SUPPORT_DIR/palm-oil-research-notifier.sh"
FORBIDDEN='未实际调用|当前环境未暴露调用入口|这是测试报告|排版调试样稿'

mkdir -p "\$STATE_DIR"
echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check \$REPORT_DATE" >> "\$LOG"

notify_morning_research() {
  if [[ ! -x "\$RESEARCH_RUNNER" ]]; then
    echo "[\$(TZ=Asia/Shanghai date '+%F %T')] research notifier not installed, skip message" >> "\$LOG"
    return 0
  fi
  if "\$RESEARCH_RUNNER" morning >> "\$LOG" 2>&1; then
    echo "[\$(TZ=Asia/Shanghai date '+%F %T')] morning research notification checked" >> "\$LOG"
  else
    echo "[\$(TZ=Asia/Shanghai date '+%F %T')] morning research notification failed; keep website workflow running" >> "\$LOG"
  fi
}

if (( WEEKDAY < 1 || WEEKDAY > 5 )); then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] not weekday, skip daily and oil-futures tab" >> "\$LOG"
  exit 0
fi

if [[ -s "\$REPORT" && -s "\$DOWNLOAD" && -s "\$DATA" ]] \\
  && grep -q "\"date\": \"\$REPORT_DATE\"" "\$DATA" \\
  && ! grep -Eq "\$FORBIDDEN" "\$REPORT"; then
  notify_morning_research
  if [[ -f "\$MORNING_STATE" ]]; then
    echo "[\$(TZ=Asia/Shanghai date '+%F %T')] daily and morning market data already published, skip retry" >> "\$LOG"
    exit 0
  fi
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] daily published, refresh morning market data" >> "\$LOG"
  cd "\$ROOT"
  git pull --ff-only >> "\$LOG" 2>&1
  bash scripts/deploy_oil_futures_tab.sh morning >> "\$LOG" 2>&1
  touch "\$MORNING_STATE"
  exit 0
fi

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] missing or invalid, start codex backfill" >> "\$LOG"

PROMPT='这是棕榈油每日晨报的 macOS 系统级调度任务，工作日06:00生成、06:20补检。先核验当天是否为中国期货市场交易日，并检查 reports/当前上海日期.md、data/reports.js、downloads/当前上海日期.md；非交易日或三项均合格时按规范停止。需要生成或补跑时，必须先完整读取并严格执行 references/daily_automation_prompt.md 及其列出的 skills；该文件和 skills/report_writer_skill/SKILL.md 是正文结构的唯一权威。正文严格按新版九栏顺序生成：【今日观点】【今日交易信号】【核心驱动与预期差】【关键数据与价格】【开盘推演】【风险提示】【信息来源与核验说明】【消息来源链接】【AI观点风险提示】。不得要求、恢复或额外新增旧独立栏目【昨夜发生了什么】【相关新闻导向分析】【今日交易重点】【关键价格】【今日观察指标】。必须覆盖P/Y/OI，交易方向与价位只取自既有数据和策略结果；先完成数据门禁、预测generation feedback、freshness治理、结构化提纲、正文、标题和85分报告审计，再运行 bash scripts/deploy_report.sh。generation feedback只能读取此前已评估结果并下调约束，必须逐字写入required_report_disclosures；晨间任务不得调用或修改收盘复盘入口、actual snapshot、预测评估、滚动指标构建及其调度，也不得改变永久权重、参数或策略。失败时重写或停止发布，不得绕过门禁。最终简要说明是否生成、审计是否通过、是否已发布。'

printf '%s\n' "\$PROMPT" | "\$CODEX_BIN" exec \\
  --cd "\$ROOT" \\
  --sandbox danger-full-access \\
  --dangerously-bypass-approvals-and-sandbox \\
  -

if [[ -s "\$REPORT" && -s "\$DOWNLOAD" && -s "\$DATA" ]] \\
  && grep -q "\"date\": \"\$REPORT_DATE\"" "\$DATA" \\
  && ! grep -Eq "\$FORBIDDEN" "\$REPORT"; then
  notify_morning_research
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] daily backfill complete, refresh morning market data" >> "\$LOG"
  cd "\$ROOT"
  git pull --ff-only >> "\$LOG" 2>&1
  bash scripts/deploy_oil_futures_tab.sh morning >> "\$LOG" 2>&1
  touch "\$MORNING_STATE"
else
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] daily still missing or invalid, skip oil-futures tab" >> "\$LOG"
fi
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
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>20</integer></dict>
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

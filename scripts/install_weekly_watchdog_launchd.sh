#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.palm-oil-weekly-watchdog.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/palm-oil-weekly-watchdog.sh"

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
WEEKDAY="\$(TZ=Asia/Shanghai date +%w)"
REPORT_ID="\$REPORT_DATE-weekend"
REPORT="\$ROOT/reports/\$REPORT_ID.md"
DOWNLOAD="\$ROOT/downloads/\$REPORT_ID.md"
DATA="\$ROOT/data/reports.js"
LOG="$SUPPORT_DIR/palm-oil-weekly-watchdog.check.log"
FORBIDDEN='未实际调用|当前环境未暴露调用入口|这是测试报告|排版调试样稿'

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check \$REPORT_ID" >> "\$LOG"

if [[ "\$WEEKDAY" != "0" ]]; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] not Sunday, skip weekly watchdog" >> "\$LOG"
  exit 0
fi

if [[ -s "\$REPORT" && -s "\$DOWNLOAD" && -s "\$DATA" ]] \\
  && grep -q "\"date\": \"\$REPORT_ID\"" "\$DATA" \\
  && ! grep -Eq "\$FORBIDDEN" "\$REPORT"; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] published, skip backfill" >> "\$LOG"
  exit 0
fi

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] missing or invalid, start codex backfill" >> "\$LOG"

PROMPT='这是棕榈油周报的 macOS 系统级调度任务，周日21:15生成、21:40补检。先检查 reports/当前上海日期-weekend.md、data/reports.js、downloads/当前上海日期-weekend.md；三项均合格时按规范停止。需要生成或补跑时，必须先完整读取并严格执行 references/weekly_automation_prompt.md 及其列出的 skills；该文件和 skills/report_writer_skill/SKILL.md 是正文结构的唯一权威。正文严格按新版十栏顺序生成：【一句话核心观点】【本周验证与预期差】【核心数据变化】【下周主线与事件】【周一开盘推演】【交易计划】【风险提示】【信息来源与核验说明】【消息来源链接】【AI观点风险提示】。不得要求、恢复或额外新增旧独立栏目【本周三大变化】【本周新闻导向分析】【市场一致预期 VS 我的判断】【市场复盘】【下周重要事件】【一句话总结】。必须覆盖P/Y/OI和至少两个可核验相对价值指标；交易方向、概率与价位只取自既有数据和策略结果。先完成数据门禁、freshness治理、结构化提纲、正文、标题和85分报告审计，再运行 bash scripts/deploy_report.sh；不得修改日报内容复盘、预测评估、滚动指标或其调度。失败时重写或停止发布，不得绕过门禁。最终简要说明是否生成、审计是否通过、是否已发布。'

printf '%s\n' "\$PROMPT" | "\$CODEX_BIN" exec \\
  --cd "\$ROOT" \\
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
  <string>com.vinsontesla.palm-oil-weekly-watchdog</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>15</integer></dict>
    <dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>$SUPPORT_DIR/palm-oil-weekly-watchdog.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$SUPPORT_DIR/palm-oil-weekly-watchdog.stderr.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.vinsontesla.palm-oil-weekly-watchdog"

echo "installed $PLIST"
echo "runner $RUNNER"
echo "runtime root $RUNTIME_ROOT"
launchctl print "gui/$(id -u)/com.vinsontesla.palm-oil-weekly-watchdog" | sed -n '1,80p'

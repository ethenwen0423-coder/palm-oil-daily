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
FORBIDDEN='未实际调用|当前环境未暴露调用入口|这是测试报告|排版调试样稿'

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] check \$REPORT_DATE" >> "\$LOG"

if (( WEEKDAY < 1 || WEEKDAY > 5 )); then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] not weekday, skip daily and oil-futures tab" >> "\$LOG"
  exit 0
fi

if [[ -s "\$REPORT" && -s "\$DOWNLOAD" && -s "\$DATA" ]] \\
  && grep -q "\"date\": \"\$REPORT_DATE\"" "\$DATA" \\
  && ! grep -Eq "\$FORBIDDEN" "\$REPORT"; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] daily published, refresh oil-futures tab on same schedule" >> "\$LOG"
  cd "\$ROOT"
  git pull --ff-only >> "\$LOG" 2>&1
  bash scripts/deploy_oil_futures_tab.sh >> "\$LOG" 2>&1
  exit 0
fi

echo "[\$(TZ=Asia/Shanghai date '+%F %T')] missing or invalid, start codex backfill" >> "\$LOG"

PROMPT='这是棕榈油每日晨报的 macOS 系统级调度任务。当前任务每天工作日 08:20 主动生成，08:40 再补检一次。请先检查 '"$RUNTIME_ROOT"'/reports/当前上海日期.md、data/reports.js、downloads/当前上海日期.md 是否都存在，且正文不含“未实际调用”“当前环境未暴露调用入口”“这是测试报告”“排版调试样稿”。如果已经合格，立即结束，不要改文件。如果缺失或不合格，请使用当前上海日期生成或补跑日报：先 git pull --ff-only，然后运行 python3 scripts/run_financial_skills.py --date 当前上海日期 --kind daily --timeout 90，读取 source_runs/当前日期-daily/manifest.json 和 raw 文件，并运行 python3 skills/data_quality_gate_skill/scripts/validate_data.py --manifest source_runs/当前日期-daily/manifest.json --strict；随后运行 python3 skills/forecast_tracking_skill/scripts/build_generation_feedback.py --metrics data/forecast/metrics/latest.json --review-dir data/review/daily --output data/forecast/feedback/latest.json --as-of 当前上海日期，并完整读取 feedback/latest.json。必须读取 references/daily_automation_prompt.md 及其中列出的全部 skills，严格按 market_data_skill、data_quality_gate_skill、forecast_generation_feedback、oil_report_freshness、report_writer_skill、headline_skill、report_quality_gate、forecast_tracking_skill 顺序执行。feedback 只能限制置信度、降级低命中率主线或补充失效情景，不能替代今日行情或提高置信度；必须逐字写入 required_report_disclosures 到【信息来源与核验说明】。同时读取最近30天 daily review，不得自动修改永久评分权重、参数或策略规则。日报必须覆盖 P/Y/OI、相关新闻导向、关键数据、交易重点、开盘推演、关键价格、观察指标、风险提示、来源链接和 AI 风险提示；核心行情须交叉核验，无法确认写“需进一步核验”。写入 reports/当前日期.md 后运行 bash scripts/deploy_report.sh；该门禁会校验复盘约束，失败必须重写后再发布。若当天不是中国期货市场交易日，停止发布并说明原因。最终简要说明是否生成、是否已发布。'

printf '%s\n' "\$PROMPT" | "\$CODEX_BIN" exec \\
  --cd "\$ROOT" \\
  --sandbox danger-full-access \\
  --dangerously-bypass-approvals-and-sandbox \\
  -

if [[ -s "\$REPORT" && -s "\$DOWNLOAD" && -s "\$DATA" ]] \\
  && grep -q "\"date\": \"\$REPORT_DATE\"" "\$DATA" \\
  && ! grep -Eq "\$FORBIDDEN" "\$REPORT"; then
  echo "[\$(TZ=Asia/Shanghai date '+%F %T')] daily backfill complete, refresh oil-futures tab on same schedule" >> "\$LOG"
  cd "\$ROOT"
  git pull --ff-only >> "\$LOG" 2>&1
  bash scripts/deploy_oil_futures_tab.sh >> "\$LOG" 2>&1
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
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>20</integer></dict>
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

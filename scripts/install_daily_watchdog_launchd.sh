#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.palm-oil-daily-watchdog.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/palm-oil-daily-watchdog.sh"
CODEX_BIN="/Applications/ChatGPT.app/Contents/Resources/codex"

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

PROMPT='这是棕榈油每日晨报的 macOS 系统级调度任务。当前任务每天工作日 08:20 主动生成，08:40 再补检一次。请先检查 '"$RUNTIME_ROOT"'/reports/当前上海日期.md、data/reports.js、downloads/当前上海日期.md 是否都存在，且正文不含“未实际调用”“当前环境未暴露调用入口”“这是测试报告”“排版调试样稿”。如果已经合格，立即结束，不要改文件。如果缺失或不合格，请使用当前上海日期生成或补跑日报：先 git pull --ff-only，然后运行 python3 scripts/run_financial_skills.py --date 当前上海日期 --kind daily --timeout 90，读取 source_runs/当前日期-daily/manifest.json 和 raw 文件，并运行 python3 skills/data_quality_gate_skill/scripts/validate_data.py --manifest source_runs/当前日期-daily/manifest.json --strict，并读取 references/daily_automation_prompt.md、references/wechat_oil_sources.md、skills/master_report_skill/SKILL.md、skills/data_quality_gate_skill/SKILL.md、skills/oil-report-freshness/SKILL.md、skills/report_writer_skill/SKILL.md、skills/vinson-research-writing/SKILL.md、skills/vinson-research-writing/checklist.md、skills/title-generation/SKILL.md、skills/title-quality-gate/SKILL.md；微信来源文件只提供历史样例来源池，不是固定引用清单，必须动态搜索当天最新同类微信/产业/期货公司来源进行观点补充，核心数据仍以交易所、官方机构、金融 skills 和研报为准。写正文和标题前必须先调用 master_report_skill，并按 market_data_skill、data_quality_gate_skill、oil_report_freshness、report_writer_skill、headline_skill、report_quality_gate 顺序调度；当前 market_data_skill 由 run_financial_skills.py 和 manifest/raw 结果承担，report_writer_skill 由 skills/report_writer_skill/SKILL.md 承担，并以 vinson-research-writing 作为通用写作规范，headline_skill 由 title-generation 与 title-quality-gate 承担，report_quality_gate 保留接口并由 data_quality_gate_skill、checklist、title gate、来源核验和 freshness 禁用项共同检查；不得跳过 oil-report-freshness，report_writer 和 title-generation 只能使用该 skill 输出的今日新增驱动和今日主线建议，不得把背景、旧政策、周度库存或待核验信息提升为今日主线。按 report_writer_skill 要求把正文从资讯汇总升级为研究分析：每个核心观点必须回答为什么，按影响程度排序驱动，写清传导链，区分预期与现实，说明观点失效条件，并给出研究置信度；日报必须新增【相关新闻导向分析】，最多3条，把当天重要新闻写成方向、传导链、交易含义和置信度，不得写成新闻堆砌；不得为此拉长篇幅。生成晨报前必须调用 skills/daily_review_skill/scripts/review_memory.py 的 load_recent_reviews(days=30)，只读取 data/review/daily/ 最近30天每日复盘，并可读取 data/review/latest_review.json 摘要；若发现连续错误类型，只能在当日报告中降低相关因素主导性或增加风险提示，不得未经人工确认永久修改参数，不得加载30天以前的每日明细。生成晨报和刷新 tab 页前必须先调用 skills/contract_selector_skill/SKILL.md，并运行 python3 skills/contract_selector_skill/scripts/select_contracts.py 刷新 data/contracts/current_contracts.json。日报和 tab 页的选择合约分析必须包含 contract_selector_skill 输出的全部合约；rank=1 作为主叙事合约，rank=2 作为换月、资金迁移、跨期强弱和流动性分析合约，不得在分析入口丢弃。按 Vinson Research Writing Standard、Title Generation 和 Title Quality Gate 提升可读性、机构研究风格和标题质量；标题必须先由 title-generation 基于 freshness 主线提炼市场主线并生成，再由 title-quality-gate 检查；未通过必须回到 title-generation 重写；标题/首页观点只能写市场观点和核心逻辑，具体价格、追高、低吸、止损、加减仓等执行动作只能放入开盘推演或交易计划；不得改变数据来源、业务逻辑或交易策略。报告结尾必须包含【消息来源链接】和【AI观点风险提示】，说明本报告仅代表 AI 基于公开信息和已调用数据源生成的研究判断，不构成投资建议。按既定日报规范生成 reports/当前日期.md，运行 bash scripts/deploy_report.sh 发布。若当天不是中国期货市场交易日，停止发布并说明原因。最终简要说明是否生成、是否已发布。'

printf '%s\n' "\$PROMPT" | "$CODEX_BIN" exec \\
  --cd "\$ROOT" \\
  --model gpt-5.5 \\
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

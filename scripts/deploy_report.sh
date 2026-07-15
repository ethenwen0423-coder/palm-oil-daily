#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

changed_reports=()
while IFS= read -r report_path; do
  changed_reports+=("$report_path")
done < <(
  {
    git diff --name-only -- 'reports/*.md'
    git ls-files --others --exclude-standard -- 'reports/*.md'
  } | sort -u
)

daily_report_dates=()
for report_path in "${changed_reports[@]}"; do
  report_file="$(basename "$report_path")"
  if [[ "$report_file" != *-weekend.md ]]; then
    report_date="${report_file%.md}"
    if [[ ! "$report_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
      echo "invalid daily report filename: $report_path" >&2
      exit 2
    fi
    daily_report_dates+=("$report_date")
  fi
done

unique_daily_dates=()
while IFS= read -r report_date; do
  [[ -n "$report_date" ]] && unique_daily_dates+=("$report_date")
done < <(printf '%s\n' "${daily_report_dates[@]}" | sort -u)

if (( ${#unique_daily_dates[@]} > 1 )); then
  echo "multiple daily report dates detected; refusing to bind one market snapshot to multiple forecasts" >&2
  exit 2
fi

if (( ${#changed_reports[@]} > 0 )); then
  python3 scripts/check_title_quality.py "${changed_reports[@]}"
fi

for report_path in "${changed_reports[@]}"; do
  report_file="$(basename "$report_path")"
  if [[ "$report_file" == *-weekend.md ]]; then
    report_date="${report_file%-weekend.md}"
    manifest="source_runs/${report_date}-weekend/manifest.json"
  else
    report_date="${report_file%.md}"
    manifest="source_runs/${report_date}-daily/manifest.json"
  fi
  python3 skills/data_quality_gate_skill/scripts/validate_data.py --manifest "$manifest" --strict
  if [[ "$report_file" != *-weekend.md ]]; then
    python3 skills/forecast_tracking_skill/scripts/validate_report_feedback.py \
      --report "$report_path" \
      --feedback data/forecast/feedback/latest.json \
      --report-date "$report_date"
  fi
done

update_oil_futures_tab=false
for report_path in "${changed_reports[@]}"; do
  if [[ "$report_path" != *-weekend.md ]]; then
    update_oil_futures_tab=true
    break
  fi
done

if [[ "$update_oil_futures_tab" == true ]]; then
  report_date="${unique_daily_dates[0]}"
  time_metadata="$({ python3 scripts/update_oil_futures_data.py \
    --report-date "$report_date" \
    --print-time-metadata; } 2>&1)" || {
      echo "$time_metadata" >&2
      exit 2
    }
  generated_at="$(printf '%s' "$time_metadata" | python3 -c 'import json,sys; print(json.load(sys.stdin)["generated_at"])')"
  cutoff_at="$(printf '%s' "$time_metadata" | python3 -c 'import json,sys; print(json.load(sys.stdin)["cutoff_at"])')"
  python3 scripts/update_oil_futures_data.py \
    --report-date "$report_date" \
    --generated-at "$generated_at" \
    --cutoff-at "$cutoff_at"
  python3 skills/data_quality_gate_skill/scripts/validate_data.py --oil-futures data/oil_futures.js --strict
else
  echo "skip oil futures tab update for weekly-only report deploy"
fi

python3 scripts/publish_report.py

if git diff --quiet -- reports data downloads; then
  echo "no report changes to deploy"
  exit 0
fi

git add -- reports data downloads miniprogram/data \
  ':(exclude)data/forecast/daily/*.json' \
  ':(exclude)data/review/runtime_snapshots/**'
if git diff --cached --name-only -- data/forecast/daily data/review/runtime_snapshots | grep -q .; then
  echo "refusing to publish Git-ignored forecast or runtime snapshot artifacts" >&2
  exit 2
fi
git commit -m "Update palm oil report"
git push

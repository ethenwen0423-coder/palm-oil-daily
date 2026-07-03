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

if (( ${#changed_reports[@]} > 0 )); then
  python3 scripts/check_title_quality.py "${changed_reports[@]}"
fi

python3 scripts/update_oil_futures_data.py
python3 scripts/publish_report.py

if git diff --quiet -- reports data downloads; then
  echo "no report changes to deploy"
  exit 0
fi

git add reports data downloads
git commit -m "Update palm oil report"
git push

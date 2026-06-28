#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/publish_report.py

if git diff --quiet -- reports data downloads; then
  echo "no report changes to deploy"
  exit 0
fi

git add reports data downloads
git commit -m "Update palm oil report"
git push

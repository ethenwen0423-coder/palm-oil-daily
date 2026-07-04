#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/update_oil_futures_data.py

if git diff --quiet -- data/oil_futures.js; then
  echo "no oil futures tab changes to deploy"
  exit 0
fi

git add data/oil_futures.js
git commit -m "Update oil futures tab"
git push

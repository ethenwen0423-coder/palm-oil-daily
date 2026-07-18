#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/update_oil_futures_data.py
python3 scripts/update_quant_model_data.py

if git diff --quiet -- data/oil_futures.js data/oil_futures.json miniprogram/data/oil_futures.js data/quant_model_signals.js data/quant_model_signals.json; then
  echo "no oil futures or quant-model changes to deploy"
  exit 0
fi

git add data/oil_futures.js data/oil_futures.json miniprogram/data/oil_futures.js data/quant_model_signals.js data/quant_model_signals.json
git commit -m "Update oil futures and quant model data"
git push

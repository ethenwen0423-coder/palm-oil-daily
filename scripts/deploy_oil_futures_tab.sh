#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

SESSION="${1:-manual}"
case "$SESSION" in
  morning|midday|close|manual) ;;
  *) echo "invalid market update session: $SESSION" >&2; exit 2 ;;
esac

SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
LOCK_DIR="$SUPPORT_DIR/market-data-deploy.lock"
mkdir -p "$SUPPORT_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another market-data deploy is already running" >&2
  exit 75
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/palm-oil-market.XXXXXX")"
cleanup() {
  rm -rf "$TMP_DIR"
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT

TODAY="$(TZ=Asia/Shanghai date +%F)"
OIL_TMP="$TMP_DIR/oil_futures.js"
EXCHANGE_TMP="$TMP_DIR/exchange_futures.js"
SKIP_OIL=false

if [[ "$SESSION" == "morning" && -s data/oil_futures.js ]]; then
  if python3 - "$TODAY" <<'PY'
import json
import sys
from pathlib import Path

text = Path("data/oil_futures.js").read_text(encoding="utf-8").strip()
payload = json.loads(text.split("=", 1)[1].strip().removesuffix(";"))
raise SystemExit(0 if payload.get("updated_at", "").startswith(sys.argv[1]) and payload.get("update_session") == "morning" else 1)
PY
  then
    SKIP_OIL=true
    echo "morning oil-futures data already published; keep report-aligned snapshot"
  fi
fi

if [[ "$SKIP_OIL" == false ]]; then
  python3 scripts/update_oil_futures_data.py --output "$OIL_TMP" --update-session "$SESSION"
  python3 skills/data_quality_gate_skill/scripts/validate_data.py --oil-futures "$OIL_TMP" --strict
fi

python3 scripts/update_exchange_futures_data.py --output "$EXCHANGE_TMP" --update-session "$SESSION"

python3 - "$SESSION" "$TODAY" "$OIL_TMP" "$EXCHANGE_TMP" "$SKIP_OIL" <<'PY'
import json
import sys
from pathlib import Path

session, today, oil_path, exchange_path, skip_oil = sys.argv[1:]

def load_wrapped(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8").strip()
    return json.loads(text.split("=", 1)[1].strip().removesuffix(";"))

payloads = [("exchange_futures", load_wrapped(exchange_path))]
if skip_oil != "true":
    payloads.append(("oil_futures", load_wrapped(oil_path)))

for name, payload in payloads:
    if payload.get("update_session") != session:
        raise SystemExit(f"{name} update_session mismatch")
    if not str(payload.get("updated_at") or "").startswith(today):
        raise SystemExit(f"{name} updated_at is not today")
    if payload.get("timezone") != "Asia/Shanghai":
        raise SystemExit(f"{name} timezone mismatch")
    if not payload.get("contracts"):
        raise SystemExit(f"{name} has no contracts")

exchange = payloads[0][1]
priced = [item for item in exchange["contracts"] if isinstance(item.get("price"), (int, float))]
if len(exchange["contracts"]) < 30 or len(priced) < 25:
    raise SystemExit("exchange_futures coverage is too small; refusing partial publish")
PY

if [[ "$SKIP_OIL" == false ]]; then
  cp "$OIL_TMP" data/oil_futures.js
  python3 scripts/sync_miniprogram_data.py oil-futures
fi
cp "$EXCHANGE_TMP" data/exchange_futures.js
python3 scripts/update_quant_model_data.py

ALLOWED=(
  data/oil_futures.js
  data/oil_futures.json
  miniprogram/data/oil_futures.js
  data/exchange_futures.js
  data/quant_model_signals.js
  data/quant_model_signals.json
)

while IFS= read -r staged; do
  [[ -z "$staged" ]] && continue
  allowed=false
  for path in "${ALLOWED[@]}"; do
    [[ "$staged" == "$path" ]] && allowed=true && break
  done
  if [[ "$allowed" == false ]]; then
    echo "refusing to include unrelated staged file: $staged" >&2
    exit 2
  fi
done < <(git diff --cached --name-only)

if git diff --quiet -- "${ALLOWED[@]}"; then
  echo "no market-data changes to deploy"
  exit 0
fi

git add -- "${ALLOWED[@]}"
git commit -m "Update ${SESSION} market data"
git push

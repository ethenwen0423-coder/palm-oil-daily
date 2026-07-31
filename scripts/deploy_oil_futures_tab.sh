#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

SESSION="${1:-manual}"
case "$SESSION" in
  morning|midday|close|night_open|night_close|overnight|manual) ;;
  *) echo "invalid market update session: $SESSION" >&2; exit 2 ;;
esac

SUPPORT_DIR="${PALM_OIL_SUPPORT_DIR:-$HOME/Library/Application Support/VinsonTesla}"
PUBLISH_MODE="${PALM_OIL_PUBLISH_MODE:-git}"
case "$PUBLISH_MODE" in
  git|files) ;;
  *) echo "invalid PALM_OIL_PUBLISH_MODE: $PUBLISH_MODE" >&2; exit 2 ;;
esac
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
FUNDAMENTAL_DATE="${2:-$TODAY}"
if [[ ! "$FUNDAMENTAL_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "invalid fundamental date: $FUNDAMENTAL_DATE" >&2
  exit 2
fi
OIL_TMP="$TMP_DIR/oil_futures.js"
EXCHANGE_TMP="$TMP_DIR/exchange_futures.js"
EXCHANGE_JSON_TMP="$TMP_DIR/exchange_futures.json"
CONTRACT_TMP="$TMP_DIR/current_contracts.json"
OIL_FUNDAMENTAL_MODE="refresh"
EXCHANGE_FUNDAMENTAL_MODE="refresh"

if [[ "$SESSION" == "midday" || "$SESSION" == "close" || "$SESSION" == "night_open" || "$SESSION" == "night_close" || "$SESSION" == "overnight" ]]; then
  OIL_FUNDAMENTAL_MODE="carry"
  EXCHANGE_FUNDAMENTAL_MODE="carry"
fi

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
    OIL_FUNDAMENTAL_MODE="carry"
    echo "morning oil fundamentals already frozen; refresh quotes and technicals only"
  fi
fi

OIL_ARGS=(
  scripts/update_oil_futures_data.py
  --output "$OIL_TMP"
  --update-session "$SESSION"
  --fundamental-mode "$OIL_FUNDAMENTAL_MODE"
  --contract-output "$CONTRACT_TMP"
)
if [[ "$OIL_FUNDAMENTAL_MODE" == "carry" ]]; then
  OIL_ARGS+=(--fundamental-date "$FUNDAMENTAL_DATE")
fi
python3 "${OIL_ARGS[@]}"
python3 skills/data_quality_gate_skill/scripts/validate_data.py --oil-futures "$OIL_TMP" --strict

if [[ "$SESSION" == "morning" && -s data/exchange_futures.js ]]; then
  if python3 - "$TODAY" <<'PY'
import json
import sys
from pathlib import Path

text = Path("data/exchange_futures.js").read_text(encoding="utf-8").strip()
payload = json.loads(text.split("=", 1)[1].strip().removesuffix(";"))
raise SystemExit(
    0
    if str(payload.get("fundamental_updated_at") or "").startswith(sys.argv[1])
    and payload.get("fundamental_update_session") == "morning"
    else 1
)
PY
  then
    EXCHANGE_FUNDAMENTAL_MODE="carry"
    echo "morning exchange fundamentals already published; keep report-aligned snapshot"
  fi
fi

EXCHANGE_ARGS=(
  scripts/update_exchange_futures_data.py
  --output "$EXCHANGE_TMP"
  --update-session "$SESSION"
  --scope core
  --fundamental-mode "$EXCHANGE_FUNDAMENTAL_MODE"
)
if [[ "$EXCHANGE_FUNDAMENTAL_MODE" == "carry" ]]; then
  EXCHANGE_ARGS+=(--fundamental-date "$FUNDAMENTAL_DATE")
fi
python3 "${EXCHANGE_ARGS[@]}"

python3 - "$SESSION" "$TODAY" "$FUNDAMENTAL_DATE" "$OIL_TMP" "$EXCHANGE_TMP" "$EXCHANGE_JSON_TMP" <<'PY'
import json
import sys
from pathlib import Path

session, today, fundamental_date, oil_path, exchange_path, exchange_json_path = sys.argv[1:]

def load_wrapped(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8").strip()
    return json.loads(text.split("=", 1)[1].strip().removesuffix(";"))

payloads = [
    ("exchange_futures", load_wrapped(exchange_path)),
    ("oil_futures", load_wrapped(oil_path)),
]

for name, payload in payloads:
    if payload.get("update_session") != session:
        raise SystemExit(f"{name} update_session mismatch")
    if not str(payload.get("updated_at") or "").startswith(today):
        raise SystemExit(f"{name} updated_at is not today")
    if payload.get("timezone") != "Asia/Shanghai":
        raise SystemExit(f"{name} timezone mismatch")
    if not payload.get("contracts"):
        raise SystemExit(f"{name} has no contracts")
    if not str(payload.get("fundamental_updated_at") or "").startswith(fundamental_date):
        raise SystemExit(f"{name} fundamental snapshot is not from {fundamental_date}")
    if payload.get("fundamental_update_session") != "morning":
        raise SystemExit(f"{name} fundamental snapshot is not aligned with morning report")
    expected_mode = (
        "carry"
        if session in {"midday", "close", "night_open", "night_close", "overnight"}
        else {"refresh", "carry"}
    )
    if isinstance(expected_mode, set):
        if payload.get("fundamental_mode") not in expected_mode:
            raise SystemExit(f"{name} morning fundamental mode is invalid")
    elif payload.get("fundamental_mode") != expected_mode:
        raise SystemExit(f"{name} intraday fundamental mode must be carry")

exchange = payloads[0][1]
if exchange.get("scope") != "core":
    raise SystemExit("exchange_futures scheduled scope must be core")
if len(exchange["contracts"]) != exchange.get("universe_expected"):
    raise SystemExit("exchange_futures core universe is incomplete")
priced = [item for item in exchange["contracts"] if isinstance(item.get("price"), (int, float))]
if len(exchange["contracts"]) < 30 or len(priced) < 25:
    raise SystemExit("exchange_futures coverage is too small; refusing partial publish")

Path(exchange_json_path).write_text(
    json.dumps(exchange, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

cp "$OIL_TMP" data/oil_futures.js
cp "$CONTRACT_TMP" data/contracts/current_contracts.json
cp "$CONTRACT_TMP" "data/contracts/${TODAY:0:7}.json"
python3 scripts/sync_miniprogram_data.py oil-futures
cp "$EXCHANGE_TMP" data/exchange_futures.js
cp "$EXCHANGE_JSON_TMP" data/exchange_futures.json
python3 scripts/update_quant_model_data.py

ALLOWED=(
  data/oil_futures.js
  data/oil_futures.json
  miniprogram/data/oil_futures.js
  data/exchange_futures.js
  data/exchange_futures.json
  data/quant_model_signals.js
  data/quant_model_signals.json
  data/contracts/current_contracts.json
  "data/contracts/${TODAY:0:7}.json"
)

if [[ "$PUBLISH_MODE" == "files" ]]; then
  python3 - "$SESSION" "$FUNDAMENTAL_DATE" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "status": "ok",
            "publish_mode": "files",
            "session": sys.argv[1],
            "fundamental_date": sys.argv[2],
        },
        ensure_ascii=False,
    )
)
PY
  exit 0
fi

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

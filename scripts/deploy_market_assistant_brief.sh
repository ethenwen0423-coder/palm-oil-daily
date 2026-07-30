#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
LOCK_DIR="$SUPPORT_DIR/market-data-deploy.lock"
LOG="$SUPPORT_DIR/market-assistant-ai.log"
TARGET="data/market_assistant_brief.json"
mkdir -p "$SUPPORT_DIR"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another market-data deploy is already running" >&2
  exit 75
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/market-assistant-ai.XXXXXX")"
cleanup() {
  rm -rf "$TMP_DIR"
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT

if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "market-assistant runtime must be clean before generation" >&2
  exit 2
fi

pull_with_retry() {
  local attempt
  for attempt in 1 2 3; do
    if GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main >> "$LOG" 2>&1; then
      return 0
    fi
    echo "[$(TZ=Asia/Shanghai date '+%F %T')] AI brief git pull failed (attempt $attempt/3)" >> "$LOG"
    if (( attempt < 3 )); then
      sleep $((attempt * 10))
    fi
  done
  return 1
}

if ! pull_with_retry; then
  echo "source sync unavailable after retries; keep previous AI brief" >&2
  exit 1
fi

python3 scripts/update_market_assistant_brief.py \
  --output "$TMP_DIR/market_assistant_brief.json" \
  --previous-output "$TARGET" \
  --timeout 300

python3 - "$TMP_DIR/market_assistant_brief.json" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("schema_version") != 1 or payload.get("status") != "ready":
    raise SystemExit("AI brief output failed schema/status validation")
if not payload.get("source_fingerprint") or not payload.get("key_moves"):
    raise SystemExit("AI brief output is missing grounding evidence")
if payload.get("fixed_logic") != ["otc_structure_library", "quant_model_rules"]:
    raise SystemExit("AI brief fixed-logic boundary changed")
PY

cp "$TMP_DIR/market_assistant_brief.json" "$TARGET"

while IFS= read -r staged; do
  [[ -z "$staged" ]] && continue
  if [[ "$staged" != "$TARGET" ]]; then
    echo "refusing to include unrelated staged file: $staged" >&2
    exit 2
  fi
done < <(git diff --cached --name-only)

if [[ -z "$(git status --porcelain -- "$TARGET")" ]]; then
  echo "AI brief source fingerprint unchanged"
  exit 0
fi

git add -- "$TARGET"
git commit -m "Update market assistant AI brief"
git push origin HEAD:main

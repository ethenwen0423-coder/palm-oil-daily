#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
LOCK_DIR="$SUPPORT_DIR/supply-demand-deploy.lock"
TARGET="data/supply-demand.json"
REPORT_DATE="${1:-$(TZ=Asia/Shanghai date +%F)}"

cd "$ROOT"
mkdir -p "$SUPPORT_DIR"

if [[ ! "$REPORT_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "report date must be YYYY-MM-DD" >&2
  exit 2
fi

if [[ "$(git branch --show-current)" != "main" ]]; then
  echo "supply-demand deploy requires the main branch" >&2
  exit 2
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another supply-demand deploy is already running" >&2
  exit 75
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/palm-oil-supply-demand.XXXXXX")"
cleanup() {
  rm -rf "$TMP_DIR"
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT

TMP_DATA="$TMP_DIR/supply-demand.json"
python3 scripts/update_supply_demand_data.py \
  --output "$TMP_DATA" \
  --existing "$TARGET" \
  --report-date "$REPORT_DATE" \
  --strict
python3 scripts/update_supply_demand_data.py --validate-only "$TMP_DATA" --strict

if [[ -f "$TARGET" ]] && cmp -s "$TMP_DATA" "$TARGET"; then
  echo "no supply-demand data or status changes"
  exit 0
fi

cp "$TMP_DATA" "$TARGET"

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  changed_path="${line:3}"
  if [[ "$changed_path" != "$TARGET" ]]; then
    echo "refusing publish because unrelated worktree change exists: $changed_path" >&2
    exit 2
  fi
done < <(git status --porcelain=v1 --untracked-files=all)

while IFS= read -r staged_path; do
  [[ -z "$staged_path" ]] && continue
  if [[ "$staged_path" != "$TARGET" ]]; then
    echo "refusing to include unrelated staged file: $staged_path" >&2
    exit 2
  fi
done < <(git diff --cached --name-only)

git add -- "$TARGET"
git commit -m "Check palm oil supply-demand data for $REPORT_DATE"
git push origin main

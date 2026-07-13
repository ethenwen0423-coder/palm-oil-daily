#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

MODE=""
REPORT_DATE=""
PERSISTENCE_CONFIRMED=false
GIT_WRITES=false

usage() {
  echo "usage: $0 (--dry-run | --publish --confirm-persistence-reviewed) --date YYYY-MM-DD" >&2
}

while (($#)); do
  case "$1" in
    --dry-run)
      [[ -z "$MODE" ]] || { usage; exit 64; }
      MODE="dry-run"
      ;;
    --publish)
      [[ -z "$MODE" ]] || { usage; exit 64; }
      MODE="publish"
      ;;
    --confirm-persistence-reviewed)
      PERSISTENCE_CONFIRMED=true
      ;;
    --date)
      shift
      REPORT_DATE="${1:-}"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 64
      ;;
  esac
  shift
done

ALLOWED_PATHS=(
  "data/forecast/evaluated/"
  "data/forecast/metrics/latest.json"
  "data/forecast/metrics/20d.json"
  "data/forecast/metrics/60d.json"
  "data/review/daily/"
  "data/review/latest_review.json"
)
EXCLUDED_PATHS=(
  "data/forecast/daily/"
  "data/review/runtime_snapshots/"
  "reports/"
  "downloads/"
  "scripts/"
  "skills/"
  "all other user changes"
)
CANDIDATES=()
OUTSIDE_STAGED=()
COMMITTED_FILES=()

join_lines() {
  printf '%s\n' "$@"
}

emit_json() {
  local status="$1"
  local stage="$2"
  local reason="$3"
  local commit_sha="${4:-}"
  local branch="${5:-}"
  local push_status="${6:-not_run}"
  STATUS_VALUE="$status" \
  STAGE_VALUE="$stage" \
  REASON_VALUE="$reason" \
  MODE_VALUE="$MODE" \
  DATE_VALUE="$REPORT_DATE" \
  CONFIRMED_VALUE="$PERSISTENCE_CONFIRMED" \
  WRITES_VALUE="$GIT_WRITES" \
  COMMIT_VALUE="$commit_sha" \
  BRANCH_VALUE="$branch" \
  PUSH_VALUE="$push_status" \
  ALLOWED_TEXT="$(join_lines "${ALLOWED_PATHS[@]}")" \
  CANDIDATE_TEXT="$(join_lines "${CANDIDATES[@]-}")" \
  EXCLUDED_TEXT="$(join_lines "${EXCLUDED_PATHS[@]}")" \
  OUTSIDE_STAGED_TEXT="$(join_lines "${OUTSIDE_STAGED[@]-}")" \
  COMMITTED_TEXT="$(join_lines "${COMMITTED_FILES[@]-}")" \
  python3 - <<'PY'
import json
import os

def lines(name: str) -> list[str]:
    return [item for item in os.environ[name].splitlines() if item]

reason = os.environ["REASON_VALUE"] or None
payload = {
    "status": os.environ["STATUS_VALUE"],
    "stage": os.environ["STAGE_VALUE"] or None,
    "reason": reason,
    "blocked_reason": reason if os.environ["STATUS_VALUE"] == "blocked" else None,
    "mode": os.environ["MODE_VALUE"],
    "date": os.environ["DATE_VALUE"],
    "persistence_confirmed": os.environ["CONFIRMED_VALUE"].lower() == "true",
    "allowed_paths": lines("ALLOWED_TEXT"),
    "candidate_files": lines("CANDIDATE_TEXT"),
    "excluded_paths": lines("EXCLUDED_TEXT"),
    "non_allowlisted_staged_files": lines("OUTSIDE_STAGED_TEXT"),
    "committed_files": lines("COMMITTED_TEXT"),
    "commit_sha": os.environ["COMMIT_VALUE"] or None,
    "branch": os.environ["BRANCH_VALUE"] or None,
    "push_status": os.environ["PUSH_VALUE"],
    "git_write_operations_performed": os.environ["WRITES_VALUE"].lower() == "true",
}
print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
PY
}

fail() {
  local status="$1"
  local stage="$2"
  local reason="$3"
  local commit_sha="${4:-}"
  local branch="${5:-}"
  local push_status="${6:-not_run}"
  emit_json "$status" "$stage" "$reason" "$commit_sha" "$branch" "$push_status"
  exit 2
}

if [[ -z "$MODE" || -z "$REPORT_DATE" ]]; then
  fail "blocked" "arguments" "exactly one of --dry-run or --publish and --date YYYY-MM-DD are required"
fi
if [[ "$MODE" == "publish" && "$PERSISTENCE_CONFIRMED" != true ]]; then
  fail "blocked" "confirmation" "--publish requires --confirm-persistence-reviewed"
fi
if ! python3 - "$REPORT_DATE" <<'PY'
from datetime import date
import sys

try:
    parsed = date.fromisoformat(sys.argv[1])
except ValueError:
    raise SystemExit(1)
raise SystemExit(0 if parsed.isoformat() == sys.argv[1] else 1)
PY
then
  fail "blocked" "arguments" "date must be valid YYYY-MM-DD"
fi

is_allowed() {
  local path="$1"
  case "$path" in
    data/forecast/evaluated/*|data/review/daily/*)
      return 0
      ;;
    data/forecast/metrics/latest.json|data/forecast/metrics/20d.json|data/forecast/metrics/60d.json|data/review/latest_review.json)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_date_candidate() {
  local path="$1"
  case "$path" in
    "data/forecast/evaluated/$REPORT_DATE.json"|"data/review/daily/$REPORT_DATE.json"|data/forecast/metrics/latest.json|data/forecast/metrics/20d.json|data/forecast/metrics/60d.json|data/review/latest_review.json)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_retention_deletion() {
  local status_code="$1"
  local path="$2"
  [[ "$status_code" == *D* ]] && [[ "$path" == data/forecast/evaluated/*.json || "$path" == data/review/daily/*.json ]]
}

collect_preflight() {
  OUTSIDE_STAGED=()
  while IFS= read -r -d '' staged_path; do
    if ! is_allowed "$staged_path"; then
      OUTSIDE_STAGED+=("$staged_path")
    fi
  done < <(git diff --cached --name-only -z)

  CANDIDATES=()
  while IFS= read -r -d '' status_entry; do
    status_code="${status_entry:0:2}"
    path="${status_entry:3}"
    staged_code="${status_code:0:1}"
    if is_allowed "$path" \
      && [[ "$path" != */.gitkeep ]] \
      && { is_date_candidate "$path" || is_retention_deletion "$status_code" "$path" || [[ "$staged_code" != " " && "$staged_code" != "?" ]]; }; then
      CANDIDATES+=("$path")
    fi
  done < <(
    git -c status.renames=false status --porcelain=v1 -z --untracked-files=all -- \
      data/forecast/evaluated \
      data/forecast/metrics/latest.json \
      data/forecast/metrics/20d.json \
      data/forecast/metrics/60d.json \
      data/review/daily \
      data/review/latest_review.json
  )
}

collect_preflight
if ((${#OUTSIDE_STAGED[@]} > 0)); then
  fail "blocked" "preflight" "staging area contains non-allowlisted paths: $(IFS=', '; echo "${OUTSIDE_STAGED[*]}")"
fi

if [[ "$MODE" == "dry-run" ]]; then
  emit_json "ok" "preflight" ""
  exit 0
fi

if ((${#CANDIDATES[@]} == 0)); then
  emit_json "noop" "preflight" "no prediction-review data changes"
  exit 0
fi

GIT_WRITES=true
if ! git add -- "${CANDIDATES[@]}"; then
  fail "failed" "stage" "failed to stage allowlisted prediction-review data"
fi

COMMITTED_FILES=()
while IFS= read -r -d '' staged_path; do
  COMMITTED_FILES+=("$staged_path")
  if ! is_allowed "$staged_path"; then
    OUTSIDE_STAGED+=("$staged_path")
  fi
done < <(git diff --cached --name-only -z)
if ((${#OUTSIDE_STAGED[@]} > 0)); then
  fail "blocked" "post_stage_validation" "staging area contains non-allowlisted paths after staging: $(IFS=', '; echo "${OUTSIDE_STAGED[*]}")"
fi
if ((${#COMMITTED_FILES[@]} == 0)); then
  emit_json "noop" "post_stage_validation" "no prediction-review data changes"
  exit 0
fi

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  fail "failed" "commit" "cannot publish from detached HEAD"
fi
if ! git commit -m "Update prediction review $REPORT_DATE" >/dev/null; then
  fail "failed" "commit" "prediction-review data commit failed" "" "$BRANCH"
fi
COMMIT_SHA="$(git rev-parse HEAD)"
if ! git push origin "$BRANCH" >/dev/null; then
  fail "failed" "push" "prediction-review data push failed" "$COMMIT_SHA" "$BRANCH" "failed"
fi

emit_json "ok" "complete" "" "$COMMIT_SHA" "$BRANCH" "ok"

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_ROOT="${PALM_OIL_AUTOMATION_ROOT:-$HOME/Sites/palm-oil-daily}"
PLIST="$HOME/Library/LaunchAgents/com.vinsontesla.oil-futures-tab.plist"
SUPPORT_DIR="$HOME/Library/Application Support/VinsonTesla"
RUNNER="$SUPPORT_DIR/oil-futures-tab.sh"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$SUPPORT_DIR"

if [[ "$ROOT" != "$RUNTIME_ROOT" ]]; then
  mkdir -p "$(dirname "$RUNTIME_ROOT")"
  if [[ ! -d "$RUNTIME_ROOT/.git" ]]; then
    git clone "$(git -C "$ROOT" remote get-url origin)" "$RUNTIME_ROOT"
  else
    git -C "$RUNTIME_ROOT" pull --ff-only
  fi
fi

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl disable "gui/$(id -u)/com.vinsontesla.oil-futures-tab" >/dev/null 2>&1 || true
rm -f "$PLIST" "$RUNNER"

echo "disabled independent oil-futures tab launchd"
echo "oil-futures tab now refreshes from the weekday daily watchdog schedule"
echo "runtime root $RUNTIME_ROOT"

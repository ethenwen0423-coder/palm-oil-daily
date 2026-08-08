#!/usr/bin/env bash
set -euo pipefail

MODE="${1:---dry-run}"
case "$MODE" in
  --dry-run|--apply) ;;
  *)
    echo "usage: sudo bash server/install_codex_cli.sh [--dry-run|--apply]" >&2
    exit 2
    ;;
esac

command -v npm >/dev/null 2>&1 || {
  echo "npm is required before installing the official @openai/codex package" >&2
  exit 2
}

if [[ "$MODE" == "--dry-run" ]]; then
  printf '%s\n' '{"status":"planned","package":"@openai/codex","credentials_modified":false}'
  exit 0
fi

[[ "$(id -u)" -eq 0 ]] || {
  echo "--apply must run as root" >&2
  exit 2
}

npm install --global @openai/codex
codex_bin="$(command -v codex)"
[[ -n "$codex_bin" && -x "$codex_bin" ]] || {
  echo "official Codex CLI installation completed without an executable" >&2
  exit 2
}
version="$($codex_bin --version)"
python3 - "$codex_bin" "$version" <<'PY'
import json
import sys

print(json.dumps({
    "status": "ok",
    "package": "@openai/codex",
    "executable": sys.argv[1],
    "version": sys.argv[2],
    "credentials_modified": False,
}, sort_keys=True))
PY

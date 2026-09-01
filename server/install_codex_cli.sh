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

legacy_backup=""
existing_codex="$(command -v codex || true)"
if [[ -n "$existing_codex" ]]; then
  existing_real="$(readlink -f "$existing_codex")"
  npm_codex_root="$(npm root --global)/@openai/codex"
  case "$existing_real" in
    "$npm_codex_root"/*)
      ;;
    /usr/local/lib/codex/*/vendor/*/bin/codex)
      legacy_version="$($existing_codex --version | awk '{print $2}')"
      [[ -n "$legacy_version" ]] || {
        echo "existing standalone Codex CLI did not report a version" >&2
        exit 2
      }
      legacy_backup="${existing_codex}.standalone-${legacy_version}"
      [[ ! -e "$legacy_backup" && ! -L "$legacy_backup" ]] || {
        echo "legacy Codex backup already exists: $legacy_backup" >&2
        exit 2
      }
      mv -- "$existing_codex" "$legacy_backup"
      ;;
    *)
      echo "refusing to overwrite an unrecognized Codex executable: $existing_codex -> $existing_real" >&2
      exit 2
      ;;
  esac
fi

if ! npm install --global @openai/codex; then
  if [[ -n "$legacy_backup" && ! -e "$existing_codex" && ! -L "$existing_codex" ]]; then
    mv -- "$legacy_backup" "$existing_codex"
  fi
  exit 1
fi
codex_bin="$(command -v codex)"
[[ -n "$codex_bin" && -x "$codex_bin" ]] || {
  echo "official Codex CLI installation completed without an executable" >&2
  exit 2
}
version="$($codex_bin --version)"
python3 - "$codex_bin" "$version" "$legacy_backup" <<'PY'
import json
import sys

print(json.dumps({
    "status": "ok",
    "package": "@openai/codex",
    "executable": sys.argv[1],
    "version": sys.argv[2],
    "credentials_modified": False,
    "legacy_backup": sys.argv[3] or None,
}, sort_keys=True))
PY

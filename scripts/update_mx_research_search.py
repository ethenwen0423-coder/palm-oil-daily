#!/usr/bin/env python3
"""Call the Eastmoney Miaoxiang finance search API and persist its raw body."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


API_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search"


def api_error(body: bytes) -> str:
    """Return the upstream semantic error without treating an HTTP 200 as success."""
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "invalid JSON response"
    if not isinstance(payload, dict):
        return "unexpected response type"
    status = payload.get("status", payload.get("code", 0))
    code = payload.get("code", status)
    success = payload.get("success")
    if status in (0, "0") and code in (0, "0") and success is not False:
        return ""
    return str(payload.get("message") or f"upstream status={status} code={code}")[:240]


def request_body(query: str, api_key: str, timeout: int) -> bytes:
    body = json.dumps({"query": query}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "apikey": api_key},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def atomic_write(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(body)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    api_key = os.environ.get("MX_APIKEY", "").strip()
    if not api_key:
        print("MX_APIKEY is not configured")
        return 2
    try:
        body = request_body(args.query, api_key, args.timeout)
        atomic_write(args.output, body)
        error = api_error(body)
        if error:
            print(f"mx-search API rejected request: {error}")
            return 3
        print(f"raw_response={args.output}")
        return 0
    except (OSError, urllib.error.URLError) as exc:
        print(f"mx-search request failed: {str(exc)[:240]}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

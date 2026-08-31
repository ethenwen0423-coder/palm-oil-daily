#!/usr/bin/env python3
"""Call the report-search skill gateway and persist its raw response body."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


API_URL = "https://openapi.iwencai.com/v1/comprehensive/search"


def request_body(query: str, api_key: str, timeout: int) -> bytes:
    body = json.dumps(
        {"channels": ["report"], "app_id": "AIME_SKILL", "query": query},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Claw-Call-Type": "normal",
            "X-Claw-Skill-Id": "report-search",
            "X-Claw-Skill-Version": "2.0.0",
            "X-Claw-Plugin-Id": "none",
            "X-Claw-Plugin-Version": "none",
            "X-Claw-Trace-Id": secrets.token_hex(32),
        },
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
    api_key = os.environ.get("IWENCAI_API_KEY", "").strip()
    if not api_key:
        print("IWENCAI_API_KEY is not configured")
        return 2
    try:
        atomic_write(args.output, request_body(args.query, api_key, args.timeout))
        print(f"raw_response={args.output}")
        return 0
    except urllib.error.HTTPError as exc:
        body = exc.read()
        atomic_write(args.output, body)
        message = body.decode("utf-8", "replace").strip().replace("\n", " ")[:240]
        print(f"report-search request failed: HTTP {exc.code}: {message}")
        return 3
    except (OSError, urllib.error.URLError) as exc:
        print(f"report-search request failed: {str(exc)[:240]}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

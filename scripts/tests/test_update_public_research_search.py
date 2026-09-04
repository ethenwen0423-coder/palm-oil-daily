from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("update_public_research_search", ROOT / "scripts" / "update_public_research_search.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


class PublicResearchSearchTests(unittest.TestCase):
    def test_report_search_contract_and_raw_response_passthrough(self):
        raw = b'{"status_code":0,"data":[{"id":"r1"}]}'
        captured = {}

        def urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return FakeResponse(raw)

        with patch.object(MODULE.urllib.request, "urlopen", side_effect=urlopen):
            result = MODULE.request_body("棕榈油 研报", "secret", 12)
        request = captured["request"]
        payload = json.loads(request.data)
        self.assertEqual(result, raw)
        self.assertEqual(payload, {"query": "棕榈油 研报", "channels": ["report"], "app_id": "AIME_SKILL", "size": 20})
        self.assertEqual(request.get_header("X-claw-skill-id"), "report-search")
        self.assertEqual(request.get_header("X-claw-skill-version"), "1.0.0")
        self.assertEqual(len(request.get_header("X-claw-trace-id")), 64)
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")


if __name__ == "__main__":
    unittest.main()

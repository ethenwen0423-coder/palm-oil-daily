from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("update_mx_research_search", ROOT / "scripts" / "update_mx_research_search.py")
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


class MxResearchSearchTests(unittest.TestCase):
    def test_mx_contract_and_raw_response_passthrough(self):
        raw = b'{"status":0,"data":{"data":{"llmSearchResponse":{"data":[]}}}}'
        captured = {}

        def urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return FakeResponse(raw)

        with patch.object(MODULE.urllib.request, "urlopen", side_effect=urlopen):
            result = MODULE.request_body("棕榈油 研报", "secret", 12)
        request = captured["request"]
        self.assertEqual(result, raw)
        self.assertEqual(json.loads(request.data), {"query": "棕榈油 研报"})
        self.assertEqual(request.get_header("Apikey"), "secret")
        self.assertEqual(captured["timeout"], 12)


if __name__ == "__main__":
    unittest.main()

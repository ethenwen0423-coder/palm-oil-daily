from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("update_htfc_tianji_data", ROOT / "scripts" / "update_htfc_tianji_data.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


class TianjiCollectorTests(unittest.TestCase):
    def test_news_resolves_tag_before_filter_and_never_persists_key(self):
        calls = []

        def opener(request, *, timeout):
            calls.append(request)
            if request.full_url.endswith("/bus/info"):
                return FakeResponse({"errorCode": 0, "data": {"tags": [{"name": "油脂油料", "tid": "tags150"}]}})
            return FakeResponse({"errorCode": 0, "data": [{"id": "KX1", "content": "油脂快讯"}]})

        client = MODULE.TianjiClient("https://example.test", "secret-key", opener=opener)
        result = MODULE.collect_news(client)
        self.assertEqual(result["status"], "ok")
        self.assertIn("tags=tags150", calls[1].full_url)
        self.assertEqual(calls[0].get_header("Apikey"), "secret-key")
        self.assertNotIn("secret-key", json.dumps(result, ensure_ascii=False))

    def test_smart_kline_does_not_guess_ambiguous_product(self):
        calls = []
        labels = [
            {"name": "棕榈油", "code": "p_one", "leafNode": True, "child": []},
            {"name": "棕榈油", "code": "p_two", "leafNode": True, "child": []},
            {"name": "豆油", "code": "y_2", "leafNode": True, "child": []},
            {"name": "菜油", "code": "oi_2", "leafNode": True, "child": []},
        ]

        def opener(request, *, timeout):
            calls.append(request.full_url)
            if request.full_url.endswith("list_report_label_tree"):
                return FakeResponse({"code": 1, "data": labels})
            return FakeResponse({"code": 1, "data": {"kLineAiReportDate": "2026-08-26"}})

        result = MODULE.collect_smart_kline(MODULE.TianjiClient("https://example.test", "key", opener=opener))
        self.assertEqual(result["products"]["P"]["status"], "mapping_required")
        self.assertFalse(any("varNum=p_one" in url or "varNum=p_two" in url for url in calls))
        self.assertTrue(any("varNum=y_2" in url for url in calls))

    def test_restricted_modules_degrade_independently(self):
        def opener(request, *, timeout):
            if "/bus/info" in request.full_url:
                if "/filter" in request.full_url:
                    return FakeResponse({"errorCode": 0, "data": []})
                return FakeResponse({"errorCode": 0, "data": {"tags": [{"name": "油脂油料", "tid": "tags150"}]}})
            raise HTTPError(request.full_url, 403, "Forbidden", {}, None)

        payload = MODULE.collect(MODULE.TianjiClient("https://example.test", "key", opener=opener))
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["modules"]["news_flash"]["status"], "ok")
        self.assertEqual(payload["modules"]["research_reports"]["status"], "permission_denied")
        self.assertEqual(payload["mode"], "read_only")


if __name__ == "__main__":
    unittest.main()

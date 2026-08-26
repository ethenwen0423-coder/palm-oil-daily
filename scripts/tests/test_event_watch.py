import importlib.util
import io
import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


WATCH = load("event_watch_base_test", ROOT / "server" / "market_watch.py")
EVENTS = load("event_watch_test", ROOT / "server" / "event_watch.py")
RUNNER = load("event_watch_runner_test", ROOT / "server" / "run_event_watch.py")


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self):
        return self.payload


class EventWatchTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 26, 10, 5, tzinfo=WATCH.SHANGHAI)

    def test_htfc_flash_uses_exact_oil_tag_and_preserves_source_fields(self):
        payload = {"data": [{
            "id": "KX1", "title": "印尼棕榈油出口更新", "content": "GAPKI 发布数据",
            "date": "2026-08-26", "time": "10:04", "tag": "tags150",
            "tagName": "油脂油料", "type": "鹰眼", "stars": 3,
        }]}
        with patch.object(EVENTS, "request_json", return_value=payload) as request:
            events, source = EVENTS.htfc_flash_events(WATCH, "https://example.test", "key", self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(events[0]["source_fields"]["tag"], "tags150")
        self.assertIn("tags=tags150", request.call_args.args[0])
        self.assertEqual(request.call_args.kwargs["headers"], {"apikey": "key"})

    def test_htfc_report_permission_failure_is_not_reported_as_zero(self):
        from urllib.error import HTTPError
        error = HTTPError("https://x", 403, "Forbidden", {}, io.BytesIO(b""))
        self.addCleanup(error.close)
        with patch.object(EVENTS, "request_json", side_effect=error):
            events, source = EVENTS.htfc_report_events(WATCH, "https://example.test", "key", self.now)
        self.assertEqual(events, [])
        self.assertEqual(source["state"], "forbidden")
        self.assertIn("HTTPError", source["detail"])

    def test_rss_results_keep_provider_and_original_link(self):
        xml = '''<?xml version="1.0"?><rss><channel><item><title>棕榈油出口增加</title><description>产地数据更新</description><link>https://example.test/a</link><guid>one</guid><pubDate>Wed, 26 Aug 2026 02:04:00 GMT</pubDate></item></channel></rss>'''.encode("utf-8")
        with patch.object(EVENTS.urllib.request, "urlopen", return_value=Response(xml)):
            events, source = EVENTS.rss_events(WATCH, self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(len(events), 2)
        self.assertTrue(all(item["source"].startswith("跨站新闻·") for item in events))
        self.assertTrue(all(item["url"] == "https://example.test/a" for item in events))

    def test_event_merge_keeps_price_events_and_replaces_old_news(self):
        prior = {
            "generated_at": "2026-08-26T10:05:00+08:00",
            "events": [
                {"id": "price:1", "kind": "market", "observed_at": "2026-08-26T10:05:00+08:00"},
                {"id": "old-news", "kind": "event", "observed_at": "2026-08-26T09:00:00+08:00"},
            ],
            "sources": [{"name": "全量期货行情", "state": "ready"}],
            "coverage": {"priced_contracts": 39},
        }
        news = [{"id": "new-news", "kind": "event", "observed_at": "2026-08-26T10:04:00+08:00"}]
        sources = [{"name": "跨站新闻搜索", "state": "ready"}]
        result = RUNNER.merge_snapshot(WATCH, prior, news, sources, self.now)
        self.assertEqual(result["generated_at"], prior["generated_at"])
        self.assertEqual({item["id"] for item in result["events"]}, {"price:1", "new-news"})
        self.assertEqual(result["coverage"]["event_sources_ready"], 1)


if __name__ == "__main__":
    unittest.main()

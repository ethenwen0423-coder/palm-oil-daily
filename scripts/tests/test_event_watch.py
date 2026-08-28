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

    def test_long_flash_uses_complete_preview_and_expanded_detail_without_hard_cutoff(self):
        body = "【美国中西部天气更新】第一段说明降雨分散。" + "中部产区天气系统继续东移。" * 12 + "最后一段说明大豆影响仍需核验。"
        event = EVENTS.normalize_event(
            WATCH,
            prefix="htfc-flash",
            source="机构资讯·油脂油料快讯",
            title="美国中西部天气更新",
            summary=body,
            observed_at=self.now.isoformat(),
            source_id="KX-long",
        )
        self.assertIsNotNone(event)
        self.assertTrue(event["summary"].endswith("。"))
        self.assertLess(len(event["summary"]), len(body))
        self.assertTrue(event["detail_summary"].endswith("。"))
        self.assertGreater(len(event["detail_summary"]), len(event["summary"]))
        self.assertFalse(event["direct_source_available"])
        self.assertIn("不代表来源方官方立场", event["ai_notice"])

    def test_sentence_digest_falls_back_to_complete_title_instead_of_partial_body(self):
        preview, detail = WATCH.summarize_source_event("棕榈油出口变化", "这是一个没有句号且非常长的来源片段" * 30)
        self.assertEqual(preview, "棕榈油出口变化。")
        self.assertEqual(detail, preview)

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

    def test_weather_events_publish_direct_forecast_with_ai_notice(self):
        payload = {"daily": {
            "time": ["2026-08-26"] * 7,
            "precipitation_sum": [1, 2, 0, 1, 0, 2, 1],
            "precipitation_probability_max": [20, 30, 10, 20, 10, 40, 20],
            "temperature_2m_max": [34, 36, 37, 36, 35, 34, 33],
            "temperature_2m_min": [24, 24, 25, 25, 24, 24, 23],
        }}
        with patch.object(EVENTS, "request_json", return_value=payload):
            events, source = EVENTS.weather_events(WATCH, self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(len(events), len(EVENTS.WEATHER_REGIONS))
        self.assertTrue(all(item["category"] == "天气产量研判" for item in events))
        self.assertTrue(all(item["direct_source_available"] for item in events))
        self.assertTrue(all("不构成投资建议" in item["ai_notice"] for item in events))
        self.assertTrue(all("production_chain" in item["weather_analysis"] for item in events))
        self.assertTrue(all("market_chain" in item["weather_analysis"] for item in events))
        by_title = {item["title"]: item for item in events}
        iowa = next(item for title, item in by_title.items() if "爱荷华" in title)
        brazil = next(item for title, item in by_title.items() if "马托格罗索" in title)
        self.assertEqual(iowa["impact"], "高")
        self.assertIn("单产", iowa["summary"])
        self.assertEqual(brazil["impact"], "低")
        self.assertIn("暂不等于大豆减产", brazil["title"])
        self.assertIn("没有直接受损对象", brazil["summary"])

    def test_canola_harvest_rain_maps_to_supply_timing_not_generic_crop_stress(self):
        region = next(item for item in EVENTS.WEATHER_REGIONS if item["profile"] == "canola")
        analysis = EVENTS.weather_analysis(region, self.now, 52.5, 26.9, 0, 5)
        self.assertEqual(analysis["impact"], "高")
        self.assertIn("收获期多雨", analysis["title"])
        self.assertIn("上市节奏", analysis["market_chain"])
        self.assertIn("不等同生物学单产下降", analysis["market_chain"])

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

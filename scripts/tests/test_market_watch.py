import importlib.util
import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("market_watch_test", ROOT / "server" / "market_watch.py")
WATCH = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(WATCH)


class MarketWatchTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 24, 10, 5, tzinfo=WATCH.SHANGHAI)
        self.oil = {"contracts": [{"symbol": "FCPO", "name": "马棕油", "price": 4200, "change_pct": 1.2}]}
        self.exchange = {"contracts": [{"symbol": "P2701", "product": "棕榈油", "price": 8000, "change_pct": 0.8}]}

    def test_first_snapshot_has_coverage_but_no_invented_price_event(self):
        payload, quotes = WATCH.build_watch(self.oil, self.exchange, {}, [], self.now, None)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["coverage"]["priced_contracts"], 2)
        self.assertEqual(payload["events"], [])
        self.assertIn("P2701", quotes)
        self.assertEqual(len(payload["sources"]), 1)

    def test_price_move_is_source_backed_and_has_impact_interpretation(self):
        previous = {"P2701": {"price": 7900}, "FCPO": {"price": 4200}}
        payload, _ = WATCH.build_watch(self.oil, self.exchange, previous, [], self.now, None)
        event = next(item for item in payload["events"] if item["scope"] == "P2701")
        self.assertEqual(event["kind"], "market")
        self.assertIn("5分钟确认异动", event["category"])
        self.assertIn("quote:P2701", event["evidence_ids"])
        self.assertTrue(event["interpretation"])

    def test_small_single_scan_move_is_filtered(self):
        exchange = {"contracts": [{"symbol": "P2701", "product": "棕榈油", "price": 10048, "change_pct": 0.8}]}
        payload, _ = WATCH.build_watch({}, exchange, {"P2701": {"price": 10000}}, [], self.now)
        self.assertEqual(payload["events"], [])
        self.assertEqual(payload["coverage"]["market_moves_published"], 0)

    def test_two_same_direction_moves_require_cumulative_confirmation(self):
        first_exchange = {"contracts": [{"symbol": "P2701", "product": "棕榈油", "price": 10060, "change_pct": 0.6}]}
        first_payload, first_state = WATCH.build_watch({}, first_exchange, {"P2701": {"price": 10000}}, [], self.now)
        self.assertEqual(first_payload["events"], [])
        second_now = self.now + WATCH.timedelta(minutes=5)
        second_exchange = {"contracts": [{"symbol": "P2701", "product": "棕榈油", "price": 10120, "change_pct": 1.2}]}
        second_payload, _ = WATCH.build_watch({}, second_exchange, first_state, [], second_now)
        event = second_payload["events"][0]
        self.assertEqual(event["category"], "10分钟确认异动")
        self.assertIn("上涨 1.20%", event["title"])

    def test_cooldown_blocks_repeated_same_contract_alert(self):
        previous = {
            "P2701": {
                "price": 10000,
                "last_event_at": (self.now - WATCH.timedelta(minutes=10)).isoformat(),
                "last_event_direction": 1,
                "last_event_move_pct": 1.1,
            }
        }
        exchange = {"contracts": [{"symbol": "P2701", "product": "棕榈油", "price": 10100, "change_pct": 2.0}]}
        payload, _ = WATCH.build_watch({}, exchange, previous, [], self.now)
        self.assertEqual(payload["events"], [])

    def test_each_scan_publishes_only_two_largest_moves(self):
        exchange = {"contracts": [
            {"symbol": "P2701", "product": "棕榈油", "price": 10100, "change_pct": 1.0},
            {"symbol": "Y2701", "product": "豆油", "price": 10200, "change_pct": 2.0},
            {"symbol": "OI2701", "product": "菜油", "price": 10300, "change_pct": 3.0},
        ]}
        previous = {symbol: {"price": 10000} for symbol in ("P2701", "Y2701", "OI2701")}
        payload, _ = WATCH.build_watch({}, exchange, previous, [], self.now)
        self.assertEqual(payload["coverage"]["market_moves_detected"], 3)
        self.assertEqual(payload["coverage"]["market_moves_published"], 2)
        self.assertEqual({event["scope"] for event in payload["events"]}, {"Y2701", "OI2701"})

    def test_legacy_small_moves_and_recent_duplicates_are_pruned(self):
        previous_events = [
            {"id": "small", "kind": "market", "category": "5分钟行情异动", "title": "焦煤 下跌 0.44%", "scope": "JM2701", "observed_at": "2026-08-24T10:00:00+08:00"},
            {"id": "latest", "kind": "market", "category": "5分钟行情异动", "title": "燃油 上涨 1.10%", "scope": "FU2611", "observed_at": "2026-08-24T09:55:00+08:00"},
            {"id": "duplicate", "kind": "market", "category": "5分钟行情异动", "title": "燃油 上涨 1.00%", "scope": "FU2611", "observed_at": "2026-08-24T09:35:00+08:00"},
        ]
        payload, _ = WATCH.build_watch(self.oil, self.exchange, {}, previous_events, self.now)
        self.assertEqual([event["id"] for event in payload["events"]], ["latest"])

    def test_news_event_impact_matches_policy_keyword(self):
        impact, interpretation = WATCH.impact_for("印尼 B50 生物柴油政策")
        self.assertEqual(impact, "高")
        self.assertIn("政策", interpretation)

    def test_public_flash_fallback_keeps_only_relevant_source_backed_events(self):
        response = type("Response", (), {
            "__enter__": lambda self: self,
            "__exit__": lambda self, *args: None,
            "read": lambda self: json.dumps({"news": [
                {"id": "1", "title": "印尼上调生物柴油掺混比例", "digest": "棕榈油需求预期变化", "showtime": "2026-08-24 10:04:00", "url_m": "https://wap.eastmoney.com/a/1.html"},
                {"id": "2", "title": "某公司发布半年报", "digest": "普通公告", "showtime": "2026-08-24 10:03:00"},
            ]}, ensure_ascii=False).encode("utf-8"),
        })()
        with patch.object(WATCH.urllib.request, "urlopen", return_value=response):
            events, source = WATCH.news_events(None, self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["source"], "东方财富7x24快讯")
        self.assertEqual(events[0]["url"], "https://wap.eastmoney.com/a/1.html")

    def test_generic_tariff_story_is_not_treated_as_oil_event(self):
        self.assertFalse(WATCH.flash_relevant("家具出口遭遇美国关税调查"))
        self.assertTrue(WATCH.flash_relevant("布伦特原油期货跌幅扩大至3%"))
        self.assertTrue(WATCH.flash_relevant("大豆产区降雨改善单产预期"))

    def test_quote_builder_never_calls_news_network(self):
        with patch.object(WATCH, "news_events", side_effect=AssertionError("news called")):
            payload, _ = WATCH.build_watch(self.oil, self.exchange, {}, [], self.now, "secret")
        self.assertEqual(payload["coverage"]["priced_contracts"], 2)


if __name__ == "__main__":
    unittest.main()

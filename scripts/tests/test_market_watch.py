import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


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
        self.assertEqual(payload["sources"][1]["state"], "unavailable")

    def test_price_move_is_source_backed_and_has_impact_interpretation(self):
        previous = {"P2701": {"price": 7900}, "FCPO": {"price": 4200}}
        payload, _ = WATCH.build_watch(self.oil, self.exchange, previous, [], self.now, None)
        event = next(item for item in payload["events"] if item["scope"] == "P2701")
        self.assertEqual(event["kind"], "market")
        self.assertIn("5分钟行情异动", event["category"])
        self.assertIn("quote:P2701", event["evidence_ids"])
        self.assertTrue(event["interpretation"])

    def test_news_event_impact_matches_policy_keyword(self):
        impact, interpretation = WATCH.impact_for("印尼 B50 生物柴油政策")
        self.assertEqual(impact, "高")
        self.assertIn("政策", interpretation)


if __name__ == "__main__":
    unittest.main()

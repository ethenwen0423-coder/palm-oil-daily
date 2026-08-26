import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "server_market_watch_test", ROOT / "server" / "run_market_watch.py"
)
WATCH = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(WATCH)


class ServerMarketWatchTests(unittest.TestCase):
    def test_market_windows_cover_day_night_and_overnight_sessions(self):
        cases = {
            datetime(2026, 8, 26, 9, 30, tzinfo=WATCH.SHANGHAI): True,
            datetime(2026, 8, 26, 10, 20, tzinfo=WATCH.SHANGHAI): False,
            datetime(2026, 8, 26, 12, 0, tzinfo=WATCH.SHANGHAI): False,
            datetime(2026, 8, 26, 15, 4, tzinfo=WATCH.SHANGHAI): False,
            datetime(2026, 8, 26, 21, 0, tzinfo=WATCH.SHANGHAI): True,
            datetime(2026, 8, 27, 2, 29, tzinfo=WATCH.SHANGHAI): True,
            datetime(2026, 8, 29, 1, 0, tzinfo=WATCH.SHANGHAI): True,
            datetime(2026, 8, 29, 9, 30, tzinfo=WATCH.SHANGHAI): False,
        }
        for now, expected in cases.items():
            with self.subTest(now=now):
                self.assertEqual(WATCH.in_market_window(now), expected)

    def test_only_concrete_delivery_contracts_are_accepted(self):
        self.assertTrue(WATCH.concrete_contract("P2701"))
        self.assertTrue(WATCH.concrete_contract("IF2609"))
        self.assertFalse(WATCH.concrete_contract("P0"))
        self.assertFalse(WATCH.concrete_contract("棕榈油"))


if __name__ == "__main__":
    unittest.main()

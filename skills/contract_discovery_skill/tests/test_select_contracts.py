from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "select_contracts.py"
SPEC = importlib.util.spec_from_file_location("contract_discovery_select", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ExchangeDataTimeTests(unittest.TestCase):
    def test_next_trading_day_night_label_rolls_back_to_previous_evening(self) -> None:
        value, warning = MODULE.normalize_exchange_data_time(
            "2026-08-27",
            "23:00:00",
            datetime(2026, 8, 27, 6, 23, 48),
        )

        self.assertEqual(value, "2026-08-26 23:00:00")
        self.assertIn("交易日夜盘标签", warning)

    def test_completed_same_day_night_quote_is_unchanged(self) -> None:
        value, warning = MODULE.normalize_exchange_data_time(
            "2026-08-27",
            "21:05:00",
            datetime(2026, 8, 27, 21, 10, 0),
        )

        self.assertEqual(value, "2026-08-27 21:05:00")
        self.assertIsNone(warning)

    def test_unexplained_future_daytime_quote_remains_future_for_gate(self) -> None:
        value, warning = MODULE.normalize_exchange_data_time(
            "2026-08-27",
            "15:00:00",
            datetime(2026, 8, 27, 6, 23, 48),
        )

        self.assertEqual(value, "2026-08-27 15:00:00")
        self.assertIsNone(warning)

    def test_discovery_payload_keeps_selector_provenance(self) -> None:
        original = MODULE.load_akshare
        MODULE.load_akshare = lambda: (_ for _ in ()).throw(RuntimeError("offline"))
        try:
            payload = MODULE.discover(datetime(2026, 8, 27, 6, 23, 48))
        finally:
            MODULE.load_akshare = original

        self.assertEqual(payload["selector_skill"], "contract_selector_skill")


if __name__ == "__main__":
    unittest.main()

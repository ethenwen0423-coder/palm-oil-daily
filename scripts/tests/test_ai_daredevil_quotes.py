import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "ai_daredevil_quote_runtime", ROOT / "server" / "run_ai_daredevil_quotes.py"
)
RUNTIME = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(RUNTIME)


class AiDaredevilMinuteQuoteTests(unittest.TestCase):
    def test_quote_gate_requires_exact_contract_trade_date_and_fresh_source_clock(self):
        row = {"合约": "P2701", "最新价": "10,020", "开盘价": "9,990", "交易日期": "2026-08-31", "时间": "11:09:00"}
        quote = RUNTIME.BASE.quote_from_row(row, "P2701", "test")
        self.assertEqual(quote["source_time"], "11:09:00")
        now = datetime.fromisoformat("2026-08-31T11:10:30+08:00")
        self.assertTrue(RUNTIME.quote_is_current(quote, now, "day-morning-2"))
        self.assertFalse(RUNTIME.quote_is_current({**quote, "trade_date": "2026-08-28"}, now, "day-morning-2"))
        self.assertFalse(RUNTIME.quote_is_current({**quote, "source_time": "11:00:00"}, now, "day-morning-2"))
        self.assertFalse(RUNTIME.quote_is_current({**quote, "last": None}, now, "day-morning-2"))
        self.assertIsNone(RUNTIME.BASE.quote_from_row(row, "P0", "test"))
        self.assertIsNone(RUNTIME.BASE.quote_from_row(row, "P2705", "test"))

    def test_session_gate_excludes_breaks_weekends_and_accepts_overnight(self):
        cases = {
            "2026-08-31T08:59:00+08:00": None,
            "2026-08-31T09:00:00+08:00": "day-morning-1",
            "2026-08-31T10:15:00+08:00": "day-morning-1",
            "2026-08-31T10:16:00+08:00": None,
            "2026-08-31T10:30:00+08:00": "day-morning-2",
            "2026-08-31T11:31:00+08:00": None,
            "2026-08-31T13:30:00+08:00": "day-afternoon",
            "2026-08-31T21:00:00+08:00": "night-evening",
            "2026-09-01T00:01:00+08:00": "night-after-midnight",
            "2026-09-05T02:30:00+08:00": "night-after-midnight",
            "2026-09-05T02:31:00+08:00": None,
            "2026-09-06T21:00:00+08:00": None,
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(RUNTIME.trading_session(datetime.fromisoformat(value)), expected)

    def test_installer_has_trading_minute_service_and_schedule(self):
        installer = (ROOT / "server" / "install_automation.sh").read_text(encoding="utf-8")
        self.assertIn('"run_ai_daredevil_quotes.py"', installer)
        self.assertIn("palm-oil-ai-daredevil-quotes.timer", installer)
        self.assertIn("Mon..Fri *-*-* 09..15:*:00 Asia/Shanghai", installer)
        self.assertIn("Mon..Fri *-*-* 21..23:*:00 Asia/Shanghai", installer)
        self.assertIn("Tue..Sat *-*-* 00..02:*:00 Asia/Shanghai", installer)
        self.assertIn("systemctl enable --now palm-oil-ai-daredevil-quotes.timer", installer)


if __name__ == "__main__":
    unittest.main()

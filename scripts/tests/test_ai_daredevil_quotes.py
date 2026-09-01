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

    def test_night_quotes_accept_exchange_date_label_variance(self):
        evening = datetime.fromisoformat("2026-09-01T21:24:00+08:00")
        current_day = {"last": 100, "trade_date": "2026-09-01", "source_time": "21:24:00"}
        next_trade_day = {"last": 100, "trade_date": "2026-09-02", "source_time": "21:24:00"}
        self.assertTrue(RUNTIME.quote_is_current(current_day, evening, "night-evening"))
        self.assertTrue(RUNTIME.quote_is_current(next_trade_day, evening, "night-evening"))
        fresh = {"TA2701": current_day, "AL2610": next_trade_day}
        self.assertTrue(RUNTIME.quote_coverage_complete(
            list(fresh), fresh, ["2026-09-01", "2026-09-02"], "night-evening"
        ))
        self.assertEqual(
            RUNTIME.canonical_mark_date(evening, "night-evening", ["2026-09-01", "2026-09-02"]),
            "2026-09-01",
        )

    def test_after_midnight_quote_may_keep_previous_calendar_label(self):
        now = datetime.fromisoformat("2026-09-02T00:01:00+08:00")
        quote = {"last": 100, "trade_date": "2026-09-01", "source_time": "00:01:00"}
        self.assertTrue(RUNTIME.quote_is_current(quote, now, "night-after-midnight"))

    def test_quote_observation_keeps_canonical_and_source_trade_dates(self):
        now = datetime.fromisoformat("2026-09-01T21:27:00+08:00")
        quote = {
            "last": 24025, "trade_date": "2026-09-02",
            "observed_at": "2026-09-02 21:26:35", "source": "test",
        }
        observation = RUNTIME.quote_observation(quote, now, "2026-09-01")
        self.assertEqual(observation["trade_date"], "2026-09-01")
        self.assertEqual(observation["source_trade_date"], "2026-09-02")
        self.assertEqual(observation["observed_at"], "2026-09-01T21:27:00+08:00")

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

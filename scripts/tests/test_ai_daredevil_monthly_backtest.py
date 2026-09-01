import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
SPEC = importlib.util.spec_from_file_location(
    "ai_daredevil_monthly_backtest",
    ROOT / "server" / "build_ai_daredevil_monthly_backtest.py",
)
BACKTEST = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BACKTEST)


class AiDaredevilMonthlyBacktestTests(unittest.TestCase):
    def test_window_is_last_sixty_completed_calendar_months(self):
        start_period, end_period, start, end = BACKTEST.month_window(date(2026, 9, 1))
        self.assertEqual(str(start_period), "2021-09")
        self.assertEqual(str(end_period), "2026-08")
        self.assertEqual(str(start.date()), "2021-09-01")
        self.assertEqual(str(end.date()), "2026-08-31")

    def test_monthly_table_uses_static_equal_weight_cash_sleeves(self):
        index = pd.to_datetime(["2021-09-30", "2021-10-29", "2021-11-30"])
        sleeves = {
            "P": pd.Series([1.10, 1.21, 1.089], index=index),
            "RB": pd.Series([1.00, 1.10, 1.21], index=index),
        }
        monthly, years, portfolio = BACKTEST.build_monthly_table(
            sleeves, ["P", "RB", "LC"], pd.Period("2021-09", "M"), pd.Period("2021-11", "M")
        )
        self.assertEqual([item["month"] for item in monthly], ["2021-09", "2021-10", "2021-11"])
        self.assertAlmostEqual(monthly[0]["return"], (1.10 + 1.00 + 1.00) / 3 - 1)
        self.assertAlmostEqual(monthly[1]["return"], portfolio.iloc[1] / portfolio.iloc[0] - 1)
        compounded = (1 + monthly[0]["return"]) * (1 + monthly[1]["return"]) * (1 + monthly[2]["return"]) - 1
        self.assertAlmostEqual(years[0]["period_return"], compounded)
        self.assertEqual(years[0]["available_months"], 3)
        self.assertFalse(years[0]["complete_year"])

    def test_contract_symbols_are_only_real_pyymm_months(self):
        symbols = BACKTEST.contract_symbols("P", 2025, 2026)
        self.assertIn("P2501", symbols)
        self.assertIn("P2612", symbols)
        self.assertNotIn("P0", symbols)
        self.assertTrue(all(len(symbol) == 5 for symbol in symbols))


if __name__ == "__main__":
    unittest.main()

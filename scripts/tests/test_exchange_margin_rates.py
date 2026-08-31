import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("exchange_margin_rates_test", ROOT / "server" / "exchange_margin_rates.py")
MARGINS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MARGINS)


class ExchangeMarginRateTests(unittest.TestCase):
    def test_qihuo_parser_matches_exact_czce_aliases_and_uses_higher_side(self):
        html = """
        <table><tr><th>合约</th><th>现价</th><th>涨跌停</th><th>多头</th><th>空头</th></tr>
        <tr><td title="手续费更新时间：2026-08-28 21:25:25.766"><a>纯碱701 (<b>SA701</b>)</a></td>
        <td>1027</td><td>1099/955</td><td>8%</td><td>9%</td></tr></table>
        """
        rows = MARGINS.parse_qihuo_margin_rows(html, ["SA2701", "SA2705"])
        self.assertEqual(set(rows), {"SA2701"})
        self.assertEqual(rows["SA2701"]["margin_rate"], 0.09)
        self.assertFalse(rows["SA2701"]["official_direct"])

    def test_shfe_parser_uses_official_general_position_rate(self):
        payload = {"report_date": "20260828", "ContractDailyTradeArgument": [{
            "INSTRUMENTID": "al2610", "TRADINGDAY": "20260828",
            "SPEC_LONGMARGINRATIO": "0.11", "SPEC_SHORTMARGINRATIO": "0.12",
            "HDEGE_LONGMARGINRATIO": "0.10", "HDEGE_SHORTMARGINRATIO": "0.10",
        }]}
        rows = MARGINS.parse_shfe_margin_rows(payload, ["AL2610"])
        self.assertEqual(rows["AL2610"]["margin_rate"], 0.12)
        self.assertTrue(rows["AL2610"]["official_direct"])
        self.assertIn("ContractDailyTradeArgument20260828.dat", rows["AL2610"]["source_url"])

    def test_stale_or_missing_cache_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "margins.json"
            path.write_text(json.dumps({"rates": {
                "AL2610": {"margin_rate": .11, "source_updated_at": "2026-08-20"}
            }}), encoding="utf-8")
            self.assertIsNone(MARGINS.load_cached_margin_book(path, ["AL2610"], date(2026, 8, 31)))

    def test_ledger_revalues_existing_position_with_exchange_rate(self):
        ledger_spec = importlib.util.spec_from_file_location(
            "margin_ledger_test", ROOT / "skills" / "manage-bollinger-rsi-futures-fund" / "scripts" / "fund_ledger.py"
        )
        ledger = importlib.util.module_from_spec(ledger_spec)
        assert ledger_spec.loader is not None
        ledger_spec.loader.exec_module(ledger)
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary)
            ledger.command_init(SimpleNamespace(state_dir=state_dir, initial_capital=1_000_000, if_missing=True))
            state_path = state_dir / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["positions"]["AL"] = {
                "variety": "AL", "name": "沪铝", "sector": "有色", "contract": "AL2610",
                "side": 1, "quantity": 1, "average_price": 23900, "last_price": 24000,
                "multiplier": 5, "margin_rate": .20, "fee_rate": .0004,
                "entry_date": "2026-08-31", "layers": 1, "layer_fills": [],
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            rates = state_dir / "rates.json"
            rates.write_text(json.dumps({"as_of": "2026-08-31", "rates": [{
                "contract": "AL2610", "margin_rate": .11, "source": "SHFE",
                "source_url": "https://example.invalid", "source_updated_at": "20260828",
                "official_direct": True,
            }]}), encoding="utf-8")
            updated = ledger.command_update_margins(SimpleNamespace(state_dir=state_dir, rates=rates))
            self.assertEqual(updated["positions"]["AL"]["margin_rate"], .11)
            self.assertEqual(updated["positions"]["AL"]["used_margin"], 13200)
            self.assertEqual(updated["used_margin"], 13200)
            self.assertEqual(updated["positions"]["AL"]["margin_source"], "SHFE")


if __name__ == "__main__":
    unittest.main()

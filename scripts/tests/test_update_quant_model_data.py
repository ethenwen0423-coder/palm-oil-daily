import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "update_quant_model_data",
    SCRIPTS / "update_quant_model_data.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class QuantModelMarketDataTest(unittest.TestCase):
    def test_reads_wrapped_market_quotes(self):
        payload = {
            "updated_at": "2026-07-23 12:41",
            "update_session": "midday",
            "contracts": [
                {
                    "symbol": "P2609",
                    "price": "9494",
                    "change": "+2.64%",
                    "trade_date": "2026-07-23",
                    "source": "test",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oil_futures.js"
            path.write_text(
                f"window.OIL_FUTURES_CONTRACTS = {json.dumps(payload)};\n",
                encoding="utf-8",
            )
            loaded, quotes = MODULE.read_market_quotes(path)

        self.assertEqual(loaded["update_session"], "midday")
        self.assertEqual(quotes["P2609"]["price"], 9494.0)
        self.assertEqual(quotes["P2609"]["trade_date"], "2026-07-23")

    def test_attaches_exact_contract_quote_without_mutating_source(self):
        contracts = [{"symbol": "P2609", "market_date": "2026-07-22"}]
        quotes = {"P2609": {"price": 9494.0, "trade_date": "2026-07-23"}}

        enriched = MODULE.attach_current_quotes(contracts, quotes)

        self.assertNotIn("current_quote", contracts[0])
        self.assertEqual(enriched[0]["current_quote"]["price"], 9494.0)
        self.assertEqual(enriched[0]["market_date"], "2026-07-22")


if __name__ == "__main__":
    unittest.main()

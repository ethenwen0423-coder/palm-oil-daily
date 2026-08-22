import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "contract_analysis", ROOT / "server" / "contract_analysis.py"
)
ANALYSIS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ANALYSIS)


class ContractAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data_root = Path(self.temp.name)
        payload = {
            "updated_at": "2026-08-22 06:20",
            "contracts": [
                {
                    "symbol": "P2701",
                    "product": "棕榈油",
                    "exchange": "DCE",
                    "category": "油脂油料",
                    "price": 10100,
                    "change_pct": 0.1,
                    "fundamental": {
                        "category": "油脂",
                        "evidence_count": 0,
                        "factors": [{"title": "跟踪框架", "text": "核验库存与基差。"}],
                    },
                }
            ],
        }
        (self.data_root / "exchange_futures.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_rejects_invalid_or_unpublished_contract(self):
        with self.assertRaises(ANALYSIS.InvalidSymbol):
            ANALYSIS.analyze_contract(self.data_root, "../../etc/passwd")
        with self.assertRaises(ANALYSIS.UnknownContract):
            ANALYSIS.analyze_contract(self.data_root, "IC2609")

    @patch.object(ANALYSIS, "fetch_warrant")
    @patch.object(ANALYSIS, "fetch_history")
    @patch.object(ANALYSIS, "fetch_quote")
    def test_selected_symbol_drives_live_quote_history_and_fundamental_calls(
        self, quote, history, warrant
    ):
        quote.return_value = (
            {"price": 10200, "change_pct": 1.0, "trade_date": "2026-08-22"},
            ANALYSIS._source("行情源", "ready", "2026-08-22", "P2701"),
        )
        bars = [
            {"open": 9900 + index, "high": 9920 + index, "low": 9880 + index, "close": 9900 + index}
            for index in range(80)
        ]
        history.return_value = (
            bars,
            ANALYSIS._source("日线源", "ready", "2026-08-22", "80条"),
        )
        warrant.return_value = (
            {"title": "注册仓单｜2026-08-22", "text": "仓单 100。"},
            ANALYSIS._source("仓单源", "ready", "2026-08-22", "P"),
        )

        result = ANALYSIS.analyze_contract(self.data_root, "p2701")

        quote.assert_called_once_with("P2701")
        history.assert_called_once_with("P2701")
        warrant.assert_called_once_with("P")
        self.assertEqual(result["contract"]["price"], 10200)
        self.assertEqual(result["contract"]["fundamental"]["evidence_status"], "observed")
        self.assertIn(result["contract"]["judgement"]["stance"], {"偏强观察", "偏弱观察", "震荡等待"})
        self.assertFalse(result["degraded"])

    @patch.object(ANALYSIS, "fetch_warrant")
    @patch.object(ANALYSIS, "fetch_history")
    @patch.object(ANALYSIS, "fetch_quote")
    def test_source_failure_is_explicit_and_keeps_snapshot_labeled(
        self, quote, history, warrant
    ):
        quote.return_value = (None, ANALYSIS._source("行情源", "unavailable", None, "timeout"))
        history.return_value = ([], ANALYSIS._source("日线源", "unavailable", None, "timeout"))
        warrant.return_value = (None, ANALYSIS._source("仓单源", "unavailable", None, "timeout"))

        result = ANALYSIS.analyze_contract(self.data_root, "P2701")

        self.assertTrue(result["degraded"])
        self.assertEqual(result["contract"]["price"], 10100)
        self.assertIn("最近发布快照", result["contract"]["fundamental"]["summary"])
        self.assertTrue(all(item["status"] == "unavailable" for item in result["sources"]))


if __name__ == "__main__":
    unittest.main()

import importlib.util
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("pure_ai_fund_runtime", ROOT / "server" / "run_pure_ai_fund.py")
PURE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(PURE)


class PureAiFundTests(unittest.TestCase):
    def test_contract_histories_are_fetched_across_varieties_concurrently(self):
        dates = pd.bdate_range("2026-04-01", periods=80)
        close = pd.Series([100 + index * 0.4 for index in range(80)])
        frame = pd.DataFrame({
            "date": dates, "open": close, "high": close + 1, "low": close - 1,
            "close": close, "volume": [1000 + index for index in range(80)], "hold": [2000] * 80,
        })
        barrier = threading.Barrier(2)

        def fetch_daily(_contract):
            barrier.wait(timeout=1)
            return frame.copy()

        products = {
            "P": {"name": "棕榈油", "sector": "油脂油料"},
            "Y": {"name": "豆油", "sector": "油脂油料"},
        }
        contracts = {"P": ["P2701"], "Y": ["Y2701"]}
        with (
            patch.object(PURE.BASE, "PRODUCTS", products),
            patch.object(PURE.BASE, "current_contracts", return_value=contracts),
            patch.object(PURE.BASE, "fetch_daily", side_effect=fetch_daily),
        ):
            facts, issues = PURE.select_contract_facts(Path("/unused"))

        self.assertEqual(issues, [])
        self.assertEqual({row["variety"] for row in facts}, {"P", "Y"})

    def test_technical_snapshot_uses_one_exact_contract_history(self):
        dates = pd.bdate_range("2026-04-01", periods=80)
        close = pd.Series([100 + index * 0.4 for index in range(80)])
        frame = pd.DataFrame({
            "date": dates, "open": close, "high": close + 1, "low": close - 1,
            "close": close, "volume": [1000 + index for index in range(80)], "hold": [2000] * 80,
        })
        result = PURE.technical_snapshot(frame, "P2701")
        self.assertEqual(result["contract"], "P2701")
        self.assertGreater(result["momentum_20d"], 0)
        self.assertIn("macd_histogram", result)
        self.assertIn("volatility_20d", result)

    def test_ai_decision_must_reference_allowed_evidence_and_respect_position(self):
        context = [{"variety": "P"}]
        allowed = {"P": {"technical:P2701:2026-08-28"}}
        state = {"positions": {}}
        output = {"decisions": [{
            "variety": "P", "action": "ENTER_LONG", "confidence": 0.8,
            "open_reason": "AI研判", "next_instruction": "等待收盘", "invalidation": "跌破昨日低点",
            "evidence_ids": ["invented:evidence"],
        }]}
        decisions, issues = PURE.validate_decisions(output, context, allowed, state)
        self.assertEqual(decisions, [])
        self.assertTrue(issues)

    def test_soft_drawdown_overrides_ai_entry(self):
        facts = [{
            "variety": "P", "name": "棕榈油", "sector": "油脂油料", "signal_date": "2026-08-28",
            "execution_contract": "P2701", "execution_reference_price": 10000, "atr14": 200,
        }]
        decisions = [{
            "variety": "P", "action": "ENTER_LONG", "confidence": 0.9,
            "open_reason": "趋势向上", "next_instruction": "继续核验", "invalidation": "跌破均线", "evidence_ids": [],
        }]
        state = {"equity": 910000, "high_water_equity": 1000000, "positions": {}}
        snapshot, rows = PURE.build_signals(facts, decisions, state)
        self.assertEqual(snapshot["signals"], [])
        self.assertEqual(rows[0]["action"], "WAIT")
        self.assertIn("暂停新增风险", rows[0]["risk_override"])

    def test_plan_audit_counts_only_orders_accepted_by_ledger_risk(self):
        audit = {"order_count": 1}
        skipped = []
        result = {"decisions": [{
            "status": "skipped",
            "reason": "single contract exceeds variety notional cap",
            "signal": {"variety": "SC", "contract": "SC2610", "action": "ENTER_LONG"},
        }]}

        PURE.record_plan_outcomes(audit, skipped, result)

        self.assertEqual(audit["proposed_order_count"], 1)
        self.assertEqual(audit["order_count"], 0)
        self.assertEqual(skipped[0]["contract"], "SC2610")
        self.assertIn("notional cap", skipped[0]["reason"])

    def test_ledger_supports_an_independent_model_and_stricter_policy(self):
        ledger, _model, _signal = PURE.BASE.load_components(ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary)
            PURE.init_ledger(ledger, state_dir)
            state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
            self.assertEqual(state["model_version"], PURE.MODEL_VERSION)
            self.assertEqual(state["policy"]["max_gross_multiple"], 1.0)
            self.assertEqual(state["policy"]["max_positions"], 6)


if __name__ == "__main__":
    unittest.main()

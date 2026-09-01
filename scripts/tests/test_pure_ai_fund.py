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

    def test_local_backtests_rank_multiple_strategies_on_exact_contract(self):
        dates = pd.bdate_range("2026-01-02", periods=100)
        close = pd.Series([100 + index * 0.5 for index in range(100)])
        frame = pd.DataFrame({
            "date": dates, "open": close + 0.1, "high": close + 1, "low": close - 1,
            "close": close, "volume": [1000 + index for index in range(100)],
        })
        results = PURE.local_strategy_backtests(frame, "P")
        self.assertGreaterEqual(len(results), 4)
        self.assertGreaterEqual(results[0]["total_return"], results[-1]["total_return"])
        self.assertEqual(results[0]["execution"], "close confirmation, next-open execution")

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

    def test_ai_entry_accepts_per_variety_strategy_and_quantity(self):
        context = [{
            "variety": "P",
            "local_strategy_backtests": [{"strategy_id": "macd_momentum", "total_return": .2}],
        }]
        allowed = {"P": {"technical:P2701:2026-08-28"}}
        state = {"positions": {}}
        output = {"decisions": [{
            "variety": "P", "action": "ENTER_LONG", "confidence": .6,
            "open_reason": "回测与当前动量一致", "next_instruction": "复核MACD", "invalidation": "MACD转负",
            "evidence_ids": ["technical:P2701:2026-08-28"], "strategy_name": "MACD动量",
            "strategy_type": "LOCAL_BACKTEST", "strategy_source": "本地Python",
            "strategy_rationale": "候选中净收益最高", "strategy_entry_rule": "MACD柱为正",
            "strategy_exit_rule": "MACD柱转负", "backtest_strategy_id": "macd_momentum",
            "target_quantity": 23, "quantity_reason": "AI自主决定23手",
        }]}
        decisions, issues = PURE.validate_decisions(output, context, allowed, state)
        self.assertEqual(issues, [])
        self.assertEqual(decisions[0]["target_quantity"], 23)
        self.assertEqual(decisions[0]["backtest_summary"]["total_return"], .2)

    def test_drawdown_does_not_override_ai_entry_and_strategy_is_persisted(self):
        facts = [{
            "variety": "P", "name": "棕榈油", "sector": "油脂油料", "signal_date": "2026-08-28",
            "execution_contract": "P2701", "execution_reference_price": 10000, "atr14": 200,
        }]
        decisions = [{
            "variety": "P", "action": "ENTER_LONG", "confidence": 0.9,
            "open_reason": "趋势向上", "next_instruction": "继续核验", "invalidation": "跌破均线", "evidence_ids": [],
            "target_quantity": 17, "quantity_reason": "AI按收益目标决定17手",
            "strategy_name": "趋势跟随", "strategy_type": "AI_SYNTHESIS", "strategy_source": "AI自主",
            "strategy_rationale": "趋势最强", "strategy_entry_rule": "突破高点", "strategy_exit_rule": "跌破均线",
            "backtest_summary": None,
        }]
        state = {"equity": 910000, "high_water_equity": 1000000, "positions": {}}
        margin_book = {"rates": {"P2701": {
            "margin_rate": .09, "long_margin_rate": .08, "short_margin_rate": .09,
            "source": "交易所标准保证金", "source_updated_at": "2026-08-28",
            "source_url": "https://example.invalid", "official_direct": False,
        }}}
        snapshot, rows = PURE.build_signals(facts, decisions, state, margin_book)
        self.assertEqual(snapshot["signals"][0]["requested_quantity"], 17)
        self.assertEqual(snapshot["signals"][0]["strategy_name"], "趋势跟随")
        self.assertEqual(rows[0]["action"], "ENTER_LONG")
        self.assertEqual(rows[0]["risk_override"], "")

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

    def test_ledger_supports_unbounded_ai_quantity_and_strategy_audit(self):
        ledger, _model, _signal = PURE.BASE.load_components(ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary)
            PURE.init_ledger(ledger, state_dir)
            state = ledger.command_status(SimpleNamespace(state_dir=state_dir))
            self.assertEqual(state["model_version"], PURE.MODEL_VERSION)
            self.assertFalse(state["policy"]["enforce_caps"])
            self.assertIsNone(state["policy"]["max_gross_multiple"])
            signals = state_dir / "signals.json"
            signals.write_text(__import__("json").dumps({
                "as_of": "2026-08-28", "completed_bar": True, "model_version": PURE.MODEL_VERSION,
                "source": "test", "signals": [{
                    "variety": "AG", "name": "白银", "sector": "贵金属", "contract": "AG2610",
                    "action": "ENTER_LONG", "signal_date": "2026-08-28", "execution_date": "2026-08-31",
                    "reference_price": 17215, "atr14": 600, "multiplier": 15, "margin_rate": .2,
                    "fee_rate": .0004, "score": .7, "requested_quantity": 17,
                    "strategy_name": "MACD动量", "strategy_type": "LOCAL_BACKTEST", "strategy_source": "本地Python",
                    "strategy_rationale": "样本收益最高", "strategy_entry_rule": "MACD柱为正",
                    "strategy_exit_rule": "MACD柱转负", "backtest_summary": {"total_return": .12},
                    "quantity_reason": "AI决定17手",
                }],
            }, ensure_ascii=False), encoding="utf-8")
            planned = ledger.command_plan(SimpleNamespace(state_dir=state_dir, signals=signals))
            order = planned["decisions"][0]["order"]
            self.assertEqual(order["quantity"], 17)
            self.assertEqual(order["strategy_name"], "MACD动量")
            filled = ledger.command_fill(SimpleNamespace(
                state_dir=state_dir, order_id=order["order_id"], date="2026-08-31",
                price=17215.0, fee=None, allow_date_mismatch=False,
            ))
            self.assertEqual(filled["state"]["positions"]["AG"]["strategy_name"], "MACD动量")
            self.assertEqual(filled["fill"]["strategy_name"], "MACD动量")

    def test_decisions_are_requested_in_bounded_batches_and_merged(self):
        context = [{"variety": f"V{index}"} for index in range(18)]

        def request_json(**kwargs):
            self.assertEqual(kwargs["model"], PURE.DECISION_MODEL)
            batch = __import__("json").loads(kwargs["prompt"].split("INPUT:\n", 1)[1])
            return {
                "market_summary": f"覆盖{len(batch)}个品种",
                "decisions": [{"variety": row["variety"]} for row in batch],
            }, "test-backend"

        with (
            patch.dict(PURE.os.environ, {
                "PURE_AI_DECISION_BATCH_SIZE": "8",
                "PURE_AI_DECISION_BATCH_WORKERS": "3",
            }),
            patch.object(PURE.MODEL_BACKEND, "request_json", side_effect=request_json) as mocked,
        ):
            output, backend = PURE.request_decisions(context, {}, 30)

        self.assertEqual(mocked.call_count, 3)
        self.assertEqual(output["batch_count"], 3)
        self.assertEqual(output["batch_errors"], [])
        self.assertEqual(len(output["decisions"]), 18)
        self.assertEqual(backend, "test-backend")

    def test_public_snapshot_distinguishes_fixed_and_latest_decision_model(self):
        state = {
            "equity": 1_000_000.0, "cash": 1_000_000.0, "used_margin": 0.0,
            "gross_notional": 0.0, "realized_pnl": 0.0, "unrealized_pnl": 0.0,
            "total_fees": 0.0, "max_drawdown": 0.0, "high_water_equity": 1_000_000.0,
            "positions": {}, "pending_orders": [], "last_mark_date": "2026-09-01",
        }
        audit = {
            "decision_backend": "codex-chatgpt-cli",
            "decision_model_configured": PURE.DECISION_MODEL,
            "decision_model_used": PURE.DECISION_MODEL,
            "evaluated_count": 0,
        }
        now = PURE.datetime.fromisoformat("2026-09-01T10:00:00+08:00")
        with (
            patch.object(PURE.BASE, "equity_curve", return_value=[{"date": "2026-09-01", "equity": 1_000_000.0}]),
            patch.object(PURE.BASE, "performance", return_value=(None, None)),
            patch.object(PURE.BASE, "load_events", return_value=[]),
            patch.object(PURE.BASE, "read_json", return_value={}),
            patch.object(PURE.BASE, "next_refresh", return_value=None),
        ):
            payload = PURE.public_snapshot(Path("/unused"), state, [{
                "priority": "决策引擎", "name": "stale-engine", "state": "ready", "note": "stale",
            }], "test", [], audit, [], now)

        self.assertEqual(payload["model"]["decision_model"], "gpt-5.6-sol")
        self.assertEqual(payload["model"]["latest_decision_model"], "gpt-5.6-sol")
        self.assertTrue(payload["governance"]["decision_model_fixed"])
        self.assertEqual(payload["governance"]["decision_model"], "gpt-5.6-sol")
        self.assertIn("固定模型 gpt-5.6-sol", payload["sources"][-1]["note"])
        self.assertEqual(sum(row["priority"] == "决策引擎" for row in payload["sources"]), 1)

    def test_missing_batch_decision_is_a_validation_issue(self):
        decisions, issues = PURE.validate_decisions(
            {"decisions": []},
            [{"variety": "P", "local_strategy_backtests": []}],
            {"P": set()},
            {"positions": {}},
        )
        self.assertEqual(decisions, [])
        self.assertEqual(issues, [{"variety": "P", "reason": "AI批次未返回该品种决定"}])


if __name__ == "__main__":
    unittest.main()

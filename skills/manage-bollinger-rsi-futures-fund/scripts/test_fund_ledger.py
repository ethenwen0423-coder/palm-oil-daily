from __future__ import annotations

import argparse
import json
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fund_ledger as ledger


class FundLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temp.name)
        ledger.command_init(argparse.Namespace(
            state_dir=self.state_dir, initial_capital=1_000_000, if_missing=False
        ))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def signal_file(self, signals: list[dict]) -> Path:
        path = self.state_dir / "signals.json"
        path.write_text(json.dumps({
            "as_of": "2026-08-28", "completed_bar": True,
            "model_version": ledger.MODEL_VERSION, "source": "test actual contracts",
            "signals": signals,
        }), encoding="utf-8")
        return path

    @staticmethod
    def entry() -> dict:
        return {
            "variety": "P", "name": "棕榈油", "sector": "油脂油料", "contract": "P2701",
            "action": "ENTER_LONG", "signal_date": "2026-08-28", "execution_date": "2026-08-31",
            "reference_price": 10000, "atr14": 200, "multiplier": 10,
            "margin_rate": 0.12, "fee_rate": 0.0004, "score": 0.5,
        }

    def test_rejects_continuous_contract(self) -> None:
        signal = self.entry()
        signal["contract"] = "P0"
        result = ledger.command_plan(argparse.Namespace(
            state_dir=self.state_dir, signals=self.signal_file([signal])
        ))
        self.assertEqual(result["decisions"][0]["status"], "rejected")

    def test_plan_fill_mark_exit_round_trip(self) -> None:
        result = ledger.command_plan(argparse.Namespace(
            state_dir=self.state_dir, signals=self.signal_file([self.entry()])
        ))
        order_id = result["decisions"][0]["order"]["order_id"]
        filled = ledger.command_fill(argparse.Namespace(
            state_dir=self.state_dir, order_id=order_id, date="2026-08-31",
            price=10000.0, fee=None, allow_date_mismatch=False,
        ))
        self.assertIn("P", filled["state"]["positions"])

        prices = self.state_dir / "prices.json"
        prices.write_text(json.dumps({"as_of": "2026-08-31", "prices": [
            {"variety": "P", "contract": "P2701", "price": 10100, "source": "test"}
        ]}), encoding="utf-8")
        marked = ledger.command_mark(argparse.Namespace(state_dir=self.state_dir, prices=prices))
        self.assertGreater(marked["unrealized_pnl"], 0)

        exit_signal = self.entry()
        exit_signal.update({"action": "EXIT_LONG", "execution_date": "2026-09-01", "reference_price": 10100})
        planned = ledger.command_plan(argparse.Namespace(
            state_dir=self.state_dir, signals=self.signal_file([exit_signal])
        ))
        exit_id = planned["decisions"][0]["order"]["order_id"]
        closed = ledger.command_fill(argparse.Namespace(
            state_dir=self.state_dir, order_id=exit_id, date="2026-09-01",
            price=10100.0, fee=None, allow_date_mismatch=False,
        ))
        self.assertFalse(closed["state"]["positions"])
        self.assertGreater(closed["state"]["equity"], 1_000_000)

    def test_wrong_model_version_fails(self) -> None:
        path = self.signal_file([self.entry()])
        payload = json.loads(path.read_text())
        payload["model_version"] = "legacy"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ledger.LedgerError):
            ledger.command_plan(argparse.Namespace(state_dir=self.state_dir, signals=path))

    def test_pending_orders_reserve_sector_capacity(self) -> None:
        first = self.entry()
        second = dict(first)
        second.update({"variety": "Y", "name": "豆油", "contract": "Y2701", "score": 0.4})
        result = ledger.command_plan(argparse.Namespace(
            state_dir=self.state_dir, signals=self.signal_file([first, second])
        ))
        quantities = [d["order"]["quantity"] for d in result["decisions"] if d["status"] == "planned"]
        notionals = sum(qty * 10000 * 10 for qty in quantities)
        self.assertLessEqual(notionals, 400_000)

    def test_same_signal_is_not_planned_twice(self) -> None:
        path = self.signal_file([self.entry()])
        ledger.command_plan(argparse.Namespace(state_dir=self.state_dir, signals=path))
        repeated = ledger.command_plan(argparse.Namespace(state_dir=self.state_dir, signals=path))
        self.assertEqual(repeated["decisions"][0]["status"], "skipped")
        state = ledger.command_status(argparse.Namespace(state_dir=self.state_dir))
        self.assertEqual(len(state["pending_orders"]), 1)

    def test_actual_gap_fill_cannot_breach_variety_cap(self) -> None:
        result = ledger.command_plan(argparse.Namespace(
            state_dir=self.state_dir, signals=self.signal_file([self.entry()])
        ))
        order_id = result["decisions"][0]["order"]["order_id"]
        with self.assertRaises(ledger.LedgerError):
            ledger.command_fill(argparse.Namespace(
                state_dir=self.state_dir, order_id=order_id, date="2026-08-31",
                price=30000.0, fee=None, allow_date_mismatch=False,
            ))
        state = ledger.command_status(argparse.Namespace(state_dir=self.state_dir))
        self.assertFalse(state["positions"])
        self.assertEqual(state["pending_orders"][0]["status"], "pending")


if __name__ == "__main__":
    unittest.main()

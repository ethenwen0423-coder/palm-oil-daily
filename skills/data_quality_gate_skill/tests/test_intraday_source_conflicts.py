from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[3]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(ROOT / "scripts"))
update = load_module("update_oil_futures_data", ROOT / "scripts" / "update_oil_futures_data.py")
gate = load_module(
    "validate_data",
    ROOT / "skills" / "data_quality_gate_skill" / "scripts" / "validate_data.py",
)


class IntradaySourceConflictTests(unittest.TestCase):
    def test_small_relative_price_gap_is_consistent(self) -> None:
        note = update.verification_note(
            {"price": 9269, "change_pct": 0.62},
            {"status": "ok", "price": 9257, "change_pct": -0.06},
        )
        self.assertIn("价格一致", note)
        self.assertIn("涨跌幅口径不同", note)

    def test_large_relative_price_gap_is_inconsistent(self) -> None:
        note = update.verification_note(
            {"price": 9269, "change_pct": 0.62},
            {"status": "ok", "price": 9200, "change_pct": 0.60},
        )
        self.assertIn("价格不一致", note)

    def test_change_basis_difference_does_not_block_publish(self) -> None:
        errors: list[str] = []
        warnings: list[str] = []
        downgraded: list[str] = []
        gate.validate_contract(
            {
                "symbol": "P2609",
                "product": "P",
                "contract_rank": 1,
                "price": "9269",
                "preclose": "9212",
                "change": "+0.62%",
                "trade_date": "2026-07-14",
                "source": "AkShare + 同花顺问财行情skill",
                "verification": "价格一致：AkShare 9269 / 行情skill 9257；涨跌幅口径不同：AkShare +0.62% / 行情skill -0.06%",
            },
            datetime(2026, 7, 14, tzinfo=ZoneInfo("Asia/Shanghai")),
            errors,
            warnings,
            downgraded,
        )
        self.assertEqual([], errors)
        self.assertTrue(any("涨跌幅基准不同" in warning for warning in warnings))
        self.assertIn("P2609.change_basis", downgraded)

    def test_real_price_conflict_still_blocks_critical_contract(self) -> None:
        errors: list[str] = []
        warnings: list[str] = []
        downgraded: list[str] = []
        gate.validate_contract(
            {
                "symbol": "P2609",
                "product": "P",
                "contract_rank": 1,
                "price": "9269",
                "preclose": "9212",
                "change": "+0.62%",
                "trade_date": "2026-07-14",
                "source": "AkShare + 同花顺问财行情skill",
                "verification": "价格不一致：AkShare 9269 / 行情skill 9200",
            },
            datetime(2026, 7, 14, tzinfo=ZoneInfo("Asia/Shanghai")),
            errors,
            warnings,
            downgraded,
        )
        self.assertTrue(any("跨来源行情冲突" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

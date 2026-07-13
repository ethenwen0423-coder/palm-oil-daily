import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "daily_review.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("daily_review", SCRIPT)
daily_review = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(daily_review)


def contract(product: str, symbol: str, rank: int, change: str) -> dict:
    return {
        "symbol": symbol,
        "contract": symbol,
        "product": product,
        "contract_rank": rank,
        "price": "100",
        "open": "99",
        "high": "102",
        "low": "98",
        "change": change,
        "volume": "1000",
        "open_interest": "2000",
        "score": {"stance": "震荡偏强"},
        "strategy_recommendation": {"upper_watch": "105", "lower_watch": "95"},
    }


def write_payload(path: Path, contracts: list[dict]) -> None:
    path.write_text(
        "window.OIL_FUTURES_CONTRACTS = " + json.dumps({"contracts": contracts}) + ";\n",
        encoding="utf-8",
    )


class DailyReviewTest(unittest.TestCase):
    def test_reviews_rank_one_contract_for_each_tracked_product(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            previous = root / "previous.js"
            current = root / "current.js"
            output = root / "reviews"
            rank_one = [
                contract("P", "P2609", 1, "+1.0%"),
                contract("Y", "Y2609", 1, "-1.0%"),
                contract("OI", "OI2609", 1, "+0.2%"),
            ]
            write_payload(previous, rank_one + [contract("P", "P2701", 2, "+9.0%")])
            write_payload(current, rank_one + [contract("Y", "Y2701", 2, "+9.0%")])

            result = daily_review.run_review(previous, current, "2026-07-10", output)

            self.assertEqual(result["status"], "OK")
            rows = result["review_result"]
            self.assertEqual({row["contract"] for row in rows}, {"P2609", "Y2609", "OI2609"})
            self.assertEqual({row["product"] for row in rows}, {"P", "Y", "OI"})
            self.assertTrue(all(row["hit_status"] in {"HIT", "PARTIAL", "MISS"} for row in rows))
            saved = json.loads((output / "2026-07-10.json").read_text(encoding="utf-8"))
            self.assertEqual(len(saved["review_result"]), 3)

    def test_empty_review_is_marked_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            previous = root / "previous.js"
            current = root / "current.js"
            output = root / "reviews"
            write_payload(previous, [])
            write_payload(current, [])

            result = daily_review.run_review(previous, current, "2026-07-10", output)

            self.assertEqual(result["status"], "REVIEW_FAILED")
            self.assertEqual(result["review_result"], [])
            self.assertEqual(result["missing_products"], ["OI", "P", "Y"])


if __name__ == "__main__":
    unittest.main()

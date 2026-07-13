import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "evaluate_forecast.py"
SPEC = importlib.util.spec_from_file_location("evaluate_forecast", SCRIPT)
evaluate_forecast = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(evaluate_forecast)


def forecast_record(product: str, contract: str, stance: str, probabilities: dict, lower: float, upper: float, invalidation_price: float | None) -> dict:
    return {
        "forecast_id": f"2026-07-13-{contract}-oil-forecast-v1",
        "report_date": "2026-07-13",
        "product": product,
        "contract": contract,
        "contract_rank": 1,
        "generated_at": "2026-07-13T08:20:00+08:00",
        "cutoff_at": "2026-07-13T08:15:00+08:00",
        "horizon": "same_trade_day_close",
        "stance": stance,
        "probabilities": probabilities,
        "expected_range": {"lower": lower, "upper": upper},
        "invalidation": {"text": "失效条件", "price": invalidation_price},
        "source_score": {"total": 60.0, "technical": 51.0, "fundamental": 50.0, "driver": 67.4, "money_flow": 56.6},
        "confidence": "medium",
        "source_confidence": "中",
        "probability_mapping_version": "score-map-v1",
        "outcome_rule_version": "outcome-v1-fixed-0.30pct",
        "calibration_status": "uncalibrated_baseline",
        "evaluation_status": "pending",
    }


def forecast_payload() -> dict:
    return {
        "schema_version": "forecast-schema-v1",
        "report_date": "2026-07-13",
        "timezone": "Asia/Shanghai",
        "records": [
            forecast_record("P", "P2609", "震荡偏强", {"up": 0.6, "range": 0.3, "down": 0.1}, 95, 105, 96),
            forecast_record("Y", "Y2609", "震荡偏弱", {"up": 0.1, "range": 0.3, "down": 0.6}, 95, 105, 104),
            forecast_record("OI", "OI2609", "震荡", {"up": 0.2, "range": 0.6, "down": 0.2}, 99.5, 100.5, 100),
        ],
    }


def actual_contract(product: str, contract: str, previous: float, close: float, high: float, low: float, rank: int = 1) -> dict:
    return {
        "product": product,
        "contract": contract,
        "contract_rank": rank,
        "trade_date": "2026-07-13",
        "preclose": str(previous),
        "price": str(close),
        "high": str(high),
        "low": str(low),
    }


def actual_payload() -> dict:
    return {
        "contracts": [
            actual_contract("P", "P2609", 100, 101, 106, 95, rank=2),
            actual_contract("P", "P2701", 100, 90, 101, 89, rank=1),
            actual_contract("Y", "Y2609", 100, 99, 105, 97),
            actual_contract("OI", "OI2609", 100, 100.3, 100.4, 99.9),
        ]
    }


def write_forecast(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_actual(path: Path, payload: dict) -> None:
    path.write_text("window.OIL_FUTURES_CONTRACTS = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")


class EvaluateForecastTest(unittest.TestCase):
    evaluated_at = "2026-07-13T21:30:00+08:00"

    def run_evaluation(self, root: Path, forecast: dict | None = None, actual: dict | None = None, output_name: str = "evaluated.json") -> tuple[dict, Path, Path]:
        forecast_path = root / "forecast.json"
        actual_path = root / "actual.js"
        output_path = root / output_name
        write_forecast(forecast_path, forecast or forecast_payload())
        write_actual(actual_path, actual or actual_payload())
        result = evaluate_forecast.evaluate_forecast(forecast_path, actual_path, output_path, self.evaluated_at)
        return result, forecast_path, output_path

    def test_p_y_oi_evaluate_by_product_and_exact_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, _, output_path = self.run_evaluation(Path(temporary))
            output = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(result["records"], 3)
        self.assertEqual(output["evaluation_status"], "evaluated")
        records = {record["product"]: record for record in output["records"]}
        self.assertEqual(records["P"]["evaluation"]["actual"]["close"], 101.0)
        self.assertEqual(records["P"]["evaluation"]["actual_class"], "up")
        self.assertEqual(records["Y"]["evaluation"]["actual_class"], "down")
        self.assertEqual(records["OI"]["evaluation"]["actual_class"], "range")

    def test_missing_same_contract_at_roll_fails(self) -> None:
        actual = actual_payload()
        actual["contracts"] = [item for item in actual["contracts"] if item["contract"] != "P2609"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "缺少同一合约"):
                self.run_evaluation(root, actual=actual)
            self.assertFalse((root / "evaluated.json").exists())

    def test_outcome_classes_and_boundary_values(self) -> None:
        self.assertEqual(evaluate_forecast.actual_class(0.31), "up")
        self.assertEqual(evaluate_forecast.actual_class(-0.31), "down")
        self.assertEqual(evaluate_forecast.actual_class(0.30), "range")
        self.assertEqual(evaluate_forecast.actual_class(-0.30), "range")

    def test_predicted_class_ties_prefer_range_then_up(self) -> None:
        self.assertEqual(evaluate_forecast.predicted_class({"up": 0.5, "range": 0.5, "down": 0}), "range")
        self.assertEqual(evaluate_forecast.predicted_class({"up": 0.5, "range": 0, "down": 0.5}), "up")

    def test_direction_ranges_brier_and_invalidation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, _, output_path = self.run_evaluation(Path(temporary))
            records = {record["product"]: record for record in json.loads(output_path.read_text(encoding="utf-8"))["records"]}
        p_evaluation = records["P"]["evaluation"]
        self.assertTrue(p_evaluation["direction_hit"])
        self.assertTrue(p_evaluation["close_in_expected_range"])
        self.assertFalse(p_evaluation["full_session_in_expected_range"])
        self.assertEqual(p_evaluation["brier_score"], 0.086667)
        self.assertTrue(p_evaluation["invalidation_triggered"])
        self.assertTrue(records["Y"]["evaluation"]["invalidation_triggered"])
        self.assertIsNone(records["OI"]["evaluation"]["invalidation_triggered"])
        self.assertEqual(records["OI"]["evaluation"]["invalidation_evaluation_status"], "direction_ambiguous")
        self.assertEqual(evaluate_forecast.evaluate_invalidation("偏多", 96, 97, 105), (False, "evaluated"))

    def test_input_bytes_unchanged_and_output_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, forecast_path, output_path = self.run_evaluation(root)
            original_bytes = forecast_path.read_bytes()
            second = evaluate_forecast.evaluate_forecast(forecast_path, root / "actual.js", output_path, self.evaluated_at)
            self.assertEqual(forecast_path.read_bytes(), original_bytes)
        self.assertFalse(first["already_exists"])
        self.assertTrue(second["already_exists"])

    def test_invalid_actual_fails_without_half_output(self) -> None:
        actual = actual_payload()
        actual["contracts"][0]["price"] = "not-a-number"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "actual.close"):
                self.run_evaluation(root, actual=actual)
            self.assertFalse((root / "evaluated.json").exists())

    def test_different_output_and_evaluated_input_cannot_be_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, forecast_path, output_path = self.run_evaluation(root)
            with self.assertRaisesRegex(ValueError, "内容不同"):
                evaluate_forecast.evaluate_forecast(forecast_path, root / "actual.js", output_path, "2026-07-13T21:31:00+08:00")

            write_forecast(forecast_path, json.loads(output_path.read_text(encoding="utf-8")))
            with self.assertRaisesRegex(ValueError, "全部为 pending"):
                evaluate_forecast.evaluate_forecast(forecast_path, root / "actual.js", root / "new-output.json", self.evaluated_at)

    def test_cli_and_output_schema_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            forecast_path = root / "forecast.json"
            actual_path = root / "actual.js"
            output_path = root / "evaluated.json"
            write_forecast(forecast_path, forecast_payload())
            write_actual(actual_path, actual_payload())
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--forecast", str(forecast_path), "--actual", str(actual_path), "--output", str(output_path), "--evaluated-at", self.evaluated_at],
                check=False,
                capture_output=True,
                text=True,
            )
            validation = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_forecast.py"), "--forecast", str(output_path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "ok")
        self.assertEqual(validation.returncode, 0, validation.stdout)


if __name__ == "__main__":
    unittest.main()

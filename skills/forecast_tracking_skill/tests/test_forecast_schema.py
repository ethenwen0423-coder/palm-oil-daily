import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "forecast_schema.py"
SPEC = importlib.util.spec_from_file_location("forecast_schema", SCRIPT)
forecast_schema = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(forecast_schema)


def valid_payload() -> dict:
    report_date = "2026-07-13"

    def record(product: str, contract: str) -> dict:
        return {
            "forecast_id": f"{report_date}-{contract}-oil-forecast-v1",
            "report_date": report_date,
            "product": product,
            "contract": contract,
            "contract_rank": 1,
            "generated_at": "2026-07-13T08:20:00+08:00",
            "cutoff_at": "2026-07-13T08:15:00+08:00",
            "horizon": "same_trade_day_close",
            "stance": "震荡偏强",
            "probabilities": {"up": 0.45, "range": 0.40, "down": 0.15},
            "expected_range": {"lower": 9250, "upper": 9420},
            "invalidation": {"text": "失效条件原文", "price": None},
            "source_score": {"total": 56.8, "technical": 51.0, "fundamental": 50.0, "driver": 67.4, "money_flow": 56.6},
            "confidence": "medium",
            "source_confidence": "中",
            "probability_mapping_version": "score-map-v1",
            "outcome_rule_version": "outcome-v1-fixed-0.30pct",
            "calibration_status": "uncalibrated_baseline",
            "evaluation_status": "pending",
        }

    return {
        "schema_version": "forecast-schema-v1",
        "report_date": report_date,
        "timezone": "Asia/Shanghai",
        "records": [record("P", "P2609"), record("Y", "Y2609"), record("OI", "OI2609")],
    }


class ForecastSchemaTest(unittest.TestCase):
    def assert_invalid(self, payload: dict, expected: str) -> None:
        result = forecast_schema.validate_forecast(payload)
        self.assertEqual(result["status"], "error")
        self.assertFalse(result["can_evaluate"])
        self.assertTrue(any(expected in error for error in result["errors"]), result["errors"])

    def test_complete_valid_p_y_oi_sample_passes(self) -> None:
        result = forecast_schema.validate_forecast(valid_payload())
        self.assertEqual(result, {"status": "ok", "can_evaluate": True, "errors": [], "warnings": []})

    def test_missing_main_contract_fails(self) -> None:
        payload = valid_payload()
        payload["records"].pop()
        self.assert_invalid(payload, "P、Y、OI")

    def test_rank_two_fails(self) -> None:
        payload = valid_payload()
        payload["records"][0]["contract_rank"] = 2
        self.assert_invalid(payload, "contract_rank 必须为 1")

    def test_probabilities_not_equal_to_one_fail(self) -> None:
        payload = valid_payload()
        payload["records"][0]["probabilities"]["down"] = 0.14
        self.assert_invalid(payload, "probabilities 合计必须为 1")

    def test_reversed_expected_range_fails(self) -> None:
        payload = valid_payload()
        payload["records"][0]["expected_range"] = {"lower": 9420, "upper": 9250}
        self.assert_invalid(payload, "expected_range.lower 必须小于 upper")

    def test_duplicate_forecast_id_fails(self) -> None:
        payload = valid_payload()
        payload["records"][1]["forecast_id"] = payload["records"][0]["forecast_id"]
        self.assert_invalid(payload, "forecast_id 在单日文件内不可重复")

    def test_invalid_date_timezone_and_status_fail(self) -> None:
        payload = valid_payload()
        payload["report_date"] = "2026-02-30"
        payload["records"][0]["report_date"] = "2026-02-30"
        payload["timezone"] = "UTC"
        payload["records"][0]["evaluation_status"] = "unknown"
        self.assert_invalid(payload, "report_date 必须为有效")
        self.assert_invalid(payload, "timezone 必须为 Asia/Shanghai")
        self.assert_invalid(payload, "evaluation_status 未知")

    def test_non_pending_initial_status_fails(self) -> None:
        payload = copy.deepcopy(valid_payload())
        payload["records"][0]["evaluation_status"] = "evaluated"
        result = forecast_schema.validate_forecast(payload, require_pending=True)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("初始 evaluation_status 只能为 pending" in error for error in result["errors"]))

    def test_evaluated_record_requires_complete_evaluation(self) -> None:
        payload = valid_payload()
        record = payload["records"][0]
        record["evaluation_status"] = "evaluated"
        record["evaluation"] = {
            "outcome_rule_version": "outcome-v1-fixed-0.30pct",
            "evaluated_at": "2026-07-13T21:30:00+08:00",
            "actual": {"trade_date": "2026-07-13", "previous_close": 100, "close": 101, "high": 102, "low": 99, "return_pct": 1},
            "threshold_pct": 0.30,
            "threshold_source": "fixed_baseline",
            "actual_class": "up",
            "predicted_class": "up",
            "direction_hit": True,
            "close_in_expected_range": True,
            "full_session_in_expected_range": False,
            "invalidation_triggered": False,
            "invalidation_evaluation_status": "evaluated",
            "brier_score": 0.1,
        }
        self.assertEqual(forecast_schema.validate_forecast(payload)["status"], "ok")
        record["evaluation"]["outcome_rule_version"] = "outcome-v2"
        self.assert_invalid(payload, "evaluation.outcome_rule_version 必须与 outcome_rule_version 一致")
        record["evaluation"]["outcome_rule_version"] = "outcome-v1-fixed-0.30pct"
        del record["evaluation"]["brier_score"]
        self.assert_invalid(payload, "evaluation 缺少 brier_score")
        record["evaluation"]["brier_score"] = 0.1
        record["evaluation_status"] = "pending"
        self.assert_invalid(payload, "pending 记录不得包含完整 evaluation 结果")

    def test_confidence_and_legacy_outcome_version_are_rejected(self) -> None:
        payload = valid_payload()
        del payload["records"][0]["confidence"]
        self.assert_invalid(payload, "confidence 只能为 high/medium/low/unknown")

        payload = valid_payload()
        payload["records"][0]["source_confidence"] = None
        payload["records"][0]["confidence"] = "unknown"
        self.assertEqual(forecast_schema.validate_forecast(payload)["status"], "ok")

        payload["records"][0]["outcome_rule_version"] = "outcome-v1"
        self.assert_invalid(payload, "legacy outcome rule version requires explicit migration")

    def test_cli_returns_json_and_nonzero_for_invalid_file(self) -> None:
        validator = SCRIPT.parent / "validate_forecast.py"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "forecast.json"
            path.write_text(json.dumps(valid_payload()), encoding="utf-8")
            valid = subprocess.run(
                [sys.executable, str(validator), "--forecast", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(valid.returncode, 0)
            self.assertEqual(json.loads(valid.stdout), {"status": "ok", "can_evaluate": True, "errors": [], "warnings": []})

            invalid_payload = valid_payload()
            invalid_payload["records"][0]["contract_rank"] = 2
            path.write_text(json.dumps(invalid_payload), encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(validator), "--forecast", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertEqual(json.loads(invalid.stdout)["status"], "error")


if __name__ == "__main__":
    unittest.main()

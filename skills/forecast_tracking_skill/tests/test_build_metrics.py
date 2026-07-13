import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "build_metrics.py"
SPEC = importlib.util.spec_from_file_location("build_metrics", SCRIPT)
build_metrics = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_metrics)


def record(product: str, report_date: str, probability_version: str = "score-map-v1", outcome_version: str = "outcome-v1-fixed-0.30pct", confidence: str = "high", direction_hit: bool = True, close_hit: bool = True, full_hit: bool = False, invalidation: bool | None = False, brier: float = 0.1) -> dict:
    contract = {"P": "P2609", "Y": "Y2609", "OI": "OI2609"}[product]
    value = {
        "forecast_id": f"{report_date}-{contract}-oil-forecast-v1",
        "report_date": report_date,
        "product": product,
        "contract": contract,
        "contract_rank": 1,
        "generated_at": f"{report_date}T08:20:00+08:00",
        "cutoff_at": f"{report_date}T08:15:00+08:00",
        "horizon": "same_trade_day_close",
        "stance": "震荡偏强",
        "probabilities": {"up": 0.6, "range": 0.3, "down": 0.1},
        "expected_range": {"lower": 90, "upper": 110},
        "invalidation": {"text": "失效条件", "price": 95},
        "source_score": {"total": 60, "technical": 50, "fundamental": 50, "driver": 60, "money_flow": 50},
        "confidence": confidence,
        "source_confidence": {"high": "高", "medium": "中", "low": "低"}.get(confidence),
        "probability_mapping_version": probability_version,
        "outcome_rule_version": outcome_version,
        "calibration_status": "uncalibrated_baseline",
        "evaluation_status": "evaluated",
        "evaluation": {
            "outcome_rule_version": outcome_version,
            "evaluated_at": f"{report_date}T21:30:00+08:00",
            "actual": {"trade_date": report_date, "previous_close": 100, "close": 101, "high": 106, "low": 94, "return_pct": 1},
            "threshold_pct": 0.30,
            "threshold_source": "fixed_baseline",
            "actual_class": "up",
            "predicted_class": "up",
            "direction_hit": direction_hit,
            "close_in_expected_range": close_hit,
            "full_session_in_expected_range": full_hit,
            "invalidation_triggered": invalidation,
            "invalidation_evaluation_status": "evaluated" if invalidation is not None else "not_evaluable",
            "brier_score": brier,
        },
    }
    return value


def evaluated_day(report_date: str, **kwargs) -> dict:
    return {
        "schema_version": "forecast-schema-v1",
        "report_date": report_date,
        "timezone": "Asia/Shanghai",
        "evaluation_status": "evaluated",
        "records": [record("P", report_date, confidence="high", **kwargs), record("Y", report_date, confidence="medium", **kwargs), record("OI", report_date, confidence="low", **kwargs)],
    }


def pending_day(report_date: str, probability_version: str = "score-map-v1", outcome_version: str = "outcome-v1-fixed-0.30pct") -> dict:
    value = evaluated_day(report_date, probability_version=probability_version, outcome_version=outcome_version)
    value.pop("evaluation_status")
    for item in value["records"]:
        item["evaluation_status"] = "pending"
        item.pop("evaluation")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def business_dates(start: date, count: int) -> list[str]:
    output: list[str] = []
    current = start
    while len(output) < count:
        if current.weekday() < 5:
            output.append(current.isoformat())
        current += timedelta(days=1)
    return output


class BuildMetricsTest(unittest.TestCase):
    def build(self, root: Path, as_of: str) -> dict:
        return build_metrics.build_metrics(root / "evaluated", root / "daily", root / "metrics", as_of)

    def test_metrics_cover_overall_products_confidence_and_grades(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = evaluated_day("2026-01-05")
            payload["records"][1]["evaluation"].update({"direction_hit": False, "close_in_expected_range": True, "full_session_in_expected_range": True, "invalidation_triggered": None, "brier_score": 0.2})
            payload["records"][2]["evaluation"].update({"direction_hit": False, "close_in_expected_range": False, "full_session_in_expected_range": False, "invalidation_triggered": True, "brier_score": 0.3})
            write_json(root / "evaluated" / "2026-01-05.json", payload)
            outputs = self.build(root, "2026-01-05")
        metric = outputs["latest.json"]["versions"]["score-map-v1|outcome-v1-fixed-0.30pct"]
        self.assertEqual(metric["overall"]["sample_count"], 3)
        self.assertEqual(metric["overall"]["directional_accuracy"]["rate"], 0.333333)
        self.assertEqual(metric["overall"]["close_range_coverage"]["rate"], 0.666667)
        self.assertEqual(metric["overall"]["full_session_range_coverage"]["rate"], 0.333333)
        self.assertEqual(metric["overall"]["invalidation_rate"]["rate"], 0.5)
        self.assertEqual(metric["overall"]["mean_brier_score"], 0.2)
        self.assertEqual(metric["overall"]["combined_grade"], {"HIT": 1, "PARTIAL": 1, "MISS": 1})
        self.assertEqual(metric["by_product"]["P"]["sample_count"], 1)
        self.assertEqual(metric["by_confidence"]["high"]["sample_count"], 1)
        self.assertEqual(metric["by_confidence"]["medium"]["sample_count"], 1)
        self.assertEqual(metric["by_confidence"]["low"]["sample_count"], 1)
        self.assertEqual(metric["by_confidence"]["unknown"]["sample_count"], 0)

    def test_unknown_confidence_is_a_separate_metrics_bucket(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = evaluated_day("2026-01-06")
            payload["records"][0]["confidence"] = "unknown"
            payload["records"][0]["source_confidence"] = None
            write_json(root / "evaluated" / "2026-01-06.json", payload)
            outputs = self.build(root, "2026-01-06")
        metric = outputs["latest.json"]["versions"]["score-map-v1|outcome-v1-fixed-0.30pct"]
        self.assertEqual(metric["by_confidence"]["unknown"]["sample_count"], 1)
        self.assertEqual(metric["by_confidence"]["high"]["sample_count"], 0)

    def test_20d_60d_use_trade_days_not_calendar_days_and_are_version_isolated(self) -> None:
        dates = business_dates(date(2026, 1, 1), 60)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for value in dates:
                write_json(root / "evaluated" / f"{value}.json", evaluated_day(value))
            alternate = evaluated_day("2026-12-31", probability_version="score-map-v2")
            write_json(root / "evaluated" / "2026-12-31.json", alternate)
            outputs = self.build(root, "2026-12-31")
        metrics20 = outputs["20d.json"]["versions"]["score-map-v1|outcome-v1-fixed-0.30pct"]
        metrics60 = outputs["60d.json"]["versions"]["score-map-v1|outcome-v1-fixed-0.30pct"]
        alternate20 = outputs["20d.json"]["versions"]["score-map-v2|outcome-v1-fixed-0.30pct"]
        self.assertEqual(metrics20["valid_trade_day_count"], 20)
        self.assertEqual(metrics60["valid_trade_day_count"], 60)
        self.assertEqual(metrics20["start_date"], dates[-20])
        self.assertEqual(metrics60["start_date"], dates[0])
        self.assertEqual(metrics20["status"], "ok")
        self.assertEqual(metrics60["status"], "ok")
        self.assertEqual(alternate20["valid_trade_day_count"], 1)
        self.assertEqual(alternate20["status"], "insufficient_sample")

    def test_invalid_day_is_excluded_and_pending_gap_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid = evaluated_day("2026-02-02")
            invalid["records"].pop()
            write_json(root / "evaluated" / "2026-02-02.json", invalid)
            write_json(root / "daily" / "2026-02-02.json", pending_day("2026-02-02"))
            write_json(root / "daily" / "2026-02-03.json", pending_day("2026-02-03"))
            outputs = self.build(root, "2026-02-03")
        metric = outputs["20d.json"]["versions"]["score-map-v1|outcome-v1-fixed-0.30pct"]
        self.assertEqual(metric["valid_trade_day_count"], 0)
        self.assertEqual(metric["evaluation_gap_count"], 6)
        self.assertEqual(metric["status"], "insufficient_sample")
        self.assertFalse(metric["public_display_allowed"])

    def test_input_unchanged_and_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_json(root / "evaluated" / "2026-03-02.json", evaluated_day("2026-03-02"))
            write_json(root / "daily" / "2026-03-03.json", pending_day("2026-03-03"))
            original = (root / "evaluated" / "2026-03-02.json").read_bytes()
            self.build(root, "2026-03-03")
            first = {name: (root / "metrics" / name).read_bytes() for name in ("latest.json", "20d.json", "60d.json")}
            self.build(root, "2026-03-03")
            second = {name: (root / "metrics" / name).read_bytes() for name in first}
            self.assertEqual((root / "evaluated" / "2026-03-02.json").read_bytes(), original)
        self.assertEqual(first, second)

    def test_cli_writes_all_fixed_output_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_json(root / "evaluated" / "2026-03-02.json", evaluated_day("2026-03-02"))
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--evaluated-dir",
                    str(root / "evaluated"),
                    "--forecast-dir",
                    str(root / "daily"),
                    "--output-dir",
                    str(root / "metrics"),
                    "--as-of",
                    "2026-03-02",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            created = {path.name for path in (root / "metrics").glob("*.json")}
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "ok")
        self.assertEqual(created, {"latest.json", "20d.json", "60d.json"})


if __name__ == "__main__":
    unittest.main()

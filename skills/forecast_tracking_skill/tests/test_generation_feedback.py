import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BUILD_PATH = ROOT / "skills" / "forecast_tracking_skill" / "scripts" / "build_generation_feedback.py"
VALIDATE_PATH = ROOT / "skills" / "forecast_tracking_skill" / "scripts" / "validate_report_feedback.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = load_module("build_generation_feedback", BUILD_PATH)
validator = load_module("validate_report_feedback", VALIDATE_PATH)


def group(samples: int, accuracy: float, coverage: float = 0.7, misses: int = 1) -> dict:
    return {
        "sample_count": samples,
        "directional_accuracy": {"rate": accuracy},
        "close_range_coverage": {"rate": coverage},
        "combined_grade": {"HIT": max(0, samples - misses), "PARTIAL": 0, "MISS": misses},
    }


def metrics(days: int, p_accuracy: float = 0.7, high_accuracy: float = 0.7) -> dict:
    key = "score-map-v1|outcome-v1-fixed-0.30pct"
    return {
        "schema_version": "forecast-metrics-v1",
        "as_of": "2026-07-14",
        "latest_version_combination": {"key": key},
        "versions": {
            key: {
                "valid_trade_day_count": days,
                "by_product": {
                    "P": group(days, p_accuracy),
                    "Y": group(days, 0.6),
                    "OI": group(days, 0.6),
                },
                "by_confidence": {"high": group(days, high_accuracy)},
            }
        },
    }


class GenerationFeedbackTest(unittest.TestCase):
    def environment(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "reviews").mkdir()
        return root

    def write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def test_no_history_is_explicit_and_never_claims_learning(self) -> None:
        root = self.environment()
        feedback = builder.build_feedback(root / "missing.json", root / "reviews", "2026-07-15")
        self.assertEqual(feedback["status"], "no_history")
        self.assertIn("暂无已评估历史样本", feedback["required_report_disclosures"][0])
        self.assertEqual(feedback["core_view_confidence_cap"], "uncapped")

    def test_insufficient_sample_is_observation_only(self) -> None:
        root = self.environment()
        self.write_json(root / "metrics.json", metrics(4, p_accuracy=0.0))
        feedback = builder.build_feedback(root / "metrics.json", root / "reviews", "2026-07-15")
        self.assertEqual(feedback["status"], "observe_only")
        self.assertEqual(feedback["products"]["P"]["action"], "observe_only")
        self.assertIn("样本不足", feedback["required_report_disclosures"][0])

    def test_low_p_accuracy_downgrades_main_view_and_caps_confidence(self) -> None:
        root = self.environment()
        self.write_json(root / "metrics.json", metrics(10, p_accuracy=0.4))
        feedback = builder.build_feedback(root / "metrics.json", root / "reviews", "2026-07-15")
        self.assertEqual(feedback["status"], "active")
        self.assertEqual(feedback["products"]["P"]["action"], "downgrade_directional_claim")
        self.assertEqual(feedback["core_view_confidence_cap_stars"], 2)
        self.assertIn("今日主线降级", feedback["required_report_disclosures"][0])

    def test_repeated_review_error_becomes_required_constraint(self) -> None:
        root = self.environment()
        self.write_json(root / "metrics.json", metrics(10))
        for day in ("2026-07-13", "2026-07-14"):
            self.write_json(root / "reviews" / f"{day}.json", {"error_type": ["原油影响低估"]})
        feedback = builder.build_feedback(root / "metrics.json", root / "reviews", "2026-07-15")
        self.assertEqual(feedback["consecutive_error_streaks"]["原油影响低估"], 2)
        self.assertTrue(any("不得让该因素单独主导" in item for item in feedback["required_report_disclosures"]))

    def test_quality_gate_requires_disclosure_and_enforces_star_cap(self) -> None:
        root = self.environment()
        self.write_json(root / "metrics.json", metrics(10, p_accuracy=0.4))
        feedback = builder.build_feedback(root / "metrics.json", root / "reviews", "2026-07-15")
        feedback_path = root / "feedback.json"
        self.write_json(feedback_path, feedback)
        disclosure = feedback["required_report_disclosures"][0]
        report = root / "report.md"
        report.write_text(f"# 07月15日晨报\n\n## 【今日观点】\n\n震荡。置信度：★★☆☆☆。\n\n## 【信息来源与核验说明】\n\n{disclosure}\n", encoding="utf-8")
        accepted = validator.validate_report(report, feedback_path, "2026-07-15")
        self.assertTrue(accepted["can_publish"], accepted)
        report.write_text(report.read_text(encoding="utf-8").replace("★★☆☆☆", "★★★★☆"), encoding="utf-8")
        rejected = validator.validate_report(report, feedback_path, "2026-07-15")
        self.assertFalse(rejected["can_publish"])
        self.assertTrue(any("超过复盘上限" in error for error in rejected["errors"]))


if __name__ == "__main__":
    unittest.main()

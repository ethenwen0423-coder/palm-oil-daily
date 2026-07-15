import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "review_prediction.py"
SPEC = importlib.util.spec_from_file_location("review_prediction", SCRIPT)
review_prediction = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(review_prediction)


def completed(returncode: int = 0, payload: dict | None = None, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout=json.dumps(payload or {}, ensure_ascii=False), stderr=stderr)


def actual_payload(trade_date: str = "2026-07-14") -> dict:
    return {
        "contracts": [
            {
                "product": product,
                "contract": f"{product}2609",
                "contract_rank": 1,
                "trade_date": trade_date,
                "price": "101",
                "preclose": "100",
                "high": "102",
                "low": "99",
            }
            for product in ("P", "Y", "OI")
        ]
    }


def write_actual(path: Path, trade_date: str = "2026-07-14") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "window.OIL_FUTURES_CONTRACTS = " + json.dumps(actual_payload(trade_date), ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )


class ReviewPipelineTest(unittest.TestCase):
    date = "2026-07-14"

    def environment(self, create_forecast: bool = True):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        paths = {
            "root": root,
            "official": root / "data" / "oil_futures.js",
            "snapshots": root / "data" / "review" / "snapshots",
            "daily_review": root / "data" / "review" / "daily",
            "forecast": root / "data" / "forecast" / "daily",
            "evaluated": root / "data" / "forecast" / "evaluated",
            "metrics": root / "data" / "forecast" / "metrics",
            "feedback_dir": root / "data" / "forecast" / "feedback",
            "feedback": root / "data" / "forecast" / "feedback" / "latest.json",
            "latest": root / "data" / "review" / "latest_review.json",
            "update_script": root / "update.py",
            "review_script": root / "daily_review.py",
            "evaluate_script": root / "evaluate.py",
            "metrics_script": root / "metrics.py",
            "feedback_script": root / "feedback.py",
            "prune_script": root / "prune.py",
        }
        paths["official"].parent.mkdir(parents=True)
        paths["official"].write_text("morning-tab", encoding="utf-8")
        paths["forecast"].mkdir(parents=True)
        if create_forecast:
            (paths["forecast"] / f"{self.date}.json").write_text("{}", encoding="utf-8")
        for key in ("update_script", "review_script", "evaluate_script", "metrics_script", "feedback_script", "prune_script"):
            paths[key].write_text("# fixture", encoding="utf-8")
        stack = ExitStack()
        self.addCleanup(stack.close)
        for name, value in (
            ("ROOT", root),
            ("OFFICIAL_TAB", paths["official"]),
            ("SNAPSHOT_DIR", paths["snapshots"]),
            ("DAILY_REVIEW_DIR", paths["daily_review"]),
            ("FORECAST_DIR", paths["forecast"]),
            ("EVALUATED_DIR", paths["evaluated"]),
            ("METRICS_DIR", paths["metrics"]),
            ("FEEDBACK_DIR", paths["feedback_dir"]),
            ("FEEDBACK_PATH", paths["feedback"]),
            ("LATEST_REVIEW", paths["latest"]),
            ("UPDATE_SCRIPT", paths["update_script"]),
            ("REVIEW_SCRIPT", paths["review_script"]),
            ("EVALUATE_SCRIPT", paths["evaluate_script"]),
            ("METRICS_SCRIPT", paths["metrics_script"]),
            ("FEEDBACK_SCRIPT", paths["feedback_script"]),
            ("PRUNE_SCRIPT", paths["prune_script"]),
        ):
            stack.enter_context(mock.patch.object(review_prediction, name, value))
        return paths

    def successful_runner(
        self, paths: dict, events: list[str], metrics_failure: bool = False, cleanup_failure: bool = False
    ):
        def run(command: list[str]) -> subprocess.CompletedProcess[str]:
            script = Path(command[1])
            if script == paths["update_script"]:
                events.append("actual")
                self.assertIn("actual-snapshot", command)
                self.assertNotIn("--report-date", command)
                output = Path(command[command.index("--output") + 1])
                write_actual(output, self.date)
                return completed(0, {"status": "ok"})
            if script == paths["review_script"]:
                events.append("daily_review")
                output_dir = Path(command[command.index("--output-dir") + 1])
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / f"{self.date}.json").write_text('{"status":"OK"}\n', encoding="utf-8")
                return completed(0, {"status": "OK"})
            if script == paths["evaluate_script"]:
                events.append("evaluate")
                output = Path(command[command.index("--output") + 1])
                output.parent.mkdir(parents=True, exist_ok=True)
                if not output.exists():
                    evaluated_at = command[command.index("--evaluated-at") + 1]
                    output.write_text(
                        json.dumps({"records": [{"evaluation": {"evaluated_at": evaluated_at}}]}),
                        encoding="utf-8",
                    )
                return completed(0, {"status": "ok", "already_exists": output.exists()})
            if script == paths["metrics_script"]:
                events.append("metrics")
                if metrics_failure:
                    return completed(7, {"status": "error", "errors": ["metrics failed"]})
                output_dir = Path(command[command.index("--output-dir") + 1])
                output_dir.mkdir(parents=True, exist_ok=True)
                for name in ("latest.json", "20d.json", "60d.json"):
                    (output_dir / name).write_text("{}\n", encoding="utf-8")
                return completed(0, {"status": "ok"})
            if script == paths["feedback_script"]:
                events.append("feedback")
                output = Path(command[command.index("--output") + 1])
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text('{"schema_version":"forecast-generation-feedback-v1"}\n', encoding="utf-8")
                return completed(0, {"status": "ok", "feedback_status": "observe_only"})
            if script == paths["prune_script"]:
                events.append("cleanup")
                if cleanup_failure:
                    return completed(8, {"status": "error", "errors": ["cleanup failed"]})
                return completed(0, {"status": "ok", "warnings": []})
            raise AssertionError(command)

        return run

    def test_successful_order_and_summary(self) -> None:
        paths = self.environment()
        events: list[str] = []
        with mock.patch.object(review_prediction, "run_command", side_effect=self.successful_runner(paths, events)):
            result = review_prediction.run_review_pipeline(self.date)
        self.assertEqual(events, ["actual", "daily_review", "evaluate", "metrics", "feedback", "cleanup"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["evaluated_forecast_path"], f"data/forecast/evaluated/{self.date}.json")
        self.assertEqual(len(result["metrics_paths"]), 3)
        self.assertEqual(result["generation_feedback_path"], "data/forecast/feedback/latest.json")
        self.assertEqual((paths["snapshots"] / f"{self.date}-previous-oil_futures.js").read_text(encoding="utf-8"), "morning-tab")

    def test_missing_forecast_stops_before_snapshot(self) -> None:
        self.environment(create_forecast=False)
        with mock.patch.object(review_prediction, "run_command") as run:
            with self.assertRaisesRegex(review_prediction.StageFailure, "冻结预测不存在") as raised:
                review_prediction.run_review_pipeline(self.date)
        self.assertEqual(raised.exception.stage, "forecast_missing")
        run.assert_not_called()

    def test_existing_morning_archive_is_preserved_for_later_backfill(self) -> None:
        paths = self.environment()
        target = paths["snapshots"] / f"{self.date}-previous-oil_futures.js"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original-morning", encoding="utf-8")
        paths["official"].write_text("newer-tab", encoding="utf-8")
        review_prediction.archive_morning_tab(target)
        self.assertEqual(target.read_text(encoding="utf-8"), "original-morning")

    def test_actual_failure_stops_all_downstream(self) -> None:
        paths = self.environment()
        calls: list[list[str]] = []
        with mock.patch.object(review_prediction, "run_command", side_effect=lambda command: calls.append(command) or completed(3, stderr="snapshot failed")):
            with self.assertRaises(review_prediction.StageFailure) as raised:
                review_prediction.run_review_pipeline(self.date)
        self.assertEqual(raised.exception.stage, "actual_snapshot")
        self.assertEqual(len(calls), 1)

    def test_wrong_actual_trade_date_stops_before_review(self) -> None:
        paths = self.environment()
        calls: list[list[str]] = []

        def run(command: list[str]):
            calls.append(command)
            write_actual(Path(command[command.index("--output") + 1]), "2026-07-15")
            return completed(0, {"status": "ok"})

        with mock.patch.object(review_prediction, "run_command", side_effect=run):
            with self.assertRaises(review_prediction.StageFailure) as raised:
                review_prediction.run_review_pipeline(self.date)
        self.assertEqual(raised.exception.stage, "actual_snapshot")
        self.assertEqual(len(calls), 1)

    def test_daily_review_failure_stops_evaluation_and_metrics(self) -> None:
        paths = self.environment()
        events: list[str] = []

        def run(command: list[str]):
            if Path(command[1]) == paths["update_script"]:
                events.append("actual")
                write_actual(Path(command[command.index("--output") + 1]), self.date)
                return completed(0, {"status": "ok"})
            events.append("daily_review")
            return completed(4, stderr="review failed")

        with mock.patch.object(review_prediction, "run_command", side_effect=run):
            with self.assertRaises(review_prediction.StageFailure) as raised:
                review_prediction.run_review_pipeline(self.date)
        self.assertEqual(raised.exception.stage, "daily_review")
        self.assertEqual(events, ["actual", "daily_review"])

    def test_evaluation_failure_preserves_existing_file_and_skips_metrics(self) -> None:
        paths = self.environment()
        old = paths["evaluated"] / f"{self.date}.json"
        old.parent.mkdir(parents=True)
        old.write_bytes(b"existing-valid-evaluation")
        events: list[str] = []

        def run(command: list[str]):
            script = Path(command[1])
            if script == paths["update_script"]:
                events.append("actual")
                write_actual(Path(command[command.index("--output") + 1]), self.date)
                return completed(0, {"status": "ok"})
            if script == paths["review_script"]:
                events.append("daily_review")
                paths["daily_review"].mkdir(parents=True, exist_ok=True)
                (paths["daily_review"] / f"{self.date}.json").write_text("{}", encoding="utf-8")
                return completed(0, {"status": "OK"})
            events.append("evaluate")
            return completed(5, {"status": "error", "errors": ["different output"]})

        with mock.patch.object(review_prediction, "run_command", side_effect=run):
            with self.assertRaises(review_prediction.StageFailure) as raised:
                review_prediction.run_review_pipeline(self.date)
        self.assertEqual(raised.exception.stage, "forecast_evaluation")
        self.assertEqual(events, ["actual", "daily_review", "evaluate"])
        self.assertEqual(old.read_bytes(), b"existing-valid-evaluation")

    def test_metrics_failure_keeps_successful_evaluation(self) -> None:
        paths = self.environment()
        events: list[str] = []
        with mock.patch.object(review_prediction, "run_command", side_effect=self.successful_runner(paths, events, metrics_failure=True)):
            with self.assertRaises(review_prediction.StageFailure) as raised:
                review_prediction.run_review_pipeline(self.date)
        self.assertEqual(raised.exception.stage, "metrics")
        self.assertTrue((paths["evaluated"] / f"{self.date}.json").exists())

    def test_cleanup_failure_is_warning_and_keeps_successful_outputs(self) -> None:
        paths = self.environment()
        events: list[str] = []
        with mock.patch.object(
            review_prediction,
            "run_command",
            side_effect=self.successful_runner(paths, events, cleanup_failure=True),
        ):
            result = review_prediction.run_review_pipeline(self.date)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["cleanup_status"], "warning")
        self.assertTrue(result["warnings"])
        self.assertTrue((paths["evaluated"] / f"{self.date}.json").exists())
        self.assertTrue((paths["metrics"] / "latest.json").exists())

    def test_identical_rerun_reuses_evaluated_at(self) -> None:
        paths = self.environment()
        events: list[str] = []
        runner = self.successful_runner(paths, events)
        with mock.patch.object(review_prediction, "run_command", side_effect=runner):
            review_prediction.run_review_pipeline(self.date)
            first = json.loads((paths["evaluated"] / f"{self.date}.json").read_text(encoding="utf-8"))
            review_prediction.run_review_pipeline(self.date)
            second = json.loads((paths["evaluated"] / f"{self.date}.json").read_text(encoding="utf-8"))
        self.assertEqual(first, second)
        self.assertEqual(events, ["actual", "daily_review", "evaluate", "metrics", "feedback", "cleanup"] * 2)

    def test_non_trading_day_outputs_valid_json(self) -> None:
        output = io.StringIO()
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--date", "2026-07-18"]), contextlib.redirect_stdout(output):
            code = review_prediction.main()
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "skipped")

    def test_main_failure_and_success_are_json(self) -> None:
        for result_or_error, expected_code, expected_status in (
            (review_prediction.StageFailure("metrics", "boom"), 2, "failed"),
            ({"date": self.date, "status": "ok"}, 0, "ok"),
        ):
            output = io.StringIO()
            patcher = (
                mock.patch.object(review_prediction, "run_review_pipeline", side_effect=result_or_error)
                if isinstance(result_or_error, Exception)
                else mock.patch.object(review_prediction, "run_review_pipeline", return_value=result_or_error)
            )
            with patcher, mock.patch.object(review_prediction, "LATEST_REVIEW", Path(tempfile.gettempdir()) / "review-integration-latest.json"), mock.patch.object(sys, "argv", [str(SCRIPT), "--date", self.date]), contextlib.redirect_stdout(output):
                code = review_prediction.main()
            payload = json.loads(output.getvalue())
            self.assertEqual(code, expected_code)
            self.assertEqual(payload["status"], expected_status)


if __name__ == "__main__":
    unittest.main()

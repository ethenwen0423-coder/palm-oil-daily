import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from skills.forecast_tracking_skill.tests.test_build_metrics import business_dates, evaluated_day, pending_day, write_json


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "prune_forecast_artifacts.py"
SPEC = importlib.util.spec_from_file_location("prune_forecast_artifacts", SCRIPT)
prune = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(prune)


class PruneForecastArtifactsTest(unittest.TestCase):
    def directories(self, root: Path) -> tuple[Path, Path, Path, Path]:
        paths = tuple(root / name for name in ("daily", "evaluated", "reviews", "runtime"))
        for path in paths:
            path.mkdir(parents=True)
        return paths

    def test_evaluated_and_review_retention_use_business_dates_not_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily, evaluated, reviews, runtime = self.directories(root)
            dates = business_dates(date(2026, 1, 1), 66)
            for index, report_date in enumerate(dates):
                target = evaluated / f"{report_date}.json"
                write_json(target, evaluated_day(report_date))
                target.touch()
                target.chmod(0o644)
            review_dates = business_dates(date(2026, 3, 1), 31)
            for report_date in review_dates:
                write_json(reviews / f"{report_date}.json", {"date": report_date, "status": "OK"})
            # Give the oldest business files the newest mtimes; retention must still remove them.
            (evaluated / f"{dates[0]}.json").touch()
            (reviews / f"{review_dates[0]}.json").touch()
            plan = prune.build_prune_plan(daily, evaluated, reviews, runtime, date.fromisoformat(dates[-1]))
        self.assertEqual(plan["evaluated_files_to_remove"], [str(evaluated / f"{dates[0]}.json")])
        self.assertEqual(plan["review_files_to_remove"], [str(reviews / f"{review_dates[0]}.json")])
        self.assertEqual(plan["retained_counts"]["evaluated_files"], 65)
        self.assertEqual(plan["retained_counts"]["review_files"], 30)

    def test_frozen_forecast_requires_matching_evaluation_and_age_over_five_days(self) -> None:
        as_of = date(2026, 7, 20)
        old_matched = "2026-07-10"
        old_unmatched = "2026-07-09"
        recent_matched = "2026-07-17"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily, evaluated, reviews, runtime = self.directories(root)
            for report_date in (old_matched, old_unmatched, recent_matched):
                write_json(daily / f"{report_date}.json", pending_day(report_date))
            for report_date in (old_matched, recent_matched):
                write_json(evaluated / f"{report_date}.json", evaluated_day(report_date))
            plan = prune.build_prune_plan(daily, evaluated, reviews, runtime, as_of)
        self.assertEqual(plan["frozen_forecast_files_to_remove"], [str(daily / f"{old_matched}.json")])
        self.assertNotIn(str(daily / f"{old_unmatched}.json"), plan["frozen_forecast_files_to_remove"])
        self.assertNotIn(str(daily / f"{recent_matched}.json"), plan["frozen_forecast_files_to_remove"])

    def test_runtime_snapshots_keep_seven_calendar_days(self) -> None:
        as_of = date(2026, 7, 20)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily, evaluated, reviews, runtime = self.directories(root)
            for age in range(9):
                report_date = (as_of - timedelta(days=age)).isoformat()
                (runtime / f"{report_date}-actual-oil_futures.js").write_text("fixture", encoding="utf-8")
            plan = prune.build_prune_plan(daily, evaluated, reviews, runtime, as_of)
        self.assertEqual(
            plan["runtime_snapshots_to_remove"],
            [
                str(runtime / "2026-07-12-actual-oil_futures.js"),
                str(runtime / "2026-07-13-actual-oil_futures.js"),
            ],
        )
        self.assertEqual(plan["retained_counts"]["runtime_snapshots"], 7)

    def test_invalid_json_and_missing_dates_are_warned_and_never_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily, evaluated, reviews, runtime = self.directories(root)
            invalid = evaluated / "2026-01-01.json"
            missing = reviews / "2026-01-01.json"
            unknown = runtime / "unknown.js"
            invalid.write_text("not json", encoding="utf-8")
            write_json(missing, {"status": "OK"})
            unknown.write_text("fixture", encoding="utf-8")
            plan = prune.build_prune_plan(daily, evaluated, reviews, runtime, date(2026, 7, 20))
        planned = sum(
            (plan[key] for key in (
                "evaluated_files_to_remove",
                "review_files_to_remove",
                "frozen_forecast_files_to_remove",
                "runtime_snapshots_to_remove",
            )),
            [],
        )
        self.assertEqual(planned, [])
        self.assertGreaterEqual(len(plan["warnings"]), 3)

    def test_dry_run_does_not_write_and_apply_rejects_outside_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily, evaluated, reviews, runtime = self.directories(root)
            as_of = date.today()
            old_date = (as_of - timedelta(days=10)).isoformat()
            write_json(daily / f"{old_date}.json", pending_day(old_date))
            write_json(evaluated / f"{old_date}.json", evaluated_day(old_date))
            command = [
                sys.executable,
                str(SCRIPT),
                "--forecast-daily-dir",
                str(daily),
                "--evaluated-dir",
                str(evaluated),
                "--review-daily-dir",
                str(reviews),
                "--runtime-snapshot-dir",
                str(runtime),
                "--dry-run",
            ]
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(payload["applied"])
            self.assertTrue((daily / f"{old_date}.json").exists())

            outside = root / "outside.json"
            outside.write_text("user data", encoding="utf-8")
            payload["frozen_forecast_files_to_remove"].append(str(outside))
            errors = prune.apply_prune_plan(payload, daily, evaluated, reviews, runtime)
            self.assertTrue(errors)
            self.assertTrue(outside.exists())
            self.assertFalse((daily / f"{old_date}.json").exists())


if __name__ == "__main__":
    unittest.main()

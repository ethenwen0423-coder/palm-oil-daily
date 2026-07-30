import importlib.util
import json
import os
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "prediction_review_watchdog.py"


def load_module():
    spec = importlib.util.spec_from_file_location("prediction_review_watchdog_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


WATCHDOG = load_module()


def write_forecast(root: Path, report_date: str, *, marker: str = "") -> Path:
    path = root / "data" / "forecast" / "daily" / f"{report_date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "forecast-schema-v1",
                "report_date": report_date,
                "records": [{"product": product, "marker": marker} for product in ("P", "Y", "OI")],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def write_valid_evaluation(root: Path, report_date: str) -> None:
    evaluated = root / "data" / "forecast" / "evaluated" / f"{report_date}.json"
    evaluated.parent.mkdir(parents=True, exist_ok=True)
    evaluated.write_text(
        json.dumps(
            {
                "report_date": report_date,
                "records": [
                    {"product": product, "evaluation_status": "evaluated"}
                    for product in ("P", "Y", "OI")
                ],
            }
        ),
        encoding="utf-8",
    )
    metrics = root / "data" / "forecast" / "metrics" / "latest.json"
    metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.write_text(
        json.dumps({"schema_version": "forecast-metrics-v1", "as_of": report_date}),
        encoding="utf-8",
    )


class PredictionReviewWatchdogTests(unittest.TestCase):
    def test_pending_dates_recover_oldest_gaps_and_gate_same_day_before_close(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for report_date in ("2026-07-29", "2026-07-30", "2026-07-31"):
                write_forecast(root, report_date)
            write_valid_evaluation(root, "2026-07-29")

            before_close = datetime(2026, 7, 31, 14, 30, tzinfo=WATCHDOG.SHANGHAI)
            after_close = datetime(2026, 7, 31, 15, 30, tzinfo=WATCHDOG.SHANGHAI)
            self.assertEqual(WATCHDOG.pending_dates(root, before_close, 5), ["2026-07-30"])
            self.assertEqual(
                WATCHDOG.pending_dates(root, after_close, 5),
                ["2026-07-30", "2026-07-31"],
            )

    def test_sync_forecast_inputs_copies_missing_valid_files_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "runtime"
            legacy = base / "legacy"
            write_forecast(legacy, "2026-07-24")
            invalid = legacy / "data" / "forecast" / "daily" / "2026-07-25.json"
            invalid.write_text("{broken", encoding="utf-8")
            copied = WATCHDOG.sync_forecast_inputs(root, legacy)
            self.assertEqual(copied, ["2026-07-24"])
            self.assertTrue((root / "data" / "forecast" / "daily" / "2026-07-24.json").exists())
            self.assertFalse((root / "data" / "forecast" / "daily" / "2026-07-25.json").exists())

    def test_sync_forecast_inputs_rejects_same_day_conflict(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "runtime"
            legacy = base / "legacy"
            write_forecast(root, "2026-07-24", marker="runtime")
            write_forecast(legacy, "2026-07-24", marker="legacy")
            with self.assertRaisesRegex(WATCHDOG.WatchdogError, "输入冲突"):
                WATCHDOG.sync_forecast_inputs(root, legacy)

    def test_lock_recovers_only_stale_empty_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            lock = Path(temporary) / "market-data-deploy.lock"
            lock.mkdir()
            self.assertFalse(WATCHDOG.acquire_lock(lock, stale_after_seconds=60))
            old = time.time() - 120
            os.utime(lock, (old, old))
            self.assertTrue(WATCHDOG.acquire_lock(lock, stale_after_seconds=60))
            lock.rmdir()


if __name__ == "__main__":
    unittest.main()

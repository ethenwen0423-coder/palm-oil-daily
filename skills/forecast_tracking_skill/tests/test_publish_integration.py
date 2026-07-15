import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
UPDATE_SCRIPT = SCRIPTS / "update_oil_futures_data.py"
DEPLOY_SCRIPT = SCRIPTS / "deploy_report.sh"
SPEC = importlib.util.spec_from_file_location("update_oil_futures_data", UPDATE_SCRIPT)
update = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(update)


def metadata(report_date: str = "2026-07-14") -> dict:
    return {
        "report_date": report_date,
        "generated_at": f"{report_date}T08:20:30+08:00",
        "cutoff_at": f"{report_date}T08:20:00+08:00",
        "timezone": "Asia/Shanghai",
        "quality_status": "unverified",
        "manifest": f"source_runs/{report_date}-daily/manifest.json",
        "market_snapshot": f"source_runs/{report_date}-daily/raw/futures_market_data.json",
    }


class UpdateForecastPublishTest(unittest.TestCase):
    def test_time_metadata_comes_from_matching_manifest_and_raw_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_runs = Path(temporary) / "source_runs"
            run_dir = source_runs / "2026-07-14-daily"
            (run_dir / "raw").mkdir(parents=True)
            (run_dir / "manifest.json").write_text(
                json.dumps({"date": "2026-07-14", "kind": "daily", "generated_at": "2026-07-14T08:20:30"}),
                encoding="utf-8",
            )
            (run_dir / "raw" / "futures_market_data.json").write_text(
                json.dumps({"date": "2026-07-14", "timestamp": "2026-07-14T08:20:00"}),
                encoding="utf-8",
            )
            with mock.patch.object(update, "SOURCE_RUNS", source_runs), mock.patch.object(update, "ROOT", Path(temporary)):
                result = update.load_forecast_time_metadata("2026-07-14")
        self.assertEqual(result["generated_at"], "2026-07-14T08:20:30+08:00")
        self.assertEqual(result["cutoff_at"], "2026-07-14T08:20:00+08:00")
        self.assertEqual(result["timezone"], "Asia/Shanghai")

    def test_missing_time_metadata_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(update, "SOURCE_RUNS", Path(temporary)):
            with self.assertRaisesRegex(RuntimeError, "缺少晨报 source manifest"):
                update.load_forecast_time_metadata("2026-07-14")

    def test_quality_gate_failure_never_calls_forecast_or_overwrites_official_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "data" / "oil_futures.js"
            output.parent.mkdir()
            output.write_text("original", encoding="utf-8")
            with (
                mock.patch.object(update, "run_data_quality_gate", side_effect=RuntimeError("gate failed")),
                mock.patch.object(update, "run_forecast_recorder") as recorder,
                mock.patch.object(update, "publish_dataset") as publisher,
            ):
                with self.assertRaisesRegex(RuntimeError, "gate failed"):
                    update.validate_freeze_and_publish({"contracts": []}, output, metadata())
            self.assertEqual(output.read_text(encoding="utf-8"), "original")
            self.assertFalse(output.with_name(".oil_futures.quality-check.tmp.js").exists())
            recorder.assert_not_called()
            publisher.assert_not_called()

    def test_forecast_failure_never_overwrites_or_publishes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "data" / "oil_futures.js"
            output.parent.mkdir()
            output.write_text("original", encoding="utf-8")
            with (
                mock.patch.object(update, "run_data_quality_gate"),
                mock.patch.object(update, "run_forecast_recorder", side_effect=RuntimeError("freeze failed")),
                mock.patch.object(update, "publish_dataset") as publisher,
            ):
                with self.assertRaisesRegex(RuntimeError, "freeze failed"):
                    update.validate_freeze_and_publish({"contracts": []}, output, metadata())
            self.assertEqual(output.read_text(encoding="utf-8"), "original")
            self.assertFalse(output.with_name(".oil_futures.quality-check.tmp.js").exists())
            publisher.assert_not_called()

    def test_already_exists_is_success_and_order_is_gate_freeze_then_publish(self) -> None:
        events: list[str] = []
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "data" / "oil_futures.js"
            output.parent.mkdir()
            output.write_text("original", encoding="utf-8")
            with (
                mock.patch.object(update, "run_data_quality_gate", side_effect=lambda _: events.append("gate")),
                mock.patch.object(
                    update,
                    "run_forecast_recorder",
                    side_effect=lambda *_: events.append("freeze") or {"status": "ok", "already_exists": True},
                ),
                mock.patch.object(update, "write_forecast_time_metadata", side_effect=lambda _: events.append("metadata")),
                mock.patch.object(update, "publish_dataset", side_effect=lambda *_: events.append("publish")),
                mock.patch.object(update, "OUTPUT", output),
            ):
                result = update.validate_freeze_and_publish({"contracts": []}, output, metadata())
        self.assertTrue(result["already_exists"])
        self.assertEqual(events, ["gate", "freeze", "metadata", "publish"])

    def test_actual_snapshot_is_atomic_and_never_publishes_or_freezes(self) -> None:
        payload = {
            "contracts": [
                {
                    "product": product,
                    "contract_rank": 1,
                    "trade_date": "2026-07-14",
                    "price": "101",
                    "preclose": "100",
                    "high": "102",
                    "low": "99",
                }
                for product in ("P", "Y", "OI")
            ]
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            official = root / "data" / "oil_futures.js"
            actual = root / "data" / "review" / "snapshots" / "2026-07-14-actual-oil_futures.js"
            official.parent.mkdir(parents=True)
            official.write_text("official", encoding="utf-8")
            with (
                mock.patch.object(update, "OUTPUT", official),
                mock.patch.object(update, "run_data_quality_gate"),
                mock.patch.object(update, "publish_dataset") as publisher,
                mock.patch.object(update, "run_forecast_recorder") as recorder,
            ):
                update.write_actual_snapshot_atomically(payload, actual, "2026-07-14")
            self.assertEqual(official.read_text(encoding="utf-8"), "official")
            self.assertTrue(actual.exists())
            publisher.assert_not_called()
            recorder.assert_not_called()

    def test_actual_snapshot_uses_exact_frozen_contracts_without_discovery_or_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            forecast_dir = root / "data" / "forecast" / "daily"
            forecast_dir.mkdir(parents=True)
            (forecast_dir / "2026-07-14.json").write_text(
                json.dumps(
                    {
                        "records": [
                            {"product": product, "contract": f"{product}2609", "contract_rank": 1}
                            for product in ("P", "Y", "OI")
                        ]
                    }
                ),
                encoding="utf-8",
            )

            def quote(_ak, _variety, contract):
                return {
                    "contract": contract,
                    "price": 101,
                    "change_pct": 1,
                    "open": 100,
                    "high": 102,
                    "low": 99,
                    "preclose": 100,
                    "volume": 10,
                    "open_interest": 20,
                    "tradedate": "2026-07-14",
                    "source": "fixture",
                }

            with (
                mock.patch.object(update, "FORECAST_DAILY_DIR", forecast_dir),
                mock.patch.object(update, "load_akshare", return_value=object()),
                mock.patch.object(update, "ak_realtime_contract", side_effect=quote),
                mock.patch.object(update, "run_contract_selector") as selector,
                mock.patch.object(update, "call_master_analysis") as analysis,
                mock.patch.object(update, "hithink_contract") as hithink,
            ):
                payload = update.build_actual_snapshot_payload("2026-07-14")
            self.assertEqual([row["contract"] for row in payload["contracts"]], ["P2609", "Y2609", "OI2609"])
            selector.assert_not_called()
            analysis.assert_not_called()
            hithink.assert_not_called()

    def test_morning_publish_module_has_no_daily_review_hook(self) -> None:
        self.assertFalse(hasattr(update, "run_daily_review"))
        self.assertFalse(hasattr(update, "archive_existing_output"))

    def test_forecast_recorder_uses_report_date_for_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            recorder = root / "record_forecast.py"
            recorder.write_text("# fixture", encoding="utf-8")
            completed = subprocess.CompletedProcess([], 0, stdout='{"status":"ok","already_exists":false}', stderr="")
            with (
                mock.patch.object(update, "ROOT", root),
                mock.patch.object(update, "FORECAST_RECORDER_CLI", recorder),
                mock.patch.object(update, "FORECAST_DAILY_DIR", root / "data" / "forecast" / "daily"),
                mock.patch.object(update.subprocess, "run", return_value=completed) as run,
            ):
                update.run_forecast_recorder(root / "temp.js", metadata())
            command = run.call_args.args[0]
        forecast_index = command.index("--forecast") + 1
        self.assertEqual(Path(command[forecast_index]).name, "2026-07-14.json")


class DeployReportTest(unittest.TestCase):
    def run_deploy(self, changed_reports: str, **flags: str) -> tuple[subprocess.CompletedProcess[str], str]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "scripts").mkdir()
        shutil.copy2(DEPLOY_SCRIPT, root / "scripts" / "deploy_report.sh")
        fake_bin = root / "fake-bin"
        fake_bin.mkdir()
        log = root / "calls.log"
        git = fake_bin / "git"
        git.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                echo "git $*" >> "$CALL_LOG"
                if [[ "$1" == "diff" && "$2" == "--name-only" ]]; then
                  printf '%s\n' "$CHANGED_REPORTS"
                elif [[ "$1" == "ls-files" ]]; then
                  exit 0
                elif [[ "$1" == "diff" && "$2" == "--quiet" ]]; then
                  exit 1
                fi
                """
            ),
            encoding="utf-8",
        )
        python = fake_bin / "python3"
        python.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                echo "python3 $*" >> "$CALL_LOG"
                if [[ "$1" == "-c" ]]; then
                  exec "$REAL_PYTHON" "$@"
                fi
                if [[ "$1" == "scripts/update_oil_futures_data.py" && "$*" == *"--print-time-metadata"* ]]; then
                  printf '%s\n' '{"generated_at":"2026-07-14T08:20:30+08:00","cutoff_at":"2026-07-14T08:20:00+08:00"}'
                  exit 0
                fi
                if [[ "${FAIL_MANIFEST:-0}" == "1" && "$1" == "skills/data_quality_gate_skill/scripts/validate_data.py" && "$*" == *"--manifest"* ]]; then
                  exit 7
                fi
                if [[ "${FAIL_FEEDBACK:-0}" == "1" && "$1" == "skills/forecast_tracking_skill/scripts/validate_report_feedback.py" ]]; then
                  exit 8
                fi
                if [[ "${FAIL_UPDATE:-0}" == "1" && "$1" == "scripts/update_oil_futures_data.py" ]]; then
                  exit 9
                fi
                exit 0
                """
            ),
            encoding="utf-8",
        )
        git.chmod(0o755)
        python.chmod(0o755)
        env = {
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "CALL_LOG": str(log),
            "CHANGED_REPORTS": changed_reports,
            "REAL_PYTHON": sys.executable,
            **flags,
        }
        result = subprocess.run(
            ["bash", str(root / "scripts" / "deploy_report.sh")],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return result, log.read_text(encoding="utf-8") if log.exists() else ""

    def test_daily_deploy_passes_explicit_time_slice(self) -> None:
        result, calls = self.run_deploy("reports/2026-07-14.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "scripts/update_oil_futures_data.py --report-date 2026-07-14 --generated-at 2026-07-14T08:20:30+08:00 --cutoff-at 2026-07-14T08:20:00+08:00",
            calls,
        )
        self.assertIn("git add -- reports data downloads miniprogram/data :(exclude)data/forecast/daily/*.json", calls)
        self.assertIn(":(exclude)data/review/runtime_snapshots/**", calls)
        self.assertNotIn("git reset", calls)

    def test_weekly_only_deploy_does_not_update_or_freeze(self) -> None:
        result, calls = self.run_deploy("reports/2026-07-13-weekend.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("update_oil_futures_data.py", calls)
        self.assertIn("scripts/publish_report.py", calls)

    def test_multiple_daily_dates_fail_before_publish(self) -> None:
        result, calls = self.run_deploy("reports/2026-07-14.md\nreports/2026-07-15.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("multiple daily report dates", result.stderr)
        self.assertNotIn("scripts/publish_report.py", calls)

    def test_manifest_gate_failure_stops_before_forecast_update(self) -> None:
        result, calls = self.run_deploy("reports/2026-07-14.md", FAIL_MANIFEST="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("update_oil_futures_data.py", calls)
        self.assertNotIn("scripts/publish_report.py", calls)

    def test_forecast_update_failure_stops_publish_and_git(self) -> None:
        result, calls = self.run_deploy("reports/2026-07-14.md", FAIL_UPDATE="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("scripts/publish_report.py", calls)
        self.assertNotIn("git add", calls)
        self.assertNotIn("git commit", calls)
        self.assertNotIn("git push", calls)

    def test_feedback_gate_failure_stops_before_forecast_update(self) -> None:
        result, calls = self.run_deploy("reports/2026-07-14.md", FAIL_FEEDBACK="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("validate_report_feedback.py", calls)
        self.assertNotIn("update_oil_futures_data.py", calls)
        self.assertNotIn("scripts/publish_report.py", calls)
        self.assertNotIn("git add", calls)


if __name__ == "__main__":
    unittest.main()

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INSTALL_SCRIPT = ROOT / "scripts" / "install_prediction_review_launchd.sh"
PRODUCTION_ROOT = "/Users/ethen/Sites/palm-oil-daily-runtime"


class PredictionReviewLaunchdDryRunTest(unittest.TestCase):
    def make_fixture(self, dirty: bool = False) -> tuple[Path, Path, Path, dict[str, str]]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        repo = base / "repo"
        home = base / "home"
        fake_bin = base / "fake-bin"
        repo.mkdir()
        home.mkdir()
        fake_bin.mkdir()

        dependencies = (
            "scripts/prediction_review_watchdog.py",
            "scripts/review_prediction.py",
            "skills/forecast_tracking_skill/scripts/evaluate_forecast.py",
            "skills/forecast_tracking_skill/scripts/build_metrics.py",
            "skills/forecast_tracking_skill/scripts/build_generation_feedback.py",
            "skills/forecast_tracking_skill/scripts/validate_forecast.py",
            "skills/forecast_tracking_skill/scripts/prune_forecast_artifacts.py",
            "scripts/publish_prediction_review.sh",
        )
        for relative in dependencies:
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n", encoding="utf-8")
        for relative in (
            "data/forecast/daily",
            "data/forecast/evaluated",
            "data/forecast/metrics",
            "data/forecast/feedback",
            "data/review/daily",
            "data/review/snapshots",
        ):
            (repo / relative).mkdir(parents=True, exist_ok=True)

        copied_script = repo / "scripts" / INSTALL_SCRIPT.name
        copied_script.write_text(
            INSTALL_SCRIPT.read_text(encoding="utf-8").replace(PRODUCTION_ROOT, str(repo)),
            encoding="utf-8",
        )
        copied_script.chmod(0o755)

        (repo / ".git").mkdir()

        launchctl_log = base / "launchctl.log"
        fake_launchctl = fake_bin / "launchctl"
        fake_launchctl.write_text('#!/usr/bin/env bash\necho "$*" >> "$LAUNCHCTL_LOG"\nexit 99\n', encoding="utf-8")
        fake_launchctl.chmod(0o755)
        fake_git = fake_bin / "git"
        fake_git.write_text('#!/usr/bin/env bash\nprintf "%s" "${FAKE_GIT_STATUS:-}"\n', encoding="utf-8")
        fake_git.chmod(0o755)
        env = {
            **os.environ,
            "HOME": str(home),
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "LAUNCHCTL_LOG": str(launchctl_log),
            "FAKE_GIT_STATUS": "?? dirty.txt\n" if dirty else "",
            "PALM_OIL_PREDICTION_RUNTIME_ROOT": str(repo),
        }
        return repo, home, launchctl_log, env

    def run_dry(self, repo: Path, env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            ["bash", str(repo / "scripts" / INSTALL_SCRIPT.name), "--dry-run"],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def test_clean_dry_run_writes_nothing_and_never_calls_launchctl(self) -> None:
        repo, home, launchctl_log, env = self.make_fixture()
        result, payload = self.run_dry(repo, env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertFalse(payload["files_written"])
        self.assertFalse(payload["launchctl_called"])
        self.assertFalse((home / "Library" / "LaunchAgents").exists())
        self.assertFalse(launchctl_log.exists())

    def test_dirty_worktree_blocks_installation(self) -> None:
        repo, _, launchctl_log, env = self.make_fixture(dirty=True)
        result, payload = self.run_dry(repo, env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertTrue(payload["installation_blocked_by_dirty_worktree"])
        self.assertIn("人工审查并提交", payload["next_action"])
        self.assertFalse(launchctl_log.exists())

    def test_missing_review_or_forecast_dependency_blocks(self) -> None:
        for missing in (
            "scripts/review_prediction.py",
            "skills/forecast_tracking_skill/scripts/evaluate_forecast.py",
            "skills/forecast_tracking_skill/scripts/build_metrics.py",
            "skills/forecast_tracking_skill/scripts/build_generation_feedback.py",
        ):
            with self.subTest(missing=missing):
                repo, _, launchctl_log, env = self.make_fixture()
                (repo / missing).unlink()
                result, payload = self.run_dry(repo, env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(missing, payload["missing_dependencies"])
                self.assertFalse(launchctl_log.exists())

    def test_output_contains_schedule_timezone_paths_and_command(self) -> None:
        result = subprocess.run(
            ["bash", str(INSTALL_SCRIPT), "--dry-run"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["schedule"],
            ["RunAtLoad", "every 15 minutes", "same-day reviews become due after 15:20"],
        )
        self.assertEqual(payload["timezone"], "Asia/Shanghai")
        self.assertEqual(payload["working_directory"], PRODUCTION_ROOT)
        self.assertEqual(payload["launch_agent_label"], "com.vinsontesla.palm-oil-prediction-review")
        self.assertEqual(payload["command"], "python3 scripts/prediction_review_watchdog.py")

    def test_script_syntax_and_retry_guard_contract(self) -> None:
        syntax = subprocess.run(["bash", "-n", str(INSTALL_SCRIPT)], text=True, capture_output=True, check=False)
        self.assertEqual(syntax.returncode, 0, syntax.stderr)
        text = INSTALL_SCRIPT.read_text(encoding="utf-8")
        watchdog = (ROOT / "scripts" / "prediction_review_watchdog.py").read_text(encoding="utf-8")
        self.assertIn("<key>RunAtLoad</key>", text)
        self.assertIn("<key>StartInterval</key>", text)
        self.assertIn("<integer>900</integer>", text)
        self.assertIn("prediction_review_watchdog.py", text)
        self.assertIn("market-data-deploy.lock", watchdog)
        self.assertIn('["git", "fetch", "origin", "main"]', watchdog)
        self.assertIn("sync_forecast_inputs", watchdog)
        self.assertIn("rollback_generated", watchdog)
        self.assertIn("publish_prediction_review.sh", watchdog)
        weekday_values = [
            int(value)
            for value in re.findall(
                r"<key>Weekday</key><integer>(\d+)</integer>",
                text,
            )
        ]
        self.assertEqual(weekday_values, [])

    def test_generated_runner_delegates_to_clean_runtime_watchdog(self) -> None:
        text = INSTALL_SCRIPT.read_text(encoding="utf-8")
        runner = text.split('cat > "$RUNNER" <<\'RUNNER\'\n', 1)[1].split("\nRUNNER\n", 1)[0]
        self.assertIn('ROOT="__RUNTIME_ROOT__"', runner)
        self.assertIn('exec python3 "$ROOT/scripts/prediction_review_watchdog.py"', runner)


if __name__ == "__main__":
    unittest.main()

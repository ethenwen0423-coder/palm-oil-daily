from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_codex_bounded.py"
INSTALLER = ROOT / "scripts" / "install_daily_watchdog_launchd.sh"


class BoundedCodexRunnerTests(unittest.TestCase):
    def test_success_writes_terminal_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            status = Path(temporary) / "status.json"
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--timeout-seconds",
                    "5",
                    "--status-file",
                    str(status),
                    "--",
                    "python3",
                    "-c",
                    "import sys; assert sys.stdin.read() == 'prompt'",
                ],
                input="prompt",
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(status.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["exit_code"], 0)

    def test_timeout_is_terminal_and_uses_exit_124(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            status = Path(temporary) / "status.json"
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--timeout-seconds",
                    "1",
                    "--status-file",
                    str(status),
                    "--",
                    "python3",
                    "-c",
                    "import time; time.sleep(30)",
                ],
                text=True,
                capture_output=True,
                timeout=8,
                check=False,
            )
            payload = json.loads(status.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 124)
        self.assertEqual(payload["status"], "timeout")
        self.assertEqual(payload["exit_code"], 124)

    def test_installer_uses_source_controlled_bounded_ephemeral_job(self) -> None:
        installer = INSTALLER.read_text(encoding="utf-8")
        self.assertIn("palm-oil-daily-runtime", installer)
        self.assertIn("run_codex_bounded.py", installer)
        self.assertIn("--timeout-seconds 900", installer)
        self.assertIn("--ephemeral", installer)
        self.assertIn("--ignore-user-config", installer)
        self.assertIn("--model gpt-5.6-terra", installer)
        self.assertIn("report_quality.json", installer)
        self.assertIn("92分报告审计", installer)
        self.assertNotIn("85分报告审计", installer)
        self.assertIn("preserve dirty supply-demand runtime", installer)
        self.assertNotIn("supply-demand runtime must be a clean main checkout", installer)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "server" / "run_research_agent.py"
SPEC = importlib.util.spec_from_file_location("server_research_agent", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ServerResearchAgentTests(unittest.TestCase):
    def test_schedule_has_daily_retry_and_sunday_weekend_window(self) -> None:
        timezone = MODULE.SHANGHAI
        self.assertIsNone(
            MODULE.select_due(datetime(2026, 8, 7, 5, 59, tzinfo=timezone))
        )
        self.assertEqual(
            MODULE.select_due(datetime(2026, 8, 7, 6, 0, tzinfo=timezone)),
            "daily",
        )
        self.assertIsNone(
            MODULE.select_due(datetime(2026, 8, 9, 21, 14, tzinfo=timezone))
        )
        self.assertEqual(
            MODULE.select_due(datetime(2026, 8, 9, 21, 15, tzinfo=timezone)),
            "weekend",
        )
        self.assertIsNone(
            MODULE.select_due(datetime(2026, 8, 8, 21, 15, tzinfo=timezone))
        )

    def test_model_output_cannot_change_fixed_logic(self) -> None:
        payload = {
            "report_markdown": "# 08月07日晨报\n" + ("报告内容" * 500),
            "outline": {"report_date": "2026-08-07", "kind": "daily"},
            "fixed_logic": ["changed"],
        }
        with self.assertRaisesRegex(MODULE.ResearchAgentError, "fixed-logic"):
            MODULE.validate_model_output(
                payload,
                report_date="2026-08-07",
                kind="daily",
            )

    def test_dry_run_is_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            site = base / "site"
            runtime = base / "runtime"
            live = base / "live"
            state = base / "state"
            site.mkdir()
            mock_response = base / "response.json"
            mock_response.write_text("{}", encoding="utf-8")
            before = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--site-root",
                    str(site),
                    "--runtime-root",
                    str(runtime),
                    "--live-data-root",
                    str(live),
                    "--state-root",
                    str(state),
                    "--now",
                    "2026-08-07T06:00:00+08:00",
                    "--mock-response",
                    str(mock_response),
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["kind"], "daily")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

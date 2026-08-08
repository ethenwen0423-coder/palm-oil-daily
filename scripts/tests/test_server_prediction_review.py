from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "server" / "run_prediction_review.py"
SPEC = importlib.util.spec_from_file_location("server_prediction_review", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ServerPredictionReviewTests(unittest.TestCase):
    def test_dry_run_is_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            site = base / "site"
            runtime = base / "runtime"
            live = base / "live"
            state = base / "state"
            site.mkdir()
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
                    "2026-08-07T15:20:00+08:00",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["current_day_eligible_after"], "15:20 Asia/Shanghai")
        self.assertEqual(before, after)

    def test_review_cli_supports_server_prepared_close_snapshot(self) -> None:
        review = (ROOT / "scripts" / "review_prediction.py").read_text(encoding="utf-8")
        self.assertIn("--prepared-actual", review)
        self.assertIn("prepared_actual.read_text", review)
        self.assertIn("validate_actual_snapshot(actual_path, review_date)", review)


if __name__ == "__main__":
    unittest.main()

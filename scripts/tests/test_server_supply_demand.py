import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "server" / "run_supply_demand.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


SUPPLY = load_module("server_supply_demand_test", RUNNER)


class ServerSupplyDemandTests(unittest.TestCase):
    def test_parse_now_uses_shanghai_timezone(self):
        parsed = SUPPLY.parse_now("2026-07-31T01:20:00Z")
        self.assertEqual(parsed.isoformat(), "2026-07-31T09:20:00+08:00")

    def test_dry_run_is_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            site = base / "site"
            live = base / "live"
            state = base / "state"
            site.mkdir()
            live.mkdir()
            before = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
            result = subprocess.run(
                [
                    "python3",
                    str(RUNNER),
                    "--site-root",
                    str(site),
                    "--live-data-root",
                    str(live),
                    "--state-root",
                    str(state),
                    "--now",
                    "2026-07-31T09:20:00+08:00",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["report_date"], "2026-07-31")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(before, after)

    def test_runner_declares_daily_idempotency_and_strict_validation(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('"official_sources_already_checked_today"', text)
        self.assertIn('"--existing"', text)
        self.assertGreaterEqual(text.count('"--strict"'), 2)
        self.assertIn("sync_module.sync_supply", text)


if __name__ == "__main__":
    unittest.main()

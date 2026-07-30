import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COLLECTOR_SCRIPT = ROOT / "server" / "run_market_collector.py"
SYNC_SCRIPT = ROOT / "server" / "sync_live_data.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


COLLECTOR = load_module("server_market_collector_test", COLLECTOR_SCRIPT)
SYNC = load_module("server_live_data_sync_test", SYNC_SCRIPT)


def write_dataset(root: Path, relative: str, marker: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if relative.endswith(".js"):
        path.write_text(f"window.TEST = {{\"marker\": \"{marker}\"}};\n", encoding="utf-8")
    else:
        payload = [{"marker": marker}] if relative == "reports.json" else {"marker": marker}
        path.write_text(
            json.dumps(payload, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


def write_all_datasets(root: Path, marker: str) -> None:
    for relative in SYNC.UPSTREAM_PATHS + SYNC.MARKET_PATHS:
        write_dataset(root, relative, marker)


class ServerMarketCollectorTests(unittest.TestCase):
    def test_session_selection_covers_recovery_windows(self):
        timezone = COLLECTOR.SHANGHAI
        cases = {
            datetime(2026, 7, 31, 6, 29, tzinfo=timezone): ("overnight", "2026-07-30"),
            datetime(2026, 7, 31, 6, 30, tzinfo=timezone): ("morning", "2026-07-31"),
            datetime(2026, 7, 31, 11, 35, tzinfo=timezone): ("midday", "2026-07-31"),
            datetime(2026, 7, 31, 15, 5, tzinfo=timezone): ("close", "2026-07-31"),
            datetime(2026, 7, 31, 21, 20, tzinfo=timezone): ("night_open", "2026-07-31"),
            datetime(2026, 7, 31, 23, 10, tzinfo=timezone): ("night_close", "2026-07-31"),
            datetime(2026, 8, 1, 2, 40, tzinfo=timezone): ("overnight", "2026-07-31"),
        }
        for now, expected in cases.items():
            with self.subTest(now=now):
                self.assertEqual(COLLECTOR.select_session(now), expected)
        self.assertIsNone(
            COLLECTOR.select_session(datetime(2026, 8, 2, 12, 0, tzinfo=timezone))
        )

    def test_dry_run_does_not_create_runtime_or_state(self):
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
                    str(COLLECTOR_SCRIPT),
                    "--site-root",
                    str(site),
                    "--runtime-root",
                    str(runtime),
                    "--live-data-root",
                    str(live),
                    "--state-root",
                    str(state),
                    "--now",
                    "2026-07-31T11:35:00+08:00",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["session"], "midday")
        self.assertEqual(before, after)

    def test_upstream_sync_stops_overwriting_server_market_data_after_marker(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            upstream = base / "upstream"
            market = base / "market"
            live = base / "live"
            write_all_datasets(upstream, "bootstrap")
            first = SYNC.sync_upstream(upstream, live)
            self.assertEqual(first["bootstrapped"], list(SYNC.MARKET_PATHS))

            write_all_datasets(market, "server")
            SYNC.sync_market(market, live, session="midday")
            write_all_datasets(upstream, "new-upstream")
            second = SYNC.sync_upstream(upstream, live)

            self.assertTrue(second["server_market_owned"])
            self.assertEqual(
                json.loads((live / "reports.json").read_text(encoding="utf-8"))[0][
                    "marker"
                ],
                "new-upstream",
            )
            self.assertEqual(
                json.loads(
                    (live / "oil_futures.json").read_text(encoding="utf-8")
                )["marker"],
                "server",
            )

    def test_sync_preflight_does_not_replace_existing_files_when_required_input_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            live = base / "live"
            write_all_datasets(source, "candidate")
            write_all_datasets(live, "existing")
            (source / "contracts" / "current_contracts.json").unlink()
            with self.assertRaises(SYNC.SyncError):
                SYNC.sync_market(source, live, session="close")
            self.assertEqual(
                json.loads(
                    (live / "oil_futures.json").read_text(encoding="utf-8")
                )["marker"],
                "existing",
            )

    def test_server_update_and_market_deploy_use_live_data_contract(self):
        update_site = (ROOT / "server" / "update-site.sh").read_text(encoding="utf-8")
        deploy = (ROOT / "scripts" / "deploy_oil_futures_tab.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("server/sync_live_data.py", update_site)
        self.assertIn("compose.automation.yaml", update_site)
        self.assertIn('PUBLISH_MODE="${PALM_OIL_PUBLISH_MODE:-git}"', deploy)
        self.assertIn('"publish_mode": "files"', deploy)
        self.assertLess(
            deploy.index('if [[ "$PUBLISH_MODE" == "files" ]]'),
            deploy.index("git add --"),
        )


if __name__ == "__main__":
    unittest.main()

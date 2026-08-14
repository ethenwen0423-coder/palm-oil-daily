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
    for relative in (
        SYNC.UPSTREAM_PATHS
        + SYNC.SUPPLY_PATHS
        + SYNC.MARKET_PATHS
        + SYNC.AI_PATHS
    ):
        write_dataset(root, relative, marker)


class ServerMarketCollectorTests(unittest.TestCase):
    def test_morning_fundamental_readiness_requires_same_day_frozen_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "oil_futures.js"
            payload = {
                "fundamental_updated_at": "2026-08-14T06:35:00+08:00",
                "fundamental_update_session": "morning",
                "contracts": [{"symbol": "P2609"}],
            }
            path.write_text(
                "window.OIL_FUTURES_CONTRACTS = "
                + json.dumps(payload, ensure_ascii=False)
                + ";\n",
                encoding="utf-8",
            )
            self.assertTrue(
                COLLECTOR.morning_fundamentals_ready(path, "2026-08-14")
            )
            self.assertFalse(
                COLLECTOR.morning_fundamentals_ready(path, "2026-08-15")
            )

    def test_morning_fundamental_readiness_rejects_invalid_or_empty_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "oil_futures.js"
            path.write_text("not-json\n", encoding="utf-8")
            self.assertFalse(
                COLLECTOR.morning_fundamentals_ready(path, "2026-08-14")
            )
            path.write_text(
                json.dumps(
                    {
                        "fundamental_updated_at": "2026-08-14T06:35:00+08:00",
                        "fundamental_update_session": "morning",
                        "contracts": [],
                    }
                ),
                encoding="utf-8",
            )
            self.assertFalse(
                COLLECTOR.morning_fundamentals_ready(path, "2026-08-14")
            )

    def test_intraday_recovery_bootstraps_morning_before_selected_session(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "oil_futures.js"
            self.assertEqual(
                COLLECTOR.deployment_sessions("midday", missing, "2026-08-14"),
                ("morning", "midday"),
            )
            self.assertEqual(
                COLLECTOR.deployment_sessions("close", missing, "2026-08-14"),
                ("morning", "close"),
            )
            self.assertEqual(
                COLLECTOR.deployment_sessions("overnight", missing, "2026-08-14"),
                ("overnight",),
            )

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

    def test_refresh_slots_allow_one_publish_per_ten_minute_window(self):
        timezone = COLLECTOR.SHANGHAI
        self.assertEqual(
            COLLECTOR.refresh_slot(
                datetime(2026, 7, 31, 11, 35, 29, tzinfo=timezone)
            ),
            "20260731T1130",
        )
        self.assertEqual(
            COLLECTOR.refresh_slot(
                datetime(2026, 7, 31, 11, 40, 1, tzinfo=timezone)
            ),
            "20260731T1140",
        )
        with self.assertRaises(ValueError):
            COLLECTOR.refresh_slot(
                datetime(2026, 7, 31, 11, 40, tzinfo=timezone),
                interval_minutes=7,
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
            self.assertEqual(first["reports_copied"], list(SYNC.REPORT_PATHS))
            self.assertEqual(first["review_copied"], list(SYNC.REVIEW_PATHS))
            self.assertEqual(first["supply_copied"], list(SYNC.SUPPLY_PATHS))
            self.assertEqual(first["ai_copied"], list(SYNC.AI_PATHS))

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
            self.assertEqual(
                json.loads(
                    (live / "market_assistant_brief.json").read_text(
                        encoding="utf-8"
                    )
                )["marker"],
                "new-upstream",
            )

    def test_research_and_review_ownership_stop_upstream_overwrites_independently(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            upstream = base / "upstream"
            server = base / "server"
            live = base / "live"
            write_all_datasets(upstream, "bootstrap")
            SYNC.sync_upstream(upstream, live)
            write_all_datasets(server, "server")

            research = SYNC.sync_research(server, live, session="daily")
            self.assertTrue(research["server_research_owned"])
            self.assertFalse((live / SYNC.REVIEW_READY_MARKER).exists())

            write_all_datasets(upstream, "upstream-after-report")
            interim = SYNC.sync_upstream(upstream, live)
            self.assertEqual(interim["reports_copied"], [])
            self.assertEqual(interim["review_copied"], list(SYNC.REVIEW_PATHS))
            self.assertEqual(
                json.loads((live / "reports.json").read_text(encoding="utf-8"))[0]["marker"],
                "server",
            )
            self.assertEqual(
                json.loads(
                    (live / "forecast" / "metrics" / "latest.json").read_text(
                        encoding="utf-8"
                    )
                )["marker"],
                "upstream-after-report",
            )

            review = SYNC.sync_review(server, live, session="close")
            self.assertTrue(review["server_review_owned"])
            write_all_datasets(upstream, "new-upstream")
            final = SYNC.sync_upstream(upstream, live)
            self.assertEqual(final["reports_copied"], [])
            self.assertEqual(final["review_copied"], [])
            self.assertEqual(
                json.loads(
                    (live / "forecast" / "metrics" / "latest.json").read_text(
                        encoding="utf-8"
                    )
                )["marker"],
                "server",
            )

    def test_supply_ownership_is_independent_and_stops_upstream_overwrites(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            upstream = base / "upstream"
            server = base / "server"
            live = base / "live"
            write_all_datasets(upstream, "bootstrap")
            SYNC.sync_upstream(upstream, live)
            write_all_datasets(server, "server")

            result = SYNC.sync_supply(server, live, session="daily")
            self.assertTrue(result["server_supply_owned"])
            self.assertTrue((live / SYNC.SUPPLY_READY_MARKER).exists())

            write_all_datasets(upstream, "new-upstream")
            second = SYNC.sync_upstream(upstream, live)
            self.assertTrue(second["server_supply_owned"])
            self.assertEqual(second["supply_copied"], [])
            self.assertEqual(
                json.loads((live / "supply-demand.json").read_text(encoding="utf-8"))[
                    "marker"
                ],
                "server",
            )

    def test_ai_ownership_is_independent_from_market_ownership(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            upstream = base / "upstream"
            server = base / "server"
            live = base / "live"
            write_all_datasets(upstream, "bootstrap")
            SYNC.sync_upstream(upstream, live)
            write_all_datasets(server, "server")

            SYNC.sync_market(server, live, session="midday")
            self.assertFalse((live / SYNC.AI_READY_MARKER).exists())
            SYNC.sync_ai(server, live, session="midday")
            self.assertTrue((live / SYNC.AI_READY_MARKER).exists())

            write_all_datasets(upstream, "new-upstream")
            result = SYNC.sync_upstream(upstream, live)
            self.assertTrue(result["server_market_owned"])
            self.assertTrue(result["server_ai_owned"])
            self.assertEqual(result["ai_copied"], [])
            self.assertEqual(
                json.loads(
                    (live / "market_assistant_brief.json").read_text(
                        encoding="utf-8"
                    )
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
        report_deploy = (ROOT / "scripts" / "deploy_report.sh").read_text(
            encoding="utf-8"
        )
        collector = COLLECTOR_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("server/sync_live_data.py", update_site)
        self.assertIn("compose.automation.yaml", update_site)
        self.assertIn('"$STATE_ROOT/automation.lock"', update_site)
        self.assertIn('state_root / "automation.lock"', collector)
        self.assertIn('"refresh_slot_already_published"', collector)
        self.assertIn('/ "market-runs"', collector)
        self.assertNotIn("if state_marker.exists()", collector)
        self.assertIn('["git", "fetch", "--depth", "1", "origin", "main"]', collector)
        self.assertIn('PUBLISH_MODE="${PALM_OIL_PUBLISH_MODE:-git}"', deploy)
        self.assertIn('"publish_mode": "files"', deploy)
        self.assertLess(
            deploy.index('if [[ "$PUBLISH_MODE" == "files" ]]'),
            deploy.index("git add --"),
        )
        self.assertIn('PUBLISH_MODE="${PALM_OIL_PUBLISH_MODE:-git}"', report_deploy)
        self.assertIn('REPORT_DATA_MODE="${PALM_OIL_REPORT_DATA_MODE:-refresh}"', report_deploy)
        self.assertIn('"publish_mode": "files"', report_deploy)
        self.assertIn("use prepared server-owned market datasets", report_deploy)
        self.assertIn("server/freeze_prepared_forecast.py", report_deploy)
        self.assertLess(
            report_deploy.index('if [[ "$PUBLISH_MODE" == "files" ]]'),
            report_deploy.index("git add --"),
        )


if __name__ == "__main__":
    unittest.main()

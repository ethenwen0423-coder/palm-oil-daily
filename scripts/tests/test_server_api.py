import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("palm_oil_server_api", ROOT / "server" / "api.py")
API = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(API)


class ServerApiStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data_root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_json(self, relative, payload):
        target = self.data_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def test_all_dynamic_datasets_have_routes(self):
        self.assertEqual(API.DATA_ROOT, Path("/site/data"))
        self.assertEqual(API.ROUTES["/api/exchange-futures"], "exchange_futures.json")
        self.assertEqual(API.ROUTES["/api/supply-demand"], "supply-demand.json")
        self.assertEqual(API.ROUTES["/api/reports"], "reports.json")
        self.assertEqual(API.ROUTES["/api/assistant/brief"], "market_assistant_brief.json")

    def test_server_update_runner_validates_all_mutable_payloads(self):
        runner = (ROOT / "server" / "update-site.sh").read_text(encoding="utf-8")
        for path in (
            "data/reports.json",
            "data/oil_futures.json",
            "data/exchange_futures.json",
            "data/quant_model_signals.json",
            "data/supply-demand.json",
            "data/market_assistant_brief.json",
        ):
            self.assertIn(path, runner)
        self.assertIn('cmp -s server/api.py "$DEPLOY_ROOT/api.py"', runner)
        self.assertIn('cp server/update-site.sh "$RUNNER_CANDIDATE"', runner)
        self.assertIn('mv -f "$RUNNER_CANDIDATE" "$RUNNER_PATH"', runner)
        self.assertNotIn('cp server/update-site.sh "$RUNNER_PATH"', runner)
        self.assertIn(
            'timeout "${GIT_FETCH_TIMEOUT_SECONDS}s" git fetch --depth 1 origin main',
            runner,
        )
        self.assertIn('restart api', runner)
        self.assertIn('PUBLIC_ACCESS_MODE="${PALM_OIL_PUBLIC_ACCESS_MODE:-private}"', runner)
        self.assertIn('compose exec -T api python3 -c', runner)
        self.assertIn('compose stop web || true', runner)
        self.assertIn('/api/status', runner)
        self.assertIn('while [ "$attempt" -le 10 ]', runner)

    def test_status_distinguishes_ready_stale_and_missing(self):
        now = datetime(2026, 7, 30, 14, 0, tzinfo=timezone.utc)
        self.write_json("oil_futures.json", {"updated_at": "2026-07-30 20:00"})
        self.write_json("exchange_futures.json", {"updated_at": "2026-07-28 15:05"})

        status = API.build_status(self.data_root, now=now)

        self.assertEqual(status["datasets"]["/api/oil-futures"]["state"], "ready")
        self.assertEqual(status["datasets"]["/api/exchange-futures"]["state"], "stale")
        self.assertEqual(status["datasets"]["/api/supply-demand"]["state"], "missing")
        self.assertEqual(status["status"], "degraded")

    def test_automated_dataset_stale_thresholds_surface_missed_runs(self):
        self.assertEqual(
            API.DATASET_RULES["/api/supply-demand"]["stale_after_seconds"],
            60 * 60 * 36,
        )
        self.assertEqual(
            API.DATASET_RULES["/api/contracts/current"]["stale_after_seconds"],
            60 * 60 * 72,
        )
        self.assertEqual(
            API.DATASET_RULES["/api/forecast/metrics/latest"]["stale_after_seconds"],
            60 * 60 * 96,
        )

    def test_status_exposes_automation_ownership_without_credentials(self):
        now = datetime(2026, 7, 30, 14, 0, tzinfo=timezone.utc)
        self.write_json("oil_futures.json", {"updated_at": "2026-07-30 20:00"})
        self.write_json(
            ".server-market-ready.json",
            {
                "generated_at": "2026-07-30T21:50:00+08:00",
                "session": "night_open",
                "owner": "server-market-collector",
            },
        )

        status = API.build_status(self.data_root, now=now)

        self.assertEqual(status["automation"]["market"]["state"], "ready")
        self.assertEqual(
            status["datasets"]["/api/oil-futures"]["owner"],
            "server-market-collector",
        )
        self.assertEqual(status["automation"]["supply"]["state"], "pending")
        self.assertNotIn("credential", json.dumps(status))

    def test_report_array_uses_latest_report_date(self):
        now = datetime(2026, 7, 30, 14, 0, tzinfo=timezone.utc)
        self.write_json("reports.json", [{"date": "2026-07-30"}, {"date": "2026-07-29"}])

        item = API.dataset_status(
            self.data_root,
            "/api/reports",
            "reports.json",
            now=now,
        )

        self.assertTrue(item["available"])
        self.assertEqual(item["state"], "ready")
        self.assertTrue(item["observed_at"].startswith("2026-07-30"))


if __name__ == "__main__":
    unittest.main()

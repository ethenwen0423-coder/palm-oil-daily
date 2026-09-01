import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


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
        self.assertEqual(API.ROUTES["/api/assistant/watch"], "market_watch.json")
        self.assertEqual(API.ROUTES["/api/assistant/research-watch"], "research_watch.json")
        self.assertEqual(API.ROUTES["/api/ai-daredevil"], "ai_daredevil.json")
        self.assertEqual(API.ROUTES["/api/ai-daredevil/pure-ai"], "ai_daredevil_pure_ai.json")
        self.assertEqual(
            API.ROUTES["/api/ai-daredevil/monthly-backtest"],
            "ai_daredevil_monthly_backtest.json",
        )
        self.assertEqual(
            API.ROUTES["/api/forecast/feedback/latest"],
            "forecast/feedback/latest.json",
        )
        self.assertEqual(API.ROUTES["/api/review/latest"], "review/latest_review.json")

    def test_market_watch_freshness_uses_event_scan_during_closed_market(self):
        self.assertEqual(
            API.DATASET_RULES["/api/assistant/watch"]["timestamp_fields"],
            ("events_updated_at", "generated_at"),
        )

    def test_server_update_runner_validates_all_mutable_payloads(self):
        runner = (ROOT / "server" / "update-site.sh").read_text(encoding="utf-8")
        self.assertIn('flock -w "$AUTOMATION_LOCK_WAIT_SECONDS" 9', runner)
        for path in (
            "data/reports.json",
            "data/oil_futures.json",
            "data/exchange_futures.json",
            "data/quant_model_signals.json",
            "data/supply-demand.json",
            "data/market_assistant_brief.json",
            "data/research_watch.json",
            "data/ai_daredevil.json",
            "data/ai_daredevil_monthly_backtest.json",
            "data/ai_daredevil_pure_ai.json",
            "data/forecast/metrics/20d.json",
            "data/forecast/metrics/60d.json",
            "data/forecast/feedback/latest.json",
            "data/review/latest_review.json",
        ):
            self.assertIn(path, runner)
        self.assertIn('server/api.py server/contract_analysis.py', runner)
        self.assertIn('cmp -s server/Caddyfile "$DEPLOY_ROOT/Caddyfile"', runner)
        self.assertIn('compose up -d api web', runner)
        self.assertIn('cmp -s "$api_source" "$DEPLOY_ROOT/$api_name"', runner)
        self.assertIn('cp server/update-site.sh "$RUNNER_CANDIDATE"', runner)
        self.assertIn('mv -f "$RUNNER_CANDIDATE" "$RUNNER_PATH"', runner)
        self.assertNotIn('cp server/update-site.sh "$RUNNER_PATH"', runner)
        self.assertIn(
            'timeout "${GIT_FETCH_TIMEOUT_SECONDS}s" git fetch --depth 1 origin main',
            runner,
        )
        self.assertIn('restart api', runner)
        self.assertIn('PUBLIC_ACCESS_MODE="${PALM_OIL_PUBLIC_ACCESS_MODE:-public}"', runner)
        self.assertNotIn('--mode research', runner)
        self.assertNotIn('--session upstream-report-publish', runner)
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

        self.assertEqual(status["automation"]["market"]["state"], "stale")
        self.assertIn(
            "/api/exchange-futures",
            status["automation"]["market"]["unhealthy_routes"],
        )
        self.assertEqual(
            status["datasets"]["/api/oil-futures"]["owner"],
            "server-market-collector",
        )
        self.assertEqual(status["automation"]["supply"]["state"], "pending")
        self.assertEqual(status["automation"]["research"]["state"], "pending")
        self.assertNotIn("credential", json.dumps(status))

    def test_public_payload_masks_institution_brand_names(self):
        payload = API.public_payload(
            {
                "label": "华泰天玑只读采集",
                "source": "HTFC Tianji",
                "evidence": ["htfc-news:KX1", "华泰期货研报"],
                "url": "https://www.htfc.com/",
            }
        )

        rendered = json.dumps(payload, ensure_ascii=False)
        for forbidden in ("华泰", "天玑", "HTFC", "Tianji", "htfc.com"):
            self.assertNotIn(forbidden, rendered)
        self.assertEqual(payload["label"], "机构资讯只读采集")
        self.assertEqual(payload["source"], "机构资讯数据")

    def test_research_and_review_markers_replace_upstream_ownership(self):
        now = datetime(2026, 7, 30, 14, 0, tzinfo=timezone.utc)
        self.write_json("reports.json", [{"date": "2026-07-30"}])
        self.write_json("forecast/metrics/latest.json", {"as_of": "2026-07-30"})
        self.write_json(
            ".server-research-ready.json",
            {
                "generated_at": "2026-07-30T21:55:00+08:00",
                "session": "daily",
                "owner": "server-research-agent",
            },
        )
        self.write_json(
            ".server-review-ready.json",
            {
                "generated_at": "2026-07-30T21:56:00+08:00",
                "session": "close",
                "owner": "server-prediction-review",
            },
        )

        status = API.build_status(self.data_root, now=now)

        self.assertEqual(
            status["datasets"]["/api/reports"]["owner"],
            "server-research-agent",
        )
        self.assertEqual(
            status["datasets"]["/api/forecast/metrics/latest"]["owner"],
            "server-prediction-review",
        )

    def test_upstream_publish_marker_does_not_claim_server_research_ready(self):
        now = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
        self.write_json("reports.json", [{"date": "2026-08-31"}])
        self.write_json(
            ".server-research-ready.json",
            {
                "generated_at": "2026-09-01T14:14:41+08:00",
                "session": "upstream-report-publish",
                "owner": "server-research-agent",
            },
        )

        status = API.build_status(self.data_root, now=now)

        research = status["automation"]["research"]
        self.assertEqual(research["state"], "pending")
        self.assertEqual(research["owner"], "upstream-sync")
        self.assertEqual(research["reason"], "server-generation-not-verified")
        self.assertEqual(
            status["datasets"]["/api/reports"]["owner"],
            "upstream-sync",
        )

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

    def test_contract_analysis_is_cached_by_selected_symbol(self):
        class FakeModule:
            calls = []

            @classmethod
            def analyze_contract(cls, data_root, symbol):
                cls.calls.append((data_root, symbol))
                return {"symbol": symbol, "contract": {"symbol": symbol}}

        API._CONTRACT_ANALYSIS_CACHE.clear()
        with patch.object(API, "_load_contract_analysis_module", return_value=FakeModule):
            first = API.contract_analysis(self.data_root, "p2701")
            second = API.contract_analysis(self.data_root, "P2701")

        self.assertEqual(first["cache"], "miss")
        self.assertEqual(second["cache"], "hit")
        self.assertEqual(FakeModule.calls, [(self.data_root, "P2701")])


if __name__ == "__main__":
    unittest.main()

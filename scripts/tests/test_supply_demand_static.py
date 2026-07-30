import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SupplyDemandStaticTests(unittest.TestCase):
    def test_page_references_existing_assets(self):
        html = (ROOT / "supply-demand.html").read_text(encoding="utf-8")
        self.assertIn('href="assets/styles.css?v=', html)
        self.assertIn('src="assets/supply-demand.js?v=', html)
        self.assertTrue((ROOT / "assets" / "styles.css").is_file())
        self.assertTrue((ROOT / "assets" / "supply-demand.js").is_file())
        script = (ROOT / "assets" / "supply-demand.js").read_text(encoding="utf-8")
        self.assertIn('API_URL = "/api/supply-demand"', script)
        self.assertIn('STATIC_DATA_URL = "data/supply-demand.json"', script)
        self.assertIn("POLL_INTERVAL_MS = 300000", script)

    def test_public_json_has_six_metrics_and_valid_sources(self):
        payload = json.loads((ROOT / "data" / "supply-demand.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 3)
        self.assertIn(payload["update_status"], {"updated", "no_change", "source_error"})
        self.assertTrue(payload["update_message"])
        self.assertTrue(payload["checked_at"])
        self.assertTrue(payload["checked_for_report_date"])
        self.assertEqual(set(payload["countries"]), {"malaysia", "indonesia"})
        for country in payload["countries"].values():
            self.assertEqual(set(country["metrics"]), {"production", "exports", "stocks"})
            for metric in country["metrics"].values():
                self.assertTrue(metric["series"])
                self.assertTrue(all(item["source_url"].startswith("https://") for item in metric["series"]))
        supplemental = payload["supplemental"]
        self.assertTrue(supplemental["global_balance"]["series"])
        generated_year = int(payload["generated_at"][:4])
        latest_global_year = int(
            supplemental["global_balance"]["series"][-1]["market_year"][:4]
        )
        self.assertLessEqual(latest_global_year, generated_year - 1)
        self.assertEqual(
            {item["key"] for item in supplemental["import_demand"]["markets"]},
            {"india", "china", "eu", "pakistan"},
        )
        self.assertEqual(
            {item["key"] for item in supplemental["vegetable_oils"]["oils"]},
            {"palm", "soybean", "rapeseed", "sunflower"},
        )

    def test_navigation_links_to_supply_demand_page(self):
        for filename in ("index.html", "reports.html", "oil-futures.html", "futures.html"):
            html = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn('href="supply-demand.html"', html, filename)

    def test_automation_follows_daily_report_and_uses_strict_allowlist(self):
        deploy = (ROOT / "scripts" / "deploy_supply_demand_data.sh").read_text(encoding="utf-8")
        installer = (ROOT / "scripts" / "install_daily_watchdog_launchd.sh").read_text(encoding="utf-8")
        self.assertIn('TARGET="data/supply-demand.json"', deploy)
        self.assertIn('changed_path" != "$TARGET', deploy)
        self.assertNotIn("deploy_report.sh", deploy)
        self.assertIn("$REPORT_DATE-supply-demand.ok", installer)
        self.assertIn('refresh_supply_demand', installer)
        self.assertIn("supply-demand checked with daily report", installer)
        self.assertNotIn("com.vinsontesla.palm-oil-supply-demand", installer)

    def test_exchange_futures_has_json_api_payload_and_deploy_allowlist(self):
        wrapped = (ROOT / "data" / "exchange_futures.js").read_text(encoding="utf-8")
        wrapped_payload = json.loads(wrapped.split("=", 1)[1].strip().removesuffix(";"))
        json_payload = json.loads((ROOT / "data" / "exchange_futures.json").read_text(encoding="utf-8"))
        self.assertEqual(json_payload, wrapped_payload)
        deploy = (ROOT / "scripts" / "deploy_oil_futures_tab.sh").read_text(encoding="utf-8")
        self.assertIn("data/exchange_futures.json", deploy)
        self.assertIn("EXCHANGE_JSON_TMP", deploy)


if __name__ == "__main__":
    unittest.main()

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

    def test_public_json_has_six_metrics_and_valid_sources(self):
        payload = json.loads((ROOT / "data" / "supply-demand.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 2)
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

    def test_automation_is_independent_and_uses_strict_allowlist(self):
        deploy = (ROOT / "scripts" / "deploy_supply_demand_data.sh").read_text(encoding="utf-8")
        installer = (ROOT / "scripts" / "install_supply_demand_launchd.sh").read_text(encoding="utf-8")
        self.assertIn('TARGET="data/supply-demand.json"', deploy)
        self.assertIn('changed_path" != "$TARGET', deploy)
        self.assertNotIn("deploy_report.sh", deploy)
        self.assertIn("<integer>13</integer>", installer)
        self.assertIn("<integer>15</integer>", installer)
        self.assertIn("status --porcelain", installer)
        self.assertIn("pull --ff-only", installer)


if __name__ == "__main__":
    unittest.main()

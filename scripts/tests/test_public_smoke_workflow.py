import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PublicSmokeWorkflowTests(unittest.TestCase):
    def test_workflow_checks_public_assistant_and_all_dynamic_routes(self):
        workflow = (ROOT / ".github" / "workflows" / "public-smoke.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('cron: "*/15 * * * *"', workflow)
        self.assertIn("https://palm.vinsontesla.com", workflow)
        self.assertIn('"$SITE_URL/api/status"', workflow)
        self.assertIn('"$SITE_URL/assistant"', workflow)
        self.assertIn("%{redirect_url}", workflow)
        for route in (
            "/api/reports",
            "/api/oil-futures",
            "/api/exchange-futures",
            "/api/quant-model-signals",
            "/api/supply-demand",
            "/api/contracts/current",
            "/api/forecast/metrics/latest",
        ):
            self.assertIn(f'"{route}"', workflow)
        self.assertIn('{"missing", "invalid"}', workflow)


if __name__ == "__main__":
    unittest.main()

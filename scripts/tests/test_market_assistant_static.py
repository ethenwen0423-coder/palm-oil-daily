import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class MarketAssistantStaticTests(unittest.TestCase):
    def test_assistant_page_has_live_sections_and_existing_assets(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("24h 盯盘助手", html)
        self.assertIn('id="monitor-data-health"', html)
        self.assertIn('id="monitor-report-headline"', html)
        self.assertIn('id="monitor-oil-list"', html)
        self.assertIn('id="monitor-gainers"', html)
        self.assertIn('id="monitor-supply-message"', html)
        self.assertIn('id="monitor-forecast-status"', html)
        self.assertTrue((ROOT / "assets" / "market-assistant.css").is_file())
        self.assertTrue((ROOT / "assets" / "market-assistant.js").is_file())

    def test_assistant_reads_all_mutable_information_from_api_with_fallbacks(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        expected = (
            ("/api/reports", "data/reports.json"),
            ("/api/oil-futures", "data/oil_futures.json"),
            ("/api/exchange-futures", "data/exchange_futures.json"),
            ("/api/supply-demand", "data/supply-demand.json"),
            ("/api/forecast/metrics/latest", "data/forecast/metrics/latest.json"),
        )
        for api, fallback in expected:
            with self.subTest(api=api):
                self.assertIn(f'"{api}"', script)
                self.assertIn(f'"{fallback}"', script)
        self.assertIn('fetchJson("/api/status")', script)
        self.assertIn("POLL_INTERVAL_MS = 60000", script)

    def test_assistant_preserves_fixed_logic_boundary(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("场外结构类型与量化模型规则保持版本化固定", html)
        self.assertIn("过期或缺失数据会明确标记", html)

    def test_home_page_links_to_assistant(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(html.count('href="assistant.html"'), 2)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class MarketAssistantStaticTests(unittest.TestCase):
    def test_assistant_page_has_live_sections_and_existing_assets(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("24h 盯盘助手", html)
        self.assertIn('id="decision-title"', html)
        self.assertIn('id="priority-list"', html)
        self.assertIn('id="market-pulse"', html)
        self.assertIn('id="oil-desk-grid"', html)
        self.assertIn('id="supply-desk-grid"', html)
        self.assertIn('id="assistant-contract-result"', html)
        self.assertIn('id="intelligence-timeline"', html)
        self.assertIn('id="dataset-status-list"', html)
        self.assertTrue((ROOT / "assets" / "market-assistant.css").is_file())
        self.assertTrue((ROOT / "assets" / "market-assistant.js").is_file())

    def test_assistant_reads_all_mutable_information_from_api_with_fallbacks(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        expected = (
            ("/api/reports", "data/reports.json"),
            ("/api/oil-futures", "data/oil_futures.json"),
            ("/api/exchange-futures", "data/exchange_futures.json"),
            ("/api/supply-demand", "data/supply-demand.json"),
            ("/api/assistant/brief", "data/market_assistant_brief.json"),
        )
        for api, fallback in expected:
            with self.subTest(api=api):
                self.assertIn(f'"{api}"', script)
                self.assertIn(f'"{fallback}"', script)
        self.assertIn('status: ["/api/status"]', script)
        self.assertIn("setInterval(load, 60000)", script)
        self.assertIn("payload.automation", script)

    def test_assistant_preserves_fixed_logic_boundary(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("不修改场外结构与量化模型规则", html)
        self.assertIn("缺失或过期数据会明确标注", html)

    def test_home_page_links_to_assistant(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(html.count('href="/assistant"'), 2)


if __name__ == "__main__":
    unittest.main()

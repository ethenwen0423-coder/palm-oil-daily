import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReportsNavigationStaticTests(unittest.TestCase):
    def test_report_detail_renders_governed_driver_sections(self):
        script = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn('"核心驱动与预期差"', script)
        self.assertIn('"本周验证与预期差"', script)

    def test_reports_page_exposes_current_clean_shortcuts(self):
        html = (ROOT / "reports.html").read_text(encoding="utf-8")
        expected_links = {
            "历史报告": "/reports",
            "24h 盯盘助手": "/assistant",
        }

        for label, target in expected_links.items():
            with self.subTest(label=label):
                self.assertIn(f'href="{target}">{label}</a>', html)

        self.assertNotIn('href="oil-futures.html"', html)
        self.assertNotIn('href="supply-demand.html"', html)
        self.assertNotIn('href="futures.html"', html)
        self.assertNotIn('href="quant-model.html"', html)


if __name__ == "__main__":
    unittest.main()

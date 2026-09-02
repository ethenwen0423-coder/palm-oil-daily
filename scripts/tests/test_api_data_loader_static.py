import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ApiDataLoaderStaticTests(unittest.TestCase):
    PAGE_CONFIGS = {
        "index.html": (
            "/api/reports",
            "PALM_OIL_REPORTS",
            "data/reports.js",
            "assets/app.js",
        ),
        "reports.html": (
            "/api/reports",
            "PALM_OIL_REPORTS",
            "data/reports.js",
            "assets/app.js",
        ),
        "report.html": (
            "/api/reports",
            "PALM_OIL_REPORTS",
            "data/reports.js",
            "assets/app.js",
        ),
        "otc-structure.html": (
            "/api/oil-futures",
            "OIL_FUTURES_CONTRACTS",
            "data/oil_futures.js",
            "assets/otc-structure.js",
        ),
        "quant-model-detail.html": (
            "/api/quant-model-signals",
            "QUANT_MODEL_SIGNALS",
            "data/quant_model_signals.js",
            "assets/quant-model-detail.js",
        ),
    }

    def test_market_pages_use_api_loader_with_static_fallback(self):
        for filename, expected_values in self.PAGE_CONFIGS.items():
            with self.subTest(filename=filename):
                html = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn('src="assets/api-data-loader.js?v=20260730-api2"', html)
                self.assertIn("window.PalmOilDataLoader.boot({", html)
                self.assertIn("pollIntervalMs: 60000", html)
                for value in expected_values:
                    self.assertIn(f'"{value}"', html)
                if "assets/app.js" in expected_values:
                    self.assertIn("-20260903-attribution", html)

    def test_market_pages_no_longer_document_write_data_scripts(self):
        pattern = re.compile(
            r"document\.write\([^)]*data/(?:oil_futures|quant_model_signals|reports|exchange_futures)\.js",
            re.DOTALL,
        )
        for filename in self.PAGE_CONFIGS:
            with self.subTest(filename=filename):
                html = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIsNone(pattern.search(html))

    def test_loader_exposes_api_first_and_static_fallback_states(self):
        loader = (ROOT / "assets/api-data-loader.js").read_text(encoding="utf-8")
        self.assertIn('cache: "no-store"', loader)
        self.assertIn('credentials: "same-origin"', loader)
        self.assertIn('source = "static"', loader)
        self.assertIn('source: "error"', loader)
        self.assertIn("document.documentElement.dataset.marketDataSource", loader)
        self.assertIn("await loadScript(consumerSrc", loader)
        self.assertIn("scheduleRefresh(", loader)
        self.assertNotIn("Array.isArray(payload))", loader)


if __name__ == "__main__":
    unittest.main()

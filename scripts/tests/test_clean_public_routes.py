import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CleanPublicRoutesTests(unittest.TestCase):
    def test_caddy_serves_clean_routes_and_redirects_legacy_html(self):
        caddy = (ROOT / "server" / "Caddyfile").read_text(encoding="utf-8")
        self.assertIn("@reportDownloads path_regexp reportDownload", caddy)
        self.assertIn("reverse_proxy @reportDownloads api:8000", caddy)
        self.assertIn("@reportAssets path /data/reports.js /data/version.js", caddy)
        self.assertIn("reverse_proxy @reportAssets api:8000", caddy)
        mappings = {
            "/assistant.html": "/assistant",
            "/reports.html": "/reports",
            "/report.html": "/report",
            "/otc-structure.html": "/otc-structure",
            "/otc-structure-library.html": "/otc-structure/library",
        }
        for legacy, clean in mappings.items():
            self.assertIn(f"redir {legacy} {clean} 308", caddy)
        for clean, physical in (
            ("/assistant", "/assistant.html"),
            ("/reports", "/reports.html"),
            ("/report", "/report.html"),
            ("/otc-structure", "/otc-structure.html"),
            ("/otc-structure/library", "/otc-structure-library.html"),
        ):
            self.assertIn(f"rewrite {clean} {physical}", caddy)

    def test_active_pages_do_not_link_to_html_urls(self):
        files = (
            "index.html",
            "assistant.html",
            "reports.html",
            "report.html",
            "otc-structure.html",
            "otc-structure-library.html",
            "assets/app.js",
            "assets/market-assistant.js",
        )
        pattern = re.compile(r"(?:href=|location(?:\.href)?\s*=)[^\n>]*\.html")
        for relative in files:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIsNone(pattern.search(text), relative)


if __name__ == "__main__":
    unittest.main()

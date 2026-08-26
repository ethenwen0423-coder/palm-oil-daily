import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SiteBrandingTests(unittest.TestCase):
    def test_public_pages_use_oils_intelligence_brand(self):
        for relative in ("index.html", "reports.html", "report.html"):
            with self.subTest(relative=relative):
                html = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("Oils Intelligence", html)
                self.assertNotIn("Palm Oil Intelligence", html)

    def test_home_positioning_covers_the_oils_sector(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("专业油脂板块研究", html)
        self.assertIn("棕榈油、豆油与菜油", html)
        self.assertIn("assets/og-oils-intelligence.png", html)
        self.assertTrue((ROOT / "assets" / "og-oils-intelligence.png").is_file())

    def test_miniprogram_uses_the_same_brand_scope(self):
        home = (ROOT / "miniprogram/pages/home/home.wxml").read_text(encoding="utf-8")
        navigation = (ROOT / "miniprogram/pages/home/home.json").read_text(encoding="utf-8")
        self.assertIn("Oils Intelligence", home)
        self.assertIn("专业油脂板块研究", home)
        self.assertIn("油脂板块研究", navigation)


if __name__ == "__main__":
    unittest.main()

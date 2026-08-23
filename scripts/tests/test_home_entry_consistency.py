import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class HomeEntryConsistencyTests(unittest.TestCase):
    def test_all_hero_links_share_one_visual_component(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        block = re.search(r'<div class="hero-actions"[^>]*>(.*?)</div>', html, re.S)
        self.assertIsNotNone(block)
        links = re.findall(r'<a\b([^>]*)>(.*?)</a>', block.group(1), re.S)

        self.assertEqual(4, len(links))
        for attributes, content in links:
            self.assertRegex(attributes, r'class="hero-button"')
            self.assertNotIn("hero-button-option", attributes)
            self.assertNotIn("hero-button-secondary", attributes)
            self.assertEqual(1, content.count('class="hero-button-icon"'))
            self.assertIn('src="assets/iconoir-arrow-right.svg"', content)
            self.assertNotRegex(content, r"[→↗]")

    def test_shared_style_and_icon_asset_exist(self):
        css = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
        icon = ROOT / "assets" / "iconoir-arrow-right.svg"

        self.assertIn(".hero-actions .hero-button {", css)
        self.assertIn("background: rgba(244, 248, 242, .035);", css)
        self.assertIn(".hero-button-icon {", css)
        self.assertTrue(icon.is_file())


if __name__ == "__main__":
    unittest.main()

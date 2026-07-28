import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReportsNavigationStaticTests(unittest.TestCase):
    def test_reports_page_exposes_all_primary_shortcuts(self):
        html = (ROOT / "reports.html").read_text(encoding="utf-8")
        expected_links = {
            "历史报告": "reports.html",
            "油脂主力": "oil-futures.html",
            "供需数据": "supply-demand.html",
            "全品种分析": "futures.html",
            "量化模型": "quant-model.html",
            "场外结构": "otc-structure.html",
        }

        for label, target in expected_links.items():
            with self.subTest(label=label):
                self.assertIn(f'href="{target}">{label}</a>', html)
                self.assertTrue((ROOT / target).is_file(), target)


if __name__ == "__main__":
    unittest.main()

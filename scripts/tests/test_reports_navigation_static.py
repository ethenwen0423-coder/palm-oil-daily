import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReportsNavigationStaticTests(unittest.TestCase):
    def test_report_detail_renders_every_markdown_section_in_source_order(self):
        script = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn('return String(value == null ? "" : value);', script)
        self.assertNotIn(".replace(/华泰期货/g", script)
        self.assertIn("const visibleSections = sections.length", script)
        self.assertIn("visibleSections\n      .map((section, index)", script)
        self.assertNotIn("const used = new Set()", script)

        required_sections = (
            "今日观点",
            "今日交易信号",
            "核心驱动与预期差",
            "关键数据与价格",
            "开盘推演",
            "一句话核心观点",
            "本周验证与预期差",
            "核心数据变化",
            "下周主线与事件",
            "周一开盘推演",
            "交易计划",
            "风险提示",
            "信息来源与核验说明",
            "消息来源链接",
            "AI观点风险提示",
        )
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(f'["{section}",', script)

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

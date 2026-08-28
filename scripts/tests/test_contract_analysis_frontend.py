import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ContractAnalysisFrontendTests(unittest.TestCase):
    def test_selected_contract_is_sent_to_backend_and_static_result_is_not_silently_used(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        self.assertIn("/api/assistant/contract-analysis?symbol=", script)
        self.assertIn("encodeURIComponent(symbol)", script)
        self.assertIn("正在按 ${esc(symbol)} 请求后台", script)
        self.assertIn("本次不自动展示旧的静态结论", script)

    def test_result_discloses_judgement_and_source_status(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        style = (ROOT / "assets" / "market-assistant.css").read_text(encoding="utf-8")
        self.assertIn("后台综合判断", script)
        self.assertIn("本次来源状态", script)
        self.assertIn("sourceState", script)
        self.assertIn(".contract-judgement", style)
        self.assertIn(".contract-sources", style)

    def test_asset_version_was_bumped(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("market-assistant.css?v=20260828-supply-detail-v1", html)
        self.assertIn("market-assistant.js?v=20260828-supply-detail-v1", html)

    def test_timeline_uses_full_width_with_readable_desktop_type(self):
        style = (ROOT / "assets" / "market-assistant.css").read_text(encoding="utf-8")
        self.assertIn(".assistant-page .workspace {\n  grid-template-columns: minmax(0, 1fr);", style)
        self.assertIn(".assistant-page .right-rail { grid-template-columns: repeat(3, minmax(0, 1fr));", style)
        self.assertIn(".assistant-page .timeline-content h3 { font-size: 15px; }", style)
        self.assertIn(".assistant-page .timeline-content p { margin-top: 6px; font-size: 11px;", style)

    def test_assistant_navigation_has_one_scroll_tracked_current_section(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        style = (ROOT / "assets" / "market-assistant.css").read_text(encoding="utf-8")
        self.assertIn("function bindSectionNavigation()", script)
        self.assertIn('link.setAttribute("aria-current", "location")', script)
        self.assertIn('else link.removeAttribute("aria-current")', script)
        self.assertIn("reachedBottom", script)
        self.assertIn('a[aria-current="location"]', style)

    def test_brand_keeps_normal_case_and_readable_spacing(self):
        style = (ROOT / "assets" / "market-assistant.css").read_text(encoding="utf-8")
        self.assertIn("text-transform: none", style)
        self.assertIn("font: 700 15px/1.35", style)
        self.assertIn("letter-spacing: .01em", style)
        self.assertIn("backdrop-filter: none", style)


if __name__ == "__main__":
    unittest.main()

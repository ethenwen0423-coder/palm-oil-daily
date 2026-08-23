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
        self.assertIn("market-assistant.css?v=20260823-1", html)
        self.assertIn("market-assistant.js?v=20260823-1", html)


if __name__ == "__main__":
    unittest.main()

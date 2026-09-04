import unittest
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[2]


class MarketAssistantStaticTests(unittest.TestCase):
    def test_assistant_page_has_live_sections_and_existing_assets(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("24h 盯盘助手", html)
        self.assertIn('id="decision-title"', html)
        self.assertIn('id="sector-view-grid"', html)
        self.assertIn('id="priority-list"', html)
        self.assertIn('id="market-pulse"', html)
        self.assertIn('id="oil-desk-grid"', html)
        self.assertIn('id="supply-desk-grid"', html)
        self.assertIn('id="assistant-contract-result"', html)
        self.assertIn('id="intelligence-timeline"', html)
        self.assertIn('id="dataset-status-list"', html)
        self.assertIn('id="data-chain-details"', html)
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
            ("/api/assistant/research-watch", "data/research_watch.json"),
        )
        for api, fallback in expected:
            with self.subTest(api=api):
                self.assertIn(f'"{api}"', script)
                self.assertIn(f'"{fallback}"', script)
        self.assertIn('status: ["/api/status"]', script)
        self.assertIn("setInterval(load, 60000)", script)
        self.assertIn("payload.automation", script)
        self.assertIn("renderSectorViews(data.brief || {}, data)", script)
        self.assertIn('class="sector-view-toggle"', script)
        self.assertIn('aria-expanded="${expanded}"', script)
        self.assertIn("sectorEvidenceDetails(item.evidence)", script)
        self.assertNotIn('sector-view-card ${stateClass}\"><a', script)
        self.assertIn("const sectorGroups", script)
        self.assertIn("renderPulse(data.oil || {}, data.watch || {})", script)
        self.assertIn('live ? "盘中行情" : "行情快照"', script)
        self.assertIn("const publicText", script)
        self.assertIn('const publicText = (value) => String(value == null ? "" : value);', script)
        self.assertNotIn(".replace(/华泰期货/g", script)

    def test_data_chain_status_expands_specific_abnormal_datasets(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        self.assertIn('aria-controls="data-chain-details"', html)
        self.assertIn("const abnormalDatasets = datasets.filter", script)
        self.assertIn("item.label, item.route", script)
        self.assertIn("bindDataChainDetails()", script)
        self.assertIn('event.key === "Escape"', script)

    def test_assistant_preserves_fixed_logic_boundary(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("不修改场外结构与量化模型规则", html)
        self.assertIn("缺失或过期数据会明确标注", html)

    def test_timeline_contains_published_evidence_not_browser_heartbeats(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn("function eventEvidence(item)", script)
        self.assertNotIn('category: "数据巡检"', script)
        self.assertNotIn('category: "休市心跳"', script)
        self.assertNotIn('category: "监控心跳"', script)
        self.assertNotIn("array(data.brief.actions).forEach", script)
        self.assertIn('watch: ["/api/assistant/watch", "data/market_watch.json"]', script)
        self.assertIn("data.watch.events_updated_at || data.watch.generated_at", script)
        self.assertNotIn('data-filter="event"', html)
        self.assertNotIn('data-filter="agent"', html)
        self.assertIn("completeTimelineSummary", script)
        self.assertIn("item.detail_summary", script)
        self.assertIn('class="timeline-detail-summary"', script)
        self.assertIn("未提供可直接打开的原文链接", script)
        self.assertIn("item.aiNotice", script)
        self.assertIn("事情经过", script)
        self.assertIn("背景与变化", script)
        self.assertIn("关键事实与数字", script)
        self.assertIn("影响是怎么传导的", script)
        self.assertIn("对油脂意味着什么", script)
        self.assertIn("接下来要看什么", script)
        self.assertIn("证据边界", script)
        self.assertIn("first(item.summary, completeTimelineSummary", script)

    def test_timeline_has_granular_filters_and_weather_classifier(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        for category in ("weather", "policy", "industry", "macro", "report", "supply"):
            self.assertIn(f'data-filter="{category}"', html)
        self.assertIn("function eventTimelineType(item)", script)
        self.assertIn('weather: "天气"', script)
        self.assertIn('class="timeline-ai-notice"', script)
        self.assertIn("market-assistant.js?v=20260904-research-diversity", html)
        self.assertIn("market-assistant.css?v=20260901-event-summary-v4", html)
        self.assertIn("function weatherDetailHtml", script)
        self.assertIn("产量因果链", script)
        self.assertIn("行情传导", script)
        self.assertIn("判断边界", script)

    def test_supply_timeline_expands_monthly_and_historical_comparisons(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        styles = (ROOT / "assets" / "market-assistant.css").read_text(encoding="utf-8")
        self.assertIn("function supplyDetailHtml", script)
        self.assertIn("产地月度变化", script)
        self.assertIn("全球年度对比", script)
        self.assertIn("主要进口市场", script)
        self.assertIn("同月历史", script)
        self.assertIn("环比、同比及历史比较由页面按所列官方数据序列自动计算", script)
        self.assertIn('item.type === "supply" ? supplyDetailHtml(item)', script)
        self.assertIn(".supply-detail-scroll", styles)

    def test_research_reports_show_original_links_and_untruncated_source_summary_notice(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        builder = (ROOT / "scripts" / "build_research_watch.py").read_text(encoding="utf-8")
        self.assertIn("查看原始研报", script)
        self.assertIn('target="_blank" rel="noopener noreferrer"', script)
        self.assertIn("未按字数截断", script)
        self.assertIn("item.summary_notice", script)
        self.assertNotIn('.strip()[:240]', builder)

    def test_research_reports_use_two_level_reading_view(self):
        script = (ROOT / "assets" / "market-assistant.js").read_text(encoding="utf-8")
        styles = (ROOT / "assets" / "market-assistant.css").read_text(encoding="utf-8")
        builder = (ROOT / "scripts" / "build_research_watch.py").read_text(encoding="utf-8")
        self.assertIn('"schema_version": 6', builder)
        self.assertIn('"mx-search"', builder)
        self.assertIn('["ready", "stale"].includes(data.researchWatch.status)', script)
        self.assertIn("reading_view", builder)
        self.assertIn("function fallbackResearchReading", script)
        self.assertIn('class="research-quick-points"', script)
        self.assertIn('class="research-reading-detail"', script)
        self.assertIn('class="research-source-summary"', script)
        self.assertIn("查看完整来源摘要", script)
        self.assertIn("AI 自我总结", script)
        self.assertIn("查看用于总结的来源片段", script)
        self.assertIn(".research-quick-points", styles)
        quick_style = styles.split(".research-quick-points em", 1)[1].split("}", 1)[0]
        self.assertNotIn("line-clamp", quick_style)

    def test_home_page_links_to_assistant(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(html.count('href="/assistant"'), 2)

    def test_assistant_fragment_links_resolve_on_the_assistant_route(self):
        html = (ROOT / "assistant.html").read_text(encoding="utf-8")
        self.assertIn('<base href="/assistant" />', html)
        for fragment in (
            "#assistant-overview",
            "#oil-desk",
            "#supply-desk",
            "#all-contracts",
            "#intelligence-workspace",
            "#system-status",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(f'href="{fragment}"', html)
                self.assertEqual(
                    urljoin("https://palm.vinsontesla.com/assistant", fragment),
                    f"https://palm.vinsontesla.com/assistant{fragment}",
                )


if __name__ == "__main__":
    unittest.main()

import importlib.util
import io
import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


WATCH = load("event_watch_base_test", ROOT / "server" / "market_watch.py")
EVENTS = load("event_watch_test", ROOT / "server" / "event_watch.py")
RUNNER = load("event_watch_runner_test", ROOT / "server" / "run_event_watch.py")


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self):
        return self.payload


class EventWatchTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 26, 10, 5, tzinfo=WATCH.SHANGHAI)

    def test_htfc_flash_uses_exact_oil_tag_and_preserves_source_fields(self):
        payload = {"data": [{
            "id": "KX1", "title": "印尼棕榈油出口更新", "content": "GAPKI 发布数据",
            "date": "2026-08-26", "time": "10:04", "tag": "tags150",
            "tagName": "油脂油料", "type": "鹰眼", "stars": 3,
        }]}
        with patch.object(EVENTS, "request_json", return_value=payload) as request:
            events, source = EVENTS.htfc_flash_events(WATCH, "https://example.test", "key", self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(events[0]["source_fields"]["tag"], "tags150")
        self.assertIn("tags=tags150", request.call_args.args[0])
        self.assertEqual(request.call_args.kwargs["headers"], {"apikey": "key"})

    def test_long_flash_uses_complete_preview_and_expanded_detail_without_hard_cutoff(self):
        body = "【美国中西部天气更新】第一段说明降雨分散。" + "中部产区天气系统继续东移。" * 12 + "最后一段说明大豆影响仍需核验。"
        event = EVENTS.normalize_event(
            WATCH,
            prefix="htfc-flash",
            source="机构资讯·油脂油料快讯",
            title="美国中西部天气更新",
            summary=body,
            observed_at=self.now.isoformat(),
            source_id="KX-long",
        )
        self.assertIsNotNone(event)
        self.assertTrue(event["summary"].endswith("。"))
        self.assertLess(len(event["summary"]), len(body))
        self.assertTrue(event["detail_summary"].endswith("。"))
        self.assertGreater(len(event["detail_summary"]), len(event["summary"]))
        self.assertFalse(event["direct_source_available"])
        self.assertIn("不代表来源方官方立场", event["ai_notice"])

    def test_sentence_digest_falls_back_to_complete_title_instead_of_partial_body(self):
        preview, detail = WATCH.summarize_source_event("棕榈油出口变化", "这是一个没有句号且非常长的来源片段" * 30)
        self.assertEqual(preview, "棕榈油出口变化。")
        self.assertEqual(detail, preview)

    def test_model_summary_replaces_question_title_and_private_source_text(self):
        event = EVENTS.normalize_event(
            WATCH,
            prefix="web-news",
            source="跨站新闻·Google News",
            title="史上最强厄尔尼诺逼近？巴克莱：棕榈油或上涨30%",
            summary="巴克莱讨论厄尔尼诺天气风险，并提出棕榈油价格在18个月内可能上涨30%。",
            observed_at=self.now.isoformat(),
            source_id="summary-one",
        )
        event["source_content_level"] = "full_article"

        class Backend:
            @staticmethod
            def request_json(**_kwargs):
                return ({"events": [{
                    "id": event["id"],
                    "headline": "巴克莱警示厄尔尼诺或推高棕榈油价格",
                    "summary": "巴克莱把潜在厄尔尼诺天气风险与棕榈油价格上涨联系起来，并给出18个月的观察窗口。该判断针对未来供应扰动和价格风险情景，不代表产量已经下降或涨幅已经实现，仍需用后续天气和产量数据验证。",
                    "detail_summary": "巴克莱讨论厄尔尼诺可能影响棕榈油市场，并提出价格在18个月内上涨30%的可能情景。机构把天气异常与东南亚棕榈油产区的降雨风险联系起来。相关判断描述的是未来供应可能受到扰动，并不是已经发生的减产。报告给出的观察窗口为18个月。价格涨幅属于情景预测，不是已经实现的市场事实。来源摘要仍未披露完整模型参数和测算过程，需要查看原文并用后续天气与产量数据核验。",
                    "background": "报告关注潜在厄尔尼诺从气候变量向农产品供应传导的可能性。巴克莱将东南亚棕榈油产区列为需要观察的区域，并给出中期风险窗口。",
                    "event_facts": ["预测窗口为18个月。", "预测涨幅为30%。", "判断属于机构情景预测。"],
                    "transmission_chain": "AI解释：厄尔尼诺可能改变东南亚降雨分布，进而影响油棕单产和棕榈油供应预期；如果产量数据确认供应收紧，风险溢价才可能传导到P。",
                    "market_relevance": "若天气冲击产量，棕榈油供应预期可能收紧。",
                    "what_to_watch": ["后续降雨与干旱监测。", "MPOB与GAPKI产量数据。"],
                    "uncertainty": "来源摘要未披露测算依据。",
                    "publishable": True,
                }]}, "mock-model")

        events, source = RUNNER.summarize_events(Backend, [event], {})
        self.assertEqual(source["state"], "ready")
        self.assertNotRegex(events[0]["title"], r"[?？…]")
        self.assertEqual(events[0]["summary_method"], "model")
        self.assertEqual(events[0]["summary_version"], 3)
        self.assertEqual(len(events[0]["event_facts"]), 3)
        self.assertIn("厄尔尼诺", events[0]["background"])
        self.assertEqual(len(events[0]["what_to_watch"]), 2)
        self.assertGreater(len(events[0]["detail_summary"]), len(events[0]["summary"]))
        self.assertNotIn("_source_title", events[0])
        self.assertNotIn("_source_summary", events[0])
        self.assertIn("来源标题：", events[0]["evidence"][0])

    def test_sparse_cross_source_event_is_withheld_without_model_fallback(self):
        event = EVENTS.normalize_event(
            WATCH,
            prefix="web-news",
            source="跨站新闻·Google News",
            title="棕榈油会大涨吗？",
            summary="棕榈油会大涨吗？",
            observed_at=self.now.isoformat(),
            source_id="sparse-one",
        )

        class Backend:
            @staticmethod
            def request_json(**_kwargs):
                raise RuntimeError("offline")

        events, source = RUNNER.summarize_events(Backend, [event], {})
        self.assertEqual(source["state"], "ready")
        self.assertEqual(events, [])

    def test_eastmoney_article_html_exposes_complete_weekly_view(self):
        article = '<p>每周棕榈油期货盘后笔记</p><p>周线和日线均为上涨ABC模型。</p><p>四小时、两小时和十五分钟周期也保留上涨结构。</p><p>周一观望，周二偏弱，周三与周四震荡。</p><p>周五日盘震荡上行。</p><p>作者说明窄幅震荡时应多看少动。</p>'
        document = f'<script>var articleTxt = {json.dumps(article, ensure_ascii=False)};</script>'
        text = EVENTS.extract_article_text(document)
        self.assertIn("周线和日线均为上涨ABC模型", text)
        self.assertIn("周五日盘震荡上行", text)

    def test_unpublishable_title_only_event_is_removed(self):
        event = EVENTS.normalize_event(
            WATCH,
            prefix="web-news",
            source="跨站新闻·Google News",
            title="棕榈油每周笔记",
            summary="棕榈油每周笔记",
            observed_at=self.now.isoformat(),
            source_id="empty-note",
        )
        event["source_content_level"] = "full_article"

        class Backend:
            @staticmethod
            def request_json(**_kwargs):
                return ({"events": [{
                    "id": event["id"], "headline": "棕榈油每周笔记内容不足",
                    "summary": "来源只显示文章标题。", "detail_summary": "来源未提供可复述的观点或事实。",
                    "background": "来源未提供足够背景，无法确认此前状态与本次变化。",
                    "event_facts": [], "transmission_chain": "AI解释：现有信息不足，无法建立事件到油脂市场的传导路径。", "market_relevance": "暂无可判断的信息价值。",
                    "what_to_watch": ["等待取得正文。", "寻找第二来源。"],
                    "uncertainty": "未取得正文。", "publishable": False,
                }]}, "mock-model")

        events, _source = RUNNER.summarize_events(Backend, [event], {})
        self.assertEqual(events, [])

    def test_cross_source_without_article_is_withheld_before_model_call(self):
        event = EVENTS.normalize_event(
            WATCH,
            prefix="web-news",
            source="跨站新闻·Google News",
            title="煤、镍、棕榈油告急：印尼的黑天鹅为何成群起飞？",
            summary="潮起网发布同名文章",
            observed_at=self.now.isoformat(),
            source_id="title-only-google",
        )
        event["source_content_level"] = "source_summary"

        class Backend:
            @staticmethod
            def request_json(**_kwargs):
                raise AssertionError("title-only cross-source items must not reach the model")

        events, source = RUNNER.summarize_events(Backend, [event], {})
        self.assertEqual(events, [])
        self.assertEqual(source["state"], "ready")

    def test_summary_headline_quality_gate_rejects_clickbait_and_trade_actions(self):
        base = {
            "summary": "印尼调整出口管理制度，相关流程和供应预期可能发生变化，需要继续核验执行情况。",
            "detail_summary": "印尼调整出口管理制度并明确负责主体。新规覆盖合同、报关和结算环节。市场关注执行磨合对出口节奏的影响。来源还列出税费和执行日期。现阶段属于政策落地风险，并非已经确认的供应缺口。后续需要用出口量和港口效率验证。",
            "background": "此前出口由不同企业分别处理，本次变化将关键流程纳入统一管理。政策目标是提高监管和定价能力。",
            "event_facts": ["新规覆盖出口合同。", "新规覆盖报关流程。", "新规覆盖结算环节。"],
            "transmission_chain": "AI解释：统一出口管理可能增加磨合成本并影响装运节奏，只有出口量确认下降后，才可能形成棕榈油供应风险溢价。",
            "market_relevance": "这是政策执行风险情景，不是已经发生的减产事实。",
            "what_to_watch": ["出口量。", "港口效率。"],
            "uncertainty": "政策实际执行效果仍待验证。",
            "publishable": True,
        }
        self.assertFalse(RUNNER.valid_model_summary({**base, "headline": "告急：印尼棕榈油黑天鹅来袭"}))
        self.assertFalse(RUNNER.valid_model_summary({**base, "headline": "印尼政策变化后建议逢低做多棕榈油"}))
        self.assertTrue(RUNNER.valid_model_summary({**base, "headline": "印尼统一出口管理抬升棕榈油供应风险"}))

    def test_htfc_report_permission_failure_is_not_reported_as_zero(self):
        from urllib.error import HTTPError
        error = HTTPError("https://x", 403, "Forbidden", {}, io.BytesIO(b""))
        self.addCleanup(error.close)
        with patch.object(EVENTS, "request_json", side_effect=error):
            events, source = EVENTS.htfc_report_events(WATCH, "https://example.test", "key", self.now)
        self.assertEqual(events, [])
        self.assertEqual(source["state"], "forbidden")
        self.assertIn("HTTPError", source["detail"])

    def test_rss_results_keep_provider_and_original_link(self):
        xml = '''<?xml version="1.0"?><rss><channel><item><title>棕榈油出口增加</title><description>产地数据更新</description><link>https://example.test/a</link><guid>one</guid><pubDate>Wed, 26 Aug 2026 02:04:00 GMT</pubDate></item></channel></rss>'''.encode("utf-8")
        with patch.object(EVENTS.urllib.request, "urlopen", return_value=Response(xml)), patch.object(
            EVENTS, "fetch_article_text_safely", side_effect=lambda url, timeout=10: (url, "棕榈油出口增加，产地公布新的出口数据和执行时间。" * 5)
        ):
            events, source = EVENTS.rss_events(WATCH, self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(len(events), 2)
        self.assertTrue(all(item["source"].startswith("跨站新闻·") for item in events))
        self.assertTrue(all(item["url"] == "https://example.test/a" for item in events))
        self.assertTrue(all(item["source_content_level"] == "full_article" for item in events))

    def test_rss_enriches_relevant_article_beyond_previous_six_item_limit(self):
        items = "".join(
            f"<item><title>棕榈油政策更新{i}</title><description>印尼棕榈油政策新闻{i}</description><link>https://example.test/{i}</link><guid>{i}</guid><pubDate>Wed, 26 Aug 2026 02:04:00 GMT</pubDate></item>"
            for i in range(8)
        )
        xml = f"<?xml version='1.0'?><rss><channel>{items}</channel></rss>".encode("utf-8")
        with patch.object(EVENTS.urllib.request, "urlopen", return_value=Response(xml)), patch.object(
            EVENTS, "fetch_article_text_safely", side_effect=lambda url, timeout=10: (url, f"这是{url}的完整正文，包含印尼棕榈油政策主体、执行时间、出口流程和影响范围。" * 5)
        ) as fetch:
            events, _source = EVENTS.rss_events(WATCH, self.now)
        self.assertTrue(any(item["url"].endswith("/7") and item["source_content_level"] == "full_article" for item in events))
        self.assertGreaterEqual(fetch.call_count, 16)

    def test_weather_events_publish_direct_forecast_with_ai_notice(self):
        payload = {"daily": {
            "time": ["2026-08-26"] * 7,
            "precipitation_sum": [1, 2, 0, 1, 0, 2, 1],
            "precipitation_probability_max": [20, 30, 10, 20, 10, 40, 20],
            "temperature_2m_max": [34, 36, 37, 36, 35, 34, 33],
            "temperature_2m_min": [24, 24, 25, 25, 24, 24, 23],
        }}
        with patch.object(EVENTS, "request_json", return_value=payload):
            events, source = EVENTS.weather_events(WATCH, self.now)
        self.assertEqual(source["state"], "ready")
        self.assertEqual(len(events), len(EVENTS.WEATHER_REGIONS))
        self.assertTrue(all(item["category"] == "天气产量研判" for item in events))
        self.assertTrue(all(item["direct_source_available"] for item in events))
        self.assertTrue(all("不构成投资建议" in item["ai_notice"] for item in events))
        self.assertTrue(all("production_chain" in item["weather_analysis"] for item in events))
        self.assertTrue(all("market_chain" in item["weather_analysis"] for item in events))
        self.assertTrue(all(item["weather_region"] for item in events))
        self.assertTrue(all("rain_total_mm" in item["weather_snapshot"] for item in events))
        by_title = {item["title"]: item for item in events}
        iowa = next(item for title, item in by_title.items() if "爱荷华" in title)
        brazil = next(item for title, item in by_title.items() if "马托格罗索" in title)
        self.assertEqual(iowa["impact"], "高")
        self.assertIn("单产", iowa["summary"])
        self.assertEqual(brazil["impact"], "低")
        self.assertIn("暂不等于大豆减产", brazil["title"])
        self.assertIn("没有直接受损对象", brazil["summary"])

    def test_canola_harvest_rain_maps_to_supply_timing_not_generic_crop_stress(self):
        region = next(item for item in EVENTS.WEATHER_REGIONS if item["profile"] == "canola")
        analysis = EVENTS.weather_analysis(region, self.now, 52.5, 26.9, 0, 5)
        self.assertEqual(analysis["impact"], "高")
        self.assertIn("收获期多雨", analysis["title"])
        self.assertIn("上市节奏", analysis["market_chain"])
        self.assertIn("不等同生物学单产下降", analysis["market_chain"])

    def test_event_merge_keeps_price_events_and_replaces_old_news(self):
        prior = {
            "generated_at": "2026-08-26T10:05:00+08:00",
            "events": [
                {"id": "price:1", "kind": "market", "observed_at": "2026-08-26T10:05:00+08:00"},
                {"id": "old-news", "kind": "event", "observed_at": "2026-08-26T09:00:00+08:00"},
            ],
            "sources": [{"name": "全量期货行情", "state": "ready"}],
            "coverage": {"priced_contracts": 39},
        }
        news = [{"id": "new-news", "kind": "event", "observed_at": "2026-08-26T10:04:00+08:00"}]
        sources = [{"name": "跨站新闻搜索", "state": "ready"}]
        result = RUNNER.merge_snapshot(WATCH, prior, news, sources, self.now)
        self.assertEqual(result["generated_at"], prior["generated_at"])
        self.assertEqual({item["id"] for item in result["events"]}, {"price:1", "new-news"})
        self.assertEqual(result["coverage"]["event_sources_ready"], 1)

    def test_weather_refresh_keeps_original_time_when_forecast_has_no_material_change(self):
        prior = {
            "events": [{
                "id": "weather:prior",
                "kind": "event",
                "category": "天气产量研判",
                "weather_region": "马来西亚柔佛",
                "title": "马来西亚柔佛温雨适中：短期供应影响有限",
                "impact": "低",
                "observed_at": "2026-08-26T08:00:00+08:00",
                "weather_analysis": {"signal": "供应影响中性"},
                "weather_snapshot": {
                    "rain_total_mm": 40.0,
                    "peak_precipitation_probability_pct": 60.0,
                    "max_temperature_c": 32.0,
                    "hot_days": 0,
                    "wet_days": 1,
                },
            }]
        }
        current = [{
            "id": "weather:new",
            "kind": "event",
            "category": "天气产量研判",
            "weather_region": "马来西亚柔佛",
            "title": "马来西亚柔佛温雨适中：短期供应影响有限",
            "impact": "低",
            "observed_at": "2026-08-26T08:05:00+08:00",
            "weather_analysis": {"signal": "供应影响中性"},
            "weather_snapshot": {
                "rain_total_mm": 44.0,
                "peak_precipitation_probability_pct": 70.0,
                "max_temperature_c": 32.6,
                "hot_days": 0,
                "wet_days": 1,
            },
        }]
        events, unchanged = RUNNER.stabilize_weather_events(current, prior)
        self.assertEqual(unchanged, 1)
        self.assertEqual(events[0]["id"], "weather:prior")
        self.assertEqual(events[0]["observed_at"], "2026-08-26T08:00:00+08:00")
        self.assertEqual(events[0]["weather_published_snapshot"]["rain_total_mm"], 40.0)

    def test_weather_refresh_gets_new_time_after_material_change(self):
        prior = {
            "events": [{
                "id": "weather:prior",
                "kind": "event",
                "category": "天气产量研判",
                "weather_region": "美国爱荷华",
                "title": "美国爱荷华温雨未见极端：美豆单产暂维持观察",
                "impact": "低",
                "observed_at": "2026-08-26T08:00:00+08:00",
                "weather_analysis": {"signal": "单产影响中性"},
                "weather_snapshot": {"rain_total_mm": 30.0, "max_temperature_c": 31.0},
            }]
        }
        current = [{
            "id": "weather:new",
            "kind": "event",
            "category": "天气产量研判",
            "weather_region": "美国爱荷华",
            "title": "美国爱荷华鼓粒期高温少雨：单产风险上升",
            "impact": "高",
            "observed_at": "2026-08-26T08:05:00+08:00",
            "weather_analysis": {"signal": "美豆单产下修风险"},
            "weather_snapshot": {"rain_total_mm": 5.0, "max_temperature_c": 39.0},
        }]
        events, unchanged = RUNNER.stabilize_weather_events(current, prior)
        self.assertEqual(unchanged, 0)
        self.assertEqual(events[0]["id"], "weather:new")
        self.assertEqual(events[0]["observed_at"], "2026-08-26T08:05:00+08:00")
        self.assertEqual(events[0]["weather_published_snapshot"]["rain_total_mm"], 5.0)


if __name__ == "__main__":
    unittest.main()

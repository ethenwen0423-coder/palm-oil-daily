from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("build_research_watch", ROOT / "scripts" / "build_research_watch.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
SHANGHAI = ZoneInfo("Asia/Shanghai")


def report(report_id: str, title: str, subclass: str, published: str = "2026-08-27 08:24:21"):
    return {"id": report_id, "title": title, "subclassCodeName": subclass, "publishDateTime": published, "aiContent": "<b>公开摘要</b><br>正文"}


def source_payload():
    products = {}
    for key in ("P", "Y", "OI"):
        products[key] = {"response": {"data": {"resultList": [report(f"oil-{key}-{index}", f"油脂日报{key}{index}", "棕榈油,豆油,菜油") for index in range(4)]}}}
    for key in ("SC", "MACRO"):
        products[key] = {"response": {"data": {"resultList": [report(f"cross-{key}-{index}", f"跨板块日报{key}{index}", "原油" if key == "SC" else "宏观") for index in range(3)]}}}
    return {"modules": {"research_reports": {"products": products}}}


class ResearchWatchTests(unittest.TestCase):
    def test_builds_seven_three_allocation_and_deduplicates(self):
        now = datetime(2026, 8, 27, 8, 35, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
            payload = MODULE.build(source, None, now)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["allocation"], {"油脂油料": 7, "跨板块": 3, "target": "70% / 30%"})
        self.assertEqual(len(payload["items"]), 10)
        self.assertEqual(payload["schema_version"], 5)
        self.assertNotIn("<", json.dumps(payload, ensure_ascii=False))

    def test_merges_public_search_and_preserves_source_content(self):
        now = datetime(2026, 8, 27, 8, 35, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            payload = source_payload()
            payload["modules"]["research_reports"]["products"]["P"]["response"]["data"]["resultList"][0]["title"] = "华泰期货油脂日报"
            payload["modules"]["research_reports"]["products"]["P"]["response"]["data"]["resultList"] = payload["modules"]["research_reports"]["products"]["P"]["response"]["data"]["resultList"][:3]
            payload["modules"]["research_reports"]["products"]["Y"]["response"]["data"]["resultList"] = payload["modules"]["research_reports"]["products"]["Y"]["response"]["data"]["resultList"][:3]
            payload["modules"]["research_reports"]["products"]["OI"]["response"]["data"]["resultList"] = []
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            public = root / "public.json"
            public.write_text(json.dumps({"data": [{
                "uid": "public-1",
                "title": "公开棕榈油深度研报",
                "summary": "棕榈油供需跟踪",
                "publish_date": "2026-08-27 07:30:00",
                "extra": {"organization": "公开机构", "cat_names": ["农产品"]},
                "url": "https://example.test/report",
            }]}), encoding="utf-8")
            result = MODULE.build(source, None, now, [public])
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertIn("华泰期货油脂日报", serialized)
        self.assertIn("institution-report-skill", result["source_counts"])
        self.assertIn("report-search", result["source_counts"])
        self.assertEqual(result["candidate_source_counts"]["report-search"], 1)
        self.assertEqual(result["source_policy"], "机构研报、问财公开研报搜索与东方财富妙想来源平权；仅按质量评分择优；跨源标题去重")

    def test_merges_mx_reports_and_refreshes_weekend_snapshot(self):
        now = datetime(2026, 8, 31, 10, 5, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
            mx = root / "mx.json"
            mx.write_text(json.dumps({
                "data": {"data": {"llmSearchResponse": {"data": [{
                    "code": "AP-20260831",
                    "title": "棕榈油周报：天气影响发酵",
                    "content": "核心观点 棕榈油库存下降，天气与生柴政策提供支撑。风险因素：MPOB报告。",
                    "date": "2026-08-31 09:21:16",
                    "informationType": "REPORT",
                    "insName": "公开期货机构",
                    "author": "研究员",
                }]}}},
            }, ensure_ascii=False), encoding="utf-8")
            result = MODULE.build(source, None, now, mx_paths=[mx])
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["report_date"], "2026-08-31")
        self.assertEqual(result["fresh_item_count"], 1)
        self.assertEqual(result["candidate_source_counts"]["mx-search"], 1)
        self.assertIn("mx-search", result["source_counts"])
        mx_item = next(item for item in result["items"] if item["source_channel"] == "mx-search")
        self.assertEqual(mx_item["organization"], "公开期货机构")
        self.assertIn("保持来源内容完整展示", mx_item["summary_notice"])

    def test_mx_original_crude_title_is_cross_sector_even_if_body_mentions_oilseeds(self):
        item = MODULE.normalize_mx_search_item({
            "code": "AP-crude",
            "title": "原油早报",
            "content": "原油供应与库存变化，同时提到豆油和棕榈油联动。",
            "date": "2026-08-31 09:14:16",
            "informationType": "REPORT",
            "insName": "公开期货机构",
        })
        self.assertEqual(item["sector"], "跨板块")

    def test_no_current_report_publishes_scan_state_instead_of_frozen_payload(self):
        now = datetime(2026, 8, 31, 10, 5, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
            existing = root / "existing.json"
            existing.write_text(json.dumps({
                "schema_version": 4,
                "status": "ready",
                "report_date": "2026-08-27",
                "generated_at": "2026-08-27T22:31:46+08:00",
                "items": [{"id": "frozen"}],
            }), encoding="utf-8")
            result = MODULE.build(source, existing, now)
        self.assertEqual(result["status"], "stale")
        self.assertEqual(result["report_date"], "2026-08-27")
        self.assertEqual(result["last_scanned_at"], "2026-08-31T10:05:00+08:00")
        self.assertEqual(result["fresh_item_count"], 0)
        self.assertNotEqual(result["items"], [{"id": "frozen"}])

    def test_preserves_complete_summary_and_direct_source_link(self):
        long_summary = "第一项关键信息包含库存与产量变化。" * 20 + "最后一项风险信息必须完整保留。"
        institution = MODULE.normalize_item({
            "id": "institution-long",
            "title": "完整标题不应被固定字数截断" * 20,
            "subclassCodeName": "棕榈油",
            "publishDateTime": "2026-08-27 08:00:00",
            "aiContent": long_summary,
            "link_url": "https://example.test/original-report.pdf",
        }, "油脂油料", "P")
        public = MODULE.normalize_public_search_item({
            "uid": "public-long",
            "title": "公开研报",
            "summary": long_summary,
            "publish_date": "2026-08-27 07:30:00",
            "url": "https://example.test/public-report",
        })
        self.assertEqual(institution["summary"], long_summary)
        self.assertTrue(institution["summary"].endswith("最后一项风险信息必须完整保留。"))
        self.assertEqual(institution["url"], "https://example.test/original-report.pdf")
        self.assertEqual(public["summary"], long_summary)
        self.assertEqual(public["url"], "https://example.test/public-report")
        self.assertIn("保持原文完整展示", institution["summary_notice"])
        self.assertEqual([point["label"] for point in institution["reading_view"]["quick_points"]], ["核心结论", "主要驱动", "关键风险"])

    def test_builds_structured_two_level_reading_without_changing_source_summary(self):
        summary = (
            "核心观点 1. 全球原油库存低位，需警惕航运中断推动油价上行。 "
            "2. 国内制造业PMI降至49.2，后续关注稳增长政策。 "
            "策略建议 1. 贵金属和部分农产品逢低关注。 "
            "风险提示 1. 地缘政治冲突可能推升能源价格。 2. 美联储超预期收紧可能压制风险资产。"
        )
        item = MODULE.normalize_item({
            "id": "structured",
            "title": "宏观大类日报",
            "subclassCodeName": "宏观",
            "publishDateTime": "2026-08-27 08:00:00",
            "aiContent": summary,
        }, "跨板块", "MACRO")
        view = item["reading_view"]
        self.assertEqual(item["summary"], summary)
        self.assertEqual(len(view["quick_points"]), 3)
        self.assertEqual(len(view["sections"]["core"]), 2)
        self.assertEqual(len(view["sections"]["strategy"]), 1)
        self.assertEqual(len(view["sections"]["risk"]), 2)
        self.assertIn("PMI降至49.2", view["quick_points"][1]["text"])
        self.assertIn("地缘政治冲突", view["quick_points"][2]["text"])
        self.assertIn("AI基于所列来源摘要生成", view["reading_notice"])

    def test_unlabelled_summary_falls_back_to_complete_clauses(self):
        summary = "棕榈油库存下降，现货基差走强。出口需求仍需继续核验。天气风险可能影响后续产量。"
        view = MODULE.build_reading_view(summary, "source_summary")
        self.assertEqual(view["sections"]["core"], [
            "棕榈油库存下降，现货基差走强。",
            "出口需求仍需继续核验。",
            "天气风险可能影响后续产量。",
        ])
        self.assertTrue(all(point["text"].endswith("。") for point in view["quick_points"]))

    def test_missing_link_uses_full_source_summary_without_fabricating_url(self):
        item = MODULE.normalize_item({
            "id": "institution-no-link",
            "title": "机构晨报",
            "subclassCodeName": "宏观",
            "publishDateTime": "2026-08-27 08:00:00",
            "brief": "核心信息一。核心信息二。风险信息三。",
        }, "跨板块", "MACRO")
        self.assertEqual(item["summary"], "核心信息一。核心信息二。风险信息三。")
        self.assertEqual(item["summary_type"], "source_summary")
        self.assertNotIn("url", item)

    def test_ai_generated_recommendation_warning_is_complete(self):
        report_date = datetime(2026, 8, 27, 8, 35, tzinfo=SHANGHAI).date()
        selected, *_ = MODULE.select(source_payload(), report_date)
        self.assertTrue(selected)
        self.assertIn("AI基于所列来源字段生成", selected[0]["ai_notice"])
        self.assertIn("不代表任何来源方官方立场", selected[0]["ai_notice"])
        self.assertIn("不构成投资建议", selected[0]["ai_notice"])
        self.assertIn("请自行核验", selected[0]["ai_notice"])

    def test_quality_score_not_source_decides_selection_order(self):
        report_date = datetime(2026, 8, 27, 8, 35, tzinfo=SHANGHAI).date()
        institution = MODULE.normalize_item(
            report("institution", "油脂日报", "棕榈油", "2026-08-20 08:00:00"),
            "油脂油料",
            "P",
        )
        public = MODULE.normalize_public_search_item({
            "uid": "public",
            "title": "棕榈油供需深度报告",
            "summary": "库存、产量、出口和基差数据显示供需变化，风险来自政策。价格从9800变为10000，库存变化12%。",
            "publish_date": "2026-08-27 07:30:00",
            "extra": {"organization": "公开机构", "cat_names": ["农产品"]},
        })
        institution_score, _ = MODULE.score_quality(institution, report_date)
        public_score, _ = MODULE.score_quality(public, report_date)
        self.assertGreater(public_score, institution_score)
        self.assertNotIn("source_priority", institution)
        self.assertNotIn("source_priority", public)

    def test_rescans_and_replaces_same_day_snapshot(self):
        now = datetime(2026, 8, 27, 9, 5, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
            existing = root / "existing.json"
            existing.write_text(json.dumps({"schema_version": 3, "status": "ready", "report_date": "2026-08-27", "items": [{"id": "frozen"}]}), encoding="utf-8")
            payload = MODULE.build(source, existing, now)
        self.assertNotEqual(payload["items"], [{"id": "frozen"}])
        self.assertEqual(payload["report_date"], "2026-08-27")
        self.assertEqual(payload["refresh_policy"], "每5分钟独立扫描机构研报与公开研报；按质量重新择优")
        self.assertEqual(payload["schema_version"], 5)


if __name__ == "__main__":
    unittest.main()

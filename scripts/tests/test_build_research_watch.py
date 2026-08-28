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
        self.assertEqual(payload["schema_version"], 3)
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
        self.assertEqual(result["source_policy"], "机构研报 skill 与问财公开研报搜索来源平权；仅按质量评分择优；跨源标题去重")

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


if __name__ == "__main__":
    unittest.main()

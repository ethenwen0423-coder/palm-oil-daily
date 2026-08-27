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
        self.assertEqual(payload["schema_version"], 2)
        self.assertNotIn("<", json.dumps(payload, ensure_ascii=False))

    def test_merges_public_search_deduplicates_and_redacts_brand(self):
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
        self.assertNotIn("华泰", serialized)
        self.assertNotIn("天玑", serialized)
        self.assertIn("institution-report-skill", result["source_counts"])
        self.assertIn("report-search", result["source_counts"])
        self.assertEqual(result["candidate_source_counts"]["report-search"], 1)
        self.assertEqual(result["source_policy"], "研报服务机构接口优先；同花顺问财公开研报搜索补充；跨源标题去重")

    def test_preserves_first_ready_snapshot_for_the_day(self):
        now = datetime(2026, 8, 27, 9, 5, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
            existing = root / "existing.json"
            existing.write_text(json.dumps({"schema_version": 2, "status": "ready", "report_date": "2026-08-27", "items": [{"id": "frozen"}]}), encoding="utf-8")
            payload = MODULE.build(source, existing, now)
        self.assertEqual(payload["items"], [{"id": "frozen"}])


if __name__ == "__main__":
    unittest.main()

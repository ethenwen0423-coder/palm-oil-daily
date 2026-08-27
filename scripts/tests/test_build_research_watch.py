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
    return {"id": report_id, "title": title, "subclassCodeName": subclass, "publishDateTime": published, "aiContent": "公开摘要"}


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

    def test_preserves_first_ready_snapshot_for_the_day(self):
        now = datetime(2026, 8, 27, 9, 5, tzinfo=SHANGHAI)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
            existing = root / "existing.json"
            existing.write_text(json.dumps({"status": "ready", "report_date": "2026-08-27", "items": [{"id": "frozen"}]}), encoding="utf-8")
            payload = MODULE.build(source, existing, now)
        self.assertEqual(payload["items"], [{"id": "frozen"}])


if __name__ == "__main__":
    unittest.main()

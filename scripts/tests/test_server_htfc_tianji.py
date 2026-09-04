from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("run_htfc_tianji", ROOT / "server" / "run_htfc_tianji.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
SHANGHAI = ZoneInfo("Asia/Shanghai")


class ServerHtfcTianjiTests(unittest.TestCase):
    def test_supplemental_refresh_slots_are_bounded_to_four_daily_batches(self):
        self.assertIsNone(MODULE.supplemental_refresh_slot(datetime(2026, 8, 31, 6, 59, tzinfo=SHANGHAI)))
        self.assertEqual(MODULE.supplemental_refresh_slot(datetime(2026, 8, 31, 7, 0, tzinfo=SHANGHAI)), "2026-08-31T07")
        self.assertEqual(MODULE.supplemental_refresh_slot(datetime(2026, 8, 31, 10, 37, tzinfo=SHANGHAI)), "2026-08-31T10")
        self.assertEqual(MODULE.supplemental_refresh_slot(datetime(2026, 8, 31, 17, 59, tzinfo=SHANGHAI)), "2026-08-31T14")
        self.assertEqual(MODULE.supplemental_refresh_slot(datetime(2026, 8, 31, 23, 59, tzinfo=SHANGHAI)), "2026-08-31T18")

    def test_quota_failures_are_visible(self):
        self.assertEqual(MODULE.failure_status("您今天的次数已用完"), "quota_exhausted")
        self.assertEqual(MODULE.failure_status("调用次数已达到上限"), "quota_exhausted")
        self.assertEqual(MODULE.failure_status("timeout"), "request_failed")

    def test_cached_public_search_inputs_are_restored_for_every_scan(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            live = root / "live"
            output = root / "output"
            relative = MODULE.PUBLIC_CACHE_PATHS["oil"]
            source = live / relative
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps({"data": [{"uid": "r1"}]}), encoding="utf-8")
            restored = MODULE.restore_cached_inputs(output, live, MODULE.PUBLIC_CACHE_PATHS)
        self.assertEqual(restored, [str(output / relative)])


if __name__ == "__main__":
    unittest.main()

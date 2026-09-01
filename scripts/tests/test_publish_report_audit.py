from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "publish_report.py"
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("publish_report_with_audit", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublishReportAuditTests(unittest.TestCase):
    def test_public_report_record_contains_bound_quality_and_artifact_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            reports = root / "reports"
            run_root = root / "source_runs" / "2026-08-07-daily"
            reports.mkdir(parents=True)
            (run_root / "raw").mkdir(parents=True)
            report = reports / "2026-08-07.md"
            report.write_text("# 08月07日晨报\n\n## 【今日观点】\n\n完整观点。\n", encoding="utf-8")
            (run_root / "report_outline.json").write_text('{"kind":"daily"}\n', encoding="utf-8")
            (run_root / "raw" / "futures_market_data.json").write_text('{"date":"2026-08-07"}\n', encoding="utf-8")
            (run_root / "report_quality.json").write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "can_publish": True,
                        "score": 97,
                        "minimum_score": 92,
                    }
                ),
                encoding="utf-8",
            )

            replacements = {
                "ROOT": root,
                "REPORTS_DIR": reports,
                "DATA_FILE": root / "data" / "reports.js",
                "VERSION_FILE": root / "data" / "version.js",
                "DOWNLOADS_DIR": root / "downloads",
                "QUALITY_DIR": root / "data" / "report_quality",
            }
            with mock.patch.multiple(MODULE, **replacements):
                with mock.patch.object(MODULE, "publish_dataset") as publish_dataset:
                    MODULE.main()

            records = publish_dataset.call_args.args[1]
            quality = records[0]["quality"]
            self.assertEqual(quality["score"], 97)
            self.assertTrue(quality["can_publish"])
            self.assertEqual(quality["source_run"], "source_runs/2026-08-07-daily")
            self.assertEqual(
                set(quality["artifacts"]),
                {"report_sha256", "quality_sha256", "outline_sha256", "source_sha256"},
            )
            self.assertTrue(all(len(value) == 64 for value in quality["artifacts"].values()))


if __name__ == "__main__":
    unittest.main()

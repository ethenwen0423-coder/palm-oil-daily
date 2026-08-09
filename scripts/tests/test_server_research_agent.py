from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "server" / "run_research_agent.py"
SPEC = importlib.util.spec_from_file_location("server_research_agent", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ServerResearchAgentTests(unittest.TestCase):
    def test_openai_responses_request_uses_strict_schema(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(
                    {
                        "output_text": json.dumps(
                            {
                                "fixed_logic": MODULE.FIXED_LOGIC,
                                "report_markdown": "# 08月07日晨报\n" + ("报告内容" * 500),
                                "outline": {
                                    "report_date": "2026-08-07",
                                    "kind": "daily",
                                },
                            }
                        )
                    }
                ).encode()

        with tempfile.TemporaryDirectory() as temporary:
            schema = Path(temporary) / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-secret"}, clear=True):
                with mock.patch.object(
                    MODULE.MODEL_BACKEND.urllib.request,
                    "urlopen",
                    return_value=FakeResponse(),
                ) as urlopen:
                    payload = MODULE.run_openai(schema, "test prompt", timeout=30)
        request = urlopen.call_args.args[0]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["fixed_logic"], MODULE.FIXED_LOGIC)
        self.assertEqual(body["text"]["format"]["type"], "json_schema")
        self.assertTrue(body["text"]["format"]["strict"])
        self.assertEqual(request.get_header("Authorization"), "Bearer sk-test-secret")

    def test_deepseek_chat_request_uses_json_mode_and_same_output_gate(self) -> None:
        expected = {
            "fixed_logic": MODULE.FIXED_LOGIC,
            "report_markdown": "# 08月07日晨报\n" + ("报告内容" * 500),
            "outline": {"report_date": "2026-08-07", "kind": "daily"},
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(
                    {"choices": [{"message": {"content": json.dumps(expected)}}]}
                ).encode()

        with tempfile.TemporaryDirectory() as temporary:
            schema = Path(temporary) / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            environment = {
                "PALM_OIL_AI_PROVIDER": "deepseek",
                "PALM_OIL_AI_API_KEY": "sk-deepseek-secret",
            }
            with mock.patch.dict(os.environ, environment, clear=True):
                with mock.patch.object(
                    MODULE.MODEL_BACKEND.urllib.request,
                    "urlopen",
                    return_value=FakeResponse(),
                ) as urlopen:
                    payload = MODULE.run_openai(schema, "test prompt", timeout=30)
        request = urlopen.call_args.args[0]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["fixed_logic"], MODULE.FIXED_LOGIC)
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertIn("OUTPUT_JSON_SCHEMA", body["messages"][0]["content"])
        self.assertEqual(request.get_header("Authorization"), "Bearer sk-deepseek-secret")

    def test_schedule_has_daily_retry_and_sunday_weekend_window(self) -> None:
        timezone = MODULE.SHANGHAI
        self.assertIsNone(
            MODULE.select_due(datetime(2026, 8, 7, 5, 59, tzinfo=timezone))
        )
        self.assertEqual(
            MODULE.select_due(datetime(2026, 8, 7, 6, 0, tzinfo=timezone)),
            "daily",
        )
        self.assertIsNone(
            MODULE.select_due(datetime(2026, 8, 9, 21, 14, tzinfo=timezone))
        )
        self.assertEqual(
            MODULE.select_due(datetime(2026, 8, 9, 21, 15, tzinfo=timezone)),
            "weekend",
        )
        self.assertIsNone(
            MODULE.select_due(datetime(2026, 8, 8, 21, 15, tzinfo=timezone))
        )

    def test_model_output_cannot_change_fixed_logic(self) -> None:
        payload = {
            "report_markdown": "# 08月07日晨报\n" + ("报告内容" * 500),
            "outline": {"report_date": "2026-08-07", "kind": "daily"},
            "fixed_logic": ["changed"],
        }
        with self.assertRaisesRegex(MODULE.ResearchAgentError, "fixed-logic"):
            MODULE.validate_model_output(
                payload,
                report_date="2026-08-07",
                kind="daily",
            )

    def test_dry_run_is_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            site = base / "site"
            runtime = base / "runtime"
            live = base / "live"
            state = base / "state"
            site.mkdir()
            mock_response = base / "response.json"
            mock_response.write_text("{}", encoding="utf-8")
            before = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--site-root",
                    str(site),
                    "--runtime-root",
                    str(runtime),
                    "--live-data-root",
                    str(live),
                    "--state-root",
                    str(state),
                    "--now",
                    "2026-08-07T06:00:00+08:00",
                    "--mock-response",
                    str(mock_response),
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["kind"], "daily")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

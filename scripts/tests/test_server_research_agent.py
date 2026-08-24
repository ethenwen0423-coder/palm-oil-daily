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
            MODULE.select_due(datetime(2026, 8, 7, 9, 0, tzinfo=timezone))
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

    def test_prompt_bounds_the_visible_headline(self) -> None:
        prompt = MODULE.build_prompt(
            report_date="2026-08-07",
            kind="daily",
            source_snapshot={},
            feedback=None,
            correction="",
        )
        self.assertIn("页面 Headline", prompt)
        self.assertIn("不得超过 50 个字符", prompt)
        self.assertIn("不得使用价格、数字或交易执行词", prompt)
        self.assertIn("至少三项 SOURCE_JSON 中有精确数字的辅助证据", prompt)
        self.assertIn("不得在“信息来源与核验说明”之前使用“需进一步核验”", prompt)
        self.assertIn("今日观点”第一段必须包含可机器读取的 `置信度：", prompt)
        self.assertIn("内部元数据，不得写成市场驱动", prompt)
        self.assertIn("必须逐字写：本报告由AI基于公开信息", prompt)
        self.assertIn("分别列出 P、Y、OI 三行", prompt)

    def test_weekend_prompt_requires_history_tables_and_relative_value(self) -> None:
        prompt = MODULE.build_prompt(
            report_date="2026-08-09",
            kind="weekend",
            source_snapshot={"research_history": {}},
            feedback=None,
            correction="",
        )
        self.assertIn("research_history.previous_report", prompt)
        self.assertIn("本周起建立连续验证基线", prompt)
        self.assertIn("必须使用 Markdown 表格", prompt)
        self.assertIn("分别列出 P、Y、OI 三行", prompt)
        self.assertIn("豆棕价差与菜豆油价差", prompt)

    def test_persistent_context_restores_previous_source_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            state = base / "state"
            runtime = base / "runtime"
            report = runtime / "reports" / "2026-08-09-weekend.md"
            run_root = runtime / "source_runs" / "2026-08-09-weekend"
            report.parent.mkdir(parents=True)
            run_root.mkdir(parents=True)
            report.write_text("report", encoding="utf-8")
            (run_root / "manifest.json").write_text("{}", encoding="utf-8")
            MODULE.persist_outputs(state, runtime, report, run_root)
            restored = base / "restored"
            (restored / "reports").mkdir(parents=True)
            MODULE.restore_persistent_outputs(state, restored)
            self.assertTrue((restored / "source_runs/2026-08-09-weekend/manifest.json").is_file())

    def test_visible_headline_is_bounded_before_title_gate(self) -> None:
        markdown = "# 08月07日晨报\n\n## 【今日观点】\n" + ("震荡延续但需要多维证据共同验证" * 8)
        bounded = MODULE.normalize_visible_headline(markdown, "daily")
        headline = bounded.splitlines()[-1]
        self.assertLessEqual(len("".join(headline.split())), 50)

    def test_daily_confidence_cap_is_written_when_model_omits_it(self) -> None:
        markdown = "# 08月07日晨报\n\n## 【今日观点】\n\n震荡，等待更多证据。\n\n## 【今日交易信号】\n"
        updated, outline = MODULE.enforce_confidence_cap(
            markdown,
            {"research_confidence": "★★★★★"},
            {"core_view_confidence_cap_stars": 2},
            "daily",
        )
        self.assertIn("置信度：★★☆☆☆。", updated)
        self.assertEqual(outline["research_confidence"], "★★☆☆☆")

    def test_final_confidence_repair_uses_audited_outline_rating(self) -> None:
        markdown = "# 08月24日晨报\n\n## 【今日观点】\n\n震荡等待基本面确认。\n\n## 【今日交易信号】\n"
        updated = MODULE.ensure_visible_confidence(
            markdown,
            {"research_confidence": "★★☆☆☆"},
            "daily",
        )
        self.assertIn("震荡等待基本面确认。\n\n置信度：★★☆☆☆。", updated)
        self.assertEqual(updated.count("置信度："), 1)

    def test_daily_audit_contracts_expose_stance_and_invalidation(self) -> None:
        markdown = """# 08月24日晨报

## 【今日交易信号】

| 品种 | 行动 |
|---|---|
| P | 等待 |

## 【风险提示】

供需与价格可能背离。

## 【信息来源与核验说明】
"""
        updated = MODULE.ensure_daily_audit_contracts(
            markdown,
            {"market_stance": "震荡", "invalidation_condition": "P跌破观察区间"},
            "daily",
        )
        self.assertIn("今日策略：震荡。", updated)
        self.assertIn("可检验失效条件：P跌破观察区间。", updated)

    def test_weekly_audit_contracts_expose_previous_validation(self) -> None:
        markdown = """# 08月24日周报

## 【本周验证与预期差】

本周价差仍在波动。

## 【核心数据变化】
"""
        updated = MODULE.ensure_weekly_previous_validation(
            markdown,
            {
                "research_history": {
                    "previous_report": {
                        "date": "2026-08-23-weekend",
                        "title": "08月23日周报",
                        "headline": "油脂维持震荡。",
                    }
                }
            },
            "weekend",
        )
        self.assertIn("2026-08-23，08月23日周报", updated)
        self.assertIn("油脂维持震荡", updated)
        self.assertIn("部分兑现、仍待确认", updated)

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

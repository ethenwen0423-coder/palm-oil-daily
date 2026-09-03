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

    def test_acceptance_report_date_uses_rank_one_exchange_trade_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "oil_futures.json").write_text(
                json.dumps(
                    {
                        "contracts": [
                            {
                                "product": product,
                                "contract_rank": 1,
                                "trade_date": "2026-09-02",
                            }
                            for product in ("P", "Y", "OI")
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                MODULE.acceptance_report_date(root, "2026-09-01"),
                "2026-09-02",
            )

    def test_acceptance_report_date_never_moves_backward(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "oil_futures.json").write_text(
                json.dumps(
                    {
                        "contracts": [
                            {
                                "product": "P",
                                "contract_rank": 1,
                                "trade_date": "2026-08-31",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                MODULE.acceptance_report_date(root, "2026-09-01"),
                "2026-09-01",
            )

    def test_shadow_acceptance_runs_before_publication_sync(self) -> None:
        source = (ROOT / "server" / "run_research_agent.py").read_text(encoding="utf-8")
        deploy = (ROOT / "scripts" / "deploy_report.sh").read_text(encoding="utf-8")
        self.assertIn('"--shadow-acceptance"', source)
        quality_branch = source.index("if args.shadow_acceptance:")
        report_dataset_check = source.index(
            'if not report_is_ready(runtime_root / "data" / "reports.json", identity):'
        )
        publication_sync = source.index("synced = sync_module.sync_research(")
        self.assertLess(quality_branch, report_dataset_check)
        self.assertLess(quality_branch, publication_sync)
        self.assertIn('"acceptance": "real_model_report_quality_validated"', source)
        self.assertIn("and not args.shadow_acceptance", source)
        self.assertIn('"PALM_OIL_SHADOW_ACCEPTANCE": "1" if args.shadow_acceptance else "0"', source)
        shadow_exit = deploy.index('if [[ "$SHADOW_ACCEPTANCE" == "1" ]]')
        self.assertLess(shadow_exit, deploy.index("server/freeze_prepared_forecast.py"))
        self.assertLess(shadow_exit, deploy.index("python3 scripts/publish_report.py"))

    def test_prompt_bounds_the_visible_headline(self) -> None:
        prompt = MODULE.build_prompt(
            report_date="2026-08-07",
            kind="daily",
            source_snapshot={},
            feedback=None,
            correction="",
            contract_text="REPOSITORY CONTRACT SENTINEL",
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
        self.assertIn("news_and_research_evidence.today_new_drivers", prompt)
        self.assertIn("两个主驱动合计不得少于350个中文可见字符", prompt)
        self.assertIn("模型初稿必须控制在 1200-1280 个可见字符", prompt)
        self.assertIn("今日交易信号不超过190字", prompt)
        self.assertIn("重写整份 report_markdown", prompt)
        self.assertIn("REPOSITORY CONTRACT SENTINEL", prompt)
        self.assertIn("指标、数值、时点、含义", prompt)
        self.assertIn("实际 skill", prompt)

    def test_compaction_prompt_preserves_outline_and_daily_contracts(self) -> None:
        prompt = MODULE.build_compaction_prompt(
            report_date="2026-09-03",
            kind="daily",
            rejected_markdown="# 09月03日晨报",
            outline={"market_stance": "震荡"},
            feedback={"required_report_disclosures": ["预测披露原句。"]},
            gate_feedback="正文篇幅 1855 字，不在 1000-1400 字预算内",
        )
        self.assertIn("1050-1320", prompt)
        self.assertIn("核心驱动与预期差350-380字", prompt)
        self.assertIn("至少三项可复核辅助数字", prompt)
        self.assertIn("预测披露原句。", prompt)
        self.assertIn('"market_stance": "震荡"', prompt)

    def test_prewrite_gate_requires_market_news_and_freshness_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            run_root = runtime / "source_runs" / "2026-08-07-daily"
            run_root.mkdir(parents=True)
            (run_root / "manifest.json").write_text(
                json.dumps(
                    {
                        "results": [
                            {"name": "futures_oil_fetch_market_data", "status": "ok"},
                            {"name": "news_and_research_skill_sources", "status": "ok"},
                            {"name": "oil_report_freshness", "status": "ok"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps({"status": "ok", "can_publish": True}),
                stderr="",
            )
            with mock.patch.object(MODULE.subprocess, "run", return_value=completed):
                payload = MODULE.run_prewrite_data_gate(runtime, run_root, 30)
            self.assertTrue(payload["can_publish"])
            self.assertTrue((run_root / "data_quality.json").is_file())

    def test_prewrite_gate_blocks_empty_research_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            run_root = runtime / "source_runs" / "2026-08-07-daily"
            run_root.mkdir(parents=True)
            (run_root / "manifest.json").write_text(
                json.dumps(
                    {
                        "results": [
                            {"name": "futures_oil_fetch_market_data", "status": "ok"},
                            {"name": "news_and_research_skill_sources", "status": "failed"},
                            {"name": "oil_report_freshness", "status": "failed"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps({"status": "ok", "can_publish": True}),
                stderr="",
            )
            with mock.patch.object(MODULE.subprocess, "run", return_value=completed):
                with self.assertRaisesRegex(MODULE.ResearchAgentError, "no publishable Level 1"):
                    MODULE.run_prewrite_data_gate(runtime, run_root, 30)

    def test_weekend_prompt_requires_history_tables_and_relative_value(self) -> None:
        prompt = MODULE.build_prompt(
            report_date="2026-08-09",
            kind="weekend",
            source_snapshot={"research_history": {}},
            feedback=None,
            correction="",
            contract_text="WEEKLY CONTRACT SENTINEL",
        )
        self.assertIn("research_history.previous_report", prompt)
        self.assertIn("本周起建立连续验证基线", prompt)
        self.assertIn("必须使用 Markdown 表格", prompt)
        self.assertIn("分别列出 P、Y、OI 三行", prompt)
        self.assertIn("豆棕价差与菜豆油价差", prompt)
        self.assertIn("高开高走、高开震荡、高开回落、低开", prompt)
        self.assertIn("WEEKLY CONTRACT SENTINEL", prompt)

    def test_repository_contract_loader_includes_original_prompts_and_checklist(self) -> None:
        contract = MODULE.load_report_contract(ROOT, "daily")
        self.assertIn("references/daily_automation_prompt.md", contract)
        self.assertIn("skills/report_writer_skill/SKILL.md", contract)
        self.assertIn("skills/vinson-research-writing/SKILL.md", contract)
        self.assertIn("skills/vinson-research-writing/checklist.md", contract)
        self.assertIn("高开、平开、低开三种情景", contract)

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
        lines = bounded.splitlines()
        heading_index = lines.index("## 【今日观点】")
        headline = next(line for line in lines[heading_index + 1 :] if line.strip())
        self.assertLessEqual(len("".join(headline.split())), 50)

    def test_visible_headline_splits_explanation_without_dropping_it(self) -> None:
        explanation = "今日策略：震荡。P偏强位置、Y回落、OI未共振，等待供需进一步确认。"
        markdown = f"# 09月02日晨报\n\n## 【今日观点】\n\n供需相抵，油脂维持震荡。{explanation}\n"
        bounded = MODULE.normalize_visible_headline(markdown, "daily")
        self.assertIn("\n供需相抵，油脂维持震荡。\n\n", bounded)
        self.assertIn(explanation, bounded)
        self.assertEqual(bounded.count(explanation), 1)

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

    def test_daily_audit_contracts_ground_top_call_chain_and_counter_from_outline(self) -> None:
        markdown = """# 08月24日晨报

## 【今日观点】

油脂等待供需确认。

置信度：★★☆☆☆。

## 【今日交易信号】

| 品种 | 行动 |
|---|---|
| P | 等待 |

## 【核心驱动与预期差】

主驱动一与主驱动二均有来源证据，预期与现实仍有差异。

## 【风险提示】

供需与价格可能背离。

## 【信息来源与核验说明】
"""
        outline = {
            "market_stance": "震荡",
            "top_call": "等待库存与外盘形成共振",
            "transmission_chain": "库存变化→基差→P/Y/OI分化",
            "strongest_counter_case": "外盘快速反向且库存累积",
            "invalidation_condition": "P跌破观察区间",
        }
        updated = MODULE.ensure_daily_audit_contracts(markdown, outline, "daily")
        self.assertIn("基准方向：震荡；行动：按交易信号表执行；失效：P跌破观察区间。", updated)
        self.assertIn("传导链：库存变化→基差→P/Y/OI分化。", updated)
        self.assertIn("最强反证：外盘快速反向且库存累积。", updated)
        self.assertNotIn("不新开仓", updated)

    def test_daily_audit_contracts_do_not_repeat_grounded_chain_or_invalidation(self) -> None:
        markdown = """# 09月02日晨报

## 【今日观点】

油脂维持震荡，按交易信号表执行；突破区间则失效。

## 【核心驱动与预期差】

主驱动一经成本传导至P；主驱动二影响Y/OI。最强反证：外盘反向且库存累积。

## 【风险提示】

若P跌破区间，判断失效。
"""
        outline = {
            "market_stance": "震荡",
            "top_call": "等待供需共振",
            "transmission_chain": "库存变化→基差→P/Y/OI分化",
            "strongest_counter_case": "外盘反向且库存累积",
            "invalidation_condition": "P跌破区间",
        }
        updated = MODULE.ensure_daily_audit_contracts(markdown, outline, "daily")
        self.assertNotIn("传导链：库存变化", updated)
        self.assertEqual(updated.count("最强反证"), 1)
        self.assertNotIn("可检验失效条件", updated)

    def test_daily_key_data_recognizes_existing_icdx_quote(self) -> None:
        markdown = """# 09月02日晨报

## 【关键数据与价格】

|指标|数值|时点|含义|
|---|---|---|---|
|印尼ICDX CPOTR|16580|2026-09-01|产地外盘|

## 【开盘推演】
"""
        updated = MODULE.ensure_daily_external_key_data(
            markdown,
            {"external": {"indonesia_cpo_spot": {"status": "ok", "price": 16580}}},
            "daily",
        )
        self.assertEqual(updated, markdown)

    def test_daily_key_data_adds_official_fact_without_exceeding_eight_rows(self) -> None:
        markdown = """# 09月03日晨报

## 【关键数据与价格】

|指标|数值|时点|含义|
|---|---|---|---|
|P2701|10235|2026-09-03|主线|
|Y2701|9142|2026-09-03|共振|
|OI2611|10334|2026-09-02|轮动|
|印尼ICDX CPOTR|16580|2026-09-01|外盘|
|豆棕价差|-1093|2026-09-02|估值|
|SPPOMA马棕产量|-3.74%|2026-08|供给|
|印度棕榈油进口|78万吨|2026-08|需求|
|P上方观察位|10489.31|2026-09-03|关键位|

## 【开盘推演】
"""
        source = {
            "fundamental": {
                "official_supply_demand": {
                    "latest_metrics": {
                        "stocks": {
                            "value": 2628326,
                            "unit": "tonnes",
                            "period": "2026-07",
                            "published_at": "2026-08-10",
                        }
                    }
                }
            }
        }
        updated = MODULE.ensure_daily_official_key_data(markdown, source, "daily")
        section = updated.split("## 【关键数据与价格】", 1)[1].split("## 【开盘推演】", 1)[0]
        self.assertIn("|MPOB期末库存|2628326吨|2026-07，2026-08-10发布|官方供需背景|", section)
        self.assertEqual(sum(1 for line in section.splitlines() if line.startswith("|")) - 2, 7)
        self.assertNotIn("SPPOMA马棕产量", section)
        self.assertNotIn("印度棕榈油进口", section)

    def test_daily_execution_compactor_keeps_full_p_outline_fields(self) -> None:
        markdown = """# 09月03日晨报

## 【今日交易信号】

今日策略：震荡。

|品种|方向|触发|确认|止损|目标|仓位上限|信号有效期|
|---|---|---|---|---|---|---|---|
|P2701|震荡|现价 10235；区间内等待驱动与资金确认|若价格突破区间且驱动/资金同向，震荡判断失效。|下方观察位 9467.87|上方观察位 10489.31 / 下方观察位 9467.87|源数据未给出，不新开仓|源数据未给出，不新开仓|
|Y2701|震荡|现价 9142；区间内等待驱动与资金确认|若价格突破区间且驱动/资金同向，震荡判断失效。|下方观察位 8317.96|上方观察位 9245.47 / 下方观察位 8317.96|源数据未给出，不新开仓|源数据未给出，不新开仓|
|OI2611|震荡|现价 10334；区间内等待驱动与资金确认|若价格突破区间且驱动/资金同向，震荡判断失效。|下方观察位 9874.38|上方观察位 10763.78 / 下方观察位 9874.38|源数据未给出，不新开仓|源数据未给出，不新开仓|

## 【核心驱动与预期差】
"""
        updated = MODULE.compact_daily_execution_table(markdown, "daily")
        self.assertIn("|品种|方向|触发|确认|止损|目标|仓位上限|信号有效期|", updated)
        self.assertIn("|P2701|震荡|10235，待确认|驱动/资金同向|9467.87|10489.31/9467.87|不新开仓|未给出/不开仓|", updated)
        self.assertIn("|Y2701|震荡|9142，待确认|驱动/资金同向|8317.96|9245.47/8317.96|不新开仓|未给出/不开仓|", updated)
        self.assertIn("|OI2611|震荡|10334，待确认|驱动/资金同向|9874.38|10763.78/9874.38|不新开仓|未给出/不开仓|", updated)

    def test_daily_source_audit_groups_ready_sources_and_preserves_disclosure(self) -> None:
        markdown = """# 09月03日晨报

## 【信息来源与核验说明】

实际 skill：market_data_skill、data_quality_gate_skill、forecast_generation_feedback、oil_report_freshness、report_writer_skill、headline_skill、report_quality_gate、forecast_tracking_skill。数据源：AkShare、ICDX官方历史价格接口、机构资讯·油脂油料快讯、MPOB/GAPKI/USDAofficialchecks、跨站新闻·GoogleNews。截止时间：2026-09-02T21:45:54+08:00。失败项：MPOB/GAPKI/USDAofficialchecks为source_error；替代来源：AkShare。来源状态：来源甲 ready；来源乙 ready。机构资讯仅作交叉验证。需进一步核验：FCPO行情口径。

预测披露原句。

## 【消息来源链接】
"""
        source = {
            "news_and_research_evidence": {
                "source_status": [
                    {"name": "来源甲", "state": "ready"},
                    {"name": "来源乙", "state": "ready"},
                ]
            }
        }
        updated = MODULE.compact_daily_source_audit(
            markdown,
            source,
            {"required_report_disclosures": ["预测披露原句。"]},
            "daily",
        )
        self.assertIn("来源状态：来源甲、来源乙=可用", updated)
        self.assertIn("实际 skill：行情采集→数据门禁→预测反馈→新鲜度治理→正文写作→标题门→报告审计→预测冻结", updated)
        self.assertIn(
            "数据源：AkShare、ICDX官方历史、机构油脂快讯、官方供需检查、跨站新闻",
            updated,
        )
        self.assertIn("失败项：供需检查失败", updated)
        self.assertEqual(updated.count("预测披露原句。"), 1)
        self.assertEqual(
            MODULE.compact_daily_source_audit(
                updated,
                source,
                {"required_report_disclosures": ["预测披露原句。"]},
                "daily",
            ),
            updated,
        )
        weekly = MODULE.compact_daily_source_audit(markdown, source, None, "weekend")
        self.assertIn("来源状态：来源甲、来源乙=可用", weekly)
        self.assertIn("实际 skill：行情采集→数据门禁→新鲜度治理→正文写作→标题门→报告审计", weekly)

    def test_weekly_source_audit_removes_duplicate_status_tail_from_verification_note(self) -> None:
        markdown = """# 09月03日周报

## 【信息来源与核验说明】

实际 skill：market_data_skill、data_quality_gate_skill、oil_report_freshness、report_writer_skill、headline_skill、report_quality_gate。数据源：AkShare、ICDX官方历史价格接口、MPOB历史数据、Open-Meteo、HTFCTianji。截止时间：2026-09-03T17:36:21+08:00。失败项：官方供需检查为source_error、FCPO行情缺失、行情skill非JSON。替代来源：官方供需沿用上次成功MPOB数据。来源状态：来源甲 ready；来源乙 ready。机构资讯仅作交叉验证。需进一步核验：上述缺口仅降低置信度并增加反证，不提升结论。来源状态：来源甲=ready（扫描100条、纳入0条）；来源乙=ready（检索1条、纳入0条）。HTFC研报模块=unavailable。

## 【消息来源链接】
"""
        source = {
            "news_and_research_evidence": {
                "source_status": [
                    {"name": "来源甲", "state": "ready"},
                    {"name": "来源乙", "state": "ready"},
                ]
            }
        }
        updated = MODULE.compact_daily_source_audit(markdown, source, None, "weekend")
        self.assertEqual(updated.count("来源状态："), 1)
        self.assertIn("需进一步核验：上述缺口仅降低置信度并增加反证，不提升结论", updated)
        self.assertNotIn("扫描100条", updated)
        self.assertNotIn("HTFC研报模块=unavailable", updated)

    def test_daily_key_data_compactor_only_shortens_explanatory_meanings(self) -> None:
        markdown = """# 09月03日晨报

## 【关键数据与价格】

|指标|数值|时点|含义|
|---|---|---|---|
|P2701|10235|2026-09-03|P主叙事|
|ICDX CPOTR|16580|2026-09-01|外盘交叉验证，不替代国内行情|
|MPOB期末库存|2628326吨|2026-07|官方供需背景|

## 【开盘推演】
"""
        updated = MODULE.compact_daily_key_data_table(markdown, "daily")
        self.assertIn("|P2701|10235|09-03|P主线|", updated)
        self.assertIn("|ICDX CPOTR|16580|09-01|外盘参照|", updated)
        self.assertIn("|MPOB期末库存|2628326吨|2026-07|供应背景|", updated)

    def test_daily_key_data_compactor_removes_repeated_year_not_date_context(self) -> None:
        markdown = """# 09月03日晨报

## 【关键数据与价格】

|指标|数值|时点|含义|
|---|---|---|---|
|P2701|10186|2026-09-02最近完整收盘|P主线|
|印尼CPOTR SEP26|16650|2026-09-02|外盘参照|
|MPOB期末库存|2628326吨|2026-07，2026-08-10发布|供应背景|
|P关键位|下方观察位9467.87|2026-09-03策略结果|失效观察|

## 【开盘推演】
"""
        updated = MODULE.compact_daily_key_data_table(markdown, "daily")
        self.assertIn("|P2701|10186|09-02收盘|P主线|", updated)
        self.assertIn("|印尼CPOTR|16650|09-02|外盘参照|", updated)
        self.assertIn("|MPOB期末库存|2628326吨|2026-07，08-10发布|供应背景|", updated)
        self.assertIn("|P关键位|观察位9467.87|09-03策略|失效观察|", updated)

    def test_daily_scenario_compactor_restores_contract_header(self) -> None:
        markdown = """# 09月03日晨报

## 【开盘推演】

|情景|触发|确认|动作|放弃|
|---|---|---|---|---|
|高开|P高开|Y/OI同步|等待确认|背离|
|平开|P平开|Y/OI同步|震荡观察|背离|
|低开|P低开|Y/OI同步|不新开仓|背离|

## 【风险提示】
"""
        updated = MODULE.compact_daily_scenario_table(markdown, "daily")
        self.assertIn("|情景|触发|确认|动作|放弃条件|", updated)
        self.assertIn("|高开|P高开|Y/OI同步|P等确认|Y/OI背离|", updated)

    def test_daily_risk_compactor_keeps_exact_outline_invalidation(self) -> None:
        markdown = """# 09月03日晨报

## 【风险提示】

供应恢复是反证。可检验失效条件：若P跌破区间，判断失效。

## 【信息来源与核验说明】
"""
        updated = MODULE.compact_daily_risk(
            markdown,
            {"invalidation_condition": "若P跌破区间，判断失效。"},
            "daily",
        )
        self.assertIn("## 【风险提示】\n\n若P跌破区间，判断失效。", updated)
        self.assertNotIn("供应恢复是反证", updated)

    def test_daily_compactors_are_idempotent_on_short_headers(self) -> None:
        markdown = """# 09月03日晨报

## 【今日交易信号】

今日策略：震荡。
重复解释。
|品种|方向|触发|确认|止损|目标|仓位|有效期|
|---|---|---|---|---|---|---|---|
|P2701|震荡|现价10235；待确认|驱动/资金同向|下9467.87|上10489.31/下9467.87|未给出，不开仓|未给出，不开仓|
|Y2701|震荡|现价9142|驱动/资金同向|下8317.96|上9245.47/下8317.96|不开仓|不开仓|
|OI2611|震荡|现价10334|驱动/资金同向|下9874.38|上10763.78/下9874.38|不开仓|不开仓|

## 【核心驱动与预期差】
"""
        once = MODULE.compact_daily_execution_table(markdown, "daily")
        twice = MODULE.compact_daily_execution_table(once, "daily")
        self.assertEqual(once, twice)
        self.assertNotIn("重复解释", once)
        self.assertIn("|品种|方向|触发|确认|止损|目标|仓位上限|信号有效期|", once)
        self.assertIn("|P2701|震荡|10235，待确认|驱动/资金同向|", once)

    def test_daily_top_call_and_driver_remove_only_cross_section_repetition(self) -> None:
        outline = {
            "top_call": "油脂供需线索偏多，但盘面仍以震荡应对。",
            "market_stance": "震荡",
            "research_confidence": "★★☆☆☆",
            "invalidation_condition": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        }
        markdown = """# 09月03日晨报

## 【今日观点】

油脂维持震荡。

P/Y/OI未共振，油脂震荡，若价格突破区间且驱动/资金同向，震荡判断失效。

行动：按交易信号表执行；失效：若价格突破区间且驱动/资金同向，震荡判断失效。置信度：★★☆☆☆。

## 【核心驱动与预期差】

主驱动一：机构资讯·油脂油料快讯给出供给证据。主驱动二：机构资讯·油脂油料快讯给出需求证据。最强反证：供应恢复。若价格突破区间且驱动/资金同向，震荡判断失效。

## 【风险提示】
"""
        updated = MODULE.compact_daily_top_call(markdown, outline, "daily")
        updated = MODULE.compact_daily_driver_repetition(updated, outline, "daily")
        self.assertIn(
            "油脂供需线索偏多，但盘面仍以震荡应对。\n\n"
            "行动：按信号表执行；失效：突破区间且驱动/资金同向；置信度：★★☆☆☆。",
            updated,
        )
        top_call = updated.split("## 【今日观点】", 1)[1].split("## 【核心驱动与预期差】", 1)[0]
        first_row = next(line.strip() for line in top_call.splitlines() if line.strip())
        self.assertLessEqual(len("".join(first_row.split())), 50)
        self.assertNotIn("行动：", first_row)
        self.assertIn("主驱动一", updated)
        self.assertIn("主驱动二：同源快讯", updated)
        self.assertIn("最强反证", updated)
        self.assertEqual(updated.count("震荡判断失效"), 1)

    def test_daily_driver_keeps_only_final_grounded_counter_case(self) -> None:
        outline = {"invalidation_condition": "若价格突破区间，判断失效。"}
        markdown = """# 09月03日晨报

## 【核心驱动与预期差】

主驱动一：供给预期传导P。主驱动二：需求现实影响Y/OI。最强反证是早期概括；若价格突破区间，判断失效。最强反证：库存与需求同时逆转。

## 【关键数据与价格】
"""
        updated = MODULE.compact_daily_driver_repetition(markdown, outline, "daily")
        self.assertEqual(updated.count("最强反证"), 1)
        self.assertIn("最强反证：库存与需求同时逆转。", updated)
        self.assertNotIn("早期概括", updated)

    def test_daily_top_call_does_not_restore_overlong_outline_headline(self) -> None:
        markdown = """# 09月03日晨报

## 【今日观点】

油脂分化等待供需验证。

## 【今日交易信号】
"""
        outline = {
            "top_call": "油脂市场供需线索仍待连续数据与跨市场价格结构共同确认" * 2,
            "market_stance": "观望",
            "position_limit": "不新开仓",
            "research_confidence": "★★☆☆☆",
            "invalidation_condition": "若驱动与资金同向则判断失效",
        }
        updated = MODULE.compact_daily_top_call(markdown, outline, "daily")
        section = updated.split("## 【今日观点】", 1)[1].split("## 【今日交易信号】", 1)[0]
        rows = [line.strip() for line in section.splitlines() if line.strip()]
        self.assertEqual(rows[0], "油脂分化等待供需验证，观望。")
        self.assertLessEqual(len("".join(rows[0].split())), 50)
        self.assertIn("行动：不新开仓", rows[1])

    def test_daily_driver_preserves_distinct_invalidation_after_duplicate_counter(self) -> None:
        outline = {"invalidation_condition": "若价格突破区间，判断失效。"}
        markdown = """# 09月03日晨报

## 【核心驱动与预期差】

主驱动一：供给传导P。主驱动二：需求影响Y/OI。最强反证是早期概括；若供需共同转弱，基准失效。最强反证：库存与需求同时逆转。

## 【关键数据与价格】
"""
        updated = MODULE.compact_daily_driver_repetition(markdown, outline, "daily")
        self.assertEqual(updated.count("最强反证"), 1)
        self.assertIn("若供需共同转弱，基准失效。", updated)

    def test_daily_driver_outline_renderer_keeps_audited_contracts_in_budget(self) -> None:
        primary = "主驱动一（Level 1，基本面）：机构资讯·油脂油料快讯于9月2日11:03称，供给数据下降3.74%、单产下降4.53%。"
        secondary = "主驱动二（Level 1）：机构资讯·油脂油料快讯于9月2日15:28称，需求增长7%至78万吨。"
        filler = "市场已经交易部分预期，但仍有大量重复解释需要压缩。" * 8
        markdown = f"# 报告\n\n## 【核心驱动与预期差】\n\n{primary}{filler}\n\n{secondary}{filler}\n\n## 【关键数据与价格】\n"
        outline = {
            "transmission_chain": "供给收缩→产地库存→FCPO→P，并影响Y/OI",
            "expectation_vs_reality": "预期供应收紧，现实价格尚未共振",
            "strongest_counter_case": "港口库存上升且产量减幅不能延续",
            "invalidation_condition": "若价格突破区间且驱动/资金同向，震荡判断失效",
        }
        updated = MODULE.compact_daily_driver_repetition(markdown, outline, "daily")
        section = updated.split("## 【核心驱动与预期差】", 1)[1].split("## 【关键数据与价格】", 1)[0]
        visible = len("".join(section.split()))
        self.assertGreaterEqual(visible, 350)
        self.assertLessEqual(visible, 380)
        self.assertIn("机构资讯·油脂油料快讯", section)
        self.assertNotIn("11:03", section)
        self.assertNotIn("15:28", section)
        self.assertIn("同日", section)
        self.assertIn("供给收缩→产地库存→FCPO→P，并影响Y/OI", section)
        self.assertIn("最强反证：港口库存上升且产量减幅不能延续", section)

    def test_daily_driver_compactor_fills_short_section_from_audited_outline(self) -> None:
        short_driver = (
            "主驱动一：天气变化影响美豆单产预期并传导Y。"
            "主驱动二：产区供应稳定限制P上行，OI跟随替代关系。"
            + "已核验事实与市场现实仍有分化，需等待盘面共同确认。" * 11
        )
        markdown = (
            f"# 报告\n\n## 【核心驱动与预期差】\n\n{short_driver}"
            "\n\n## 【关键数据与价格】\n"
        )
        outline = {
            "transmission_chain": "天气→美豆单产→CBOT豆油→Y→P/OI",
            "expectation_vs_reality": "市场预期风险升温，现实是三油仍未共振",
            "strongest_counter_case": "产区天气转稳且供应恢复",
            "invalidation_condition": "若三油与资金同向突破则震荡判断失效",
        }
        updated = MODULE.compact_daily_driver_repetition(markdown, outline, "daily")
        section = updated.split("## 【核心驱动与预期差】", 1)[1].split(
            "## 【关键数据与价格】", 1
        )[0]
        visible = len("".join(section.split()))
        self.assertGreaterEqual(visible, 350)
        self.assertLessEqual(visible, 380)
        self.assertTrue(any(value in section for value in outline.values()))

    def test_daily_driver_uses_safe_evidence_boundary_when_core_fields_are_present(self) -> None:
        outline = {
            "transmission_chain": "天气→单产→CBOT豆油→Y→P/OI",
            "expectation_vs_reality": "天气预期升温但三油现实仍未共振",
            "strongest_counter_case": "天气恢复且作物评级未下修",
            "invalidation_condition": "若价格与资金同向突破则震荡失效",
            "evidence_status": {
                "limited": ["官方供需检查source_error"],
                "needs_verification": ["FCPO价格", "天气覆盖与土壤墒情"],
            },
        }
        body = (
            "主驱动一：天气变化影响单产。主驱动二：现货报价影响近端预期。"
            f"传导：{outline['transmission_chain']}。"
            f"预期/现实：{outline['expectation_vs_reality']}。"
            f"最强反证：{outline['strongest_counter_case']}。"
            f"失效：{outline['invalidation_condition']}。"
        )
        filler = "盘面分化说明预期尚未转化为一致定价。"
        while len("".join(body.split())) < 330:
            body += filler
        markdown = f"# 报告\n\n## 【核心驱动与预期差】\n\n{body}\n\n## 【关键数据与价格】\n"
        updated = MODULE.compact_daily_driver_repetition(markdown, outline, "daily")
        section = updated.split("## 【核心驱动与预期差】", 1)[1].split(
            "## 【关键数据与价格】", 1
        )[0]
        visible = len("".join(section.split()))
        self.assertGreaterEqual(visible, 350)
        self.assertLessEqual(visible, 380)
        self.assertIn("待核验：", section)
        self.assertNotIn("source_error", section)

    def test_daily_driver_depth_restores_previous_grounded_section(self) -> None:
        previous_driver = "主驱动一：" + "供给收缩→P支撑，预期与现实待验证。" * 20 + "主驱动二：需求恢复。最强反证：供应回升。"
        current = "# 报告\n\n## 【核心驱动与预期差】\n\n主驱动一：过短。主驱动二：过短。\n\n## 【关键数据与价格】\n"
        previous = f"# 报告\n\n## 【核心驱动与预期差】\n\n{previous_driver}\n\n## 【关键数据与价格】\n"
        restored = MODULE.preserve_daily_driver_depth(current, previous, "daily")
        self.assertIn(previous_driver, restored)

    def test_daily_key_data_copies_external_quote_from_source_without_calculation(self) -> None:
        markdown = """# 08月24日晨报

## 【关键数据与价格】

|指标|数值|时点|含义|
|---|---|---|---|
|P2701|10171|2026-08-28|国内行情|

## 【开盘推演】
"""
        source = {
            "timestamp": "2026-09-02T00:05:00+08:00",
            "external": {
                "bmd_palm_oil": {
                    "name": "BMD棕榈油",
                    "status": "ok",
                    "price": 4432.5,
                    "fetched_at": "2026-09-01",
                }
            },
        }
        updated = MODULE.ensure_daily_external_key_data(markdown, source, "daily")
        self.assertIn("|BMD棕榈油|4432.5|2026-09-01|外盘交叉验证，不替代国内行情|", updated)
        self.assertNotIn("涨跌", updated)

    def test_daily_key_data_does_not_duplicate_existing_external_quote(self) -> None:
        markdown = """# 08月24日晨报

## 【关键数据与价格】

|指标|数值|时点|含义|
|---|---|---|---|
|FCPO|4432.5|2026-09-01|外盘|

## 【开盘推演】
"""
        updated = MODULE.ensure_daily_external_key_data(
            markdown,
            {"external": {"bmd_palm_oil": {"status": "ok", "price": 4432.5}}},
            "daily",
        )
        self.assertEqual(updated, markdown)

    def test_weekly_audit_contracts_never_fabricate_previous_validation(self) -> None:
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
        self.assertEqual(updated, markdown)
        self.assertNotIn("部分兑现、仍待确认", updated)

    def test_weekly_existing_view_only_gets_missing_iso_date(self) -> None:
        markdown = """# 08月24日周报

## 【本周验证与预期差】

上一期为08月23日周报，核心判断是“油脂维持震荡。”本期部分兑现。

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
        self.assertIn("上一期报告：2026-08-23，08月23日周报。", updated)
        self.assertEqual(updated.count("油脂维持震荡"), 1)

    def test_weekly_previous_reference_uses_exact_audited_title(self) -> None:
        markdown = """# 09月03日周报

## 【本周验证与预期差】

上一期2026-08-02周报判断油脂偏弱，本期部分兑现。

## 【核心数据变化】
"""
        updated = MODULE.ensure_weekly_previous_validation(
            markdown,
            {
                "research_history": {
                    "previous_report": {
                        "date": "2026-08-02-weekend",
                        "title": "08月02日周报",
                        "headline": "油脂偏弱。",
                    }
                }
            },
            "weekend",
        )
        self.assertIn("上一期报告：2026-08-02，08月02日周报。", updated)
        self.assertIn("本期部分兑现", updated)

    def test_weekly_postprocessors_restore_audited_contracts_and_budget(self) -> None:
        markdown = """# 09月03日周报

## 【一句话核心观点】

出口走弱与油脂分化下维持震荡判断。

基准方向：震荡；区间内等待确认；研究置信度：中。

## 【本周验证与预期差】

上一期2026-08-02周报判断油脂偏弱，本期部分兑现。""" + ("补足正文。" * 360) + """

## 【交易计划】

|品种|方向|触发|确认|止损|目标|仓位上限|信号有效期|
|---|---|---|---|---|---|---|---|
|P2701|震荡，不新开仓|现价10289；区间内等待驱动与资金确认|区间内等待驱动与资金确认|下方观察位9467.87|上方观察位10499.32 / 下方观察位9467.87|源数据未给出，不新开仓|源数据未给出，不新开仓|
|Y2701|震荡，不新开仓|现价9113；区间内等待驱动与资金确认|区间内等待驱动与资金确认|下方观察位8317.96|上方观察位9240.04 / 下方观察位8317.96|源数据未给出，不新开仓|源数据未给出，不新开仓|
|OI2611|震荡，不新开仓|现价10370；区间内等待驱动与资金确认|区间内等待驱动与资金确认|下方观察位10144.76|上方观察位10595.24 / 下方观察位10144.76|源数据未给出，不新开仓|源数据未给出，不新开仓|

## 【风险提示】

旧的泛化风险提示。

## 【消息来源链接】
"""
        outline = {
            "market_stance": "震荡",
            "research_confidence": "★★★☆☆",
            "strongest_counter_case": "印度棕榈油进口持续增强并带动三油同向。",
            "invalidation_condition": "若价格突破区间且驱动/资金同向，震荡判断失效。",
        }
        updated = MODULE.ensure_visible_confidence(markdown, outline, "weekend")
        updated = MODULE.compact_weekly_top_call(updated, outline, "weekend")
        updated = MODULE.compact_weekly_risk(updated, outline, "weekend")
        before = MODULE.visible_report_body_chars(updated)
        updated = MODULE.compact_weekly_execution_table(updated, "weekend")
        self.assertIn("研究置信度：★★★☆☆", updated)
        self.assertIn("最强反证：印度棕榈油进口持续增强并带动三油同向。", updated)
        self.assertIn("失效条件：若价格突破区间且驱动/资金同向，震荡判断失效。", updated)
        self.assertIn("|P2701|震荡/不开仓|10289待确认|驱动/资金确认|9467.87|10499.32/9467.87|不开仓|未给出|", updated)
        self.assertLess(MODULE.visible_report_body_chars(updated), before)

    def test_report_punctuation_is_normalized(self) -> None:
        self.assertEqual(MODULE.normalize_report_punctuation("失效。；等待。。"), "失效；等待。")

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

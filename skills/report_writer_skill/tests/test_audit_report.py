import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_PATH = ROOT / "skills" / "report_writer_skill" / "scripts" / "audit_report.py"
SPEC = importlib.util.spec_from_file_location("report_writer_audit", AUDIT_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def source_payload() -> dict:
    return {
        "date": "2026-07-27",
        "timestamp": "2026-07-27T08:22:31",
        "domestic": {
            "soybean_oil": {"name": "豆油", "price": 8609.0, "change_pct": -0.13},
            "palm_oil": {"name": "棕榈油", "price": 9515.0, "change_pct": -0.57},
            "rapeseed_oil": {"name": "菜油", "price": 10191.0, "change_pct": -0.88},
        },
        "external": {
            "bmd_palm_oil": {"name": "BMD 棕油", "price": 4723.0, "change_pct": 0.04},
        },
        "fundamental": {
            "spread": {
                "soybean_palm_spread": {"name": "豆棕价差", "price": -906.0},
                "rapeseed_soybean_spread": {"name": "菜豆油价差", "price": 1582.0},
            },
            "cross_drivers": {
                "crude_oil": {"name": "WTI 原油", "price": 84.51, "change_pct": -5.37},
            },
        },
        "news_and_research_evidence": {
            "today_new_drivers": [
                {
                    "source": "BMD",
                    "title": "FCPO收盘保持韧性",
                    "mainline_eligible": True,
                }
            ],
            "source_status": [
                {"name": "BMD", "state": "ready"},
                {"name": "DCE", "state": "ready"},
            ],
        },
    }


def outline_payload() -> dict:
    return {
        "schema_version": "oil-report-outline-v1",
        "report_date": "2026-07-27",
        "kind": "daily",
        "data_cutoff": "2026-07-27T08:22:31+08:00",
        "top_call": "外盘支撑尚未传导至内盘，确认后再偏多",
        "market_stance": "偏多",
        "primary_driver": {
            "name": "FCPO相对坚挺",
            "evidence_level": "Level 1",
            "source": "BMD",
            "as_of": "2026-07-24 17:59",
            "impact": "支撑进口成本",
        },
        "secondary_driver": {
            "name": "内盘油脂分化",
            "evidence_level": "Level 1",
            "source": "DCE",
            "as_of": "2026-07-27 08:22",
            "impact": "限制追涨空间",
        },
        "transmission_chain": "FCPO坚挺→进口成本上移→P获得支撑",
        "expectation_vs_reality": "预期交易供应收紧，现实尚待内盘确认",
        "strongest_counter_case": "原油急跌并引发外盘油脂回落",
        "invalidation_condition": "P跌破9480且Y/OI同步走弱",
        "trade_trigger": "P上破9510元/吨",
        "confirmation_condition": "P站稳9520元/吨",
        "stop_loss": "P跌破9480元/吨",
        "target_range": "9600-9650元/吨",
        "position_limit": "20%",
        "signal_expiry": "2026-07-27 11:30",
        "research_confidence": "★★☆☆☆",
        "evidence_status": {
            "verified": ["P/Y/OI盘前快照", "FCPO收盘"],
            "limited": ["库存频率较低"],
            "needs_verification": ["开盘资金确认"],
        },
    }


DISCLOSURE = (
    "预测校准：近5个有效交易日共15条评估，P/Y/OI方向命中率分别为20.0%/20.0%/20.0%，"
    "整体Brier分数0.377，收盘区间覆盖率100.0%，区间宽度质量暂无可复现指标；"
    "P/Y/OI今日主线降级，核心置信度不高于★★☆☆☆；样本仍有限，不据此声称准确率改善。"
)


def valid_report() -> str:
    report = f"""# 07月27日晨报

## 【今日观点】

外盘待确认，偏多仅触发后执行；支撑失守则失效。置信度：★★☆☆☆。

## 【今日交易信号】

今日策略：偏多。P/Y/OI强弱取决于开盘确认。

| 品种 | 方向 | 触发 | 确认 | 止损 | 目标 | 仓位上限 | 信号有效期 |
|---|---|---|---|---|---|---|---|
| P | 偏多 | 9510元/吨 | 9520元/吨 | 9480元/吨 | 9600-9650元/吨 | 20% | 2026-07-27 11:30 |
| Y | 观望 | 与P同步走强 | 成交确认 | 反向走弱 | 源数据未给出 | 不新开仓 | 日内 |
| OI | 观望 | 与P同步走强 | 成交确认 | 反向走弱 | 源数据未给出 | 不新开仓 | 日内 |

## 【核心驱动与预期差】

主驱动一：截至2026-07-24 17:59，FCPO 4723点保持相对韧性，进口成本→国内盘面支撑→P确认后偏强。它说明产地报价尚未跟随内盘转弱，进口成本对P构成下方约束，但不能直接推出国内需求改善；市场已交易外盘韧性，尚未定价的是开盘后国内买盘是否承接，这需要成交和持仓共同核验。主驱动二：截至2026-07-27 08:22的内盘分化限制单边追价。P、Y、OI没有形成同步确认，意味着资金更可能交易品种相对强弱，而不是油脂板块一致趋势。市场预期供应收紧，现实是内盘尚未确认，当前定价并不充分。只有P触发后Y与OI同步走强，成本支撑才会从预期转化为现实，否则继续按区间而非趋势处理。最强反证是原油急跌并引发外盘油脂回落；原油下行会沿生柴估值链压低植物油需求溢价，若同时出现P跌破关键支撑与Y/OI转弱，该情景会推翻偏多判断。

## 【关键数据与价格】

| 指标 | 数值 | 时点 | 含义 |
|---|---:|---|---|
| P主力 | 9515元/吨 | 2026-07-27 08:22 | 支撑待确认 |
| Y主力 | 8609元/吨 | 2026-07-27 08:22 | 与P存在分化 |
| OI主力 | 10191元/吨 | 2026-07-27 08:22 | 与P存在分化 |
| BMD FCPO | 4723点 | 2026-07-24 17:59 | 成本支撑 |
| WTI原油 | 84.51美元/桶 | 2026-07-27 08:22 | 生柴承压 |
| 豆棕价差 | -906元/吨 | 2026-07-27 08:22 | P相对偏强 |
| 菜豆价差 | 1582元/吨 | 2026-07-27 08:22 | OI相对溢价 |
| P止损关键位 | 9480元/吨 | 2026-07-27日内 | 失守则放弃偏多 |
| P目标关键位 | 9600-9650元/吨 | 2026-07-27日内 | 触及后不追价 |

## 【开盘推演】

| 情景 | 触发 | 确认 | 动作 | 放弃条件 |
|---|---|---|---|---|
| 高开 | P上破9510 | 站稳9520且Y/OI同步 | 按20%上限执行 | Y/OI背离或P回落 |
| 平开 | P测试9510 | 成交及Y/OI同步确认 | 确认后执行 | 迟迟未确认则观望 |
| 低开 | P接近9480 | Y/OI同步走弱 | 不新开仓 | P收复且Y/OI转强前放弃 |

## 【风险提示】

原油急跌或P跌破9480且Y/OI同步走弱，判断失效；外盘口径变化时先核验。

## 【信息来源与核验说明】

实际 skill（执行链）：行情采集→数据门禁→预测反馈→新鲜度治理→正文写作→标题门→报告审计→预测冻结。数据源：DCE盘前快照、BMD和结构化行情。截止时间：2026-07-27 08:22。失败项：无。替代来源：无。需进一步核验：开盘资金确认。

{DISCLOSURE}

## 【消息来源链接】

| 来源 | 用途 | 链接 |
|---|---|---|
| DCE | 内盘行情 | https://www.dce.com.cn/ |

## 【AI观点风险提示】

本报告由AI基于公开信息、已调用数据源和既定研究框架生成，仅代表生成时点的研究判断，不构成投资建议或交易指令。期货价格波动较大，客户应结合自身风险承受能力独立决策。
"""
    count = audit.visible_body_chars(report)
    if count < 1050:
        filler = "研究补充说明资金与价差需要共同确认否则不改变基准判断"
        report = report.replace("市场预期", filler * ((1050 - count) // len(filler) + 1) + "。市场预期")
    return report


class AuditReportTest(unittest.TestCase):
    def test_fresh_event_display_alias_is_auditable_but_empty_value_is_not(self) -> None:
        item = {
            "source": "机构资讯·油脂油料快讯",
            "title": "9月3日国内棕榈油现货报价再度上涨",
        }
        self.assertTrue(audit._fresh_event_used(item, "主驱动二：机构油脂快讯称现货走强。"))
        self.assertFalse(audit._fresh_event_used(item, "主驱动二：某机构称现货走强。"))
        self.assertFalse(audit._fresh_event_used({"source": "", "title": ""}, "任意正文"))

    def test_concrete_contract_is_added_as_numeric_alias(self) -> None:
        payload = {
            "domestic": {
                "palm_oil": {
                    "name": "棕榈油",
                    "contract": "P2701",
                    "price": 10171.0,
                    "change_pct": 1.25,
                }
            }
        }
        records = audit._flatten_records(payload)
        palm = next(record for record in records if record.key == "domestic.palm_oil")
        self.assertIn("P2701", palm.aliases)

    def test_previous_source_snapshot_is_not_a_current_numeric_record(self) -> None:
        records = audit._flatten_records(
            {
                "domestic": {"palm_oil": {"contract": "P2701", "price": 10171}},
                "research_history": {
                    "previous_source_snapshot": {
                        "domestic": {"palm_oil": {"contract": "P2609", "price": 9000}}
                    }
                },
            }
        )
        self.assertEqual([record.price for record in records], [10171.0])

    def test_integral_prices_accept_decimal_zero_formatting(self) -> None:
        pattern = audit._number_pattern(8819.0)
        self.assertIsNotNone(pattern.search("豆油 8819.0"))
        self.assertIsNotNone(pattern.search("豆油 8,819.00"))
        self.assertIsNone(pattern.search("豆油 8819.5"))

    def test_indonesia_and_mpob_records_have_report_aliases(self) -> None:
        records = audit._flatten_records(
            {
                "external": {"indonesia_cpo_spot": {"name": "印尼棕榈油", "price": 16580}},
                "fundamental": {
                    "official_supply_demand": {
                        "latest_metrics": {
                            "production": {"label": "CPO产量", "value": 1792979},
                            "exports": {"label": "棕榈油出口", "value": 1392178},
                            "stocks": {"label": "期末库存", "value": 2628326},
                        }
                    }
                },
            }
        )
        aliases = {record.key: record.aliases for record in records}
        self.assertIn("ICDX", aliases["external.indonesia_cpo_spot"])
        self.assertIn("MPOB产量", aliases["fundamental.official_supply_demand.latest_metrics.production"])
        self.assertIn("MPOB出口", aliases["fundamental.official_supply_demand.latest_metrics.exports"])
        self.assertIn("MPOB期末库存", aliases["fundamental.official_supply_demand.latest_metrics.stocks"])

    def test_visible_body_count_ignores_markdown_table_separators(self) -> None:
        self.assertEqual(audit.visible_body_chars("# 标题\n\n|指标|数值|\n|---|---:|\n|P|9500|"), 11)

    def environment(self) -> tuple[Path, Path, Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        report = root / "report.md"
        outline = root / "outline.json"
        source = root / "source.json"
        feedback = root / "feedback.json"
        report.write_text(valid_report(), encoding="utf-8")
        outline.write_text(json.dumps(outline_payload(), ensure_ascii=False), encoding="utf-8")
        source.write_text(json.dumps(source_payload(), ensure_ascii=False), encoding="utf-8")
        feedback.write_text(
            json.dumps({"required_report_disclosures": [DISCLOSURE]}, ensure_ascii=False),
            encoding="utf-8",
        )
        return report, outline, source, feedback

    def run_audit(self):
        report, outline, source, feedback = self.environment()
        result = audit.audit_report(report, outline, "daily", source, feedback)
        return result, report, outline, source, feedback

    def test_valid_daily_report_passes_with_reproducible_numeric_sample(self) -> None:
        result, *_ = self.run_audit()
        self.assertTrue(result["can_publish"], result)
        self.assertGreaterEqual(result["score"], 85)
        self.assertEqual(result["numeric_audit"]["critical_checked"], 3)
        self.assertEqual(len(result["numeric_audit"]["sampled_noncritical"]), 3)
        second, *_ = self.run_audit()
        self.assertEqual(
            result["numeric_audit"]["sampled_noncritical"],
            second["numeric_audit"]["sampled_noncritical"],
        )

    def test_shortened_execution_headers_are_blocked(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8")
            .replace("仓位上限 | 信号有效期", "仓位 | 有效期"),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"], result)
        self.assertTrue(any("仓位上限、信号有效期" in item for item in result["hard_failures"]))

    def test_shortened_scenario_header_is_blocked(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8").replace("动作 | 放弃条件", "动作 | 放弃"),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"], result)
        self.assertTrue(any("放弃条件" in item for item in result["hard_failures"]))

    def test_cryptic_key_data_meaning_is_blocked(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8").replace("| 支撑待确认 |", "| P |"),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"], result)
        self.assertTrue(any("关键数据表含义过度压缩" in item for item in result["hard_failures"]))

    def test_incomplete_visible_skill_chain_is_blocked(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8").replace("→预测冻结", ""),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"], result)
        self.assertTrue(any("缺少执行链阶段：预测冻结" in item for item in result["hard_failures"]))

    def test_critical_price_mismatch_blocks_publication(self) -> None:
        result, report, outline, source, feedback = self.run_audit()
        report.write_text(report.read_text(encoding="utf-8").replace("| P主力 | 9515", "| P主力 | 9516"), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("关键行情不一致：棕榈油" in item for item in result["hard_failures"]))

    def test_reported_spread_and_percentage_are_fully_checked(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        text = report.read_text(encoding="utf-8")
        text = text.replace("| 豆棕价差 | -906", "| 豆棕价差 | -905")
        text = text.replace("| WTI原油 | 84.51美元/桶", "| WTI原油 | 84.51美元/桶，下跌4.37%")
        report.write_text(text, encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("价差不一致：豆棕价差" in item for item in result["hard_failures"]))
        self.assertTrue(any("涨跌幅不一致：WTI 原油" in item for item in result["hard_failures"]))

    def test_direction_conflict_blocks_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(report.read_text(encoding="utf-8").replace("今日策略：偏多", "今日策略：偏空"), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("交易方向冲突" in item for item in result["hard_failures"]))

    def test_stale_policy_promoted_to_main_driver_blocks_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        payload = json.loads(outline.read_text(encoding="utf-8"))
        payload["primary_driver"]["evidence_level"] = "Level 2"
        payload["primary_driver"]["name"] = "过期政策"
        outline.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("Level 2/3" in item for item in result["hard_failures"]))

    def test_missing_forecast_disclosure_blocks_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(report.read_text(encoding="utf-8").replace(DISCLOSURE, ""), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("预测披露缺失" in item for item in result["hard_failures"]))

    def test_mechanical_repeated_conclusions_block_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(report.read_text(encoding="utf-8") + "\n【结论】\n【结论】\n【结论】\n", encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("机械性" in item for item in result["errors"]))

    def test_repeated_news_sentence_blocks_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        sentence = "国际原油显著回落通过生柴估值压制植物油风险溢价并成为盘前主驱动。"
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "## 【核心驱动与预期差】",
                f"## 【核心驱动与预期差】\n\n{sentence}\n{sentence}",
            ),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("重复长句" in item for item in result["errors"]))

    def test_repeated_strategy_table_cells_are_not_duplicate_prose(self) -> None:
        text = """## 【交易计划】

| 品种 | 失效条件 |
| --- | --- |
| P | 若价格突破区间且驱动/资金同向，震荡判断失效。 |
| Y | 若价格突破区间且驱动/资金同向，震荡判断失效。 |
| OI | 若价格突破区间且驱动/资金同向，震荡判断失效。 |
"""
        self.assertEqual(audit._duplicate_sentences(text), [])

    def test_weekly_structured_contract_helpers_accept_complete_tables(self) -> None:
        data = """| 指标 | 数值 | 统计时间 | 变化 | 含义 |
|---|---|---|---|---|
| P2701 | 9500 | 周五收盘 | 上涨 | 偏强 |
| Y2701 | 8600 | 周五收盘 | 持平 | 跟随 |
| OI2701 | 10100 | 周五收盘 | 下跌 | 分化 |
| 豆棕价差 | -900 | 周五收盘 | 收窄 | P强 |
| 菜豆油价差 | 1500 | 周五收盘 | 走阔 | OI强 |
"""
        events = """| 日期 | 事件 | 重要性 | 触发条件 |
|---|---|---|---|
| 周一 | 开盘验证 | 高 | P确认 |
| 周二 | 库存观察 | 中 | 数据发布 |
| 周三 | 出口观察 | 中 | 数据发布 |
| 周四 | 外盘联动 | 中 | FCPO波动 |
| 周五 | 周线确认 | 高 | P收盘 |
"""
        failures: list[str] = []
        audit._require_weekly_data_table(data, failures)
        audit._require_weekly_events_table(events, failures)
        self.assertEqual(failures, [])

    def test_weekly_data_table_without_change_and_meaning_is_blocked(self) -> None:
        failures: list[str] = []
        audit._require_weekly_data_table(
            """| 指标 | 数值 |
|---|---|
| P | 9500 |
| Y | 8600 |
| OI | 10100 |
""",
            failures,
        )
        self.assertTrue(any("指标、数值、统计时间、变化和含义" in item for item in failures))

    def test_future_dated_source_record_blocks_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        payload = json.loads(source.read_text(encoding="utf-8"))
        payload["domestic"]["palm_oil"]["published_at"] = "2026-07-28"
        source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("报告日之后" in item for item in result["hard_failures"]))

    def test_source_error_cannot_be_promoted_to_driver(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "主驱动二：", "主驱动二：source_error 是当前主驱动。"
            ),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("数据源错误被升级" in item for item in result["hard_failures"]))

    def test_internal_score_cannot_be_research_driver(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        payload = json.loads(outline.read_text(encoding="utf-8"))
        payload["primary_driver"]["name"] = "基本面评分50"
        outline.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("内部评分" in item for item in result["hard_failures"]))

    def test_short_ai_disclaimer_blocks_publication(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "期货价格波动较大，客户应结合自身风险承受能力独立决策。", ""
            ),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("完整固定声明" in item for item in result["hard_failures"]))

    def test_missing_data_cannot_be_fundamental_driver(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "截至2026-07-24 17:59，FCPO 4723点保持相对韧性",
                "缺少供需增量信息，因此维持震荡",
            ),
            encoding="utf-8",
        )
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("证据缺口" in item for item in result["hard_failures"]))

    def test_august_31_low_quality_report_is_now_blocked(self) -> None:
        report = ROOT / "reports" / "2026-08-31.md"
        run_root = ROOT / "source_runs" / "2026-08-31-daily"
        result = audit.audit_report(
            report,
            run_root / "report_outline.json",
            "daily",
            run_root / "raw" / "futures_market_data.json",
            None,
        )
        self.assertFalse(result["can_publish"], result)
        joined = "\n".join(result["hard_failures"])
        self.assertIn("日报交易信号必须使用包含品种、方向、触发、确认、止损、目标、仓位上限、信号有效期", joined)
        self.assertIn("关键数据与价格必须使用包含指标、数值、时点和含义", joined)
        self.assertIn("开盘推演必须使用包含情景、触发、确认、动作、放弃条件", joined)
        self.assertIn("信息来源与核验说明缺少审计字段", joined)


if __name__ == "__main__":
    unittest.main()

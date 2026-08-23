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

外盘支撑仍需内盘确认，今日策略偏多但只在触发后执行；若关键支撑失守，基准观点失效。置信度：★★☆☆☆。

## 【今日交易信号】

今日策略：偏多。P/Y/OI强弱取决于开盘确认。

| 品种 | 触发 | 确认 | 止损 | 目标 | 仓位 | 有效期 |
|---|---:|---:|---:|---:|---:|---|
| P | 9510元/吨 | 9520元/吨 | 9480元/吨 | 9600-9650元/吨 | 20% | 2026-07-27 11:30 |

## 【核心驱动与预期差】

截至2026-07-24 17:59，FCPO 4723点保持相对韧性，进口成本→国内盘面支撑→P确认后偏强。第二驱动是截至2026-07-27 08:22的内盘分化，它限制单边追价。市场预期供应收紧，现实是内盘尚未确认，当前定价并不充分。最强反证是原油急跌并带动外盘油脂回落，该情景会推翻偏多判断。

## 【关键数据与价格】

截至2026-07-27 08:22，P主力9515元/吨、Y主力8609元/吨、OI主力10191元/吨；豆棕价差-906元/吨，菜豆价差1582元/吨。同期WTI 84.51美元/桶。数据说明外盘支撑与内盘分化并存，必须等待确认。

## 【开盘推演】

高开时等待9520站稳再执行；平开时观察9510触发及成交确认；低开时若9480失守即放弃。Y/OI同步走强才支持P延续，二者背离则压低仓位，不追赶已错过的信号。

## 【风险提示】

若原油继续急跌，生柴估值链条会削弱；若P跌破9480且Y/OI同步走弱，当前判断失效；若外盘报价口径变化，需先核验再调整结论。

## 【信息来源与核验说明】

行情截至2026-07-27 08:22，来自DCE盘前快照、BMD和结构化行情。需进一步核验：开盘资金确认。

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
        report = report.replace("第二驱动是", filler * ((1050 - count) // len(filler) + 1) + "。第二驱动是")
    return report


class AuditReportTest(unittest.TestCase):
    def test_integral_prices_accept_decimal_zero_formatting(self) -> None:
        pattern = audit._number_pattern(8819.0)
        self.assertIsNotNone(pattern.search("豆油 8819.0"))
        self.assertIsNotNone(pattern.search("豆油 8,819.00"))
        self.assertIsNone(pattern.search("豆油 8819.5"))

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

    def test_critical_price_mismatch_blocks_publication(self) -> None:
        result, report, outline, source, feedback = self.run_audit()
        report.write_text(report.read_text(encoding="utf-8").replace("P主力9515", "P主力9516"), encoding="utf-8")
        result = audit.audit_report(report, outline, "daily", source, feedback)
        self.assertFalse(result["can_publish"])
        self.assertTrue(any("关键行情不一致：棕榈油" in item for item in result["hard_failures"]))

    def test_reported_spread_and_percentage_are_fully_checked(self) -> None:
        _, report, outline, source, feedback = self.run_audit()
        text = report.read_text(encoding="utf-8")
        text = text.replace("豆棕价差-906", "豆棕价差-905")
        text = text.replace("WTI 84.51美元/桶", "WTI 84.51美元/桶，下跌4.37%")
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
                "第二驱动是", "source_error 是当前主驱动。第二驱动是"
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


if __name__ == "__main__":
    unittest.main()

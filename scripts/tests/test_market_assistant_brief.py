import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "market_assistant_brief",
    ROOT / "scripts" / "update_market_assistant_brief.py",
)
BRIEF = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BRIEF)


def source_payloads():
    return {
        "reports": [
            {
                "date": "2026-07-30",
                "headline": "油脂主线保持分化",
                "summary": "棕榈油与豆油走势不同步，等待外盘和资金共振。",
            }
        ],
        "oil-futures": {
            "updated_at": "2026-07-30 23:28",
            "update_session": "night_close",
            "contracts": [
                {
                    "product": "P",
                    "name": "棕榈油",
                    "contract": "P2609",
                    "contract_rank": 1,
                    "price": "8120",
                    "change": "+0.60%",
                    "score": {"stance": "偏强"},
                    "view": "价格偏强但外盘尚未共振。",
                }
            ],
        },
        "exchange-futures": {
            "updated_at": "2026-07-30 23:28",
            "contracts": [
                {
                    "symbol": "au",
                    "product": "黄金",
                    "price": 798.2,
                    "change_pct": 1.2,
                    "fundamental": {"summary": "贵金属波动扩大。"},
                }
            ],
        },
        "supply-demand": {
            "checked_at": "2026-07-30 06:30",
            "update_status": "no_change",
            "update_message": "今日已检查官方来源，官网暂未更新数据。",
        },
        "forecast-metrics": {
            "as_of": "2026-07-30",
            "public_display_allowed": False,
        },
        "contracts": {
            "month": "2026-07",
            "generated_at": "2026-07-30 23:20",
            "products": {"P": [], "Y": [], "OI": []},
        },
    }


def model_payload():
    return {
        "headline": "油脂与贵金属出现分化",
        "market_state": "分化",
        "summary": "棕榈油保持偏强，但跨市场共振仍需等待，官方资料没有出现新的确认信号。",
        "key_moves": [
            {
                "evidence_id": "oil:P2609",
                "interpretation": "棕榈油相对偏强，但外盘确认不足。",
            }
        ],
        "watchlist": [
            {
                "priority": "高",
                "item": "棕榈油与外盘联动",
                "trigger": "波动扩大",
                "why": "当前强弱分化，方向确认需要跨市场共振。",
                "evidence_ids": ["oil:P2609", "exchange:au"],
            }
        ],
        "actions": [
            {
                "status": "monitoring",
                "task": "监控油脂跨市场共振",
                "result": "当前只有局部走强，尚未形成一致方向。",
                "next_check": "下一次行情刷新",
            }
        ],
        "risks": ["预测评估样本不足，不能把历史结果包装成稳定能力。"],
        "confidence": "中",
    }


class MarketAssistantBriefTests(unittest.TestCase):
    def test_context_is_bounded_and_has_traceable_evidence(self):
        context = BRIEF.build_context(source_payloads())
        ids = {item["id"] for item in context["evidence"]}
        self.assertIn("oil:P2609", ids)
        self.assertIn("exchange:au", ids)
        self.assertIn("supply:official-check", ids)
        self.assertLessEqual(len(context["evidence"]), 24)
        self.assertEqual(context["fixed_logic"], ["otc_structure_library", "quant_model_rules"])

    def test_model_output_is_enriched_from_evidence_not_model_numbers(self):
        context = BRIEF.build_context(source_payloads())
        result = BRIEF.validate_and_enrich(model_payload(), context)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["update_session"], "night_close")
        self.assertEqual(result["key_moves"][0]["value"], "8120；涨跌 +0.60%")
        self.assertEqual(result["key_moves"][0]["source"], "oil-futures")

    def test_unknown_evidence_is_rejected(self):
        context = BRIEF.build_context(source_payloads())
        payload = model_payload()
        payload["key_moves"][0]["evidence_id"] = "unknown:evidence"
        with self.assertRaisesRegex(BRIEF.BriefError, "未知证据"):
            BRIEF.validate_and_enrich(payload, context)

    def test_uncontrolled_numbers_in_narrative_are_rejected(self):
        context = BRIEF.build_context(source_payloads())
        payload = model_payload()
        payload["summary"] = "棕榈油上涨百分之一，直接给出数字 1。"
        with self.assertRaisesRegex(BRIEF.BriefError, "未受控数字"):
            BRIEF.validate_and_enrich(payload, context)

    def test_automation_uses_read_only_structured_codex_and_shared_lock(self):
        generator = (ROOT / "scripts" / "update_market_assistant_brief.py").read_text(encoding="utf-8")
        deploy = (ROOT / "scripts" / "deploy_market_assistant_brief.sh").read_text(encoding="utf-8")
        installer = (ROOT / "scripts" / "install_market_assistant_launchd.sh").read_text(encoding="utf-8")
        self.assertIn('"read-only"', generator)
        self.assertIn('"--output-schema"', generator)
        self.assertIn("market-data-deploy.lock", deploy)
        self.assertIn('git add -- "$TARGET"', deploy)
        self.assertIn("<integer>900</integer>", installer)
        self.assertIn("previous valid brief remains", installer)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock


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
                    "category": "贵金属",
                    "price": 798.2,
                    "change_pct": 1.2,
                    "fundamental": {"summary": "贵金属波动扩大。"},
                }
            ],
        },
        "quant-model-signals": {
            "generated_at": "2026-07-30T23:31:00+08:00",
            "market_updated_at": "2026-07-30 23:28",
            "default_model_id": "bollinger-rsi-ma6-v1",
            "model_contracts": {
                "bollinger-rsi-ma6-v1": [
                    {
                        "symbol": "P2609",
                        "product": "P",
                        "product_name": "棕榈油",
                        "rank": 1,
                        "model_scope_label": "成熟模型映射",
                        "signals": {
                            "flat": {
                                "action": "WAIT",
                                "execution": "none",
                                "rationale": ["no new crossover"],
                            }
                        },
                    }
                ]
            },
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
        "htfc-tianji": {
            "generated_at": "2026-07-30T23:30:00+08:00",
            "modules": {
                "news_flash": {
                    "status": "ok",
                    "response": {"data": [{
                        "id": "KX1",
                        "date": "2026-07-30",
                        "time": "23:20",
                        "tagName": "油脂油料",
                        "tag2": "产业监测",
                        "content": "港口库存出现变化。",
                    }]},
                },
                "smart_kline": {
                    "status": "ok",
                    "products": {
                        "P": {
                            "status": "ok",
                            "label": {"name": "棕榈油"},
                            "response": {"code": 1, "data": {
                                "kLineAiReportDate": "2026-07-30",
                                "kLineAiContent": "短期偏强但仍需成交确认。",
                                "marketData": {"closePrice": ["8120"]},
                            }},
                        }
                    },
                },
            },
        },
        "market-watch": {},
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
        "sector_views": [
            {
                "sector": "贵金属",
                "state": "偏强",
                "summary": "黄金领涨但仍需观察板块内部共振。",
                "evidence_ids": ["sector:贵金属"],
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
    def test_codex_quota_cooldown_limits_model_frequency(self):
        timezone = BRIEF.SHANGHAI
        previous = datetime(2026, 8, 14, 10, 0, tzinfo=timezone)
        self.assertEqual(
            BRIEF.quota_cooldown_remaining(
                previous,
                minimum_minutes=30,
                now=datetime(2026, 8, 14, 10, 12, tzinfo=timezone),
            ),
            18 * 60,
        )
        self.assertEqual(
            BRIEF.quota_cooldown_remaining(
                previous,
                minimum_minutes=30,
                now=datetime(2026, 8, 14, 10, 31, tzinfo=timezone),
            ),
            0,
        )

    def test_openai_responses_request_uses_structured_output_and_never_logs_key(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({"output_text": json.dumps(model_payload())}).encode()

        context = BRIEF.build_context(source_payloads())
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-secret"}, clear=True):
            with mock.patch.object(
                BRIEF.MODEL_BACKEND.urllib.request,
                "urlopen",
                return_value=FakeResponse(),
            ) as urlopen:
                result = BRIEF.run_openai(context, 30)
        request = urlopen.call_args.args[0]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(result["headline"], model_payload()["headline"])
        self.assertEqual(body["text"]["format"]["type"], "json_schema")
        self.assertTrue(body["text"]["format"]["strict"])
        self.assertEqual(request.get_header("Authorization"), "Bearer sk-test-secret")

    def test_context_is_bounded_and_has_traceable_evidence(self):
        context = BRIEF.build_context(source_payloads())
        ids = {item["id"] for item in context["evidence"]}
        self.assertIn("oil:P2609", ids)
        self.assertIn("exchange:au", ids)
        self.assertIn("sector:贵金属", ids)
        self.assertIn("quant:bollinger-rsi-ma6-v1:P2609", ids)
        self.assertIn("supply:official-check", ids)
        self.assertIn("htfc-news:KX1", ids)
        self.assertIn("htfc-kline:P", ids)
        self.assertLessEqual(len(context["evidence"]), 40)
        self.assertEqual(context["fixed_logic"], ["otc_structure_library", "quant_model_rules"])
        self.assertEqual(
            context["source_snapshot"]["quant-model-signals"],
            "2026-07-30 23:28",
        )

    def test_live_market_watch_quotes_replace_close_snapshot_for_sector_evidence(self):
        payloads = source_payloads()
        payloads["market-watch"] = {
            "generated_at": "2026-07-30T23:35:00+08:00",
            "quotes": [{
                "symbol": "AU2610",
                "product": "AU",
                "name": "黄金",
                "category": "贵金属",
                "price": 790,
                "change_pct": -1.5,
            }],
        }
        context = BRIEF.build_context(payloads)
        sector = next(item for item in context["evidence"] if item["id"] == "sector:贵金属")
        self.assertEqual(sector["source"], "market-watch")
        self.assertIn("-1.50%", sector["value"])
        self.assertEqual(sector["observed_at"], "2026-07-30T23:35:00+08:00")

    def test_model_output_is_enriched_from_evidence_not_model_numbers(self):
        context = BRIEF.build_context(source_payloads())
        result = BRIEF.validate_and_enrich(model_payload(), context)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["update_session"], "night_close")
        self.assertEqual(result["key_moves"][0]["value"], "8120；涨跌 +0.60%")
        self.assertEqual(result["key_moves"][0]["source"], "oil-futures")
        self.assertEqual(result["sector_views"][0]["sector"], "贵金属")
        self.assertEqual(
            result["sector_views"][0]["evidence"][0]["id"],
            "sector:贵金属",
        )

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

    def test_automation_uses_server_only_structured_model_backend_and_shared_lock(self):
        generator = (ROOT / "scripts" / "update_market_assistant_brief.py").read_text(encoding="utf-8")
        backend = (ROOT / "server" / "model_backend.py").read_text(encoding="utf-8")
        deploy = (ROOT / "scripts" / "deploy_market_assistant_brief.sh").read_text(encoding="utf-8")
        installer = (ROOT / "scripts" / "install_market_assistant_launchd.sh").read_text(encoding="utf-8")
        self.assertIn('"codex-cli"', backend)
        self.assertIn('"gpt-5.6-terra"', backend)
        self.assertIn('"--output-schema"', backend)
        self.assertIn('"--ephemeral"', backend)
        self.assertIn('"read-only"', backend)
        self.assertIn('"OPENAI_API_KEY"', backend)
        self.assertIn('environment.pop(name, None)', backend)
        self.assertIn("MODEL_BACKEND.request_json", generator)
        self.assertIn("market-data-deploy.lock", deploy)
        self.assertIn('git add -- "$TARGET"', deploy)
        self.assertIn("<integer>900</integer>", installer)
        self.assertIn("previous valid brief remains", installer)


if __name__ == "__main__":
    unittest.main()

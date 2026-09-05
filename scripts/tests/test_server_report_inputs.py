from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "server" / "build_report_inputs.py"
SPEC = importlib.util.spec_from_file_location("server_build_report_inputs", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_json(root: Path, relative: str, payload: object) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def contract(product: str, price: str, change: str, rank: int = 1) -> dict[str, object]:
    return {
        "product": product,
        "product_name": product,
        "symbol": f"{product}2609",
        "contract": f"{product}2609",
        "contract_rank": rank,
        "price": price,
        "change": change,
        "preclose": "9000",
        "open": "9010",
        "high": "9100",
        "low": "8990",
        "trade_date": "2026-08-07",
        "source": "server test",
        "verification": "价格一致",
        "view": "技术偏强，等待基本面确认",
        "technical_detail": ["收盘位于短期均线上方"],
        "fundamental_detail": ["豆棕价差仍处倒挂"],
        "score": {
            "total": 0,
            "technical": 0,
            "fundamental": 0,
            "driver": 0,
            "money_flow": 0,
            "stance": "震荡",
            "view_confidence": "中",
        },
        "strategy_recommendation": {
            "lower_watch": float(price) - 30,
            "upper_watch": float(price) + 30,
            "invalidation": f"突破 {float(price) + 30:g} 后重评",
        },
    }


class ServerReportInputsTest(unittest.TestCase):
    def build_data(self, root: Path) -> None:
        write_json(
            root,
            "oil_futures.json",
            {
                "updated_at": "2026-08-07 23:10",
                "contracts": [
                    contract("P", "9200", "+1.00%"),
                    {**contract("P", "9250", "+0.80%", 2), "symbol": "P2701", "contract": "P2701"},
                    contract("Y", "8300", "-0.50%"),
                    {**contract("Y", "8350", "-0.30%", 2), "symbol": "Y2701", "contract": "Y2701"},
                    contract("OI", "9900", "+0.20%"),
                    {**contract("OI", "9950", "+0.10%", 2), "symbol": "OI2701", "contract": "OI2701"},
                    {
                        **contract("FCPO", "4400", "-0.10%"),
                        "contract_rank": None,
                        "symbol": "FCPO",
                    },
                ],
                "market_references": {
                    "cbot_bean_oil": {
                        "label": "CBOT豆油", "price": "70.25", "change": "+0.35%",
                        "updated_at": "2026-08-07 23:10", "source": "CME",
                    },
                    "crude_oil": {
                        "label": "WTI原油", "price": "84.51", "change": "-1.20%",
                        "updated_at": "2026-08-07 23:10", "source": "NYMEX",
                    },
                },
            },
        )
        write_json(
            root,
            "exchange_futures.json",
            {
                "updated_at": "2026-08-07 23:10",
                "contracts": [
                    {
                        "product": "棕榈", "symbol": "P2609", "price": 9200,
                        "change_pct": 1.0, "volume": 1000, "open_interest": 2000,
                        "trade_date": "2026-08-07", "source": "DCE",
                        "technical": {"status": "ok", "snapshot_date": "2026-08-07", "trend": "震荡"},
                        "fundamental": {
                            "summary": "两项国内证据",
                            "factors": [
                                {
                                    "title": "仓单库存｜2026-08-07",
                                    "text": "注册仓单为 430，当日变化 +0.00。该口径不等于社会总库存。",
                                },
                                {
                                    "title": "期现基差｜2026-08-07",
                                    "text": "现货价 9,100，主力结算价 9,200；按“主力－现货”计算为 +100.00（+1.10%）。",
                                },
                            ],
                            "evidence_dates": ["2026-08-07"],
                            "evidence_sources": ["DCE", "现货源"],
                        },
                    }
                ],
            },
        )
        write_json(
            root,
            "quant_model_signals.json",
            {"generated_at": "2026-08-07T23:11:00+08:00", "market_updated_at": "2026-08-07 23:10"},
        )
        write_json(
            root,
            "supply-demand.json",
            {
                "checked_at": "2026-08-08T09:20:00+08:00",
                "update_status": "no_change",
                "update_message": "官网暂未更新数据",
                "countries": {
                    "malaysia": {
                        "source": {"name": "MPOB", "url": "https://example.test/mpob"},
                        "metrics": {
                            "production": {
                                "label": "CPO产量",
                                "unit": "tonnes",
                                "series": [
                                    {"period": "2026-05", "value": 100, "published_at": "2026-06-10"},
                                    {"period": "2026-06", "value": 110, "published_at": "2026-07-10"},
                                ],
                            },
                            "exports": {
                                "label": "棕榈油出口",
                                "unit": "tonnes",
                                "series": [{"period": "2026-06", "value": 90, "published_at": "2026-07-10"}],
                            },
                            "stocks": {
                                "label": "棕榈油库存",
                                "unit": "tonnes",
                                "series": [{"period": "2026-06", "value": 120, "published_at": "2026-07-10"}],
                            },
                        },
                    },
                    "indonesia": {
                        "source": {"name": "GAPKI", "url": "https://example.test/gapki"},
                        "metrics": {
                            "production": {
                                "label": "CPO产量", "unit": "tonnes",
                                "series": [{"period": "2026-05", "value": 210, "published_at": "2026-07-20"}],
                            },
                            "exports": {
                                "label": "棕榈油出口", "unit": "tonnes",
                                "series": [{"period": "2026-05", "value": 180, "published_at": "2026-07-20"}],
                            },
                        },
                    },
                },
                "supplemental": {
                    "status": "ready", "release_period": "2026-07", "source": "USDA PSD",
                    "global_balance": {
                        "title": "全球棕榈油平衡表", "definition": "百万吨",
                        "series": [
                            {"period": "2025/26", "production": 80.0},
                            {"period": "2026/27", "production": 82.0},
                        ],
                    },
                    "import_demand": {
                        "title": "主要进口市场", "definition": "百万吨",
                        "markets": [
                            {"key": "india", "name": "印度", "series": [{"period": "2026/27", "imports": 9.0}]},
                            {"key": "china", "name": "中国", "series": [{"period": "2026/27", "imports": 6.0}]},
                        ],
                    },
                },
            },
        )
        write_json(
            root,
            "contracts/current_contracts.json",
            {
                "generated_at": "2026-08-07 23:10",
                "products": {
                    "P": [{"symbol": "P2609"}],
                    "Y": [{"symbol": "Y2609"}],
                    "OI": [{"symbol": "OI2609"}],
                },
            },
        )
        write_json(
            root,
            "reports.json",
            [
                {
                    "date": "2026-08-02-weekend",
                    "kind": "weekend",
                    "title": "08月02日周报",
                    "headline": "供应压力仍需价格确认",
                    "content": "历史正文",
                }
            ],
        )
        write_json(
            root,
            "market_watch.json",
            {
                "generated_at": "2026-08-08T09:20:00+08:00",
                "events_updated_at": "2026-08-08T09:20:00+08:00",
                "sources": [
                    {"name": "跨站新闻搜索", "state": "ready", "detail": "测试源可用"},
                    {"name": "华泰天玑·研报", "state": "ready", "detail": "测试研报可用"},
                ],
                "events": [
                    {
                        "id": "event-1",
                        "kind": "event",
                        "title": "马来西亚棕榈油出口预期调整",
                        "summary": "出口变化影响短期供需预期。",
                        "interpretation": "需要结合盘面确认。",
                        "impact": "中性",
                        "scope": "P · Y · OI",
                        "source": "华泰天玑·研报",
                        "url": "https://example.test/report",
                        "observed_at": "2026-08-08T08:30:00+08:00",
                    }
                ],
            },
        )

    def test_builds_manifest_and_numeric_snapshot_from_live_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data = base / "live-data"
            runtime = base / "runtime"
            self.build_data(data)
            payload = MODULE.write_source_run(
                data,
                runtime,
                "2026-08-08",
                "weekend",
                MODULE.parse_now("2026-08-08T21:15:00+08:00"),
            )
            snapshot = json.loads(Path(payload["snapshot"]).read_text(encoding="utf-8"))
            manifest = json.loads(Path(payload["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(snapshot["domestic"]["palm_oil"]["price"], 9200.0)
            self.assertEqual(snapshot["domestic"]["soybean_oil"]["change_pct"], -0.5)
            self.assertEqual(snapshot["domestic"]["palm_oil"]["technical_detail"], ["收盘位于短期均线上方"])
            self.assertEqual(
                [row["contract"] for row in snapshot["contract_structure"]["P"]],
                ["P2609", "P2701"],
            )
            self.assertEqual(snapshot["contract_structure"]["Y"][1]["price"], 8350.0)
            self.assertEqual(snapshot["fundamental"]["official_supply_demand"]["latest_metrics"]["production"]["change_pct"], 10.0)
            self.assertEqual(
                snapshot["fundamental"]["official_supply_demand"]["origin_matrix"]["indonesia"]["latest_metrics"]["exports"]["value"],
                180.0,
            )
            self.assertEqual(
                snapshot["fundamental"]["official_supply_demand"]["global_balance"]["global_palm_oil_balance"]["series"][-1]["production"],
                82.0,
            )
            self.assertEqual(snapshot["external"]["cbot_bean_oil"]["price"], 70.25)
            self.assertEqual(
                snapshot["fundamental"]["exchange_context"]["oilseed_and_energy"]["palm_oil"]["physical_market"]["metrics"]["warehouse_receipts"]["price"],
                430.0,
            )
            self.assertEqual(len(snapshot["research_coverage"]["required_dimensions"]), 8)
            self.assertEqual(snapshot["fundamental"]["spread"]["soybean_palm_spread"]["price"], -900.0)
            self.assertEqual(snapshot["research_history"]["previous_report"]["date"], "2026-08-02-weekend")
            self.assertEqual(snapshot["server_evidence"]["fixed_logic"], [
                "otc_structure_library",
                "quant_model_rules",
            ])
            self.assertEqual(manifest["source_mode"], "governed_skill_chain")
            self.assertEqual(manifest["results"][0]["name"], "futures_oil_fetch_market_data")
            self.assertEqual(snapshot["news_and_research_evidence"]["fresh_event_count"], 1)
            self.assertEqual(manifest["results"][-1]["name"], "oil_report_freshness")
            self.assertEqual(manifest["results"][-1]["status"], "ok")
            self.assertTrue((runtime / "source_runs/2026-08-08-weekend/raw/futures_market_data.weekly_compatible.json").is_file())

    def test_missing_rank_one_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data = base / "live-data"
            runtime = base / "runtime"
            self.build_data(data)
            oil_path = data / "oil_futures.json"
            oil = json.loads(oil_path.read_text(encoding="utf-8"))
            oil["contracts"] = [item for item in oil["contracts"] if item.get("product") != "OI"]
            oil_path.write_text(json.dumps(oil), encoding="utf-8")
            with self.assertRaises(MODULE.ReportInputError):
                MODULE.write_source_run(
                    data,
                    runtime,
                    "2026-08-08",
                    "weekend",
                    MODULE.parse_now("2026-08-08T21:15:00+08:00"),
                )

    def test_refuses_backdated_report_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data = base / "live-data"
            runtime = base / "runtime"
            self.build_data(data)
            with self.assertRaises(MODULE.ReportInputError):
                MODULE.write_source_run(
                    data,
                    runtime,
                    "2026-08-07",
                    "daily",
                    MODULE.parse_now("2026-08-08T06:00:00+08:00"),
                )

    def test_daily_report_refuses_stale_market_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data = base / "live-data"
            runtime = base / "runtime"
            self.build_data(data)
            with self.assertRaisesRegex(MODULE.ReportInputError, "stale server dataset"):
                MODULE.write_source_run(
                    data,
                    runtime,
                    "2026-08-08",
                    "daily",
                    MODULE.parse_now("2026-08-08T09:00:00+08:00"),
                )

    def test_future_dated_rank_one_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data = base / "live-data"
            runtime = base / "runtime"
            self.build_data(data)
            oil_path = data / "oil_futures.json"
            oil = json.loads(oil_path.read_text(encoding="utf-8"))
            oil["contracts"][0]["trade_date"] = "2026-08-09"
            oil_path.write_text(json.dumps(oil), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.ReportInputError, "future-dated rank-1 contract"):
                MODULE.write_source_run(
                    data,
                    runtime,
                    "2026-08-08",
                    "weekend",
                    MODULE.parse_now("2026-08-08T21:15:00+08:00"),
                )


if __name__ == "__main__":
    unittest.main()

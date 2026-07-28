import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "update_exchange_futures_data.py"
SPEC = importlib.util.spec_from_file_location("update_exchange_futures_data", SCRIPT)
UPDATE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(UPDATE)


class ExchangeFuturesFundamentalTest(unittest.TestCase):
    def test_core_universe_covers_every_research_category(self):
        self.assertGreaterEqual(len(UPDATE.CORE_PRODUCTS), 30)
        self.assertEqual(
            set(UPDATE.CORE_PRODUCTS_BY_CATEGORY),
            set(UPDATE.CATEGORY_RULES),
        )
        self.assertTrue({"棕榈", "豆油", "菜油", "豆粕", "菜粕"}.issubset(UPDATE.CORE_PRODUCTS))
        self.assertNotIn("胶合板", UPDATE.CORE_PRODUCTS)
        self.assertNotIn("线材", UPDATE.CORE_PRODUCTS)

    def test_news_matching_requires_direct_title_match(self):
        news = [
            {
                "title": "东方财富财经早餐",
                "content": "沪铜、黄金、原油均有波动",
                "date": "2026-07-28",
            },
            {
                "title": "沪铜库存继续下降",
                "content": "交易所库存数据更新",
                "date": "2026-07-28",
            },
        ]
        matched = UPDATE.news_for("沪铜", news)
        self.assertEqual([item["title"] for item in matched], ["沪铜库存继续下降"])

    def test_commodity_fundamental_starts_with_observed_values(self):
        result = UPDATE.fundamental_summary(
            "沪铜",
            "有色金属",
            [],
            "CU",
            104810,
            {
                "CU": {
                    "date": "2026-07-28",
                    "value": 26924,
                    "daily_change": -100,
                    "five_record_change": -1900,
                    "source": "仓单源",
                }
            },
            {
                "CU": {
                    "date": "2026-07-28",
                    "spot_price": 105323.33,
                    "dominant_contract_price": 104810,
                    "dom_basis": -513.33,
                    "dom_basis_rate": -0.49,
                    "source": "基差源",
                }
            },
            {},
            {},
        )
        self.assertEqual(result["evidence_status"], "observed")
        self.assertEqual(result["evidence_count"], 2)
        self.assertTrue(result["factors"][0]["title"].startswith("仓单库存"))
        self.assertIn("主力－现货", result["factors"][1]["text"])
        self.assertTrue(result["factors"][2]["title"].startswith("跟踪框架"))

    def test_missing_evidence_is_explicitly_not_a_conclusion(self):
        result = UPDATE.fundamental_summary(
            "原木",
            "林木建材",
            [],
            "LG",
            800,
            {},
            {},
            {},
            {},
        )
        self.assertEqual(result["evidence_status"], "missing")
        self.assertEqual(result["evidence_count"], 0)
        self.assertIn("不作为当前基本面结论", result["summary"])

    def test_stock_index_uses_spot_basis_and_valuation(self):
        evidence, sources, dates = UPDATE.build_fundamental_evidence(
            "IC",
            "股指期货",
            7460,
            {},
            {},
            {
                "000905": {
                    "date": "2026-07-28 22:00",
                    "spot_price": 7443.43,
                    "change_pct": -3.59,
                    "spot_source": "指数行情源",
                    "valuation_date": "2026-07-28",
                    "pe": 31.2,
                    "dividend_yield": 1.2,
                    "valuation_source": "估值源",
                }
            },
            {},
        )
        self.assertEqual(len(evidence), 2)
        self.assertIn("期指主力－现货", evidence[0]["text"])
        self.assertIn("市盈率", evidence[1]["text"])
        self.assertEqual(sources, ["指数行情源", "估值源"])
        self.assertEqual(dates, ["2026-07-28 22:00", "2026-07-28"])


if __name__ == "__main__":
    unittest.main()

import importlib.util
import sys
import unittest
import urllib.error
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "update_supply_demand_data.py"
SPEC = importlib.util.spec_from_file_location("update_supply_demand_data", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def make_point(period: str, value: int, source: str = "https://example.test/source"):
    return {
        "period": period,
        "value": value,
        "published_at": f"{period}-10",
        "source_url": source,
    }


class SupplyDemandParserTests(unittest.TestCase):
    def test_parse_mpob_export_thousand_separators(self):
        html = """
        <table><tr><th>PRODUCT</th><th>UNIT</th><th>JAN</th><th>FEB</th></tr>
        <tr><td>PALM OIL</td><td>Tonnes</td><td>1,453,163</td><td>1,065,204</td>
        <td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>2,518,367</td></tr></table>
        """
        rows = module.parse_mpob_export(html, 2026, "https://example.test/mpob")
        self.assertEqual(rows[0]["value"], 1_453_163)
        self.assertEqual(rows[1]["period"], "2026-02")

    def test_parse_mpob_paired_current_year_values(self):
        html = """
        <table>
        <tr><td>MALAYSIA</td><td>1,000</td><td>1,100</td><td>2,000</td><td>2,200</td>
        <td>3,000</td><td>3,300</td><td>4,000</td><td>4,400</td><td>5,000</td><td>5,500</td>
        <td>6,000</td><td>6,600</td><td>21,000</td><td>23,100</td></tr>
        <tr><td>MALAYSIA</td><td>7,000</td><td>7,700</td><td>8,000</td><td>8,800</td>
        <td>9,000</td><td>9,900</td><td>10,000</td><td>11,000</td><td>12,000</td><td>13,200</td>
        <td>14,000</td><td>15,400</td><td>81,000</td><td>89,100</td></tr>
        </table>
        """
        rows = module.parse_mpob_paired_rows(html, 2026, "MALAYSIA", "https://example.test/mpob")
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["value"], 1_100)
        self.assertEqual(rows[-1]["value"], 15_400)

    def test_parse_gapki_indonesian_quantities(self):
        html = """
        <meta property="article:published_time" content="2026-07-15T08:36:12+00:00" />
        <h1 class="title entry-title">Kinerja Industri Sawit Mei 2026</h1>
        <p>Produksi CPO pada Mei 2026 mencapai 4.165 ribu ton.</p>
        <p>Total ekspor produk sawit pada Mei 2026 hanya mencapai 1.996 ribu ton.</p>
        <p>Stok di akhir Mei 2026 tercatat sebesar 3.042 ribu ton.</p>
        """
        period, published, metrics = module.parse_gapki_article(html, "https://example.test/gapki")
        self.assertEqual(period, "2026-05")
        self.assertEqual(published, "2026-07-15")
        self.assertEqual(metrics["production"]["value"], 4_165_000)
        self.assertEqual(metrics["stocks"]["value"], 3_042_000)

    def test_parse_gapki_decimal_millions(self):
        self.assertEqual(module.parse_indonesian_quantity("3,04", "juta"), 3_040_000)
        self.assertEqual(module.parse_indonesian_quantity("3.04", "juta"), 3_040_000)

    def test_gapki_total_cpo_pko_is_not_mislabeled_as_cpo(self):
        html = """
        <meta property="article:published_time" content="2024-12-24T04:58:43+00:00" />
        <h1 class="title entry-title">Produksi Dan Ekspor Naik, Stok Berkurang</h1>
        <p>Produksi CPO dan PKO bulan Oktober 2024 mencapai 4.843 ribu ton.</p>
        <p>Total ekspor naik kembali dari 2.260 ribu ton menjadi 2.888 ribu ton pada bulan Oktober.</p>
        <p>Stok akhir Oktober turun menjadi 2.502 ribu ton.</p>
        """
        period, _, metrics = module.parse_gapki_article(html, "https://example.test/gapki")
        self.assertEqual(period, "2024-10")
        self.assertNotIn("production", metrics)
        self.assertEqual(metrics["exports"]["value"], 2_888_000)

    def test_gapki_missing_fields_is_rejected(self):
        html = """
        <meta property="article:published_time" content="2026-07-15T08:36:12+00:00" />
        <h1 class="title entry-title">Kinerja Industri Sawit Mei 2026</h1>
        <p>Produksi CPO pada Mei 2026 mencapai 4.165 ribu ton.</p>
        """
        with self.assertRaises(module.SourceParseError):
            module.parse_gapki_article(html, "https://example.test/gapki")

    def test_network_404_is_source_unavailable(self):
        error = urllib.error.HTTPError(
            "https://example.test/missing",
            404,
            "Not Found",
            {},
            None,
        )
        with patch.object(module.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(module.SourceUnavailable):
                module.fetch_text("https://example.test/missing")


class SupplyDemandPayloadTests(unittest.TestCase):
    def setUp(self):
        periods = [f"2026-{month:02d}" for month in range(1, 7)]
        self.source_data = {
            metric: [make_point(period, 1_000_000 + index) for index, period in enumerate(periods)]
            for metric in ("production", "exports", "stocks")
        }

    def test_source_failure_preserves_previous_series(self):
        now = datetime(2026, 7, 28, 13, 15, tzinfo=ZoneInfo("Asia/Shanghai"))
        previous = {
            "schema_version": 1,
            "generated_at": "2026-07-20T13:15:00+08:00",
            "timezone": "Asia/Shanghai",
            "display_months": 24,
            "countries": {
                "malaysia": module.country_payload("malaysia", self.source_data, now.date()),
                "indonesia": module.country_payload("indonesia", self.source_data, now.date()),
            },
        }

        def unavailable(_):
            raise module.SourceUnavailable("offline")

        result = module.build_payload(now, previous, unavailable, unavailable)
        self.assertEqual(result["countries"]["malaysia"]["status"], "source_unreachable")
        self.assertEqual(
            result["countries"]["malaysia"]["metrics"]["production"]["series"],
            previous["countries"]["malaysia"]["metrics"]["production"]["series"],
        )

    def test_validation_rejects_duplicate_months(self):
        now = datetime(2026, 7, 28, tzinfo=ZoneInfo("Asia/Shanghai"))
        country = module.country_payload("malaysia", self.source_data, now.date())
        country["metrics"]["production"]["series"].append(
            country["metrics"]["production"]["series"][-1]
        )
        payload = {
            "schema_version": 1,
            "generated_at": now.isoformat(),
            "timezone": "Asia/Shanghai",
            "display_months": 24,
            "countries": {"malaysia": country, "indonesia": country},
        }
        with self.assertRaises(ValueError):
            module.validate_payload(payload)

    def test_malaysia_stale_after_release_window(self):
        now = datetime(2026, 7, 28, tzinfo=ZoneInfo("Asia/Shanghai"))
        old = {
            metric: [make_point("2026-05", 1_000_000)]
            for metric in ("production", "exports", "stocks")
        }
        country = module.country_payload("malaysia", old, now.date())
        self.assertEqual(country["status"], "stale")

    def test_single_country_success_keeps_other_country_failure_visible(self):
        now = datetime(2026, 7, 28, 13, 15, tzinfo=ZoneInfo("Asia/Shanghai"))

        def malaysia(_):
            return self.source_data

        def indonesia(_):
            raise module.SourceUnavailable("offline")

        result = module.build_payload(now, {}, malaysia, indonesia)
        self.assertNotEqual(result["countries"]["malaysia"]["status"], "source_unreachable")
        self.assertEqual(result["countries"]["indonesia"]["status"], "source_unreachable")

    def test_historical_revision_replaces_same_month(self):
        old = {"production": [make_point("2026-05", 1_000_000)]}
        previous = {
            "metrics": {
                "production": {"series": old["production"]},
                "exports": {"series": []},
                "stocks": {"series": []},
            }
        }
        revised = {
            "production": [make_point("2026-05", 1_100_000)],
            "exports": [],
            "stocks": [],
        }
        merged = module.merge_source_data(revised, previous)
        self.assertEqual(merged["production"][0]["value"], 1_100_000)


if __name__ == "__main__":
    unittest.main()

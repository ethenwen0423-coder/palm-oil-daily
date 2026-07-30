import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
INTRADAY_INSTALLER = ROOT / "scripts" / "install_oil_futures_tab_launchd.sh"
MARKET_DEPLOY = ROOT / "scripts" / "deploy_oil_futures_tab.sh"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


EXCHANGE = load_module("exchange_refresh_boundary", ROOT / "scripts" / "update_exchange_futures_data.py")
OIL = load_module("oil_refresh_boundary", ROOT / "scripts" / "update_oil_futures_data.py")


class FundamentalRefreshBoundaryTest(unittest.TestCase):
    def test_intraday_schedule_requires_morning_snapshot_and_carry_mode(self):
        installer = INTRADAY_INSTALLER.read_text(encoding="utf-8")
        deploy = MARKET_DEPLOY.read_text(encoding="utf-8")
        self.assertIn(r"\$FUNDAMENTAL_DATE-morning.ok", installer)
        self.assertIn("morning report/fundamental snapshot not published", installer)
        self.assertIn("--fundamental-mode", deploy)
        self.assertIn('OIL_FUNDAMENTAL_MODE="carry"', deploy)
        self.assertIn('EXCHANGE_FUNDAMENTAL_MODE="carry"', deploy)
        self.assertIn("pull_with_retry", installer)
        self.assertIn("attempt * 10", installer)
        self.assertIn("keep state open for next recovery", installer)
        self.assertIn("$HOME/Sites/palm-oil-daily-runtime", installer)
        self.assertIn("oil-futures runtime must be a clean main checkout", installer)
        self.assertIn("<integer>16</integer><key>Minute</key><integer>0</integer>", installer)
        self.assertIn('SESSION="night_open"', installer)
        self.assertIn('SESSION="night_close"', installer)
        self.assertIn('SESSION="overnight"', installer)
        self.assertIn('date -v-1d +%F', installer)
        self.assertIn('<integer>23</integer><key>Minute</key><integer>10</integer>', installer)
        self.assertIn('<integer>2</integer><key>Minute</key><integer>40</integer>', installer)
        self.assertIn("--fundamental-date", deploy)
        self.assertIn("data/contracts/current_contracts.json", deploy)
        self.assertIn('"data/contracts/${TODAY:0:7}.json"', deploy)
        self.assertIn("--contract-output", deploy)
        self.assertIn('CONTRACT_TMP="$TMP_DIR/current_contracts.json"', deploy)
        self.assertIn('cp "$CONTRACT_TMP" data/contracts/current_contracts.json', deploy)
        self.assertIn("--output-only", OIL.run_contract_selector.__code__.co_consts)

    def test_market_collector_paths_can_run_outside_macos(self):
        deploy = MARKET_DEPLOY.read_text(encoding="utf-8")
        oil_updater = (ROOT / "scripts" / "update_oil_futures_data.py").read_text(
            encoding="utf-8"
        )
        exchange_updater = (
            ROOT / "scripts" / "update_exchange_futures_data.py"
        ).read_text(encoding="utf-8")
        self.assertIn("PALM_OIL_SUPPORT_DIR", deploy)
        self.assertIn("PALM_OIL_PRIVATE_ENV", oil_updater)
        self.assertNotIn('TECHNICAL_HELPER = Path.home() / ".codex"', exchange_updater)
        self.assertIn("runtime_indicators.py", exchange_updater)

    def test_exchange_carry_requires_same_day_morning_snapshot(self):
        payload = {
            "fundamental_updated_at": "2026-07-28 06:18",
            "fundamental_update_session": "morning",
            "contracts": [
                {
                    "product": "沪铜",
                    "fundamental": {"evidence_count": 2},
                    "news_hotspots": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "exchange.js"
            path.write_text(
                f"window.EXCHANGE_FUTURES_DATA = {json.dumps(payload, ensure_ascii=False)};\n",
                encoding="utf-8",
            )
            loaded, records = EXCHANGE.load_frozen_fundamentals(path, "2026-07-28")
        self.assertEqual(loaded["fundamental_update_session"], "morning")
        self.assertEqual(records["沪铜"]["fundamental"]["evidence_count"], 2)

    def test_exchange_carry_rejects_stale_snapshot(self):
        payload = {
            "fundamental_updated_at": "2026-07-27 06:18",
            "fundamental_update_session": "morning",
            "contracts": [{"product": "沪铜", "fundamental": {}, "news_hotspots": []}],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "exchange.js"
            path.write_text(
                f"window.EXCHANGE_FUTURES_DATA = {json.dumps(payload, ensure_ascii=False)};\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "晨间基本面尚未冻结"):
                EXCHANGE.load_frozen_fundamentals(path, "2026-07-28")

    def test_oil_carry_preserves_morning_fundamental_and_updates_technical_score(self):
        morning = {
            "product": "P",
            "contract_rank": 1,
            "market": "DCE",
            "fundamental_detail": [{"title": "基本面", "text": "晨间冻结"}],
            "score": {"fundamental": 42},
        }
        intraday = {
            "product": "P",
            "contract_rank": 1,
            "market": "DCE",
            "fundamental_detail": [{"title": "基本面", "text": "盘中重算"}],
            "score": {
                "technical": 70,
                "fundamental": 60,
                "driver": 55,
                "money_flow": 65,
                "total": 63,
            },
        }
        result = OIL.carry_frozen_oil_fundamentals(
            [intraday],
            {OIL.oil_contract_freeze_key(morning): morning},
        )[0]
        self.assertEqual(result["fundamental_detail"], morning["fundamental_detail"])
        self.assertEqual(result["score"]["fundamental"], 42)
        self.assertEqual(result["score"]["technical"], 70)
        self.assertEqual(result["score"]["total"], 57.5)
        self.assertIn("午盘与收盘不重新计算", result["fundamental_snapshot_note"])

    def test_overnight_carry_accepts_previous_trading_day_snapshot(self):
        payload = {
            "fundamental_updated_at": "2026-07-30 06:18",
            "fundamental_update_session": "morning",
            "contracts": [
                {
                    "product": "P",
                    "contract_rank": 1,
                    "market": "DCE",
                    "fundamental_detail": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "oil.js"
            path.write_text(
                f"window.OIL_FUTURES_CONTRACTS = {json.dumps(payload, ensure_ascii=False)};\n",
                encoding="utf-8",
            )
            loaded, records = OIL.load_frozen_oil_fundamentals(path, "2026-07-30")
        self.assertEqual(loaded["fundamental_update_session"], "morning")
        self.assertIn(("P", 1, "DCE"), records)

    def test_contract_discovery_falls_back_per_product_without_mutating_saved_file(self):
        month = "2026-07"
        previous = {
            "month": month,
            "generated_at": "2026-07-30 23:20:41",
            "products": {
                "P": [{"symbol": "P2609", "rank": 1}],
                "Y": [{"symbol": "Y2609", "rank": 1}],
                "OI": [{"symbol": "OI2609", "rank": 1}],
                "M": [{"symbol": "M2609", "rank": 1}],
                "RM": [{"symbol": "RM2609", "rank": 1}],
            },
            "warnings": [],
        }
        fresh = {
            "month": month,
            "generated_at": "2026-07-31 00:13:42",
            "products": {
                "P": [],
                "Y": [{"symbol": "Y2609", "rank": 1}],
                "OI": [{"symbol": "OI2609", "rank": 1}],
                "M": [{"symbol": "M2609", "rank": 1}],
                "RM": [{"symbol": "RM2609", "rank": 1}],
            },
            "warnings": ["P 合约实时行情获取失败"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            saved = Path(temporary) / "current_contracts.json"
            saved.write_text(json.dumps(previous, ensure_ascii=False), encoding="utf-8")
            before = saved.read_text(encoding="utf-8")
            with (
                mock.patch.object(OIL, "CONTRACT_DISCOVERY_CURRENT", saved),
                mock.patch.object(OIL, "run_contract_selector", return_value=(fresh, [])),
                mock.patch.object(OIL, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = datetime(2026, 7, 31, tzinfo=OIL.SHANGHAI)
                result = OIL.load_contract_discovery()
            self.assertEqual(result["products"]["P"], previous["products"]["P"])
            self.assertIn("P 实时合约发现缺失", "；".join(result["warnings"]))
            self.assertEqual(saved.read_text(encoding="utf-8"), before)

    def test_contract_discovery_is_written_only_to_explicit_temporary_output(self):
        payload = {
            "month": "2026-07",
            "products": {
                symbol: [{"symbol": f"{symbol}2609"}]
                for symbol in ("P", "Y", "OI", "M", "RM")
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "candidate.json"
            OIL.write_contract_discovery(payload, output)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["products"]["P"][0]["symbol"], "P2609")


if __name__ == "__main__":
    unittest.main()

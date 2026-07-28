import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


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
        self.assertIn(r"\$TODAY-morning.ok", installer)
        self.assertIn("morning report/fundamental snapshot not published", installer)
        self.assertIn("--fundamental-mode", deploy)
        self.assertIn('OIL_FUNDAMENTAL_MODE="carry"', deploy)
        self.assertIn('EXCHANGE_FUNDAMENTAL_MODE="carry"', deploy)

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


if __name__ == "__main__":
    unittest.main()

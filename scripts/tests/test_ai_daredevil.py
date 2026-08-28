import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("ai_daredevil_runtime", ROOT / "server" / "run_ai_daredevil.py")
RUNTIME = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(RUNTIME)


class AiDaredevilTests(unittest.TestCase):
    def test_static_page_exposes_required_fund_sections_and_risk_notice(self):
        html = (ROOT / "ai-daredevil.html").read_text(encoding="utf-8")
        script = (ROOT / "assets" / "ai-daredevil.js").read_text(encoding="utf-8")
        for label in ("AI敢死队", "当前持仓", "今日动作", "下一步指令", "未执行信号", "净值曲线", "全品种收盘扫描"):
            self.assertIn(label, html)
        self.assertIn("不构成投资建议", html)
        self.assertIn('const API = "/api/ai-daredevil"', script)
        self.assertIn("60 * 1000", script)

    def test_runtime_initializes_persistent_virtual_fund_without_requesting_quotes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = subprocess.run(
                [sys.executable, str(ROOT / "server" / "run_ai_daredevil.py"),
                 "--site-root", str(ROOT), "--live-data-root", str(root / "live"),
                 "--state-root", str(root / "state"), "--now", "2026-08-28T19:00:00+08:00"],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((root / "live" / "ai_daredevil.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["equity"], 1_000_000)
            self.assertEqual(payload["model"]["version"], RUNTIME.MODEL_VERSION)
            self.assertEqual(payload["positions"], [])
            self.assertTrue((root / "state" / "ai-daredevil" / "trade_ledger.jsonl").is_file())
            self.assertTrue((root / "live" / RUNTIME.READY_MARKER).is_file())

    def test_quote_parser_requires_exact_delivery_contract(self):
        row = {"合约": "P2701", "最新价": "10,020", "开盘价": "9,990", "交易日期": "2026-08-28"}
        quote = RUNTIME.quote_from_row(row, "P2701", "test")
        self.assertEqual(quote["last"], 10020)
        self.assertEqual(quote["open"], 9990)
        self.assertIsNone(RUNTIME.quote_from_row(row, "P0", "test"))
        self.assertIsNone(RUNTIME.quote_from_row(row, "P2705", "test"))

    def test_akshare_realtime_uses_display_symbols_instead_of_variety_codes(self):
        self.assertEqual(RUNTIME.PRODUCT_REALTIME_SYMBOL["P"], "棕榈")
        self.assertEqual(RUNTIME.PRODUCT_REALTIME_SYMBOL["TA"], "PTA")
        self.assertEqual(set(RUNTIME.PRODUCT_REALTIME_SYMBOL), set(RUNTIME.PRODUCTS))

    def test_daily_fetch_has_a_hard_timeout_boundary(self):
        source = (ROOT / "server" / "run_ai_daredevil.py").read_text(encoding="utf-8")
        self.assertIn("urlopen(request, timeout=15)", source)
        self.assertIn("ThreadPoolExecutor", source)

    def test_installer_has_exact_session_open_and_hourly_schedule(self):
        installer = (ROOT / "server" / "install_automation.sh").read_text(encoding="utf-8")
        self.assertIn("palm-oil-ai-daredevil.timer", installer)
        self.assertIn("Mon..Fri *-*-* *:00:00 Asia/Shanghai", installer)
        self.assertIn("13:30:00 Asia/Shanghai", installer)
        self.assertIn("15:25:00 Asia/Shanghai", installer)
        self.assertIn("systemctl enable --now palm-oil-ai-daredevil.timer", installer)

    def test_close_scan_calls_authoritative_contract_local_model_and_uses_t_minus_1_main(self):
        ledger, model, _signal_model = RUNTIME.load_components(ROOT)
        dates = pd.bdate_range("2026-06-29", periods=40)
        def bars(contract, latest_volume):
            close = [100.0] * 39 + ([110.0] if contract == "P2701" else [90.0])
            volume = [1000.0 if contract == "P2701" else 500.0] * 39 + [latest_volume]
            return pd.DataFrame({
                "date": dates, "open": close, "high": [value + 2 for value in close],
                "low": [value - 2 for value in close], "close": close,
                "volume": volume, "hold": [2000.0] * 40,
            })
        frames = {"P2701": bars("P2701", 1000), "P2705": bars("P2705", 2000)}
        with tempfile.TemporaryDirectory() as temporary:
            state = {"positions": {}, "pending_orders": {}, "_strategy_path": str(Path(temporary) / "strategy.json")}
            with mock.patch.object(RUNTIME, "current_contracts", return_value={"P": list(frames)}), \
                 mock.patch.object(RUNTIME, "fetch_daily", side_effect=lambda contract: frames[contract]), \
                 mock.patch.object(RUNTIME, "next_trade_date", return_value=dates[-1].date()), \
                 mock.patch.object(model, "prepare_contract_local_main", wraps=model.prepare_contract_local_main) as formal:
                snapshot, skipped, audit = RUNTIME.scan_signals(ROOT, ROOT / "data", state, model)
            self.assertTrue(formal.called)
            self.assertEqual(len(skipped), len(RUNTIME.PRODUCTS) - 1)
            self.assertEqual(snapshot["signals"][0]["contract"], "P2705")
            self.assertEqual(snapshot["signals"][0]["action"], "ENTER_LONG")
            self.assertEqual(audit["universe_count"], len(RUNTIME.PRODUCTS))
            self.assertEqual(audit["evaluated_count"], 1)
            self.assertEqual(len(audit["missing_varieties"]), len(RUNTIME.PRODUCTS) - 1)
            self.assertEqual(audit["candidate_count"], 1)
            self.assertEqual(audit["order_count"], 1)


if __name__ == "__main__":
    unittest.main()

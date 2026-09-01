import importlib.util
import json
import subprocess
import sys
import tempfile
import urllib.error
import unittest
from pathlib import Path
from types import SimpleNamespace
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
        stylesheet = (ROOT / "assets" / "ai-daredevil.css").read_text(encoding="utf-8")
        for label in ("AI敢死队", "布林带模型", "纯AI决策", "当前持仓", "开仓日期", "使用策略", "开仓原因", "今日动作", "下一步指令", "未执行信号", "净值曲线", "跨板块策略池全量扫描"):
            self.assertIn(label, html)
        self.assertIn("不构成投资建议", html)
        self.assertIn('api: "/api/ai-daredevil"', script)
        self.assertIn('api: "/api/ai-daredevil/pure-ai"', script)
        self.assertIn('kind === "skipped"', script)
        self.assertIn('assets/ai-daredevil.css?v=20260901-2', html)
        self.assertIn('assets/ai-daredevil.js?v=20260901-3', html)
        self.assertIn("名义金额 / 保证金", html)
        self.assertIn("item.margin_rate", script)
        self.assertIn('item.margin_applied_side === "long"', script)
        self.assertIn('item.margin_applied_side === "short"', script)
        self.assertIn("实际保证金", script)
        self.assertIn("不设置仓位、回撤、品种数量或板块上限", script)
        self.assertIn("策略：${escapeHtml(strategyName(item))}", script)
        self.assertIn('id="max-drawdown" class="is-drawdown"', html)
        self.assertIn('.is-positive { color: var(--dd-red) !important; }', stylesheet)
        self.assertIn('.is-negative { color: var(--dd-green) !important; }', stylesheet)
        self.assertIn('.is-drawdown { color: var(--dd-green) !important; }', stylesheet)
        self.assertIn('const pnlClass = kind === "trade" ? (pnl > 0 ? "is-positive" : (pnl < 0 ? "is-negative" : "")) : "";', script)
        self.assertIn("累计已实现（非今日）", html)
        self.assertIn("今日盈亏 = 当前权益 − 上一交易日权益", script)
        self.assertIn('colorize(el("realized-pnl"), summary.realized_pnl)', script)
        self.assertIn('if (amount > 0) return `+${money.format(amount)}`', script)
        self.assertIn('if (amount < 0) return `-${money.format(Math.abs(amount))}`', script)
        self.assertIn('className: "position-pnl-negative", text: `（${money.format(Math.abs(amount))}）`', script)
        self.assertIn('.position-pnl-positive { color: var(--dd-red); }', stylesheet)
        self.assertIn('.position-pnl-negative { color: var(--dd-green); }', stylesheet)
        self.assertIn("60 * 1000", script)
        self.assertIn("过去五年逐月回测收益", html)
        self.assertIn("当前 40 个跨板块品种静态等权基准", html)
        self.assertIn('backtestApi: "/api/ai-daredevil/monthly-backtest"', script)
        self.assertIn("monthly-return-table", stylesheet)
        self.assertIn("不是实时基金动态前八仓位", html)
        self.assertIn('if (value == null || value === "")', script)

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
        self.assertEqual(RUNTIME.PRODUCT_REALTIME_NODE["P"], "zly_qh")
        self.assertEqual(set(RUNTIME.PRODUCT_REALTIME_NODE), set(RUNTIME.PRODUCTS))

    def test_realtime_quotes_use_bounded_concurrent_direct_requests(self):
        payload = json.dumps([{
            "symbol": "P2701", "trade": "10020", "open": "9990",
            "date": "2026-09-01", "time": "21:01:00",
        }]).encode()

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return payload

        with mock.patch.object(RUNTIME.urllib.request, "urlopen", return_value=Response()) as fetch:
            quotes, error = RUNTIME.akshare_quotes(["P2701"], timeout=90)
        self.assertIsNone(error)
        self.assertEqual(quotes["P2701"]["last"], 10020)
        self.assertEqual(quotes["P2701"]["source"], "新浪期货实时行情（AKShare 同源）")
        self.assertEqual(fetch.call_args.kwargs["timeout"], 12)

    def test_margin_rate_uses_the_actual_long_or_short_exchange_side(self):
        book = {"rates": {"SA2701": {
            "contract": "SA2701", "margin_rate": .12,
            "long_margin_rate": .08, "short_margin_rate": .12,
        }}}
        long_row = RUNTIME.margin_rate("SA2701", book, "ENTER_LONG")
        short_row = RUNTIME.margin_rate("SA2701", book, "ENTER_SHORT")
        self.assertEqual(long_row["margin_rate"], .08)
        self.assertEqual(long_row["margin_applied_side"], "long")
        self.assertEqual(short_row["margin_rate"], .12)
        self.assertEqual(short_row["margin_applied_side"], "short")

    def test_normalized_margin_cache_is_persisted_before_public_snapshot(self):
        cached = {
            "fetched_at": "2026-09-01T08:00:00+08:00",
            "validation": "按实际持仓方向使用",
            "rates": {"AL2610": {"contract": "AL2610"}},
        }
        resolver = SimpleNamespace(
            load_cached_margin_book=mock.Mock(return_value=cached),
            fetch_margin_book=mock.Mock(side_effect=AssertionError("fresh cache should be reused")),
        )
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary)
            now = pd.Timestamp("2026-09-01T08:30:00+08:00").to_pydatetime()
            with mock.patch.object(RUNTIME, "load_margin_resolver", return_value=resolver):
                result = RUNTIME.resolve_margin_book(state_dir, ["AL2610"], now, 20)
            persisted = json.loads((state_dir / RUNTIME.MARGIN_BOOK_FILE).read_text(encoding="utf-8"))
        self.assertEqual(result["validation"], "按实际持仓方向使用")
        self.assertEqual(persisted["validation"], "按实际持仓方向使用")

    def test_partial_fresh_margin_cache_is_merged_with_partial_refresh(self):
        cached_rate = {
            "contract": "TA2701", "margin_rate": .08,
            "long_margin_rate": .07, "short_margin_rate": .08,
            "source_updated_at": "2026-08-31",
        }
        fresh_rate = {
            "contract": "AU2610", "margin_rate": .16,
            "long_margin_rate": .16, "short_margin_rate": .16,
            "source_updated_at": "2026-09-01",
        }
        resolver = SimpleNamespace(
            source_is_fresh=lambda row, _day: row.get("source_updated_at") >= "2026-08-25",
            load_cached_margin_book=mock.Mock(return_value=None),
            fetch_margin_book=mock.Mock(return_value={
                "coverage_status": "partial", "rates": {"AU2610": fresh_rate},
                "unresolved_contracts": ["TA2701"], "validated_count": 1,
            }),
        )
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary)
            (state_dir / RUNTIME.MARGIN_BOOK_FILE).write_text(
                json.dumps({"rates": {"TA2701": cached_rate}}), encoding="utf-8"
            )
            now = pd.Timestamp("2026-09-01T20:30:00+08:00").to_pydatetime()
            with mock.patch.object(RUNTIME, "load_margin_resolver", return_value=resolver):
                result = RUNTIME.resolve_margin_book(
                    state_dir, ["AU2610", "TA2701"], now, 20, force=True
                )
        self.assertEqual(result["coverage_status"], "complete")
        self.assertEqual(set(result["rates"]), {"AU2610", "TA2701"})
        self.assertTrue(result["cache_fallback_used"])

    def test_realtime_contract_discovery_uses_bounded_direct_requests(self):
        products = {
            "P": {"name": "棕榈油", "sector": "油脂油料"},
            "Y": {"name": "豆油", "sector": "油脂油料"},
        }
        nodes = {"P": "zly_qh", "Y": "dy_qh"}

        class Response:
            def __init__(self, request):
                contract = "P2701" if "zly_qh" in request.full_url else "Y2701"
                self.payload = json.dumps([{"symbol": contract, "volume": 1000, "position": 2000}]).encode()

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return self.payload

        with tempfile.TemporaryDirectory() as temporary:
            data_root = Path(temporary)
            with (
                mock.patch.object(RUNTIME, "PRODUCTS", products),
                mock.patch.object(RUNTIME, "PRODUCT_REALTIME_NODE", nodes),
                mock.patch.object(RUNTIME.urllib.request, "urlopen", side_effect=lambda request, timeout: Response(request)) as fetch,
            ):
                result = RUNTIME.current_contracts(data_root)

        self.assertEqual(result, {"P": ["P2701"], "Y": ["Y2701"]})
        self.assertEqual(fetch.call_count, 2)
        self.assertTrue(all(call.kwargs["timeout"] == 12 for call in fetch.call_args_list))

    def test_cross_sector_universe_and_non_p_signal_score(self):
        self.assertGreaterEqual(len(RUNTIME.PRODUCTS), 40)
        self.assertGreaterEqual(len({row["sector"] for row in RUNTIME.PRODUCTS.values()}), 8)
        score, components, basis = RUNTIME.allocation_score(
            "TA", 1,
            SimpleNamespace(atr=80, close=5100, ma20=5000, ma6=5040, rsi=62),
            SimpleNamespace(volume=900_000, close=5100),
        )
        self.assertGreater(score, 0)
        self.assertIn("liquidity", components)
        self.assertIn("跨板块", basis)

    def test_daily_fetch_has_a_hard_timeout_boundary(self):
        source = (ROOT / "server" / "run_ai_daredevil.py").read_text(encoding="utf-8")
        self.assertIn("urlopen(request, timeout=15)", source)
        self.assertIn("ThreadPoolExecutor", source)
        self.assertIn("pd.Timedelta(days=120)", source)

    def test_daily_fetch_retries_on_the_alternate_history_host(self):
        payload = (
            "var _contract_history=(["
            '{"d":"2026-08-31","o":"100","h":"102","l":"99",'
            '"c":"101","v":"1000","p":"2000","s":"100"}]);'
        ).encode()

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return payload

        with (
            mock.patch.object(
                RUNTIME.urllib.request, "urlopen",
                side_effect=[urllib.error.URLError("temporary"), Response()],
            ) as fetch,
            mock.patch.object(RUNTIME.time_module, "sleep") as sleep,
        ):
            frame = RUNTIME.fetch_daily("MA2611")

        self.assertEqual(len(frame), 1)
        self.assertEqual(fetch.call_count, 2)
        self.assertIn("stock2.finance.sina.com.cn", fetch.call_args_list[0].args[0].full_url)
        self.assertIn("stock.finance.sina.com.cn", fetch.call_args_list[1].args[0].full_url)
        self.assertEqual(fetch.call_args_list[0].kwargs["timeout"], 15)
        sleep.assert_called_once()

    def test_completed_close_cutoff_excludes_the_current_morning_bar(self):
        morning = pd.Timestamp("2026-09-01T09:12:00+08:00").to_pydatetime()
        close = pd.Timestamp("2026-09-01T15:25:00+08:00").to_pydatetime()
        self.assertEqual(str(RUNTIME.completed_close_cutoff(morning)), "2026-08-31")
        self.assertEqual(str(RUNTIME.completed_close_cutoff(close)), "2026-09-01")

    def test_installer_has_exact_session_open_and_hourly_schedule(self):
        installer = (ROOT / "server" / "install_automation.sh").read_text(encoding="utf-8")
        self.assertIn("palm-oil-ai-daredevil.timer", installer)
        self.assertIn("Mon..Fri *-*-* *:00:00 Asia/Shanghai", installer)
        self.assertIn("13:30:00 Asia/Shanghai", installer)
        self.assertIn("15:25:00 Asia/Shanghai", installer)
        self.assertIn("systemctl enable --now palm-oil-ai-daredevil.timer", installer)
        runtime = (ROOT / "server" / "run_ai_daredevil.py").read_text(encoding="utf-8")
        self.assertIn('"run_pure_ai_fund.py"', runtime)

    def test_installer_updates_monthly_backtest_on_first_day(self):
        installer = (ROOT / "server" / "install_automation.sh").read_text(encoding="utf-8")
        self.assertIn("palm-oil-ai-daredevil-backtest.timer", installer)
        self.assertIn("*-*-01 03:20:00 Asia/Shanghai", installer)
        self.assertIn("build_ai_daredevil_monthly_backtest.py", installer)
        self.assertIn("systemctl enable --now palm-oil-ai-daredevil-backtest.timer", installer)

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

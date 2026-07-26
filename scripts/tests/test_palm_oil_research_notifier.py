import importlib.util
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "palm_oil_research_notifier.py"
SPEC = importlib.util.spec_from_file_location("palm_oil_research_notifier", SCRIPT)
NOTIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(NOTIFIER)


def history(count=80):
    return [
        {
            "close": 9000 + index * 5,
            "high": 9050 + index * 5,
            "low": 8950 + index * 5,
        }
        for index in range(count)
    ]


class CalendarAndChunkTest(unittest.TestCase):
    def test_existing_weekday_semantics_are_monday_to_friday(self):
        self.assertTrue(NOTIFIER.is_trading_day(date(2026, 7, 27), set()))
        self.assertTrue(NOTIFIER.is_trading_day(date(2026, 7, 31), set()))
        self.assertFalse(NOTIFIER.is_trading_day(date(2026, 7, 26), set()))

    def test_auto_edition_windows(self):
        tz = ZoneInfo("Asia/Shanghai")
        self.assertEqual(NOTIFIER.auto_edition(datetime(2026, 7, 27, 15, 45, tzinfo=tz)), "close")
        self.assertEqual(NOTIFIER.auto_edition(datetime(2026, 7, 27, 20, 35, tzinfo=tz)), "night")
        self.assertIsNone(NOTIFIER.auto_edition(datetime(2026, 7, 27, 12, 0, tzinfo=tz)))

    def test_only_retry_window_is_final_attempt(self):
        tz = ZoneInfo("Asia/Shanghai")
        self.assertFalse(NOTIFIER.final_attempt("close", datetime(2026, 7, 27, 15, 45, tzinfo=tz)))
        self.assertTrue(NOTIFIER.final_attempt("close", datetime(2026, 7, 27, 16, 0, tzinfo=tz)))
        self.assertFalse(NOTIFIER.final_attempt("night", datetime(2026, 7, 27, 20, 35, tzinfo=tz)))
        self.assertTrue(NOTIFIER.final_attempt("night", datetime(2026, 7, 27, 20, 45, tzinfo=tz)))

    def test_message_is_single_and_bounded(self):
        messages = NOTIFIER.prepare_messages("段落。\n\n" * 1500, "2026-07-27", "close")
        self.assertEqual(len(messages), 1)
        self.assertTrue(all(len(message) <= NOTIFIER.MAX_MESSAGE_CHARS for message in messages))
        self.assertNotIn("·1/", messages[0])

    def test_source_link_table_is_collapsed(self):
        source = """# 晨报

## 【观点】
正文

## 【消息来源链接】
| 来源 | 链接 |
|---|---|
| 示例 | https://example.com/very-long |

## 【AI观点风险提示】
风险
"""
        result = NOTIFIER.normalize_morning_markdown(source, "2026-07-27")
        self.assertIn(NOTIFIER.public_report_url("2026-07-27"), result)
        self.assertNotIn("example.com", result)
        self.assertIn("AI观点风险提示", result)

    def test_installers_keep_existing_weekday_values(self):
        research = (ROOT / "scripts" / "install_palm_oil_research_notifier_launchd.sh").read_text(
            encoding="utf-8"
        )
        daily = (ROOT / "scripts" / "install_daily_watchdog_launchd.sh").read_text(encoding="utf-8")
        for weekday in range(1, 6):
            self.assertIn(f"<integer>{weekday}</integer>", research)
            self.assertIn(f"<integer>{weekday}</integer>", daily)
        self.assertNotIn("<key>Weekday</key><integer>6</integer>", research)
        self.assertNotIn("<key>Weekday</key><integer>6</integer>", daily)
        self.assertIn("notify_morning_research", daily)


class IndicatorAndDeliveryTest(unittest.TestCase):
    def test_indicators_include_required_fields(self):
        result = NOTIFIER.calculate_indicators(history())
        self.assertEqual(result["status"], "ok")
        for key in ["ma", "macd_hist", "rsi14", "kdj_k", "boll_upper", "atr14", "high20", "low60"]:
            self.assertIn(key, result)

    def test_short_history_fails_closed(self):
        self.assertEqual(NOTIFIER.calculate_indicators(history(20))["status"], "insufficient")

    def test_cbot_fetch_converts_chart_to_indicators(self):
        closes = [30 + index * 0.1 for index in range(80)]
        payload = {
            "chart": {
                "result": [
                    {
                        "indicators": {
                            "quote": [
                                {
                                    "close": closes,
                                    "high": [value + 0.3 for value in closes],
                                    "low": [value - 0.3 for value in closes],
                                }
                            ]
                        }
                    }
                ]
            }
        }
        response = mock.Mock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        with mock.patch("requests.get", return_value=response):
            result = NOTIFIER.fetch_cbot_bean_oil()
        self.assertEqual(result["status"], "ok")
        self.assertIn("macd_hist", result)
        self.assertAlmostEqual(result["price"], closes[-1])

    def test_delivery_is_idempotent_and_resumes_parts(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            messages = ["唯一消息"]
            calls = []

            def fake_send(recipient, message, attempts=3):
                calls.append(message)

            with mock.patch.dict(
                NOTIFIER.os.environ,
                {
                    "PALM_OIL_MESSAGE_RECIPIENT": "+8613800000000",
                    "PALM_OIL_MESSAGE_RECEIPT_CONFIRMED": "1",
                },
                clear=False,
            ), mock.patch.object(NOTIFIER, "send_message", side_effect=fake_send), mock.patch.object(
                NOTIFIER.time, "sleep"
            ):
                first = NOTIFIER.deliver(messages, "2026-07-27", "close", base, False)
                second = NOTIFIER.deliver(messages, "2026-07-27", "close", base, False)
            self.assertEqual(first["status"], "submitted_to_messages")
            self.assertEqual(second["status"], "duplicate")
            self.assertEqual(calls, messages)

    def test_delivery_rejects_multiple_bubbles(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(NOTIFIER.ResearchNotifierError):
                NOTIFIER.deliver(
                    ["第一段", "第二段"],
                    "2026-07-27",
                    "close",
                    Path(temporary),
                    True,
                )

    def test_corrupt_state_is_not_silently_reset(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "state.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(NOTIFIER.ResearchNotifierError):
                NOTIFIER.load_state(path)

    def test_logs_exclude_recipient_and_message(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            NOTIFIER.append_log(base, {"recipient": "secret", "message": "body", "status": "ok"})
            text = (base / "runs.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("secret", text)
            self.assertNotIn("body", text)
            self.assertIn('"status": "ok"', text)


if __name__ == "__main__":
    unittest.main()

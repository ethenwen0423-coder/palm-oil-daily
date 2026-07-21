from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
INSTALLER = ROOT / "scripts" / "install_daily_watchdog_launchd.sh"
WEEKLY_INSTALLER = ROOT / "scripts" / "install_weekly_watchdog_launchd.sh"
INTRADAY_INSTALLER = ROOT / "scripts" / "install_oil_futures_tab_launchd.sh"
MARKET_DEPLOY = ROOT / "scripts" / "deploy_oil_futures_tab.sh"
LEGACY_REVIEW_INSTALLER = ROOT / "scripts" / "install_daily_review_launchd.sh"


class DailyWatchdogLaunchdTests(unittest.TestCase):
    def test_watchdog_runs_monday_through_friday(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        schedule = re.findall(
            r"<key>Weekday</key><integer>(\d+)</integer>"
            r"<key>Hour</key><integer>(\d+)</integer>"
            r"<key>Minute</key><integer>(\d+)</integer>",
            text,
        )

        self.assertEqual(
            schedule,
            [(str(day), "8", minute) for minute in ("20", "40") for day in range(1, 6)],
        )

    def test_weekly_watchdog_runs_only_sunday_evening(self) -> None:
        text = WEEKLY_INSTALLER.read_text(encoding="utf-8")
        schedule = re.findall(
            r"<key>Weekday</key><integer>(\d+)</integer>"
            r"<key>Hour</key><integer>(\d+)</integer>"
            r"<key>Minute</key><integer>(\d+)</integer>",
            text,
        )
        self.assertEqual(schedule, [("0", "21", "15"), ("0", "21", "40")])

    def test_intraday_market_refresh_runs_after_midday_and_close(self) -> None:
        text = INTRADAY_INSTALLER.read_text(encoding="utf-8")
        schedule = re.findall(
            r"<key>Weekday</key><integer>(\d+)</integer>"
            r"<key>Hour</key><integer>(\d+)</integer>"
            r"<key>Minute</key><integer>(\d+)</integer>",
            text,
        )
        expected = [
            (str(day), hour, minute)
            for hour, minute in (("11", "35"), ("11", "50"), ("15", "5"), ("15", "20"))
            for day in range(1, 6)
        ]
        self.assertEqual(schedule, expected)
        self.assertIn(r"\$TODAY-\$SESSION.ok", text)
        self.assertIn("already published, skip retry", text)

    def test_market_deploy_updates_both_technical_datasets(self) -> None:
        text = MARKET_DEPLOY.read_text(encoding="utf-8")
        self.assertIn("update_oil_futures_data.py", text)
        self.assertIn("update_exchange_futures_data.py", text)
        self.assertIn("data/exchange_futures.js", text)
        self.assertIn("--update-session", text)

    def test_daily_retry_does_not_repeat_morning_market_publish(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn("$REPORT_DATE-morning.ok", text)
        self.assertIn("daily and morning market data already published, skip retry", text)
        self.assertIn("deploy_oil_futures_tab.sh morning", text)

    def test_watchdogs_follow_codex_default_model(self) -> None:
        for installer in (INSTALLER, WEEKLY_INSTALLER):
            text = installer.read_text(encoding="utf-8")
            self.assertNotIn("--model", text)
            self.assertNotRegex(text, r"gpt-[0-9]")

    def test_watchdogs_resolve_current_codex_executable(self) -> None:
        for installer in (INSTALLER, WEEKLY_INSTALLER):
            text = installer.read_text(encoding="utf-8")
            self.assertIn("/Applications/ChatGPT.app/Contents/Resources/codex", text)
            self.assertIn("command -v codex", text)

    def test_legacy_2305_review_installer_is_removed(self) -> None:
        self.assertFalse(LEGACY_REVIEW_INSTALLER.exists())


if __name__ == "__main__":
    unittest.main()

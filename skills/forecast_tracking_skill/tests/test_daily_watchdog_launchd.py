from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
INSTALLER = ROOT / "scripts" / "install_daily_watchdog_launchd.sh"
WEEKLY_INSTALLER = ROOT / "scripts" / "install_weekly_watchdog_launchd.sh"
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

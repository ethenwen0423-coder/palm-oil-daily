from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
INSTALLER = ROOT / "scripts" / "install_daily_watchdog_launchd.sh"
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
            [(str(day), "8", minute) for minute in ("20", "40") for day in range(2, 7)],
        )

    def test_legacy_2305_review_installer_is_removed(self) -> None:
        self.assertFalse(LEGACY_REVIEW_INSTALLER.exists())


if __name__ == "__main__":
    unittest.main()

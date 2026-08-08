from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "server" / "freeze_prepared_forecast.py"
SPEC = importlib.util.spec_from_file_location("server_prepared_forecast", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeUpdate:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.events: list[str] = []

    def load_forecast_time_metadata(self, report_date: str):
        self.events.append("metadata")
        return {"report_date": report_date}

    def run_data_quality_gate(self, path: Path) -> None:
        self.events.append(f"gate:{path.name}")

    def run_forecast_recorder(self, path: Path, metadata: dict[str, str]):
        self.events.append(f"freeze:{metadata['report_date']}")
        return {"forecast": "data/forecast/daily/test.json", "already_exists": False}

    def write_forecast_time_metadata(self, metadata: dict[str, str]) -> Path:
        self.events.append("write-metadata")
        return ROOT / "source_runs" / "test" / "forecast_time_metadata.json"


class ServerPreparedForecastTests(unittest.TestCase):
    def test_quality_gate_precedes_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            oil = Path(temporary) / "oil_futures.js"
            oil.write_text("window.OIL_FUTURES_CONTRACTS = {};", encoding="utf-8")
            fake = FakeUpdate(ROOT)
            with mock.patch.object(MODULE, "load_update_module", return_value=fake):
                result = MODULE.freeze("2026-08-08", oil)

        self.assertEqual(
            fake.events,
            ["metadata", "gate:oil_futures.js", "freeze:2026-08-08", "write-metadata"],
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import sys
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "oil_timeout_test", ROOT / "scripts" / "update_oil_futures_data.py"
)
assert SPEC and SPEC.loader
oil = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oil)


class AkshareCallTimeoutTests(unittest.TestCase):
    def test_returns_result_before_timeout(self) -> None:
        self.assertEqual(oil.akshare_call(lambda: "ok", timeout=1), "ok")

    def test_returns_none_and_interrupts_stalled_call(self) -> None:
        started = time.monotonic()
        self.assertIsNone(oil.akshare_call(lambda: time.sleep(5), timeout=1))
        self.assertLess(time.monotonic() - started, 2.5)


if __name__ == "__main__":
    unittest.main()

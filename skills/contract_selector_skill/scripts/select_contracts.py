#!/usr/bin/env python3
"""Compatibility entrypoint for contract_selector_skill."""

from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_SCRIPT = ROOT / "skills" / "contract_discovery_skill" / "scripts" / "select_contracts.py"


if __name__ == "__main__":
    runpy.run_path(str(DISCOVERY_SCRIPT), run_name="__main__")

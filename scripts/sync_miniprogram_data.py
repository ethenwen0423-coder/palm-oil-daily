#!/usr/bin/env python3
"""Publish website datasets as JSON endpoints and mini-program fallbacks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MINI_DATA_DIR = ROOT / "miniprogram" / "data"

DATASETS = {
    "reports": {
        "source": DATA_DIR / "reports.js",
        "prefix": "window.PALM_OIL_REPORTS = ",
        "json": DATA_DIR / "reports.json",
        "module": MINI_DATA_DIR / "reports.js",
    },
    "oil-futures": {
        "source": DATA_DIR / "oil_futures.js",
        "prefix": "window.OIL_FUTURES_CONTRACTS = ",
        "json": DATA_DIR / "oil_futures.json",
        "module": MINI_DATA_DIR / "oil_futures.js",
    },
}


def publish_dataset(name: str, payload: Any) -> None:
    config = DATASETS[name]
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    config["json"].parent.mkdir(parents=True, exist_ok=True)
    MINI_DATA_DIR.mkdir(parents=True, exist_ok=True)
    config["json"].write_text(text + "\n", encoding="utf-8")
    config["module"].write_text(f"module.exports = {text};\n", encoding="utf-8")


def load_existing(name: str) -> Any:
    config = DATASETS[name]
    text = config["source"].read_text(encoding="utf-8").strip()
    prefix = config["prefix"]
    if not text.startswith(prefix) or not text.endswith(";"):
        raise ValueError(f"unexpected dataset wrapper: {config['source']}")
    return json.loads(text[len(prefix) : -1])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "datasets",
        nargs="*",
        choices=sorted(DATASETS),
        default=list(DATASETS),
    )
    args = parser.parse_args()
    for name in args.datasets:
        publish_dataset(name, load_existing(name))
        print(f"synced {name} for mini program")


if __name__ == "__main__":
    main()

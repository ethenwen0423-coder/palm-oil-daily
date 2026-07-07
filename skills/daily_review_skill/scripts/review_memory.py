#!/usr/bin/env python3
"""Rolling 30-day storage for daily oil-futures review details."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DAILY_REVIEW_DIR = ROOT / "data" / "review" / "daily"
LOG_PATH = ROOT / "data" / "review" / "review_memory.log"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")


def _date_from_name(path: Path) -> datetime | None:
    if not DATE_RE.fullmatch(path.name):
        return None
    try:
        return datetime.strptime(path.stem, "%Y-%m-%d")
    except ValueError:
        return None


def _log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_recent_reviews(days: int = 30) -> dict[str, Any]:
    """Load only recent daily review JSON files from data/review/daily."""
    warnings: list[str] = []
    if not DAILY_REVIEW_DIR.exists():
        return {"reviews": [], "warnings": warnings, "loaded_count": 0}

    today = datetime.now().date()
    cutoff = today - timedelta(days=days - 1)
    candidates: list[tuple[datetime, Path]] = []
    for path in DAILY_REVIEW_DIR.glob("*.json"):
        parsed = _date_from_name(path)
        if parsed is None:
            warnings.append(f"ignored invalid review filename: {_relative(path)}")
            continue
        if parsed.date() < cutoff:
            continue
        candidates.append((parsed, path))

    reviews: list[dict[str, Any]] = []
    for _, path in sorted(candidates, key=lambda item: item[0]):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            warning = f"ignored damaged review file: {_relative(path)} ({exc})"
            warnings.append(warning)
            _log(warning)
            continue
        reviews.append({"path": _relative(path), "payload": payload})

    return {"reviews": reviews, "warnings": warnings, "loaded_count": len(reviews)}


def prune_old_reviews(days: int = 30) -> dict[str, Any]:
    """Keep only the latest N valid dated daily review files."""
    warnings: list[str] = []
    deleted: list[str] = []
    DAILY_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    safe_dir = DAILY_REVIEW_DIR.resolve()
    dated: list[tuple[datetime, Path]] = []

    for path in DAILY_REVIEW_DIR.iterdir():
        if not path.is_file() or not path.name.endswith(".json"):
            continue
        parsed = _date_from_name(path)
        if parsed is None:
            warnings.append(f"ignored invalid review filename: {_relative(path)}")
            continue
        if parsed.date() > datetime.now().date():
            warnings.append(f"future review retained: {_relative(path)}")
            continue
        dated.append((parsed, path))

    dated.sort(key=lambda item: item[0], reverse=True)
    for _, path in dated[days:]:
        resolved = path.resolve()
        if safe_dir not in resolved.parents or not DATE_RE.fullmatch(path.name):
            warnings.append(f"refused unsafe delete: {_relative(path)}")
            continue
        path.unlink()
        deleted_path = _relative(path)
        deleted.append(deleted_path)
        _log(f"deleted old daily review: {deleted_path}")

    retained_count = len([path for path in DAILY_REVIEW_DIR.glob("*.json") if _date_from_name(path) is not None])
    return {"retained_count": retained_count, "deleted": deleted, "warnings": warnings}


def save_today_review(review: dict[str, Any], days: int = 30) -> dict[str, Any]:
    """Save review to data/review/daily/YYYY-MM-DD.json and prune old daily details."""
    date_text = str(review.get("date") or "")
    try:
        parsed = datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("review['date'] must be YYYY-MM-DD") from exc

    DAILY_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    target = DAILY_REVIEW_DIR / f"{parsed:%Y-%m-%d}.json"
    target.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    prune = prune_old_reviews(days=days)
    return {
        "saved": _relative(target),
        "retained_count": prune["retained_count"],
        "deleted": prune["deleted"],
        "warnings": prune["warnings"],
    }


if __name__ == "__main__":
    print(json.dumps(load_recent_reviews(), ensure_ascii=False, indent=2))

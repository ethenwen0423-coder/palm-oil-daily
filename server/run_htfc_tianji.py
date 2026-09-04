#!/usr/bin/env python3
"""Refresh read-only HTFC Tianji evidence into the live API data mount."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
SUPPLEMENTAL_REFRESH_HOURS = (7, 10, 14, 18)
PUBLIC_SEARCH_SIZE = 100
PUBLIC_CACHE_PATHS = {
    "oil": Path("research_cache/report_search_oil.json"),
    "cross": Path("research_cache/report_search_cross.json"),
}
MX_CACHE_PATHS = {
    "oil": Path("research_cache/mx_search_oil.json"),
    "cross": Path("research_cache/mx_search_cross.json"),
}


def supplemental_refresh_slot(now: datetime) -> str | None:
    """Limit each paid public-search source to four two-query batches per day."""
    local = now.astimezone(ZoneInfo("Asia/Shanghai"))
    eligible = [hour for hour in SUPPLEMENTAL_REFRESH_HOURS if local.hour >= hour]
    if not eligible:
        return None
    return f"{local.date().isoformat()}T{max(eligible):02d}"


def should_attempt_supplemental(configured: bool, slot: str | None, previous_slot: object, force: bool) -> bool:
    return configured and slot is not None and (force or previous_slot != slot)


def load_previous_source_status(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    value = payload.get("source_status", {}) if isinstance(payload, dict) else {}
    return value if isinstance(value, dict) else {}


def retained_source_status(previous: dict[str, object], configured: bool, slot: str | None) -> dict[str, object]:
    if not configured:
        return {"configured": False, "status": "not_configured"}
    result: dict[str, object] = {
        "configured": True,
        "status": "scheduled" if slot is None else "cached",
    }
    for key in ("attempt_slot", "last_attempt_at"):
        value = previous.get(key)
        if value:
            result[key] = value
    return result


def failure_status(output: str) -> str:
    normalized = output.lower()
    quota_markers = ("次数已用完", "调用次数已达到上限", "额度", "quota", "rate limit")
    return "quota_exhausted" if any(marker in normalized for marker in quota_markers) else "request_failed"


def load_sync(site_root: Path):
    path = site_root / "server" / "sync_live_data.py"
    spec = importlib.util.spec_from_file_location("palm_sync_live_data", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("live-data sync module is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def restore_cached_inputs(output_root: Path, live_data_root: Path, cache_paths: dict[str, Path]) -> list[str]:
    inputs: list[str] = []
    for relative in cache_paths.values():
        source = live_data_root / relative
        target = output_root / relative
        if not source.is_file():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        inputs.append(str(target))
    return inputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)))
    parser.add_argument("--live-data-root", type=Path, default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)))
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--force-supplemental-refresh", action="store_true", help="refresh paid public research sources even when the current slot was already attempted")
    args = parser.parse_args()
    site_root = args.site_root.resolve()
    live_data_root = args.live_data_root.resolve()
    try:
        sync = load_sync(site_root)
        with tempfile.TemporaryDirectory(prefix="server-htfc-tianji.") as temporary:
            output_root = Path(temporary)
            output = output_root / "htfc_tianji.json"
            htfc_fresh = False
            payload: dict[str, object] = {}
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(site_root / "scripts" / "update_htfc_tianji_data.py"),
                        "--output",
                        str(output),
                        "--timeout",
                        str(args.timeout),
                    ],
                    cwd=site_root,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=max(args.timeout * 8, 120),
                    check=False,
                )
                if result.returncode == 0 and output.is_file():
                    payload = json.loads(output.read_text(encoding="utf-8"))
                    htfc_fresh = bool(payload.get("available_modules"))
            except (subprocess.TimeoutExpired, json.JSONDecodeError):
                htfc_fresh = False
            if not htfc_fresh:
                existing_htfc = live_data_root / "htfc_tianji.json"
                if existing_htfc.is_file():
                    try:
                        shutil.copy2(existing_htfc, output)
                        payload = json.loads(output.read_text(encoding="utf-8"))
                    except json.JSONDecodeError:
                        payload = {}
                if not payload:
                    payload = {
                        "schema_version": 1,
                        "status": "unavailable",
                        "available_modules": [],
                    }
                    output.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            public_cache_inputs = restore_cached_inputs(output_root, live_data_root, PUBLIC_CACHE_PATHS)
            public_search_inputs = [value for path in public_cache_inputs for value in ("--public-search", path)]
            public_search_count = 0
            scan_now = datetime.now(ZoneInfo("Asia/Shanghai"))
            refresh_slot = supplemental_refresh_slot(scan_now)
            previous_status = load_previous_source_status(live_data_root / "research_watch.json")
            iwencai_configured = bool(os.environ.get("IWENCAI_API_KEY", "").strip())
            mx_configured = bool(os.environ.get("MX_APIKEY", "").strip())
            source_status = {
                "institution-report-skill": {"configured": True, "status": "ready" if htfc_fresh else "unavailable"},
                "report-search": retained_source_status(
                    previous_status.get("report-search", {}) if isinstance(previous_status.get("report-search"), dict) else {},
                    iwencai_configured,
                    refresh_slot,
                ),
                "mx-search": retained_source_status(
                    previous_status.get("mx-search", {}) if isinstance(previous_status.get("mx-search"), dict) else {},
                    mx_configured,
                    refresh_slot,
                ),
            }
            previous_iwencai = previous_status.get("report-search", {}) if isinstance(previous_status.get("report-search"), dict) else {}
            attempt_iwencai = should_attempt_supplemental(
                iwencai_configured,
                refresh_slot,
                previous_iwencai.get("attempt_slot"),
                args.force_supplemental_refresh,
            )
            if attempt_iwencai:
                source_status["report-search"] = {
                    "configured": True,
                    "status": "request_failed",
                    "attempt_slot": refresh_slot,
                    "last_attempt_at": scan_now.isoformat(timespec="seconds"),
                }
                public_failures: list[str] = []
                today = scan_now.date()
                yesterday = today - timedelta(days=1)
                date_window = (
                    f"{yesterday.year}年{yesterday.month}月{yesterday.day}日"
                    f"至{today.year}年{today.month}月{today.day}日"
                )
                for name, query in (
                    ("oil", f"{date_window} 棕榈油 豆油 菜油 油脂油料 期货研报 研究报告"),
                    ("cross", f"{date_window} 原油 宏观 农产品 期货研报 研究报告"),
                ):
                    public_output = output_root / PUBLIC_CACHE_PATHS[name]
                    public_output.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        public_result = subprocess.run(
                            [
                                sys.executable,
                                str(site_root / "scripts" / "update_public_research_search.py"),
                                "--query",
                                query,
                                "--output",
                                str(public_output),
                                "--timeout",
                                str(args.timeout),
                                "--size",
                                str(PUBLIC_SEARCH_SIZE),
                            ],
                            cwd=site_root,
                            env={**os.environ, "PYTHONUNBUFFERED": "1"},
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            timeout=max(args.timeout * 2, 90),
                            check=False,
                        )
                    except subprocess.TimeoutExpired:
                        public_failures.append("request_failed")
                        continue
                    if public_result.returncode == 0 and public_output.is_file():
                        public_search_count += 1
                    else:
                        public_failures.append(failure_status(public_result.stdout or ""))
                if public_search_count:
                    source_status["report-search"]["status"] = "ready"
                elif "quota_exhausted" in public_failures:
                    source_status["report-search"]["status"] = "quota_exhausted"
            public_search_inputs = [
                value
                for relative in PUBLIC_CACHE_PATHS.values()
                if (output_root / relative).is_file()
                for value in ("--public-search", str(output_root / relative))
            ]
            mx_cache_inputs = restore_cached_inputs(output_root, live_data_root, MX_CACHE_PATHS)
            mx_search_inputs = [value for path in mx_cache_inputs for value in ("--mx-search", path)]
            mx_search_count = 0
            previous_mx = previous_status.get("mx-search", {}) if isinstance(previous_status.get("mx-search"), dict) else {}
            attempt_mx = should_attempt_supplemental(
                mx_configured,
                refresh_slot,
                previous_mx.get("attempt_slot"),
                args.force_supplemental_refresh,
            )
            if attempt_mx:
                source_status["mx-search"] = {
                    "configured": True,
                    "status": "request_failed",
                    "attempt_slot": refresh_slot,
                    "last_attempt_at": scan_now.isoformat(timespec="seconds"),
                }
                mx_failures: list[str] = []
                today = scan_now.date()
                yesterday = today - timedelta(days=1)
                date_window = (
                    f"{yesterday.year}年{yesterday.month}月{yesterday.day}日"
                    f"至{today.year}年{today.month}月{today.day}日"
                )
                for name, query in (
                    ("oil", f"{date_window} 棕榈油 豆油 菜油 油脂油料 券商研报 研究报告"),
                    ("cross", f"{date_window} 原油 宏观 农产品 券商研报 研究报告"),
                ):
                    mx_output = output_root / MX_CACHE_PATHS[name]
                    mx_output.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        mx_result = subprocess.run(
                            [
                                sys.executable,
                                str(site_root / "scripts" / "update_mx_research_search.py"),
                                "--query",
                                query,
                                "--output",
                                str(mx_output),
                                "--timeout",
                                str(args.timeout),
                            ],
                            cwd=site_root,
                            env={**os.environ, "PYTHONUNBUFFERED": "1"},
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            timeout=max(args.timeout * 2, 90),
                            check=False,
                        )
                    except subprocess.TimeoutExpired:
                        mx_failures.append("request_failed")
                        continue
                    if mx_result.returncode == 0 and mx_output.is_file():
                        mx_search_count += 1
                    else:
                        mx_failures.append(failure_status(mx_result.stdout or ""))
                if mx_search_count:
                    source_status["mx-search"]["status"] = "ready"
                elif "quota_exhausted" in mx_failures:
                    source_status["mx-search"]["status"] = "quota_exhausted"
            mx_search_inputs = [
                value
                for relative in MX_CACHE_PATHS.values()
                if (output_root / relative).is_file()
                for value in ("--mx-search", str(output_root / relative))
            ]
            source_status_output = output_root / "research_source_status.json"
            source_status_output.write_text(json.dumps(source_status, ensure_ascii=False), encoding="utf-8")
            research_output = output_root / "research_watch.json"
            research_result = subprocess.run(
                [
                    sys.executable,
                    str(site_root / "scripts" / "build_research_watch.py"),
                    "--input",
                    str(output),
                    "--existing",
                    str(live_data_root / "research_watch.json"),
                    "--output",
                    str(research_output),
                    *public_search_inputs,
                    *mx_search_inputs,
                    "--source-status",
                    str(source_status_output),
                ],
                cwd=site_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=30,
                check=False,
            )
            if research_result.returncode != 0 or not research_output.is_file():
                raise RuntimeError("research watch builder did not produce a dataset")
            copied = sync.sync_htfc(output_root, live_data_root, session="scheduled")
        print(json.dumps({
            "status": payload.get("status"),
            "generated_at": payload.get("generated_at"),
            "available_modules": payload.get("available_modules"),
            "htfc_fresh": htfc_fresh,
            "public_search_count": public_search_count,
            "mx_search_count": mx_search_count,
            "source_status": source_status,
            "copied": copied.get("copied", []),
        }, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)[:300], "retry": True}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

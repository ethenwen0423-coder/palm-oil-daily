#!/usr/bin/env python3
"""Generate and atomically publish one source-grounded AI market brief."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_RUNTIME_ROOT = Path("/srv/palm-oil-daily/ai-runtime")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
DEFAULT_STATE_ROOT = Path("/srv/palm-oil-daily/state")
DEFAULT_TIMEOUT_SECONDS = 600


class AiBriefRunnerError(RuntimeError):
    """Raised when the server cannot safely publish a verified AI brief."""


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AiBriefRunnerError(f"cannot load server module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODEL_BACKEND = load_module(
    "server_model_backend",
    Path(__file__).with_name("model_backend.py"),
)


def model_backend_configured() -> bool:
    return MODEL_BACKEND.backend_configured()


def validate_brief(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AiBriefRunnerError("AI brief output is missing or invalid JSON") from exc
    if not isinstance(payload, dict):
        raise AiBriefRunnerError("AI brief output must be a JSON object")
    if payload.get("schema_version") != 1 or payload.get("status") != "ready":
        raise AiBriefRunnerError("AI brief output failed schema/status validation")
    if (
        not payload.get("source_fingerprint")
        or not payload.get("key_moves")
        or not payload.get("sector_views")
    ):
        raise AiBriefRunnerError("AI brief output is missing grounding evidence")
    if payload.get("fixed_logic") != [
        "otc_structure_library",
        "quant_model_rules",
    ]:
        raise AiBriefRunnerError("AI brief fixed-logic boundary changed")
    source_snapshot = payload.get("source_snapshot")
    if (
        not isinstance(source_snapshot, dict)
        or not source_snapshot.get("quant-model-signals")
    ):
        raise AiBriefRunnerError("AI brief did not consume dynamic quant-model output")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)),
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_AI_RUNTIME_ROOT", DEFAULT_RUNTIME_ROOT)),
    )
    parser.add_argument(
        "--live-data-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)),
    )
    parser.add_argument(
        "--state-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", DEFAULT_STATE_ROOT)),
    )
    parser.add_argument("--mock-response", type=Path)
    # Subscription-backed Codex structured output can legitimately need more
    # than five minutes on the small production host.  This is a server-only
    # execution envelope; the report prompt, schema and publication gate stay
    # identical to the repository generator.
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    site_root = args.site_root.resolve()
    runtime_root = args.runtime_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_root = args.state_root.resolve()
    support = load_module(
        "server_market_collector_support",
        Path(__file__).with_name("run_market_collector.py"),
    )
    try:
        support.validate_runtime_paths(site_root, runtime_root, live_data_root)
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2

    backend = (
        "mock"
        if args.mock_response
        else MODEL_BACKEND.resolve_config(require_key=False)["backend"]
        if model_backend_configured()
        else "missing"
    )
    plan = {
        "status": "planned" if backend != "missing" else "blocked",
        "backend": backend,
        "site_root": str(site_root),
        "runtime_root": str(runtime_root),
        "live_data_root": str(live_data_root),
        "first_generation_required": not (
            live_data_root / ".server-ai-ready.json"
        ).exists(),
    }
    if args.dry_run:
        print(json.dumps({**plan, "dry_run": True}, ensure_ascii=False, sort_keys=True))
        return 0 if backend != "missing" else 2
    if backend == "missing":
        print(
            json.dumps(
                {
                    **plan,
                    "reason": "no authenticated unattended model backend is configured",
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2

    lock = support.acquire_lock(state_root / "automation.lock")
    if lock is None:
        print(json.dumps({"status": "busy", "retry": True}, ensure_ascii=False))
        return 0
    log_path = state_root / "ai-brief.log"
    try:
        sync_module = support.import_sync_module(site_root)
        sync_module.sync_upstream(site_root / "data", live_data_root)
        support.ensure_runtime(site_root, runtime_root)
        support.copy_live_inputs(live_data_root, runtime_root)
        with tempfile.TemporaryDirectory(prefix="server-ai-brief.") as temporary:
            output_root = Path(temporary) / "data"
            output_path = output_root / "market_assistant_brief.json"
            command = [
                sys.executable,
                "scripts/update_market_assistant_brief.py",
                "--output",
                str(output_path),
                "--previous-output",
                str(live_data_root / "market_assistant_brief.json"),
                "--timeout",
                str(args.timeout),
            ]
            if args.force or not (live_data_root / sync_module.AI_READY_MARKER).exists():
                command.append("--force")
            if args.mock_response:
                command.extend(["--mock-response", str(args.mock_response.resolve())])
            environment = {
                **os.environ,
                "PYTHONUNBUFFERED": "1",
            }
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as log:
                support.run_checked(
                    command,
                    cwd=runtime_root,
                    environment=environment,
                    timeout=max(args.timeout + 60, 120),
                    output=log,
                )
            payload = validate_brief(output_path)
            synced = sync_module.sync_ai(
                output_root,
                live_data_root,
                session=str(payload.get("update_session") or "manual"),
            )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "backend": backend,
                    "generated_at": payload.get("generated_at"),
                    "source_fingerprint": payload.get("source_fingerprint"),
                    "copied": synced["copied"],
                    "server_ai_owned": True,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (AiBriefRunnerError, OSError, RuntimeError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "reason": str(exc),
                    "retry": True,
                    "server_ai_owned": (
                        live_data_root / ".server-ai-ready.json"
                    ).exists(),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    finally:
        support.fcntl.flock(lock.fileno(), support.fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

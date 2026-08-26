#!/usr/bin/env python3
"""Read-only readiness audit for the 24-hour server automation runtime."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_DEPLOY_ROOT = Path("/srv/palm-oil-daily/deploy")
DEFAULT_MARKET_PYTHON = Path("/srv/palm-oil-daily/venv/bin/python")
DEFAULT_STATE_ROOT = Path("/srv/palm-oil-daily/state")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
REQUIRED_PYTHON_MODULES = ("requests", "akshare", "pandas", "numpy")
REQUIRED_REPOSITORY_PATHS = (
    "server/enable_ai_automation.sh",
    "server/install_automation.sh",
    "server/install_codex_cli.sh",
    "server/requirements-market.txt",
    "server/run_ai_brief.py",
    "server/run_research_agent.py",
    "server/run_prediction_review.py",
    "server/build_report_inputs.py",
    "server/freeze_prepared_forecast.py",
    "server/run_market_collector.py",
    "server/run_supply_demand.py",
    "server/sync_live_data.py",
    "scripts/deploy_oil_futures_tab.sh",
    "scripts/deploy_report.sh",
    "scripts/review_prediction.py",
    "scripts/update_oil_futures_data.py",
    "scripts/update_exchange_futures_data.py",
    "scripts/update_quant_model_data.py",
    "skills/data_quality_gate_skill/scripts/validate_data.py",
)
AUTOMATION_UNIT_PATTERN = re.compile(r"(palm|oil|market)", re.IGNORECASE)


def run(
    arguments: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 15,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            arguments,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            env={
                **os.environ,
                **(environment or {}),
                "GIT_TERMINAL_PROMPT": "0",
            },
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(arguments, 127, "", str(exc))


def command_output(
    arguments: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 15,
) -> str:
    result = run(arguments, cwd=cwd, timeout=timeout)
    return result.stdout.strip() if result.returncode == 0 else ""


def remote_host(remote: str) -> str | None:
    value = remote.strip()
    if not value:
        return None
    if "://" in value:
        return urlsplit(value).hostname
    match = re.match(r"^(?:[^@]+@)?([^:]+):", value)
    return match.group(1) if match else None


def read_os_release(path: Path = Path("/etc/os-release")) -> str | None:
    try:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator:
                values[key] = value.strip().strip('"')
        return values.get("PRETTY_NAME") or values.get("NAME")
    except OSError:
        return None


def git_value(site_root: Path, *arguments: str) -> str:
    if not (site_root / ".git").exists():
        return ""
    return command_output(["git", *arguments], cwd=site_root)


def repository_status(site_root: Path, *, network: bool) -> dict[str, Any]:
    remote = git_value(site_root, "remote", "get-url", "origin")
    missing = [
        relative
        for relative in REQUIRED_REPOSITORY_PATHS
        if not (site_root / relative).exists()
    ]
    network_fetch_ready: bool | None = None
    if network and (site_root / ".git").exists():
        network_fetch_ready = (
            run(
                ["git", "ls-remote", "--exit-code", "origin", "refs/heads/main"],
                cwd=site_root,
                timeout=30,
            ).returncode
            == 0
        )
    return {
        "path": str(site_root),
        "exists": site_root.is_dir(),
        "is_git_checkout": (site_root / ".git").exists(),
        "branch": git_value(site_root, "branch", "--show-current") or None,
        "head": git_value(site_root, "rev-parse", "--short", "HEAD") or None,
        "clean": not bool(git_value(site_root, "status", "--porcelain", "--untracked-files=all")),
        "origin_host": remote_host(remote),
        "origin_main": git_value(site_root, "rev-parse", "--short", "refs/remotes/origin/main")
        or None,
        "network_fetch_ready": network_fetch_ready,
        "missing_required_paths": missing,
        "data_writable": os.access(site_root / "data", os.W_OK),
    }


def compose_path(deploy_root: Path) -> Path | None:
    for name in ("compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"):
        candidate = deploy_root / name
        if candidate.exists():
            return candidate
    return None


def inspect_api_mounts(container_id: str) -> list[dict[str, Any]]:
    if not container_id:
        return []
    result = run(
        ["docker", "inspect", "--format", "{{json .Mounts}}", container_id],
        timeout=15,
    )
    if result.returncode != 0:
        return []
    try:
        mounts = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return [
        {
            "type": item.get("Type"),
            "source": item.get("Source"),
            "destination": item.get("Destination"),
            "read_only": not bool(item.get("RW")),
        }
        for item in mounts
        if isinstance(item, dict) and item.get("Destination") in {"/site", "/site/data"}
    ]


def docker_status(deploy_root: Path) -> dict[str, Any]:
    config = compose_path(deploy_root)
    override = deploy_root / "compose.automation.yaml"
    docker_available = shutil.which("docker") is not None
    compose_available = False
    services: list[str] = []
    running_services: list[str] = []
    api_mounts: list[dict[str, Any]] = []
    if docker_available:
        compose_available = run(["docker", "compose", "version"]).returncode == 0
    if config and compose_available:
        base = ["docker", "compose", "-f", str(config)]
        if override.is_file():
            base.extend(["-f", str(override)])
        services = command_output([*base, "config", "--services"]).splitlines()
        running_services = command_output(
            [*base, "ps", "--status", "running", "--services"]
        ).splitlines()
        container_id = command_output([*base, "ps", "-q", "api"])
        api_mounts = inspect_api_mounts(container_id)
    return {
        "available": docker_available,
        "compose_available": compose_available,
        "compose_path": str(config) if config else None,
        "compose_override": str(override) if override.is_file() else None,
        "services": services,
        "running_services": running_services,
        "api_mounts": api_mounts,
        "api_running": "api" in running_services,
        "web_running": "web" in running_services,
    }


def public_web_listeners() -> list[str] | None:
    """Return non-loopback TCP listeners on HTTP(S) ports, if ss is available."""
    if shutil.which("ss") is None:
        return None
    result = run(["ss", "-H", "-lnt"], timeout=15)
    if result.returncode != 0:
        return None
    listeners: list[str] = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue
        endpoint = fields[3]
        host, separator, port = endpoint.rpartition(":")
        if not separator or port not in {"80", "443"}:
            continue
        normalized_host = host.strip("[]")
        if normalized_host in {"127.0.0.1", "::1", "localhost"}:
            continue
        listeners.append(endpoint)
    return sorted(set(listeners))


def timezone_name() -> str | None:
    value = command_output(["timedatectl", "show", "-p", "Timezone", "--value"])
    if value:
        return value
    try:
        return Path("/etc/timezone").read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def systemd_status() -> dict[str, Any]:
    available = shutil.which("systemctl") is not None
    units: list[str] = []
    timers: list[str] = []
    if available:
        unit_output = command_output(
            ["systemctl", "list-unit-files", "--no-legend", "--no-pager"],
            timeout=20,
        )
        units = [
            line.split()[0]
            for line in unit_output.splitlines()
            if line.strip() and AUTOMATION_UNIT_PATTERN.search(line.split()[0])
        ][:50]
        timer_output = command_output(
            ["systemctl", "list-timers", "--all", "--no-legend", "--no-pager"],
            timeout=20,
        )
        timers = [
            line.strip()
            for line in timer_output.splitlines()
            if AUTOMATION_UNIT_PATTERN.search(line)
        ][:50]
    required = (
        "palm-oil-market-collector.timer",
        "palm-oil-event-watch.timer",
        "palm-oil-supply-demand.timer",
        "palm-oil-ai-brief.timer",
        "palm-oil-research-agent.timer",
        "palm-oil-prediction-review.timer",
    )
    states: dict[str, dict[str, bool]] = {}
    if available:
        for name in required:
            states[name] = {
                "enabled": run(["systemctl", "is-enabled", "--quiet", name]).returncode == 0,
                "active": run(["systemctl", "is-active", "--quiet", name]).returncode == 0,
            }
    else:
        states = {name: {"enabled": False, "active": False} for name in required}
    return {
        "available": available,
        "unit_files": units,
        "timers": timers,
        "required_timers": states,
    }


def live_data_status(site_root: Path, live_data_root: Path) -> dict[str, Any]:
    try:
        import importlib.util

        script = site_root / "server" / "api.py"
        spec = importlib.util.spec_from_file_location("server_audit_api", script)
        if spec is None or spec.loader is None:
            raise OSError(f"cannot load {script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        status = module.build_status(live_data_root)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return {
            "path": str(live_data_root),
            "available": False,
            "error": str(exc),
            "status": "invalid",
            "datasets": {},
            "automation": {},
        }
    return {
        "path": str(live_data_root),
        "available": live_data_root.is_dir(),
        "status": status.get("status"),
        "datasets": status.get("datasets", {}),
        "automation": status.get("automation", {}),
    }


def probe_python_modules(executable: Path) -> tuple[str | None, dict[str, bool]]:
    script = (
        "import importlib.util,json,platform;"
        f"names={REQUIRED_PYTHON_MODULES!r};"
        "print(json.dumps({'version':platform.python_version(),"
        "'modules':{name:importlib.util.find_spec(name) is not None for name in names}}))"
    )
    result = run([str(executable), "-c", script])
    if result.returncode != 0:
        return None, {name: False for name in REQUIRED_PYTHON_MODULES}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, {name: False for name in REQUIRED_PYTHON_MODULES}
    modules = payload.get("modules")
    if not isinstance(modules, dict):
        modules = {}
    return (
        str(payload.get("version") or "") or None,
        {name: bool(modules.get(name)) for name in REQUIRED_PYTHON_MODULES},
    )


def python_status(
    site_root: Path,
    market_python: Path = DEFAULT_MARKET_PYTHON,
) -> dict[str, Any]:
    executable = market_python if market_python.is_file() else Path(sys.executable)
    version, modules = probe_python_modules(executable)
    technical_runtime = (
        site_root
        / "skills"
        / "technical_basic_analysis_skill"
        / "scripts"
        / "runtime_indicators.py"
    )
    return {
        "executable": str(executable),
        "version": version,
        "modules": modules,
        "technical_runtime_present": technical_runtime.exists(),
    }


def credential_capabilities(
    deploy_root: Path,
    state_root: Path = DEFAULT_STATE_ROOT,
) -> dict[str, bool]:
    configured_codex = os.environ.get("CODEX_BIN", "").strip()
    codex_bin = (
        configured_codex
        if configured_codex
        and os.path.isfile(configured_codex)
        and os.access(configured_codex, os.X_OK)
        else shutil.which("codex") or ""
    )
    codex_home = state_root / "home" / ".codex"
    codex_status = (
        run(
            [codex_bin, "login", "status"],
            timeout=20,
            environment={
                "HOME": str(state_root / "home"),
                "CODEX_HOME": str(codex_home),
                "XDG_CACHE_HOME": str(state_root / "cache"),
            },
        )
        if codex_bin
        else None
    )
    codex_status_text = (
        f"{codex_status.stdout}\n{codex_status.stderr}".lower()
        if codex_status is not None
        else ""
    )
    codex_authenticated = bool(
        codex_status is not None
        and codex_status.returncode == 0
        and "chatgpt" in codex_status_text
    )
    openai_env_file = Path(
        os.environ.get(
            "PALM_OIL_AI_ENV_FILE",
            os.environ.get("PALM_OIL_OPENAI_ENV_FILE", "/etc/palm-oil-ai.env"),
        )
    )
    openai_api_key_configured = False
    model_api_key_configured = False
    model_provider = "missing"
    try:
        mode = openai_env_file.stat().st_mode & 0o777
        lines = openai_env_file.read_text(encoding="utf-8").splitlines()
        openai_api_key_configured = mode == 0o600 and any(
            line.startswith("OPENAI_API_KEY=") and len(line) > len("OPENAI_API_KEY=")
            for line in lines
        )
        model_api_key_configured = mode == 0o600 and any(
            line.startswith(prefix) and len(line) > len(prefix)
            for line in lines
            for prefix in (
                "PALM_OIL_AI_API_KEY=",
                "OPENAI_API_KEY=",
            )
        )
        provider_line = next(
            (line for line in lines if line.startswith("PALM_OIL_AI_PROVIDER=")),
            "",
        )
        model_provider = provider_line.partition("=")[2].strip() or (
            "openai" if openai_api_key_configured else "missing"
        )
    except OSError:
        pass
    return {
        "codex_cli_present": bool(codex_bin),
        "codex_cli_authenticated": codex_authenticated,
        "codex_auth_method": "chatgpt" if codex_authenticated else "missing",
        "openai_api_key_present": bool(os.environ.get("OPENAI_API_KEY")),
        "openai_api_key_configured": openai_api_key_configured,
        "model_api_key_present": bool(
            os.environ.get("PALM_OIL_AI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        ),
        "model_api_key_configured": model_api_key_configured,
        "model_provider": model_provider,
        "github_token_present": bool(os.environ.get("GITHUB_TOKEN")),
        "git_credential_helper_configured": bool(
            command_output(["git", "config", "--global", "--get", "credential.helper"])
        ),
        "deploy_env_present": (deploy_root / ".env").is_file(),
        "private_env_present": (deploy_root / "private.env").is_file()
        or (state_root / "private.env").is_file(),
    }


def build_audit(
    site_root: Path,
    deploy_root: Path,
    *,
    network: bool = False,
    access_mode: str = "private",
    state_root: Path = DEFAULT_STATE_ROOT,
    live_data_root: Path = DEFAULT_LIVE_DATA_ROOT,
) -> dict[str, Any]:
    repository = repository_status(site_root, network=network)
    docker = docker_status(deploy_root)
    python = python_status(site_root)
    systemd = systemd_status()
    credentials = credential_capabilities(deploy_root, state_root)
    live_data = live_data_status(site_root, live_data_root)
    public_listeners = public_web_listeners()
    blockers: list[str] = []
    if platform.system() != "Linux":
        blockers.append("server audit must run on Linux")
    if not repository["is_git_checkout"]:
        blockers.append("site checkout is missing")
    if repository["missing_required_paths"]:
        blockers.append("repository automation dependencies are incomplete")
    if not docker["compose_available"] or not docker["api_running"]:
        blockers.append("Docker Compose API service is not running")
    if access_mode == "private" and docker["web_running"]:
        blockers.append("public web service is running during private mode")
    if access_mode == "private" and public_listeners:
        blockers.append("public HTTP(S) listeners are active during private mode")
    missing_modules = [name for name, ready in python["modules"].items() if not ready]
    if missing_modules:
        blockers.append(f"missing Python modules: {', '.join(missing_modules)}")
    if not python["technical_runtime_present"]:
        blockers.append("repository technical-indicator runtime is missing")
    ai_backend = (
        "codex-chatgpt-quota"
        if credentials["model_provider"] == "codex"
        and credentials["codex_cli_authenticated"]
        else "missing"
    )
    if ai_backend == "missing":
        blockers.append(
            "Codex CLI is not selected and authenticated with ChatGPT subscription access"
        )
    required_timer_states = systemd.get("required_timers", {})
    inactive_timers = [
        name
        for name, state in required_timer_states.items()
        if not state.get("enabled") or not state.get("active")
    ]
    if inactive_timers:
        blockers.append(f"required automation timers are inactive: {', '.join(inactive_timers)}")
    if not (state_root / "research-backend.accepted.json").is_file():
        blockers.append("server research model has not passed real-output acceptance")
    if not live_data.get("available"):
        blockers.append("server live-data directory is unavailable")
    unavailable_datasets = [
        route
        for route, item in live_data.get("datasets", {}).items()
        if item.get("state") in {"missing", "invalid"}
    ]
    if unavailable_datasets:
        blockers.append(
            "server live datasets are unavailable: " + ", ".join(unavailable_datasets)
        )
    for owner in ("market", "supply", "ai"):
        if live_data.get("automation", {}).get(owner, {}).get("state") != "ready":
            blockers.append(f"server {owner} automation has no successful ownership marker")
    api_data_mount = next(
        (
            item
            for item in docker["api_mounts"]
            if item.get("destination") == "/site/data"
        ),
        None,
    )
    return {
        "schema_version": 1,
        "status": "ready" if not blockers else "blocked",
        "read_only": True,
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "os": read_os_release(),
            "timezone": timezone_name(),
            "user": os.environ.get("USER") or os.environ.get("LOGNAME"),
            "uid": os.getuid(),
        },
        "repository": repository,
        "docker": docker,
        "systemd": systemd,
        "live_data": live_data,
        "python": python,
        "credentials": credentials,
        "access": {
            "mode": access_mode,
            "public_web_listeners": public_listeners,
            "web_service_running": docker["web_running"],
        },
        "migration": {
            "market_collector_ready": not bool(missing_modules)
            and python["technical_runtime_present"],
            "ai_backend": ai_backend,
            "api_data_mount": api_data_mount,
            "research_backend_accepted": (
                state_root / "research-backend.accepted.json"
            ).is_file(),
            "live_data_mount_required": not bool(
                api_data_mount
                and str(api_data_mount.get("source") or "").rstrip("/").endswith(
                    "/live-data"
                )
            ),
        },
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)),
    )
    parser.add_argument(
        "--live-data-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)),
    )
    parser.add_argument(
        "--deploy-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_DEPLOY_ROOT", DEFAULT_DEPLOY_ROOT)),
    )
    parser.add_argument(
        "--network",
        action="store_true",
        help="also verify read-only access to origin/main",
    )
    parser.add_argument(
        "--access-mode",
        choices=("private", "public"),
        default=os.environ.get("PALM_OIL_PUBLIC_ACCESS_MODE", "private"),
        help="expected public-access state; private fails when web listeners exist",
    )
    parser.add_argument(
        "--state-root",
        type=Path,
        default=Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", DEFAULT_STATE_ROOT)),
    )
    args = parser.parse_args()
    payload = build_audit(
        args.site_root.resolve(),
        args.deploy_root.resolve(),
        network=args.network,
        access_mode=args.access_mode,
        state_root=args.state_root.resolve(),
        live_data_root=args.live_data_root.resolve(),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run configured financial skill entrypoints and save auditable raw outputs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = Path.home() / ".codex" / "skills"
SOURCE_RUNS = ROOT / "source_runs"


def shlex_join(parts: list[str]) -> str:
    return " ".join(subprocess.list2cmdline([part]) for part in parts)


def run_command(
    name: str,
    command: list[str],
    output_dir: Path,
    timeout: int,
    env: dict[str, str],
) -> dict[str, object]:
    started_at = datetime.now().isoformat(timespec="seconds")
    stdout_path = output_dir / f"{name}.stdout.txt"
    stderr_path = output_dir / f"{name}.stderr.txt"
    try:
        result = subprocess.run(
            command,
            cwd=str(ROOT),
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        status = "ok" if result.returncode == 0 else "failed"
        return {
            "name": name,
            "status": status,
            "returncode": result.returncode,
            "command": shlex_join(command),
            "started_at": started_at,
            "finished_at": datetime.now().isoformat(timespec="seconds"),
            "stdout": str(stdout_path.relative_to(ROOT)),
            "stderr": str(stderr_path.relative_to(ROOT)),
        }
    except subprocess.TimeoutExpired as exc:
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text(exc.stderr or f"timeout after {timeout}s", encoding="utf-8")
        return {
            "name": name,
            "status": "timeout",
            "returncode": None,
            "command": shlex_join(command),
            "started_at": started_at,
            "finished_at": datetime.now().isoformat(timespec="seconds"),
            "stdout": str(stdout_path.relative_to(ROOT)),
            "stderr": str(stderr_path.relative_to(ROOT)),
        }


def skill_path(name: str) -> Path:
    return SKILLS / name


def normalize_weekly_futures_data(source: Path, target: Path) -> None:
    """Create a compatibility copy for the installed weekly report script."""
    if not source.exists():
        return
    data = json.loads(source.read_text(encoding="utf-8"))
    spread = data.get("fundamental", {}).get("spread", {})
    for key in ["soybean_palm_spread", "rapeseed_soybean_spread"]:
        value = spread.get(key)
        if isinstance(value, dict):
            spread[key] = value.get("price")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_commands(report_date: str, kind: str, output_dir: Path) -> list[tuple[str, list[str]]]:
    raw = output_dir / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    futures = skill_path("futures-oil-daily")
    mx_search = skill_path("mx-search")
    mx_data = skill_path("mx-data")
    report_search = skill_path("report-search")
    hithink = skill_path("hithink-market-query")

    futures_data = raw / "futures_market_data.json"
    futures_report_data = (
        raw / "futures_market_data.weekly_compatible.json" if kind == "weekend" else futures_data
    )
    futures_report = raw / f"futures_oil_{kind}.md"
    futures_report_script = (
        futures / "scripts" / "generate_weekly_report.py"
        if kind == "weekend"
        else futures / "scripts" / "generate_daily_report.py"
    )
    news_query = (
        "棕榈油 豆油 菜油 油脂油料 周报 MPOB MPOA ITS GAPKI USDA CME ICE DCE 印尼B50 马来出口 库存 原油 豆棕价差 菜豆价差"
        if kind == "weekend"
        else "棕榈油 豆油 菜油 油脂油料 晨报 FCPO 原油 美豆油 美元 人民币 马来出口 库存 今日交易 豆棕价差"
    )
    market_query = (
        "棕榈油期货主力合约 豆油 菜油 最新价 涨跌幅 成交量 持仓量 周涨跌"
        if kind == "weekend"
        else "棕榈油期货主力合约 豆油 菜油 夜盘 最新价 涨跌幅 成交量 持仓量"
    )
    research_query = (
        "棕榈油 豆油 菜油 油脂油料 周报 研报 行情预测 豆棕价差 菜豆价差 永安期货 中信期货 国泰君安期货 银河期货"
        if kind == "weekend"
        else "棕榈油 豆油 菜油 油脂油料 晨报 交易策略 行情预测 永安期货 中信期货 国泰君安期货 银河期货"
    )

    commands: list[tuple[str, list[str]]] = [
        (
            "futures_oil_fetch_market_data",
            [
                sys.executable,
                str(futures / "scripts" / "fetch_market_data.py"),
                "--date",
                report_date,
                "--output",
                str(futures_data),
            ],
        ),
    ]
    if kind == "weekend":
        commands.append(
            (
                "futures_oil_normalize_weekly_data",
                ["__normalize_weekly_futures_data__", str(futures_data), str(futures_report_data)],
            )
        )
    commands.extend(
        [
        (
            "futures_oil_generate_report",
            [
                sys.executable,
                str(futures_report_script),
                "--date",
                report_date,
                "--data",
                str(futures_report_data),
                "--output",
                str(futures_report),
            ],
        ),
        (
            "mx_search_news",
            [
                sys.executable,
                str(mx_search / "scripts" / "search_mx.py"),
                "--query",
                news_query,
                "--output",
                "json",
                "--save",
                str(raw / "mx_search_news.json"),
            ],
        ),
        (
            "mx_data_market",
            [
                sys.executable,
                str(mx_data / "scripts" / "query_mx_data.py"),
                "--query",
                market_query,
                "--output",
                "json",
                "--save",
                str(raw / "mx_data_market.json"),
            ],
        ),
        (
            "iwencai_market",
            [
                sys.executable,
                str(hithink / "scripts" / "cli.py"),
                "--query",
                market_query,
                "--limit",
                "10",
            ],
        ),
        (
            "report_search_research",
            [
                sys.executable,
                str(report_search / "scripts" / "research_report_search.py"),
                "-q",
                research_query,
                "-l",
                "10",
                "-f",
                "json",
                "-o",
                str(raw / "report_search_research.json"),
            ],
        ),
        ]
    )
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="Run palm-oil report financial skill sources.")
    parser.add_argument("--date", required=True, help="Report date, YYYY-MM-DD")
    parser.add_argument("--kind", choices=["daily", "weekend"], required=True)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if any configured source command fails.",
    )
    args = parser.parse_args()

    output_dir = SOURCE_RUNS / f"{args.date}-{args.kind}"
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    skill_status = {}
    for name in [
        "futures-oil-daily",
        "commodity-analysis",
        "mx-search",
        "mx-data",
        "report-search",
        "hithink-market-query",
    ]:
        path = skill_path(name)
        skill_status[name] = {
            "path": str(path),
            "installed": path.exists(),
            "skill_md": str(path / "SKILL.md") if (path / "SKILL.md").exists() else None,
        }

    env_status = {
        "MX_APIKEY": bool(env.get("MX_APIKEY")),
        "IWENCAI_API_KEY": bool(env.get("IWENCAI_API_KEY")),
    }

    results = []
    for name, command in build_commands(args.date, args.kind, output_dir):
        if command[0] == "__normalize_weekly_futures_data__":
            started_at = datetime.now().isoformat(timespec="seconds")
            try:
                normalize_weekly_futures_data(Path(command[1]), Path(command[2]))
                results.append(
                    {
                        "name": name,
                        "status": "ok",
                        "returncode": 0,
                        "command": shlex_join(command),
                        "started_at": started_at,
                        "finished_at": datetime.now().isoformat(timespec="seconds"),
                    }
                )
            except Exception as exc:  # noqa: BLE001 - audit script must record failures.
                results.append(
                    {
                        "name": name,
                        "status": "failed",
                        "returncode": None,
                        "command": shlex_join(command),
                        "started_at": started_at,
                        "finished_at": datetime.now().isoformat(timespec="seconds"),
                        "error": str(exc),
                    }
                )
            continue
        missing_executable = command[1] if len(command) > 1 and command[1].endswith(".py") else None
        if missing_executable and not Path(missing_executable).exists():
            results.append(
                {
                    "name": name,
                    "status": "missing_script",
                    "returncode": None,
                    "command": shlex_join(command),
                    "started_at": datetime.now().isoformat(timespec="seconds"),
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
            continue
        results.append(run_command(name, command, output_dir, args.timeout, env))

    manifest = {
        "date": args.date,
        "kind": args.kind,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "skills": skill_status,
        "environment": env_status,
        "results": results,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = all(item.get("status") == "ok" for item in results)
    print(f"source manifest: {manifest_path.relative_to(ROOT)}")
    print(f"source status: {'ok' if ok else 'has_failures'}")
    return 0 if ok or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())

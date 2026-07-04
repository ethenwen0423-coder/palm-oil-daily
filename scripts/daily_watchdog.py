#!/usr/bin/env python3
"""Check whether today's daily report was published and backfill it if missing."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_FILE = Path.home() / ".codex" / "automations" / "automation" / "automation.toml"
REPORTS_FILE = ROOT / "data" / "reports.js"
REPORTS_DIR = ROOT / "reports"
LOG_DIR = ROOT / "logs" / "daily-watchdog"
LOCK_DIR = ROOT / ".daily-watchdog.lock"
SHANGHAI = ZoneInfo("Asia/Shanghai")


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(SHANGHAI).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line)
    with (LOG_DIR / f"{datetime.now(SHANGHAI):%Y-%m-%d}.log").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def today_string(override: str | None) -> str:
    if override:
        return override
    return datetime.now(SHANGHAI).strftime("%Y-%m-%d")


def is_weekday(report_date: str) -> bool:
    return datetime.strptime(report_date, "%Y-%m-%d").weekday() < 5


def report_is_published(report_date: str) -> bool:
    report_path = REPORTS_DIR / f"{report_date}.md"
    if not report_path.exists() or report_path.stat().st_size == 0:
        return False
    if not REPORTS_FILE.exists():
        return False

    text = REPORTS_FILE.read_text(encoding="utf-8")
    marker = f'"date": "{report_date}"'
    if marker not in text:
        return False

    content = report_path.read_text(encoding="utf-8")
    forbidden = ["未实际调用", "当前环境未暴露调用入口", "这是测试报告", "排版调试样稿"]
    return not any(word in content for word in forbidden)


def load_automation_prompt() -> tuple[str, str]:
    if not AUTOMATION_FILE.exists():
        raise FileNotFoundError(f"missing automation config: {AUTOMATION_FILE}")
    text = AUTOMATION_FILE.read_text(encoding="utf-8")
    prompt_match = re.search(r'^prompt\s*=\s*"(?P<value>(?:\\.|[^"])*)"', text, re.M | re.S)
    model_match = re.search(r'^model\s*=\s*"(?P<value>[^"]+)"', text, re.M)
    if not prompt_match:
        raise ValueError(f"missing prompt in automation config: {AUTOMATION_FILE}")
    prompt = json.loads(f'"{prompt_match.group("value")}"')
    model = model_match.group("value") if model_match else "gpt-5.5"
    return prompt, model


def acquire_lock() -> bool:
    try:
        LOCK_DIR.mkdir()
        (LOCK_DIR / "pid").write_text(str(os.getpid()), encoding="utf-8")
        return True
    except FileExistsError:
        pid_file = LOCK_DIR / "pid"
        age = time.time() - LOCK_DIR.stat().st_mtime
        if age > 60 * 60:
            log("发现超过1小时的旧锁，清理后继续")
            if pid_file.exists():
                pid_file.unlink()
            LOCK_DIR.rmdir()
            return acquire_lock()
        return False


def release_lock() -> None:
    pid_file = LOCK_DIR / "pid"
    if pid_file.exists():
        pid_file.unlink()
    if LOCK_DIR.exists():
        LOCK_DIR.rmdir()


def run_backfill(report_date: str, dry_run: bool) -> int:
    prompt, model = load_automation_prompt()
    backfill_prompt = f"""
这是棕榈油每日晨报的兜底补跑任务。

原因：到 08:50 仍未检测到 {report_date} 的正式日报已经发布到网站数据。

请严格按原日报自动任务执行，但使用固定报告日期 {report_date}，不要改成其他日期。
必须先运行 git pull --ff-only。
必须先读取并调用 skills/master_report_skill/SKILL.md，按 market_data_skill、oil_report_freshness、report_writer_skill、headline_skill、report_quality_gate 顺序调度。
必须调用 scripts/run_financial_skills.py 并读取 source_runs/{report_date}-daily/manifest.json。
必须调用 skills/oil-report-freshness/SKILL.md 后再进入正文写作和标题生成。
必须生成或更新 reports/{report_date}.md，然后运行 bash scripts/deploy_report.sh 发布。
如果今天不是中国期货市场交易日，停止发布并说明原因。
如果已发现报告实际存在且合格，停止补跑。

原日报任务要求如下：

{prompt}
""".strip()

    log(f"日报缺失，启动补跑：{report_date}")
    if dry_run:
        log("dry-run 模式：不实际执行 codex")
        return 0

    run_dir = LOG_DIR / report_date
    run_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = run_dir / f"codex-{datetime.now(SHANGHAI):%H%M%S}.stdout.log"
    stderr_path = run_dir / f"codex-{datetime.now(SHANGHAI):%H%M%S}.stderr.log"

    command = [
        "codex",
        "exec",
        "--cd",
        str(ROOT),
        "--model",
        model,
        "--sandbox",
        "danger-full-access",
        "--dangerously-bypass-approvals-and-sandbox",
        "-",
    ]
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr:
        result = subprocess.run(
            command,
            input=backfill_prompt,
            text=True,
            cwd=str(ROOT),
            stdout=stdout,
            stderr=stderr,
            check=False,
        )

    if result.returncode == 0 and report_is_published(report_date):
        log(f"补跑完成并检测到网站数据已更新：{report_date}")
        return 0

    if result.returncode == 0:
        log(f"补跑进程结束，但未检测到合格网站数据：{report_date}")
        return 2

    log(f"补跑失败，退出码 {result.returncode}；详见 {stdout_path} / {stderr_path}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill missing palm-oil daily reports.")
    parser.add_argument("--date", help="Report date, YYYY-MM-DD. Defaults to today in Asia/Shanghai.")
    parser.add_argument("--force", action="store_true", help="Run backfill even if report exists.")
    parser.add_argument("--dry-run", action="store_true", help="Only log what would happen.")
    args = parser.parse_args()

    report_date = today_string(args.date)
    if not is_weekday(report_date):
        log(f"{report_date} 不是周一至周五，跳过日报兜底")
        return 0

    if not acquire_lock():
        log("已有日报兜底任务在运行，跳过本次检查")
        return 0

    try:
        if report_is_published(report_date) and not args.force:
            log(f"{report_date} 日报已发布，兜底检查通过")
            return 0
        return run_backfill(report_date, args.dry_run)
    finally:
        release_lock()


if __name__ == "__main__":
    sys.exit(main())

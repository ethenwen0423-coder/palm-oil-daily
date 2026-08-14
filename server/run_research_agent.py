#!/usr/bin/env python3
"""Generate one governed daily or weekend report entirely on the server."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_SITE_ROOT = Path("/srv/palm-oil-daily/site")
DEFAULT_RUNTIME_ROOT = Path("/srv/palm-oil-daily/research-runtime")
DEFAULT_LIVE_DATA_ROOT = Path("/srv/palm-oil-daily/live-data")
DEFAULT_STATE_ROOT = Path("/srv/palm-oil-daily/state")
FIXED_LOGIC = ["otc_structure_library", "quant_model_rules"]
ALLOWED_CHANGED_PREFIXES = (
    "data/",
    "downloads/",
    "miniprogram/data/",
    "reports/",
)


class ResearchAgentError(RuntimeError):
    """Raised when a report cannot be safely generated or published internally."""


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ResearchAgentError(f"cannot load server module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODEL_BACKEND = load_module(
    "server_model_backend",
    Path(__file__).with_name("model_backend.py"),
)


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(SHANGHAI)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def select_due(now: datetime, force_kind: str | None = None) -> str | None:
    if force_kind:
        return force_kind
    minutes = now.hour * 60 + now.minute
    if 1 <= now.isoweekday() <= 5 and minutes >= 360:
        return "daily"
    if now.isoweekday() == 7 and minutes >= 21 * 60 + 15:
        return "weekend"
    return None


def report_id(report_date: str, kind: str) -> str:
    return f"{report_date}-weekend" if kind == "weekend" else report_date


def report_is_ready(path: Path, identity: str) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(payload, list) and any(
        isinstance(item, dict)
        and item.get("date") == identity
        and len(str(item.get("content") or "")) >= 800
        for item in payload
    )


def model_backend_configured() -> bool:
    return MODEL_BACKEND.backend_configured()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text.rstrip() + "\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))


def restore_persistent_outputs(state_root: Path, runtime_root: Path) -> None:
    report_store = state_root / "research-reports"
    if report_store.is_dir():
        for source in report_store.glob("*.md"):
            shutil.copy2(source, runtime_root / "reports" / source.name)
    data_store = state_root / "research-data"
    for relative in ("forecast", "review"):
        source = data_store / relative
        if source.is_dir():
            shutil.copytree(
                source,
                runtime_root / "data" / relative,
                dirs_exist_ok=True,
                copy_function=shutil.copy2,
            )


def persist_outputs(
    state_root: Path,
    runtime_root: Path,
    report_path: Path,
) -> None:
    report_store = state_root / "research-reports"
    report_store.mkdir(parents=True, exist_ok=True)
    shutil.copy2(report_path, report_store / report_path.name)
    data_store = state_root / "research-data"
    for relative in ("forecast", "review"):
        source = runtime_root / "data" / relative
        if source.is_dir():
            shutil.copytree(
                source,
                data_store / relative,
                dirs_exist_ok=True,
                copy_function=shutil.copy2,
            )


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchAgentError(f"cannot read governed input: {path}") from exc


def build_prompt(
    *,
    report_date: str,
    kind: str,
    source_snapshot: dict[str, Any],
    feedback: dict[str, Any] | None,
    correction: str,
) -> str:
    sections = (
        [
            "今日观点",
            "今日交易信号",
            "核心驱动与预期差",
            "关键数据与价格",
            "开盘推演",
            "风险提示",
            "信息来源与核验说明",
            "消息来源链接",
            "AI观点风险提示",
        ]
        if kind == "daily"
        else [
            "一句话核心观点",
            "本周验证与预期差",
            "核心数据变化",
            "下周主线与事件",
            "周一开盘推演",
            "交易计划",
            "风险提示",
            "信息来源与核验说明",
            "消息来源链接",
            "AI观点风险提示",
        ]
    )
    budget = "1000-1400" if kind == "daily" else "1600-2000"
    title = datetime.fromisoformat(report_date).strftime("%m月%d日") + (
        "晨报" if kind == "daily" else "周报"
    )
    disclosure_text = (
        json.dumps(feedback.get("required_report_disclosures", []), ensure_ascii=False)
        if feedback
        else "[]"
    )
    correction_block = f"\n上次门禁反馈，必须逐项修正：\n{correction}\n" if correction else ""
    return f"""
你是部署在腾讯云、只使用给定证据的油脂研究报告写作器。不要联网，不要调用工具，不要读取其他文件。

只输出符合 JSON Schema 的 JSON 对象。report_markdown 是完整 Markdown，outline 是内部审计提纲，fixed_logic 必须原样为 {json.dumps(FIXED_LOGIC, ensure_ascii=False)}。

硬性边界：
1. 报告日期为 {report_date}，类型为 {kind}，一级标题必须精确为“# {title}”。
2. 正文栏目按此顺序且标题格式为 `## 【栏目】`：{json.dumps(sections, ensure_ascii=False)}。
3. 正文可见字符预算 {budget}；消息链接与固定免责声明不计入预算。
4. 只能复制 SOURCE_JSON 中的数字、价格、涨跌、时间、合约、score 与 strategy_recommendation；禁止自行计算或创造任何价格、概率、止损、目标、仓位与来源。
5. P/Y/OI 三个 rank=1 合约及其 exact price 必须在关键数据中各出现一次；每个数字同时写明 SOURCE_JSON 中的时点口径。
6. 今日/下周交易计划必须来自 strategy_recommendation。若源中没有止损、目标或仓位，明确写“源数据未给出，不新开仓”，不得补造数字。
7. 只选两个 Level 1 驱动，写清事实→机制→P/Y/OI影响→预期与现实→结论；最强反证和可检验失效条件必须明确。
8. 日报的 `今日策略：偏多/偏空/震荡/观望` 必须与 outline.market_stance 完全一致；周报也必须在正文落实该基准方向。
9. outline 的 trade_trigger、confirmation_condition、stop_loss、target_range、position_limit、signal_expiry 必须逐字出现在正文。
10. 日报在“信息来源与核验说明”中逐字包含 REQUIRED_DISCLOSURES 的每一句；反馈只能降低置信度或增加反证，不能提高置信度。
11. 缺失信息统一写“需进一步核验”；禁止把未核验信息升级为主驱动。场外结构类型库和量化模型规则不可更改。
12. 最后固定写 AI 风险声明，说明仅为研究判断、不构成投资建议或交易指令。

REQUIRED_DISCLOSURES：
{disclosure_text}

SOURCE_JSON：
{json.dumps(source_snapshot, ensure_ascii=False, sort_keys=True)}
{correction_block}
""".strip()


def run_openai(schema: Path, prompt: str, *, timeout: int) -> dict[str, Any]:
    try:
        output, _backend = MODEL_BACKEND.request_json(
            schema=load_json(schema),
            schema_name="server_research_report",
            prompt=prompt,
            timeout=timeout,
            verbosity="medium",
            model=os.environ.get("PALM_OIL_RESEARCH_AI_MODEL", "").strip() or None,
        )
        return output
    except MODEL_BACKEND.ModelBackendError as exc:
        raise ResearchAgentError(str(exc)) from exc


def validate_model_output(
    payload: Any,
    *,
    report_date: str,
    kind: str,
) -> tuple[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ResearchAgentError("research model output must be a JSON object")
    if payload.get("fixed_logic") != FIXED_LOGIC:
        raise ResearchAgentError("research model changed the fixed-logic boundary")
    markdown = payload.get("report_markdown")
    outline = payload.get("outline")
    if not isinstance(markdown, str) or len(markdown) < 800:
        raise ResearchAgentError("research report markdown is missing or too short")
    if not isinstance(outline, dict):
        raise ResearchAgentError("research report outline is missing")
    if outline.get("report_date") != report_date or outline.get("kind") != kind:
        raise ResearchAgentError("research outline date/kind mismatch")
    expected = datetime.fromisoformat(report_date).strftime("%m月%d日") + (
        "晨报" if kind == "daily" else "周报"
    )
    if not markdown.lstrip().startswith(f"# {expected}\n"):
        raise ResearchAgentError("research report title mismatch")
    forbidden = ("未实际调用", "当前环境未暴露调用入口", "这是测试报告", "排版调试样稿")
    if any(value in markdown for value in forbidden):
        raise ResearchAgentError("research report contains a forbidden placeholder")
    return markdown, outline


def validate_change_scope(runtime_root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=runtime_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ResearchAgentError("cannot inspect research runtime changes")
    changed: list[str] = []
    for line in completed.stdout.splitlines():
        path = line[3:].split(" -> ")[-1]
        changed.append(path)
        if not path.startswith(ALLOWED_CHANGED_PREFIXES):
            raise ResearchAgentError(f"research agent changed protected path: {path}")
    return changed


def run_deploy(
    runtime_root: Path,
    environment: dict[str, str],
    log_path: Path,
    *,
    timeout: int,
) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["bash", "scripts/deploy_report.sh"],
            cwd=runtime_root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ResearchAgentError(f"report gate did not complete: {exc}") from exc
    output = (completed.stdout or "") + (completed.stderr or "")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(output)
        if output and not output.endswith("\n"):
            log.write("\n")
    return completed.returncode == 0, output[-5000:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(os.environ.get("PALM_OIL_SITE_ROOT", DEFAULT_SITE_ROOT)))
    parser.add_argument("--runtime-root", type=Path, default=Path(os.environ.get("PALM_OIL_RESEARCH_RUNTIME_ROOT", DEFAULT_RUNTIME_ROOT)))
    parser.add_argument("--live-data-root", type=Path, default=Path(os.environ.get("PALM_OIL_LIVE_DATA_ROOT", DEFAULT_LIVE_DATA_ROOT)))
    parser.add_argument("--state-root", type=Path, default=Path(os.environ.get("PALM_OIL_SERVER_STATE_ROOT", DEFAULT_STATE_ROOT)))
    parser.add_argument("--now", default=os.environ.get("PALM_OIL_RESEARCH_NOW"))
    parser.add_argument("--force-kind", choices=("daily", "weekend"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--acceptance-only",
        action="store_true",
        help="Run a real model-backed report draft acceptance without publishing it.",
    )
    parser.add_argument("--mock-response", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now = parse_now(args.now)
    kind = select_due(now, args.force_kind)
    if not kind:
        print(json.dumps({"status": "noop", "reason": "no_report_due", "now": now.isoformat(timespec="seconds")}, ensure_ascii=False))
        return 0
    report_date = now.date().isoformat()
    identity = report_id(report_date, kind)
    site_root = args.site_root.resolve()
    runtime_root = args.runtime_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_root = args.state_root.resolve()
    support = load_module("server_research_support", Path(__file__).with_name("run_market_collector.py"))
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
        "report_date": report_date,
        "kind": kind,
        "report_id": identity,
        "runtime_root": str(runtime_root),
        "live_data_root": str(live_data_root),
    }
    if args.dry_run:
        print(json.dumps({**plan, "dry_run": True}, ensure_ascii=False, sort_keys=True))
        return 0 if backend != "missing" else 2
    if backend == "missing":
        print(json.dumps({**plan, "reason": "no authenticated unattended model backend is configured"}, ensure_ascii=False, sort_keys=True))
        return 2
    if args.attempts < 1 or args.attempts > 3:
        print(json.dumps({"status": "error", "reason": "attempts must be between 1 and 3"}, ensure_ascii=False))
        return 2

    lock = support.acquire_lock(state_root / "automation.lock")
    if lock is None:
        print(json.dumps({"status": "busy", "retry": True}, ensure_ascii=False))
        return 0
    log_path = state_root / "research-agent.log"
    try:
        sync_module = support.import_sync_module(site_root)
        sync_module.sync_upstream(site_root / "data", live_data_root)
        if (
            report_is_ready(live_data_root / "reports.json", identity)
            and not args.force
            and not args.acceptance_only
        ):
            print(json.dumps({"status": "noop", "reason": "report_already_ready", "report_id": identity}, ensure_ascii=False))
            return 0

        support.ensure_runtime(site_root, runtime_root)
        restore_persistent_outputs(state_root, runtime_root)
        support.copy_live_inputs(live_data_root, runtime_root)
        input_builder = load_module(
            "server_report_input_builder",
            site_root / "server" / "build_report_inputs.py",
        )
        built = input_builder.write_source_run(
            live_data_root,
            runtime_root,
            report_date,
            kind,
            now,
        )
        source_snapshot = load_json(Path(built["snapshot"]))
        feedback = None
        if kind == "daily":
            feedback_value = load_json(runtime_root / "data" / "forecast" / "feedback" / "latest.json")
            if not isinstance(feedback_value, dict):
                raise ResearchAgentError("daily forecast feedback must be a JSON object")
            feedback = feedback_value

        if args.acceptance_only:
            prompt = build_prompt(
                report_date=report_date,
                kind=kind,
                source_snapshot=source_snapshot,
                feedback=feedback,
                correction="",
            )
            if args.mock_response:
                model_payload = load_json(args.mock_response.resolve())
            else:
                model_payload = run_openai(
                    site_root / "references" / "server_report_output.schema.json",
                    prompt,
                    timeout=args.timeout,
                )
            markdown, outline = validate_model_output(
                model_payload,
                report_date=report_date,
                kind=kind,
            )
            accepted = {
                "status": "ok",
                "acceptance": "real_model_report_draft_validated",
                "backend": backend,
                "report_date": report_date,
                "kind": kind,
                "markdown_chars": len(markdown),
                "market_stance": outline.get("market_stance"),
                "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            }
            support.atomic_state_marker(
                state_root / "research-backend.accepted.json",
                accepted,
            )
            print(json.dumps(accepted, ensure_ascii=False, sort_keys=True))
            return 0

        report_path = runtime_root / "reports" / f"{identity}.md"
        run_root = Path(built["run_root"])
        outline_path = run_root / "report_outline.json"
        quality_path = run_root / "report_quality.json"
        schema = site_root / "references" / "server_report_output.schema.json"
        environment = {
            **os.environ,
            "PALM_OIL_PUBLISH_MODE": "files",
            "PALM_OIL_REPORT_DATA_MODE": "prepared",
            "PYTHONUNBUFFERED": "1",
        }
        correction = ""
        attempts = 1 if args.mock_response else args.attempts
        success = False
        last_gate = ""
        for attempt in range(1, attempts + 1):
            prompt = build_prompt(
                report_date=report_date,
                kind=kind,
                source_snapshot=source_snapshot,
                feedback=feedback,
                correction=correction,
            )
            if args.mock_response:
                model_payload = load_json(args.mock_response.resolve())
            else:
                model_payload = run_openai(schema, prompt, timeout=args.timeout)
            markdown, outline = validate_model_output(
                model_payload,
                report_date=report_date,
                kind=kind,
            )
            atomic_write_text(report_path, markdown)
            atomic_write_json(outline_path, outline)
            success, last_gate = run_deploy(
                runtime_root,
                environment,
                log_path,
                timeout=max(args.timeout, 300),
            )
            if success:
                break
            quality = load_json(quality_path) if quality_path.exists() else {}
            correction = json.dumps(
                {"gate_output": last_gate, "report_quality": quality},
                ensure_ascii=False,
            )[-9000:]
        if not success:
            raise ResearchAgentError(f"report remained blocked after {attempts} attempt(s): {last_gate[-1200:]}")

        quality = load_json(quality_path)
        if not isinstance(quality, dict) or quality.get("can_publish") is not True:
            raise ResearchAgentError("report quality gate did not produce can_publish=true")
        if not report_is_ready(runtime_root / "data" / "reports.json", identity):
            raise ResearchAgentError("internal reports dataset does not contain the new report")
        if kind == "daily" and not (runtime_root / "data" / "forecast" / "daily" / f"{report_date}.json").is_file():
            raise ResearchAgentError("daily report did not freeze its prediction record")
        if kind == "daily":
            previous_snapshot = (
                runtime_root
                / "data"
                / "review"
                / "runtime_snapshots"
                / f"{report_date}-previous-oil_futures.js"
            )
            previous_snapshot.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(runtime_root / "data" / "oil_futures.js", previous_snapshot)
        changed = validate_change_scope(runtime_root)
        persist_outputs(state_root, runtime_root, report_path)
        synced = sync_module.sync_research(
            runtime_root / "data",
            live_data_root,
            session=kind,
        )
        completed = {
            "status": "ok",
            "report_id": identity,
            "kind": kind,
            "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            "quality_score": quality.get("score"),
            "changed": changed,
            "copied": synced["copied"],
            "server_research_owned": True,
        }
        support.atomic_state_marker(state_root / "research-runs" / f"{identity}.ok.json", completed)
        print(json.dumps(completed, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ResearchAgentError) as exc:
        print(json.dumps({"status": "error", "report_id": identity, "reason": str(exc), "retry": True}, ensure_ascii=False, sort_keys=True))
        return 2
    finally:
        support.fcntl.flock(lock.fileno(), support.fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate one governed daily or weekend report entirely on the server."""

from __future__ import annotations

import argparse
import json
import os
import re
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
    # A daily report freezes a forward-looking morning forecast.  Retrying it
    # after the domestic close would leak the realised session into that
    # forecast while still labelling the result as a morning report.  The
    # 06:00--08:59 window gives the timer several retries before the open;
    # intraday and overnight monitoring continues through the separate market
    # collector and AI-brief timers.
    if 1 <= now.isoweekday() <= 5 and 360 <= minutes < 540:
        return "daily"
    if now.isoweekday() == 7 and minutes >= 21 * 60 + 15:
        return "weekend"
    return None


def report_id(report_date: str, kind: str) -> str:
    return f"{report_date}-weekend" if kind == "weekend" else report_date


def acceptance_report_date(live_data_root: Path, current_date: str) -> str:
    """Use the exchange trade date for drafts without advancing freshness time."""

    latest = datetime.fromisoformat(current_date).date()
    try:
        payload = json.loads(
            (live_data_root / "oil_futures.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return current_date
    for item in payload.get("contracts", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("product") or "").upper() not in {"P", "Y", "OI"}:
            continue
        try:
            rank = int(item.get("contract_rank"))
            trade_date = datetime.fromisoformat(
                str(item.get("trade_date") or "")
            ).date()
        except (TypeError, ValueError):
            continue
        if rank == 1 and trade_date > latest:
            latest = trade_date
    return latest.isoformat()


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
    source_store = state_root / "research-context" / "source_runs"
    if source_store.is_dir():
        shutil.copytree(
            source_store,
            runtime_root / "source_runs",
            dirs_exist_ok=True,
            copy_function=shutil.copy2,
        )


def persist_outputs(
    state_root: Path,
    runtime_root: Path,
    report_path: Path,
    run_root: Path,
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
    context_store = state_root / "research-context" / "source_runs" / run_root.name
    shutil.copytree(
        run_root,
        context_store,
        dirs_exist_ok=True,
        copy_function=shutil.copy2,
    )


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchAgentError(f"cannot read governed input: {path}") from exc


def load_report_contract(site_root: Path, kind: str) -> str:
    """Load the repository-owned contract instead of relying on a prompt copy."""
    contract_name = "daily_automation_prompt.md" if kind == "daily" else "weekly_automation_prompt.md"
    paths = (
        site_root / "references" / contract_name,
        site_root / "skills" / "report_writer_skill" / "SKILL.md",
        site_root / "skills" / "vinson-research-writing" / "SKILL.md",
        site_root / "skills" / "vinson-research-writing" / "checklist.md",
    )
    parts: list[str] = []
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ResearchAgentError(f"cannot load repository report contract: {path}") from exc
        if not content:
            raise ResearchAgentError(f"repository report contract is empty: {path}")
        parts.append(f"===== {path.relative_to(site_root)} =====\n{content}")
    return "\n\n".join(parts)


def build_prompt(
    *,
    report_date: str,
    kind: str,
    source_snapshot: dict[str, Any],
    feedback: dict[str, Any] | None,
    correction: str,
    contract_text: str,
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
    draft_target = "1200-1280" if kind == "daily" else "1600-1800"
    title = datetime.fromisoformat(report_date).strftime("%m月%d日") + (
        "晨报" if kind == "daily" else "周报"
    )
    disclosure_text = (
        json.dumps(feedback.get("required_report_disclosures", []), ensure_ascii=False)
        if feedback
        else "[]"
    )
    confidence_cap = (
        "★" * int(feedback.get("core_view_confidence_cap_stars", 5))
        + "☆" * (5 - int(feedback.get("core_view_confidence_cap_stars", 5)))
        if feedback
        else "★★★★★"
    )
    kind_requirements = (
        """
日报研究要求：
- 两个主驱动至少一个必须来自基本面事实（供给、需求、库存、出口、产量、基差或价差）；技术面只能说明触发与确认，不能替代基本面解释。
- 必须读取 news_and_research_evidence.today_new_drivers；至少使用一条与油脂直接相关的 Level 1 快讯或研报作为交叉验证，并写清事件时间、来源、市场已经交易了什么、尚未定价什么。资讯约占30%，你的机制、品种传导、预期差和反证分析约占70%。
- “信息来源与核验说明”必须逐项列出 news_and_research_evidence.source_status 中的来源名称与真实状态；失败、不可用或降级不得省略。
- “今日观点”不能只有口号；Headline 后至少用一段解释为什么、P/Y/OI如何分化、什么证据会改变判断。两个主驱动合计不得少于350个中文可见字符。
- “缺少数据”“暂无新增驱动”“来源失败”是证据边界，不是基本面驱动；不得用数据缺口支撑方向判断。
- `## 【今日交易信号】`必须使用 Markdown 表格并分别列出 P、Y、OI 三行，逐品种完整写方向、触发、确认、止损、目标、仓位上限与信号有效期。
- `## 【关键数据与价格】`必须使用 Markdown 表格，列名至少包含指标、数值、时点、含义；必须包含 P/Y/OI、关键外盘或原油、至少一个价差，以及提纲中的 P 止损或目标关键位。
- `## 【开盘推演】`必须使用 Markdown 表格，三行分别为高开、平开、低开，列名至少包含情景、触发、确认、动作、放弃条件；每行都要写明 Y/OI 同步或背离时对 P 的处理。
- score、driver/fundamental/technical 分数、数据条数、采集状态均是内部元数据，不得写成市场驱动或正文结论。
- `source_error`、抓取失败、官方检查失败只允许出现在“信息来源与核验说明”，不得进入观点、驱动、策略或优先级判断。
- 日报初稿按仓库中已通过门禁的紧凑版式分配篇幅：今日观点约30-50字，今日交易信号不超过190字，核心驱动与预期差350-380字，关键数据与价格约300字，开盘推演不超过140字，风险提示不超过50字，信息来源与核验说明约270字。表格分隔线不计入这些栏目预算。
- 交易表中相同确认/失效条件不得逐行长篇复述；每行仍须完整，但应使用 SOURCE_JSON 已有的最短完整短语。关键数据表只保留满足合同所需的6-8行，不得在表后复述。
- 信息来源与核验说明使用单段紧凑审计句：五个审计字段、来源状态及 REQUIRED_DISCLOSURES 各出现一次；不得解释 skill 名称，不得复述正文观点。
"""
        if kind == "daily"
        else """
周报研究要求：
- 必须读取 research_history.previous_report，先复述上一期日期及核心判断，再用本期事实说明“兑现/部分兑现/未兑现”；若历史为空，明确写“本周起建立连续验证基线”，不得假造上期观点。
- 必须读取 news_and_research_evidence.today_new_drivers 与 continuing_background，区分本周新增信息和延续背景；至少引用一条可核验研报或事件，并把资讯事实与自己的传导、预期差及反证分析分开。
- “信息来源与核验说明”必须逐项列出 news_and_research_evidence.source_status 中的来源名称与真实状态；失败、不可用或降级不得省略。
- 核心数据变化必须优先使用 research_history.market_comparison 与 official_supply_demand.latest_metrics；不得把单日涨跌冒充周度变化，也不得从 score 推导变化。
- `## 【核心数据变化】`、`## 【下周主线与事件】`、`## 【交易计划】`必须使用 Markdown 表格。核心数据表列名至少包含指标、数值、统计时间、变化、含义，并含 P/Y/OI、豆棕价差、菜豆油价差。事件表列名至少包含日期、事件、重要性、触发条件，并逐行覆盖周一至周五。交易计划必须分别列出 P、Y、OI 三行，并完整写方向、触发、确认、止损、目标、仓位上限和信号有效期。
- `## 【周一开盘推演】`必须使用 Markdown 表格，四行分别为高开高走、高开震荡、高开回落、低开，列名至少包含情景、概率、触发、确认、动作、放弃条件；概率只能复制 SOURCE_JSON 中既有模型/规则。
- 正文必须同时解释豆棕价差与菜豆油价差各自说明什么；两个主驱动至少一个必须来自供给、需求、库存、出口、产量、基差或价差等基本面事实。
- score、driver/fundamental/technical 分数、数据条数、采集状态均是内部元数据，不得写成市场驱动或正文结论。
- `source_error`、抓取失败、官方检查失败只允许出现在“信息来源与核验说明”，不得进入观点、驱动、交易计划或下周主线。
"""
    )
    correction_block = f"\n上次门禁反馈，必须逐项修正：\n{correction}\n" if correction else ""
    return f"""
你是部署在腾讯云、只使用给定证据的油脂研究报告写作器。不要联网，不要调用工具，不要读取其他文件。

只输出符合 JSON Schema 的 JSON 对象。report_markdown 是完整 Markdown，outline 是内部审计提纲，fixed_logic 必须原样为 {json.dumps(FIXED_LOGIC, ensure_ascii=False)}。

硬性边界：
1. 报告日期为 {report_date}，类型为 {kind}，一级标题必须精确为“# {title}”。
2. 正文栏目按此顺序且标题格式为 `## 【栏目】`：{json.dumps(sections, ensure_ascii=False)}。
3. 正文可见字符预算 {budget}；消息链接与固定免责声明不计入预算。
3a. 模型初稿必须控制在 {draft_target} 个可见字符，为服务器按同一提纲补齐审计句预留空间；表格单元格使用最短且完整的短语，表格后不得复述同一事实。超出目标时必须删去重复修饰和重复解释，不能删去必需栏目、证据、P/Y/OI 行或执行字段。
3b. `## 【今日观点】`（周报为 `## 【一句话核心观点】`）标题后的第一句是页面 Headline：日报去除空白后不得超过 50 个字符，周报不得超过 100 个字符；只写一句明确观点，不得使用价格、数字或交易执行词。该句必须短于其后的解释段落。
4. 只能复制 SOURCE_JSON 中的数字、价格、涨跌、时间、合约、score 与 strategy_recommendation；禁止自行计算或创造任何价格、概率、止损、目标、仓位与来源。
4a. 数据栏目除 P/Y/OI 三个 rank=1 合约外，必须再列出至少三项 SOURCE_JSON 中有精确数字的辅助证据（优先官方供需、FCPO、CBOT、WTI、库存或价差）；每项均写名称、精确数字与该字段的时点。若源中没有三项，停止输出而不要编造。
4b. institutional_evidence 中的华泰天玑快讯、研报和智能K线可用于交叉验证与风险提示，但属于机构资讯与研究判断，不得冒充官方统计，不得覆盖交易所行情或官方供需数据；权限受限模块只能在“信息来源与核验说明”中披露。
5. P/Y/OI 三个 rank=1 合约及其 exact price 必须在关键数据中各出现一次；每个数字同时写明 SOURCE_JSON 中的时点口径。
6. 今日/下周交易计划必须来自 strategy_recommendation。若源中没有止损、目标或仓位，明确写“源数据未给出，不新开仓”，不得补造数字。
7. 只选两个 Level 1 驱动，写清事实→机制→P/Y/OI影响→预期与现实→结论；最强反证和可检验失效条件必须明确。
8. 日报的 `今日策略：偏多/偏空/震荡/观望` 必须与 outline.market_stance 完全一致；周报也必须在正文落实该基准方向。
9. outline 的 trade_trigger、confirmation_condition、stop_loss、target_range、position_limit、signal_expiry 必须逐字出现在正文。
10. 日报在“信息来源与核验说明”中逐字包含 REQUIRED_DISCLOSURES 的每一句；反馈只能降低置信度或增加反证，不能提高置信度。
10a. 日报“今日观点”第一段必须包含可机器读取的 `置信度：{confidence_cap}`，outline.research_confidence 也必须精确为 `{confidence_cap}`。
11. 不得在“信息来源与核验说明”之前使用“需进一步核验”；所有证据缺口只能集中在该栏目、最多写一次。禁止把未核验信息升级为主驱动。场外结构类型库和量化模型规则不可更改。
12. `## 【AI观点风险提示】`必须逐字写：本报告由AI基于公开信息、已调用数据源和既定研究框架生成，仅代表生成时点的研究判断，不构成投资建议或交易指令。期货价格波动较大，客户应结合自身风险承受能力独立决策。
13. `## 【信息来源与核验说明】`必须明确列出“实际 skill”“数据源”“截止时间”“失败项”“替代来源”五个审计字段；无失败或无替代时也要明确写“无”，不能省略字段。

{kind_requirements}

以下是当前 GitHub 仓库随代码发布的原始日报/周报合同与写作清单，全部属于硬约束；不得用上方摘要替代。若任何摘要与原始合同表述不一致，以原始合同中更严格的要求为准：

{contract_text}

REQUIRED_DISCLOSURES：
{disclosure_text}

SOURCE_JSON：
{json.dumps(source_snapshot, ensure_ascii=False, sort_keys=True)}
{correction_block}

若存在上次门禁反馈，必须把被拒稿当作编辑底稿，逐段重写整份 report_markdown，而不是在旧稿后追加修补；若反馈含正文篇幅超限，至少删去被拒稿约一半的重复字句，优先压缩表格单元格、来源状态和重复解释，初稿仍须落在 {draft_target} 个可见字符内。不得用遗漏必需字段来换取篇幅。
""".strip()


def build_compaction_prompt(
    report_date: str,
    kind: str,
    rejected_markdown: str,
    outline: dict[str, Any],
    feedback: dict[str, Any] | None,
    gate_feedback: str,
) -> str:
    """Build a small editing prompt when a complete draft only needs compression."""
    disclosure_text = json.dumps(
        (feedback or {}).get("required_report_disclosures", []),
        ensure_ascii=False,
    )
    return f"""
你是油脂研究日报的资深压缩编辑。只输出符合 JSON Schema 的 JSON 对象。
report_markdown 是压缩后的完整 Markdown；outline 必须逐字段保持为 OUTLINE_JSON；fixed_logic 必须原样为 {json.dumps(FIXED_LOGIC, ensure_ascii=False)}。

编辑边界：
1. 报告日期仍为 {report_date}，类型仍为 {kind}。不得新增或更改任何数字、日期、时间、合约、方向、来源状态、策略参数或事实；只能删除重复内容、合并同义句并缩短已有短语。
2. 正文可见字符必须为 1050-1320，为服务器的确定性审计补句预留空间。栏目顺序和标题保持不变；消息来源链接与固定 AI 免责声明不计入预算。
3. 今日观点30-50字；今日交易信号不超过190字；核心驱动与预期差350-380字；关键数据与价格不超过290字；开盘推演不超过130字；风险提示不超过45字；信息来源与核验说明不超过270字。
4. 完整保留八列 P/Y/OI 交易表、四列关键数据表、五列高开/平开/低开推演表。相同确认或失效条件用已有最短短语，不逐行长篇复述；各单元格仍不得为空。
5. 核心驱动仍须明确“主驱动一/主驱动二”，合计不少于350字，并保留事实→机制→P/Y/OI→预期与现实/定价→结论、最强反证和可检验失效条件。
6. 关键数据保留 P/Y/OI、一个外盘、一个价差、一个 P 关键位，并确保至少三项可复核辅助数字；只保留满足合同所需的6-8行。
7. 信息来源与核验说明必须保留“实际 skill、数据源、截止时间、失败项、替代来源”五字段和每个来源的真实状态。相同状态可合并为“甲、乙均ready”，但不得遗漏失败/不可用/降级来源。
8. REQUIRED_DISCLOSURES 中每句必须逐字保留。Headline、置信度和固定 AI 风险提示必须保留。不得用省略号、“同上”或空单元格压缩。

REQUIRED_DISCLOSURES：
{disclosure_text}

OUTLINE_JSON：
{json.dumps(outline, ensure_ascii=False, sort_keys=True)}

门禁反馈：
{gate_feedback[-4000:]}

被拒稿：
{rejected_markdown}
""".strip()


def normalize_visible_headline(markdown: str, kind: str) -> str:
    """Put the visible headline on its own bounded line without dropping prose."""
    section = "今日观点" if kind == "daily" else "一句话核心观点"
    limit = 50 if kind == "daily" else 100
    lines = markdown.splitlines()
    heading_index = next(
        (index for index, line in enumerate(lines) if line.strip() == f"## 【{section}】"),
        None,
    )
    if heading_index is None:
        return markdown
    headline_index = next(
        (index for index in range(heading_index + 1, len(lines)) if lines[index].strip()),
        None,
    )
    if headline_index is None or lines[headline_index].lstrip().startswith("## 【"):
        return markdown
    original = lines[headline_index].strip()
    sentence_match = re.match(r".*?[。！？]", original)
    if (
        len(re.sub(r"\s+", "", original)) <= limit
        and (sentence_match is None or sentence_match.end() == len(original))
    ):
        return markdown

    headline = sentence_match.group(0).strip() if sentence_match else ""
    remainder = original[len(headline) :].strip() if headline else original
    if not headline or len(re.sub(r"\s+", "", headline)) > limit:
        visible = 0
        split_at = 0
        for split_at, character in enumerate(original, start=1):
            if not character.isspace():
                visible += 1
            if visible >= limit:
                break
        headline = original[:split_at].strip()
        remainder = original[split_at:].strip()

    replacement = [headline]
    if remainder:
        replacement.extend(["", remainder])
    lines[headline_index : headline_index + 1] = replacement
    suffix = "\n" if markdown.endswith("\n") else ""
    return "\n".join(lines) + suffix


def enforce_confidence_cap(markdown: str, outline: dict[str, Any], feedback: dict[str, Any] | None, kind: str) -> tuple[str, dict[str, Any]]:
    """Make a pre-existing calibration cap visible without altering the model's view."""
    if kind != "daily" or not feedback:
        return markdown, outline
    stars = int(feedback.get("core_view_confidence_cap_stars", 5))
    stars = min(5, max(0, stars))
    rating = "★" * stars + "☆" * (5 - stars)
    outline = {**outline, "research_confidence": rating}
    section_pattern = re.compile(r"(## 【今日观点】\s*\n)(.*?)(?=\n## 【|\Z)", re.DOTALL)
    match = section_pattern.search(markdown)
    if match is None or re.search(r"置信度[：:]\s*[★☆]{5}", match.group(2)):
        return markdown, outline
    body = match.group(2).rstrip()
    updated = f"{match.group(1)}{body}\n\n置信度：{rating}。"
    return markdown[: match.start()] + updated + markdown[match.end() :], outline


def ensure_visible_confidence(
    markdown: str,
    outline: dict[str, Any],
    kind: str,
) -> str:
    """Make the audited outline rating visible even if the model omits it."""
    if kind != "daily":
        return markdown
    rating = str(outline.get("research_confidence") or "")
    if re.fullmatch(r"[★☆]{5}", rating) is None:
        return markdown
    section_pattern = re.compile(
        r"(## 【今日观点】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = section_pattern.search(markdown)
    if match is None:
        return markdown
    body = re.sub(r"\n*置信度[：:]\s*[★☆]{5}[。.]?", "", match.group(2)).strip()
    lines = body.splitlines()
    if not lines:
        return markdown
    body = "\n".join([lines[0], "", f"置信度：{rating}。", *lines[1:]]).strip()
    updated = f"{match.group(1)}{body}\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def ensure_daily_audit_contracts(
    markdown: str,
    outline: dict[str, Any],
    kind: str,
) -> str:
    """Expose audited outline fields without inventing values or conclusions."""
    if kind != "daily":
        return markdown
    stance = str(outline.get("market_stance") or "")
    top_call = str(outline.get("top_call") or "").strip().rstrip("。")
    transmission = str(outline.get("transmission_chain") or "").strip().rstrip("。")
    counter_case = str(outline.get("strongest_counter_case") or "").strip().rstrip("。")
    invalidation = str(outline.get("invalidation_condition") or "").strip().rstrip("。")

    view_pattern = re.compile(
        r"(## 【今日观点】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    view_match = view_pattern.search(markdown)
    if view_match and stance in {"偏多", "偏空", "震荡", "观望"}:
        body = view_match.group(2).strip()
        missing_parts: list[str] = []
        if stance not in body:
            missing_parts.append(f"基准方向：{stance}")
        if not any(marker in body for marker in ("策略", "执行", "观望", "空仓", "交易", "不追")):
            missing_parts.append("行动：按交易信号表执行")
        if invalidation and not any(marker in body for marker in ("失效", "推翻", "放弃", "反证")):
            missing_parts.append(f"失效：{invalidation}")
        if missing_parts:
            lines = body.splitlines()
            audit_line = "；".join(missing_parts) + "。"
            body = "\n".join([lines[0], "", audit_line, *lines[1:]]).strip()
            updated = f"{view_match.group(1)}{body}\n"
            markdown = markdown[: view_match.start()] + updated + markdown[view_match.end() :]

    driver_pattern = re.compile(
        r"(## 【核心驱动与预期差】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    driver_match = driver_pattern.search(markdown)
    if driver_match:
        body = driver_match.group(2).strip()
        audit_lines: list[str] = []
        if transmission and not any(marker in body for marker in ("→", "传导", "因此", "使得")):
            audit_lines.append(f"传导链：{transmission}。")
        risk_match_for_counter = re.search(
            r"## 【风险提示】\s*\n(.*?)(?=\n## 【|\Z)",
            markdown,
            re.DOTALL,
        )
        counter_scope = body + (risk_match_for_counter.group(1) if risk_match_for_counter else "")
        counter_terms = [
            term.strip()
            for term in re.split(r"并|且|、|，|；|。", counter_case)
            if len(term.strip()) >= 4
        ]
        counter_is_grounded = bool(counter_case) and (
            counter_case in counter_scope
            or (counter_terms and all(term in counter_scope for term in counter_terms))
        )
        if counter_case and not counter_is_grounded:
            audit_lines.append(f"最强反证：{counter_case}。")
        if audit_lines:
            body = f"{body}\n\n{' '.join(audit_lines)}"
            updated = f"{driver_match.group(1)}{body}\n"
            markdown = markdown[: driver_match.start()] + updated + markdown[driver_match.end() :]

    signal_pattern = re.compile(
        r"(## 【今日交易信号】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    signal_match = signal_pattern.search(markdown)
    if signal_match and stance in {"偏多", "偏空", "震荡", "观望"}:
        body = signal_match.group(2).strip()
        body = re.sub(r"^今日策略[：:].*?\n+", "", body)
        updated = f"{signal_match.group(1)}今日策略：{stance}。\n\n{body}\n"
        markdown = markdown[: signal_match.start()] + updated + markdown[signal_match.end() :]

    risk_pattern = re.compile(
        r"(## 【风险提示】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    risk_match = risk_pattern.search(markdown)
    if risk_match and invalidation:
        body = risk_match.group(2).strip()
        if not any(marker in body for marker in ("失效", "若", "一旦", "推翻")):
            body = f"{body}\n\n可检验失效条件：{invalidation}。"
        updated = f"{risk_match.group(1)}{body}\n"
        markdown = markdown[: risk_match.start()] + updated + markdown[risk_match.end() :]
    return markdown


def ensure_daily_external_key_data(
    markdown: str,
    source_snapshot: dict[str, Any],
    kind: str,
) -> str:
    """Copy one verified external quote into the key-data table when omitted."""
    if kind != "daily":
        return markdown
    pattern = re.compile(
        r"(## 【关键数据与价格】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    external_markers = ("FCPO", "BMD", "CBOT", "WTI", "原油", "美豆", "CPOTR", "ICDX", "印尼CPO")
    if any(marker in body for marker in external_markers):
        return markdown

    external = source_snapshot.get("external")
    if not isinstance(external, dict):
        return markdown
    candidates = (
        ("bmd_palm_oil", "FCPO"),
        ("cbot_bean_oil", "CBOT豆油"),
        ("cbot_soybean", "CBOT大豆"),
        ("crude_oil", "WTI原油"),
        ("indonesia_cpo_spot", "ICDX CPOTR"),
    )
    selected: tuple[str, str, str] | None = None
    for key, fallback_name in candidates:
        record = external.get(key)
        if not isinstance(record, dict) or record.get("status") != "ok":
            continue
        value = record.get("price")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        as_of = str(
            record.get("fetched_at")
            or record.get("published_at")
            or source_snapshot.get("timestamp")
            or ""
        ).strip()
        if not as_of:
            continue
        name = str(record.get("name") or fallback_name).strip()
        if not any(marker in name for marker in external_markers):
            name = fallback_name
        number = str(int(value)) if float(value).is_integer() else format(float(value), ".15g")
        selected = (name, number, as_of)
        break
    if selected is None:
        return markdown

    lines = body.splitlines()
    aliases = {
        "item": ("品种", "指标", "合约"),
        "value": ("数值", "价格", "关键位"),
        "time": ("时点", "时间", "日期", "口径"),
        "meaning": ("含义", "意义", "判断"),
    }
    for index in range(len(lines) - 1):
        header = lines[index].strip()
        separator = lines[index + 1].strip()
        if not (
            header.startswith("|")
            and header.endswith("|")
            and re.fullmatch(r"\|[\s:|-]+\|", separator)
        ):
            continue
        headers = [cell.strip() for cell in header.strip("|").split("|")]
        columns: dict[str, int] = {}
        for field, names in aliases.items():
            found = next(
                (position for position, value in enumerate(headers) if any(name in value for name in names)),
                None,
            )
            if found is None:
                break
            columns[field] = found
        if len(columns) != len(aliases):
            continue
        end = index + 2
        while end < len(lines) and lines[end].strip().startswith("|") and lines[end].strip().endswith("|"):
            end += 1
        row = [""] * len(headers)
        name, value, as_of = selected
        row[columns["item"]] = name.replace("|", "/")
        row[columns["value"]] = value
        row[columns["time"]] = as_of.replace("|", "/")
        row[columns["meaning"]] = "外盘交叉验证，不替代国内行情"
        lines.insert(end, "|" + "|".join(row) + "|")
        updated_body = "\n".join(lines)
        updated = f"{match.group(1)}{updated_body}\n"
        return markdown[: match.start()] + updated + markdown[match.end() :]
    return markdown


def ensure_daily_official_key_data(
    markdown: str,
    source_snapshot: dict[str, Any],
    kind: str,
) -> str:
    """Copy one exact official metric into the daily table for the third audit fact."""
    if kind != "daily":
        return markdown
    pattern = re.compile(
        r"(## 【关键数据与价格】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    if any(marker in body for marker in ("MPOB产量", "MPOB出口", "MPOB期末库存")):
        return markdown
    fundamental = source_snapshot.get("fundamental")
    official = fundamental.get("official_supply_demand") if isinstance(fundamental, dict) else None
    metrics = official.get("latest_metrics") if isinstance(official, dict) else None
    if not isinstance(metrics, dict):
        return markdown
    choices = (
        ("stocks", "MPOB期末库存"),
        ("exports", "MPOB出口"),
        ("production", "MPOB产量"),
    )
    selected: tuple[str, str, str] | None = None
    for key, name in choices:
        record = metrics.get(key)
        if not isinstance(record, dict):
            continue
        value = record.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        period = str(record.get("period") or "").strip()
        published = str(record.get("published_at") or "").strip()
        if not period and not published:
            continue
        number = str(int(value)) if float(value).is_integer() else format(float(value), ".15g")
        unit = "吨" if str(record.get("unit") or "") == "tonnes" else str(record.get("unit") or "")
        as_of = "，".join(part for part in (period, f"{published}发布" if published else "") if part)
        selected = (name, f"{number}{unit}", as_of)
        break
    if selected is None:
        return markdown

    lines = body.splitlines()
    for index in range(len(lines) - 1):
        header = lines[index].strip()
        separator = lines[index + 1].strip()
        if not (
            header.startswith("|")
            and header.endswith("|")
            and re.fullmatch(r"\|[\s:|-]+\|", separator)
        ):
            continue
        headers = [cell.strip() for cell in header.strip("|").split("|")]
        aliases = {
            "item": ("品种", "指标", "合约"),
            "value": ("数值", "价格", "关键位"),
            "time": ("时点", "时间", "日期", "口径"),
            "meaning": ("含义", "意义", "判断"),
        }
        columns: dict[str, int] = {}
        for field, names in aliases.items():
            found = next(
                (position for position, value in enumerate(headers) if any(name in value for name in names)),
                None,
            )
            if found is None:
                break
            columns[field] = found
        if len(columns) != len(aliases):
            continue
        end = index + 2
        while end < len(lines) and lines[end].strip().startswith("|") and lines[end].strip().endswith("|"):
            end += 1
        data_indexes = list(range(index + 2, end))
        while len(data_indexes) >= 7:
            external_markers = (
                "FCPO", "BMD", "CBOT", "WTI", "原油", "美豆", "CPOTR", "ICDX", "印尼CPO"
            )
            removed = False
            for row_index in data_indexes:
                cells = [cell.strip() for cell in lines[row_index].strip("|").split("|")]
                item = cells[columns["item"]] if len(cells) == len(headers) else ""
                protected = (
                    re.fullmatch(r"(?:P|Y|OI)(?:\d{4})?", item, re.I) is not None
                    or any(marker in item for marker in external_markers)
                    or any(marker in item for marker in ("价差", "基差", "观察位", "止损", "目标", "关键位"))
                )
                if not protected:
                    lines.pop(row_index)
                    end -= 1
                    removed = True
                    break
            if not removed:
                break
            data_indexes = list(range(index + 2, end))
        row = [""] * len(headers)
        name, value, as_of = selected
        row[columns["item"]] = name
        row[columns["value"]] = value
        row[columns["time"]] = as_of
        row[columns["meaning"]] = "官方供需背景"
        lines.insert(end, "|" + "|".join(row) + "|")
        updated_body = "\n".join(lines)
        updated = f"{match.group(1)}{updated_body}\n"
        return markdown[: match.start()] + updated + markdown[match.end() :]
    return markdown


def compact_daily_execution_table(markdown: str, kind: str) -> str:
    """Shorten execution cells while preserving every audited price and decision."""
    if kind != "daily":
        return markdown
    pattern = re.compile(
        r"(## 【今日交易信号】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    lines = match.group(2).strip().splitlines()
    header_index = next(
        (
            index
            for index in range(len(lines) - 1)
            if lines[index].strip().startswith("|")
            and re.fullmatch(r"\|[\s:|-]+\|", lines[index + 1].strip())
        ),
        None,
    )
    if header_index is None:
        return markdown
    headers = [cell.strip() for cell in lines[header_index].strip("|").split("|")]
    aliases = {
        "品种": ("品种", "合约"),
        "方向": ("方向",),
        "触发": ("触发",),
        "确认": ("确认",),
        "止损": ("止损", "失效"),
        "目标": ("目标",),
        "仓位上限": ("仓位上限", "仓位", "行动"),
        "信号有效期": ("信号有效期", "有效期", "到期"),
    }
    indexes = {
        name: next(
            (index for index, value in enumerate(headers) if any(alias in value for alias in names)),
            None,
        )
        for name, names in aliases.items()
    }
    if any(value is None for value in indexes.values()):
        return markdown
    assert all(value is not None for value in indexes.values())

    lines[header_index] = lines[header_index].replace("仓位上限", "仓位").replace("信号有效期", "有效期")

    def first_number(value: str) -> str:
        found = re.search(r"[-+]?\d+(?:\.\d+)?", value)
        return found.group(0) if found else ""

    row_index = header_index + 2
    while row_index < len(lines) and lines[row_index].strip().startswith("|"):
        cells = [cell.strip() for cell in lines[row_index].strip("|").split("|")]
        if len(cells) != len(headers):
            row_index += 1
            continue
        item = cells[indexes["品种"]]  # type: ignore[index]
        if re.fullmatch(r"(?:P|Y|OI)(?:\d{4})?", item, re.I):
            trigger = cells[indexes["触发"]]  # type: ignore[index]
            trigger_price = first_number(trigger)
            if trigger_price:
                suffix = "，待确认" if item.upper().startswith("P") else ""
                cells[indexes["触发"]] = f"{trigger_price}{suffix}"  # type: ignore[index]
            confirmation = cells[indexes["确认"]]  # type: ignore[index]
            if item.upper().startswith("P") and "驱动/资金同向" in confirmation:
                cells[indexes["确认"]] = "同向则失效"  # type: ignore[index]
            elif "驱动/资金同向" in confirmation:
                cells[indexes["确认"]] = "同向"  # type: ignore[index]
            elif "Y/OI同步" in confirmation:
                cells[indexes["确认"]] = "同步"  # type: ignore[index]
            stop = cells[indexes["止损"]]  # type: ignore[index]
            stop_price = first_number(stop)
            if stop_price:
                cells[indexes["止损"]] = stop_price  # type: ignore[index]
            target = cells[indexes["目标"]]  # type: ignore[index]
            target_prices = re.findall(r"[-+]?\d+(?:\.\d+)?", target)
            if len(target_prices) >= 2:
                cells[indexes["目标"]] = f"{target_prices[0]}/{target_prices[1]}"  # type: ignore[index]
            elif target_prices:
                cells[indexes["目标"]] = target_prices[0]  # type: ignore[index]
            for field in ("仓位上限", "信号有效期"):
                if "不新开仓" in cells[indexes[field]]:  # type: ignore[index]
                    cells[indexes[field]] = "不开仓" if field == "仓位上限" else "未给出"  # type: ignore[index]
            lines[row_index] = "|" + "|".join(cells) + "|"
        row_index += 1
    strategy = re.search(r"今日策略[：:]\s*(偏多|偏空|震荡|观望)", match.group(2))
    if strategy:
        lines = [f"今日策略：{strategy.group(1)}。", "", *lines[header_index:]]
    updated_body = "\n".join(lines)
    updated = f"{match.group(1)}{updated_body}\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def compact_daily_scenario_table(markdown: str, kind: str) -> str:
    """Compress scenario table wording without changing its decision branches."""
    if kind != "daily":
        return markdown
    pattern = re.compile(r"(## 【开盘推演】\s*\n)(.*?)(?=\n## 【|\Z)", re.DOTALL)
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    body = re.sub(r"Y/OI同步(?:走强|转强|转弱)?", "Y/OI同步", body)
    body = re.sub(r"(?:Y/OI)?背离(?:扩大)?(?:时|则)?(?:继续)?(?:不追|不新开仓|放弃P处理)", "背离则放弃", body)
    body = re.sub(r"(?:区间内)?等待(?:驱动与资金)?确认", "等待确认", body)
    body = re.sub(r"维持震荡观察", "震荡观察", body)
    body = body.replace("放弃条件", "放弃")
    body = body.replace("P等待确认", "P等确认").replace("等待区间确认", "P等确认")
    body = body.replace("震荡观察", "P观望")
    body = body.replace("Y/OI背离则放弃判断", "背离").replace("背离则放弃", "背离")
    lines = body.splitlines()
    header_index = next(
        (
            index
            for index in range(len(lines) - 1)
            if lines[index].strip().startswith("|")
            and re.fullmatch(r"\|[\s:|-]+\|", lines[index + 1].strip())
        ),
        None,
    )
    if header_index is not None:
        headers = [cell.strip() for cell in lines[header_index].strip("|").split("|")]
        aliases = {
            "情景": ("情景",),
            "触发": ("触发",),
            "确认": ("确认",),
            "动作": ("动作", "应对"),
            "放弃": ("放弃", "失效"),
        }
        indexes = {
            name: next(
                (i for i, value in enumerate(headers) if any(alias in value for alias in names)),
                None,
            )
            for name, names in aliases.items()
        }
        if all(index is not None for index in indexes.values()):
            lines[header_index] = lines[header_index].replace("放弃条件", "放弃")
            row_index = header_index + 2
            while row_index < len(lines) and lines[row_index].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[row_index].strip("|").split("|")]
                if len(cells) != len(headers):
                    row_index += 1
                    continue
                scenario = cells[indexes["情景"]]  # type: ignore[index]
                if scenario in {"高开", "平开", "低开"}:
                    cells[indexes["触发"]] = f"P{scenario}"  # type: ignore[index]
                    cells[indexes["确认"]] = "Y/OI同步"  # type: ignore[index]
                    cells[indexes["动作"]] = {  # type: ignore[index]
                        "高开": "P等确认",
                        "平开": "P观望",
                        "低开": "P不开仓",
                    }[scenario]
                    cells[indexes["放弃"]] = "背离"  # type: ignore[index]
                    lines[row_index] = "|" + "|".join(cells) + "|"
                row_index += 1
            body = "\n".join(lines)
    updated = f"{match.group(1)}{body}\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def compact_daily_key_data_table(markdown: str, kind: str) -> str:
    """Remove explanatory filler from already self-describing key-data rows."""
    if kind != "daily":
        return markdown
    pattern = re.compile(
        r"(## 【关键数据与价格】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    replacements = {
        "P主叙事": "P",
        "豆系共振": "Y",
        "轮动观察": "OI",
        "产地参照": "产地",
        "相对强弱": "价差",
        "区间边界": "区间",
        "官方供需背景": "官方",
        "外盘交叉验证，不替代国内行情": "外盘验证",
    }
    for verbose, compact in replacements.items():
        body = body.replace(verbose, compact)
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|") or re.fullmatch(r"\|[\s:|-]+\|", line.strip()):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"指标", "品种", "合约"}:
            continue
        item = cells[0].upper()
        if re.fullmatch(r"P\d{4}", item):
            cells[3] = "P"
        elif re.fullmatch(r"Y\d{4}", item):
            cells[3] = "Y"
        elif re.fullmatch(r"OI\d{4}", item):
            cells[3] = "OI"
        elif "CPOTR" in item or "ICDX" in item:
            cells[3] = "外盘"
        elif "价差" in cells[0]:
            cells[3] = "价差"
        elif any(marker in cells[0] for marker in ("产量", "库存")):
            cells[3] = "供"
        elif "出口" in cells[0]:
            cells[3] = "需"
        lines[index] = "|" + "|".join(cells) + "|"
    body = "\n".join(lines)
    updated = f"{match.group(1)}{body}\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def compact_daily_risk(markdown: str, outline: dict[str, Any], kind: str) -> str:
    """Keep the risk section as one testable invalidation without duplicating drivers."""
    if kind != "daily":
        return markdown
    invalidation = str(outline.get("invalidation_condition") or "").strip().rstrip("。.")
    if not invalidation:
        return markdown
    pattern = re.compile(r"(## 【风险提示】\s*\n)(.*?)(?=\n## 【|\Z)", re.DOTALL)
    match = pattern.search(markdown)
    if not match:
        return markdown
    updated = f"{match.group(1)}{invalidation}。\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def compact_daily_top_call(markdown: str, outline: dict[str, Any], kind: str) -> str:
    """Keep a concise first-screen action while retaining stance and invalidation."""
    if kind != "daily":
        return markdown
    pattern = re.compile(r"(## 【今日观点】\s*\n)(.*?)(?=\n## 【|\Z)", re.DOTALL)
    match = pattern.search(markdown)
    if not match:
        return markdown
    lines = [line.strip() for line in match.group(2).splitlines() if line.strip()]
    if not lines:
        return markdown
    headline = lines[0]
    stance = str(outline.get("market_stance") or "")
    if stance and stance not in headline:
        headline = f"{headline.rstrip('。')}，{stance}。"
    invalidation = str(outline.get("invalidation_condition") or "").strip().rstrip("。.")
    invalidation = re.sub(r"^若(?:价格)?", "", invalidation)
    invalidation = re.sub(r"[，,]?(?:震荡)?判断失效$", "", invalidation)
    rating = str(outline.get("research_confidence") or "")
    audit = "行动：交易表"
    if invalidation:
        audit += f"；失效：{invalidation}"
    if re.fullmatch(r"[★☆]{5}", rating):
        audit += f"；置信度：{rating}"
    updated = f"{match.group(1)}{headline}\n\n{audit}。\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def compact_daily_driver_repetition(markdown: str, outline: dict[str, Any], kind: str) -> str:
    """Remove driver sentences already carried verbatim by the top call and risk section."""
    if kind != "daily":
        return markdown
    pattern = re.compile(
        r"(## 【核心驱动与预期差】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    invalidation = str(outline.get("invalidation_condition") or "").strip().rstrip("。.")
    if invalidation:
        body = re.sub(rf"(?:^|(?<=。)|(?<=；))\s*{re.escape(invalidation)}[。.]?", "", body)
    source_name = "机构资讯·油脂油料快讯"
    first = body.find(source_name)
    if first >= 0:
        body = body[: first + len(source_name)] + body[first + len(source_name) :].replace(source_name, "同源快讯")
    body = re.sub(r"结论为[^。]{2,20}。", "", body)
    updated = f"{match.group(1)}{body}\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def compact_daily_source_audit(
    markdown: str,
    source_snapshot: dict[str, Any],
    feedback: dict[str, Any] | None,
    kind: str,
) -> str:
    """Render the source audit once, grouping identical states without omission."""
    if kind != "daily":
        return markdown
    pattern = re.compile(
        r"(## 【信息来源与核验说明】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    disclosures = [
        value.strip()
        for value in (feedback or {}).get("required_report_disclosures", [])
        if isinstance(value, str) and value.strip()
    ]
    audit_body = body
    for disclosure in disclosures:
        audit_body = audit_body.replace(disclosure, "")

    def field(start: str, end: str | None) -> str:
        suffix = rf"(?=[。；]\s*{end}\s*[：:])" if end else r"(?=[。；]|\Z)"
        found = re.search(rf"{start}\s*[：:]\s*(.*?){suffix}", audit_body, re.DOTALL | re.I)
        return re.sub(r"\s+", "", found.group(1)).strip("。；") if found else ""

    skills = field(r"实际\s*skill(?:（短名）|\(短名\))?", "数据源")
    sources = field("数据源", "截止时间")
    cutoff = field("截止时间", "失败项")
    failures = field("失败项", "替代来源")
    replacements = field("替代来源", None)
    if not all((skills, sources, cutoff, failures, replacements)):
        return markdown
    skill_names = [part for part in re.split(r"[、,，/]", skills) if part]
    skill_short = {
        "market_data_skill": "mkt",
        "market": "mkt",
        "data_quality_gate_skill": "gate",
        "forecast_generation_feedback": "fb",
        "feedback": "fb",
        "oil_report_freshness": "fresh",
        "report_writer_skill": "writer",
        "headline_skill": "title",
        "headline": "title",
        "report_quality_gate": "audit",
        "report_gate": "audit",
        "forecast_tracking_skill": "track",
        "tracking": "track",
    }
    skills = "/".join(skill_short.get(name, name) for name in skill_names)
    source_short = {
        "ICDX官方历史价格接口": "ICDX",
        "机构资讯·油脂油料快讯": "机构油脂快讯",
        "MPOB官方检查": "MPOB",
    }
    sources = "、".join(
        source_short.get(name, name)
        for name in re.split(r"[、,，]", sources)
        if name
    )
    failures = failures.replace("官方检查source_error", "检查失败")
    failures = failures.replace("官方供需检查source_error", "供需检查失败")
    replacements = replacements.replace("官方历史价格接口", "历史接口")

    research = source_snapshot.get("news_and_research_evidence")
    statuses = research.get("source_status") if isinstance(research, dict) else None
    grouped: dict[str, list[str]] = {}
    if isinstance(statuses, list):
        for item in statuses:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            state = str(item.get("state") or "").strip()
            if name and state:
                grouped.setdefault(state, []).append(name)
    status_parts = [
        f"{'、'.join(names)}={state}"
        for state, names in grouped.items()
        if names
    ]
    needs_match = re.search(
        r"需进一步核验\s*[：:]\s*(.*?)(?=预测校准\s*[：:]|\Z)",
        audit_body,
        re.DOTALL,
    )
    needs = re.sub(r"\s+", "", needs_match.group(1)).strip("。；") if needs_match else ""
    parts = [
        f"实际 skill（短名）：{skills}",
        f"数据源：{sources}",
        f"截止时间：{cutoff}",
        f"失败项：{failures}",
        f"替代来源：{replacements}",
    ]
    if status_parts:
        parts.append(f"来源状态：{'；'.join(status_parts)}")
    if "机构" in body:
        parts.append("机构资讯仅作交叉验证")
    if needs:
        parts.append(f"需进一步核验：{needs}")
    compact = "。".join(parts) + "。"
    if disclosures:
        compact += "\n\n" + "\n".join(disclosures)
    updated = f"{match.group(1)}{compact}\n"
    return markdown[: match.start()] + updated + markdown[match.end() :]


def preserve_daily_driver_depth(
    markdown: str,
    previous_markdown: str,
    kind: str,
) -> str:
    """Restore the prior grounded driver section if an editor cuts it below 350."""
    if kind != "daily" or not previous_markdown:
        return markdown
    pattern = re.compile(
        r"(## 【核心驱动与预期差】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    current = pattern.search(markdown)
    previous = pattern.search(previous_markdown)
    if not current or not previous:
        return markdown
    current_chars = len(re.sub(r"\s+", "", current.group(2)))
    previous_chars = len(re.sub(r"\s+", "", previous.group(2)))
    if current_chars >= 350 or previous_chars < 350:
        return markdown
    restored = f"{current.group(1)}{previous.group(2).strip()}\n"
    return markdown[: current.start()] + restored + markdown[current.end() :]


def ensure_weekly_previous_validation(
    markdown: str,
    source_snapshot: dict[str, Any],
    kind: str,
) -> str:
    """Make the previous-week validation visible when source history exists."""
    if kind != "weekend":
        return markdown
    history = source_snapshot.get("research_history")
    previous = history.get("previous_report") if isinstance(history, dict) else None
    if not isinstance(previous, dict):
        return markdown
    previous_date = str(previous.get("date") or "").removesuffix("-weekend")
    previous_title = str(previous.get("title") or "").strip()
    previous_headline = str(previous.get("headline") or "").strip().rstrip("。")
    if not previous_date or not (previous_title or previous_headline):
        return markdown

    pattern = re.compile(
        r"(## 【本周验证与预期差】\s*\n)(.*?)(?=\n## 【|\Z)",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return markdown
    body = match.group(2).strip()
    has_previous_view = any(
        value and value in body for value in (previous_title, previous_headline)
    )
    if previous_date in body and has_previous_view:
        return markdown
    if has_previous_view:
        updated = f"{match.group(1)}上一期报告日期：{previous_date}。\n\n{body}\n"
        return markdown[: match.start()] + updated + markdown[match.end() :]
    # Never manufacture an outcome such as “部分兑现”.  Missing comparison
    # evidence must remain missing so the deterministic audit blocks/retries.
    return markdown


def normalize_report_punctuation(markdown: str) -> str:
    return markdown.replace("。；", "；").replace("。。", "。")


def run_openai(schema: Path, prompt: str, *, timeout: int) -> dict[str, Any]:
    try:
        output, _backend = MODEL_BACKEND.request_json(
            schema=load_json(schema),
            schema_name="server_research_report",
            prompt=prompt,
            timeout=timeout,
            verbosity="low",
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


def run_prewrite_data_gate(runtime_root: Path, run_root: Path, timeout: int) -> dict[str, Any]:
    """Execute the original data-quality stage before any report prose is written."""
    manifest_path = run_root / "manifest.json"
    command = [
        sys.executable,
        "skills/data_quality_gate_skill/scripts/validate_data.py",
        "--manifest",
        str(manifest_path),
        "--strict",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=runtime_root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ResearchAgentError(f"pre-write data quality gate did not complete: {exc}") from exc
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ResearchAgentError("pre-write data quality gate returned invalid JSON") from exc
    manifest = load_json(manifest_path)
    required_research = {
        item.get("name"): item.get("status")
        for item in manifest.get("results", [])
        if isinstance(item, dict)
        and item.get("name") in {"news_and_research_skill_sources", "oil_report_freshness"}
    }
    if completed.returncode != 0 or payload.get("can_publish") is not True:
        raise ResearchAgentError(f"pre-write data quality gate blocked publication: {payload}")
    if required_research != {
        "news_and_research_skill_sources": "ok",
        "oil_report_freshness": "ok",
    }:
        raise ResearchAgentError(
            "news/research or freshness skill stage has no publishable Level 1 evidence"
        )
    atomic_write_json(run_root / "data_quality.json", payload)
    return payload


def record_skill_stage(
    run_root: Path,
    stage: str,
    status: str,
    artifact: str,
) -> None:
    path = run_root / "skill_chain.json"
    payload: dict[str, Any] = {"schema_version": "report-skill-chain-v1", "stages": []}
    if path.is_file():
        loaded = load_json(path)
        if isinstance(loaded, dict):
            payload = loaded
    stages = payload.setdefault("stages", [])
    if not isinstance(stages, list):
        stages = []
        payload["stages"] = stages
    stages[:] = [item for item in stages if not isinstance(item, dict) or item.get("stage") != stage]
    stages.append(
        {
            "stage": stage,
            "status": status,
            "artifact": artifact,
            "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        }
    )
    atomic_write_json(path, payload)


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
    parser.add_argument(
        "--shadow-acceptance",
        action="store_true",
        help="Run the complete quality gate for the exchange trade date without publishing it.",
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
    site_root = args.site_root.resolve()
    runtime_root = args.runtime_root.resolve()
    live_data_root = args.live_data_root.resolve()
    state_root = args.state_root.resolve()
    report_date = now.date().isoformat()
    if args.acceptance_only or args.shadow_acceptance:
        report_date = acceptance_report_date(live_data_root, report_date)
    identity = report_id(report_date, kind)
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
            allow_date_override=args.acceptance_only or args.shadow_acceptance,
        )
        run_root = Path(built["run_root"])
        record_skill_stage(run_root, "market_data_skill", "ok", "manifest.json")
        run_prewrite_data_gate(runtime_root, run_root, min(args.timeout, 300))
        record_skill_stage(run_root, "data_quality_gate_skill", "ok", "data_quality.json")
        source_snapshot = load_json(Path(built["snapshot"]))
        contract_text = load_report_contract(site_root, kind)
        feedback = None
        if kind == "daily":
            feedback_builder = load_module(
                "server_generation_feedback_builder",
                runtime_root
                / "skills"
                / "forecast_tracking_skill"
                / "scripts"
                / "build_generation_feedback.py",
            )
            feedback_path = runtime_root / "data" / "forecast" / "feedback" / "latest.json"
            feedback = feedback_builder.build_feedback(
                runtime_root / "data" / "forecast" / "metrics" / "latest.json",
                runtime_root / "data" / "review" / "daily",
                report_date,
            )
            feedback_builder._write_atomically(feedback_path, feedback)
            feedback_value = load_json(runtime_root / "data" / "forecast" / "feedback" / "latest.json")
            if not isinstance(feedback_value, dict):
                raise ResearchAgentError("daily forecast feedback must be a JSON object")
            feedback = feedback_value
            record_skill_stage(
                run_root,
                "forecast_generation_feedback",
                "ok",
                "../../data/forecast/feedback/latest.json",
            )
        record_skill_stage(
            run_root,
            "oil_report_freshness",
            "ok",
            "raw/futures_market_data.json#news_and_research_evidence",
        )

        if args.acceptance_only:
            prompt = build_prompt(
                report_date=report_date,
                kind=kind,
                source_snapshot=source_snapshot,
                feedback=feedback,
                correction="",
                contract_text=contract_text,
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
        outline_path = run_root / "report_outline.json"
        quality_path = run_root / "report_quality.json"
        schema = site_root / "references" / "server_report_output.schema.json"
        environment = {
            **os.environ,
            "PALM_OIL_PUBLISH_MODE": "files",
            "PALM_OIL_REPORT_DATA_MODE": "prepared",
            "PALM_OIL_TARGET_REPORT": f"reports/{identity}.md",
            "PYTHONUNBUFFERED": "1",
        }
        correction = ""
        previous_markdown = ""
        previous_outline: dict[str, Any] = {}
        attempts = 1 if args.mock_response else args.attempts
        success = False
        last_gate = ""
        for attempt in range(1, attempts + 1):
            if previous_markdown and kind == "daily" and "正文篇幅" in correction:
                prompt = build_compaction_prompt(
                    report_date=report_date,
                    kind=kind,
                    rejected_markdown=previous_markdown,
                    outline=previous_outline,
                    feedback=feedback,
                    gate_feedback=correction,
                )
            else:
                prompt = build_prompt(
                    report_date=report_date,
                    kind=kind,
                    source_snapshot=source_snapshot,
                    feedback=feedback,
                    correction=correction,
                    contract_text=contract_text,
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
            markdown, outline = enforce_confidence_cap(markdown, outline, feedback, kind)
            markdown = ensure_visible_confidence(markdown, outline, kind)
            markdown = ensure_daily_audit_contracts(markdown, outline, kind)
            markdown = ensure_daily_external_key_data(markdown, source_snapshot, kind)
            markdown = ensure_daily_official_key_data(markdown, source_snapshot, kind)
            markdown = preserve_daily_driver_depth(markdown, previous_markdown, kind)
            markdown = compact_daily_driver_repetition(markdown, outline, kind)
            markdown = compact_daily_execution_table(markdown, kind)
            markdown = compact_daily_scenario_table(markdown, kind)
            markdown = compact_daily_key_data_table(markdown, kind)
            markdown = compact_daily_risk(markdown, outline, kind)
            markdown = compact_daily_top_call(markdown, outline, kind)
            markdown = compact_daily_source_audit(markdown, source_snapshot, feedback, kind)
            markdown = ensure_weekly_previous_validation(markdown, source_snapshot, kind)
            markdown = normalize_visible_headline(markdown, kind)
            markdown = normalize_report_punctuation(markdown)
            atomic_write_text(report_path, markdown)
            atomic_write_json(outline_path, outline)
            record_skill_stage(run_root, "report_writer_skill", "ok", report_path.name)
            success, last_gate = run_deploy(
                runtime_root,
                environment,
                log_path,
                timeout=max(args.timeout, 300),
            )
            if success:
                break
            quality = load_json(quality_path) if quality_path.exists() else {}
            previous_markdown = markdown
            previous_outline = outline
            correction = json.dumps(
                {
                    "gate_output": last_gate,
                    "report_quality": quality,
                    "previous_rejected_report": markdown,
                },
                ensure_ascii=False,
            )[-9000:]
        if not success:
            raise ResearchAgentError(f"report remained blocked after {attempts} attempt(s): {last_gate[-1200:]}")

        quality = load_json(quality_path)
        if not isinstance(quality, dict) or quality.get("can_publish") is not True:
            raise ResearchAgentError("report quality gate did not produce can_publish=true")
        record_skill_stage(run_root, "headline_skill", "ok", report_path.name)
        record_skill_stage(run_root, "report_quality_gate", "ok", "report_quality.json")
        if not report_is_ready(runtime_root / "data" / "reports.json", identity):
            raise ResearchAgentError("internal reports dataset does not contain the new report")
        if kind == "daily" and not (runtime_root / "data" / "forecast" / "daily" / f"{report_date}.json").is_file():
            raise ResearchAgentError("daily report did not freeze its prediction record")
        if args.shadow_acceptance:
            accepted = {
                "status": "ok",
                "acceptance": "real_model_report_quality_validated",
                "backend": backend,
                "report_date": report_date,
                "kind": kind,
                "quality_score": quality.get("score"),
                "can_publish": quality.get("can_publish"),
                "completed_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            }
            support.atomic_state_marker(
                state_root / "research-quality.accepted.json",
                accepted,
            )
            print(json.dumps(accepted, ensure_ascii=False, sort_keys=True))
            return 0
        if kind == "daily":
            record_skill_stage(
                run_root,
                "forecast_tracking_skill",
                "ok",
                f"../../data/forecast/daily/{report_date}.json",
            )
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
        persist_outputs(state_root, runtime_root, report_path, run_root)
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

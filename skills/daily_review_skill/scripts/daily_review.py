#!/usr/bin/env python3
"""Review yesterday's oil-futures tab analysis against today's actual market action."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from review_memory import DAILY_REVIEW_DIR, save_today_review


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = DAILY_REVIEW_DIR
TRACKED = {"P", "Y", "OI"}


def save_review(review: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    if output_dir.resolve() == DAILY_REVIEW_DIR.resolve():
        return save_today_review(review)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{review['date']}.json"
    target.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"saved": str(target), "retained_count": 1, "deleted": [], "warnings": []}


def as_float(value: Any) -> float | None:
    if value in (None, "", "-", "需进一步核验"):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    text = text.replace("%", "")
    multiplier = 1.0
    if "万" in text:
        multiplier = 10000.0
        text = text.replace("万手", "").replace("万", "")
    text = re.sub(r"[^0-9.+-]", "", text)
    if not text:
        return None
    try:
        return float(text) * multiplier
    except ValueError:
        return None


def load_js_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^\s*window\.[A-Z0-9_]+\s*=\s*", "", text).strip()
    if text.endswith(";"):
        text = text[:-1]
    return json.loads(text)


def contract_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the rank-1 contract for each tracked product."""
    contracts: dict[str, dict[str, Any]] = {}
    for item in payload.get("contracts", []):
        product = str(item.get("product") or "").upper()
        rank = item.get("contract_rank")
        try:
            rank = int(rank)
        except (TypeError, ValueError):
            continue
        if product in TRACKED and rank == 1:
            contracts[product] = item
    return contracts


def upper_lower(previous: dict[str, Any]) -> tuple[float | None, float | None]:
    strategy = previous.get("strategy_recommendation", {}) or {}
    upper = as_float(strategy.get("upper_watch"))
    lower = as_float(strategy.get("lower_watch"))
    if upper is None:
        upper = as_float(strategy.get("take_profit"))
    if lower is None:
        lower = as_float(strategy.get("stop_loss"))
    if upper is not None and lower is not None and upper < lower:
        upper, lower = lower, upper
    return upper, lower


def actual_market(previous: dict[str, Any], current: dict[str, Any], upper: float | None, lower: float | None) -> dict[str, Any]:
    open_price = as_float(current.get("open"))
    high = as_float(current.get("high"))
    low = as_float(current.get("low"))
    close = as_float(current.get("price"))
    change_pct = as_float(current.get("change"))
    prev_volume = as_float(previous.get("volume"))
    cur_volume = as_float(current.get("volume"))
    prev_oi = as_float(previous.get("open_interest"))
    cur_oi = as_float(current.get("open_interest"))
    volume_change = None if prev_volume in (None, 0) or cur_volume is None else (cur_volume - prev_volume) / prev_volume * 100
    open_interest_change = None if prev_oi in (None, 0) or cur_oi is None else (cur_oi - prev_oi) / prev_oi * 100
    intraday_direction = "up" if change_pct is not None and change_pct > 0 else "down" if change_pct is not None and change_pct < 0 else "flat"
    return {
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "change_pct": change_pct,
        "volume_change": volume_change,
        "open_interest_change": open_interest_change,
        "intraday_direction": intraday_direction,
        "whether_break_upper": bool(upper is not None and high is not None and high > upper),
        "whether_break_lower": bool(lower is not None and low is not None and low < lower),
        "whether_close_above_upper": bool(upper is not None and close is not None and close > upper),
        "whether_close_below_lower": bool(lower is not None and close is not None and close < lower),
    }


def classify(stance: str, actual: dict[str, Any]) -> str:
    direction = actual.get("intraday_direction")
    break_upper = actual.get("whether_break_upper")
    break_lower = actual.get("whether_break_lower")
    close_above_upper = actual.get("whether_close_above_upper")
    close_below_lower = actual.get("whether_close_below_lower")
    if stance in {"偏多", "震荡偏强"}:
        if direction == "up" and not break_lower:
            return "HIT"
        if direction == "down" and break_lower:
            return "MISS"
        return "PARTIAL"
    if stance in {"偏空", "震荡偏弱"}:
        if direction == "down" and not break_upper:
            return "HIT"
        if direction == "up" and break_upper:
            return "MISS"
        return "PARTIAL"
    if not break_upper and not break_lower:
        return "HIT"
    if (break_upper and not close_above_upper) or (break_lower and not close_below_lower):
        return "PARTIAL"
    return "MISS"


def attribution(previous: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    score = previous.get("score", {}) or {}
    errors: list[str] = []
    technical = as_float(score.get("technical")) or 50
    driver = as_float(score.get("driver")) or 50
    money_flow = as_float(score.get("money_flow")) or 50
    confidence = previous.get("view_confidence") or score.get("view_confidence")
    warning = str(previous.get("contradiction_warning") or score.get("contradiction_warning") or "")
    if abs(technical - 50) > abs(driver - 50) + 8:
        errors.append("技术面权重过高")
    if actual.get("whether_break_upper") or actual.get("whether_break_lower"):
        errors.append("支撑压力位设置不合理")
    if actual.get("volume_change") is not None and abs(actual["volume_change"]) >= 25:
        errors.append("资金行为低估")
    if actual.get("open_interest_change") is not None and abs(actual["open_interest_change"]) >= 8:
        errors.append("持仓变化低估")
    if driver < 52 and actual.get("intraday_direction") in {"up", "down"}:
        errors.append("外盘驱动遗漏")
    if money_flow < 52 and actual.get("intraday_direction") == "up":
        errors.append("板块轮动识别不足")
    if "库存" in warning:
        errors.append("库存旧数据被误用为今日驱动")
    if "政策" in warning:
        errors.append("政策旧消息被误用为今日驱动")
    if confidence == "高":
        errors.append("置信度过高")
    if warning and warning != "暂无明显冲突信号":
        errors.append("信号冲突未降级为震荡")
    return list(dict.fromkeys(errors)) or ["波动率低估"]


def suggestion_for(error_type: str, consecutive_count: int) -> dict[str, Any]:
    rule_pool = consecutive_count >= 3
    suggestions = {
        "技术面权重过高": ("技术面可触发方向结论", "技术面与驱动/资金冲突时应降级为震荡或分歧震荡。"),
        "基本面信息滞后": ("基本面慢变量参与评分", "非24小时基本面只作背景，不作为当日主驱动。"),
        "外盘驱动遗漏": ("外盘仅作说明", "FCPO、CBOT、原油方向一致时提高driver_score权重解释。"),
        "原油影响低估": ("原油按一般外盘处理", "原油大幅波动时提高生柴估值链条提示。"),
        "FCPO影响低估": ("FCPO只作外盘参考", "P合约应优先校验FCPO与内盘背离。"),
        "CBOT影响低估": ("CBOT只作豆油参考", "Y和油脂板块共振时提高CBOT豆油解释权重。"),
        "资金行为低估": ("成交量仅作辅助", "成交量异常变化应提高money_flow_score解释权重。"),
        "持仓变化低估": ("持仓只作背景", "价格与持仓同向变化时应提高资金确认强度。"),
        "板块轮动识别不足": ("单合约独立评分", "加入P/Y/OI相对强弱变化作为板块轮动提示。"),
        "库存旧数据被误用为今日驱动": ("库存压力影响方向", "周度库存只作背景压力，不作为今日主驱动。"),
        "政策旧消息被误用为今日驱动": ("政策消息影响方向", "旧政策未出现24小时新增进展时只作背景。"),
        "支撑压力位设置不合理": ("观察位由技术区间生成", "扩大波动率缓冲或引入前高前低二次确认。"),
        "波动率低估": ("ATR观察位固定倍数", "波动放大时提高观察区间宽度。"),
        "置信度过高": ("多因子一致时高置信", "存在冲突提示时置信度不得高于中。"),
        "信号冲突未降级为震荡": ("总分决定观点", "技术、驱动、资金冲突时优先输出分歧震荡。"),
    }
    original, new_rule = suggestions.get(error_type, ("原规则需核验", "保持观察并累计更多样本。"))
    return {
        "建议调整项": error_type,
        "原规则": original,
        "问题": f"{error_type}导致昨日观点未被今日行情验证。",
        "新规则建议": new_rule + (" 建议将该规则加入候选参数调整池。" if rule_pool else ""),
        "影响范围": "daily_review_skill 输出学习建议；不自动修改评分权重。",
        "是否需要人工确认": True,
        "whether_update_rule": rule_pool,
        "human_approval_required": True,
    }


def recent_consecutive_error_counts(output_dir: Path, error_types: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    paths = sorted(output_dir.glob("*.json"), reverse=True)[:5]
    for error_type in set(error_types):
        for path in paths:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                break
            rows = payload if isinstance(payload, list) else payload.get("items", [])
            present = any(error_type in (item.get("error_type", []) if isinstance(item, dict) else []) for item in rows)
            if not present:
                break
            counter[error_type] += 1
    return counter


def review_markdown(rows: list[dict[str, Any]], suggestions: list[dict[str, Any]]) -> str:
    lines = [
        "## 昨日判断复盘",
        "",
        "| 合约 | 昨日观点 | 今日实际 | 结果 | 偏差原因 |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        errors = "；".join(row.get("error_type") or ["无"])
        lines.append(f"| {row['contract']} | {row['previous_view']} | {row['actual_result']} | {row['hit_status']} | {errors} |")
    lines.extend(["", "## 偏差归因", ""])
    if any(row.get("error_type") for row in rows):
        for row in rows:
            if row.get("error_type"):
                lines.append(f"- {row['contract']}：{'; '.join(row['error_type'])}。")
    else:
        lines.append("- 今日无 MISS，暂不生成偏差归因。")
    lines.extend(["", "## 改进建议", ""])
    if suggestions:
        for item in suggestions:
            lines.append(
                f"- 建议调整项：{item['建议调整项']}；原规则：{item['原规则']}；问题：{item['问题']}；"
                f"新规则建议：{item['新规则建议']}；影响范围：{item['影响范围']}；是否需要人工确认：是。"
            )
    else:
        lines.append("- 今日无 MISS，不建议调整核心规则。")
    return "\n".join(lines)


def fmt(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "需进一步核验"
    return f"{number:.2f}"


def run_review(previous_path: Path, current_path: Path, date: str, output_dir: Path) -> dict[str, Any]:
    previous = contract_map(load_js_payload(previous_path))
    current = contract_map(load_js_payload(current_path))
    rows: list[dict[str, Any]] = []
    learning: list[dict[str, Any]] = []
    all_errors: list[str] = []
    missing = sorted(product for product in TRACKED if product not in previous or product not in current)
    if missing:
        failure = {
            "date": date,
            "status": "REVIEW_FAILED",
            "review_result": [],
            "error_type": ["主力合约复盘数据缺失"],
            "suggested_improvement": [],
            "whether_update_rule": False,
            "human_approval_required": True,
            "failure_reason": f"缺少主力合约复盘数据：{', '.join(missing)}",
            "missing_products": missing,
            "review_markdown": "## 昨日判断复盘\n\nREVIEW_FAILED：主力合约复盘数据不完整，禁止生成正常复盘结论。",
            "learning_notes": [],
        }
        memory_result = save_review(failure, output_dir)
        return {
            **failure,
            "learning_notes_path": str(ROOT / memory_result["saved"]),
            "review_memory": memory_result,
        }

    for product in sorted(TRACKED):
        prev = previous[product]
        cur = current[product]
        if not prev or not cur:
            continue
        score = prev.get("score", {}) or {}
        stance = str(score.get("stance") or "震荡")
        upper, lower = upper_lower(prev)
        actual = actual_market(prev, cur, upper, lower)
        hit_status = classify(stance, actual)
        errors = attribution(prev, actual) if hit_status == "MISS" else []
        all_errors.extend(errors)
        actual_result = f"{cur.get('change', '需进一步核验')}，高 {cur.get('high', '需进一步核验')} / 低 {cur.get('low', '需进一步核验')} / 收 {cur.get('price', '需进一步核验')}"
        rows.append(
            {
                "contract": str(cur.get("contract") or cur.get("symbol") or product),
                "product": product,
                "contract_rank": 1,
                "previous_view": stance,
                "actual_result": actual_result,
                "hit_status": hit_status,
                "error_type": errors,
                "actual_market": actual,
            }
        )
    counts = recent_consecutive_error_counts(output_dir, all_errors)
    current_errors = set(all_errors)
    suggestions = [suggestion_for(error, counts[error] + (1 if error in current_errors else 0)) for error in sorted(current_errors)]
    for row in rows:
        root_cause = "；".join(row["error_type"]) if row["error_type"] else "昨日观点基本被今日行情验证"
        learning.append(
            {
                "date": date,
                "contract": row["contract"],
                "previous_view": row["previous_view"],
                "actual_result": row["actual_result"],
                "hit_status": row["hit_status"],
                "error_type": row["error_type"],
                "root_cause": root_cause,
                "suggested_rule_change": [item["新规则建议"] for item in suggestions if item["建议调整项"] in row["error_type"]],
                "confidence_adjustment": "MISS时下调一档；HIT保持；PARTIAL维持中性观察",
                "requires_human_approval": bool(row["error_type"]),
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    review_payload = {
        "date": date,
        "status": "OK",
        "review_result": rows,
        "error_type": sorted(set(all_errors)),
        "suggested_improvement": suggestions,
        "whether_update_rule": any(item["whether_update_rule"] for item in suggestions),
        "human_approval_required": bool(suggestions),
        "review_markdown": review_markdown(rows, suggestions),
        "learning_notes": learning,
    }
    memory_result = save_review(review_payload, output_dir)
    return {
        **review_payload,
        "learning_notes_path": str(ROOT / memory_result["saved"]),
        "review_memory": memory_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    result = run_review(args.previous, args.current, args.date, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result.get("status") == "REVIEW_FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())

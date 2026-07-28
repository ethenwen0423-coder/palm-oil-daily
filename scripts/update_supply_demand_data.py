#!/usr/bin/env python3
"""Build the static Malaysia and Indonesia palm-oil supply/demand dataset."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Shanghai")
MPOB_BASE = "https://bepi.mpob.gov.my/stat/web_report1.php?val="
GAPKI_BASE = "https://gapki.id"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) VinsonResearch/1.0"
DISPLAY_MONTHS = 24
# Include the current, not-yet-published month so at least 25 released months
# can be retained under the normal one-month publication lag.
MIN_HISTORY_MONTHS = 26
MONTH_NAMES = {
    "januari": 1,
    "februari": 2,
    "maret": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "agustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "desember": 12,
}
MONTH_PATTERN = "|".join(MONTH_NAMES)
# Match text within one sentence while allowing Indonesian thousands separators.
CLAUSE_PATTERN = r"(?:[^.\n]|\.(?=\d))"


class SourceUnavailable(RuntimeError):
    """The source could not be accessed."""


class SourceParseError(RuntimeError):
    """The source response did not contain an unambiguous data point."""


class TableParser(HTMLParser):
    """Small dependency-free HTML table parser for MPOB's stable tables."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] = []
        self._cell: list[str] = []
        self._in_cell = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"}:
            self._in_cell = True
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._in_cell:
            self._row.append(" ".join("".join(self._cell).split()))
            self._in_cell = False
        elif tag == "tr" and self._row:
            self.rows.append(self._row)


def fetch_text(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SourceUnavailable(f"{url}: {exc}") from exc


def month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def shift_month(period: str, delta: int) -> str:
    year, month = map(int, period.split("-"))
    absolute = year * 12 + month - 1 + delta
    return month_key(absolute // 12, absolute % 12 + 1)


def release_date_for_period(period: str, day: int = 10) -> str:
    next_period = shift_month(period, 1)
    year, month = map(int, next_period.split("-"))
    return date(year, month, min(day, 28)).isoformat()


def parse_integer(value: str) -> int | None:
    cleaned = value.replace(",", "").replace("\xa0", "").strip()
    if not cleaned or not re.fullmatch(r"\d+(?:\.\d+)?", cleaned):
        return None
    return int(round(float(cleaned)))


def parse_indonesian_quantity(raw: str, magnitude: str | None) -> int:
    value = raw.strip()
    magnitude = (magnitude or "").lower()
    if "," in value and "." in value:
        numeric = float(value.replace(".", "").replace(",", "."))
    elif "," in value:
        numeric = float(value.replace(",", "."))
    elif "." in value and magnitude == "ribu" and len(value.rsplit(".", 1)[1]) == 3:
        numeric = float(value.replace(".", ""))
    else:
        numeric = float(value)
    if magnitude == "ribu":
        numeric *= 1_000
    elif magnitude == "juta":
        numeric *= 1_000_000
    return int(round(numeric))


def point(period: str, value: int, published_at: str, source_url: str) -> dict[str, object]:
    return {
        "period": period,
        "value": value,
        "published_at": published_at,
        "source_url": source_url,
    }


def parse_mpob_export(html: str, year: int, source_url: str) -> list[dict[str, object]]:
    parser = TableParser()
    parser.feed(html)
    target = next(
        (
            row
            for row in parser.rows
            if len(row) >= 14 and row[0].strip().upper() == "PALM OIL" and row[1].upper() == "TONNES"
        ),
        None,
    )
    if target is None:
        raise SourceParseError(f"MPOB export row missing for {year}")
    result = []
    for month, raw in enumerate(target[2:14], start=1):
        value = parse_integer(raw)
        if value is not None:
            period = month_key(year, month)
            result.append(point(period, value, release_date_for_period(period), source_url))
    return result


def parse_mpob_paired_rows(
    html: str,
    year: int,
    row_label: str,
    source_url: str,
) -> list[dict[str, object]]:
    parser = TableParser()
    parser.feed(html)
    rows = [
        row
        for row in parser.rows
        if len(row) >= 13 and row[0].strip().upper() == row_label.upper()
    ]
    if not rows:
        raise SourceParseError(f"MPOB row {row_label!r} missing for {year}")
    result: list[dict[str, object]] = []
    month = 1
    for row in rows[:2]:
        pairs = row[1:13]
        for index in range(1, len(pairs), 2):
            value = parse_integer(pairs[index])
            if value is not None:
                period = month_key(year, month)
                result.append(point(period, value, release_date_for_period(period), source_url))
            month += 1
    return result


def fetch_malaysia_year(year: int) -> dict[str, list[dict[str, object]]]:
    codes = {
        "production": (f"{year}44", "MALAYSIA"),
        "exports": (f"{year}34", "PALM OIL"),
        "stocks": (f"{year}11", "TOTAL PALM OIL"),
    }
    result: dict[str, list[dict[str, object]]] = {}
    for metric, (code, label) in codes.items():
        source_url = f"{MPOB_BASE}{code}"
        html = fetch_text(source_url)
        if metric == "exports":
            result[metric] = parse_mpob_export(html, year, source_url)
        else:
            result[metric] = parse_mpob_paired_rows(html, year, label, source_url)
    return result


def strip_html(fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", fragment)
    return " ".join(unescape(without_tags).replace("\xa0", " ").split())


def extract_gapki_page(html: str) -> tuple[str, str, str]:
    title_match = re.search(r"<h1[^>]*class=[\"'][^\"']*entry-title[^\"']*[\"'][^>]*>(.*?)</h1>", html, re.I | re.S)
    title = strip_html(title_match.group(1)) if title_match else ""
    published_match = re.search(r'article:published_time["\']\s+content=["\']([^"\']+)', html, re.I)
    if not published_match:
        published_match = re.search(r'<time[^>]+datetime=["\']([^"\']+)', html, re.I)
    published_at = published_match.group(1)[:10] if published_match else ""
    paragraphs = [strip_html(item) for item in re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.I | re.S)]
    body = "\n".join(item for item in paragraphs if item)
    return title, published_at, body


def infer_gapki_period(title: str, body: str) -> str | None:
    for text in (title, body):
        match = re.search(rf"\b({MONTH_PATTERN})\s+(20\d{{2}})\b", text, re.I)
        if match:
            return month_key(int(match.group(2)), MONTH_NAMES[match.group(1).lower()])
    return None


def quantity_from_match(match: re.Match[str]) -> int:
    return parse_indonesian_quantity(match.group("value"), match.groupdict().get("magnitude"))


def parse_gapki_article(html: str, source_url: str) -> tuple[str, str, dict[str, dict[str, object]]]:
    title, published_at, body = extract_gapki_page(html)
    period = infer_gapki_period(title, body)
    if not period or not published_at:
        raise SourceParseError(f"GAPKI article has no period or publication date: {source_url}")

    metric_patterns = {
        "production": [
            rf"Produksi\s+CPO(?!\s*(?:dan|&)\s*PKO)(?:\s+(?:pada|bulan))?(?:\s+({MONTH_PATTERN})\s+20\d{{2}})?"
            rf"[^.]*?\b(?:mencapai|sebesar|menjadi)\s+(?P<value>\d[\d.,]*)\s*"
            rf"(?P<magnitude>ribu|juta)?\s*ton",
        ],
        "exports": [
            rf"Total\s+ekspor(?:\s+produk\s+sawit)?{CLAUSE_PATTERN}{{0,220}}?"
            rf"\b(?:mencapai|sebesar|menjadi)\s+(?P<value>\d[\d.,]*)\s*"
            rf"(?P<magnitude>ribu|juta)?\s*ton",
        ],
        "stocks": [
            rf"stok\s+(?:di\s+)?akhir\s+(?:({MONTH_PATTERN})\s+20\d{{2}})?"
            rf"[^.]*?\b(?:mencapai|sebesar|menjadi|tercatat\s+sebesar)\s+(?P<value>\d[\d.,]*)\s*"
            rf"(?P<magnitude>ribu|juta)?\s*ton",
            rf"stok(?:\s+CPO|\s+minyak\s+sawit|\s+akhir)?[^.]{{0,100}}?"
            rf"\b(?:mencapai|sebesar|menjadi|tercatat\s+sebesar)\s+(?P<value>\d[\d.,]*)\s*"
            rf"(?P<magnitude>ribu|juta)?\s*ton",
        ],
    }

    parsed: dict[str, dict[str, object]] = {}
    for metric, patterns in metric_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, body, re.I)
            if match:
                parsed[metric] = point(period, quantity_from_match(match), published_at, source_url)
                break
    if len(parsed) < 2:
        raise SourceParseError(f"GAPKI article did not yield enough metrics: {source_url}")
    return period, published_at, parsed


def search_gapki_candidates(start_period: str) -> list[str]:
    candidates: dict[str, str] = {}
    for query in ("kinerja", "produksi", "stok"):
        endpoint = (
            f"{GAPKI_BASE}/wp-json/wp/v2/search?"
            + urllib.parse.urlencode({"search": query, "per_page": 100})
        )
        payload = json.loads(fetch_text(endpoint))
        for item in payload:
            title = unescape(str(item.get("title") or ""))
            url = str(item.get("url") or "")
            if "/news/" not in url:
                continue
            if not re.search(r"produksi|ekspor|stok|kinerja", title, re.I):
                continue
            url_date = re.search(r"/news/(20\d{2})/(\d{2})/", url)
            if url_date:
                article_period = month_key(int(url_date.group(1)), int(url_date.group(2)))
                if article_period < shift_month(start_period, 1):
                    continue
            candidates[url] = title
    return sorted(candidates)


def fetch_indonesia(start_period: str) -> dict[str, list[dict[str, object]]]:
    urls = search_gapki_candidates(start_period)
    if not urls:
        raise SourceParseError("GAPKI search returned no candidate monthly releases")
    collected: dict[str, dict[str, dict[str, object]]] = {
        "production": {},
        "exports": {},
        "stocks": {},
    }

    def parse_url(url: str) -> tuple[str, str, dict[str, dict[str, object]]] | None:
        try:
            return parse_gapki_article(fetch_text(url), url)
        except (SourceUnavailable, SourceParseError):
            return None

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(parse_url, url): url for url in urls}
        for future in as_completed(futures):
            parsed = future.result()
            if parsed is None:
                continue
            period, published_at, metrics = parsed
            if period < start_period:
                continue
            for metric, item in metrics.items():
                previous = collected[metric].get(period)
                if previous is None or str(previous["published_at"]) < published_at:
                    collected[metric][period] = item

    if not any(collected.values()):
        raise SourceParseError("GAPKI monthly releases yielded no structured observations")
    return {
        metric: [items[key] for key in sorted(items)]
        for metric, items in collected.items()
    }


def metric_payload(label: str, definition: str, series: list[dict[str, object]]) -> dict[str, object]:
    return {
        "label": label,
        "unit": "tonnes",
        "display_unit": "万吨",
        "definition": definition,
        "series": sorted(series, key=lambda item: str(item["period"])),
    }


def country_status(
    country: str,
    metrics: dict[str, dict[str, object]],
    today: date,
    fetch_error: str | None = None,
) -> tuple[str, str]:
    if fetch_error:
        return fetch_error, "本次官方来源更新失败，继续展示上次成功数据；需进一步核验。"
    series = [metric.get("series", []) for metric in metrics.values()]
    if any(not items for items in series):
        return "partial", "部分官方指标暂缺，缺失位置不做插值；需进一步核验。"
    latest_periods = [str(items[-1]["period"]) for items in series if items]
    latest = min(latest_periods)
    current = month_key(today.year, today.month)
    if country == "malaysia":
        expected = shift_month(current, -1 if today.day >= 12 else -2)
        if latest < expected:
            return "stale", "最新统计期晚于正常发布节奏，当前数值需进一步核验。"
    elif latest < shift_month(current, -3):
        return "stale", "最新统计期已落后超过三个完整自然月，当前数值需进一步核验。"
    if len(set(latest_periods)) > 1:
        return "partial", "各指标最新统计期不一致，页面按各自最近一期展示。"
    visible_start = shift_month(max(latest_periods), -(DISPLAY_MONTHS - 1))
    visible_counts = [
        sum(1 for item in items if str(item["period"]) >= visible_start)
        for items in series
    ]
    if any(count < DISPLAY_MONTHS for count in visible_counts):
        return "partial", "部分历史月份缺少可比的官方原始口径，图中保留断点；需进一步核验。"
    return "ok", "官方月度数据已更新。"


def latest_period(metrics: dict[str, dict[str, object]]) -> str | None:
    periods = [
        str(item["period"])
        for metric in metrics.values()
        for item in metric.get("series", [])
    ]
    return max(periods) if periods else None


def country_payload(
    key: str,
    source_data: dict[str, list[dict[str, object]]],
    today: date,
    fetch_error: str | None = None,
) -> dict[str, object]:
    if key == "malaysia":
        name = "马来西亚"
        source = {"name": "Malaysian Palm Oil Board (MPOB)", "url": "https://bepi.mpob.gov.my/"}
        definitions = {
            "production": ("CPO产量", "MPOB公布的马来西亚月度毛棕榈油（CPO）产量。"),
            "exports": ("棕榈油出口", "MPOB公布的PALM OIL出口量，包含CPO与加工棕榈油。"),
            "stocks": ("期末库存", "MPOB公布的TOTAL PALM OIL月末库存，包含CPO与加工棕榈油。"),
        }
    else:
        name = "印度尼西亚"
        source = {"name": "Gabungan Pengusaha Kelapa Sawit Indonesia (GAPKI)", "url": "https://gapki.id/"}
        definitions = {
            "production": ("CPO产量", "GAPKI月度行业稿披露的印度尼西亚CPO产量。"),
            "exports": ("棕榈油产品出口", "GAPKI月度行业稿披露的棕榈油产品出口总量，采用协会原始口径。"),
            "stocks": ("期末库存", "GAPKI月度行业稿披露的行业期末库存，采用协会原始口径。"),
        }
    metrics = {
        metric: metric_payload(label, definition, source_data.get(metric, []))
        for metric, (label, definition) in definitions.items()
    }
    status, message = country_status(key, metrics, today, fetch_error)
    return {
        "name": name,
        "status": status,
        "status_message": message,
        "latest_period": latest_period(metrics),
        "source": source,
        "metrics": metrics,
    }


def merge_source_data(
    fresh: dict[str, list[dict[str, object]]],
    previous_country: dict[str, object] | None,
) -> dict[str, list[dict[str, object]]]:
    previous_metrics = (previous_country or {}).get("metrics", {})
    result: dict[str, list[dict[str, object]]] = {}
    for metric in ("production", "exports", "stocks"):
        merged: dict[str, dict[str, object]] = {}
        old_metric = previous_metrics.get(metric, {}) if isinstance(previous_metrics, dict) else {}
        for item in old_metric.get("series", []) if isinstance(old_metric, dict) else []:
            merged[str(item["period"])] = item
        for item in fresh.get(metric, []):
            merged[str(item["period"])] = item
        result[metric] = [merged[key] for key in sorted(merged)]
    return result


def validate_payload(payload: dict[str, object], strict: bool = False) -> None:
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    countries = payload.get("countries")
    if not isinstance(countries, dict) or set(countries) != {"malaysia", "indonesia"}:
        raise ValueError("countries must contain malaysia and indonesia")
    for country_key, country in countries.items():
        if country.get("status") not in {"ok", "partial", "stale", "source_unreachable", "parse_error"}:
            raise ValueError(f"{country_key}: invalid status")
        metrics = country.get("metrics")
        if not isinstance(metrics, dict) or set(metrics) != {"production", "exports", "stocks"}:
            raise ValueError(f"{country_key}: invalid metric set")
        for metric_key, metric in metrics.items():
            series = metric.get("series")
            if not isinstance(series, list):
                raise ValueError(f"{country_key}.{metric_key}: series must be a list")
            periods: list[str] = []
            for item in series:
                period = str(item.get("period") or "")
                if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", period):
                    raise ValueError(f"{country_key}.{metric_key}: invalid period {period!r}")
                if not isinstance(item.get("value"), int) or int(item["value"]) < 0:
                    raise ValueError(f"{country_key}.{metric_key}: invalid value")
                if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", str(item.get("published_at") or "")):
                    raise ValueError(f"{country_key}.{metric_key}: invalid published_at")
                if not str(item.get("source_url") or "").startswith("https://"):
                    raise ValueError(f"{country_key}.{metric_key}: source_url is required")
                periods.append(period)
            if periods != sorted(set(periods)):
                raise ValueError(f"{country_key}.{metric_key}: periods must be unique and sorted")
            if strict and not series:
                raise ValueError(f"{country_key}.{metric_key}: no observations")


def load_existing(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def semantic_content(payload: dict[str, object]) -> object:
    return {
        "schema_version": payload.get("schema_version"),
        "display_months": payload.get("display_months"),
        "countries": payload.get("countries"),
    }


def build_payload(
    now: datetime,
    existing: dict[str, object],
    malaysia_fetcher: Callable[[int], dict[str, list[dict[str, object]]]] = fetch_malaysia_year,
    indonesia_fetcher: Callable[[str], dict[str, list[dict[str, object]]]] = fetch_indonesia,
) -> dict[str, object]:
    current_period = month_key(now.year, now.month)
    start_period = shift_month(current_period, -(MIN_HISTORY_MONTHS - 1))
    previous_countries = existing.get("countries", {}) if isinstance(existing, dict) else {}
    countries: dict[str, dict[str, object]] = {}

    malaysia_fresh: dict[str, list[dict[str, object]]] = {
        "production": [],
        "exports": [],
        "stocks": [],
    }
    malaysia_error: str | None = None
    try:
        for year in range(int(start_period[:4]), now.year + 1):
            yearly = malaysia_fetcher(year)
            for metric in malaysia_fresh:
                malaysia_fresh[metric].extend(
                    item for item in yearly.get(metric, []) if str(item["period"]) >= start_period
                )
    except SourceUnavailable:
        malaysia_error = "source_unreachable"
    except (SourceParseError, ValueError, KeyError):
        malaysia_error = "parse_error"
    malaysia_previous = previous_countries.get("malaysia") if isinstance(previous_countries, dict) else None
    malaysia_merged = merge_source_data(malaysia_fresh, malaysia_previous)
    countries["malaysia"] = country_payload("malaysia", malaysia_merged, now.date(), malaysia_error)

    indonesia_fresh: dict[str, list[dict[str, object]]] = {
        "production": [],
        "exports": [],
        "stocks": [],
    }
    indonesia_error: str | None = None
    try:
        indonesia_fresh = indonesia_fetcher(start_period)
    except SourceUnavailable:
        indonesia_error = "source_unreachable"
    except (SourceParseError, ValueError, KeyError, json.JSONDecodeError):
        indonesia_error = "parse_error"
    indonesia_previous = previous_countries.get("indonesia") if isinstance(previous_countries, dict) else None
    indonesia_merged = merge_source_data(indonesia_fresh, indonesia_previous)
    countries["indonesia"] = country_payload("indonesia", indonesia_merged, now.date(), indonesia_error)

    candidate: dict[str, object] = {
        "schema_version": 1,
        "generated_at": now.astimezone(TIMEZONE).isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "display_months": DISPLAY_MONTHS,
        "countries": countries,
    }
    validate_payload(candidate)
    if existing and semantic_content(candidate) == semantic_content(existing):
        candidate["generated_at"] = existing.get("generated_at", candidate["generated_at"])
    return candidate


def write_payload(payload: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/supply-demand.json"))
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--validate-only", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        validate_payload(json.loads(args.validate_only.read_text(encoding="utf-8")), strict=args.strict)
        print(f"validated {args.validate_only}")
        return 0
    existing_path = args.existing or (args.output if args.output.exists() else None)
    existing = load_existing(existing_path)
    payload = build_payload(datetime.now(TIMEZONE), existing)
    validate_payload(payload, strict=args.strict)
    write_payload(payload, args.output)
    statuses = {
        key: country["status"]
        for key, country in payload["countries"].items()
    }
    print(json.dumps({"output": str(args.output), "statuses": statuses}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, SourceUnavailable, SourceParseError, json.JSONDecodeError) as exc:
        print(f"supply-demand update failed: {exc}", file=sys.stderr)
        raise SystemExit(2)

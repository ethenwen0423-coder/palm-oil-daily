#!/usr/bin/env python3
"""Build the static Malaysia and Indonesia palm-oil supply/demand dataset."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
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
USDA_PSD_HOME = "https://apps.fas.usda.gov/psdonline/app/index.html"
USDA_PSD_ZIP = "https://apps.fas.usda.gov/psdonline/downloads/psd_oilseeds_csv.zip"
USDA_PSD_SOAP = "https://apps.fas.usda.gov/PSDExternalAPIService/svcPSD_AMIS.asmx"
USDA_COMMODITIES = {
    "palm": ("棕榈油", "4243000"),
    "soybean": ("豆油", "4232000"),
    "rapeseed": ("菜籽油", "4239100"),
    "sunflower": ("葵花籽油", "4236000"),
}
USDA_IMPORT_MARKETS = {
    "india": ("印度", "IN"),
    "china": ("中国", "CH"),
    "eu": ("欧盟", "E4"),
    "pakistan": ("巴基斯坦", "PK"),
}
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


def fetch_bytes(
    url: str,
    timeout: int = 30,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> bytes:
    request_headers = {"User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, data=data, headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SourceUnavailable(f"{url}: {exc}") from exc


def fetch_text(url: str, timeout: int = 20) -> str:
    return fetch_bytes(url, timeout=timeout).decode("utf-8", errors="ignore")


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


def marketing_year_label(year: int) -> str:
    return f"{year}/{str(year + 1)[-2:]}"


def psd_tonnes(raw: str) -> int:
    return int(round(float(raw) * 1_000))


def psd_release_period(row: dict[str, str]) -> str:
    year = int(row["Calendar_Year"])
    month = int(row["Month"])
    return month_key(year, month)


def parse_usda_country_archive(
    archive: bytes,
    minimum_year: int,
    maximum_year: int | None = None,
) -> list[dict[str, object]]:
    attributes = {"Imports", "Domestic Consumption", "Ending Stocks"}
    country_codes = {code: key for key, (_, code) in USDA_IMPORT_MARKETS.items()}
    observations: dict[str, dict[int, dict[str, object]]] = {
        key: {} for key in USDA_IMPORT_MARKETS
    }
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            csv_name = next(name for name in bundle.namelist() if name.lower().endswith(".csv"))
            with bundle.open(csv_name) as raw:
                reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
                for row in reader:
                    if row.get("Commodity_Code") != USDA_COMMODITIES["palm"][1]:
                        continue
                    market_key = country_codes.get(str(row.get("Country_Code") or ""))
                    attribute = str(row.get("Attribute_Description") or "")
                    if market_key is None or attribute not in attributes:
                        continue
                    if str(row.get("Unit_Description") or "").strip() != "(1000 MT)":
                        continue
                    market_year = int(row["Market_Year"])
                    if market_year < minimum_year or (
                        maximum_year is not None and market_year > maximum_year
                    ):
                        continue
                    item = observations[market_key].setdefault(
                        market_year,
                        {
                            "market_year": marketing_year_label(market_year),
                            "release_period": psd_release_period(row),
                            "source_url": USDA_PSD_ZIP,
                        },
                    )
                    item["release_period"] = max(
                        str(item["release_period"]),
                        psd_release_period(row),
                    )
                    field = {
                        "Imports": "imports",
                        "Domestic Consumption": "domestic_consumption",
                        "Ending Stocks": "ending_stocks",
                    }[attribute]
                    item[field] = psd_tonnes(row["Value"])
    except (zipfile.BadZipFile, StopIteration, KeyError, ValueError, csv.Error) as exc:
        raise SourceParseError(f"USDA PSD country archive could not be parsed: {exc}") from exc

    markets = []
    required = {"imports", "domestic_consumption", "ending_stocks"}
    for key, (name, _) in USDA_IMPORT_MARKETS.items():
        series = [
            item
            for _, item in sorted(observations[key].items())
            if required.issubset(item)
        ]
        if not series:
            raise SourceParseError(f"USDA PSD has no import-demand rows for {name}")
        markets.append({"key": key, "name": name, "series": series})
    return markets


def parse_usda_world_xml(
    payload: bytes,
    commodity_key: str,
    minimum_year: int,
    maximum_year: int | None = None,
) -> dict[str, object]:
    attributes = {"Production", "Total Dom. Cons.", "Ending Stocks"}
    observations: dict[int, dict[str, object]] = {}
    try:
        root = ET.fromstring(payload)
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] != "Commodity" or not list(element):
                continue
            row = {
                child.tag.rsplit("}", 1)[-1]: (child.text or "").strip()
                for child in element
            }
            attribute = row.get("Attribute_Description")
            if attribute not in attributes:
                continue
            if str(row.get("Unit_Description") or "").strip() != "(1000 MT)":
                continue
            market_year = int(row["Market_Year"])
            if market_year < minimum_year or (
                maximum_year is not None and market_year > maximum_year
            ):
                continue
            release_period = month_key(int(row["Calendar_Year"]), int(row["Month"]))
            item = observations.setdefault(
                market_year,
                {
                    "market_year": marketing_year_label(market_year),
                    "release_period": release_period,
                    "source_url": USDA_PSD_HOME,
                },
            )
            item["release_period"] = max(str(item["release_period"]), release_period)
            field = {
                "Production": "production",
                "Total Dom. Cons.": "domestic_consumption",
                "Ending Stocks": "ending_stocks",
            }[str(attribute)]
            item[field] = psd_tonnes(row["Value"])
    except (ET.ParseError, KeyError, ValueError) as exc:
        raise SourceParseError(f"USDA PSD world response could not be parsed: {exc}") from exc

    required = {"production", "domestic_consumption", "ending_stocks"}
    series = [
        item
        for _, item in sorted(observations.items())
        if required.issubset(item)
    ]
    if not series:
        raise SourceParseError(f"USDA PSD has no world balance for {commodity_key}")
    return {
        "key": commodity_key,
        "name": USDA_COMMODITIES[commodity_key][0],
        "series": series,
    }


def fetch_usda_world(
    commodity_key: str,
    minimum_year: int,
    maximum_year: int,
) -> dict[str, object]:
    code = USDA_COMMODITIES[commodity_key][1]
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getWorldDatabyCommodity xmlns="http://www.fas.usda.gov/wsfaspsd/">
      <strCommodityCode>{code}</strCommodityCode>
    </getWorldDatabyCommodity>
  </soap:Body>
</soap:Envelope>""".encode("utf-8")
    payload = fetch_bytes(
        USDA_PSD_SOAP,
        timeout=45,
        data=envelope,
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://www.fas.usda.gov/wsfaspsd/getWorldDatabyCommodity",
        },
    )
    return parse_usda_world_xml(payload, commodity_key, minimum_year, maximum_year)


def fetch_usda_supplemental(now: datetime) -> dict[str, object]:
    minimum_year = now.year - 11
    maximum_year = now.year - 1
    with ThreadPoolExecutor(max_workers=5) as executor:
        archive_future = executor.submit(fetch_bytes, USDA_PSD_ZIP, 90)
        world_futures = {
            key: executor.submit(fetch_usda_world, key, minimum_year, maximum_year)
            for key in USDA_COMMODITIES
        }
        archive = archive_future.result()
        import_markets = parse_usda_country_archive(archive, minimum_year, maximum_year)
        oils = [world_futures[key].result() for key in USDA_COMMODITIES]

    release_periods = [
        str(item["release_period"])
        for market in import_markets
        for item in market["series"]
    ] + [
        str(item["release_period"])
        for oil in oils
        for item in oil["series"]
    ]
    incomplete = (
        any(len(market["series"]) < 10 for market in import_markets)
        or any(len(oil["series"]) < 10 for oil in oils)
    )
    return {
        "status": "partial" if incomplete else "ok",
        "status_message": (
            "部分年度序列不足10个市场年度，按官方可用数据展示；需进一步核验。"
            if incomplete
            else "USDA PSD年度供需数据已更新。"
        ),
        "release_period": max(release_periods),
        "frequency": "market_year",
        "unit": "tonnes",
        "display_unit": "万吨",
        "source": {
            "name": "USDA Foreign Agricultural Service — Production, Supply and Distribution",
            "url": USDA_PSD_HOME,
            "download_url": USDA_PSD_ZIP,
        },
        "global_balance": {
            "title": "全球棕榈油年度平衡",
            "definition": "USDA PSD全球口径的产量、国内消费量与期末库存；不纳入下一市场年度预测。",
            "series": next(oil["series"] for oil in oils if oil["key"] == "palm"),
        },
        "import_demand": {
            "title": "主要进口市场需求",
            "definition": "统一采用USDA PSD市场年度口径，避免不同海关HS编码造成不可比。",
            "markets": import_markets,
        },
        "vegetable_oils": {
            "title": "四大植物油供需对比",
            "definition": "对比棕榈油、豆油、菜籽油和葵花籽油的全球供需；不纳入下一市场年度预测。",
            "oils": oils,
        },
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
    if payload.get("schema_version") not in {1, 2, 3}:
        raise ValueError("schema_version must be 1, 2 or 3")
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
    if int(payload.get("schema_version") or 0) >= 2:
        validate_supplemental(payload.get("supplemental"), strict=strict)
    if payload.get("schema_version") == 3:
        if payload.get("update_status") not in {"updated", "no_change", "source_error"}:
            raise ValueError("update_status is invalid")
        for field in ("checked_at", "data_updated_at"):
            try:
                datetime.fromisoformat(str(payload.get(field) or ""))
            except ValueError as exc:
                raise ValueError(f"{field} must be an ISO datetime") from exc
        if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", str(payload.get("checked_for_report_date") or "")):
            raise ValueError("checked_for_report_date must be YYYY-MM-DD")
        if not str(payload.get("update_message") or "").strip():
            raise ValueError("update_message is required")


def validate_annual_series(
    series: object,
    label: str,
    strict: bool,
) -> None:
    if not isinstance(series, list):
        raise ValueError(f"{label}: series must be a list")
    years: list[int] = []
    required = {"production", "domestic_consumption", "ending_stocks"}
    for item in series:
        if not isinstance(item, dict):
            raise ValueError(f"{label}: series item must be an object")
        match = re.fullmatch(r"(20\d{2})/\d{2}", str(item.get("market_year") or ""))
        if not match:
            raise ValueError(f"{label}: invalid market_year")
        years.append(int(match.group(1)))
        for field in required:
            if not isinstance(item.get(field), int) or int(item[field]) < 0:
                raise ValueError(f"{label}: invalid {field}")
        if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", str(item.get("release_period") or "")):
            raise ValueError(f"{label}: invalid release_period")
        if not str(item.get("source_url") or "").startswith("https://"):
            raise ValueError(f"{label}: source_url is required")
    if years != sorted(set(years)):
        raise ValueError(f"{label}: market years must be unique and sorted")
    if strict and not series:
        raise ValueError(f"{label}: no observations")


def validate_supplemental(value: object, strict: bool = False) -> None:
    if not isinstance(value, dict):
        raise ValueError("supplemental must be an object")
    if value.get("status") not in {"ok", "partial", "stale", "source_unreachable", "parse_error"}:
        raise ValueError("supplemental: invalid status")
    global_balance = value.get("global_balance")
    import_demand = value.get("import_demand")
    vegetable_oils = value.get("vegetable_oils")
    if not all(isinstance(item, dict) for item in (global_balance, import_demand, vegetable_oils)):
        raise ValueError("supplemental: required sections are missing")
    validate_annual_series(global_balance.get("series"), "supplemental.global_balance", strict)

    markets = import_demand.get("markets")
    if (
        not isinstance(markets, list)
        or not all(isinstance(item, dict) for item in markets)
        or {item.get("key") for item in markets} != set(USDA_IMPORT_MARKETS)
    ):
        raise ValueError("supplemental.import_demand: invalid markets")
    for market in markets:
        series = market.get("series")
        if not isinstance(series, list):
            raise ValueError("supplemental.import_demand: series must be a list")
        years: list[int] = []
        for item in series:
            match = re.fullmatch(r"(20\d{2})/\d{2}", str(item.get("market_year") or ""))
            if not match:
                raise ValueError("supplemental.import_demand: invalid market_year")
            years.append(int(match.group(1)))
            for field in ("imports", "domestic_consumption", "ending_stocks"):
                if not isinstance(item.get(field), int) or int(item[field]) < 0:
                    raise ValueError(f"supplemental.import_demand: invalid {field}")
            if not str(item.get("source_url") or "").startswith("https://"):
                raise ValueError("supplemental.import_demand: source_url is required")
        if years != sorted(set(years)):
            raise ValueError("supplemental.import_demand: market years must be unique and sorted")
        if strict and not series:
            raise ValueError("supplemental.import_demand: no observations")

    oils = vegetable_oils.get("oils")
    if (
        not isinstance(oils, list)
        or not all(isinstance(item, dict) for item in oils)
        or {item.get("key") for item in oils} != set(USDA_COMMODITIES)
    ):
        raise ValueError("supplemental.vegetable_oils: invalid oils")
    for oil in oils:
        validate_annual_series(
            oil.get("series"),
            f"supplemental.vegetable_oils.{oil.get('key')}",
            strict,
        )


def load_existing(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def semantic_content(payload: dict[str, object]) -> object:
    return {
        "schema_version": payload.get("schema_version"),
        "display_months": payload.get("display_months"),
        "countries": payload.get("countries"),
        "supplemental": payload.get("supplemental"),
    }


def data_content(payload: dict[str, object]) -> object:
    countries = payload.get("countries") if isinstance(payload, dict) else {}
    country_series = {}
    if isinstance(countries, dict):
        for country_key, country in countries.items():
            metrics = country.get("metrics", {}) if isinstance(country, dict) else {}
            country_series[country_key] = {
                metric_key: metric.get("series", [])
                for metric_key, metric in metrics.items()
                if isinstance(metric, dict)
            }
    supplemental = payload.get("supplemental") if isinstance(payload, dict) else {}
    if not isinstance(supplemental, dict):
        supplemental = {}
    global_balance = supplemental.get("global_balance", {})
    import_demand = supplemental.get("import_demand", {})
    vegetable_oils = supplemental.get("vegetable_oils", {})
    return {
        "countries": country_series,
        "global_balance": (
            global_balance.get("series", [])
            if isinstance(global_balance, dict)
            else []
        ),
        "import_demand": [
            {"key": market.get("key"), "series": market.get("series", [])}
            for market in (
                import_demand.get("markets", [])
                if isinstance(import_demand, dict)
                else []
            )
            if isinstance(market, dict)
        ],
        "vegetable_oils": [
            {"key": oil.get("key"), "series": oil.get("series", [])}
            for oil in (
                vegetable_oils.get("oils", [])
                if isinstance(vegetable_oils, dict)
                else []
            )
            if isinstance(oil, dict)
        ],
    }


def build_payload(
    now: datetime,
    existing: dict[str, object],
    malaysia_fetcher: Callable[[int], dict[str, list[dict[str, object]]]] = fetch_malaysia_year,
    indonesia_fetcher: Callable[[str], dict[str, list[dict[str, object]]]] = fetch_indonesia,
    usda_fetcher: Callable[[datetime], dict[str, object]] = fetch_usda_supplemental,
    report_date: str | None = None,
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

    previous_supplemental = existing.get("supplemental") if isinstance(existing, dict) else None
    supplemental: dict[str, object]
    try:
        supplemental = usda_fetcher(now)
    except SourceUnavailable:
        supplemental_error = "source_unreachable"
        supplemental = json.loads(json.dumps(previous_supplemental or {}))
        supplemental["status"] = supplemental_error
        supplemental["status_message"] = "本次USDA官方来源更新失败，继续展示上次成功数据；需进一步核验。"
    except (SourceParseError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError):
        supplemental_error = "parse_error"
        supplemental = json.loads(json.dumps(previous_supplemental or {}))
        supplemental["status"] = supplemental_error
        supplemental["status_message"] = "本次USDA官方数据解析失败，继续展示上次成功数据；需进一步核验。"

    candidate: dict[str, object] = {
        "schema_version": 3,
        "generated_at": now.astimezone(TIMEZONE).isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "display_months": DISPLAY_MONTHS,
        "countries": countries,
        "supplemental": supplemental,
    }
    data_changed = not existing or data_content(candidate) != data_content(existing)
    source_statuses = [
        country.get("status")
        for country in countries.values()
    ] + [supplemental.get("status")]
    checked_at = now.astimezone(TIMEZONE).isoformat(timespec="seconds")
    if any(status in {"source_unreachable", "parse_error"} for status in source_statuses):
        update_status = "source_error"
        update_message = "今日已检查官方来源，部分官网暂时无法访问；继续展示上次成功数据，需进一步核验。"
    elif data_changed:
        update_status = "updated"
        update_message = "今日检查发现官方新数据或历史修订，页面数据已完成更新。"
    else:
        update_status = "no_change"
        update_message = "今日已检查官方来源，官网暂未更新数据，继续展示最近一期官方值。"
    candidate.update(
        {
            "checked_at": checked_at,
            "checked_for_report_date": report_date or now.date().isoformat(),
            "data_updated_at": (
                checked_at
                if data_changed
                else existing.get("data_updated_at")
                or existing.get("generated_at")
                or checked_at
            ),
            "update_status": update_status,
            "update_message": update_message,
        }
    )
    validate_payload(candidate)
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
    parser.add_argument("--report-date")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        validate_payload(json.loads(args.validate_only.read_text(encoding="utf-8")), strict=args.strict)
        print(f"validated {args.validate_only}")
        return 0
    existing_path = args.existing or (args.output if args.output.exists() else None)
    existing = load_existing(existing_path)
    if args.report_date and not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", args.report_date):
        raise ValueError("--report-date must be YYYY-MM-DD")
    payload = build_payload(datetime.now(TIMEZONE), existing, report_date=args.report_date)
    validate_payload(payload, strict=args.strict)
    write_payload(payload, args.output)
    statuses = {
        key: country["status"]
        for key, country in payload["countries"].items()
    }
    statuses["usda_psd"] = payload["supplemental"]["status"]
    print(json.dumps({"output": str(args.output), "statuses": statuses}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, SourceUnavailable, SourceParseError, json.JSONDecodeError) as exc:
        print(f"supply-demand update failed: {exc}", file=sys.stderr)
        raise SystemExit(2)

#!/usr/bin/env python3
"""Collect source-backed oil-market news and research without blocking quotes."""

from __future__ import annotations

import concurrent.futures
import html
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any, Callable


GOOGLE_NEWS_URL = "https://news.google.com/rss/search"
BING_NEWS_URL = "https://www.bing.com/news/search"
HTFC_FLASH_PATH = "/bus/info/filter"
HTFC_REPORT_TYPES_PATH = "/bus/report/ptypes_v2"
HTFC_REPORT_LIST_PATH = "/bus/report/specificList"
WEB_QUERY = "(棕榈油 OR 豆油 OR 菜油 OR 大豆 OR 油脂油料 OR MPOB OR GAPKI OR 生物柴油 OR 产区天气 OR 降雨 OR 干旱) (研报 OR 报告 OR 快讯 OR 期货 OR 预报)"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_REGIONS = (
    {"name": "马来西亚柔佛", "lat": 1.4927, "lon": 103.7414, "scope": "P · FCPO", "crop": "棕榈油", "profile": "palm"},
    {"name": "印尼廖内", "lat": 0.5071, "lon": 101.4478, "scope": "P · FCPO", "crop": "棕榈油", "profile": "palm"},
    {"name": "美国爱荷华", "lat": 41.8780, "lon": -93.0977, "scope": "Y · M", "crop": "大豆", "profile": "us_soy"},
    {"name": "巴西马托格罗索", "lat": -12.6819, "lon": -56.9211, "scope": "Y · M", "crop": "大豆", "profile": "brazil_soy"},
    {"name": "加拿大萨斯喀彻温", "lat": 52.9399, "lon": -106.4509, "scope": "OI · RM", "crop": "油菜籽", "profile": "canola"},
)
WEATHER_AI_NOTICE = "AI 基于所列直接天气数据生成影响研判，不代表 Open-Meteo 或其他来源方的官方立场，不构成投资建议；请自行核验。"
WEATHER_MECHANISM_SOURCES = {
    "palm": {"name": "MPOB Journal of Oil Palm Research：降雨与棕榈油产量滞后", "url": "https://jopr.mpob.gov.my/the-effects-of-season-rainfall-and-cycle-of-oil-palm-yield-in-malaysia/"},
    "us_soy": {"name": "Iowa State University：大豆生长与R5-R6鼓粒阶段", "url": "https://crops.extension.iastate.edu/files/article/SoybeanGrowthandDevelopment_0.pdf"},
    "brazil_soy": {"name": "Embrapa：巴西大豆播种窗口与干旱风险", "url": "https://www.embrapa.br/en/busca-de-noticias/-/noticia/1472780/integracao-de-tecnologias-reduz-riscos-de-perda-com-estiagem"},
    "canola": {"name": "Canola Council of Canada：收获期天气、产量与品质", "url": "https://www.canolacouncil.org/canola-encyclopedia/harvest-management/"},
}
ARTICLE_TEXT_LIMIT = 12_000
ARTICLE_DOWNLOAD_LIMIT = 1_500_000
ARTICLE_CLASS_RE = re.compile(r"(?:article|post|entry|story|main)[-_ ]?(?:body|content|text)|xeditor_content", re.I)


class ArticleTextExtractor(HTMLParser):
    """Collect visible text from likely article containers without dependencies."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.capture_depths: list[int] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.depth += 1
        attributes = {name: value or "" for name, value in attrs}
        classes = attributes.get("class", "")
        if tag == "article" or ARTICLE_CLASS_RE.search(classes):
            self.capture_depths.append(self.depth)
        if self.capture_depths and tag in {"p", "br", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, _tag: str) -> None:
        if self.capture_depths and self.capture_depths[-1] == self.depth:
            self.capture_depths.pop()
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data: str) -> None:
        if self.capture_depths:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"[ \t\r\f\v]+", " ", "".join(self.parts)).strip()


def compact(value: Any, limit: int = 300) -> str:
    without_markup = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", without_markup).strip()[:limit]


def normalize_time(value: Any, fallback: datetime) -> str:
    text = compact(value, 80)
    if not text:
        return fallback.isoformat(timespec="seconds")
    parsed: datetime | None = None
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, OverflowError):
        pass
    if parsed is None:
        for candidate in (text, text.replace("/", "-")):
            try:
                parsed = datetime.fromisoformat(candidate)
                break
            except ValueError:
                pass
    if parsed is None:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=fallback.tzinfo)
    return parsed.astimezone(fallback.tzinfo).isoformat(timespec="seconds")


def request_json(url: str, timeout: int, *, headers: dict[str, str] | None = None, data: bytes | None = None) -> Any:
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def public_https_url(value: Any) -> str:
    url = compact(value, 1000)
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return ""
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)}
        if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
            return ""
    except (OSError, ValueError):
        return ""
    return url


def resolve_google_news_url(url: str, timeout: int = 10) -> str:
    """Resolve a Google News RSS wrapper to its publisher URL."""
    safe_url = public_https_url(url)
    parsed = urllib.parse.urlparse(safe_url)
    if not safe_url or parsed.hostname != "news.google.com":
        return safe_url
    article_match = re.search(r"/(?:rss/)?articles/([^/?]+)", parsed.path)
    if not article_match:
        return safe_url
    article_id = article_match.group(1)
    wrapper_url = f"https://news.google.com/rss/articles/{article_id}?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    request = urllib.request.Request(wrapper_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        wrapper = response.read(ARTICLE_DOWNLOAD_LIMIT + 1).decode("utf-8", "replace")
    timestamp = re.search(r'data-n-a-ts="([^"]+)', wrapper)
    signature = re.search(r'data-n-a-sg="([^"]+)', wrapper)
    if not timestamp or not signature:
        return safe_url
    rpc_request = [
        "garturlreq",
        [["X", "X", ["X", "X"], None, None, 1, 1, "CN:zh-Hans", None, 180, None, None, None, None, None, 0, None, None, [1608992183, 723341000]], "X", "X", 1, [1608992183, 723341000], 1, None, None, 0],
        article_id,
        int(timestamp.group(1)),
        signature.group(1),
    ]
    payload = [[["Fbv4je", json.dumps(rpc_request, separators=(",", ":")), None, "generic"]]]
    data = urllib.parse.urlencode({"f.req": json.dumps(payload, separators=(",", ":"))}).encode("utf-8")
    rpc = urllib.request.Request(
        "https://news.google.com/_/DotsSplashUi/data/batchexecute",
        data=data,
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
    )
    with urllib.request.urlopen(rpc, timeout=timeout) as response:
        result = response.read(200_000).decode("utf-8", "replace")
    match = re.search(r'\[\\"garturlres\\",\\"(https:[^"\\]+)', result)
    if not match:
        return safe_url
    return public_https_url(match.group(1).replace("\\/", "/")) or safe_url


def extract_article_text(document: str) -> str:
    candidates: list[str] = []
    # Eastmoney Fortune pages expose the complete article HTML as a JS string.
    match = re.search(r"var\s+articleTxt\s*=\s*(\"(?:\\.|[^\"\\])*\")\s*;", document, re.S)
    if match:
        try:
            candidates.append(clean_article_text(json.loads(match.group(1))))
        except (json.JSONDecodeError, TypeError):
            pass
    for match in re.finditer(r'"articleBody"\s*:\s*("(?:\\.|[^"\\])*")', document, re.S):
        try:
            candidates.append(clean_article_text(json.loads(match.group(1))))
        except (json.JSONDecodeError, TypeError):
            pass
    parser = ArticleTextExtractor()
    try:
        parser.feed(document)
        candidates.append(clean_article_text(parser.text()))
    except (ValueError, TypeError):
        pass
    for match in re.finditer(r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)', document, re.I):
        candidates.append(clean_article_text(html.unescape(match.group(1))))
    useful = [item for item in candidates if len(item) >= 80]
    return max(useful, key=len, default="")[:ARTICLE_TEXT_LIMIT]


def clean_article_text(value: Any) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>", " ", str(value or ""), flags=re.I | re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", text))
    lines = [re.sub(r"\s+", " ", line).strip(" =") for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def fetch_article_text(url: str, timeout: int = 10) -> tuple[str, str]:
    direct_url = resolve_google_news_url(url, timeout=timeout)
    safe_url = public_https_url(direct_url)
    if not safe_url:
        return url, ""
    request = urllib.request.Request(safe_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = str(response.headers.get("Content-Type") or "").lower()
        if "html" not in content_type:
            return safe_url, ""
        raw = response.read(ARTICLE_DOWNLOAD_LIMIT + 1)
        if len(raw) > ARTICLE_DOWNLOAD_LIMIT:
            return safe_url, ""
        charset = response.headers.get_content_charset() or "utf-8"
    return safe_url, extract_article_text(raw.decode(charset, "replace"))


def source_error(name: str, exc: BaseException) -> dict[str, Any]:
    state = "forbidden" if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403) else "error"
    return {"name": name, "state": state, "detail": f"抓取失败：{type(exc).__name__} {str(exc)[:100]}"}


def weather_analysis(region: dict[str, Any], now: datetime, rain_total: float, max_temp: float, hot_days: int, wet_days: int) -> dict[str, Any]:
    profile = region["profile"]
    source = WEATHER_MECHANISM_SOURCES[profile]
    if profile == "palm":
        stage = "常年采收；短期看采收运输，生物学产量看数月滞后"
        if rain_total > 140 or wet_days >= 6:
            impact, signal = "高", "短期供应偏紧风险"
            title = f"{region['name']}降雨密集：鲜果采收与到厂量或受扰"
            production = "频繁强降雨 → 田间采收和道路运输受阻 → 鲜果串到厂量可能下降 → 当期CPO产出节奏放慢。"
            market = "若主要产区同步出现并被产量数据确认，P与FCPO供应风险溢价偏多；单一地点一周预报不能直接等同全国减产。"
        elif rain_total < 10 and max_temp >= 35:
            impact, signal = "中", "远期减产观察"
            title = f"{region['name']}偏干偏热：短期利于采收，远期关注坐果"
            production = "短期干燥 → 田间作业更顺畅；若高温少雨持续数月 → 水分胁迫、授粉与坐果受压 → 约9至12个月后单产可能下修。"
            market = "近月供应未必收紧，远月P与FCPO才可能逐步计入减产预期；本周数据仅构成观察信号。"
        else:
            impact, signal = "低", "供应影响中性"
            title = f"{region['name']}温雨适中：短期供应影响有限"
            production = "本周未见持续干热或洪涝 → 采收运输大体正常 → 暂无证据下调当期鲜果串和CPO产量。"
            market = "对P与FCPO方向影响中性；需连续数周至数月异常天气，才能形成可靠的产量传导。"
        boundary = "油棕为多年生作物，一周天气主要影响采收节奏；真正的生物学减产通常存在数月滞后。"
    elif profile == "us_soy":
        stage = "8月通常处于结荚—鼓粒期（R5-R6），粒重和单产对热旱更敏感"
        if now.month in (8, 9) and rain_total < 10 and (hot_days >= 3 or max_temp >= 38):
            impact, signal = "高", "美豆单产下修风险"
            title = f"{region['name']}鼓粒期高温少雨：单产风险上升"
            production = "鼓粒期少雨叠加高温 → 蒸散增强、籽粒灌浆受限 → 粒重与单产预期可能下修。"
            market = "若干热覆盖美国中西部并被作物评级确认，CBOT大豆与豆油风险溢价偏多，Y与M通常跟随外盘传导。"
            boundary = "单点预报不能代表整个美豆带；必须同时核验土壤墒情、覆盖范围和USDA作物优良率。"
        elif rain_total < 15:
            impact, signal = "中", "单产压力观察"
            title = f"{region['name']}降雨偏少：鼓粒条件需继续核验"
            production = "鼓粒期水分补给偏少 → 粒重形成存在压力 → 单产预期可能边际下修。"
            market = "对CBOT大豆、豆油及Y/M偏多，但需更广区域和连续预报确认。"
            boundary = "一周少雨不是已确认减产，土壤前期储水可缓冲短期降水不足。"
        else:
            impact, signal = "低", "单产影响中性"
            title = f"{region['name']}温雨未见极端：美豆单产暂维持观察"
            production = "温雨未触发明显热旱阈值 → 鼓粒条件暂未恶化 → 暂无新增单产下修证据。"
            market = "对CBOT大豆、豆油及Y/M影响中性。"
            boundary = "仍需结合整个美豆带天气、土壤墒情和作物评级。"
    elif profile == "brazil_soy":
        stage = "8月多为播种前干季；大豆尚未大面积出苗"
        if now.month in (7, 8):
            impact, signal = "低", "当前产量影响中性"
            title = f"{region['name']}播种前干季少雨：暂不等于大豆减产"
            production = "作物尚未大面积播种 → 本周少雨没有直接受损对象 → 当前大豆产量不因这份预报下调。"
            market = "对CBOT大豆、豆油及Y/M当前影响中性；若9月下旬后雨季启动仍延迟，才会经播种推迟和二季作物窗口收窄形成偏多传导。"
            boundary = "必须按物候阶段解释；播种前的季节性干燥不能套用鼓粒期干旱逻辑。"
        elif rain_total < 15 and now.month in (9, 10, 11):
            impact, signal = "中", "播种延迟风险"
            title = f"{region['name']}播种窗口降雨不足：进度延迟风险上升"
            production = "土壤墒情不足 → 播种或出苗推迟 → 生育期和后续二季作物窗口被压缩 → 产量风险上升。"
            market = "若CONAB播种进度同步落后，CBOT大豆、豆油及Y/M风险溢价偏多。"
            boundary = "需核验雨季是否持续延迟以及官方播种进度，不能由单周预报直接确认减产。"
        else:
            impact, signal = "低", "播种条件中性"
            title = f"{region['name']}播种条件暂未恶化"
            production = "降雨尚未触发明显播种或出苗风险 → 当前产量预期暂不调整。"
            market = "对CBOT大豆、豆油及Y/M影响中性。"
            boundary = "继续核验区域雨季启动和官方播种进度。"
    else:
        stage = "8月通常处于成熟—割晒—收获期"
        if rain_total >= 40 or wet_days >= 3:
            impact, signal = ("高", "收获与品质风险") if rain_total >= 80 or wet_days >= 5 else ("中", "上市节奏放慢风险")
            title = f"{region['name']}收获期多雨：上市节奏与品质风险上升"
            production = "降雨增加 → 割晒、田间干燥和脱粒推迟 → 籽粒回潮及品质不确定性上升 → 可交付供应节奏放慢。"
            market = "若降雨范围扩大且收获进度落后，菜籽及OI/RM风险溢价偏多；这更多是收获损失和上市节奏风险，不等同生物学单产下降。"
            boundary = "需核验实际收获进度、霜冻和品质数据；油菜籽雨后也可能较快恢复收割。"
        elif max_temp >= 30 and rain_total < 10:
            impact, signal = "中", "收获损失观察"
            title = f"{region['name']}收获期偏热偏干：关注落粒损失"
            production = "高温干燥 → 成熟和田间干燥加快 → 有利收获推进，但过快干燥可能增加荚果开裂与落粒损失。"
            market = "供应节奏可能加快但损耗风险上升，对OI/RM方向暂偏中性。"
            boundary = "实际影响取决于成熟度、割晒方式和田间管理。"
        else:
            impact, signal = "低", "收获影响中性"
            title = f"{region['name']}收获天气平稳：供应节奏暂未受扰"
            production = "温雨未触发收获延迟或快速干燥风险 → 田间作业节奏暂不受明显影响。"
            market = "对菜籽及OI/RM影响中性。"
            boundary = "继续核验收获进度、霜冻和品质数据。"
    return {
        "stage": stage,
        "signal": signal,
        "title": title,
        "production_chain": production,
        "market_chain": market,
        "boundary": boundary,
        "impact": impact,
        "mechanism_source": source,
    }


def weather_events(watch: Any, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    failures: list[str] = []
    for region in WEATHER_REGIONS:
        params = {
            "latitude": region["lat"],
            "longitude": region["lon"],
            "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min",
            "forecast_days": 7,
            "timezone": "auto",
        }
        url = OPEN_METEO_URL + "?" + urllib.parse.urlencode(params)
        try:
            payload = request_json(url, timeout)
            daily = payload.get("daily") if isinstance(payload, dict) else None
            if not isinstance(daily, dict) or not daily.get("time"):
                raise ValueError("missing daily forecast")
            rain = [float(value or 0) for value in daily.get("precipitation_sum", [])]
            high = [float(value) for value in daily.get("temperature_2m_max", []) if value is not None]
            probability = [float(value or 0) for value in daily.get("precipitation_probability_max", [])]
            if not rain or not high:
                raise ValueError("incomplete weather metrics")
            rain_total = round(sum(rain), 1)
            hot_days = sum(value >= 35 for value in high)
            wet_days = sum(value >= 10 for value in rain)
            peak_probability = round(max(probability), 0) if probability else 0
            analysis = weather_analysis(region, now, rain_total, max(high), hot_days, wet_days)
            forecast_date = str(daily["time"][0])
            direct_facts = f"未来7日累计降雨 {rain_total:.1f} mm；最高降雨概率 {peak_probability:.0f}%；最高温 {max(high):.1f}°C；≥35°C共 {hot_days} 天。"
            summary = f"结论：{analysis['signal']}。因果链：{analysis['production_chain']}"
            events.append({
                "id": watch.event_id("weather", region["name"], forecast_date),
                "kind": "event",
                "category": "天气产量研判",
                "weather_region": region["name"],
                "title": analysis["title"],
                "summary": summary,
                "detail_summary": f"天气事实：{direct_facts} 物候位置：{analysis['stage']}。",
                "summary_generated": True,
                "ai_notice": WEATHER_AI_NOTICE,
                "interpretation": f"产量链：{analysis['production_chain']} 行情链：{analysis['market_chain']} 判断边界：{analysis['boundary']}",
                "weather_analysis": {
                    "direct_facts": direct_facts,
                    "signal": analysis["signal"],
                    "stage": analysis["stage"],
                    "production_chain": analysis["production_chain"],
                    "market_chain": analysis["market_chain"],
                    "boundary": analysis["boundary"],
                    "mechanism_source": analysis["mechanism_source"],
                },
                "weather_snapshot": {
                    "forecast_start": forecast_date,
                    "forecast_end": str(daily["time"][-1]),
                    "rain_total_mm": rain_total,
                    "peak_precipitation_probability_pct": peak_probability,
                    "max_temperature_c": round(max(high), 1),
                    "hot_days": hot_days,
                    "wet_days": wet_days,
                },
                "impact": analysis["impact"],
                "scope": region["scope"],
                "source": "Open-Meteo 直接预报数据",
                "url": url,
                "direct_source_available": True,
                "observed_at": now.isoformat(timespec="seconds"),
                "evidence_ids": [f"weather:{region['name']}:{forecast_date}"],
                "evidence": [direct_facts, f"物候：{analysis['stage']}", f"机制依据：{analysis['mechanism_source']['name']}"],
            })
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError, ValueError, TypeError) as exc:
            failures.append(f"{region['name']} {type(exc).__name__}")
    state = "ready" if not failures else ("degraded" if events else "error")
    detail = f"覆盖 {len(events)}/{len(WEATHER_REGIONS)} 个油脂油料核心产区"
    if failures:
        detail += "；失败：" + "、".join(failures)
    return events, {"name": "全球农产品产区天气", "state": state, "detail": detail}


def normalize_event(watch: Any, *, prefix: str, source: str, title: Any, summary: Any, observed_at: Any, url: Any = "", source_id: Any = "") -> dict[str, Any] | None:
    clean_title = watch.clean_source_text(title)
    clean_summary = watch.clean_source_text(summary)
    if not clean_title or not watch.flash_relevant(f"{clean_title} {clean_summary}"):
        return None
    observed = normalize_time(observed_at, fallback=datetime.now().astimezone())
    impact, interpretation = watch.impact_for(f"{clean_title} {clean_summary}")
    preview, detail_summary = watch.summarize_source_event(clean_title, clean_summary)
    clean_url = compact(url, 500)
    return {
        "id": watch.event_id(prefix, source_id or clean_title, observed, url),
        "kind": "event",
        "category": "跨源事件研判",
        "title": clean_title,
        "summary": preview,
        "detail_summary": detail_summary,
        "summary_generated": True,
        "ai_notice": watch.AI_EVENT_NOTICE,
        "interpretation": interpretation,
        "impact": impact,
        "scope": "P · Y · OI",
        "source": source,
        "url": clean_url,
        "direct_source_available": bool(clean_url),
        "observed_at": observed,
        "evidence_ids": [watch.event_id(f"{prefix}-evidence", source_id or clean_title, url)],
        # Consumed by run_event_watch.py before the public snapshot is written.
        # Private source text must never reach the public API.
        "_source_title": clean_title,
        "_source_summary": clean_summary,
    }


def rss_events(watch: Any, now: datetime, timeout: int = 10) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    providers = (
        ("Google News", GOOGLE_NEWS_URL + "?" + urllib.parse.urlencode({"q": WEB_QUERY + " when:1d", "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"})),
        ("Bing News", BING_NEWS_URL + "?" + urllib.parse.urlencode({"q": WEB_QUERY, "format": "rss"})),
    )
    events: list[dict[str, Any]] = []
    details: list[str] = []
    failures = 0
    for provider, url in providers:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/rss+xml, application/xml"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                root = ET.fromstring(response.read())
            items = root.findall(".//item")
            included = 0
            enriched = 0
            article_attempts = 0
            for item in items[:40]:
                observed = normalize_time(item.findtext("pubDate"), now)
                try:
                    if datetime.fromisoformat(observed) < now - timedelta(days=3):
                        continue
                except ValueError:
                    pass
                raw_title = item.findtext("title")
                raw_summary = item.findtext("description")
                raw_url = item.findtext("link") or ""
                if not watch.flash_relevant(f"{watch.clean_source_text(raw_title)} {watch.clean_source_text(raw_summary)}"):
                    continue
                direct_url = raw_url
                article_text = ""
                if article_attempts < 6:
                    article_attempts += 1
                    try:
                        direct_url, article_text = fetch_article_text(raw_url, timeout=min(timeout, 10))
                        if article_text:
                            enriched += 1
                    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, TypeError, json.JSONDecodeError):
                        pass
                event = normalize_event(
                    watch,
                    prefix="web-news",
                    source=f"跨站新闻·{provider}",
                    title=raw_title,
                    summary=article_text or raw_summary,
                    observed_at=observed,
                    url=direct_url,
                    source_id=item.findtext("guid"),
                )
                if event:
                    event["source_content_level"] = "full_article" if article_text else "source_summary"
                    if direct_url != raw_url:
                        event["aggregator_url"] = compact(raw_url, 500)
                    events.append(event)
                    included += 1
            details.append(f"{provider} {len(items)}→{included}（正文 {enriched}）")
        except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError, OSError) as exc:
            failures += 1
            details.append(f"{provider} {type(exc).__name__}")
    state = "ready" if failures == 0 else ("degraded" if failures < len(providers) else "error")
    return events[:30], {"name": "跨站新闻搜索", "state": state, "detail": "；".join(details)}


def htfc_flash_events(watch: Any, base_url: str | None, api_key: str | None, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = "机构资讯·油脂油料快讯"
    if not base_url or not api_key:
        return [], {"name": name, "state": "unavailable", "detail": "机构资讯接口未配置。"}
    url = base_url.rstrip("/") + HTFC_FLASH_PATH + "?" + urllib.parse.urlencode({"tags": "tags150", "lastId": "", "type": ""})
    try:
        payload = request_json(url, timeout, headers={"apikey": api_key})
        data = payload.get("data") if isinstance(payload, dict) else None
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("items") or []
        else:
            records = []
        events = []
        for item in records[:40]:
            if not isinstance(item, dict):
                continue
            event = normalize_event(
                watch,
                prefix="htfc-flash",
                source=name,
                title=item.get("title"),
                summary=item.get("content"),
                observed_at=" ".join(filter(None, (compact(item.get("date"), 20), compact(item.get("time"), 20)))) or now.isoformat(timespec="seconds"),
                url=item.get("url"),
                source_id=item.get("id"),
            )
            if event:
                event["source_fields"] = {key: item.get(key) for key in ("id", "tag", "tag2", "tagName", "type", "stars") if item.get(key) is not None}
                events.append(event)
        return events[:30], {"name": name, "state": "ready", "detail": f"精确标签 tags150 返回 {len(records)} 条，纳入 {len(events[:30])} 条。"}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError, AttributeError) as exc:
        return [], source_error(name, exc)


def category_pairs(payload: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(payload, dict):
        label = payload.get("item_name") or payload.get("name") or payload.get("label")
        value = payload.get("item_value") or payload.get("value")
        if label and value:
            pairs.append((str(label), str(value)))
        for child in payload.values():
            pairs.extend(category_pairs(child))
    elif isinstance(payload, list):
        for child in payload:
            pairs.extend(category_pairs(child))
    return pairs


def htfc_report_events(watch: Any, base_url: str | None, api_key: str | None, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = "机构资讯·研报"
    if not base_url or not api_key:
        return [], {"name": name, "state": "unavailable", "detail": "机构资讯接口未配置。"}
    try:
        types = request_json(base_url.rstrip("/") + HTFC_REPORT_TYPES_PATH, timeout, headers={"apikey": api_key})
        matching = [(label, value) for label, value in category_pairs(types) if watch.flash_relevant(label)]
        if not matching:
            return [], {"name": name, "state": "ready", "detail": "分类接口可用，但没有识别到油脂油料研报分类；未猜测 item_value。"}
        events: list[dict[str, Any]] = []
        scanned = 0
        for label, value in matching[:3]:
            url = base_url.rstrip("/") + HTFC_REPORT_LIST_PATH + "?" + urllib.parse.urlencode({"curPage": 1, "pageSize": 20, "item_value": value})
            payload = request_json(url, timeout, headers={"apikey": api_key})
            records = watch.extract_records(payload)
            scanned += len(records)
            for item in records[:20]:
                event = normalize_event(
                    watch,
                    prefix="htfc-report",
                    source=name,
                    title=item.get("title") or item.get("report_title") or item.get("name"),
                    summary=item.get("summary") or item.get("abstract") or item.get("content"),
                    observed_at=watch.event_time(item, now),
                    url=item.get("url") or item.get("link") or item.get("attachment_url"),
                    source_id=item.get("id") or item.get("report_id"),
                )
                if event:
                    event["research_category"] = label
                    events.append(event)
        return events[:30], {"name": name, "state": "ready", "detail": f"扫描 {len(matching[:3])} 个相关分类、{scanned} 篇，纳入 {len(events[:30])} 篇。"}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError, AttributeError) as exc:
        return [], source_error(name, exc)


def mx_events(watch: Any, api_key: str | None, now: datetime, timeout: int = 12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not api_key:
        return [], {"name": "东方财富妙想资讯", "state": "unavailable", "detail": "生产环境未配置 MX_APIKEY；公开东方财富快讯仍独立运行。"}
    return watch.news_events(api_key, now, timeout)


def collect_all(watch: Any, now: datetime, *, mx_api_key: str | None, htfc_base_url: str | None, htfc_api_key: str | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    jobs: tuple[Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]], ...] = (
        lambda: watch.eastmoney_flash_events(now, timeout=10),
        lambda: mx_events(watch, mx_api_key, now),
        lambda: rss_events(watch, now),
        lambda: htfc_flash_events(watch, htfc_base_url, htfc_api_key, now),
        lambda: htfc_report_events(watch, htfc_base_url, htfc_api_key, now),
        lambda: weather_events(watch, now),
    )
    events: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        for result in executor.map(lambda job: job(), jobs):
            batch, source = result
            events.extend(batch)
            sources.append(source)
    deduped: dict[str, dict[str, Any]] = {}
    for event in events:
        key = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", str(event.get("title") or "").lower())
        existing = deduped.get(key)
        if existing is None or str(event.get("observed_at") or "") > str(existing.get("observed_at") or ""):
            deduped[key] = event
    return list(deduped.values()), sources

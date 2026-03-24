#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "feed_sources.json"
OUTPUT_PATH = ROOT / "data" / "daily-brief.js"
USER_AGENT = "daily-briefing-bot/1.0 (+https://github.com/cake0524/daily-briefing)"
MAX_FEATURED = 2
MAX_BRIEFS = 4
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def shorten(text, max_len):
    text = strip_html(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def parse_date(raw_value):
    if not raw_value:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    try:
        parsed = parsedate_to_datetime(raw_value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        pass

    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ):
        try:
            parsed = datetime.strptime(raw_value, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def request_feed(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=20) as response:
        return response.read()


def get_child_text(parent, names):
    for name in names:
        child = parent.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def parse_rss(root, source_name):
    items = []
    channel = root.find("channel")
    if channel is None:
        return items

    for item in channel.findall("item"):
        link = get_child_text(item, ["link"])
        title = get_child_text(item, ["title"])
        description = get_child_text(item, ["description", "content:encoded"])
        pub_date = get_child_text(item, ["pubDate", "dc:date"])
        if not title or not link:
            continue
        items.append(
            {
                "source": source_name,
                "title": strip_html(title),
                "summary": shorten(description or title, 110),
                "description": shorten(description or title, 180),
                "url": link.strip(),
                "published_at": parse_date(pub_date),
            }
        )
    return items


def parse_atom(root, source_name):
    items = []
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}")[0] + "}"

    for entry in root.findall(f"{namespace}entry"):
        title = get_child_text(entry, [f"{namespace}title"])
        summary = get_child_text(entry, [f"{namespace}summary", f"{namespace}content"])
        updated = get_child_text(entry, [f"{namespace}updated", f"{namespace}published"])
        link = ""
        for link_node in entry.findall(f"{namespace}link"):
            href = link_node.attrib.get("href")
            rel = link_node.attrib.get("rel", "alternate")
            if href and rel == "alternate":
                link = href
                break
            if href and not link:
                link = href
        if not title or not link:
            continue
        items.append(
            {
                "source": source_name,
                "title": strip_html(title),
                "summary": shorten(summary or title, 110),
                "description": shorten(summary or title, 180),
                "url": link.strip(),
                "published_at": parse_date(updated),
            }
        )
    return items


def parse_feed(xml_bytes, source_name):
    root = ET.fromstring(xml_bytes)
    tag = root.tag.lower()
    if tag.endswith("rss") or tag.endswith("rdf"):
        return parse_rss(root, source_name)
    if tag.endswith("feed"):
        return parse_atom(root, source_name)
    return []


def fetch_items(feed):
    try:
        xml_bytes = request_feed(feed["url"])
        return parse_feed(xml_bytes, feed["source"])
    except (HTTPError, URLError, TimeoutError, ET.ParseError) as exc:
        print(f"warning: failed to fetch {feed['url']}: {exc}", file=sys.stderr)
        return []


def make_featured(items, impact_template):
    featured = []
    for index, item in enumerate(items[:MAX_FEATURED], start=1):
        published = item["published_at"].astimezone(SHANGHAI_TZ).strftime("%H:%M")
        featured.append(
            {
                "priority": f"重点看点 {index:02d}",
                "time": published,
                "title": item["title"],
                "summary": item["summary"],
                "impact": impact_template,
                "source": item["source"],
                "url": item["url"],
            }
        )
    return featured


def make_briefs(items):
    briefs = []
    for item in items[MAX_FEATURED : MAX_FEATURED + MAX_BRIEFS]:
        briefs.append(
            {
                "text": shorten(item["title"], 80),
                "source": item["source"],
                "url": item["url"],
            }
        )
    return briefs


def make_highlight(section, featured):
    if featured:
        title = featured[0]["title"]
    else:
        title = f"{section['title']} 暂无新内容"
    return {
        "topic": section["highlight_topic"],
        "title": shorten(title, 40),
        "summary": section["highlight_summary"],
    }


def dedupe(items):
    seen = set()
    deduped = []
    for item in items:
        key = item["url"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def build_data():
    config = load_config()
    sections = []
    highlights = []

    for section in config["sections"]:
        items = []
        for feed in section["feeds"]:
            items.extend(fetch_items(feed))

        items = dedupe(items)
        items.sort(key=lambda item: item["published_at"], reverse=True)

        featured = make_featured(items, section["impact_template"])
        briefs = make_briefs(items)
        sections.append(
            {
                "id": section["id"],
                "tag": section["tag"],
                "title": section["title"],
                "description": section["description"],
                "featured": featured,
                "briefs": briefs,
            }
        )
        highlights.append(make_highlight(section, featured))

    now = datetime.now(SHANGHAI_TZ)
    return {
        "publishDate": f"{now.year}年{now.month}月{now.day}日",
        "highlights": highlights[:3],
        "sections": sections,
    }


def write_output(data):
    serialized = json.dumps(data, ensure_ascii=False, indent=2)
    OUTPUT_PATH.write_text(f"window.dailyBrief = {serialized};\n", encoding="utf-8")


def main():
    data = build_data()
    write_output(data)


if __name__ == "__main__":
    main()

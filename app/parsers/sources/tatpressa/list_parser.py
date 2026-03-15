from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.models.news import TOPIC_CULTURE, TOPIC_ECOLOGY, TOPIC_SOCIETY
from app.parsers.contracts import ParsedNewsListItem, ParsedNewsListPage
from app.parsers.http_client import RetryHttpClient

NEWS_ID_RE = re.compile(r"/news/(?P<id>\d+)\.html")
TOP_LINE_DATE_RE = re.compile(r"(?P<date>\d{2}\.\d{2}\.\d{4})")


class TatpressaListParser:
    TOPIC_URLS = {
        TOPIC_ECOLOGY: "https://www.tatpressa.ru/news/subject/ekologiya-9.html",
        TOPIC_CULTURE: "https://www.tatpressa.ru/news/subject/kultura-4.html",
        TOPIC_SOCIETY: "https://www.tatpressa.ru/news/subject/obshchestvo-1.html",
    }

    def __init__(self, http_client: RetryHttpClient, topic_urls: dict[str, str] | None = None) -> None:
        self._http_client = http_client
        self._topic_urls = topic_urls or self.TOPIC_URLS

    async def parse_page(self, topic: str, page: int = 1) -> ParsedNewsListPage:
        base_url = self._topic_urls[topic]
        params = {"page": page} if page > 1 else None
        html = await self._http_client.get(base_url, params=params)
        soup = BeautifulSoup(html, "html.parser")

        items: list[ParsedNewsListItem] = []
        for item_node in soup.select("div.list-view div.items div.item"):
            title_node = item_node.select_one("a.title[href*='/news/']")
            if title_node is None:
                continue

            href = title_node.get("href", "").strip()
            external_url = urljoin(base_url, href)
            external_id = self._extract_external_id(href)
            if external_id is None:
                continue

            top_text = self._normalized_text(item_node.select_one("div.top"))
            parsed_date = self._extract_date(top_text)
            topic_raw = self._extract_topic_raw(top_text)

            description = self._normalized_text(item_node.select_one("a.short")) or self._normalized_text(
                title_node
            )
            image_url = self._extract_image(item_node, base_url)

            items.append(
                ParsedNewsListItem(
                    external_id=external_id,
                    external_url=external_url,
                    title=self._normalized_text(title_node),
                    description=description,
                    image_url=image_url,
                    published_at=parsed_date,
                    topic=topic,
                    topic_raw=topic_raw,
                    source_page=page,
                )
            )

        has_next_page = soup.select_one("div.pager li.next a") is not None
        return ParsedNewsListPage(topic=topic, page=page, items=items, has_next_page=has_next_page)

    @staticmethod
    def _normalized_text(node) -> str:
        if node is None:
            return ""
        return " ".join(node.get_text(" ", strip=True).split())

    @staticmethod
    def _extract_external_id(href: str) -> str | None:
        match = NEWS_ID_RE.search(href)
        if match is None:
            return None
        return match.group("id")

    @staticmethod
    def _extract_date(top_text: str) -> datetime:
        match = TOP_LINE_DATE_RE.search(top_text)
        if match is None:
            return datetime.utcnow()
        return datetime.strptime(match.group("date"), "%d.%m.%Y")

    @staticmethod
    def _extract_topic_raw(top_text: str) -> str | None:
        match = TOP_LINE_DATE_RE.search(top_text)
        if match is None:
            return None
        raw = top_text.replace(match.group("date"), "").strip()
        return raw or None

    @staticmethod
    def _extract_image(item_node, base_url: str) -> str | None:
        image_node = item_node.select_one("img.news_image")
        if image_node is None:
            return None
        image_src = image_node.get("src", "").strip()
        if not image_src:
            return None
        return urljoin(base_url, image_src)

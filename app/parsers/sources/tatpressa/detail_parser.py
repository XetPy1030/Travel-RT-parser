from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.parsers.contracts import ParsedNewsDetail
from app.parsers.http_client import RetryHttpClient

NOISE_LINE_RE = re.compile(
    r"^(Комментарии|Самые читаемые|Бренд-инфо|Пресс-инфо|Наверх|Реклама|WWW\.ТАТPRESSA|VK\.)",
    re.IGNORECASE,
)
NEWS_ID_RE = re.compile(r"/news/(?P<id>\d+)\.html")


class TatpressaDetailParser:
    def __init__(self, http_client: RetryHttpClient) -> None:
        self._http_client = http_client

    async def parse(self, external_url: str) -> ParsedNewsDetail:
        html = await self._http_client.get(external_url)
        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_title(soup)
        description = self._extract_description(soup)
        content = self._extract_content(soup)
        image_url = self._extract_image(soup, external_url)

        if not description:
            description = title
        if not content:
            content = description

        return ParsedNewsDetail(
            external_id=self._extract_external_id(external_url),
            external_url=external_url,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
        )

    @staticmethod
    def _extract_external_id(external_url: str) -> str:
        match = NEWS_ID_RE.search(external_url)
        return match.group("id") if match else external_url

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        for selector in ("td.central_column h1", "h1"):
            node = soup.select_one(selector)
            if node and node.get_text(strip=True):
                return " ".join(node.get_text(" ", strip=True).split())
        title_node = soup.select_one("title")
        if title_node and title_node.get_text(strip=True):
            return " ".join(title_node.get_text(" ", strip=True).split())
        return ""

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> str:
        description_meta = soup.select_one("meta[name='Description']")
        if description_meta and description_meta.get("content"):
            return " ".join(description_meta["content"].split())

        for selector in ("td.central_column p", "p"):
            node = soup.select_one(selector)
            if node and node.get_text(strip=True):
                return " ".join(node.get_text(" ", strip=True).split())
        return ""

    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        container = soup.select_one("td.central_column") or soup
        lines: list[str] = []
        for node in container.select("h1, p"):
            text = " ".join(node.get_text(" ", strip=True).split())
            if not text:
                continue
            if NOISE_LINE_RE.search(text):
                continue
            if len(text) < 2:
                continue
            lines.append(text)

        if not lines:
            raw_text = " ".join(container.get_text(" ", strip=True).split())
            return raw_text

        # Удаляем дубли заголовка в начале текста.
        if len(lines) >= 2 and lines[0].lower() == lines[1].lower():
            lines = lines[1:]

        return "\n".join(lines).strip()

    @staticmethod
    def _extract_image(soup: BeautifulSoup, page_url: str) -> str | None:
        image_node = soup.select_one("td.central_column img[src*='news']")
        if image_node is None:
            image_node = soup.select_one("img[src*='news']")
        if image_node is None:
            return None
        src = image_node.get("src", "").strip()
        if not src:
            return None
        return urljoin(page_url, src)

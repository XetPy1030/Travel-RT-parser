from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from loguru import logger

from app.config.settings import Settings
from app.models.news import (
    EXTERNAL_SOURCE_TATNEWS,
    TOPIC_CULTURE,
    TOPIC_ECOLOGY,
    TOPIC_SOCIETY,
    News,
    NewsParseCursor,
)
from app.parsers import RetryHttpClient
from app.parsers.contracts import ParsedNewsDetail, ParsedNewsListItem
from app.parsers.sources.tatpressa import TatpressaDetailParser, TatpressaListParser


@dataclass(slots=True)
class IngestionStats:
    created: int = 0
    updated: int = 0
    failed: int = 0
    skipped_duplicates: int = 0


class NewsIngestionService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def run(
        self,
        topics: Iterable[str] | None = None,
        max_pages_per_topic: int | None = None,
    ) -> IngestionStats:
        selected_topics = list(topics or [TOPIC_ECOLOGY, TOPIC_CULTURE, TOPIC_SOCIETY])
        max_pages = max_pages_per_topic or self._settings.news_max_pages_per_topic

        stats = IngestionStats()
        topic_urls = {
            TOPIC_ECOLOGY: self._settings.tatpressa_ecology_url,
            TOPIC_CULTURE: self._settings.tatpressa_culture_url,
            TOPIC_SOCIETY: self._settings.tatpressa_society_url,
        }

        async with RetryHttpClient(
            timeout_seconds=self._settings.http_timeout_seconds,
            retries=self._settings.http_retries,
            user_agent=self._settings.http_user_agent,
        ) as http_client:
            list_parser = TatpressaListParser(http_client=http_client, topic_urls=topic_urls)
            detail_parser = TatpressaDetailParser(http_client=http_client)

            for topic in selected_topics:
                await self._ingest_topic(
                    topic=topic,
                    max_pages=max_pages,
                    list_parser=list_parser,
                    detail_parser=detail_parser,
                    stats=stats,
                )

        return stats

    async def _ingest_topic(
        self,
        topic: str,
        max_pages: int,
        list_parser: TatpressaListParser,
        detail_parser: TatpressaDetailParser,
        stats: IngestionStats,
    ) -> None:
        cursor = await NewsParseCursor.get_or_none(external_source=EXTERNAL_SOURCE_TATNEWS, topic=topic)
        if cursor is None:
            cursor = await NewsParseCursor.create(
                external_source=EXTERNAL_SOURCE_TATNEWS,
                topic=topic,
                last_external_id=None,
                last_page=1,
            )

        stop_external_id = cursor.last_external_id
        newest_external_id = None
        should_stop = False

        for page in range(1, max_pages + 1):
            parsed_page = await list_parser.parse_page(topic=topic, page=page)
            if not parsed_page.items:
                break

            if page == 1:
                newest_external_id = parsed_page.items[0].external_id

            for item in parsed_page.items:
                if stop_external_id and item.external_id == stop_external_id:
                    stats.skipped_duplicates += 1
                    should_stop = True
                    break

                try:
                    detail = await detail_parser.parse(item.external_url)
                    created = await self._upsert_news(item=item, detail=detail)
                    if created:
                        stats.created += 1
                    else:
                        stats.updated += 1
                except Exception as exc:  # noqa: BLE001
                    stats.failed += 1
                    logger.exception("Failed to process news item {}: {}", item.external_url, exc)

            if should_stop or not parsed_page.has_next_page:
                break

        cursor.last_external_id = newest_external_id or cursor.last_external_id
        cursor.last_parsed_at = datetime.now(timezone.utc)
        cursor.last_page = 1
        await cursor.save()

    async def _upsert_news(self, item: ParsedNewsListItem, detail: ParsedNewsDetail) -> bool:
        payload_hash = self._build_payload_hash(item=item, detail=detail)

        defaults = {
            "external_url": item.external_url,
            "parsed_title": detail.title or item.title,
            "parsed_image": detail.image_url or item.image_url or "",
            "parsed_description": detail.description or item.description,
            "parsed_content": detail.content or item.description,
            "parsed_created_at": item.published_at,
            "parsed_topic": item.topic,
            "parsed_topic_raw": item.topic_raw,
            "source_page": item.source_page,
            "raw_payload_hash": payload_hash,
        }

        existed = await News.filter(
            external_source=EXTERNAL_SOURCE_TATNEWS,
            external_id=item.external_id,
        ).exists()

        if existed:
            await News.filter(
                external_source=EXTERNAL_SOURCE_TATNEWS,
                external_id=item.external_id,
            ).update(**defaults)
            return False

        await News.create(
            external_source=EXTERNAL_SOURCE_TATNEWS,
            external_id=item.external_id,
            **defaults,
        )
        return True

    @staticmethod
    def _build_payload_hash(item: ParsedNewsListItem, detail: ParsedNewsDetail) -> str:
        normalized = "|".join(
            [
                item.external_id,
                item.title,
                item.description,
                detail.title,
                detail.description,
                detail.content,
                item.topic,
            ]
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

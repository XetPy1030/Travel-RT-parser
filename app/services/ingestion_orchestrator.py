from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from loguru import logger

from app.config.settings import Settings
from app.services.news_ingestion_service import IngestionStats, NewsIngestionService


@dataclass(slots=True)
class ProcessedEntityStats:
    entity: str
    created: int = 0
    updated: int = 0
    failed: int = 0
    skipped: int = 0


class IngestionOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self._news_service = NewsIngestionService(settings=settings)

    async def run_once(self, topics: Iterable[str] | None = None) -> dict[str, ProcessedEntityStats]:
        result: dict[str, ProcessedEntityStats] = {}

        news_stats = await self._news_service.run(topics=topics)
        result["news"] = self._to_processed_stats("news", news_stats)

        # Заглушки под будущие сущности с отдельными источниками.
        result["places"] = await self._run_places_stub()
        result["routes"] = await self._run_routes_stub()
        return result

    async def _run_places_stub(self) -> ProcessedEntityStats:
        logger.info("Places ingestion is not implemented yet.")
        return ProcessedEntityStats(entity="places")

    async def _run_routes_stub(self) -> ProcessedEntityStats:
        logger.info("Routes ingestion is not implemented yet.")
        return ProcessedEntityStats(entity="routes")

    @staticmethod
    def _to_processed_stats(entity: str, stats: IngestionStats) -> ProcessedEntityStats:
        return ProcessedEntityStats(
            entity=entity,
            created=stats.created,
            updated=stats.updated,
            failed=stats.failed,
            skipped=stats.skipped_duplicates,
        )

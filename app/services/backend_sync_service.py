from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from loguru import logger

from app.config.settings import Settings
from app.models.base import BaseParsedEntity
from app.models.news import News


@dataclass(slots=True)
class SyncStats:
    sent: int = 0
    failed: int = 0
    skipped: int = 0


class BackendSyncService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def sync_approved_news(self, limit: int = 50) -> SyncStats:
        stats = SyncStats()
        queryset = News.filter(
            moderation_status=BaseParsedEntity.MODERATION_APPROVED,
            is_sent_to_backend=False,
        ).order_by("id").limit(limit)
        items = await queryset

        if not items:
            return stats

        async with self._build_client() as client:
            for item in items:
                try:
                    backend_id = await self.create_news(client=client, news=item)
                    item.backend_id = backend_id
                    item.is_sent_to_backend = True
                    item.backend_synced_at = datetime.now(timezone.utc)
                    await item.save()
                    stats.sent += 1
                except Exception as exc:  # noqa: BLE001
                    stats.failed += 1
                    logger.exception("Failed to sync news id {}: {}", item.id, exc)
        return stats

    async def create_news(self, client: httpx.AsyncClient, news: News) -> int | None:
        payload = self._build_news_payload(news)
        url = self._build_url(self._settings.backend_news_create_path)
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json() if response.content else {}
        return data.get("id")

    async def update_news(self, client: httpx.AsyncClient, news: News) -> None:
        # Контракт на будущее: обновление сущности в backend после изменений.
        _ = client
        _ = news
        raise NotImplementedError("Update sync is not enabled yet.")

    async def delete_news(self, client: httpx.AsyncClient, news: News) -> None:
        # Контракт на будущее: удаление сущности в backend.
        _ = client
        _ = news
        raise NotImplementedError("Delete sync is not enabled yet.")

    def _build_news_payload(self, news: News) -> dict:
        payload = {
            "title": news.parsed_title,
            "description": news.parsed_description,
            "content": news.parsed_content,
            "published_at": self._to_iso_datetime(news.parsed_created_at),
        }
        if news.parsed_image:
            # Временная стратегия: передаем URL, backend может скачать/привязать файл.
            payload["image_url"] = news.parsed_image
        return payload

    @staticmethod
    def _to_iso_datetime(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    def _build_url(self, path: str) -> str:
        base = self._settings.backend_base_url.rstrip("/")
        suffix = path if path.startswith("/") else f"/{path}"
        return f"{base}{suffix}"

    def _build_client(self) -> httpx.AsyncClient:
        headers = {}
        if self._settings.backend_token:
            headers["Authorization"] = f"Bearer {self._settings.backend_token}"

        return httpx.AsyncClient(
            timeout=self._settings.backend_timeout_seconds,
            headers=headers,
        )

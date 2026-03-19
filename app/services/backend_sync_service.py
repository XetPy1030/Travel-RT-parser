from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from loguru import logger
from tortoise.expressions import Q

from app.config.settings import Settings
from app.models.base import BaseParsedEntity
from app.models.news import News


@dataclass(slots=True)
class SyncStats:
    sent: int = 0
    failed: int = 0
    skipped: int = 0


@dataclass(frozen=True, slots=True)
class DownloadedImage:
    filename: str
    content: bytes
    content_type: str


class BackendSyncService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def sync_approved_news(self, limit: int = 50) -> SyncStats:
        stats = SyncStats()
        items = await self._get_items_to_sync(limit=limit)

        if not items:
            return stats

        async with self._build_backend_client() as backend_client, self._build_fetch_client() as fetch_client:
            for item in items:
                await self._sync_one(
                    backend_client=backend_client,
                    fetch_client=fetch_client,
                    news=item,
                    stats=stats,
                )
        return stats

    async def _get_items_to_sync(self, limit: int) -> list[News]:
        criteria = (
            Q(moderation_status=BaseParsedEntity.MODERATION_APPROVED, is_sent_to_backend=False)
            | Q(
                moderation_status=BaseParsedEntity.MODERATION_APPROVED,
                is_sent_to_backend=True,
                needs_backend_update=True,
            )
        )
        items = await News.filter(criteria).order_by("id").limit(limit)
        return list(items)

    async def _sync_one(
        self,
        backend_client: httpx.AsyncClient,
        fetch_client: httpx.AsyncClient,
        news: News,
        stats: SyncStats,
    ) -> None:
        try:
            if news.is_sent_to_backend and news.needs_backend_update:
                if not news.backend_id:
                    stats.skipped += 1
                    return
                await self.update_news(backend_client=backend_client, fetch_client=fetch_client, news=news)
                news.needs_backend_update = False
                news.backend_synced_at = datetime.now(timezone.utc)
                await news.save()
                stats.sent += 1
                return

            backend_id = await self.create_news(backend_client=backend_client, fetch_client=fetch_client, news=news)
            news.backend_id = backend_id
            news.is_sent_to_backend = True
            news.backend_synced_at = datetime.now(timezone.utc)
            news.needs_backend_update = False
            await news.save()
            stats.sent += 1
        except Exception as exc:  # noqa: BLE001
            stats.failed += 1
            logger.exception("Failed to sync news id {}: {}", news.id, exc)

    async def create_news(self, backend_client: httpx.AsyncClient, fetch_client: httpx.AsyncClient, news: News) -> int | None:
        url = self._build_url(self._settings.backend_news_create_path)
        if news.parsed_image:
            response = await self._post_news_with_image(
                backend_client=backend_client,
                fetch_client=fetch_client,
                url=url,
                news=news,
            )
        else:
            payload = self._build_news_payload(news)
            response = await backend_client.post(url, json=payload)
        response.raise_for_status()
        data = response.json() if response.content else {}
        return data.get("id")

    async def update_news(self, backend_client: httpx.AsyncClient, fetch_client: httpx.AsyncClient, news: News) -> None:
        if not news.backend_id:
            raise ValueError("backend_id is required for update")

        path = f"{self._settings.backend_news_create_path.rstrip('/')}/{news.backend_id}/"
        url = self._build_url(path)

        if news.parsed_image:
            response = await self._patch_news_with_image(
                backend_client=backend_client,
                fetch_client=fetch_client,
                url=url,
                news=news,
            )
        else:
            payload = self._build_news_payload(news)
            payload.pop("image_url", None)
            response = await backend_client.patch(url, json=payload)

        response.raise_for_status()

    async def _post_news_with_image(
        self,
        backend_client: httpx.AsyncClient,
        fetch_client: httpx.AsyncClient,
        url: str,
        news: News,
    ) -> httpx.Response:
        data = self._build_news_payload(news)
        image_url = data.pop("image_url", None)
        if not image_url:
            return await backend_client.post(url, json=data)

        image = await self._download_image(client=fetch_client, url=image_url)
        if not image:
            return await backend_client.post(url, json=data)

        files = {"image": (image.filename, image.content, image.content_type)}
        return await backend_client.post(url, data=data, files=files)

    async def _patch_news_with_image(
        self,
        backend_client: httpx.AsyncClient,
        fetch_client: httpx.AsyncClient,
        url: str,
        news: News,
    ) -> httpx.Response:
        data = self._build_news_payload(news)
        image_url = data.pop("image_url", None)
        if not image_url:
            return await backend_client.patch(url, json=data)

        image = await self._download_image(client=fetch_client, url=image_url)
        if not image:
            return await backend_client.patch(url, json=data)

        payload = dict(data)
        files = {"image": (image.filename, image.content, image.content_type)}
        return await backend_client.patch(url, data=payload, files=files)

    async def _download_image(self, client: httpx.AsyncClient, url: str) -> DownloadedImage | None:
        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to download image {}: {}", url, exc)
            return None

        content = resp.content
        if not content:
            return None

        content_type = resp.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()
        filename = self._filename_from_url(url, content_type=content_type)
        return DownloadedImage(filename=filename, content=content, content_type=content_type)

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
    def _filename_from_url(url: str, content_type: str) -> str:
        name = url.split("?")[0].rstrip("/").split("/")[-1] or "image"
        if "." in name and len(name.rsplit(".", 1)[-1]) <= 5:
            return name

        ext = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }.get(content_type, "bin")
        return f"{name}.{ext}"

    @staticmethod
    def _to_iso_datetime(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    def _build_url(self, path: str) -> str:
        base = self._settings.backend_base_url.rstrip("/")
        suffix = path if path.startswith("/") else f"/{path}"
        return f"{base}{suffix}"

    def _build_backend_client(self) -> httpx.AsyncClient:
        headers = {}
        if self._settings.backend_token:
            headers["Authorization"] = f"Bearer {self._settings.backend_token}"

        return httpx.AsyncClient(
            timeout=self._settings.backend_timeout_seconds,
            headers=headers,
        )

    def _build_fetch_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._settings.http_timeout_seconds)

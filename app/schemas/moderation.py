"""Схемы для эндпоинтов модерации."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class NewsRead(BaseModel):
    """Карточка новости для чтения (список и деталь)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    external_source: str
    external_url: str
    parsed_title: str
    parsed_description: str
    parsed_created_at: datetime
    parsed_topic: str
    moderation_status: str
    moderation_comment: str | None
    is_sent_to_backend: bool
    backend_id: int | None
    needs_backend_update: bool


class ModerationActionResult(BaseModel):
    """Ответ на действие модерации (approve/reject)."""

    status: Literal["ok"] = "ok"
    news_id: int
    moderation_status: str

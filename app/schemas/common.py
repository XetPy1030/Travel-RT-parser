"""Общие схемы ответов API."""
from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ эндпоинта проверки здоровья сервиса."""

    status: str

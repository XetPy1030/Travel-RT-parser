"""Схемы для эндпоинтов аутентификации."""
from __future__ import annotations

from pydantic import BaseModel


class TokenRequest(BaseModel):
    """Тело запроса: пароль для входа."""

    password: str


class TokenResponse(BaseModel):
    """Ответ: access_token и тип."""

    access_token: str
    token_type: str = "bearer"

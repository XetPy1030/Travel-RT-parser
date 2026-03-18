"""Эндпоинт для получения JWT по паролю."""
from __future__ import annotations

import secrets

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.auth import create_access_token
from app.config.settings import settings

router = APIRouter(tags=["auth"])


class TokenRequest(BaseModel):
    """Тело запроса: пароль для входа."""

    password: str


class TokenResponse(BaseModel):
    """Ответ: access_token и тип."""

    access_token: str
    token_type: str = "bearer"


def _password_ok(password: str) -> bool:
    """Сравнение пароля за константное время (защита от timing-атак)."""
    expected = settings.auth_password
    return bool(expected) and secrets.compare_digest(password, expected)


@router.post("/token", response_model=TokenResponse)
async def login(data: TokenRequest) -> TokenResponse:
    """
    Принимает пароль, возвращает JWT.
    Пароль задаётся в настройках (AUTH_PASSWORD).
    """
    if not settings.auth_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth not configured (AUTH_PASSWORD not set)",
        )
    if not _password_ok(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    token = create_access_token()
    return TokenResponse(access_token=token)

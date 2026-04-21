"""Реэкспорт схем API."""
from __future__ import annotations

from app.schemas.auth import TokenRequest, TokenResponse
from app.schemas.common import HealthResponse
from app.schemas.moderation import ModerationActionResult, ModerationApproveAllResult, NewsRead

__all__ = [
    "HealthResponse",
    "ModerationActionResult",
    "ModerationApproveAllResult",
    "NewsRead",
    "TokenRequest",
    "TokenResponse",
]

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.models.base import BaseParsedEntity
from app.models.news import News
from app.schemas import ModerationActionResult, ModerationApproveAllResult, NewsRead

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/pending/news", response_model=list[NewsRead])
async def list_pending_news(limit: int = Query(default=50, ge=1, le=500)) -> list[NewsRead]:
    news_list = await News.filter(
        moderation_status=BaseParsedEntity.MODERATION_PENDING,
    ).limit(limit).order_by("-parsed_at")
    return [NewsRead.model_validate(item) for item in news_list]


@router.post("/news/approve-all", response_model=ModerationApproveAllResult)
async def approve_all_pending_news() -> ModerationApproveAllResult:
    """Одобрить все новости со статусом «на модерации» (одним запросом к БД)."""
    now = datetime.now(timezone.utc)
    approved_count = await News.filter(
        moderation_status=BaseParsedEntity.MODERATION_PENDING,
    ).update(
        moderation_status=BaseParsedEntity.MODERATION_APPROVED,
        moderation_comment=None,
        updated_at=now,
    )
    return ModerationApproveAllResult(approved_count=approved_count)


@router.get("/news/{news_id}", response_model=NewsRead)
async def get_news(news_id: int) -> NewsRead:
    news = await News.get_or_none(id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return NewsRead.model_validate(news)


@router.post("/news/{news_id}/approve", response_model=ModerationActionResult)
async def approve_news(news_id: int) -> ModerationActionResult:
    news = await News.get_or_none(id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    news.moderation_status = BaseParsedEntity.MODERATION_APPROVED
    news.moderation_comment = None
    news.updated_at = datetime.now(timezone.utc)
    await news.save()
    return ModerationActionResult(news_id=news_id, moderation_status=news.moderation_status)


@router.post("/news/{news_id}/reject", response_model=ModerationActionResult)
async def reject_news(news_id: int, reason: str | None = None) -> ModerationActionResult:
    news = await News.get_or_none(id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    news.moderation_status = BaseParsedEntity.MODERATION_REJECTED
    news.moderation_comment = reason
    news.updated_at = datetime.now(timezone.utc)
    await news.save()
    return ModerationActionResult(news_id=news_id, moderation_status=news.moderation_status)

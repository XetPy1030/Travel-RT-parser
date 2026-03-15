from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.models.base import BaseParsedEntity
from app.models.news import News

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/pending/news")
async def list_pending_news(limit: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    news_list = await News.filter(
        moderation_status=BaseParsedEntity.MODERATION_PENDING,
    ).limit(limit).order_by("-parsed_at")
    return [await _serialize_news_item(item) for item in news_list]


@router.get("/news/{news_id}")
async def get_news(news_id: int) -> dict:
    news = await News.get_or_none(id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return await _serialize_news_item(news)


@router.post("/news/{news_id}/approve")
async def approve_news(news_id: int) -> dict:
    news = await News.get_or_none(id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    news.moderation_status = BaseParsedEntity.MODERATION_APPROVED
    news.moderation_comment = None
    news.updated_at = datetime.now(timezone.utc)
    await news.save()
    return {"status": "ok", "news_id": news_id, "moderation_status": news.moderation_status}


@router.post("/news/{news_id}/reject")
async def reject_news(news_id: int, reason: str | None = None) -> dict:
    news = await News.get_or_none(id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    news.moderation_status = BaseParsedEntity.MODERATION_REJECTED
    news.moderation_comment = reason
    news.updated_at = datetime.now(timezone.utc)
    await news.save()
    return {"status": "ok", "news_id": news_id, "moderation_status": news.moderation_status}


async def _serialize_news_item(news: News) -> dict:
    return {
        "id": news.id,
        "external_id": news.external_id,
        "external_source": news.external_source,
        "external_url": news.external_url,
        "parsed_title": news.parsed_title,
        "parsed_description": news.parsed_description,
        "parsed_created_at": news.parsed_created_at.isoformat(),
        "parsed_topic": news.parsed_topic,
        "moderation_status": news.moderation_status,
        "moderation_comment": news.moderation_comment,
        "is_sent_to_backend": news.is_sent_to_backend,
        "backend_id": news.backend_id,
    }

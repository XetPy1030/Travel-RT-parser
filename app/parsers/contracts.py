from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ParsedNewsListItem:
    external_id: str
    external_url: str
    title: str
    description: str
    image_url: str | None
    published_at: datetime
    topic: str
    topic_raw: str | None
    source_page: int


@dataclass(slots=True)
class ParsedNewsListPage:
    topic: str
    page: int
    items: list[ParsedNewsListItem]
    has_next_page: bool


@dataclass(slots=True)
class ParsedNewsDetail:
    external_id: str
    external_url: str
    title: str
    description: str
    content: str
    image_url: str | None

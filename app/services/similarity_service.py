from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class RelatedCandidate:
    entity_a_id: int
    entity_b_id: int
    score: float


class SimilarityService(Protocol):
    async def find_related_candidates(self, entity_type: str) -> list[RelatedCandidate]:
        """Возвращает пары похожих сущностей для последующей записи RelatedEntity."""


class NoopSimilarityService:
    async def find_related_candidates(self, entity_type: str) -> list[RelatedCandidate]:
        # Для news на этапе 1 similarity отключен.
        return []

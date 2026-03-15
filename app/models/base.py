from typing import Any

from tortoise import fields, ForeignKeyFieldInstance
from tortoise.models import Model


class BaseParsedEntity(Model):
    """Сущность, полученная парсером и ожидающая модерации/отправки."""

    MODERATION_PENDING = "pending"
    MODERATION_APPROVED = "approved"
    MODERATION_REJECTED = "rejected"
    MODERATION_STATUSES = (
        (MODERATION_PENDING, "На модерации"),
        (MODERATION_APPROVED, "Одобрено"),
        (MODERATION_REJECTED, "Отклонено"),
    )

    id = fields.IntField(primary_key=True)
    # ДАННЫЕ СУЩНОСТИ

    # Идентификатор из внешнего источника (если есть).
    external_id = fields.CharField(max_length=255, index=True)
    # Enum с источником парсинга
    external_source: str
    # URL для внешнего источника
    external_url = fields.CharField(max_length=255)

    parsed_at = fields.DatetimeField(auto_now_add=True)
    moderation_status = fields.CharField(
        max_length=20,
        choices=MODERATION_STATUSES,
        default=MODERATION_PENDING,
        index=True,
    )
    moderation_comment = fields.TextField(null=True)

    is_sent_to_backend = fields.BooleanField(default=False, index=True)
    backend_synced_at = fields.DatetimeField(null=True)
    backend_id = fields.IntField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseRelatedEntity(Model):
    """Связь между похожими сущностями."""

    id = fields.IntField(primary_key=True)
    entity_a: ForeignKeyFieldInstance[Any]
    entity_a_id: int
    entity_b: ForeignKeyFieldInstance[Any]
    entity_b_id: int
    score = fields.FloatField(default=0.0)
    is_similarity_confirmed = fields.BooleanField(default=False, index=True)
    similarity_confirmed_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    async def save(self, *args, **kwargs):
        """
        Нормализует пару в недиректный вид:
        (a, b) и (b, a) считаются одной связью.
        """
        if self.entity_a_id is None or self.entity_b_id is None:
            raise ValueError("Both entity_a and entity_b must be set before save.")

        if self.entity_a_id == self.entity_b_id:
            raise ValueError("Related entities must be different.")

        if self.entity_a_id > self.entity_b_id:
            self.entity_a_id, self.entity_b_id = self.entity_b_id, self.entity_a_id

        await super().save(*args, **kwargs)

    class Meta:
        abstract = True
        unique_together = (("entity_a", "entity_b"),)


class BaseParseCursor(Model):
    """Курсор парсинга: что было последним обработано по каждому источнику."""

    id = fields.IntField(primary_key=True)
    external_source: str

    last_external_id = fields.CharField(max_length=255, null=True)
    last_parsed_at = fields.DatetimeField(null=True)

    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


from tortoise import fields
from tortoise.models import Model


class Source(Model):
    """Источник данных для парсинга (сайт, канал, API)."""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=150, unique=True)
    url = fields.CharField(max_length=500, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "sources"


class ParsedEntity(Model):
    """Сущность, полученная парсером и ожидающая модерации/отправки."""

    MODERATION_PENDING = "pending"
    MODERATION_APPROVED = "approved"
    MODERATION_REJECTED = "rejected"
    MODERATION_STATUSES = (
        (MODERATION_PENDING, "На модерации"),
        (MODERATION_APPROVED, "Одобрено"),
        (MODERATION_REJECTED, "Отклонено"),
    )

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=500)
    content = fields.TextField(null=True)

    # Идентификатор из внешнего источника (если есть).
    external_id = fields.CharField(max_length=255, null=True, index=True)
    source = fields.ForeignKeyField("models.Source", related_name="entities")

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

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "parsed_entities"


class RelatedEntity(Model):
    """Связь между похожими сущностями."""

    id = fields.IntField(pk=True)
    source_entity = fields.ForeignKeyField(
        "models.ParsedEntity",
        related_name="similar_to",
        on_delete=fields.CASCADE,
    )
    related_entity = fields.ForeignKeyField(
        "models.ParsedEntity",
        related_name="similar_from",
        on_delete=fields.CASCADE,
    )
    score = fields.FloatField(default=0.0)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "related_entities"
        unique_together = (("source_entity_id", "related_entity_id"),)


class ParseCursor(Model):
    """Курсор парсинга: что было последним обработано по каждому источнику."""

    id = fields.IntField(pk=True)
    source = fields.OneToOneField("models.Source", related_name="cursor")

    last_external_id = fields.CharField(max_length=255, null=True)
    last_parsed_at = fields.DatetimeField(null=True)

    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "parse_cursors"

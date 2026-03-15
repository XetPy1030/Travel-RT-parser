from tortoise import fields

from .base import BaseParsedEntity, BaseParseCursor, BaseRelatedEntity

EXTERNAL_SOURCE_TATNEWS = "tatnews"
EXTERNAL_SOURCES = (
    (EXTERNAL_SOURCE_TATNEWS, "Tatnews"),
)

TOPIC_ECOLOGY = "ecology"
TOPIC_CULTURE = "culture"
TOPIC_SOCIETY = "society"
TOPICS = (
    (TOPIC_ECOLOGY, "Экология"),
    (TOPIC_CULTURE, "Культура"),
    (TOPIC_SOCIETY, "Общество"),
)


class News(BaseParsedEntity):
    """Новость."""

    parsed_title = fields.CharField(max_length=255)
    parsed_image = fields.CharField(max_length=255)
    parsed_description = fields.TextField()
    parsed_content = fields.TextField()
    parsed_created_at = fields.DatetimeField()

    parsed_topic = fields.CharField(max_length=32, choices=TOPICS)
    parsed_topic_raw = fields.CharField(max_length=255, null=True)

    external_source = fields.CharField(max_length=255, choices=EXTERNAL_SOURCES)
    source_page = fields.IntField(default=1)
    raw_payload_hash = fields.CharField(max_length=64, null=True, index=True)

    class Meta:
        unique_together = (("external_source", "external_id"),)


class NewsRelatedEntity(BaseRelatedEntity):
    """Связь между новостями."""

    news_a = fields.ForeignKeyField("models.News", related_name="similar_links_a", on_delete=fields.CASCADE)
    news_b = fields.ForeignKeyField("models.News", related_name="similar_links_b", on_delete=fields.CASCADE)


class NewsParseCursor(BaseParseCursor):
    """Курсор парсинга новостей."""

    external_source = fields.CharField(max_length=255, choices=EXTERNAL_SOURCES)
    topic = fields.CharField(max_length=32, choices=TOPICS)
    last_page = fields.IntField(default=1)

    class Meta:
        unique_together = (("external_source", "topic"),)

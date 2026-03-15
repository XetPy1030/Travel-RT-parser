from tortoise import fields

from .base import BaseParsedEntity, BaseParseCursor, BaseRelatedEntity

EXTERNAL_SOURCE_TATNEWS = "tatnews"
EXTERNAL_SOURCES = (
    (EXTERNAL_SOURCE_TATNEWS, "Tatnews"),
)


class News(BaseParsedEntity):
    """Новость."""

    parsed_title = fields.CharField(max_length=255)
    parsed_image = fields.CharField(max_length=255)
    parsed_description = fields.TextField()
    parsed_content = fields.TextField()
    parsed_created_at = fields.DatetimeField()

    external_source = fields.CharField(max_length=255, choices=EXTERNAL_SOURCES)


class NewsRelatedEntity(BaseRelatedEntity):
    """Связь между новостями."""

    news_a = fields.ForeignKeyField("models.News", related_name="similar_links_a", on_delete=fields.CASCADE)
    news_b = fields.ForeignKeyField("models.News", related_name="similar_links_b", on_delete=fields.CASCADE)


class NewsParseCursor(BaseParseCursor):
    """Курсор парсинга новостей."""

    external_source = fields.CharField(max_length=255, choices=EXTERNAL_SOURCES)

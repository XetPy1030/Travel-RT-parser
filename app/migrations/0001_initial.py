from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='News',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('external_id', fields.CharField(db_index=True, max_length=255)),
                ('external_url', fields.CharField(max_length=255)),
                ('parsed_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('moderation_status', fields.CharField(default='pending', db_index=True, max_length=20)),
                ('moderation_comment', fields.TextField(null=True, unique=False)),
                ('is_sent_to_backend', fields.BooleanField(default=False, db_index=True)),
                ('backend_synced_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
                ('backend_id', fields.IntField(null=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ('parsed_title', fields.CharField(max_length=255)),
                ('parsed_image', fields.CharField(max_length=255)),
                ('parsed_description', fields.TextField(unique=False)),
                ('parsed_content', fields.TextField(unique=False)),
                ('parsed_created_at', fields.DatetimeField(auto_now=False, auto_now_add=False)),
                ('external_source', fields.CharField(max_length=255)),
            ],
            options={'table': 'news', 'app': 'models', 'pk_attr': 'id', 'table_description': 'Новость.'},
            bases=['BaseParsedEntity'],
        ),
        ops.CreateModel(
            name='NewsParseCursor',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('last_external_id', fields.CharField(null=True, max_length=255)),
                ('last_parsed_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ('external_source', fields.CharField(max_length=255)),
            ],
            options={'table': 'newsparsecursor', 'app': 'models', 'pk_attr': 'id', 'table_description': 'Курсор парсинга новостей.'},
            bases=['BaseParseCursor'],
        ),
        ops.CreateModel(
            name='NewsRelatedEntity',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('score', fields.FloatField(default=0.0)),
                ('is_similarity_confirmed', fields.BooleanField(default=False, db_index=True)),
                ('similarity_confirmed_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('news_a', fields.ForeignKeyField('models.News', source_field='news_a_id', db_constraint=True, to_field='id', related_name='similar_links_a', on_delete=OnDelete.CASCADE)),
                ('news_b', fields.ForeignKeyField('models.News', source_field='news_b_id', db_constraint=True, to_field='id', related_name='similar_links_b', on_delete=OnDelete.CASCADE)),
            ],
            options={'table': 'newsrelatedentity', 'app': 'models', 'pk_attr': 'id', 'table_description': 'Связь между новостями.'},
            bases=['BaseRelatedEntity'],
        ),
    ]

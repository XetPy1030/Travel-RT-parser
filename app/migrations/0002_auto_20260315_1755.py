from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.migrations.constraints import UniqueConstraint

class Migration(migrations.Migration):
    dependencies = [('models', '0001_initial')]

    initial = False

    operations = [
        ops.AddField(
            model_name='News',
            name='parsed_topic',
            field=fields.CharField(max_length=32),
        ),
        ops.AddField(
            model_name='News',
            name='parsed_topic_raw',
            field=fields.CharField(null=True, max_length=255),
        ),
        ops.AddField(
            model_name='News',
            name='raw_payload_hash',
            field=fields.CharField(null=True, db_index=True, max_length=64),
        ),
        ops.AddField(
            model_name='News',
            name='source_page',
            field=fields.IntField(default=1),
        ),
        ops.AddConstraint(
            model_name='News',
            constraint=UniqueConstraint(fields=('external_source', 'external_id'), name=None),
        ),
        ops.AddField(
            model_name='NewsParseCursor',
            name='last_page',
            field=fields.IntField(default=1),
        ),
        ops.AddField(
            model_name='NewsParseCursor',
            name='topic',
            field=fields.CharField(max_length=32),
        ),
        ops.AddConstraint(
            model_name='NewsParseCursor',
            constraint=UniqueConstraint(fields=('external_source', 'topic'), name=None),
        ),
    ]

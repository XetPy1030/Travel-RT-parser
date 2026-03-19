from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0003_auto_20260319_0547')]

    initial = False

    operations = [
        ops.AlterField(
            model_name='News',
            name='needs_backend_update',
            field=fields.BooleanField(default=False, db_index=True),
        ),
    ]

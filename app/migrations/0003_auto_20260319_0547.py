from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0002_auto_20260315_1755')]

    initial = False

    operations = [
        ops.AddField(
            model_name='News',
            name='needs_backend_update',
            field=fields.BooleanField(default=False, db_index=True, db_default=False),
        ),
    ]

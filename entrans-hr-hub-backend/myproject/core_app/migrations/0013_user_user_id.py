import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0012_user_firstname_lastname_passwordexpiry'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

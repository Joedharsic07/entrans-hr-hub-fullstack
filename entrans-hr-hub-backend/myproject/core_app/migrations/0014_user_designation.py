from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0013_user_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='designation',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]

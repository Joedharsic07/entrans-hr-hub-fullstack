from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0011_timesheetemaillog'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='password_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

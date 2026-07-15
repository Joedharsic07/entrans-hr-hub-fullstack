import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_management', '0014_user_designation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_changed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='UserAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[
                        ('login', 'Login'),
                        ('logout', 'Logout'),
                        ('password_change', 'Password Change'),
                        ('password_reset', 'Password Reset'),
                    ],
                    default='login',
                    max_length=50,
                )),
                ('status', models.CharField(
                    choices=[('success', 'Success'), ('failed', 'Failed')],
                    default='success',
                    max_length=20,
                )),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, default='', max_length=500)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='access_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'user_access_log',
                'ordering': ['-timestamp'],
            },
        ),
    ]

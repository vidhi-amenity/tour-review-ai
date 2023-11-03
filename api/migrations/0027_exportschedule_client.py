# Generated by Django 3.1.6 on 2023-07-06 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0026_scheduleemailaddress_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportschedule',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated by Django 3.1.6 on 2023-03-07 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20230302_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='responded',
            field=models.BooleanField(default=False),
        ),
    ]

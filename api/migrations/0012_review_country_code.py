# Generated by Django 3.1.6 on 2023-04-26 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20230322_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='country_code',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
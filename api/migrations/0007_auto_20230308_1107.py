# Generated by Django 3.1.6 on 2023-03-08 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20230307_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='product',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='product_id',
            field=models.IntegerField(null=True),
        ),
    ]

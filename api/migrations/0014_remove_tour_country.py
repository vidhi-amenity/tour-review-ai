# Generated by Django 3.1.6 on 2023-05-10 07:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_country_tour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='country',
        ),
    ]
# Generated by Django 3.1.6 on 2023-07-14 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_auto_20230714_1433'),
        ('api', '0028_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='modified_at',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='payload',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='status',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='user',
        ),
        migrations.AddField(
            model_name='payment',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='authentication.company'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-19 10:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_destination'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='destination',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='destination',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

# Generated by Django 5.1.5 on 2025-01-27 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listitem',
            name='is_valid',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]

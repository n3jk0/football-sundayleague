# Generated by Django 2.2.6 on 2020-03-01 20:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0009_auto_20191113_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        )
    ]

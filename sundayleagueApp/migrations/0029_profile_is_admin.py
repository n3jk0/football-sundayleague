# Generated by Django 2.2.6 on 2021-02-04 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0028_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]

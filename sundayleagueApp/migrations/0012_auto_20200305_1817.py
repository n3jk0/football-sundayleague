# Generated by Django 2.2.6 on 2020-03-05 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0011_auto_20200305_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='tablerow',
            name='penalty_points',
            field=models.IntegerField(default=0),
        ),
    ]
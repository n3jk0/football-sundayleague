# Generated by Django 3.1.6 on 2021-02-18 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0030_auto_20210206_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('NOT_STARTED', 'Not started'), ('LIVE', 'Live'), ('COMPLETED', 'Completed'), ('CONFIRMED', 'Confirmed')], default='NOT_STARTED', max_length=32),
        ),
    ]
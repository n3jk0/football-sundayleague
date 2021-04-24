# Generated by Django 3.1.6 on 2021-03-23 16:01

from django.db import migrations, models
from sundayleagueApp.services import SystemSettingsUtils
from sundayleagueApp import constants

def insert_data(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    SystemSetting = apps.get_model("sundayleagueApp", "SystemSetting")
    systemSetting = SystemSetting(key=constants.WRITE_SCORERS_ENABLED, string_value="True")
    systemSetting.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0032_auto_20210306_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('string_value', models.CharField(max_length=255)),
            ],
        ),
        migrations.RunPython(insert_data),
    ]
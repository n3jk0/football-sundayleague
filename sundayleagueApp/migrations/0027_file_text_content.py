# Generated by Django 2.2.6 on 2020-12-31 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0026_auto_20200823_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='text_content',
            field=models.CharField(max_length=10000, null=True),
        ),
    ]